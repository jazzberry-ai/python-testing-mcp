"""
Python Coverage Tool - MCP Integration

Implements the coverage tool for the MCP server using the tool registry system.
"""

import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from ..registry import BaseTool
from .runner import CoverageRunner, CoverageRunResult


class RunCoverageArgs(BaseModel):
    """Arguments for the run_coverage tool."""
    source_path: str
    test_path: Optional[str] = None
    test_command: Optional[str] = None
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None


class AnalyzeCoverageArgs(BaseModel):
    """Arguments for the analyze_coverage tool."""
    coverage_json_path: str


class SuggestTestsArgs(BaseModel):
    """Arguments for the suggest_tests tool."""
    source_path: str
    coverage_threshold: float = 80.0


class PythonCoverageTool(BaseTool):
    """Python coverage tool implementation."""
    
    @property
    def name(self) -> str:
        return "python-coverage"
    
    @property
    def description(self) -> str:
        return "Python code coverage analysis and testing tool"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions for the coverage tool."""
        return [
            {
                "name": "run_python_coverage",
                "description": "Run coverage analysis on Python code with optional test execution",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source_path": {
                            "type": "string",
                            "description": "Path to source code directory or file to analyze"
                        },
                        "test_path": {
                            "type": "string",
                            "description": "Optional: Path to test directory or file"
                        },
                        "test_command": {
                            "type": "string",
                            "description": "Optional: Custom test command to run (e.g., 'pytest -v')"
                        },
                        "include_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: Patterns to include in coverage analysis"
                        },
                        "exclude_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: Patterns to exclude from coverage analysis"
                        }
                    },
                    "required": ["source_path"]
                }
            },
            {
                "name": "analyze_coverage_report",
                "description": "Analyze an existing coverage JSON report and provide insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "coverage_json_path": {
                            "type": "string",
                            "description": "Path to coverage JSON report file"
                        }
                    },
                    "required": ["coverage_json_path"]
                }
            },
            {
                "name": "suggest_coverage_improvements",
                "description": "Analyze code coverage and suggest specific test improvements",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source_path": {
                            "type": "string",
                            "description": "Path to source code directory or file"
                        },
                        "coverage_threshold": {
                            "type": "number",
                            "description": "Target coverage percentage (default: 80.0)",
                            "default": 80.0
                        }
                    },
                    "required": ["source_path"]
                }
            }
        ]
    
    async def handle_mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle MCP tool calls for the coverage tool."""
        try:
            if tool_name == "run_python_coverage":
                args = RunCoverageArgs(**arguments)
                return await self._run_coverage(args)
            
            elif tool_name == "analyze_coverage_report":
                args = AnalyzeCoverageArgs(**arguments)
                return await self._analyze_coverage_report(args)
            
            elif tool_name == "suggest_coverage_improvements":
                args = SuggestTestsArgs(**arguments)
                return await self._suggest_coverage_improvements(args)
            
            else:
                raise NotImplementedError(f"Tool {tool_name} not handled by coverage tool")
        
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error executing {tool_name}: {str(e)}"
            }]
    
    async def _run_coverage(self, args: RunCoverageArgs) -> List[Dict[str, Any]]:
        """Run coverage analysis on Python code."""
        # Validate source path
        if not args.source_path or not args.source_path.strip():
            return [{
                "type": "text",
                "text": "Error: Source path cannot be empty. Please provide a valid source path."
            }]
        
        abs_source_path = os.path.abspath(args.source_path)
        
        if not os.path.exists(abs_source_path):
            return [{
                "type": "text",
                "text": f"Error: Source path '{abs_source_path}' not found. Please check the path and ensure it exists."
            }]
        
        # Validate test path if provided
        if args.test_path:
            abs_test_path = os.path.abspath(args.test_path)
            if not os.path.exists(abs_test_path):
                return [{
                    "type": "text",
                    "text": f"Error: Test path '{abs_test_path}' not found. Please check the path and ensure it exists."
                }]
        
        try:
            runner = CoverageRunner()
            result = runner.run_coverage(
                source_path=abs_source_path,
                test_path=args.test_path,
                test_command=args.test_command,
                include_patterns=args.include_patterns,
                exclude_patterns=args.exclude_patterns
            )
            
            if not result.success:
                return [{
                    "type": "text",
                    "text": f"Coverage analysis failed: {result.error}\\n\\nOutput:\\n{result.output}"
                }]
            
            # Format results
            result_text = self._format_coverage_results(result)
            
            return [{"type": "text", "text": result_text}]
        
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error running coverage analysis: {str(e)}"
            }]
    
    async def _analyze_coverage_report(self, args: AnalyzeCoverageArgs) -> List[Dict[str, Any]]:
        """Analyze an existing coverage JSON report."""
        if not args.coverage_json_path or not args.coverage_json_path.strip():
            return [{
                "type": "text",
                "text": "Error: Coverage JSON path cannot be empty."
            }]
        
        abs_path = os.path.abspath(args.coverage_json_path)
        
        if not os.path.exists(abs_path):
            return [{
                "type": "text",
                "text": f"Error: Coverage JSON file '{abs_path}' not found."
            }]
        
        try:
            runner = CoverageRunner()
            reports = runner.analyzer.parse_coverage_json(abs_path)
            summary = runner.analyzer.generate_coverage_summary(reports)
            critical_gaps = runner.analyzer.identify_critical_gaps(reports)
            
            # Create result object
            result = CoverageRunResult(
                success=True,
                coverage_percentage=summary.get('overall_coverage', 0.0),
                reports=reports,
                summary=summary,
                critical_gaps=critical_gaps,
                output="Analysis completed from existing report"
            )
            
            result_text = self._format_coverage_results(result)
            
            return [{"type": "text", "text": result_text}]
        
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error analyzing coverage report: {str(e)}"
            }]
    
    async def _suggest_coverage_improvements(self, args: SuggestTestsArgs) -> List[Dict[str, Any]]:
        """Suggest coverage improvements for the given source code."""
        if not args.source_path or not args.source_path.strip():
            return [{
                "type": "text",
                "text": "Error: Source path cannot be empty."
            }]
        
        abs_source_path = os.path.abspath(args.source_path)
        
        if not os.path.exists(abs_source_path):
            return [{
                "type": "text",
                "text": f"Error: Source path '{abs_source_path}' not found."
            }]
        
        try:
            # First run coverage analysis
            runner = CoverageRunner()
            result = runner.run_coverage(source_path=abs_source_path)
            
            if not result.success:
                return [{
                    "type": "text",
                    "text": f"Could not analyze coverage for suggestions: {result.error}"
                }]
            
            # Generate suggestions
            suggestions = runner.suggest_test_improvements(result.reports)
            
            # Format suggestions
            result_text = f"# Coverage Improvement Suggestions for {abs_source_path}\\n\\n"
            result_text += f"**Current Overall Coverage**: {result.coverage_percentage:.1f}%\\n"
            result_text += f"**Target Coverage**: {args.coverage_threshold}%\\n\\n"
            
            if result.coverage_percentage >= args.coverage_threshold:
                result_text += "🎉 **Congratulations!** Your code already meets the target coverage threshold.\\n\\n"
                result_text += "## Additional Improvements\\n\\n"
            else:
                gap = args.coverage_threshold - result.coverage_percentage
                result_text += f"📈 **Coverage Gap**: {gap:.1f}% improvement needed\\n\\n"
                result_text += "## Priority Improvements\\n\\n"
            
            if suggestions:
                high_priority = [s for s in suggestions if s.get('priority') == 'high']
                medium_priority = [s for s in suggestions if s.get('priority') == 'medium']
                low_priority = [s for s in suggestions if s.get('priority') == 'low']
                
                for priority_group, title in [(high_priority, '🔴 High Priority'), 
                                             (medium_priority, '🟡 Medium Priority'), 
                                             (low_priority, '🟢 Low Priority')]:
                    if priority_group:
                        result_text += f"### {title}\\n\\n"
                        for suggestion in priority_group:
                            result_text += f"- **{suggestion['type'].replace('_', ' ').title()}**\\n"
                            result_text += f"  - File: `{suggestion.get('file', 'N/A')}`\\n"
                            result_text += f"  - {suggestion['suggestion']}\\n\\n"
            else:
                result_text += "No specific suggestions available. Consider adding more comprehensive tests.\\n"
            
            # Add critical gaps
            if result.critical_gaps:
                result_text += "## Critical Coverage Gaps\\n\\n"
                for gap in result.critical_gaps[:5]:  # Show top 5 gaps
                    result_text += f"- **{gap['type'].replace('_', ' ').title()}**: {gap['recommendation']}\\n"
            
            return [{"type": "text", "text": result_text}]
        
        except Exception as e:
            return [{
                "type": "text",
                "text": f"Error generating coverage suggestions: {str(e)}"
            }]
    
    def _format_coverage_results(self, result: CoverageRunResult) -> str:
        """Format coverage results for display."""
        text = "# Python Coverage Analysis Results\\n\\n"
        
        # Overall summary
        text += f"## Overall Coverage: {result.coverage_percentage:.1f}%\\n\\n"
        
        summary = result.summary
        if summary:
            text += f"### Summary Statistics\\n"
            text += f"- **Total Files**: {summary.get('total_files', 0)}\\n"
            text += f"- **Total Lines**: {summary.get('total_lines', 0)}\\n"
            text += f"- **Covered Lines**: {summary.get('covered_lines', 0)}\\n"
            text += f"- **Files with 100% Coverage**: {summary.get('files_with_full_coverage', 0)}\\n"
            text += f"- **Files with 0% Coverage**: {summary.get('files_with_no_coverage', 0)}\\n\\n"
        
        # Per-file breakdown
        if result.reports:
            text += f"### Per-File Coverage\\n\\n"
            
            # Sort files by coverage percentage
            sorted_files = sorted(result.reports.items(), key=lambda x: x[1].coverage_percentage)
            
            for file_path, report in sorted_files:
                coverage_icon = "✅" if report.coverage_percentage == 100 else "⚠️" if report.coverage_percentage >= 80 else "❌"
                text += f"{coverage_icon} **{os.path.basename(file_path)}** - {report.coverage_percentage:.1f}%\\n"
                text += f"   - Lines: {report.covered_lines}/{report.total_lines}\\n"
                
                if report.missing_lines:
                    missing_count = len(report.missing_lines)
                    if missing_count <= 10:
                        text += f"   - Missing lines: {', '.join(map(str, report.missing_lines))}\\n"
                    else:
                        text += f"   - Missing lines: {missing_count} lines uncovered\\n"
                
                if report.uncovered_functions:
                    text += f"   - Uncovered functions: {', '.join(report.uncovered_functions)}\\n"
                
                text += "\\n"
        
        # Critical gaps
        if result.critical_gaps:
            text += f"### 🚨 Critical Coverage Gaps\\n\\n"
            for gap in result.critical_gaps[:5]:  # Show top 5 gaps
                priority_icon = "🔴" if gap['priority'] == 'high' else "🟡" if gap['priority'] == 'medium' else "🟢"
                text += f"{priority_icon} **{gap['type'].replace('_', ' ').title()}**\\n"
                text += f"   - {gap['recommendation']}\\n\\n"
        
        # Execution output (if useful)
        if result.output and "Error" not in result.output:
            text += f"### Execution Details\\n\\n"
            text += f"```\\n{result.output[:1000]}\\n```\\n"
            if len(result.output) > 1000:
                text += "\\n*(Output truncated)*\\n"
        
        return text


def get_tool() -> PythonCoverageTool:
    """Get the coverage tool instance."""
    return PythonCoverageTool()