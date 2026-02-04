import time
from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.agents import AgentAction


# ====================== DETAILED LOGGING CALLBACK ======================
class DetailedLoggingCallbackHandler(BaseCallbackHandler):
    """Enhanced callback handler with detailed execution logging."""

    def __init__(self, log_file):
        self.log_file = log_file

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        print("\n=== LLM CALL STARTED ===", file=self.log_file, flush=True)
        self._llm_start_time = time.perf_counter()

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        duration = time.perf_counter() - self._llm_start_time
        usage = None
        if response.generations:
            msg = response.generations[0][0].message
            usage = getattr(msg, "usage_metadata", None) or msg.response_metadata.get("usage", {})

        print("LLM CALL FINISHED", file=self.log_file, flush=True)
        if usage:
            print(f"   Input tokens : {usage.get('input_tokens', 'N/A')}", file=self.log_file)
            print(f"   Output tokens: {usage.get('output_tokens', 'N/A')}", file=self.log_file)
            print(f"   Total tokens : {usage.get('total_tokens', 'N/A')}", file=self.log_file)
        else:
            print("   No token usage metadata", file=self.log_file)
        print(f"   Duration: {duration:.3f}s", file=self.log_file, flush=True)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "UnknownTool")
        print(f"\n>>> TOOL START: {tool_name}", file=self.log_file, flush=True)
        print(f"    Request -> {input_str}", file=self.log_file, flush=True)
        self._tool_start_time = time.perf_counter()
        self._current_tool_name = tool_name

    def on_tool_end(self, output: str, **kwargs) -> None:
        duration = time.perf_counter() - self._tool_start_time
        tool_name = getattr(self, "_current_tool_name", "UnknownTool")
        print(f"<<< TOOL END: {tool_name}", file=self.log_file, flush=True)
        print(f"    Response -> {output}", file=self.log_file, flush=True)
        print(f"    Tool duration: {duration:.3f}s", file=self.log_file, flush=True)

    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        print(f"\nAGENT ACTION -> Tool: {action.tool}", file=self.log_file, flush=True)
        print(f"    Input -> {action.tool_input}", file=self.log_file, flush=True)


# ====================== STATS-TRACKING CALLBACK ======================
class CleanStatsCallback(DetailedLoggingCallbackHandler):
    """Extended callback that captures token/timing statistics into a mutable stats dict.

    Args:
        log_file: Open file object for writing log lines.
        stats: A dict with keys:
            - 'total_llm_time' (float)
            - 'total_tokens_input' (int)
            - 'total_tokens_output' (int)
            - 'total_mcp_time' (float)
            - 'conversation_steps' (list)
            This callback will mutate these values during execution.
    """

    def __init__(self, log_file, stats: dict):
        super().__init__(log_file)
        self._stats = stats

    def on_llm_end(self, response: LLMResult, **kwargs):
        super().on_llm_end(response, **kwargs)
        duration = time.perf_counter() - self._llm_start_time

        self._stats['total_llm_time'] += duration
        usage = {}
        output_text = ""
        if response.generations:
            msg = response.generations[0][0].message
            output_text = msg.content if isinstance(msg.content, str) else str(msg.content)
            usage = getattr(msg, "usage_metadata", None) or msg.response_metadata.get("usage", {})

        self._stats['total_tokens_input'] += usage.get("input_tokens", 0)
        self._stats['total_tokens_output'] += usage.get("output_tokens", 0)

        self._stats['conversation_steps'].append({
            "type": "llm_response",
            "duration_s": round(duration, 3),
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "output_text": output_text
        })

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        tool_name = serialized.get("name", "Unknown")
        self._current_tool_name = tool_name
        self._current_tool_input = input_str
        super().on_tool_start(serialized, input_str, **kwargs)

    def on_tool_end(self, output: str, **kwargs):
        duration = time.perf_counter() - self._tool_start_time
        self._stats['total_mcp_time'] += duration
        print(f"<<< TOOL END: {self._current_tool_name}", file=self.log_file, flush=True)
        print(f"    Response -> {output}", file=self.log_file, flush=True)
        print(f"    Tool duration: {duration:.3f}s", file=self.log_file, flush=True)

        self._stats['conversation_steps'].append({
            "type": "mcp_tool_call",
            "tool": self._current_tool_name,
            "duration_s": round(duration, 3),
            "input": self._current_tool_input,
            "output": str(output)
        })
