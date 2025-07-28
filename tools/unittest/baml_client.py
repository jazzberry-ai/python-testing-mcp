"""
BAML-powered client for unit test generation with structured responses.
"""

import os
from typing import List, Dict, Any, Optional

# Import BAML client
from baml_client.sync_client import b as baml_client
from baml_client.types import UnitTestCase


class BamlUnitTestClient:
    """BAML-powered client for structured unit test generation."""
    
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
    
    def generate_unit_test_cases(self, function_signature: str, function_code: str, 
                               framework: str, docstring: str) -> List[Dict[str, Any]]:
        """Generate unit test cases using BAML for structured responses.
        
        Args:
            function_signature: The function signature to test
            function_code: The complete function code
            framework: Testing framework ('pytest' or 'unittest')
            docstring: Function docstring
            
        Returns:
            List of structured test cases
        """
        try:
            # Use BAML to generate structured unit test cases
            result = baml_client.GenerateUnitTestCases(
                function_signature=function_signature,
                function_code=function_code,
                framework=framework,
                docstring=docstring
            )
            
            # Convert BAML response to the format expected by the generator
            test_cases = []
            for test_case in result:
                test_cases.append({
                    'name': test_case.name,
                    'description': test_case.description,
                    'test_code': test_case.test_code,
                    'imports': test_case.imports
                })
            
            return test_cases
            
        except Exception as e:
            print(f"Error generating unit test cases with BAML: {e}")
            return []