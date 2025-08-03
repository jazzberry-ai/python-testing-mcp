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

// Define the structure for coverage analysis data.
class CoverageAnalysis {
  function_name string @description("The name of the function being analyzed")
  branches string[] @description("List of conditional branches found in the function")
  loops string[] @description("List of loops found in the function")
  exception_paths string[] @description("List of exception handling paths")
  return_statements string[] @description("List of different return paths")
  parameters string[] @description("Function parameters and their types if available")
}

// Define the function for coverage-focused test generation.
function GenerateCoverageTests(source_code: string, analysis: CoverageAnalysis) -> PythonTestFile {
  client Gemini

  prompt #"
    You are an expert Python test engineer specializing in achieving maximum code coverage. Your task is to generate a comprehensive test suite that achieves 100% line and branch coverage for the following Python function.

    Do not add any commentary before or after the response.

    Source Code:
    ---
    {{ source_code }}
    ---

    Coverage Analysis:
    - Function: {{ analysis.function_name }}
    - Conditional branches: {{ analysis.branches }}
    - Loops: {{ analysis.loops }}
    - Exception paths: {{ analysis.exception_paths }}
    - Return statements: {{ analysis.return_statements }}
    - Parameters: {{ analysis.parameters }}

    Generate test cases that cover ALL of the following:

    1. **Branch Coverage**: Create test cases for EVERY conditional branch (if/elif/else)
       - Test both True and False conditions for each if statement
       - Test all elif branches individually
       - Test else branches when conditions are False

    2. **Loop Coverage**: 
       - Test loops with zero iterations (empty collections, False conditions)
       - Test loops with one iteration
       - Test loops with multiple iterations
       - Test early loop exits (break statements)
       - Test continue statements in loops

    3. **Exception Coverage**:
       - Test all try/except blocks by triggering each exception type
       - Test finally blocks execution
       - Test successful execution without exceptions

    4. **Return Path Coverage**:
       - Test each different return statement in the function
       - Test functions that return None implicitly
       - Test early returns from conditional blocks

    5. **Parameter Coverage**:
       - Test with different parameter types and values
       - Test boundary values for numeric parameters
       - Test empty/null values for collection parameters
       - Test invalid parameter types that might cause exceptions

    6. **Edge Cases**:
       - Test with minimum and maximum values
       - Test with empty inputs ([], "", {}, None)
       - Test with single-element collections
       - Test with very large inputs

    For each test case:
    - Use descriptive names that indicate what coverage they achieve (e.g., 'test_branch_condition_true', 'test_loop_zero_iterations')
    - Include comments explaining which coverage path is being tested
    - Use appropriate assertions to verify correct behavior
    - Use self.assertRaises() for exception testing
    - Ensure proper test isolation (each test is independent)

    Generate enough test cases to achieve 100% coverage of all identified paths.

    {{ ctx.output_format }}
  "#
}