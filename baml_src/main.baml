// baml_src/main.baml

// Define the structure for a single test case.
class TestCase {
  name string @description("The name of the test function, e.g., 'test_addition'")
  body string @description("The complete Python code for the test function body, correctly indented.")
}

// Define the overall structure for the generated Python test file.
class PythonTestFile {
  imports string[] @description("A list of necessary import statements for the test file.")
  test_cases TestCase[] @description("An array of test cases to be included in the file.")
}

// Define the Gemini client
client<llm> Gemini {
  provider google-ai
  options {
    model "gemini-2.5-flash"
    api_key env.GEMINI_API_KEY
  }
}

// Define the structure for fuzzing inputs.
class FuzzInput {
  value string @description("A single fuzzing input, represented as a string.")
}

// Define the function that will call the LLM using Gemini.
function GenerateTests(source_code: string) -> PythonTestFile {
  client Gemini

  prompt #"
    You are an expert Python software tester. Your task is to generate a comprehensive suite of unittest tests for the following Python code.

    Do not add any commentary before or after the response.

    Source Code:
    ---
    {{ source_code }}
    ---

    Generate 4-6 different test cases covering:
    1. Normal/positive cases
    2. Edge cases (zero, empty, boundary values)
    3. Different data types if the function supports them
    4. Error cases that should raise exceptions (use self.assertRaises for these)

    For each test case, provide:
    - A descriptive test name that starts with 'test_'
    - The complete function body with proper assertions
    - For error cases, use self.assertRaises(ExceptionType): followed by the function call

    Please generate the tests in the required format.

    {{ ctx.output_format }}
  "#
}

// Define the function that will call the LLM for fuzzing.
function GenerateFuzzInputs(source_code: string) -> FuzzInput[] {
  client Gemini

  prompt #"
    You are a software security and testing expert.
    Your task is to generate a Python list of 20 diverse and challenging inputs for fuzz testing the following Python function.
    The list should include edge cases, malformed data, large inputs, and any other inputs that might cause unexpected behavior or crashes.
    
    IMPORTANT: Each input must be a simple Python literal (numbers, strings, lists, tuples, booleans, None) that can be parsed by ast.literal_eval(). 
    Do NOT use expressions like 10**100, float('inf'), or function calls. Use actual literal values like:
    - Large integers: 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
    - For infinity-like behavior, use very large numbers
    - For NaN-like behavior, use None or unusual combinations
    - Use actual byte strings like b'abc', not b'abc'

    Here is the function to fuzz:
    ```python
    {{ source_code }}
    ```

    Please generate the fuzzing inputs in the required format.

    {{ ctx.output_format }}
  "#
}