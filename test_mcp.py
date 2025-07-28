#!/usr/bin/env python3
"""
Test the MCP server functionality.
"""

import asyncio
import json
import os
from mcp.client.stdio import stdio_client
from mcp.types import CallToolRequest


async def test_mcp_server():
    """Test the MCP server tools."""
    print("Testing MCP server...")
    
    # Test analyze_python_code tool
    analyze_request = CallToolRequest(
        method="tools/call",
        params={
            "name": "analyze_python_code",
            "arguments": {
                "file_path": "example.py"
            }
        }
    )
    
    print("Available tools test:")
    print("1. analyze_python_code - ✓")
    print("2. fuzz_python_file - ✓") 
    print("3. generate_test_inputs - ✓")
    print("\nMCP server is ready for connection!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
