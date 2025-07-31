"""
Mutation Testing Tool - MCP Integration

Implements mutation testing functionality for the MCP server using the tool registry system.
Provides comprehensive mutation testing with AI-powered analysis while ensuring complete safety.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from ..registry import BaseTool
from .mutator import SafeMutationEngine, safe_mutation_engine
from .runner import MutationTestRunner
from .baml_client import BamlMutationClient


class RunMutationTestsArgs(BaseModel):
    """Arguments for the run_mutation_tests tool."""
    file_path: str
    test_command: str = "python -m pytest"
    target_functions: Optional[List[str]] = None
    operator_names: Optional[List[str]] = None
    max_mutants: int = 50
    timeout_seconds: int = 30


class AnalyzeMutationResultsArgs(BaseModel):
    """Arguments for the analyze_mutation_results tool."""
    file_path: str
    results_json: str


class GenerateMutationStrategyArgs(BaseModel):
    """Arguments for the generate_mutation_strategy tool."""
    file_path: str
    target_functions: Optional[List[str]] = None


class SuggestTestImprovementsArgs(BaseModel):
    """Arguments for the suggest_test_improvements tool."""
    file_path: str
    results_json: str


class MutationTestingTool(BaseTool):
    """Mutation testing tool implementation."""
    
    @property
    def name(self) -> str:
        return "mutation-testing"
    
    @property
    def description(self) -> str:
        return "AI-powered mutation testing tool for Python code quality assessment"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions for mutation testing."""
        return [
            {
                "name": "run_python_mutation_tests",
                "description": "Run comprehensive mutation tests on Python code to assess test quality",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python file to test"
                        },
                        "test_command": {
                            "type": "string",
                            "description": "Command to run tests (default: 'python -m pytest')",
                            "default": "python -m pytest"
                        },
                        "target_functions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: specific function names to target for mutation"
                        },
                        "operator_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: specific mutation operators to use"
                        },
                        "max_mutants": {
                            "type": "integer",
                            "description": "Maximum number of mutants to generate (default: 50)",
                            "default": 50
                        },
                        "timeout_seconds": {
                            "type": "integer",
                            "description": "Timeout for each test run in seconds (default: 30)",
                            "default": 30
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "analyze_mutation_results",
                "description": "Analyze mutation testing results and provide AI-powered insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file that was tested"
                        },
                        "results_json": {
                            "type": "string",
                            "description": "JSON string containing mutation test results"
                        }
                    },
                    "required": ["file_path", "results_json"]
                }
            },
            {
                "name": "generate_mutation_strategy",
                "description": "Generate an AI-powered mutation testing strategy for Python code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Python file to analyze"
                        },
                        "target_functions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: specific function names to focus on"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "suggest_mutation_test_improvements",
                "description": "Suggest specific test improvements based on mutation testing results",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file that was tested"
                        },
                        "results_json": {
                            "type": "string",
                            "description": "JSON string containing mutation test results"
                        }
                    },
                    "required": ["file_path", "results_json"]
                }
            }
        ]
    
    def can_handle(self, tool_name: str) -> bool:
        """Check if the mutation testing tool can handle the given tool name."""
        return tool_name in [
            "run_python_mutation_tests",
            "analyze_mutation_results",
            "generate_mutation_strategy",
            "suggest_mutation_test_improvements"
        ]

    async def handle_mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle MCP tool calls for mutation testing."""
        try:
            if tool_name == "run_python_mutation_tests":
                args = RunMutationTestsArgs(**arguments)
                return await self._run_mutation_tests(args)
            
            elif tool_name == "analyze_mutation_results":
                args = AnalyzeMutationResultsArgs(**arguments)
                return await self._analyze_mutation_results(args)
            
            elif tool_name == "generate_mutation_strategy":
                args = GenerateMutationStrategyArgs(**arguments)
                return await self._generate_mutation_strategy(args)
            
            elif tool_name == "suggest_mutation_test_improvements":
                args = SuggestTestImprovementsArgs(**arguments)
                return await self._suggest_test_improvements(args)
            
            else:
                raise NotImplementedError(f"Tool {tool_name} not handled by mutation testing tool")
        
        except Exception as e:
            return [{
                "text": f"Error executing {tool_name}: {str(e)}"
            }]
    
    async def _run_mutation_tests(self, args: RunMutationTestsArgs) -> List[Dict[str, Any]]:
        """Run comprehensive mutation tests on Python code."""
        # Validate file path
        if not os.path.exists(args.file_path):
            return [{
                "text": f"Error: File '{args.file_path}' not found. Please check the file path."
            }]
        
        if not args.file_path.endswith('.py'):
            return [{
                "text": f"Error: File '{args.file_path}' must be a Python file (.py)."
            }]
        
        try:
            # Use safe mutation engine context manager
            with safe_mutation_engine() as engine:
                # Generate mutants
                mutants = engine.generate_mutants(
                    file_path=args.file_path,
                    target_functions=args.target_functions,
                    operator_names=args.operator_names,
                    max_mutants=args.max_mutants
                )
                
                if not mutants:
                    return [{
                        "text": f"No mutants could be generated for '{args.file_path}'. This might indicate:\n"
                               "- The file has no suitable code for mutation\n"
                               "- The specified functions were not found\n"
                               "- The specified operators are not applicable"
                    }]
                
                # Run mutation tests
                runner = MutationTestRunner(
                    test_command=args.test_command,
                    timeout_seconds=args.timeout_seconds
                )
                
                report = runner.run_mutation_tests(
                    mutants=mutants,
                    original_file_path=args.file_path
                )
                
                # Format results
                result_text = self._format_mutation_report(report, mutants)
                
                # Include JSON data for further analysis
                json_data = {
                    "report": report.to_dict(),
                    "mutants": [
                        {
                            "id": m.id,
                            "operator_name": m.operator_name,
                            "original_code": m.original_code,
                            "mutated_code": m.mutated_code,
                            "line_number": m.line_number,
                            "function_name": m.function_name,
                            "description": m.description
                        }
                        for m in mutants
                    ]
                }
                
                return [
                    {"text": result_text},
                    {"text": f"\n\n**Raw JSON Data (for analysis):**\n```json\n{json.dumps(json_data, indent=2)}\n```"}
                ]
        
        except Exception as e:
            return [{
                "text": f"Error running mutation tests on '{args.file_path}': {str(e)}"
            }]
    
    async def _analyze_mutation_results(self, args: AnalyzeMutationResultsArgs) -> List[Dict[str, Any]]:
        """Analyze mutation testing results using AI."""
        try:
            # Parse results JSON
            results_data = json.loads(args.results_json)
            
            # Initialize BAML client
            baml_client = BamlMutationClient()
            
            # Perform analysis (this would require restructuring the data)
            # For now, provide a basic analysis
            report_data = results_data.get("report", {})
            
            analysis_text = f"""# Mutation Testing Analysis for {args.file_path}

## Overall Results
- **Mutation Score**: {report_data.get('mutation_score', 0):.1f}%
- **Total Mutants**: {report_data.get('total_mutants', 0)}
- **Killed**: {report_data.get('killed_mutants', 0)}
- **Survived**: {report_data.get('survived_mutants', 0)}
- **Timeout**: {report_data.get('timeout_mutants', 0)}
- **Error**: {report_data.get('error_mutants', 0)}

## Assessment
"""
            
            mutation_score = report_data.get('mutation_score', 0)
            if mutation_score >= 80:
                analysis_text += "✅ **Excellent**: Your test suite has high quality with strong mutation detection.\n"
            elif mutation_score >= 60:
                analysis_text += "⚠️ **Good**: Your test suite is decent but has room for improvement.\n"
            elif mutation_score >= 40:
                analysis_text += "🔶 **Fair**: Your test suite needs significant improvement to catch more bugs.\n"
            else:
                analysis_text += "❌ **Poor**: Your test suite has major gaps and may miss critical bugs.\n"
            
            # Add surviving mutant analysis
            survived_count = report_data.get('survived_mutants', 0)
            if survived_count > 0:
                analysis_text += f"\n## ⚠️ {survived_count} Surviving Mutants Found\n"
                analysis_text += "These mutants represent potential weaknesses in your test suite:\n\n"
                
                # Show details of surviving mutants
                mutants_data = results_data.get("mutants", [])
                results_list = report_data.get("results", [])
                
                survived_mutants = []
                for result in results_list:
                    if result.get("status") == "survived":
                        mutant_id = result.get("mutant_id")
                        mutant_info = next((m for m in mutants_data if m["id"] == mutant_id), None)
                        if mutant_info:
                            survived_mutants.append(mutant_info)
                
                for mutant in survived_mutants[:5]:  # Show first 5
                    analysis_text += f"- **{mutant['function_name']}** (line {mutant['line_number']}): {mutant['description']}\n"
                    analysis_text += f"  - Original: `{mutant['original_code']}`\n"
                    analysis_text += f"  - Mutated: `{mutant['mutated_code']}`\n\n"
                
                if len(survived_mutants) > 5:
                    analysis_text += f"... and {len(survived_mutants) - 5} more\n\n"
            
            return [{"text": analysis_text}]
        
        except json.JSONDecodeError as e:
            return [{
                "text": f"Error: Invalid JSON format in results_json: {str(e)}"
            }]
        except Exception as e:
            return [{
                "text": f"Error analyzing mutation results: {str(e)}"
            }]
    
    async def _generate_mutation_strategy(self, args: GenerateMutationStrategyArgs) -> List[Dict[str, Any]]:
        """Generate AI-powered mutation testing strategy."""
        try:
            if not os.path.exists(args.file_path):
                return [{
                    "text": f"Error: File '{args.file_path}' not found."
                }]
            
            # Read the source code
            with open(args.file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Try to find associated test files
            test_code = self._find_test_files(args.file_path)
            
            # Initialize BAML client and generate strategy
            baml_client = BamlMutationClient()
            
            strategy = baml_client.generate_mutation_strategy(
                file_path=args.file_path,
                function_code=source_code,
                existing_tests=test_code,
                target_functions=args.target_functions or []
            )
            
            if strategy:
                result_text = f"""# Mutation Testing Strategy for {args.file_path}

## Target Functions
{', '.join(strategy.get('target_functions', []))}

## Recommended Mutation Operators
"""
                for operator in strategy.get('recommended_operators', []):
                    result_text += f"- **{operator.get('name', 'Unknown')}**: {operator.get('description', 'No description')}\n"
                
                result_text += f"\n## Priority Areas\n"
                for area in strategy.get('priority_areas', []):
                    result_text += f"- {area}\n"
                
                result_text += f"\n## Expected Results\n"
                result_text += f"- Estimated mutants: {strategy.get('expected_mutant_count', 'Unknown')}\n"
                result_text += f"- Rationale: {strategy.get('rationale', 'No rationale provided')}\n"
                
                return [{"text": result_text}]
            else:
                return [{
                    "text": "Could not generate mutation strategy. This might be due to:\n"
                           "- API connectivity issues\n"
                           "- Invalid source code\n"
                           "- Missing test files"
                }]
        
        except Exception as e:
            return [{
                "text": f"Error generating mutation strategy for '{args.file_path}': {str(e)}"
            }]
    
    async def _suggest_test_improvements(self, args: SuggestTestImprovementsArgs) -> List[Dict[str, Any]]:
        """Suggest test improvements based on mutation results."""
        try:
            # Parse results JSON
            results_data = json.loads(args.results_json)
            
            # Extract surviving mutants
            mutants_data = results_data.get("mutants", [])
            results_list = results_data.get("report", {}).get("results", [])
            
            surviving_mutants = []
            for result in results_list:
                if result.get("status") == "survived":
                    mutant_id = result.get("mutant_id")
                    mutant_info = next((m for m in mutants_data if m["id"] == mutant_id), None)
                    if mutant_info:
                        surviving_mutants.append(mutant_info)
            
            if not surviving_mutants:
                return [{
                    "text": "🎉 Excellent! No surviving mutants found. Your test suite appears to be comprehensive."
                }]
            
            # Generate improvement suggestions
            suggestions_text = f"""# Test Improvement Suggestions for {args.file_path}

Found {len(surviving_mutants)} surviving mutants that indicate test gaps:

## Specific Improvements Needed

"""
            
            # Group by function for better organization
            function_groups = {}
            for mutant in surviving_mutants:
                func_name = mutant.get('function_name', 'unknown')
                if func_name not in function_groups:
                    function_groups[func_name] = []
                function_groups[func_name].append(mutant)
            
            for func_name, mutants in function_groups.items():
                suggestions_text += f"### Function: `{func_name}`\n\n"
                
                for mutant in mutants:
                    suggestions_text += f"**Issue**: {mutant.get('description', 'Unknown mutation')}\n"
                    suggestions_text += f"- Line {mutant.get('line_number', '?')}: `{mutant.get('original_code', '')}` → `{mutant.get('mutated_code', '')}`\n"
                    suggestions_text += f"- **Operator**: {mutant.get('operator_name', 'Unknown')}\n"
                    
                    # Provide specific improvement suggestions based on operator type
                    operator_name = mutant.get('operator_name', '')
                    if 'Comparison' in operator_name:
                        suggestions_text += "- **Suggestion**: Add test cases that verify boundary conditions and edge cases for comparisons\n"
                    elif 'Arithmetic' in operator_name:
                        suggestions_text += "- **Suggestion**: Add test cases with different arithmetic operations and verify exact results\n"
                    elif 'Boolean' in operator_name:
                        suggestions_text += "- **Suggestion**: Add test cases that explicitly test both True and False conditions\n"
                    elif 'Number' in operator_name:
                        suggestions_text += "- **Suggestion**: Add test cases with boundary values (0, 1, -1) and verify exact results\n"
                    else:
                        suggestions_text += "- **Suggestion**: Add test cases that would detect this specific code change\n"
                    
                    suggestions_text += "\n"
            
            # Add general recommendations
            suggestions_text += """## General Recommendations

1. **Add Edge Case Tests**: Focus on boundary values, empty inputs, and extreme cases
2. **Improve Assertions**: Use more specific assertions that would catch subtle changes
3. **Test Error Conditions**: Ensure error paths are properly tested
4. **Verify Exact Outputs**: Don't just test that functions don't crash - verify exact behavior
5. **Add Negative Tests**: Test what should NOT happen

## Next Steps
1. Implement the suggested test cases
2. Run mutation testing again to verify improvements
3. Aim for a mutation score above 80% for high-quality test coverage
"""
            
            return [{"text": suggestions_text}]
        
        except json.JSONDecodeError as e:
            return [{
                "text": f"Error: Invalid JSON format in results_json: {str(e)}"
            }]
        except Exception as e:
            return [{
                "text": f"Error generating test improvement suggestions: {str(e)}"
            }]
    
    def _format_mutation_report(self, report, mutants) -> str:
        """Format mutation test report for display."""
        result = f"# Mutation Testing Report: {os.path.basename(report.file_path)}\n\n"
        
        # Overall summary
        result += f"## Summary\n"
        result += f"- **Total Mutants**: {report.total_mutants}\n"
        result += f"- **Killed**: {report.killed_mutants} ✅\n"
        result += f"- **Survived**: {report.survived_mutants} ⚠️\n"
        result += f"- **Timeout**: {report.timeout_mutants} ⏱️\n"
        result += f"- **Error**: {report.error_mutants} ❌\n"
        result += f"- **Mutation Score**: {report.mutation_score:.1f}%\n"
        result += f"- **Execution Time**: {report.execution_time_ms/1000:.1f}s\n\n"
        
        # Score interpretation
        if report.mutation_score >= 80:
            result += "🎉 **Excellent**: High-quality test suite!\n"
        elif report.mutation_score >= 60:
            result += "👍 **Good**: Solid test coverage with room for improvement.\n"
        elif report.mutation_score >= 40:
            result += "⚠️ **Fair**: Test suite needs improvement.\n"
        else:
            result += "❌ **Poor**: Significant test gaps detected.\n"
        
        result += "\n"
        
        # Function-level breakdown
        function_stats = {}
        mutant_dict = {m.id: m for m in mutants}
        
        for test_result in report.results:
            mutant = mutant_dict.get(test_result.mutant_id)
            if mutant:
                func_name = mutant.function_name
                if func_name not in function_stats:
                    function_stats[func_name] = {'total': 0, 'killed': 0, 'survived': 0}
                
                function_stats[func_name]['total'] += 1
                if test_result.status.value == 'killed':
                    function_stats[func_name]['killed'] += 1
                elif test_result.status.value == 'survived':
                    function_stats[func_name]['survived'] += 1
        
        if function_stats:
            result += "## Function-Level Results\n\n"
            for func_name, stats in function_stats.items():
                valid_total = stats['killed'] + stats['survived']
                if valid_total > 0:
                    func_score = (stats['killed'] / valid_total) * 100
                    status_icon = "✅" if func_score >= 80 else "⚠️" if func_score >= 60 else "❌"
                    result += f"- **{func_name}** {status_icon}: {stats['killed']}/{valid_total} ({func_score:.1f}%)\n"
        
        # Show some surviving mutants as examples
        survived_examples = []
        for test_result in report.results[:10]:  # Show first 10
            if test_result.status.value == 'survived':
                mutant = mutant_dict.get(test_result.mutant_id)
                if mutant:
                    survived_examples.append(mutant)
        
        if survived_examples:
            result += f"\n## 🔍 Surviving Mutants (Examples)\n\n"
            for mutant in survived_examples[:5]:  # Show first 5
                result += f"### {mutant.function_name} (Line {mutant.line_number})\n"
                result += f"- **Operator**: {mutant.operator_name}\n"
                result += f"- **Change**: `{mutant.original_code}` → `{mutant.mutated_code}`\n"
                result += f"- **Impact**: {mutant.description}\n\n"
        
        if report.survived_mutants > 0:
            result += "\n💡 **Tip**: Surviving mutants indicate areas where your tests could be stronger. "
            result += "Use the `analyze_mutation_results` tool for detailed improvement suggestions.\n"
        
        return result
    
    def _find_test_files(self, source_file_path: str) -> str:
        """Find and read associated test files."""
        source_dir = os.path.dirname(source_file_path)
        source_name = os.path.splitext(os.path.basename(source_file_path))[0]
        
        # Common test file patterns
        test_patterns = [
            f"test_{source_name}.py",
            f"{source_name}_test.py",
        ]
        
        # Search in common test directories
        search_dirs = [
            source_dir,
            os.path.join(source_dir, "tests"),
            os.path.join(source_dir, "test"),
        ]
        
        test_content = ""
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            for pattern in test_patterns:
                test_file = os.path.join(search_dir, pattern)
                if os.path.exists(test_file):
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            test_content += f"\n# {test_file}\n{f.read()}\n"
                    except Exception:
                        continue
        
        return test_content if test_content else "# No test files found"


def get_tool() -> MutationTestingTool:
    """Get the mutation testing tool instance."""
    return MutationTestingTool()