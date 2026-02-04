import sqlite3
import pandas as pd
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "mcp_analysis.db")

def format_time(seconds):
    """Format seconds to a readable string"""
    if seconds is None:
        return "N/A"
    return f"{seconds:.3f}s"

def get_efficiency_rating(total_tokens, all_tokens):
    """
    Assign efficiency rating based on token count ranking
    Low: Lowest token count (1st place)
    Medium: 2nd lowest token count
    High: 3rd lowest token count
    Extreme: Highest token count (4th place)
    """
    # Sort tokens and find rank (1 = lowest, 4 = highest)
    sorted_tokens = sorted(all_tokens)
    rank = sorted_tokens.index(total_tokens) + 1  # 1-indexed rank
    
    if rank == 1:
        return "Low"
    elif rank == 2:
        return "Medium"
    elif rank == 3:
        return "High"
    else:
        return "Extreme"

def print_full_report():
    """Print the comprehensive Full Report comparing all servers across all prompts"""
    conn = sqlite3.connect(db_path)
    
    # Create the Full_Report view query
    query = """
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
        ORDER BY e.prompt_id
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("\n❌ No data found in database")
        return
    
    # Column widths
    col_number = 8
    col_prompt = 60
    col_winner = 12
    col_steps = 10
    
    # Print header
    print("\n" + "="*160)
    print("FULL PERFORMANCE REPORT")
    print("="*160)
    
    # Column headers
    header = (f"{'Number':<{col_number}}"
              f"{'Prompt':<{col_prompt}}"
              f"{'Steps_W...':<{col_winner}}"
              f"{'Tokens_...':<{col_winner}}"
              f"{'Time_W...':<{col_winner}}"
              f"{'CData_St...':<{col_steps}}"
              f"{'Monday_...':<{col_steps}}"
              f"{'Graph_St...':<{col_steps}}"
              f"{'Full_Steps':<{col_steps}}")
    
    print(header)
    print("-"*160)
    
    # Print each row
    for _, row in df.iterrows():
        # Truncate prompt if too long
        prompt_text = row['Prompt']
        if len(prompt_text) > col_prompt - 4:
            prompt_text = prompt_text[:col_prompt - 7] + "..."
        
        # Format values
        num = int(row['Number'])
        steps_w = row['Steps_Winner'] if pd.notna(row['Steps_Winner']) else '-'
        tokens_w = row['Tokens_Winner'] if pd.notna(row['Tokens_Winner']) else '-'
        time_w = row['Time_Winner'] if pd.notna(row['Time_Winner']) else '-'
        
        cdata_steps = int(row['CData_Steps']) if pd.notna(row['CData_Steps']) else '-'
        monday_steps = int(row['Monday_Steps']) if pd.notna(row['Monday_Steps']) else '-'
        graph_steps = int(row['Graph_Steps']) if pd.notna(row['Graph_Steps']) else '-'
        full_steps = int(row['Full_Steps']) if pd.notna(row['Full_Steps']) else '-'
        
        # Print row
        row_str = (f"{num:<{col_number}}"
                   f"{prompt_text:<{col_prompt}}"
                   f"{steps_w:<{col_winner}}"
                   f"{tokens_w:<{col_winner}}"
                   f"{time_w:<{col_winner}}"
                   f"{str(cdata_steps):<{col_steps}}"
                   f"{str(monday_steps):<{col_steps}}"
                   f"{str(graph_steps):<{col_steps}}"
                   f"{str(full_steps):<{col_steps}}")
        
        print(row_str)
    
    print("="*160)
    
    # Print token and time data as separate table
    print("\n" + "="*160)
    print("TOKEN AND TIME METRICS")
    print("="*160)
    
    # Token headers
    header_tokens = (f"{'Number':<{col_number}}"
                     f"{'CData_Tok...':<{col_steps+2}}"
                     f"{'Monday_T...':<{col_steps+2}}"
                     f"{'Graph_To...':<{col_steps+2}}"
                     f"{'Full_Toke...':<{col_steps+2}}"
                     f"{'CData_Tim...':<{col_steps+2}}"
                     f"{'Monday_T...':<{col_steps+2}}"
                     f"{'Graph_Ti...':<{col_steps+2}}"
                     f"{'Full_Time':<{col_steps+2}}")
    
    print(header_tokens)
    print("-"*160)
    
    # Print token and time rows
    for _, row in df.iterrows():
        num = int(row['Number'])
        
        # Tokens
        cdata_tok = f"{int(row['CData_Total_Tokens']):,}" if pd.notna(row['CData_Total_Tokens']) else '-'
        monday_tok = f"{int(row['Monday_Total_Tokens']):,}" if pd.notna(row['Monday_Total_Tokens']) else '-'
        graph_tok = f"{int(row['Graph_Total_Tokens']):,}" if pd.notna(row['Graph_Total_Tokens']) else '-'
        full_tok = f"{int(row['Full_Total_Tokens']):,}" if pd.notna(row['Full_Total_Tokens']) else '-'
        
        # Times
        cdata_time = f"{row['CData_Whole_Chat_Time']:.1f}" if pd.notna(row['CData_Whole_Chat_Time']) else '-'
        monday_time = f"{row['Monday_Whole_Chat_Time']:.1f}" if pd.notna(row['Monday_Whole_Chat_Time']) else '-'
        graph_time = f"{row['Graph_Whole_Chat_Time']:.1f}" if pd.notna(row['Graph_Whole_Chat_Time']) else '-'
        full_time = f"{row['Full_Whole_Chat_Time']:.1f}" if pd.notna(row['Full_Whole_Chat_Time']) else '-'
        
        # Print row
        row_str = (f"{num:<{col_number}}"
                   f"{cdata_tok:<{col_steps+2}}"
                   f"{monday_tok:<{col_steps+2}}"
                   f"{graph_tok:<{col_steps+2}}"
                   f"{full_tok:<{col_steps+2}}"
                   f"{cdata_time:<{col_steps+2}}"
                   f"{monday_time:<{col_steps+2}}"
                   f"{graph_time:<{col_steps+2}}"
                   f"{full_time:<{col_steps+2}}")
        
        print(row_str)
    
    print("="*160 + "\n")

def analyze_prompt_performance(prompt_id):
    """Generate performance comparison tables for a specific prompt"""
    conn = sqlite3.connect(db_path)
    
    # Check if prompt exists
    prompt_check = pd.read_sql_query("""
        SELECT COUNT(*) as count, raw_user_prompt
        FROM executions
        WHERE prompt_id = ?
        GROUP BY raw_user_prompt
    """, conn, params=(prompt_id,))
    
    if prompt_check.empty:
        print(f"\n❌ No data found for prompt_id: {prompt_id}")
        conn.close()
        return
    
    prompt_text = prompt_check['raw_user_prompt'].iloc[0]
    print(f"Use Case {prompt_id}\n{prompt_text[:]}")
    
    # Get execution data for the prompt
    df_exec = pd.read_sql_query("""
        SELECT 
            server_type,
            execution_time_s,
            llm_time_s,
            mcp_time_s,
            total_tokens,
            input_tokens,
            output_tokens,
            total_steps
        FROM executions
        WHERE prompt_id = ?
        ORDER BY server_type
    """, conn, params=(prompt_id,))
    
    if df_exec.empty:
        print(f"\n❌ No execution data found for prompt_id: {prompt_id}")
        conn.close()
        return
    
    # Get all token counts for efficiency rating comparison
    all_tokens = df_exec['total_tokens'].tolist()
    
    # TABLE 1: Execution Metrics
    print("Execution Metrics")
    print(f"{'='*80}")
    print(f"{'Metric':<30} ", end="")
    for _, row in df_exec.iterrows():
        server_name = row['server_type'].upper()
        if server_name == 'CDATA':
            server_name = 'CData Monday'
        elif server_name == 'STATIC':
            server_name = 'Local Native (Static)'
        elif server_name == 'DYNAMIC':
            server_name = 'Local Native (Dynamic)'
        elif server_name == 'FULL':
            server_name = 'Local Native (Full)'
        print(f"{server_name:<25}", end="")
    print()
    print("-" * 80)
    
    # Total Time
    print(f"{'Total Time':<30} ", end="")
    for _, row in df_exec.iterrows():
        total_time = row['llm_time_s'] + row['mcp_time_s']
        print(f"{format_time(total_time):<25}", end="")
    print()
    
    # MCP Time
    print(f"{'MCP Time':<30} ", end="")
    for _, row in df_exec.iterrows():
        print(f"{format_time(row['mcp_time_s']):<25}", end="")
    print()
    
    # LLM Time
    print(f"{'LLM Time':<30} ", end="")
    for _, row in df_exec.iterrows():
        print(f"{format_time(row['llm_time_s']):<25}", end="")
    print()
    
    # Execution Time (actual wall clock time)
    print(f"{'Execution Time':<30} ", end="")
    for _, row in df_exec.iterrows():
        print(f"{format_time(row['execution_time_s']):<25}", end="")
    print()
    
    # Total Steps
    print(f"{'Total Steps':<30} ", end="")
    for _, row in df_exec.iterrows():
        print(f"{int(row['total_steps']):<25}", end="")
    print()
    
    # TABLE 2: Token Metrics
    print(f"\n{'='*80}")
    print("AI Token Costs")
    print(f"{'='*80}")
    print(f"{'Metric':<30} ", end="")
    for _, row in df_exec.iterrows():
        server_name = row['server_type'].upper()
        if server_name == 'CDATA':
            server_name = 'CData Monday'
        elif server_name == 'STATIC':
            server_name = 'Local Native (Static)'
        elif server_name == 'DYNAMIC':
            server_name = 'Local Native (Dynamic)'
        elif server_name == 'FULL':
            server_name = 'Local Native (Full)'
        print(f"{server_name:<25}", end="")
    print()
    print("-" * 80)
    
    # Total Tokens
    print(f"{'Total Token Count':<30} ", end="")
    for _, row in df_exec.iterrows():
        print(f"{int(row['total_tokens']):,} tokens{'':<10}", end="")
    print()
    
    # Token Efficiency with ratings (based on ranking)
    print(f"{'Token Consumption':<30} ", end="")
    for _, row in df_exec.iterrows():
        rating = get_efficiency_rating(row['total_tokens'], all_tokens)
        print(f"{rating:<25}", end="")
    print()
    
    print(f"\n{'='*80}\n")
    
    conn.close()

def list_available_prompts():
    """List all available prompt IDs"""
    conn = sqlite3.connect(db_path)
    
    df = pd.read_sql_query("""
        SELECT DISTINCT 
            prompt_id,
            raw_user_prompt,
            COUNT(DISTINCT server_type) as server_count
        FROM executions
        GROUP BY prompt_id, raw_user_prompt
        ORDER BY prompt_id
    """, conn)
    
    print("\n=== AVAILABLE PROMPTS ===")
    for _, row in df.iterrows():
        prompt_preview = row['raw_user_prompt'][:80] + "..." if len(row['raw_user_prompt']) > 80 else row['raw_user_prompt']
        print(f"Prompt {row['prompt_id']:2d} ({row['server_count']} servers): {prompt_preview}")
    
    conn.close()
    return df

if __name__ == "__main__":
    # List available prompts
    available_prompts = list_available_prompts()
    
    # Get user input
    print("\n" + "="*80)
    print("Options:")
    print("  Enter a prompt number to analyze a specific use case")
    print("  Enter 'full' or 'all' to see the full report for all use cases")
    print("="*80)
    
    try:
        user_input = input("Enter your choice: ").strip().lower()
        
        if user_input in ['full', 'all']:
            print_full_report()
        else:
            prompt_id = int(user_input)
            analyze_prompt_performance(prompt_id)
    except ValueError:
        print("❌ Invalid input. Please enter a number or 'full'/'all'.")
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")