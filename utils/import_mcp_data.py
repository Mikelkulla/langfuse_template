import json
import sqlite3
from pathlib import Path
from typing import List, Dict

class MCPDataImporter:
    def __init__(self, db_path: str = "mcp_analysis.db"):
        self.db_path = db_path
        self.conn = None
        
    def create_database(self):
        """Create SQLite database with schema"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.executescript("""
            DROP TABLE IF EXISTS conversation_steps;
            DROP TABLE IF EXISTS executions;
            DROP VIEW IF EXISTS performance_comparison;
            DROP VIEW IF EXISTS tool_usage_stats;
            DROP VIEW IF EXISTS tool_details;
            DROP VIEW IF EXISTS tool_usage_by_server;
            DROP VIEW IF EXISTS tool_usage_by_tool;
            DROP VIEW IF EXISTS performance_comparison_by_server;
            DROP VIEW IF EXISTS performance_comparison_by_prompt;
            DROP VIEW IF EXISTS prompt_steps_comparison;
            DROP VIEW IF EXISTS prompt_steps_detailed;
            DROP VIEW IF EXISTS prompt_execution_patterns;
            DROP VIEW IF EXISTS conversation_steps_with_execution;
            DROP VIEW IF EXISTS Full_Report;
            
            
            CREATE TABLE executions (
                execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                server_type TEXT NOT NULL,
                server_description TEXT,
                execution_timestamp TEXT,
                session_mode TEXT,
                raw_user_prompt TEXT,
                final_answer TEXT,
                execution_time_s REAL,
                total_tokens INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                llm_time_s REAL,
                mcp_time_s REAL,
                total_steps INTEGER,
                langfuse_trace_url TEXT,
                UNIQUE(prompt_id, server_type)
            );
            
            CREATE TABLE conversation_steps (
                step_id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER,
                step_number INTEGER,
                step_type TEXT,
                duration_s REAL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                tool_name TEXT,
                tool_input TEXT,
                tool_output TEXT,
                output_text TEXT,
                FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
            );
            
            CREATE VIEW performance_comparison AS
            SELECT 
                prompt_id,
                server_type,
                execution_time_s,
                total_tokens,
                total_steps,
                llm_time_s,
                mcp_time_s as mcp_time_sum_s,
                ROUND(execution_time_s - llm_time_s, 3) as real_mcp_time_s,
                ROUND((execution_time_s - llm_time_s) * 100.0 / execution_time_s, 3) as real_mcp_time_pct,
                ROUND(llm_time_s * 100.0 / execution_time_s, 3) as llm_time_pct,
                ROUND(mcp_time_s * 100.0 / execution_time_s, 3) as mcp_sum_pct,
                ROUND(CAST(output_tokens AS REAL) / input_tokens, 4) as token_efficiency,
                CASE 
                    WHEN (mcp_time_s + llm_time_s) > execution_time_s 
                    THEN 'Yes' 
                    ELSE 'No' 
                END as has_parallel_execution,
                ROUND(mcp_time_s / NULLIF(execution_time_s - llm_time_s, 0), 3) as parallelism_factor
            FROM executions
            ORDER BY prompt_id, server_type;
            
            CREATE VIEW tool_usage_stats AS
            SELECT 
                e.prompt_id,
                e.server_type,
                COUNT(CASE WHEN c.step_type = 'mcp_tool_call' THEN 1 END) as tool_call_count,
                AVG(CASE WHEN c.step_type = 'mcp_tool_call' THEN c.duration_s END) as avg_tool_duration,
                COUNT(CASE WHEN c.step_type = 'llm_response' THEN 1 END) as llm_response_count,
                AVG(CASE WHEN c.step_type = 'llm_response' THEN c.duration_s END) as avg_llm_duration
            FROM executions e
            LEFT JOIN conversation_steps c ON e.execution_id = c.execution_id
            GROUP BY e.execution_id, e.prompt_id, e.server_type;
            
            CREATE VIEW tool_details AS
            SELECT 
                e.prompt_id,
                e.server_type,
                c.step_number,
                c.tool_name,
                ROUND(c.duration_s, 3) as duration_s,
                c.tool_input,
                c.tool_output,
                e.raw_user_prompt
            FROM conversation_steps c
            JOIN executions e ON c.execution_id = e.execution_id
            WHERE c.step_type = 'mcp_tool_call'
            ORDER BY e.prompt_id, e.server_type, c.step_number;
            
            -- ✨ NEW: Aggregated tool usage by server type (4 rows total)
            CREATE VIEW tool_usage_by_server AS
            SELECT 
                e.server_type,
                COUNT(DISTINCT e.prompt_id) as prompt_count,
                COUNT(CASE WHEN c.step_type = 'mcp_tool_call' THEN 1 END) as total_tool_calls,
                ROUND(AVG(CASE WHEN c.step_type = 'mcp_tool_call' THEN c.duration_s END), 3) as avg_tool_duration,
                ROUND(MIN(CASE WHEN c.step_type = 'mcp_tool_call' THEN c.duration_s END), 3) as min_tool_duration,
                ROUND(MAX(CASE WHEN c.step_type = 'mcp_tool_call' THEN c.duration_s END), 3) as max_tool_duration,
                COUNT(CASE WHEN c.step_type = 'llm_response' THEN 1 END) as total_llm_responses,
                ROUND(AVG(CASE WHEN c.step_type = 'llm_response' THEN c.duration_s END), 3) as avg_llm_duration,
                ROUND(AVG(e.execution_time_s), 3) as avg_execution_time,
                ROUND(AVG(e.total_tokens), 0) as avg_total_tokens
            FROM executions e
            LEFT JOIN conversation_steps c ON e.execution_id = c.execution_id
            GROUP BY e.server_type
            ORDER BY e.server_type;
            
            -- ✨ NEW: Aggregated statistics per tool (one row per tool_name)
            CREATE VIEW tool_usage_by_tool AS
            SELECT 
                c.tool_name,
                COUNT(*) as usage_count,
                COUNT(DISTINCT e.prompt_id) as used_in_prompts,
                COUNT(DISTINCT e.server_type) as used_in_servers,
                ROUND(AVG(c.duration_s), 3) as avg_duration_s,
                ROUND(MIN(c.duration_s), 3) as min_duration_s,
                ROUND(MAX(c.duration_s), 3) as max_duration_s,
                ROUND(SUM(c.duration_s), 3) as total_duration_s,
                ROUND(AVG(c.total_tokens), 0) as avg_tokens,
                ROUND(SUM(c.total_tokens), 0) as total_tokens,
                GROUP_CONCAT(DISTINCT e.server_type) as servers_used,
                COUNT(CASE WHEN e.server_type = 'cdata' THEN 1 END) as cdata_count,
                COUNT(CASE WHEN e.server_type = 'static' THEN 1 END) as static_count,
                COUNT(CASE WHEN e.server_type = 'dynamic' THEN 1 END) as dynamic_count,
                COUNT(CASE WHEN e.server_type = 'full' THEN 1 END) as full_count
            FROM conversation_steps c
            JOIN executions e ON c.execution_id = e.execution_id
            WHERE c.step_type = 'mcp_tool_call'
            GROUP BY c.tool_name
            ORDER BY usage_count DESC;
            
            -- ✨ NEW: Performance comparison aggregated by server type
            CREATE VIEW performance_comparison_by_server AS
            SELECT 
                e.server_type,
                COUNT(DISTINCT e.prompt_id) as prompt_count,
                ROUND(AVG(e.execution_time_s), 3) as avg_execution_time_s,
                ROUND(MIN(e.execution_time_s), 3) as min_execution_time_s,
                ROUND(MAX(e.execution_time_s), 3) as max_execution_time_s,
                ROUND(AVG(e.total_tokens), 0) as avg_total_tokens,
                ROUND(AVG(e.total_steps), 1) as avg_total_steps,
                ROUND(AVG(e.llm_time_s), 3) as avg_llm_time_s,
                ROUND(AVG(e.mcp_time_s), 3) as avg_mcp_time_sum_s,
                ROUND(AVG(e.execution_time_s - e.llm_time_s), 3) as avg_real_mcp_time_s,
                ROUND(AVG((e.execution_time_s - e.llm_time_s) * 100.0 / e.execution_time_s), 2) as avg_real_mcp_time_pct,
                ROUND(AVG(e.llm_time_s * 100.0 / e.execution_time_s), 2) as avg_llm_time_pct,
                ROUND(AVG(e.mcp_time_s * 100.0 / e.execution_time_s), 2) as avg_mcp_sum_pct,
                ROUND(AVG(CAST(e.output_tokens AS REAL) / e.input_tokens), 4) as avg_token_efficiency,
                ROUND(SUM(CASE WHEN (e.mcp_time_s + e.llm_time_s) > e.execution_time_s THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as parallel_execution_pct,
                ROUND(AVG(e.mcp_time_s / NULLIF(e.execution_time_s - e.llm_time_s, 0)), 3) as avg_parallelism_factor
            FROM executions e
            GROUP BY e.server_type
            ORDER BY e.server_type;
            
            -- ✨ NEW: Performance comparison aggregated by prompt (comparing servers for each prompt)
            CREATE VIEW performance_comparison_by_prompt AS
            SELECT 
                e.prompt_id,
                e.raw_user_prompt,
                COUNT(DISTINCT e.server_type) as server_count,
                ROUND(AVG(e.execution_time_s), 3) as avg_execution_time_s,
                ROUND(MIN(e.execution_time_s), 3) as min_execution_time_s,
                ROUND(MAX(e.execution_time_s), 3) as max_execution_time_s,
                ROUND(MAX(e.execution_time_s) - MIN(e.execution_time_s), 3) as execution_time_range,
                ROUND(AVG(e.total_tokens), 0) as avg_total_tokens,
                ROUND(MIN(e.total_tokens), 0) as min_total_tokens,
                ROUND(MAX(e.total_tokens), 0) as max_total_tokens,
                ROUND(AVG(e.total_steps), 1) as avg_total_steps,
                ROUND(AVG(e.llm_time_s), 3) as avg_llm_time_s,
                ROUND(AVG(e.mcp_time_s), 3) as avg_mcp_time_sum_s,
                ROUND(AVG(e.execution_time_s - e.llm_time_s), 3) as avg_real_mcp_time_s,
                ROUND(AVG((e.execution_time_s - e.llm_time_s) * 100.0 / e.execution_time_s), 2) as avg_real_mcp_time_pct,
                ROUND(AVG(e.llm_time_s * 100.0 / e.execution_time_s), 2) as avg_llm_time_pct,
                ROUND(AVG(CAST(e.output_tokens AS REAL) / e.input_tokens), 4) as avg_token_efficiency,
                ROUND(MIN(CAST(e.output_tokens AS REAL) / e.input_tokens), 4) as min_token_efficiency,
                ROUND(MAX(CAST(e.output_tokens AS REAL) / e.input_tokens), 4) as max_token_efficiency,
                -- Best/worst performing server for this prompt
                (SELECT server_type FROM executions WHERE prompt_id = e.prompt_id ORDER BY execution_time_s ASC LIMIT 1) as fastest_server,
                (SELECT server_type FROM executions WHERE prompt_id = e.prompt_id ORDER BY execution_time_s DESC LIMIT 1) as slowest_server,
                -- Most/least token efficient server
                (SELECT server_type FROM executions WHERE prompt_id = e.prompt_id ORDER BY CAST(output_tokens AS REAL) / input_tokens ASC LIMIT 1) as most_efficient_server,
                (SELECT server_type FROM executions WHERE prompt_id = e.prompt_id ORDER BY CAST(output_tokens AS REAL) / input_tokens DESC LIMIT 1) as least_efficient_server
            FROM executions e
            GROUP BY e.prompt_id
            ORDER BY e.prompt_id;

            -- ✨ NEW: Prompt Comparison 1          
            CREATE VIEW prompt_steps_comparison AS
            SELECT 
                c.step_number,
                e.prompt_id,
                e.raw_user_prompt,
                MAX(CASE WHEN e.server_type = 'cdata' THEN c.step_type END) as cdata_step_type,
                MAX(CASE WHEN e.server_type = 'cdata' THEN c.tool_name END) as cdata_tool,
                MAX(CASE WHEN e.server_type = 'cdata' THEN c.duration_s END) as cdata_duration,
                MAX(CASE WHEN e.server_type = 'static' THEN c.step_type END) as static_step_type,
                MAX(CASE WHEN e.server_type = 'static' THEN c.tool_name END) as static_tool,
                MAX(CASE WHEN e.server_type = 'static' THEN c.duration_s END) as static_duration,
                MAX(CASE WHEN e.server_type = 'dynamic' THEN c.step_type END) as dynamic_step_type,
                MAX(CASE WHEN e.server_type = 'dynamic' THEN c.tool_name END) as dynamic_tool,
                MAX(CASE WHEN e.server_type = 'dynamic' THEN c.duration_s END) as dynamic_duration,
                MAX(CASE WHEN e.server_type = 'full' THEN c.step_type END) as full_step_type,
                MAX(CASE WHEN e.server_type = 'full' THEN c.tool_name END) as full_tool,
                MAX(CASE WHEN e.server_type = 'full' THEN c.duration_s END) as full_duration
            FROM conversation_steps c
            JOIN executions e ON c.execution_id = e.execution_id
            GROUP BY c.step_number, e.prompt_id
            ORDER BY e.prompt_id, c.step_number;
                             
            CREATE VIEW prompt_steps_detailed AS
            SELECT 
                e.prompt_id,
                e.server_type,
                c.step_number,
                c.step_type,
                c.tool_name,
                ROUND(c.duration_s, 3) as duration_s,
                c.total_tokens,
                c.tool_input,
                SUBSTR(c.tool_output, 1, 200) as tool_output_preview,
                SUBSTR(c.output_text, 1, 200) as output_text_preview
            FROM conversation_steps c
            JOIN executions e ON c.execution_id = e.execution_id
            ORDER BY e.prompt_id, c.step_number, e.server_type;
                             
            CREATE VIEW prompt_execution_patterns AS
            SELECT 
                e.prompt_id,
                e.raw_user_prompt,
                e.server_type,
                e.total_steps,
                COUNT(CASE WHEN c.step_type = 'mcp_tool_call' THEN 1 END) as tool_calls,
                COUNT(CASE WHEN c.step_type = 'llm_response' THEN 1 END) as llm_responses,
                GROUP_CONCAT(
                    CASE 
                        WHEN c.step_type = 'mcp_tool_call' THEN c.tool_name 
                        ELSE 'LLM'
                    END, ' → '
                ) as execution_sequence,
                ROUND(SUM(CASE WHEN c.step_type = 'mcp_tool_call' THEN c.duration_s END), 3) as total_tool_time,
                ROUND(SUM(CASE WHEN c.step_type = 'llm_response' THEN c.duration_s END), 3) as total_llm_time
            FROM executions e
            LEFT JOIN conversation_steps c ON e.execution_id = c.execution_id
            GROUP BY e.execution_id, e.prompt_id, e.server_type
            ORDER BY e.prompt_id, e.server_type;
                             
            CREATE VIEW conversation_steps_with_execution AS
            SELECT 
                -- From executions table
                e.prompt_id,
                e.server_type,
                e.execution_timestamp,
                e.raw_user_prompt,
                e.final_answer,
                e.execution_time_s,
                e.total_tokens AS execution_total_tokens,
                e.llm_time_s,
                e.mcp_time_s,
                e.total_steps,
                -- From conversation_steps table
                c.step_number,
                c.step_type,
                c.duration_s,
                c.total_tokens AS step_total_tokens,
                c.tool_name,
                c.tool_input,
                c.tool_output,
                c.output_text
            FROM conversation_steps c
            JOIN executions e ON c.execution_id = e.execution_id
            ORDER BY e.prompt_id, e.server_type, c.step_number;
                             
            CREATE VIEW Full_Report AS
            SELECT 
                e.prompt_id as Number,
                e.raw_user_prompt as Prompt,
                -- Winners
                (SELECT server_type FROM executions WHERE prompt_id = e.prompt_id ORDER BY total_steps ASC LIMIT 1) as Steps_Winner,
                (SELECT server_type FROM executions WHERE prompt_id = e.prompt_id ORDER BY total_tokens ASC LIMIT 1) as Tokens_Winner,
                (SELECT server_type FROM executions WHERE prompt_id = e.prompt_id ORDER BY execution_time_s ASC LIMIT 1) as Time_Winner,
                -- total_steps
                MAX(CASE WHEN e.server_type = 'cdata' THEN e.total_steps END) as CData_Steps,
                MAX(CASE WHEN e.server_type = 'static' THEN e.total_steps END) as Monday_Steps,
                MAX(CASE WHEN e.server_type = 'dynamic' THEN e.total_steps END) as Graph_Steps,
                MAX(CASE WHEN e.server_type = 'full' THEN e.total_steps END) as Full_Steps,
                -- total_tokens
                MAX(CASE WHEN e.server_type = 'cdata' THEN e.total_tokens END) as CData_Total_Tokens,
                MAX(CASE WHEN e.server_type = 'static' THEN e.total_tokens END) as Monday_Total_Tokens,
                MAX(CASE WHEN e.server_type = 'dynamic' THEN e.total_tokens END) as Graph_Total_Tokens,
                MAX(CASE WHEN e.server_type = 'full' THEN e.total_tokens END) as Full_Total_Tokens,
                -- execution_time_s
                MAX(CASE WHEN e.server_type = 'cdata' THEN e.execution_time_s END) as CData_Whole_Chat_Time,
                MAX(CASE WHEN e.server_type = 'static' THEN e.execution_time_s END) as Monday_Whole_Chat_Time,
                MAX(CASE WHEN e.server_type = 'dynamic' THEN e.execution_time_s END) as Graph_Whole_Chat_Time,
                MAX(CASE WHEN e.server_type = 'full' THEN e.execution_time_s END) as Full_Whole_Chat_Time
            FROM executions e
            GROUP BY e.prompt_id
            ORDER BY e.prompt_id;
        """)
        
        self.conn.commit()
        print(f"✓ Database created: {self.db_path}")
    
    def import_json_file(self, json_file_path: str):
        """Import a single JSON file containing array of test results"""
        try:
            # Use UTF-8 encoding to handle Unicode characters (emojis, special chars)
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    self._import_execution(item)
            else:
                self._import_execution(data)
            
            self.conn.commit()
            print(f"✓ Imported: {json_file_path}")
            
        except UnicodeDecodeError as e:
            print(f"✗ Encoding error in {json_file_path}: {e}")
            print("  Trying with error handling...")
            
            # Fallback: try with error handling
            with open(json_file_path, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    self._import_execution(item)
            else:
                self._import_execution(data)
            
            self.conn.commit()
            print(f"✓ Imported (with replacements): {json_file_path}")
    
    def _import_execution(self, data: Dict):
        """Import a single execution record"""
        cursor = self.conn.cursor()
        
        # Determine server type from mcp_server field
        server_mapping = {
            'cdata_monday': 'cdata',
            'native_monday_static': 'static',
            'native_monday_dynamic': 'dynamic',
            'native_monday_full': 'full'
        }
        server_type = server_mapping.get(data.get('mcp_server', ''), 'unknown')
        
        # Insert execution record
        cursor.execute("""
            INSERT OR REPLACE INTO executions (
                prompt_id, server_type, server_description, execution_timestamp,
                session_mode, raw_user_prompt, final_answer, execution_time_s,
                total_tokens, input_tokens, output_tokens, llm_time_s, mcp_time_s,
                total_steps, langfuse_trace_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('prompt_id'),
            server_type,
            data.get('server_description'),
            data.get('execution_timestamp'),
            data.get('session_mode'),
            data.get('raw_user_prompt'),
            data.get('final_answer'),
            data.get('execution_time_s'),
            data['summary'].get('total_tokens'),
            data['summary'].get('input_tokens'),
            data['summary'].get('output_tokens'),
            data['summary'].get('llm_time_s'),
            data['summary'].get('mcp_time_s'),
            data['summary'].get('total_steps'),
            data.get('langfuse_trace_url')
        ))
        
        execution_id = cursor.lastrowid
        
        # Import conversation flow
        for idx, step in enumerate(data.get('conversation_flow', []), 1):
            step_type = step.get('type')
            
            cursor.execute("""
                INSERT INTO conversation_steps (
                    execution_id, step_number, step_type, duration_s,
                    input_tokens, output_tokens, total_tokens,
                    tool_name, tool_input, tool_output, output_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id,
                idx,
                step_type,
                step.get('duration_s'),
                step.get('input_tokens'),
                step.get('output_tokens'),
                step.get('total_tokens'),
                step.get('tool'),
                step.get('input'),
                step.get('output'),
                step.get('output_text')
            ))
    
    def import_multiple_files(self, file_pattern: str):
        """Import multiple JSON files matching a pattern"""
        files = list(Path('.').glob(file_pattern))
        print(f"Found {len(files)} files matching '{file_pattern}'")
        
        for file_path in files:
            self.import_json_file(str(file_path))
        
        print(f"\n✓ Total imported: {len(files)} files")
    
    def close(self):
        if self.conn:
            self.conn.close()

#Usage
if __name__ == "__main__":
    importer = MCPDataImporter("mcp_analysis.db")
    
    # Create database
    importer.create_database()
    
    # Import your JSON file
    # importer.import_json_file("../executions/Prompts/prompt_1.json")
    
    # If you want to import ALL prompt files (prompt_1.json to prompt_24.json):
    importer.import_multiple_files("../executions/Prompts/prompt_*.json")
    
    importer.close()
    
    print("\n✓ Import complete! Database ready for analysis.")