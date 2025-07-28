"""
BAML-powered client for AI interactions with better structured responses.
"""

import os
import json
from typing import List, Dict, Any, Optional

# Import BAML client
from baml_client.sync_client import b as baml_client
from baml_client.types import FuzzTestInput, CrashAnalysis


class BamlGeminiClient:
    """BAML-powered client for structured AI interactions."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the BAML client.
        
        Args:
            api_key: Google API key. If not provided, will look for GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY env var or pass api_key.")
        
        # Set environment variable for BAML to use
        os.environ['GEMINI_API_KEY'] = self.api_key
    
    def generate_fuzzing_inputs(self, function_signature: str, function_code: str, num_inputs: int = 10) -> List[Dict[str, Any]]:
        """Generate fuzzing inputs using BAML for structured responses.
        
        Args:
            function_signature: The function signature to analyze
            function_code: The complete function code
            num_inputs: Number of test inputs to generate
            
        Returns:
            List of dictionaries containing test inputs and expected behavior
        """
        try:
            # Use BAML to generate structured fuzzing inputs
            result = baml_client.GenerateFuzzingInputs(
                function_signature=function_signature,
                function_code=function_code,
                num_inputs=num_inputs
            )
            
            # Convert BAML response to the format expected by the fuzzer
            fuzzing_inputs = []
            for test_input in result:
                fuzzing_inputs.append({
                    'args': test_input.args,
                    'kwargs': test_input.kwargs,
                    'description': test_input.description,
                    'expected_behavior': test_input.expected_behavior
                })
            
            return fuzzing_inputs
            
        except Exception as e:
            print(f"Error generating fuzzing inputs with BAML: {e}")
            return []
    
    def analyze_crash(self, function_code: str, error_info: str, test_input: Dict[str, Any]) -> str:
        """Analyze a crash using BAML for structured response.
        
        Args:
            function_code: The function that crashed
            error_info: Error message and traceback
            test_input: The input that caused the crash
            
        Returns:
            Analysis of the crash and potential fixes
        """
        try:
            # Convert test_input to string for BAML
            test_input_str = json.dumps(test_input, indent=2)
            
            # Use BAML to analyze the crash
            result = baml_client.AnalyzeCrash(
                function_code=function_code,
                error_info=error_info,
                test_input=test_input_str
            )
            
            # Format the structured response into a readable analysis
            analysis = f"""Root Cause: {result.root_cause}

Severity: {result.severity.upper()}

Suggested Fix:
{result.suggested_fix}

Additional Test Cases to Prevent Similar Issues:
"""
            for i, test_case in enumerate(result.additional_test_cases, 1):
                analysis += f"{i}. {test_case}\n"
            
            return analysis
            
        except Exception as e:
            return f"Error: Failed to analyze crash using BAML: {e}"
    
    def generate_coverage_improvements(self, file_path: str, uncovered_functions: List[str], 
                                     missing_lines: List[int], current_coverage: float) -> List[Dict[str, Any]]:
        """Generate coverage improvement suggestions using BAML.
        
        Args:
            file_path: Path to the file being analyzed
            uncovered_functions: List of functions without coverage
            missing_lines: List of line numbers not covered
            current_coverage: Current coverage percentage
            
        Returns:
            List of structured improvement suggestions
        """
        try:
            # Use BAML to generate coverage improvements
            result = baml_client.GenerateCoverageImprovements(
                file_path=file_path,
                uncovered_functions=uncovered_functions,
                missing_lines=missing_lines,
                current_coverage=current_coverage
            )
            
            # Convert BAML response to dictionary format
            improvements = []
            for improvement in result:
                improvements.append({
                    'file_path': improvement.file_path,
                    'function_name': improvement.function_name,
                    'current_coverage_percentage': improvement.current_coverage_percentage,
                    'suggestion_type': improvement.suggestion_type,
                    'priority': improvement.priority,
                    'suggested_tests': improvement.suggested_tests,
                    'code_examples': improvement.code_examples
                })
            
            return improvements
            
        except Exception as e:
            print(f"Error generating coverage improvements with BAML: {e}")
            return []