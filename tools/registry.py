"""
Tool Registry System

Manages dynamic discovery and registration of testing tools.
"""

from typing import Dict, List, Type, Any, Optional
from abc import ABC, abstractmethod
import importlib
import os


class BaseTool(ABC):
    """Base class for all testing tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Tool version."""
        pass
    
    @abstractmethod
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions for this tool."""
        pass
    
    @abstractmethod
    @abstractmethod
    def can_handle(self, tool_name: str) -> bool:
        """Check if the tool can handle the given tool name."""
        pass

    @abstractmethod
    async def handle_mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle MCP tool calls for this tool."""
        pass


class ToolRegistry:
    """Registry for managing testing tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._auto_discover()
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def get_all_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions for all registered tools."""
        mcp_tools = []
        for tool in self._tools.values():
            mcp_tools.extend(tool.get_mcp_tools())
        return mcp_tools
    
    async def handle_mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Route MCP calls to the appropriate tool."""
        for tool_instance in self._tools.values():
            if tool_instance.can_handle(tool_name):
                return await tool_instance.handle_mcp_call(tool_name, arguments)
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    def _auto_discover(self) -> None:
        """Automatically discover and register tools."""
        tools_dir = os.path.dirname(__file__)
        
        for item in os.listdir(tools_dir):
            tool_dir = os.path.join(tools_dir, item)
            
            # Skip files and non-tool directories
            if not os.path.isdir(tool_dir) or item.startswith('_'):
                continue
            
            # Try to import and register the tool
            try:
                module_name = f"tools.{item}.tool"
                module = importlib.import_module(module_name)
                
                if hasattr(module, 'get_tool'):
                    tool = module.get_tool()
                    if isinstance(tool, BaseTool):
                        self.register_tool(tool)
            except (ImportError, AttributeError):
                # Tool doesn't follow the expected structure, skip it
                continue