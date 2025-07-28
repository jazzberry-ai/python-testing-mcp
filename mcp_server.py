#!/usr/bin/env python3
"""
MCP Server for Python Fuzzing Tool

This implements a Model Context Protocol server that exposes the fuzzing tool
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
from pydantic import BaseModel

from fuzzer.fuzzer import PythonFuzzer
from fuzzer.analyzer import CodeAnalyzer


# MCP Server instance
server = Server("python-fuzzing-tool")


class FuzzFileArgs(BaseModel):
    """Arguments for the fuzz_file tool."""
    file_path: str
    num_tests: int = 10
    specific_function: Optional[str] = None


class AnalyzeCodeArgs(BaseModel):
    """Arguments for the analyze_code tool."""
    file_path: str


class GenerateTestsArgs(BaseModel):
    """Arguments for the generate_tests tool."""
    function_code: str
    function_signature: str
    num_tests: int = 5


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available fuzzing tools."""
    return [
        Tool(
            name="fuzz_python_file",
            description="Fuzz test all functions in a Python file using AI-generated test cases",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the Python file to fuzz test"
                    },
                    "num_tests": {
                        "type": "integer",
                        "description": "Number of test cases to generate per function (default: 10)",
                        "default": 10
                    },
                    "specific_function": {
                        "type": "string",
                        "description": "Optional: specific function name to fuzz (default: all functions)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="analyze_python_code",
            description="Analyze a Python file to extract function information and structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the Python file to analyze"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="generate_test_inputs",
            description="Generate AI-powered test inputs for a specific function",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_code": {
                        "type": "string",
                        "description": "The complete function code to generate tests for"
                    },
                    "function_signature": {
                        "type": "string",
                        "description": "The function signature (e.g., 'add(a, b)')"
                    },
                    "num_tests": {
                        "type": "integer",
                        "description": "Number of test cases to generate (default: 5)",
                        "default": 5
                    }
                },
                "required": ["function_code", "function_signature"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return [TextContent(
            type="text",
            text="Error: GEMINI_API_KEY environment variable not set. Please set your Gemini API key."
        )]
    
    try:
        if name == "fuzz_python_file":
            args = FuzzFileArgs(**arguments)
            return await fuzz_python_file(args)
        
        elif name == "analyze_python_code":
            args = AnalyzeCodeArgs(**arguments)
            return await analyze_python_code(args)
        
        elif name == "generate_test_inputs":
            args = GenerateTestsArgs(**arguments)
            return await generate_test_inputs(args)
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def fuzz_python_file(args: FuzzFileArgs) -> List[TextContent]:
    """Fuzz test a Python file."""
    # Validate file path
    if not args.file_path or not args.file_path.strip():
        return [TextContent(
            type="text",
            text="Error: File path cannot be empty. Please provide a valid file path."
        )]
    
    # Convert relative path to absolute for better error reporting
    abs_path = os.path.abspath(args.file_path)
    
    if not os.path.exists(abs_path):
        return [TextContent(
            type="text",
            text=f"Error: File '{abs_path}' not found. Please check the file path and ensure it exists."
        )]
    
    if not args.file_path.endswith('.py'):
        return [TextContent(
            type="text",
            text=f"Error: File '{args.file_path}' must be a Python file (.py). Please provide a valid Python file."
        )]
    
    # Validate num_tests parameter
    if args.num_tests <= 0:
        return [TextContent(
            type="text",
            text=f"Error: Number of tests must be positive, got {args.num_tests}. Please provide a valid number."
        )]
    
    try:
        fuzzer = PythonFuzzer(api_key)
        
        if args.specific_function:
            # Fuzz specific function
            fuzzer.load_target_file(args.file_path)
            functions = fuzzer.analyzer.extract_functions()
            
            target_func = None
            for func in functions:
                if func.name == args.specific_function:
                    target_func = func
                    break
            
            if not target_func:
                available_functions = [f.name for f in functions]
                return [TextContent(
                    type="text",
                    text=f"Error: Function '{args.specific_function}' not found.\nAvailable functions: {', '.join(available_functions)}"
                )]
            
            report = fuzzer.fuzz_function(target_func, args.num_tests)
            reports = [report]
        else:
            # Fuzz all functions
            reports = fuzzer.fuzz_all_functions(args.file_path, args.num_tests)
        
        # Format results
        result_text = format_fuzz_results(reports)
        
        return [TextContent(type="text", text=result_text)]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error fuzzing file '{args.file_path}': {str(e)}. Please check the file syntax and try again."
        )]


async def analyze_python_code(args: AnalyzeCodeArgs) -> List[TextContent]:
    """Analyze Python code structure."""
    # Validate file path
    if not args.file_path or not args.file_path.strip():
        return [TextContent(
            type="text",
            text="Error: File path cannot be empty. Please provide a valid file path."
        )]
    
    # Convert relative path to absolute for better error reporting
    abs_path = os.path.abspath(args.file_path)
    
    if not os.path.exists(abs_path):
        return [TextContent(
            type="text",
            text=f"Error: File '{abs_path}' not found. Please verify the file path is correct."
        )]
    
    if not args.file_path.endswith('.py'):
        return [TextContent(
            type="text",
            text=f"Error: File '{args.file_path}' must be a Python file (.py). Please provide a valid Python file."
        )]
    
    try:
        analyzer = CodeAnalyzer(args.file_path)
        functions = analyzer.extract_functions()
        imports = analyzer.get_imports()
        classes = analyzer.get_classes()
        
        result = f"# Code Analysis: {args.file_path}\n\n"
        
        if imports:
            result += f"## Imports ({len(imports)})\n"
            for imp in imports:
                result += f"- {imp}\n"
            result += "\n"
        
        if classes:
            result += f"## Classes ({len(classes)})\n"
            for cls in classes:
                result += f"- {cls}\n"
            result += "\n"
        
        if functions:
            result += f"## Functions ({len(functions)})\n"
            for func in functions:
                result += f"- **{func.name}** (line {func.line_number})\n"
                result += f"  - Signature: `{func.signature}`\n"
                if func.docstring:
                    result += f"  - Description: {func.docstring.split('.')[0]}.\n"
                result += f"  - Method: {'Yes' if func.is_method else 'No'}\n\n"
        else:
            result += "No functions found.\n"
        
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error analyzing code in '{args.file_path}': {str(e)}. Please ensure the file contains valid Python code."
        )]


async def generate_test_inputs(args: GenerateTestsArgs) -> List[TextContent]:
    """Generate test inputs for a specific function."""
    # Validate inputs
    if not args.function_code or not args.function_code.strip():
        return [TextContent(
            type="text",
            text="Error: Function code cannot be empty. Please provide valid function code."
        )]
    
    if not args.function_signature or not args.function_signature.strip():
        return [TextContent(
            type="text",
            text="Error: Function signature cannot be empty. Please provide a valid function signature."
        )]
    
    if args.num_tests <= 0:
        return [TextContent(
            type="text",
            text=f"Error: Number of tests must be positive, got {args.num_tests}. Please provide a valid number."
        )]
    
    try:
        from fuzzer.gemini_client import GeminiClient
        
        client = GeminiClient()
        test_inputs = client.generate_fuzzing_inputs(
            args.function_signature,
            args.function_code,
            args.num_tests
        )
        
        if not test_inputs:
            return [TextContent(
                type="text",
                text=f"Failed to generate test inputs for function '{args.function_signature}'. Please verify the function code is valid and the Gemini API is accessible."
            )]
        
        result = f"# Generated Test Inputs for {args.function_signature}\n\n"
        
        for i, test_input in enumerate(test_inputs, 1):
            result += f"## Test Case {i}: {test_input.get('description', 'No description')}\n"
            result += f"- **Expected Behavior**: {test_input.get('expected_behavior', 'unknown')}\n"
            result += f"- **Arguments**: {test_input.get('args', [])}\n"
            result += f"- **Keyword Arguments**: {test_input.get('kwargs', {})}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error generating test inputs for '{args.function_signature}': {str(e)}. Please check the function code and API connectivity."
        )]


def format_fuzz_results(reports) -> str:
    """Format fuzzing results for display."""
    result = "# Fuzzing Results\n\n"
    
    # Summary
    total_functions = len(reports)
    total_tests = sum(report.total_tests for report in reports)
    total_crashes = sum(len(report.crashes) for report in reports)
    total_successful = sum(report.successful_tests for report in reports)
    
    result += f"## Summary\n"
    result += f"- **Functions tested**: {total_functions}\n"
    result += f"- **Total test cases**: {total_tests}\n"
    result += f"- **Successful tests**: {total_successful}\n"
    result += f"- **Total crashes**: {total_crashes}\n"
    
    if total_tests > 0:
        success_rate = (total_successful / total_tests) * 100
        result += f"- **Success rate**: {success_rate:.1f}%\n"
    
    result += "\n## Per-Function Results\n\n"
    
    for report in reports:
        status = "✅" if len(report.crashes) == 0 else "❌"
        result += f"### {status} {report.function_name}\n"
        result += f"- Tests: {report.successful_tests}/{report.total_tests} passed\n"
        result += f"- Crashes: {len(report.crashes)}\n"
        
        if report.crashes:
            result += f"\n**Crash Details:**\n"
            for i, crash in enumerate(report.crashes[:3], 1):  # Show first 3 crashes
                result += f"{i}. {crash.test_input.get('description', 'Unknown test')}\n"
                result += f"   - Error: {crash.error.split('Traceback')[0].strip()}\n"
        
        if report.analysis:
            result += f"\n**AI Analysis:**\n{report.analysis[:500]}...\n"
        
        result += "\n"
    
    if total_crashes > 0:
        result += f"\n⚠️ **Found {total_crashes} crashes that need investigation!**\n"
    
    return result


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
