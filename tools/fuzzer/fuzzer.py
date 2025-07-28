"""
Core fuzzing logic for testing Python functions.
"""

import sys
import traceback
import importlib.util
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import time

from .analyzer import CodeAnalyzer, FunctionInfo
from .gemini_client import GeminiClient


@dataclass
class FuzzResult:
    """Result of a single fuzz test."""
    test_input: Dict[str, Any]
    success: bool
    error: Optional[str]
    execution_time: float
    output: Any


@dataclass
class FuzzReport:
    """Complete fuzzing report for a function."""
    function_name: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    results: List[FuzzResult]
    crashes: List[FuzzResult]
    analysis: Optional[str] = None


class PythonFuzzer:
    """Main fuzzing engine for Python functions."""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize the fuzzer.
        
        Args:
            gemini_api_key: Gemini API key for generating test inputs
        """
        self.gemini_client = GeminiClient(gemini_api_key)
        self.analyzer = None
        self.target_module = None
    
    def load_target_file(self, file_path: str) -> None:
        """Load the target Python file for fuzzing.
        
        Args:
            file_path: Path to the Python file to fuzz
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.analyzer = CodeAnalyzer(file_path)
        
        # Dynamically import the module
        spec = importlib.util.spec_from_file_location("target_module", file_path)
        self.target_module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(self.target_module)
        except Exception as e:
            raise ImportError(f"Failed to load module '{file_path}': {e}. Please ensure the file contains valid Python syntax.")
    
    def fuzz_function(self, function_info: FunctionInfo, num_tests: int = 10) -> FuzzReport:
        """Fuzz a specific function.
        
        Args:
            function_info: Information about the function to fuzz
            num_tests: Number of test cases to generate
            
        Returns:
            Complete fuzzing report
        """
        print(f"Fuzzing function: {function_info.name}")
        
        # Generate test inputs using Gemini
        test_inputs = self.gemini_client.generate_fuzzing_inputs(
            function_info.signature,
            function_info.code,
            num_tests
        )
        
        if not test_inputs:
            print(f"Warning: Failed to generate test inputs for {function_info.name} - skipping function")
            return FuzzReport(
                function_name=function_info.name,
                total_tests=0,
                successful_tests=0,
                failed_tests=0,
                results=[],
                crashes=[]
            )
        
        results = []
        crashes = []
        
        # Get the actual function object
        target_func = getattr(self.target_module, function_info.name, None)
        if not target_func:
            print(f"Warning: Function '{function_info.name}' not found in loaded module - skipping function")
            return FuzzReport(
                function_name=function_info.name,
                total_tests=0,
                successful_tests=0,
                failed_tests=0,
                results=[],
                crashes=[]
            )
        
        print(f"Running {len(test_inputs)} test cases...")
        
        for i, test_input in enumerate(test_inputs):
            print(f"  Test {i+1}/{len(test_inputs)}: {test_input.get('description', 'No description')}")
            result = self._execute_test(target_func, test_input)
            results.append(result)
            
            if not result.success:
                crashes.append(result)
        
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = len(results) - successful_tests
        
        report = FuzzReport(
            function_name=function_info.name,
            total_tests=len(results),
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            results=results,
            crashes=crashes
        )
        
        # Analyze crashes if any occurred
        if crashes:
            print(f"Analyzing {len(crashes)} crashes...")
            crash_analysis = self._analyze_crashes(function_info, crashes)
            report.analysis = crash_analysis
        
        return report
    
    def _execute_test(self, func, test_input: Dict[str, Any]) -> FuzzResult:
        """Execute a single test case.
        
        Args:
            func: The function to test
            test_input: Test input containing args, kwargs, etc.
            
        Returns:
            Test result
        """
        args = test_input.get('args', [])
        kwargs = test_input.get('kwargs', {})
        
        start_time = time.time()
        
        try:
            # Handle special values in args and kwargs (convert from JSON-safe strings)
            def process_value(value):
                if value == "null" or value is None:
                    return None
                elif value == "infinity":
                    return float('inf')
                elif value == "-infinity":
                    return float('-inf')
                elif value == "nan":
                    return float('nan')
                else:
                    return value
            
            processed_args = [process_value(arg) for arg in args]
            processed_kwargs = {k: process_value(v) for k, v in kwargs.items()}
            
            output = func(*processed_args, **processed_kwargs)
            execution_time = time.time() - start_time
            
            return FuzzResult(
                test_input=test_input,
                success=True,
                error=None,
                execution_time=execution_time,
                output=output
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_info = f"{type(e).__name__}: {str(e)}\nTraceback:\n{traceback.format_exc()}"
            
            return FuzzResult(
                test_input=test_input,
                success=False,
                error=error_info,
                execution_time=execution_time,
                output=None
            )
    
    def _analyze_crashes(self, function_info: FunctionInfo, crashes: List[FuzzResult]) -> str:
        """Analyze crashes and provide insights.
        
        Args:
            function_info: Information about the crashed function
            crashes: List of crash results
            
        Returns:
            Analysis report
        """
        analysis_parts = []
        
        for crash in crashes[:3]:  # Analyze first 3 crashes to avoid token limits
            crash_analysis = self.gemini_client.analyze_crash(
                function_info.code,
                crash.error,
                crash.test_input
            )
            analysis_parts.append(f"Crash Analysis:\n{crash_analysis}\n" + "="*50)
        
        return "\n\n".join(analysis_parts)
    
    def fuzz_all_functions(self, file_path: str, num_tests: int = 10) -> List[FuzzReport]:
        """Fuzz all functions in a Python file.
        
        Args:
            file_path: Path to Python file
            num_tests: Number of tests per function
            
        Returns:
            List of fuzzing reports
        """
        self.load_target_file(file_path)
        functions = self.analyzer.extract_functions()
        
        print(f"Found {len(functions)} functions to fuzz:")
        for func in functions:
            print(f"  - {func.name} (line {func.line_number})")
        
        reports = []
        for func_info in functions:
            if not func_info.name.startswith('_'):  # Skip private functions
                report = self.fuzz_function(func_info, num_tests)
                reports.append(report)
                print()  # Add spacing between function reports
        
        return reports
    
    def save_report(self, reports: List[FuzzReport], output_file: str) -> None:
        """Save fuzzing reports to a JSON file.
        
        Args:
            reports: List of fuzzing reports
            output_file: Output file path
        """
        report_data = []
        
        for report in reports:
            report_dict = {
                'function_name': report.function_name,
                'total_tests': report.total_tests,
                'successful_tests': report.successful_tests,
                'failed_tests': report.failed_tests,
                'crash_count': len(report.crashes),
                'results': [],
                'analysis': report.analysis
            }
            
            for result in report.results:
                result_dict = {
                    'test_input': result.test_input,
                    'success': result.success,
                    'error': result.error,
                    'execution_time': result.execution_time,
                    'output': str(result.output) if result.output is not None else None
                }
                report_dict['results'].append(result_dict)
            
            report_data.append(report_dict)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"Report saved to: {output_file}")
