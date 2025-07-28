#!/usr/bin/env python3
"""
MCP Server for Software Testing Agent

This implements a Model Context Protocol server that exposes multiple testing tools
functionality to MCP-compatible clients like Cursor, Claude, etc.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
)

from tools import ToolRegistry


# MCP Server instance
server = Server("software-testing-agent")
tool_registry = ToolRegistry()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available testing tools."""
    mcp_tools = tool_registry.get_all_mcp_tools()
    
    # Convert to MCP Tool objects
    tools = []
    for tool_def in mcp_tools:
        tools.append(Tool(
            name=tool_def["name"],
            description=tool_def["description"],
            inputSchema=tool_def["inputSchema"]
        ))
    
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        # Route call to appropriate tool via registry
        results = await tool_registry.handle_mcp_call(name, arguments)
        
        # Convert results to TextContent objects
        text_results = []
        for result in results:
            text_results.append(TextContent(
                type="text",
                text=result["text"]
            ))
        
        return text_results
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]




async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
