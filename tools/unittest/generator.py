"""
Unit test generator for Python code using AI-powered analysis.
"""

import ast
import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Import the Gemini client from fuzzer tool for AI integration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'fuzzer'))
from gemini_client import GeminiClient
from .baml_client import BamlUnitTestClient

# Import analyzer from fuzzer for code analysis
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'fuzzer'))
from analyzer import CodeAnalyzer, FunctionInfo


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    description: str
    test_code: str
    imports: List[str]
    setup_code: str = ""
    teardown_code: str = ""


@dataclass
class TestSuite:
    """Represents a complete test suite for a Python file."""
    target_file: str
    test_file_name: str
    test_class_name: str
    imports: List[str]
    test_cases: List[TestCase]
    setup_code: str = ""
    teardown_code: str = ""


class UnitTestGenerator:
    """Generates comprehensive unit tests for Python code."""
    
    def __init__(self, gemini_api_key: Optional[str] = None, use_baml: bool = True):
        """Initialize the unit test generator.
        
        Args:
            gemini_api_key: Gemini API key for AI-powered test generation
            use_baml: Whether to use BAML for structured responses (default: True)
        """
        if gemini_api_key:
            if use_baml:
                try:
                    self.gemini_client = BamlUnitTestClient(gemini_api_key)
                    self.using_baml = True
                except Exception as e:
                    print(f"Warning: Failed to initialize BAML client, falling back to basic client: {e}")
                    self.gemini_client = GeminiClient(gemini_api_key)
                    self.using_baml = False
            else:
                self.gemini_client = GeminiClient(gemini_api_key)
                self.using_baml = False
        else:
            self.gemini_client = None
            self.using_baml = False
        
    def generate_test_suite(self, file_path: str, framework: str = "pytest") -> TestSuite:
        """Generate a complete test suite for a Python file.
        
        Args:
            file_path: Path to the Python file to test
            framework: Testing framework to use ('pytest', 'unittest')
            
        Returns:
            Complete test suite
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Analyze the target file
        analyzer = CodeAnalyzer(file_path)
        functions = analyzer.extract_functions()
        imports = analyzer.get_imports()
        classes = analyzer.get_classes()
        
        # Generate test file name
        file_stem = Path(file_path).stem
        test_file_name = f"test_{file_stem}.py"
        test_class_name = f"Test{file_stem.title().replace('_', '')}"
        
        # Generate test cases for each function
        test_cases = []
        required_imports = set()
        
        for func_info in functions:
            if not func_info.name.startswith('_'):  # Skip private functions
                func_tests = self._generate_function_tests(func_info, framework)
                test_cases.extend(func_tests)
                
                # Collect required imports
                for test_case in func_tests:
                    required_imports.update(test_case.imports)
        
        # Add basic imports based on framework
        if framework == "pytest":
            base_imports = [
                "import pytest",
                f"from {file_stem} import *"
            ]
        else:  # unittest
            base_imports = [
                "import unittest",
                f"from {file_stem} import *"
            ]
            
        all_imports = base_imports + list(required_imports)
        
        return TestSuite(
            target_file=file_path,
            test_file_name=test_file_name,
            test_class_name=test_class_name,
            imports=all_imports,
            test_cases=test_cases
        )
    
    def _generate_function_tests(self, func_info: FunctionInfo, framework: str) -> List[TestCase]:
        """Generate test cases for a specific function.
        
        Args:
            func_info: Information about the function to test
            framework: Testing framework being used
            
        Returns:
            List of test cases for the function
        """
        test_cases = []
        
        # Generate basic test cases
        basic_tests = self._generate_basic_tests(func_info, framework)
        test_cases.extend(basic_tests)
        
        # Generate AI-powered test cases if available
        if self.gemini_client:
            ai_tests = self._generate_ai_tests(func_info, framework)
            test_cases.extend(ai_tests)
        
        return test_cases
    
    def _generate_basic_tests(self, func_info: FunctionInfo, framework: str) -> List[TestCase]:
        """Generate basic test cases without AI.
        
        Args:
            func_info: Function information
            framework: Testing framework
            
        Returns:
            List of basic test cases
        """
        test_cases = []
        func_name = func_info.name
        
        # Happy path test
        happy_path_test = self._create_happy_path_test(func_info, framework)
        if happy_path_test:
            test_cases.append(happy_path_test)
        
        # Edge case tests
        edge_tests = self._create_edge_case_tests(func_info, framework)
        test_cases.extend(edge_tests)
        
        # Error handling tests
        error_tests = self._create_error_tests(func_info, framework)
        test_cases.extend(error_tests)
        
        return test_cases
    
    def _create_happy_path_test(self, func_info: FunctionInfo, framework: str) -> Optional[TestCase]:
        """Create a happy path test case."""
        func_name = func_info.name
        test_name = f"test_{func_name}_happy_path"
        
        # Generate basic test code based on function signature
        if framework == "pytest":
            test_code = f'''def {test_name}():
    """Test {func_name} with valid inputs."""
    # TODO: Add specific test implementation
    # result = {func_name}(valid_args)
    # assert result == expected_value
    pass'''
        else:  # unittest
            test_code = f'''def {test_name}(self):
    """Test {func_name} with valid inputs."""
    # TODO: Add specific test implementation
    # result = {func_name}(valid_args)
    # self.assertEqual(result, expected_value)
    pass'''
        
        return TestCase(
            name=test_name,
            description=f"Test {func_name} with valid inputs",
            test_code=test_code,
            imports=[]
        )
    
    def _create_edge_case_tests(self, func_info: FunctionInfo, framework: str) -> List[TestCase]:
        """Create edge case test cases."""
        test_cases = []
        func_name = func_info.name
        
        # Empty/None input test
        test_name = f"test_{func_name}_edge_cases"
        if framework == "pytest":
            test_code = f'''def {test_name}():
    """Test {func_name} with edge case inputs."""
    # TODO: Test with empty inputs, None values, boundary conditions
    # Examples:
    # - Empty lists/strings
    # - Zero values
    # - Maximum/minimum values
    # - None inputs
    pass'''
        else:  # unittest
            test_code = f'''def {test_name}(self):
    """Test {func_name} with edge case inputs."""
    # TODO: Test with empty inputs, None values, boundary conditions
    # Examples:
    # - Empty lists/strings
    # - Zero values
    # - Maximum/minimum values
    # - None inputs
    pass'''
        
        test_cases.append(TestCase(
            name=test_name,
            description=f"Test {func_name} with edge case inputs",
            test_code=test_code,
            imports=[]
        ))
        
        return test_cases
    
    def _create_error_tests(self, func_info: FunctionInfo, framework: str) -> List[TestCase]:
        """Create error handling test cases."""
        test_cases = []
        func_name = func_info.name
        
        test_name = f"test_{func_name}_error_handling"
        if framework == "pytest":
            test_code = f'''def {test_name}():
    """Test {func_name} error handling."""
    # TODO: Test error conditions
    # Examples:
    # with pytest.raises(ValueError):
    #     {func_name}(invalid_input)
    # with pytest.raises(TypeError):
    #     {func_name}(wrong_type)
    pass'''
        else:  # unittest
            test_code = f'''def {test_name}(self):
    """Test {func_name} error handling."""
    # TODO: Test error conditions
    # Examples:
    # with self.assertRaises(ValueError):
    #     {func_name}(invalid_input)
    # with self.assertRaises(TypeError):
    #     {func_name}(wrong_type)
    pass'''
        
        test_cases.append(TestCase(
            name=test_name,
            description=f"Test {func_name} error handling",
            test_code=test_code,
            imports=[]
        ))
        
        return test_cases
    
    def _generate_ai_tests(self, func_info: FunctionInfo, framework: str) -> List[TestCase]:
        """Generate AI-powered test cases.
        
        Args:
            func_info: Function information
            framework: Testing framework
            
        Returns:
            List of AI-generated test cases
        """
        if not self.gemini_client:
            return []
        
        try:
            if self.using_baml:
                # Use BAML for structured responses
                test_cases_data = self.gemini_client.generate_unit_test_cases(
                    function_signature=func_info.signature,
                    function_code=func_info.code,
                    framework=framework,
                    docstring=func_info.docstring
                )
                
                # Convert to TestCase objects
                test_cases = []
                for data in test_cases_data:
                    test_case = TestCase(
                        name=data['name'],
                        description=data['description'],
                        test_code=data['test_code'],
                        imports=data['imports']
                    )
                    test_cases.append(test_case)
                
                return test_cases
            else:
                # Use original method with basic client
                prompt = self._create_test_generation_prompt(func_info, framework)
                response = self.gemini_client.model.generate_content(prompt)
                
                if response and response.text:
                    return self._parse_ai_test_response(response.text, func_info.name, framework)
        except Exception as e:
            print(f"Warning: Failed to generate AI tests for {func_info.name}: {e}")
        
        return []
    
    def _create_test_generation_prompt(self, func_info: FunctionInfo, framework: str) -> str:
        """Create a prompt for AI test generation."""
        return f"""Generate comprehensive unit tests for this Python function using {framework}.

Function to test:
```python
{func_info.code}
```

Function signature: {func_info.signature}
Docstring: {func_info.docstring}

Please generate specific, executable test cases that cover:
1. Normal valid inputs with expected outputs
2. Edge cases (empty inputs, boundary values, etc.)
3. Error conditions with appropriate exception testing
4. Different input types and combinations

Return the response as a JSON array of test cases with this structure:
[
  {{
    "name": "test_function_name_specific_case",
    "description": "What this test verifies",
    "test_code": "Complete {framework} test function code",
    "imports": ["any additional imports needed"]
  }}
]

Make the tests specific and executable, not just templates. Include actual test data and assertions."""
    
    def _parse_ai_test_response(self, response: str, func_name: str, framework: str) -> List[TestCase]:
        """Parse AI response into test cases."""
        try:
            # Use the existing error-tolerant JSON parsing from GeminiClient
            parsed_data = self.gemini_client._parse_json_tolerant(response)
            
            if not isinstance(parsed_data, list):
                return []
            
            test_cases = []
            for item in parsed_data:
                if isinstance(item, dict) and all(key in item for key in ['name', 'description', 'test_code']):
                    test_case = TestCase(
                        name=item['name'],
                        description=item['description'],
                        test_code=item['test_code'],
                        imports=item.get('imports', [])
                    )
                    test_cases.append(test_case)
            
            return test_cases
            
        except Exception as e:
            print(f"Warning: Failed to parse AI test response for {func_name}: {e}")
            return []
    
    def generate_test_file_content(self, test_suite: TestSuite, framework: str = "pytest") -> str:
        """Generate the complete test file content.
        
        Args:
            test_suite: Test suite to generate
            framework: Testing framework to use
            
        Returns:
            Complete test file content as string
        """
        lines = []
        
        # File header
        lines.append('"""')
        lines.append(f'Unit tests for {test_suite.target_file}')
        lines.append('')
        lines.append('Generated by Software Testing Agent')
        lines.append('"""')
        lines.append('')
        
        # Imports
        for import_stmt in test_suite.imports:
            lines.append(import_stmt)
        lines.append('')
        
        if framework == "unittest":
            # Create unittest class
            lines.append(f'class {test_suite.test_class_name}(unittest.TestCase):')
            lines.append('    """Test cases for the target module."""')
            lines.append('')
            
            # Setup method if needed
            if test_suite.setup_code:
                lines.append('    def setUp(self):')
                lines.append('        """Set up test fixtures."""')
                for line in test_suite.setup_code.split('\n'):
                    lines.append(f'        {line}')
                lines.append('')
            
            # Test methods
            for test_case in test_suite.test_cases:
                # Add test method with proper indentation
                test_lines = test_case.test_code.split('\n')
                for line in test_lines:
                    lines.append(f'    {line}')
                lines.append('')
            
            # Teardown method if needed
            if test_suite.teardown_code:
                lines.append('    def tearDown(self):')
                lines.append('        """Clean up after tests."""')
                for line in test_suite.teardown_code.split('\n'):
                    lines.append(f'        {line}')
                lines.append('')
            
            # Main execution
            lines.append('')
            lines.append('if __name__ == "__main__":')
            lines.append('    unittest.main()')
            
        else:  # pytest
            # Setup fixture if needed
            if test_suite.setup_code:
                lines.append('@pytest.fixture')
                lines.append('def setup():')
                lines.append('    """Set up test fixtures."""')
                for line in test_suite.setup_code.split('\n'):
                    lines.append(f'    {line}')
                lines.append('')
            
            # Test functions
            for test_case in test_suite.test_cases:
                lines.append(test_case.test_code)
                lines.append('')
        
        return '\n'.join(lines)
    
    def save_test_file(self, test_suite: TestSuite, output_dir: str = ".", framework: str = "pytest") -> str:
        """Save the generated test file.
        
        Args:
            test_suite: Test suite to save
            output_dir: Directory to save the test file
            framework: Testing framework used
            
        Returns:
            Path to the saved test file
        """
        content = self.generate_test_file_content(test_suite, framework)
        output_path = os.path.join(output_dir, test_suite.test_file_name)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path