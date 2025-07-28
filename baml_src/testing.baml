// BAML schemas for software testing tools

// Fuzzing test input data model
class FuzzTestInput {
  args (string | int | float | bool | null)[]
  kwargs map<string, (string | int | float | bool | null)>
  description string
  expected_behavior "normal" | "error" | "edge_case"
}

// Crash analysis result
class CrashAnalysis {
  root_cause string
  severity "low" | "medium" | "high" | "critical"
  suggested_fix string
  additional_test_cases string[]
}

// Unit test case structure
class UnitTestCase {
  name string
  description string
  test_code string
  imports string[]
}

// Coverage improvement suggestion
class CoverageImprovement {
  file_path string
  function_name string
  current_coverage_percentage float
  suggestion_type "missing_tests" | "edge_cases" | "error_handling"
  priority "low" | "medium" | "high"
  suggested_tests string[]
  code_examples string[]
}

// Generate fuzzing test inputs for a Python function
function GenerateFuzzingInputs(
  function_signature: string,
  function_code: string,
  num_inputs: int
) -> FuzzTestInput[] {
  client TestingFallback
  prompt #"
    Analyze this Python function and generate {{ num_inputs }} diverse fuzzing test inputs.
    Focus on edge cases, boundary conditions, and potential error conditions.

    Function signature: {{ function_signature }}
    Function code:
    ```python
    {{ function_code }}
    ```

    Generate test inputs that cover:
    1. Normal valid inputs
    2. Edge cases (empty, null, boundary values)
    3. Invalid inputs that might cause errors
    4. Large inputs that might cause performance issues
    5. Unusual data types or formats

    For special values use:
    - For infinity: use string "infinity" not float('inf')
    - For None/null: use null
    - For very large numbers: use regular integers like 999999999
    - Use only standard JSON types: string, number, boolean, null, array

    Generate realistic test cases with appropriate descriptions and expected behavior.

    {{ ctx.output_format }}
  "#
}

// Analyze a crash and provide insights
function AnalyzeCrash(
  function_code: string,
  error_info: string,
  test_input: string
) -> CrashAnalysis {
  client TestingFallback
  prompt #"
    Analyze this Python function crash and provide insights:

    Function code:
    ```python
    {{ function_code }}
    ```

    Error:
    {{ error_info }}

    Test input that caused the crash:
    {{ test_input }}

    Provide a comprehensive analysis including root cause, severity assessment, suggested fix, and additional test cases to prevent similar issues.

    {{ ctx.output_format }}
  "#
}

// Generate unit test cases for a function
function GenerateUnitTestCases(
  function_signature: string,
  function_code: string,
  framework: string,
  docstring: string
) -> UnitTestCase[] {
  client TestingFallback
  prompt #"
    Generate comprehensive unit tests for this Python function using {{ framework }}.

    Function to test:
    ```python
    {{ function_code }}
    ```

    Function signature: {{ function_signature }}
    Docstring: {{ docstring }}

    Please generate specific, executable test cases that cover:
    1. Normal valid inputs with expected outputs
    2. Edge cases (empty inputs, boundary values, etc.)
    3. Error conditions with appropriate exception testing
    4. Different input types and combinations

    Make the tests specific and executable, not just templates. Include actual test data and assertions.
    Use proper {{ framework }} syntax and assertions.

    Generate 3-5 comprehensive test cases that would provide good coverage.

    {{ ctx.output_format }}
  "#
}

// Generate coverage improvement suggestions
function GenerateCoverageImprovements(
  file_path: string,
  uncovered_functions: string[],
  missing_lines: int[],
  current_coverage: float
) -> CoverageImprovement[] {
  client TestingFallback
  prompt #"
    Analyze this Python file's coverage and suggest specific improvements:

    File: {{ file_path }}
    Current coverage: {{ current_coverage }}%
    Uncovered functions: {{ uncovered_functions }}
    Missing lines: {{ missing_lines }}

    Generate specific, actionable suggestions for improving test coverage.
    Focus on the most critical gaps and provide concrete test recommendations.

    For each suggestion, include:
    - Which function or area needs testing
    - What type of tests are missing
    - Priority level
    - Specific test scenarios to implement
    - Code examples where helpful

    {{ ctx.output_format }}
  "#
}

// Test the fuzzing function
test sample_fuzzing {
  functions [GenerateFuzzingInputs]
  args {
    function_signature "add_numbers(a, b)"
    function_code #"
      def add_numbers(a, b):
          """Add two numbers together."""
          return a + b
    "#
    num_inputs 5
  }
}

// Test the unit test generation
test sample_unit_tests {
  functions [GenerateUnitTestCases]
  args {
    function_signature "divide_numbers(x, y)"
    function_code #"
      def divide_numbers(x, y):
          """Divide x by y."""
          return x / y
    "#
    framework "pytest"
    docstring "Divide x by y."
  }
}