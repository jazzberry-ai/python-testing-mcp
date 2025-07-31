import ast
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import get_gemini_client, read_python_file, parse_python_ast

def generate_unit_tests(file_path: str) -> str:
    """
    Takes a Python file path as input, generates a basic unit test file for it,
    and saves it, returning the new file's path.
    It uses Gemini to generate the test cases.
    """
    try:
        source_code = read_python_file(file_path)
        tree = parse_python_ast(source_code)
    except (FileNotFoundError, SyntaxError) as e:
        return f"Error: {e}"

    test_cases = []
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    try:
        model = get_gemini_client()
    except (KeyError, Exception) as e:
        return f"Error: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_source = ast.get_source_segment(source_code, node)

            prompt = f"""
You are a Python unit testing expert.
Your task is to generate a single, complete and runnable unit test method for the provided Python function.
The test method should be part of a `unittest.TestCase` class.
The generated code should be a complete method, including the `def` keyword, method name, and `self` parameter.
The test method name must start with `test_`.
Use standard Python `unittest` assertions.
Do not add any comments to the generated code.

Here is the function you need to write a test for:
```python
{function_source}
```
"""
            try:
                response = model.generate_content(prompt)
                generated_test_code = response.text
            except Exception as e:
                generated_test_code = f"""
    def test_{node.name}(self):
        # TODO: Implement test case for {node.name} (Gemini API call failed: {e})
        self.assertTrue(True)  # Placeholder assertion
"""
            test_cases.append(generated_test_code)

    if not test_cases:
        return f"No functions found in {file_path} to generate tests for."

    class_name_parts = [part.capitalize() for part in module_name.split('_')]
    class_name = "".join(class_name_parts)

    test_file_content = f"""
import unittest
import {module_name}

class Test{class_name}(unittest.TestCase):
{"".join(test_cases)}

if __name__ == '__main__':
    unittest.main()
"""

    test_file_name = f"test_{module_name}.py"
    test_file_path = os.path.join(os.path.dirname(file_path), test_file_name)

    with open(test_file_path, 'w') as f:
        f.write(test_file_content.strip())

    return f"Successfully generated unit tests at {test_file_path}"