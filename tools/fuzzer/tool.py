"""
Python Fuzzer Tool - MCP Integration

Implements the fuzzer tool for the MCP server using the tool registry system.
"""

import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from ..registry import BaseTool
from .fuzzer import PythonFuzzer
from .analyzer import CodeAnalyzer


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


class PythonFuzzerTool(BaseTool):
    """Python fuzzer tool implementation."""
    
    @property
    def name(self) -> str:
        return "python-fuzzer"
    
    @property
    def description(self) -> str:
        return "AI-powered Python function fuzzing tool"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions for the fuzzer."""
        return [
            {
                "name": "fuzz_python_file",
                "description": "Fuzz test all functions in a Python file using AI-generated test cases",
                "inputSchema": {
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
            },
            {
                "name": "analyze_python_code",
                "description": "Analyze a Python file to extract function information and structure",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python file to analyze"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "generate_test_inputs",
                "description": "Generate AI-powered test inputs for a specific function",
                "inputSchema": {
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
            }
        ]
    
    def can_handle(self, tool_name: str) -> bool:
        """Check if the fuzzer tool can handle the given tool name."""
        return tool_name in ["fuzz_python_file", "analyze_python_code", "generate_test_inputs"]

    async def handle_mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle MCP tool calls for the fuzzer."""
        # Check for API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return [{
                "type": "text",
                "text": "Error: GEMINI_API_KEY environment variable not set. Please set your Gemini API key."
            }]
        
        try:
            if tool_name == "fuzz_python_file":
                args = FuzzFileArgs(**arguments)
                return await self._fuzz_python_file(args, api_key)
            
            elif tool_name == "analyze_python_code":
                args = AnalyzeCodeArgs(**arguments)
                return await self._analyze_python_code(args)
            
            elif tool_name == "generate_test_inputs":
                args = GenerateTestsArgs(**arguments)
                return await self._generate_test_inputs(args, api_key)
            
            else:
                # This case should ideally not be reached if can_handle is used correctly
                raise ValueError(f"Tool {tool_name} not handled by fuzzer")
        
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error executing {tool_name}: {str(e)}"
            }]
    
    async def _fuzz_python_file(self, args: FuzzFileArgs, api_key: str) -> List[Dict[str, Any]]:
        """Fuzz test a Python file."""
        # Validate file path
        if not args.file_path or not args.file_path.strip():
            return [{
                "type": "text",
                "text": "Error: File path cannot be empty. Please provide a valid file path."
            }]
        
        # Convert relative path to absolute for better error reporting
        abs_path = os.path.abspath(args.file_path)
        
        if not os.path.exists(abs_path):
            return [{
                "type": "text",
                "text": f"Error: File '{abs_path}' not found. Please check the file path and ensure it exists."
            }]
        
        if not args.file_path.endswith('.py'):
            return [{
                "type": "text",
                "text": f"Error: File '{args.file_path}' must be a Python file (.py). Please provide a valid Python file."
            }]
        
        # Validate num_tests parameter
        if args.num_tests <= 0:
            return [{
                "type": "text",
                "text": f"Error: Number of tests must be positive, got {args.num_tests}. Please provide a valid number."
            }]
        
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
                    return [{
                        "type": "text",
                        "text": f"Error: Function '{args.specific_function}' not found.\nAvailable functions: {', '.join(available_functions)}"
                    }]
                
                report = fuzzer.fuzz_function(target_func, args.num_tests)
                reports = [report]
            else:
                # Fuzz all functions
                reports = fuzzer.fuzz_all_functions(args.file_path, args.num_tests)
            
            # Format results
            result_text = self._format_fuzz_results(reports)
            
            return [{"type": "text", "text": result_text}]
        
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error fuzzing file '{args.file_path}': {str(e)}. Please check the file syntax and try again."
            }]
    
    async def _analyze_python_code(self, args: AnalyzeCodeArgs) -> List[Dict[str, Any]]:
        """Analyze Python code structure."""
        # Validate file path
        if not args.file_path or not args.file_path.strip():
            return [{
                "type": "text",
                "text": "Error: File path cannot be empty. Please provide a valid file path."
            }]
        
        # Convert relative path to absolute for better error reporting
        abs_path = os.path.abspath(args.file_path)
        
        if not os.path.exists(abs_path):
            return [{
                "type": "text",
                "text": f"Error: File '{abs_path}' not found. Please verify the file path is correct."
            }]
        
        if not args.file_path.endswith('.py'):
            return [{
                "type": "text",
                "text": f"Error: File '{args.file_path}' must be a Python file (.py). Please provide a valid Python file."
            }]
        
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
            
            return [{"type": "text", "text": result}]
        
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error analyzing code in '{args.file_path}': {str(e)}. Please ensure the file contains valid Python code."
            }]
    
    async def _generate_test_inputs(self, args: GenerateTestsArgs, api_key: str) -> List[Dict[str, Any]]:
        """Generate test inputs for a specific function."""
        # Validate inputs
        if not args.function_code or not args.function_code.strip():
            return [{
                "type": "text",
                "text": "Error: Function code cannot be empty. Please provide valid function code."
            }]
        
        if not args.function_signature or not args.function_signature.strip():
            return [{
                "type": "text",
                "text": "Error: Function signature cannot be empty. Please provide a valid function signature."
            }]
        
        if args.num_tests <= 0:
            return [{
                "type": "text",
                "text": f"Error: Number of tests must be positive, got {args.num_tests}. Please provide a valid number."
            }]
        
        try:
            from .gemini_client import GeminiClient
            
            client = GeminiClient()
            test_inputs = client.generate_fuzzing_inputs(
                args.function_signature,
                args.function_code,
                args.num_tests
            )
            
            if not test_inputs:
                return [{
                    "type": "text",
                    "text": f"Failed to generate test inputs for function '{args.function_signature}'. Please verify the function code is valid and the Gemini API is accessible."
                }]
            
            result = f"# Generated Test Inputs for {args.function_signature}\n\n"
            
            for i, test_input in enumerate(test_inputs, 1):
                result += f"## Test Case {i}: {test_input.get('description', 'No description')}\n"
                result += f"- **Expected Behavior**: {test_input.get('expected_behavior', 'unknown')}\n"
                result += f"- **Arguments**: {test_input.get('args', [])}\n"
                result += f"- **Keyword Arguments**: {test_input.get('kwargs', {})}\n\n"
            
            return [{"type": "text", "text": result}]
        
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error generating test inputs for '{args.function_signature}': {str(e)}. Please check the function code and API connectivity."
            }]
    
    def _format_fuzz_results(self, reports) -> str:
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


def get_tool() -> PythonFuzzerTool:
    """Get the fuzzer tool instance."""
    return PythonFuzzerTool()