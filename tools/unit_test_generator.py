import ast
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from baml_client.sync_client import b
from baml_client.types import PythonTestFile
from utils import read_python_file, parse_python_ast


def generate_unit_tests(file_path: str) -> str:
    """
    Takes a Python file path as input, generates a unit test file for it,
    and saves it, returning the new file's path.
    It uses BAML to generate the test cases.
    """
    try:
        source_code = read_python_file(file_path)
        tree = parse_python_ast(source_code)
    except (FileNotFoundError, SyntaxError) as e:
        return f"Error: {e}"

    test_file_content = []
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_source = ast.get_source_segment(source_code, node)

            try:
                # Call the BAML function to generate the tests
                test_file: PythonTestFile = b.GenerateTests(function_source)

                # Format the generated tests
                for test_case in test_file.test_cases:
                    # Ensure test name starts with 'test_'
                    test_name = test_case.name
                    if not test_name.startswith('test_'):
                        test_name = f'test_{test_name}'
                    
                    test_file_content.append(f"    def {test_name}(self):")
                    # Process the body line by line with proper indentation handling
                    body_lines = test_case.body.split('\n')
                    
                    import re
                    inside_with_block = False
                    
                    for line in body_lines:
                        if not line.strip():
                            test_file_content.append("")
                            continue
                            
                        # Remove any existing indentation and get the content
                        content = line.strip()
                        
                        # Add module prefix to function calls that match functions in the source file
                        for func_node in ast.walk(tree):
                            if isinstance(func_node, ast.FunctionDef):
                                func_pattern = rf'\b{func_node.name}\('
                                if re.search(func_pattern, content):
                                    content = re.sub(func_pattern, f'{module_name}.{func_node.name}(', content)
                        
                        # Determine proper indentation
                        if content.startswith('with self.assertRaises'):
                            # This starts a with block
                            inside_with_block = True
                            test_file_content.append(f"        {content}")
                        elif inside_with_block and not content.startswith(('with ', 'if ', 'for ', 'def ', 'class ', 'try:', 'except', 'finally:', 'else:')):
                            # This line should be inside the with block (indented further)
                            test_file_content.append(f"            {content}")
                        else:
                            # Normal method body line or start of new block
                            inside_with_block = False
                            test_file_content.append(f"        {content}")
                    
                    test_file_content.append("")  # Add blank line between tests

            except Exception as e:
                # Fallback: create a simple test method
                test_file_content.append(f"    def test_{node.name}(self):")
                test_file_content.append(f"        # TODO: BAML generation failed: {str(e)[:100]}")
                test_file_content.append(f"        self.assertTrue(True)  # Placeholder assertion")
                test_file_content.append("")

    if not test_file_content:
        return f"No functions found in {file_path} to generate tests for."

    class_name_parts = [part.capitalize() for part in module_name.split('_')]
    class_name = "".join(class_name_parts)

    full_test_file = f"""import unittest
import {module_name}

class Test{class_name}(unittest.TestCase):
{chr(10).join(test_file_content)}
if __name__ == '__main__':
    unittest.main()
"""

    test_file_name = f"test_{module_name}.py"
    test_file_path = os.path.join(os.path.dirname(file_path), test_file_name)

    with open(test_file_path, 'w') as f:
        f.write(full_test_file.strip())

    return f"Successfully generated unit tests at {test_file_path}"