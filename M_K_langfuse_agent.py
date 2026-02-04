import asyncio
import json
import os
import time
import re
from datetime import datetime
from dotenv import load_dotenv

from mcp_manager.tools_manager import ToolsManager
load_dotenv(dotenv_path=r'C:\Users\MikelKulla\Desktop\langfuse_template\.env')

# MUST come before any HTTP library imports
from env_setup import configure_proxy_and_certs, enable_error_passthrough
configure_proxy_and_certs()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler

from server_configs import __version__, __author__, __description__, __last_updated__, get_server_configurations
from prompts import ALL_PROMPTS
from callbacks import CleanStatsCallback


# ====================== MAIN WITH PERSISTENT SESSION ======================
async def main():
    """
    Main execution function with persistent MCP session support.

    Features:
    - Persistent single-process MCP connections
    - Comprehensive logging and metrics
    - Multi-server configuration support
    - Langfuse integration for observability
    """
    start_time = time.perf_counter()

    # Print version banner
    print("=" * 70)
    print(f"  {__description__}")
    print(f"  Version: {__version__} | Author: {__author__}")
    print(f"  Last Updated: {__last_updated__}")
    print("=" * 70)
    print()

    # Get Monday API token from environment
    monday_token = os.environ.get("MONDAY_API_KEY")
    if not monday_token:
        raise ValueError("MONDAY_API_KEY not found in environment variables")
    # =======================================================================================================================================
    # =======================================================================================================================================
    # CHANGE THIS TO SWITCH SERVERS
    active_server = "cdata_monday"
    active_server = "native_monday_static"
    active_server = "native_monday_dynamic"
    active_server = "native_monday_full"
    active_server = "cdata_jira_mcp"
    active_server = "cdata_monday_mcp_custom"
    active_server = "cdata_bc365_mcp_custom"
    active_server = "cdata_bc365_mcp"
    # =======================================================================================================================================
    # =======================================================================================================================================
    connections_map = get_server_configurations(monday_token)

    if active_server not in connections_map:
        raise ValueError(
            f"Server '{active_server}' not configured. "
            f"Available: {', '.join(connections_map.keys())}"
        )

    config = connections_map[active_server]
    print(f"Selected Server: {active_server}")
    print(f"   Description: {config['description']}")
    print()

    # CRITICAL FIX: Give native server time to start
    if config["is_native"]:
        print(f"Starting native Monday MCP server ({active_server})... waiting 3 seconds")
        await asyncio.sleep(3)

    # Create MCP client
    print(f"Creating MCP client for '{active_server}'...")
    mcp_client = MultiServerMCPClient(
        connections={active_server: {k: v for k, v in config.items() if k not in ["is_native", "description"]}}
    )
    print("MCP client created")

    # ═══════════════════════════════════════════════════════════════
    # USE PERSISTENT SESSION - SINGLE PROCESS ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════
    print(f"Opening persistent session for '{active_server}' server...")
    async with mcp_client.session(active_server) as session:
        print(f"Persistent session opened")

        tools_manager = ToolsManager(session)
        # Optional retry for native servers
        for attempt in range(2):
            try:
                safe_tools = await tools_manager.load_tools()
                break
            except Exception as e:
                if attempt == 0 and config["is_native"]:
                    print("Native server not ready yet, retrying in 2s...")
                    await asyncio.sleep(2)
                else:
                    raise e

        llm = ChatAnthropic(
            model=os.environ["MODEL"],
            temperature=1,
            api_key=os.environ["ANTHROPIC_API_KEY"],
            max_tokens=10000,
            max_retries=6
        )

        agent = create_agent(llm, safe_tools)
        print("Agent created with persistent session tools")

        # ===== PROMPT SELECTION =====
        idx = 48
        idx -= 1
        run_number, user_prompt = ALL_PROMPTS[idx]

        # Generate clean filename
        clean_snippet = re.sub(r'[^a-zA-Z0-9]', '', user_prompt.replace(" ", ""))[:10]
        base_filename = f"{run_number}_{clean_snippet}"
        log_dir = r"C:\Users\MikelKulla\Desktop\langfuse_template\executions"

        # Include version in filename for tracking
        versioned_filename = f"v{__version__.replace('.', '_')}_{active_server}_{base_filename}"
        log_path = os.path.join(log_dir, f"{versioned_filename}.log")
        json_path = os.path.join(log_dir, f"{versioned_filename}.json")

        print(f"\n{'='*70}")
        print(f"Running prompt #{run_number} with PERSISTENT session")
        print(f"   Server: {active_server}")
        print(f"   Version: {__version__}")
        print(f"{'='*70}")
        print(f"Logs: {log_path}")
        print(f"JSON: {json_path}\n")

        # Stats dict - mutated by CleanStatsCallback
        stats = {
            'total_llm_time': 0.0,
            'total_tokens_input': 0,
            'total_tokens_output': 0,
            'total_mcp_time': 0.0,
            'conversation_steps': [],
        }

        # Load prompt history
        prompt_json_path = os.path.join(log_dir, f"prompt_{run_number}.json")
        if os.path.exists(prompt_json_path):
            try:
                with open(prompt_json_path, "r", encoding="utf-8") as f:
                    prompt_history = json.load(f)
                    if not isinstance(prompt_history, list):
                        prompt_history = []
            except:
                prompt_history = []
        else:
            prompt_history = []

        with open(log_path, "a", encoding="utf-8") as log_file:
            print("=" * 90, file=log_file, flush=True)
            print(f"  {__description__}", file=log_file, flush=True)
            print(f"  Version: {__version__} | Author: {__author__}", file=log_file, flush=True)
            print("=" * 90, file=log_file, flush=True)
            print(f"EXECUTION #{run_number} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=log_file, flush=True)
            print(f"Model: {os.environ['MODEL']} | Provider: Anthropic", file=log_file, flush=True)
            print(f"MCP Server: {active_server} | Session: PERSISTENT", file=log_file, flush=True)
            print(f"Server Description: {config['description']}", file=log_file, flush=True)
            print(f"Prompt: {user_prompt}", file=log_file, flush=True)
            print("=" * 90, file=log_file, flush=True)

            langfuse_handler = LangfuseCallbackHandler()
            stats_handler = CleanStatsCallback(log_file, stats)

            final_answer = ""
            trace_url = ""

            try:
                agent_config = {
                    "callbacks": [langfuse_handler, stats_handler],
                    "run_name": f"CData_v{__version__}_Exec_{run_number}",
                    "metadata": {
                        "framework_version": __version__,
                        "execution_number": run_number,
                        "model": os.environ["MODEL"],
                        "mcp_server": active_server,
                        "session_mode": "persistent",
                        "server_description": config['description']
                    },
                    "recursion_limit": 200,
                }

                response = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_prompt}]},
                    config=agent_config,
                )

                final_answer = response["messages"][-1].content

                print("\n" + "=" * 90, file=log_file, flush=True)
                print("FINAL ANSWER:", file=log_file, flush=True)
                print(final_answer, file=log_file, flush=True)
                print("=" * 90, file=log_file, flush=True)

                # Get trace URL safely
                try:
                    if hasattr(langfuse_handler, 'last_trace_id') and langfuse_handler.last_trace_id:
                        project_id = langfuse_handler.client.project_id or "default"
                        trace_url = f"https://cloud.langfuse.com/project/{project_id}/traces/{langfuse_handler.last_trace_id}"
                        print(f"\nLangfuse Trace: {trace_url}", file=log_file, flush=True)
                except:
                    trace_url = ""

            except Exception as e:
                final_answer = f"ERROR: {str(e)}"
                print(f"\nFATAL ERROR: {e}", file=log_file, flush=True)
                import traceback
                traceback.print_exc(file=log_file)

        # Save execution data with version info
        total_execution_time = time.perf_counter() - start_time

        current_execution = {
            "framework_version": __version__,
            "framework_author": __author__,
            "execution_timestamp": datetime.now().isoformat(),
            "execution_timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "mcp_server": active_server,
            "server_description": config['description'],
            "session_mode": "persistent",
            "execution_time_s": round(total_execution_time, 3),
            "raw_user_prompt": user_prompt,
            "prompt_id": run_number,
            "final_answer": final_answer,
            "langfuse_trace_url": trace_url,
            "summary": {
                "total_tokens": stats['total_tokens_input'] + stats['total_tokens_output'],
                "input_tokens": stats['total_tokens_input'],
                "output_tokens": stats['total_tokens_output'],
                "llm_time_s": round(stats['total_llm_time'], 3),
                "mcp_time_s": round(stats['total_mcp_time'], 3),
                "total_steps": len(stats['conversation_steps'])
            },
            "conversation_flow": stats['conversation_steps']
        }

        prompt_history.append(current_execution)

        # Save full history for this prompt
        with open(prompt_json_path, "w", encoding="utf-8") as f:
            json.dump(prompt_history, f, indent=2, ensure_ascii=False)

        # Save individual run JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(current_execution, f, indent=2, ensure_ascii=False)

        # Append summary to log
        with open(log_path, "a", encoding="utf-8") as log_file:
            print("\n" + "=" * 50, file=log_file, flush=True)
            print("                  EXECUTION SUMMARY                 ", file=log_file)
            print("=" * 50, file=log_file)
            print(f"  Framework Version: {__version__}", file=log_file)
            print(f"  Session Mode     : PERSISTENT (single process)", file=log_file)
            print(f"  Total Time       : {total_execution_time:.3f}s", file=log_file)
            print(f"  Total Tokens     : {stats['total_tokens_input'] + stats['total_tokens_output']}", file=log_file)
            print(f"  LLM Time         : {stats['total_llm_time']:.3f}s", file=log_file)
            print(f"  MCP Time         : {stats['total_mcp_time']:.3f}s", file=log_file)
            print(f"  Steps Recorded   : {len(stats['conversation_steps'])}", file=log_file)
            print(f"  JSON Saved       : {json_path}", file=log_file)
            print("=" * 50, file=log_file, flush=True)

        print("\nExecution complete! Everything saved:")
        print(f"   Log  : {log_path}")
        print(f"   JSON : {json_path}")
        if trace_url:
            print(f"   Trace: {trace_url}")

    # Session closes here automatically
    print("\nPersistent session closed - process terminated cleanly")
    print(f"Total execution time: {time.perf_counter() - start_time:.3f}s")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecution interrupted by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
