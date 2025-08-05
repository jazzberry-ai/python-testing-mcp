import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from fastmcp import FastMCP
from unit_test_generator import generate_unit_tests
from fuzz_tester import fuzz_test_function
from coverage_tester import generate_coverage_tests

mcp = FastMCP(name="python_testing_tools")

@mcp.tool()
def generate_unit_tests_tool(file_path: str) -> str:
    """
    Takes a Python file path as input, generates a basic unit test file for it,
    and saves it, returning the new file's path.
    It uses Gemini to generate the test cases.
    """
    return generate_unit_tests(file_path)

@mcp.tool()
def fuzz_test_function_tool(file_path: str, function_name: str) -> str:
    """
    Performs fuzz testing on a specific function within a given file.
    It uses Gemini to generate intelligent fuzzing inputs.
    """
    return fuzz_test_function(file_path, function_name)

@mcp.tool()
def generate_coverage_tests_tool(file_path: str) -> str:
    """
    Generates comprehensive test cases designed to achieve maximum code coverage.
    Analyzes code structure using AST and creates tests for all branches, loops, exception paths, and edge cases.
    Uses AI to generate intelligent test cases that target specific coverage scenarios.
    """
    return generate_coverage_tests(file_path)

if __name__ == "__main__":
    mcp.run()
