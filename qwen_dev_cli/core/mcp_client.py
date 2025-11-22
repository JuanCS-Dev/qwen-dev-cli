"""MCP Client Adapter.

This module provides an adapter to make the internal ToolRegistry look like
an MCP (Model Context Protocol) client, satisfying the interface required
by BaseAgent.
"""

from typing import Any, Dict, Optional
from ..tools.base import ToolRegistry, ToolResult

class MCPClient:
    """Adapter for ToolRegistry to match MCP interface."""
    
    def __init__(self, registry: ToolRegistry):
        """Initialize with tool registry.
        
        Args:
            registry: The application's tool registry
        """
        self.registry = registry
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of arguments for the tool
            
        Returns:
            Tool execution result as a dictionary
            
        Raises:
            ValueError: If tool not found or arguments invalid
            Exception: If tool execution fails
        """
        tool = self.registry.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Validate parameters
        is_valid, error = tool.validate_params(**arguments)
        if not is_valid:
            raise ValueError(f"Invalid parameters for '{tool_name}': {error}")
        
        # Execute tool
        # Note: Accessing protected method as this is a trusted internal adapter
        try:
            result: ToolResult = await tool._execute_validated(**arguments)
        except Exception as e:
            raise Exception(f"Tool execution failed: {str(e)}")
        
        if not result.success:
            raise Exception(result.error or "Unknown tool execution error")
        
        # Normalize output to Dict[str, Any]
        if isinstance(result.data, dict):
            return result.data
        else:
            return {"output": result.data}
