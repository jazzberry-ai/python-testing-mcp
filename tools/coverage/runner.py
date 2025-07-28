"""
Coverage runner for executing tests with coverage measurement.
"""

import os
import subprocess
import tempfile
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from .analyzer import CoverageAnalyzer, CoverageReport


@dataclass
class CoverageRunResult:
    """Result of a coverage run."""
    success: bool
    coverage_percentage: float
    reports: Dict[str, CoverageReport]
    summary: Dict[str, any]
    critical_gaps: List[Dict[str, any]]
    output: str
    error: Optional[str] = None


class CoverageRunner:
    """Runs tests with coverage measurement and analysis."""
    
    def __init__(self):
        """Initialize the coverage runner."""
        self.analyzer = CoverageAnalyzer()
    
    def run_coverage(
        self,
        source_path: str,
        test_path: Optional[str] = None,
        test_command: Optional[str] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> CoverageRunResult:
        """Run coverage analysis on Python code.
        
        Args:
            source_path: Path to source code directory or file
            test_path: Path to test directory or file (optional)
            test_command: Custom test command to run (optional)
            include_patterns: Patterns to include in coverage (optional)
            exclude_patterns: Patterns to exclude from coverage (optional)
            
        Returns:
            Coverage run result with analysis
        """
        # Validate paths
        if not os.path.exists(source_path):
            return CoverageRunResult(
                success=False,
                coverage_percentage=0.0,
                reports={},
                summary={},
                critical_gaps=[],
                output="",
                error=f"Source path not found: {source_path}"
            )
        
        # Create temporary directory for coverage data
        with tempfile.TemporaryDirectory() as temp_dir:
            coverage_file = os.path.join(temp_dir, '.coverage')
            json_report_file = os.path.join(temp_dir, 'coverage.json')
            
            try:
                # Run coverage
                run_result = self._execute_coverage(
                    source_path=source_path,
                    test_path=test_path,
                    test_command=test_command,
                    coverage_file=coverage_file,
                    json_report_file=json_report_file,
                    include_patterns=include_patterns,
                    exclude_patterns=exclude_patterns
                )
                
                if not run_result[0]:  # success
                    return CoverageRunResult(
                        success=False,
                        coverage_percentage=0.0,
                        reports={},
                        summary={},
                        critical_gaps=[],
                        output=run_result[2],  # output
                        error=run_result[1]    # error
                    )
                
                # Parse coverage results
                if os.path.exists(json_report_file):
                    reports = self.analyzer.parse_coverage_json(json_report_file)
                    summary = self.analyzer.generate_coverage_summary(reports)
                    critical_gaps = self.analyzer.identify_critical_gaps(reports)
                    
                    return CoverageRunResult(
                        success=True,
                        coverage_percentage=summary.get('overall_coverage', 0.0),
                        reports=reports,
                        summary=summary,
                        critical_gaps=critical_gaps,
                        output=run_result[2],
                        error=None
                    )
                else:
                    return CoverageRunResult(
                        success=False,
                        coverage_percentage=0.0,
                        reports={},
                        summary={},
                        critical_gaps=[],
                        output=run_result[2],
                        error="Coverage JSON report not generated"
                    )
                    
            except Exception as e:
                return CoverageRunResult(
                    success=False,
                    coverage_percentage=0.0,
                    reports={},
                    summary={},
                    critical_gaps=[],
                    output="",
                    error=f"Coverage execution failed: {str(e)}"
                )
    
    def _execute_coverage(
        self,
        source_path: str,
        test_path: Optional[str],
        test_command: Optional[str],
        coverage_file: str,
        json_report_file: str,
        include_patterns: Optional[List[str]],
        exclude_patterns: Optional[List[str]]
    ) -> Tuple[bool, Optional[str], str]:
        """Execute coverage measurement.
        
        Returns:
            (success, error_message, output)
        """
        # Set environment variable for coverage data file
        env = os.environ.copy()
        env['COVERAGE_FILE'] = coverage_file
        
        # Build coverage command
        coverage_cmd = ['python', '-m', 'coverage', 'run']
        
        # Add source specification
        if os.path.isfile(source_path):
            coverage_cmd.extend(['--source', os.path.dirname(source_path)])
        else:
            coverage_cmd.extend(['--source', source_path])
        
        # Add include patterns
        if include_patterns:
            for pattern in include_patterns:
                coverage_cmd.extend(['--include', pattern])
        
        # Add exclude patterns
        if exclude_patterns:
            for pattern in exclude_patterns:
                coverage_cmd.extend(['--omit', pattern])
        
        # Determine what to run
        if test_command:
            # Use custom test command
            coverage_cmd.extend(['-m'] + test_command.split())
        elif test_path and os.path.exists(test_path):
            # Run specific test file/directory
            if os.path.isfile(test_path):
                coverage_cmd.append(test_path)
            else:
                # Run pytest on directory
                coverage_cmd.extend(['-m', 'pytest', test_path])
        else:
            # Try to auto-discover tests
            possible_test_paths = [
                'test_*.py',
                'tests/',
                '*_test.py',
                'test/'
            ]
            
            test_found = False
            for test_pattern in possible_test_paths:
                if '*' in test_pattern:
                    # Use glob pattern with pytest
                    coverage_cmd.extend(['-m', 'pytest', '-v'])
                    test_found = True
                    break
                elif os.path.exists(test_pattern):
                    if os.path.isfile(test_pattern):
                        coverage_cmd.append(test_pattern)
                    else:
                        coverage_cmd.extend(['-m', 'pytest', test_pattern])
                    test_found = True
                    break
            
            if not test_found:
                # Just run the source file itself to measure import coverage
                if os.path.isfile(source_path):
                    coverage_cmd.append(source_path)
                else:
                    return False, "No tests found and source_path is not a file", ""
        
        output_lines = []
        
        try:
            # Run coverage
            result = subprocess.run(
                coverage_cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minute timeout
            )
            
            output_lines.append(f"Coverage command: {' '.join(coverage_cmd)}")
            output_lines.append(f"Return code: {result.returncode}")
            output_lines.append(f"STDOUT: {result.stdout}")
            if result.stderr:
                output_lines.append(f"STDERR: {result.stderr}")
            
            # Generate JSON report
            json_cmd = [
                'python', '-m', 'coverage', 'json',
                '--output-file', json_report_file
            ]
            
            json_result = subprocess.run(
                json_cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )
            
            output_lines.append(f"JSON report command: {' '.join(json_cmd)}")
            output_lines.append(f"JSON return code: {json_result.returncode}")
            
            if json_result.returncode != 0:
                output_lines.append(f"JSON STDERR: {json_result.stderr}")
                return False, f"Failed to generate JSON report: {json_result.stderr}", "\\n".join(output_lines)
            
            # Coverage run might have non-zero exit code due to test failures, but still generate valid coverage
            if os.path.exists(json_report_file):
                return True, None, "\\n".join(output_lines)
            else:
                return False, "Coverage data not generated", "\\n".join(output_lines)
                
        except subprocess.TimeoutExpired:
            return False, "Coverage execution timed out", "\\n".join(output_lines)
        except Exception as e:
            return False, f"Coverage execution error: {str(e)}", "\\n".join(output_lines)
    
    def run_coverage_on_single_file(self, file_path: str) -> CoverageRunResult:
        """Run coverage on a single Python file without tests.
        
        This is useful for measuring import coverage or basic execution coverage.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Coverage run result
        """
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return CoverageRunResult(
                success=False,
                coverage_percentage=0.0,
                reports={},
                summary={},
                critical_gaps=[],
                output="",
                error=f"Invalid Python file: {file_path}"
            )
        
        return self.run_coverage(
            source_path=file_path,
            test_path=None,
            test_command=None
        )
    
    def suggest_test_improvements(self, reports: Dict[str, CoverageReport]) -> List[Dict[str, any]]:
        """Suggest improvements based on coverage analysis.
        
        Args:
            reports: Coverage reports
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        for file_path, report in reports.items():
            if report.coverage_percentage < 80:
                suggestions.append({
                    'type': 'increase_coverage',
                    'file': file_path,
                    'current_coverage': report.coverage_percentage,
                    'suggestion': f'Consider adding tests to increase coverage from {report.coverage_percentage:.1f}% to at least 80%',
                    'priority': 'high' if report.coverage_percentage < 50 else 'medium'
                })
            
            if report.uncovered_functions:
                suggestions.append({
                    'type': 'test_functions',
                    'file': file_path,
                    'functions': report.uncovered_functions,
                    'suggestion': f'Add tests for uncovered functions: {", ".join(report.uncovered_functions)}',
                    'priority': 'high'
                })
            
            if len(report.missing_lines) > 10 and report.coverage_percentage > 70:
                suggestions.append({
                    'type': 'edge_cases',
                    'file': file_path,
                    'missing_lines_count': len(report.missing_lines),
                    'suggestion': f'Focus on testing edge cases - {len(report.missing_lines)} lines need coverage',
                    'priority': 'medium'
                })
        
        return suggestions