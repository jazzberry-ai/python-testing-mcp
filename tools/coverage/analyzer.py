"""
Coverage analyzer for parsing coverage reports and identifying uncovered code.
"""

import ast
import json
import os
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass


@dataclass
class CoverageReport:
    """Coverage report for a Python file."""
    file_path: str
    total_lines: int
    covered_lines: int
    missing_lines: List[int]
    excluded_lines: List[int]
    coverage_percentage: float
    uncovered_functions: List[str]
    uncovered_branches: List[str]


@dataclass
class FunctionCoverage:
    """Coverage information for a specific function."""
    name: str
    line_start: int
    line_end: int
    covered_lines: Set[int]
    total_lines: int
    coverage_percentage: float
    is_fully_covered: bool


class CoverageAnalyzer:
    """Analyzes Python code coverage reports and provides insights."""
    
    def __init__(self):
        """Initialize the coverage analyzer."""
        pass
    
    def parse_coverage_json(self, coverage_json_path: str) -> Dict[str, CoverageReport]:
        """Parse coverage.py JSON report format.
        
        Args:
            coverage_json_path: Path to coverage JSON report
            
        Returns:
            Dictionary mapping file paths to coverage reports
        """
        if not os.path.exists(coverage_json_path):
            raise FileNotFoundError(f"Coverage JSON file not found: {coverage_json_path}")
        
        with open(coverage_json_path, 'r', encoding='utf-8') as f:
            coverage_data = json.load(f)
        
        reports = {}
        
        # Parse files from coverage data
        files_data = coverage_data.get('files', {})
        
        for file_path, file_data in files_data.items():
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
            
            executed_lines = set(file_data.get('executed_lines', []))
            missing_lines = file_data.get('missing_lines', [])
            excluded_lines = file_data.get('excluded_lines', [])
            
            # Calculate coverage stats
            total_lines = len(executed_lines) + len(missing_lines)
            covered_lines = len(executed_lines)
            coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            
            # Analyze uncovered functions and branches
            uncovered_functions = self._find_uncovered_functions(file_path, missing_lines)
            uncovered_branches = file_data.get('missing_branches', [])
            
            report = CoverageReport(
                file_path=file_path,
                total_lines=total_lines,
                covered_lines=covered_lines,
                missing_lines=missing_lines,
                excluded_lines=excluded_lines,
                coverage_percentage=coverage_percentage,
                uncovered_functions=uncovered_functions,
                uncovered_branches=uncovered_branches
            )
            
            reports[file_path] = report
        
        return reports
    
    def _find_uncovered_functions(self, file_path: str, missing_lines: List[int]) -> List[str]:
        """Find functions that have uncovered lines.
        
        Args:
            file_path: Path to Python file
            missing_lines: List of line numbers that are not covered
            
        Returns:
            List of function names with uncovered code
        """
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            uncovered_functions = []
            missing_set = set(missing_lines)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if any line in the function is uncovered
                    func_lines = range(node.lineno, node.end_lineno + 1 if node.end_lineno else node.lineno + 1)
                    if any(line in missing_set for line in func_lines):
                        uncovered_functions.append(node.name)
            
            return uncovered_functions
            
        except Exception:
            return []
    
    def analyze_function_coverage(self, file_path: str, coverage_data: Dict) -> List[FunctionCoverage]:
        """Analyze coverage at the function level.
        
        Args:
            file_path: Path to Python file
            coverage_data: Coverage data for the file
            
        Returns:
            List of function coverage information
        """
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            executed_lines = set(coverage_data.get('executed_lines', []))
            function_coverages = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    line_start = node.lineno
                    line_end = node.end_lineno or node.lineno
                    
                    # Find covered lines in this function
                    func_lines = set(range(line_start, line_end + 1))
                    covered_in_func = func_lines & executed_lines
                    
                    total_lines = len(func_lines)
                    coverage_percentage = (len(covered_in_func) / total_lines * 100) if total_lines > 0 else 0
                    is_fully_covered = len(covered_in_func) == total_lines
                    
                    func_coverage = FunctionCoverage(
                        name=node.name,
                        line_start=line_start,
                        line_end=line_end,
                        covered_lines=covered_in_func,
                        total_lines=total_lines,
                        coverage_percentage=coverage_percentage,
                        is_fully_covered=is_fully_covered
                    )
                    
                    function_coverages.append(func_coverage)
            
            return function_coverages
            
        except Exception:
            return []
    
    def generate_coverage_summary(self, reports: Dict[str, CoverageReport]) -> Dict[str, any]:
        """Generate overall coverage summary.
        
        Args:
            reports: Dictionary of coverage reports
            
        Returns:
            Summary statistics
        """
        if not reports:
            return {
                'total_files': 0,
                'total_lines': 0,
                'covered_lines': 0,
                'overall_coverage': 0.0,
                'files_with_full_coverage': 0,
                'files_with_no_coverage': 0,
                'worst_covered_files': [],
                'best_covered_files': []
            }
        
        total_lines = sum(report.total_lines for report in reports.values())
        covered_lines = sum(report.covered_lines for report in reports.values())
        overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        
        files_with_full_coverage = sum(1 for report in reports.values() if report.coverage_percentage == 100)
        files_with_no_coverage = sum(1 for report in reports.values() if report.coverage_percentage == 0)
        
        # Sort files by coverage percentage
        sorted_reports = sorted(reports.items(), key=lambda x: x[1].coverage_percentage)
        
        worst_covered = [(path, report.coverage_percentage) for path, report in sorted_reports[:5]]
        best_covered = [(path, report.coverage_percentage) for path, report in sorted_reports[-5:]]
        
        return {
            'total_files': len(reports),
            'total_lines': total_lines,
            'covered_lines': covered_lines,
            'overall_coverage': round(overall_coverage, 2),
            'files_with_full_coverage': files_with_full_coverage,
            'files_with_no_coverage': files_with_no_coverage,
            'worst_covered_files': worst_covered,
            'best_covered_files': best_covered
        }
    
    def identify_critical_gaps(self, reports: Dict[str, CoverageReport]) -> List[Dict[str, any]]:
        """Identify critical coverage gaps that should be prioritized.
        
        Args:
            reports: Dictionary of coverage reports
            
        Returns:
            List of critical gaps with recommendations
        """
        gaps = []
        
        for file_path, report in reports.items():
            if report.coverage_percentage < 50:
                gaps.append({
                    'type': 'low_coverage_file',
                    'file': file_path,
                    'coverage': report.coverage_percentage,
                    'recommendation': f'File has very low coverage ({report.coverage_percentage:.1f}%). Consider adding comprehensive tests.',
                    'priority': 'high'
                })
            
            if report.uncovered_functions:
                gaps.append({
                    'type': 'uncovered_functions',
                    'file': file_path,
                    'functions': report.uncovered_functions,
                    'recommendation': f'Functions have no test coverage: {", ".join(report.uncovered_functions)}',
                    'priority': 'medium'
                })
            
            if len(report.missing_lines) > 20:
                gaps.append({
                    'type': 'many_uncovered_lines',
                    'file': file_path,
                    'uncovered_lines': len(report.missing_lines),
                    'recommendation': f'File has {len(report.missing_lines)} uncovered lines. Focus on testing core logic.',
                    'priority': 'medium'
                })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        gaps.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return gaps