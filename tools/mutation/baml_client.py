"""
BAML Client for Mutation Testing

Provides AI-powered analysis of mutation testing results using BAML structured responses.
"""

import os
from typing import List, Dict, Any, Optional
from baml_client.sync_client import b
from baml_client.types import MutationStrategy, MutationReport

from .mutator import Mutant
from .runner import MutationTestReport, MutationResult, MutationStatus


class BamlMutationClient:
    """Client for AI-powered mutation testing analysis using BAML."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the BAML mutation client.
        
        Args:
            api_key: Optional API key (uses environment variable if not provided)
        """
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
        
        # Verify API key is available
        if not os.getenv('GEMINI_API_KEY'):
            print("Warning: GEMINI_API_KEY not set. AI-powered analysis will not be available.")
    
    def generate_mutation_strategy(
        self, 
        file_path: str,
        function_code: str,
        existing_tests: str,
        target_functions: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an intelligent mutation testing strategy using AI.
        
        Args:
            file_path: Path to the file being analyzed
            function_code: Source code of functions to be mutated
            existing_tests: Existing test code
            target_functions: List of function names to target
            
        Returns:
            Dictionary containing mutation strategy or None if generation fails
        """
        try:
            strategy = b.GenerateMutationStrategy(
                file_path=file_path,
                function_code=function_code,
                existing_tests=existing_tests,
                target_functions=target_functions
            )
            
            return strategy.model_dump()
        
        except Exception as e:
            print(f"Failed to generate mutation strategy: {e}")
            return None
    
    def analyze_mutation_results(
        self,
        file_path: str,
        report: MutationTestReport,
        mutants: List[Mutant]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze mutation testing results and provide insights.
        
        Args:
            file_path: Path to the file that was tested
            report: Mutation test report
            mutants: List of mutants that were tested
            
        Returns:
            Dictionary containing analysis results or None if analysis fails
        """
        try:
            # Prepare data for analysis
            mutation_results_summary = self._format_results_summary(report)
            survived_mutants = self._format_survived_mutants(report, mutants)
            killed_mutants = self._format_killed_mutants(report, mutants)
            
            analysis = b.AnalyzeMutationResults(
                file_path=file_path,
                mutation_results=mutation_results_summary,
                survived_mutants=survived_mutants,
                killed_mutants=killed_mutants,
                mutation_score=report.mutation_score
            )
            
            return analysis.model_dump()
        
        except Exception as e:
            print(f"Failed to analyze mutation results: {e}")
            return None
    
    def generate_test_improvements(
        self,
        function_code: str,
        surviving_mutants: List[Mutant],
        current_tests: str
    ) -> List[str]:
        """
        Generate specific test improvements to kill surviving mutants.
        
        Args:
            function_code: Source code of the function being tested
            surviving_mutants: List of mutants that survived testing
            current_tests: Current test code
            
        Returns:
            List of test improvement suggestions
        """
        try:
            # Format surviving mutants for analysis
            surviving_mutant_descriptions = []
            for mutant in surviving_mutants:
                description = (
                    f"Mutant {mutant.id}: {mutant.description}\n"
                    f"Original: {mutant.original_code}\n"
                    f"Mutated: {mutant.mutated_code}\n"
                    f"Line: {mutant.line_number}\n"
                )
                surviving_mutant_descriptions.append(description)
            
            improvements = b.GenerateTestImprovements(
                function_code=function_code,
                surviving_mutants=surviving_mutant_descriptions,
                current_tests=current_tests
            )
            
            return improvements
        
        except Exception as e:
            print(f"Failed to generate test improvements: {e}")
            return []
    
    def _format_results_summary(self, report: MutationTestReport) -> str:
        """Format mutation test results into a readable summary."""
        summary = f"""
Mutation Testing Results Summary:
- Total Mutants: {report.total_mutants}
- Killed Mutants: {report.killed_mutants}
- Survived Mutants: {report.survived_mutants}
- Timeout Mutants: {report.timeout_mutants}
- Error Mutants: {report.error_mutants}
- Mutation Score: {report.mutation_score:.1f}%
- Execution Time: {report.execution_time_ms}ms

Status Distribution:
"""
        
        for result in report.results:
            summary += f"- {result.mutant_id}: {result.status.value}"
            if result.failing_tests:
                summary += f" (failed tests: {', '.join(result.failing_tests)})"
            if result.error_message:
                summary += f" (error: {result.error_message[:100]}...)"
            summary += "\n"
        
        return summary
    
    def _format_survived_mutants(self, report: MutationTestReport, mutants: List[Mutant]) -> List[str]:
        """Format information about mutants that survived testing."""
        survived_mutants = []
        mutant_dict = {m.id: m for m in mutants}
        
        for result in report.results:
            if result.status == MutationStatus.SURVIVED:
                mutant = mutant_dict.get(result.mutant_id)
                if mutant:
                    description = (
                        f"Mutant {mutant.id} ({mutant.operator_name}):\n"
                        f"  Function: {mutant.function_name}\n"
                        f"  Line: {mutant.line_number}\n"
                        f"  Description: {mutant.description}\n"
                        f"  Original: {mutant.original_code}\n"
                        f"  Mutated: {mutant.mutated_code}\n"
                        f"  Execution Time: {result.execution_time_ms}ms\n"
                    )
                    survived_mutants.append(description)
        
        return survived_mutants
    
    def _format_killed_mutants(self, report: MutationTestReport, mutants: List[Mutant]) -> List[str]:
        """Format information about mutants that were killed by tests."""
        killed_mutants = []
        mutant_dict = {m.id: m for m in mutants}
        
        for result in report.results:
            if result.status == MutationStatus.KILLED:
                mutant = mutant_dict.get(result.mutant_id)
                if mutant:
                    description = (
                        f"Mutant {mutant.id} ({mutant.operator_name}):\n"
                        f"  Function: {mutant.function_name}\n"
                        f"  Line: {mutant.line_number}\n"
                        f"  Description: {mutant.description}\n"
                        f"  Killed by: {', '.join(result.failing_tests) if result.failing_tests else 'Unknown tests'}\n"
                        f"  Execution Time: {result.execution_time_ms}ms\n"
                    )
                    killed_mutants.append(description)
        
        return killed_mutants
    
    def create_mutation_summary(self, report: MutationTestReport, mutants: List[Mutant]) -> Dict[str, Any]:
        """Create a comprehensive summary of mutation testing results."""
        # Group results by function
        function_results = {}
        mutant_dict = {m.id: m for m in mutants}
        
        for result in report.results:
            mutant = mutant_dict.get(result.mutant_id)
            if mutant:
                func_name = mutant.function_name
                if func_name not in function_results:
                    function_results[func_name] = {
                        'total': 0,
                        'killed': 0,
                        'survived': 0,
                        'timeout': 0,
                        'error': 0
                    }
                
                function_results[func_name]['total'] += 1
                if result.status == MutationStatus.KILLED:
                    function_results[func_name]['killed'] += 1
                elif result.status == MutationStatus.SURVIVED:
                    function_results[func_name]['survived'] += 1
                elif result.status == MutationStatus.TIMEOUT:
                    function_results[func_name]['timeout'] += 1
                elif result.status == MutationStatus.ERROR:
                    function_results[func_name]['error'] += 1
        
        # Calculate function-level scores
        function_scores = {}
        for func_name, results in function_results.items():
            valid_mutants = results['killed'] + results['survived']
            if valid_mutants > 0:
                function_scores[func_name] = (results['killed'] / valid_mutants) * 100.0
            else:
                function_scores[func_name] = 0.0
        
        # Identify weak areas (functions with low mutation scores)
        weak_areas = [
            func_name for func_name, score in function_scores.items()
            if score < 75.0  # Less than 75% mutation score
        ]
        
        return {
            'overall_score': report.mutation_score,
            'function_scores': function_scores,
            'function_results': function_results,
            'weak_areas': weak_areas,
            'total_mutants': report.total_mutants,
            'execution_time_ms': report.execution_time_ms
        }