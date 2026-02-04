class ToolsManager:
    """Handles all tool-related operations for an MCP session."""
    
    def __init__(self, session):
        """
        Args:
            session: Active MCP session from mcp_client.session()
        """
        self.session = session
        self._tools = []
        self._tools_metadata = {}
    
    async def load_tools(self, enable_error_passthrough=True):
        """
        Load all tools from the MCP session.
        
        Returns:
            List of LangChain tool objects ready to use
        """
        from langchain_mcp_adapters.tools import load_mcp_tools
        
        print("Loading MCP tools from persistent session...")
        self._tools = await load_mcp_tools(self.session)
        print(f"Loaded {len(self._tools)} tools")
        
        if enable_error_passthrough:
            self._enable_error_passthrough()
        
        return self._tools
    
    def _enable_error_passthrough(self):
        """Enable error passthrough for all tools."""
        for tool in self._tools:
            if hasattr(tool, "handle_tool_error"):
                tool.handle_tool_error = True
            if hasattr(tool, "handle_validation_error"):
                tool.handle_validation_error = True
    
    def get_tools(self):
        """Get currently loaded tools."""
        return self._tools
    
    def get_tool_names(self):
        """Get list of tool names."""
        return [tool.name for tool in self._tools]
    
    def get_tool_by_name(self, name):
        """Get specific tool by name."""
        for tool in self._tools:
            if tool.name == name:
                return tool
        return None
