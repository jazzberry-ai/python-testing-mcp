"""
MCP tool integration for the unit testing generator.
"""

import os
import json
from typing import Dict, List, Any, Optional
from tools.registry import BaseTool
from .generator import UnitTestGenerator


class UnitTestTool(BaseTool):
    """MCP tool for generating Python unit tests."""
    
    def __init__(self):
        """Initialize the unit test tool."""
        self.generator = UnitTestGenerator(os.getenv('GEMINI_API_KEY'))
    
    @property
    def name(self) -> str:
        """Tool name."""
        return "unit_testing_tool"
    
    @property
    def description(self) -> str:
        """Tool description."""
        return "Generate comprehensive unit tests for Python code"
    
    @property
    def version(self) -> str:
        """Tool version."""
        return "1.0.0"
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions."""
        return [
            {
                "name": "generate_unit_tests",
                "description": "Generate comprehensive unit tests for a Python file. Returns complete test file content that can be saved and used immediately.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python file to generate tests for"
                        },
                        "framework": {
                            "type": "string",
                            "enum": ["pytest", "unittest"],
                            "default": "pytest",
                            "description": "Testing framework to use (pytest or unittest)"
                        },
                        "output_dir": {
                            "type": "string",
                            "description": "Optional: Directory to save the test file (defaults to same directory as source file)",
                            "default": "."
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "generate_test_file_content",
                "description": "Generate unit test file content without saving to disk. Returns the complete test file as a string.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python file to generate tests for"
                        },
                        "framework": {
                            "type": "string",
                            "enum": ["pytest", "unittest"],
                            "default": "pytest",
                            "description": "Testing framework to use (pytest or unittest)"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "analyze_test_coverage_gaps",
                "description": "Analyze a Python file and suggest specific unit tests needed to improve coverage.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python file to analyze"
                        },
                        "existing_test_file": {
                            "type": "string",
                            "description": "Optional: Path to existing test file to analyze what's already covered"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]
    
    def can_handle(self, tool_name: str) -> bool:
        """Check if the unit test tool can handle the given tool name."""
        return tool_name in ["generate_unit_tests", "generate_test_file_content", "analyze_test_coverage_gaps"]

    async def handle_mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle MCP tool calls."""
        try:
            if tool_name == "generate_unit_tests":
                return await self._generate_unit_tests(arguments)
            elif tool_name == "generate_test_file_content":
                return await self._generate_test_file_content(arguments)
            elif tool_name == "analyze_test_coverage_gaps":
                return await self._analyze_test_coverage_gaps(arguments)
            else:
                # This case should ideally not be reached if can_handle is used correctly
                raise ValueError(f"Tool {tool_name} not implemented by unit test tool")
        except Exception as e:
            return [{"text": f"Error in {tool_name}: {str(e)}"}]
    
    async def _generate_unit_tests(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate and save unit tests."""
        file_path = arguments["file_path"]
        framework = arguments.get("framework", "pytest")
        output_dir = arguments.get("output_dir", os.path.dirname(file_path) if os.path.dirname(file_path) else ".")
        
        if not os.path.exists(file_path):
            return [{"text": f"Error: File '{file_path}' not found"}]
        
        try:
            # Generate test suite
            test_suite = self.generator.generate_test_suite(file_path, framework)
            
            # Save test file
            saved_path = self.generator.save_test_file(test_suite, output_dir, framework)
            
            # Generate summary
            num_tests = len(test_suite.test_cases)
            summary = f"""✅ **Unit Tests Generated Successfully**

**Target File**: `{file_path}`
**Test File**: `{saved_path}`
**Framework**: {framework}
**Tests Generated**: {num_tests}

**Test File Structure**:
- Test class: `{test_suite.test_class_name}` (unittest) or standalone functions (pytest)
- Import statements: {len(test_suite.imports)} imports
- Test cases covering:
  - Happy path scenarios
  - Edge cases and boundary conditions  
  - Error handling and exceptions
  - AI-generated comprehensive test cases

**Generated Test Cases**:
"""
            
            for i, test_case in enumerate(test_suite.test_cases, 1):
                summary += f"{i}. `{test_case.name}` - {test_case.description}\n"
            
            summary += f"""
**Usage**:
```bash
# Run with pytest
pytest {saved_path}

# Run with unittest (if using unittest framework)
python {saved_path}
```

The test file is ready to use and contains TODO comments where specific test data needs to be added."""
            
            return [{"text": summary}]
            
        except Exception as e:
            return [{"text": f"Error generating unit tests: {str(e)}"}]
    
    async def _generate_test_file_content(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test file content without saving."""
        file_path = arguments["file_path"]
        framework = arguments.get("framework", "pytest")
        
        if not os.path.exists(file_path):
            return [{"text": f"Error: File '{file_path}' not found"}]
        
        try:
            # Generate test suite
            test_suite = self.generator.generate_test_suite(file_path, framework)
            
            # Generate content
            content = self.generator.generate_test_file_content(test_suite, framework)
            
            # Create response
            summary = f"""# Generated Unit Test File Content

**Framework**: {framework}
**Target File**: `{file_path}`
**Test File Name**: `{test_suite.test_file_name}`

## Complete Test File Content:

```python
{content}
```

## Summary:
- **Tests Generated**: {len(test_suite.test_cases)}
- **Framework**: {framework}
- **Ready to use**: Copy the content above into `{test_suite.test_file_name}`

## Test Cases Included:
"""
            
            for i, test_case in enumerate(test_suite.test_cases, 1):
                summary += f"{i}. `{test_case.name}` - {test_case.description}\n"
            
            return [{"text": summary}]
            
        except Exception as e:
            return [{"text": f"Error generating test content: {str(e)}"}]
    
    async def _analyze_test_coverage_gaps(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze test coverage gaps and suggest improvements."""
        file_path = arguments["file_path"]
        existing_test_file = arguments.get("existing_test_file")
        
        if not os.path.exists(file_path):
            return [{"text": f"Error: File '{file_path}' not found"}]
        
        try:
            # Import analyzer here to avoid circular imports
            from ..fuzzer.analyzer import CodeAnalyzer
            
            analyzer = CodeAnalyzer(file_path)
            functions = analyzer.extract_functions()
            classes = analyzer.get_classes()
            
            # Analyze existing tests if provided
            existing_tests = []
            if existing_test_file and os.path.exists(existing_test_file):
                test_analyzer = CodeAnalyzer(existing_test_file)
                existing_functions = test_analyzer.extract_functions()
                existing_tests = [f.name for f in existing_functions if f.name.startswith('test_')]
            
            # Generate analysis
            analysis = f"""# Test Coverage Gap Analysis

**Target File**: `{file_path}`
**Functions Found**: {len(functions)}
**Classes Found**: {len(classes)}
**Existing Tests**: {len(existing_tests)}

## Functions Needing Tests:

"""
            
            untested_functions = []
            for func in functions:
                if not func.name.startswith('_'):  # Skip private functions
                    # Check if this function has tests
                    has_test = any(test_name.find(func.name) != -1 for test_name in existing_tests)
                    if not has_test:
                        untested_functions.append(func)
                        analysis += f"### `{func.name}()`\n"
                        analysis += f"- **Signature**: `{func.signature}`\n"
                        analysis += f"- **Line**: {func.line_number}\n"
                        if func.docstring:
                            analysis += f"- **Description**: {func.docstring[:100]}...\n"
                        analysis += f"- **Suggested Tests**:\n"
                        analysis += f"  - Happy path with valid inputs\n"
                        analysis += f"  - Edge cases (empty/null inputs)\n"
                        analysis += f"  - Error conditions and exceptions\n"
                        analysis += f"  - Boundary value testing\n\n"
            
            if classes:
                analysis += "## Classes Needing Tests:\n\n"
                for class_name in classes:
                    analysis += f"### `{class_name}`\n"
                    analysis += f"- **Suggested Tests**:\n"
                    analysis += f"  - Constructor testing\n"
                    analysis += f"  - Method testing for each public method\n"
                    analysis += f"  - State management testing\n"
                    analysis += f"  - Integration testing between methods\n\n"
            
            # Summary
            analysis += f"""## Summary:
- **Functions needing tests**: {len(untested_functions)}
- **Priority**: Focus on public functions with complex logic
- **Recommendation**: Generate tests using the `generate_unit_tests` tool

## Next Steps:
1. Use `generate_unit_tests` to create comprehensive test file
2. Focus on functions with complex logic or error handling
3. Add integration tests for class interactions
4. Consider property-based testing for mathematical functions"""
            
            return [{"text": analysis}]
            
        except Exception as e:
            return [{"text": f"Error analyzing coverage gaps: {str(e)}"}]


def get_tool() -> UnitTestTool:
    """Get the unit test tool instance."""
    return UnitTestTool()