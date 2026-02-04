# MCP Agent Framework with Langfuse Observability

**Version:** 1.0.1 | **Author:** Mikel Kulla | **Last Updated:** 2025-01-21

A production-ready framework for testing and benchmarking MCP (Model Context Protocol) server implementations using Anthropic's Claude as the AI agent. Features persistent MCP sessions, comprehensive execution logging, token/timing metrics, and Langfuse integration for full observability.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Usage](#usage)
  - [Running a Prompt](#running-a-prompt)
  - [Switching Servers](#switching-servers)
  - [Adding New Prompts](#adding-new-prompts)
- [Architecture](#architecture)
- [Supported MCP Servers](#supported-mcp-servers)
- [Output & Results](#output--results)
- [Analysis Tools](#analysis-tools)

---

## Quick Start

```bash
# 1. Clone/copy this folder
# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac
# Edit .env with your API keys

# 5. Create output directory
mkdir executions

# 6. Run
python M_K_langfuse_agent.py
```

---

## Project Structure

```
langfuse_template/
    M_K_langfuse_agent.py                      # Main entry point - run this
    env_setup.py                               # Proxy/SSL config + error passthrough
    server_configs.py                          # MCP server configurations + version info
    prompts.py                                 # Test prompt library (65 prompts)
    callbacks.py                               # LangChain callback handlers for metrics
    requirements.txt                           # Python dependencies
    .env                                       # Your API keys (git-ignored)
    .env.example                               # Template for .env
    utils/                                     # Post-execution analysis tools
        analyze_data.py                        #   Performance reports
        import_mcp_data.py                     #   JSON -> SQLite importer
        query_executor.py                      #   Interactive SQL query tool
    executions/                                # Output logs & JSON (git-ignored)
```

### What Each File Does

| File | Purpose |
|------|---------|
| `M_K_langfuse_agent.py` | Main orchestrator. Opens a persistent MCP session, creates a Claude agent, runs a selected prompt, tracks all metrics, and saves results to log + JSON files. |
| `env_setup.py` | Sets proxy/SSL environment variables and provides `enable_error_passthrough()` to make MCP tool errors visible instead of silently failing. |
| `server_configs.py` | Defines all available MCP server configurations (CData, Native Monday, Jira, BC365). Also holds framework version metadata. |
| `prompts.py` | Library of 65 test prompts grouped by domain: Monday.com (1-44) and Dynamics 365 Business Central (45-65). |
| `callbacks.py` | Two LangChain callback handlers: `DetailedLoggingCallbackHandler` for file logging, `CleanStatsCallback` for token/timing metric collection. |

---

## Setup

### Prerequisites

- **Python 3.10+**
- **Java JDK 21** (for CData MCP servers)
- **Node.js / npm** (for native Monday MCP server)
- **CData MCP Server** installed (for the connectors you want to test)

### 1. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
copy .env.example .env
```

Edit `.env` with your actual keys:

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `MODEL` | Yes | Claude model name (e.g., `claude-sonnet-4-5-20250929`) |
| `MONDAY_API_KEY` | Yes (If Monday native is used) | Monday.com API token (JWT) |
| `LANGFUSE_SECRET_KEY` | Yes | Langfuse project secret key |
| `LANGFUSE_PUBLIC_KEY` | Yes | Langfuse project public key |
| `LANGFUSE_HOST` | Yes | Langfuse instance URL (e.g., `https://cloud.langfuse.com`) |

### 3. Configure Proxy (if applicable)

If you're behind a corporate proxy, edit `env_setup.py`:

```python
os.environ["HTTP_PROXY"] = "http://127.0.0.1:8888"     # Your proxy
os.environ["SSL_CERT_FILE"] = r"C:\path\to\cert.pem"   # Your cert
```

If you don't use a proxy, you can comment out or clear those lines.

### 4. Create Output Directory

```bash
mkdir executions
```

### 5. Configure Server Paths

Edit `server_configs.py` to match your local CData installation paths. The default paths assume:
- CData MCP Server installed at `C:\Program Files\CData\...`
- Java JDK 21 at `C:\Program Files\Java\jdk-21\`

### 6. Configure logging & .env path
Edit `M_K_langfuse_agent.py` to match your desired path for logs & .env:
```python
log_dir = r"C:\Users\MikelKulla\Documents\CData_Projects\langfuse_template\executions"
```
```python
load_dotenv(dotenv_path=r'C:\Users\MikelKulla\Documents\CData_Projects\langfuse_template\.env')
```
---

## Usage

### Running a Prompt

**Step 1:** Open `M_K_langfuse_agent.py`

**Step 2:** Set which prompt to run (line ~123):
```python
idx = 48      # Change this to the prompt number you want
idx -= 1
run_number, user_prompt = ALL_PROMPTS[idx]
```

**Step 3:** Run:
```bash
python M_K_langfuse_agent.py
```

The framework will:
1. Open a persistent MCP session to the selected server
2. Load all available MCP tools
3. Create a Claude agent with those tools
4. Execute your prompt with full metric tracking
5. Save results to `executions/` as `.log` and `.json` files
6. Print a Langfuse trace URL for cloud-based inspection

### Switching Servers

In `M_K_langfuse_agent.py` (lines ~52-60), the last uncommented line wins:

```python
# CHANGE THIS TO SWITCH SERVERS
active_server = "cdata_monday"
active_server = "native_monday_static"
active_server = "native_monday_dynamic"
active_server = "native_monday_full"
active_server = "cdata_jira_mcp"
active_server = "cdata_monday_mcp_custom"
active_server = "cdata_bc365_mcp_custom"
active_server = "cdata_bc365_mcp"            # <-- this one runs
```

Comment out all but the server you want to test.

### Adding New Prompts

Edit `prompts.py` and add to the appropriate list:

```python
# For Monday.com / Jira prompts:
MONDAY_PROMPTS = [
    ...
    (44, "Your existing last prompt"),
    (NEW_ID, "Your new prompt text here"),
]

# For Dynamics 365 Business Central prompts:
BC365_PROMPTS = [
    ...
    (NEW_ID, "Your new BC365 prompt here"),
]
```

Rules:
- Prompt IDs must be unique and sequential
- Use the `LLM Note:` convention for agent constraints (e.g., `"LLM Note: Use only one tool at a time."`)
- Multi-line prompts use triple quotes (`"""..."""`)

---

## Architecture

```
User selects prompt + server
        |
        v
  M_K_langfuse_agent.py
        |
        +-- env_setup.py           (proxy/SSL configuration)
        +-- server_configs.py      (server connection details)
        +-- prompts.py             (prompt library)
        |
        v
  MultiServerMCPClient            (persistent stdio session)
        |
        v
  load_mcp_tools()                (discover server capabilities)
        |
        v
  ChatAnthropic (Claude)   +  MCP Tools  =  Agent
        |
        v
  agent.ainvoke(prompt)
        |
        +-- callbacks.py
        |     +-- CleanStatsCallback     (token counts, timing)
        |     +-- LangfuseCallbackHandler (cloud tracing)
        |
        v
  Results saved
        +-- executions/*.log       (human-readable trace)
        +-- executions/*.json      (structured metrics)
        +-- Langfuse cloud         (interactive trace viewer)
```

**Key design decisions:**
- **Persistent sessions:** One MCP process per run (not one per tool call). Dramatically reduces overhead.
- **Error passthrough:** MCP tool errors are surfaced to the agent instead of crashing silently.
- **Stats via dict:** The `CleanStatsCallback` mutates a shared `stats` dict rather than using closures, making it importable as a module.

---

## Supported MCP Servers (Add your own configs here)

| Key | Type | Backend | Transport |
|-----|------|---------|-----------|
| `cdata_monday` | CData | Monday.com via SQL | stdio (Java) |
| `native_monday_static` | Native | Monday.com GraphQL (static tools) | stdio (Node.js) |
| `native_monday_dynamic` | Native | Monday.com GraphQL (dynamic tools) | stdio (Node.js) |
| `native_monday_full` | Native | Monday.com GraphQL (all tools) | stdio (Node.js) |
| `cdata_jira_mcp` | CData | Jira via SQL | stdio (Java) |
| `cdata_monday_mcp_custom` | CData (Debug) | Monday.com via SQL (dev build) | stdio (Java) |
| `cdata_bc365_mcp` | CData | MS Dynamics 365 Business Central | stdio (Java) |
| `cdata_bc365_mcp_custom` | CData (Debug) | MS Dynamics 365 BC (dev build) | stdio (Java) |

To add a new server, add an entry to `get_server_configurations()` in `server_configs.py`.

---

## Output & Results

### File Naming Convention

```
v{version}_{server}_{promptID}_{snippet}.{ext}
```

Example: `v1_0_1_cdata_bc365_mcp_48_GivemeaLis.log`

### JSON Output Structure

Each execution produces a JSON file with:

```json
{
  "framework_version": "1.0.1",
  "execution_timestamp": "2025-01-21T14:30:45",
  "mcp_server": "cdata_bc365_mcp",
  "session_mode": "persistent",
  "execution_time_s": 42.567,
  "prompt_id": 48,
  "raw_user_prompt": "Give me a list of...",
  "final_answer": "Here are the results...",
  "langfuse_trace_url": "https://cloud.langfuse.com/project/.../traces/...",
  "summary": {
    "total_tokens": 5432,
    "input_tokens": 2100,
    "output_tokens": 3332,
    "llm_time_s": 8.234,
    "mcp_time_s": 12.456,
    "total_steps": 5
  },
  "conversation_flow": [
    { "type": "llm_response", "duration_s": 1.2, "input_tokens": 500, ... },
    { "type": "mcp_tool_call", "tool": "BC365_run_query", "duration_s": 2.3, ... }
  ]
}
```

---

## Analysis Tools

After running executions, use the `utils/` scripts to analyze results:

### 1. Import Results to SQLite

```bash
cd utils
python import_mcp_data.py
```

This imports all `prompt_*.json` files from `executions/` into `mcp_analysis.db`.

### 2. Run Performance Reports

```bash
python analyze_data.py
```

Interactive mode lets you:
- Compare execution metrics across servers for a specific prompt
- View a full cross-server comparison report

### 3. Custom SQL Queries

```bash
# Interactive mode
python query_executor.py

# Direct query
python query_executor.py -q "SELECT * FROM performance_comparison_by_server"

# Export to CSV
python query_executor.py -q "SELECT * FROM Full_Report" -o report.csv
```

Available views: `performance_comparison`, `tool_usage_stats`, `performance_comparison_by_server`, `Full_Report`, and more.

---
