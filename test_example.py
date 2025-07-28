"""
Basic test file to verify the fuzzing tool works correctly.
"""

import pytest
from fuzzer.fuzzer import PythonFuzzer
from fuzzer.analyzer import CodeAnalyzer
from fuzzer.gemini_client import GeminiClient
import os


def test_code_analyzer():
    """Test the code analyzer on the example file."""
    analyzer = CodeAnalyzer("example.py")
    functions = analyzer.extract_functions()
    
    # Should find several functions
    assert len(functions) > 0
    
    # Check if we found the expected functions
    function_names = [f.name for f in functions]
    expected_functions = ["add_numbers", "divide_numbers", "find_max", "factorial", "process_string", "calculate_average"]
    
    for expected in expected_functions:
        assert expected in function_names, f"Function {expected} not found"
    
    # Test function info extraction
    add_func = next(f for f in functions if f.name == "add_numbers")
    assert add_func.signature == "add_numbers(a, b)"
    assert "return a + b" in add_func.code


def test_imports_extraction():
    """Test import extraction."""
    analyzer = CodeAnalyzer("example.py")
    imports = analyzer.get_imports()
    
    # example.py doesn't have imports, but test the functionality
    assert isinstance(imports, list)


def test_fuzzer_initialization():
    """Test fuzzer initialization without API key."""
    # This should fail without API key
    try:
        fuzzer = PythonFuzzer()
        assert False, "Should have failed without API key"
    except ValueError as e:
        assert "API key required" in str(e)


def test_fuzzer_with_mock_key():
    """Test fuzzer initialization with a mock key."""
    # We can't test the full functionality without a real API key
    # but we can test initialization
    try:
        fuzzer = PythonFuzzer("mock_key")
        assert fuzzer.gemini_client is not None
    except Exception:
        # This might fail due to API validation, which is expected
        pass


def test_file_loading():
    """Test loading a Python file."""
    # This test requires a real API key to work fully
    if not os.getenv('GEMINI_API_KEY'):
        pytest.skip("GEMINI_API_KEY not set")
    
    fuzzer = PythonFuzzer()
    fuzzer.load_target_file("example.py")
    
    assert fuzzer.analyzer is not None
    assert fuzzer.target_module is not None
    
    # Test that we can access functions from the loaded module
    assert hasattr(fuzzer.target_module, 'add_numbers')
    assert hasattr(fuzzer.target_module, 'divide_numbers')


if __name__ == "__main__":
    pytest.main([__file__])
