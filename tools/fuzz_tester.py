import ast
import os
import importlib.util
import sys
import traceback
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from baml_client.sync_client import b
from baml_client.types import FuzzInput
from utils import read_python_file, parse_python_ast

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
        # Call the BAML function to generate the fuzzing inputs
        fuzz_inputs: list[FuzzInput] = b.GenerateFuzzInputs(function_source)
        
        fuzz_input_values = []
        parsing_errors = 0
        for i, fuzz_input in enumerate(fuzz_inputs):
            try:
                parsed_value = ast.literal_eval(fuzz_input.value)
                fuzz_input_values.append(parsed_value)
            except Exception as parse_error:
                parsing_errors += 1
                # Skip inputs that can't be parsed
                continue
        
        if parsing_errors > 0:
            print(f"Warning: Skipped {parsing_errors} fuzzing inputs due to parsing errors")
        
        if not fuzz_input_values:
            return f"Error: No valid fuzzing inputs could be parsed from BAML response"
            
    except Exception as e:
        return f"Error generating fuzzing inputs from BAML: {e}"

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    function_to_test = getattr(module, function_name)

    crashes = []
    for i, fuzz_input in enumerate(fuzz_input_values):
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
        return f"Fuzz testing completed for '{function_name}'. No crashes found in {len(fuzz_input_values)} test cases."

    result = f"Fuzz testing for '{function_name}' found {len(crashes)} crash(es):\n\n"
    for crash in crashes:
        result += f"- Input: {crash['input']}\n"
        result += f"  Error: {crash['error']}\n"

    return result