import ast
import os
import importlib.util
import sys
import traceback
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import get_gemini_client, read_python_file, parse_python_ast

def fuzz_test_function(file_path: str, function_name: str) -> str:
    """
    Performs fuzz testing on a specific function within a given file.
    It uses Gemini to generate intelligent fuzzing inputs.
    """
    try:
        source_code = read_python_file(file_path)
        tree = parse_python_ast(source_code)
    except (FileNotFoundError, SyntaxError) as e:
        return f"Error: {e}"

    function_source = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            function_source = ast.get_source_segment(source_code, node)
            break

    if not function_source:
        return f"Error: Function '{function_name}' not found in {file_path}"

    try:
        model = get_gemini_client()
    except (KeyError, Exception) as e:
        return f"Error: {e}"

    prompt = f"""
You are a software security and testing expert.
Your task is to generate a Python list of 20 diverse and challenging inputs for fuzz testing the following Python function.
The list should include edge cases, malformed data, large inputs, and any other inputs that might cause unexpected behavior or crashes.
The output should be a single Python list of values.

Here is the function to fuzz:
```python
{function_source}
```
"""

    try:
        response = model.generate_content(prompt)
        fuzz_inputs_str = response.text.strip()
        if fuzz_inputs_str.startswith("```python"):
            fuzz_inputs_str = fuzz_inputs_str[len("```python"):].strip()
        if fuzz_inputs_str.endswith("```"):
            fuzz_inputs_str = fuzz_inputs_str[:-len("```")].strip()

        fuzz_inputs = ast.literal_eval(fuzz_inputs_str)
    except Exception as e:
        return f"Error generating or parsing fuzzing inputs from Gemini: {e}"

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    function_to_test = getattr(module, function_name)

    crashes = []
    for i, fuzz_input in enumerate(fuzz_inputs):
        try:
            if isinstance(fuzz_input, tuple):
                function_to_test(*fuzz_input)
            else:
                function_to_test(fuzz_input)
        except Exception as e:
            crashes.append({
                "input": fuzz_input,
                "error": traceback.format_exc()
            })

    if not crashes:
        return f"Fuzz testing completed for '{function_name}'. No crashes found in {len(fuzz_inputs)} test cases."

    result = f"Fuzz testing for '{function_name}' found {len(crashes)} crash(es):\n\n"
    for crash in crashes:
        result += f"- Input: {crash['input']}\n"
        result += f"  Error: {crash['error']}\n"

    return result