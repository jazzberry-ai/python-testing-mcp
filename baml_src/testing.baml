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

// Mutation testing schemas

// Mutation operator definition
class MutationOperator {
  name string
  description string
  category "arithmetic" | "comparison" | "logical" | "boolean" | "constant" | "statement"
  original_pattern string
  mutated_pattern string
  risk_level "low" | "medium" | "high"
}

// Individual mutant information
class Mutant {
  id string
  operator_name string
  original_code string
  mutated_code string
  line_number int
  column_number int
  function_name string
  description string
}

// Result of testing a single mutant
class MutationResult {
  mutant_id string
  status "killed" | "survived" | "timeout" | "error"
  execution_time_ms int
  test_output string
  failing_tests string[]
  error_message string
}

// Mutation strategy recommendation
class MutationStrategy {
  target_functions string[]
  recommended_operators MutationOperator[]
  priority_areas string[]
  expected_mutant_count int
  rationale string
}

// Comprehensive mutation testing report
class MutationReport {
  total_mutants int
  killed_mutants int
  survived_mutants int
  timeout_mutants int
  error_mutants int
  mutation_score float
  function_scores map<string, float>
  weak_areas string[]
  improvement_suggestions string[]
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

// Generate mutation testing strategy for a Python file
function GenerateMutationStrategy(
  file_path: string,
  function_code: string,
  existing_tests: string,
  target_functions: string[]
) -> MutationStrategy {
  client TestingFallback
  prompt #"
    Analyze this Python code and generate an intelligent mutation testing strategy:

    File: {{ file_path }}
    Target functions: {{ target_functions }}

    Code to analyze:
    ```python
    {{ function_code }}
    ```

    Existing tests:
    ```python
    {{ existing_tests }}
    ```

    Generate a comprehensive mutation testing strategy that includes:
    1. Recommended mutation operators based on the code patterns
    2. Priority areas where mutations are most likely to reveal test weaknesses
    3. Expected number of mutants to generate
    4. Rationale for the mutation strategy

    Focus on mutations that are most likely to:
    - Reveal missing test cases
    - Expose weak assertions
    - Find boundary condition issues
    - Identify logical errors in tests

    {{ ctx.output_format }}
  "#
}

// Analyze mutation testing results and provide insights
function AnalyzeMutationResults(
  file_path: string,
  mutation_results: string,
  survived_mutants: string[],
  killed_mutants: string[],
  mutation_score: float
) -> MutationReport {
  client TestingFallback
  prompt #"
    Analyze these mutation testing results and provide comprehensive insights:

    File: {{ file_path }}
    Mutation Score: {{ mutation_score }}%

    Mutation Results Summary:
    {{ mutation_results }}

    Survived Mutants (these reveal test weaknesses):
    {{ survived_mutants }}

    Killed Mutants (these show good test coverage):
    {{ killed_mutants }}

    Provide a detailed analysis including:
    1. Overall assessment of test quality based on mutation score
    2. Identification of weak areas where mutants survived
    3. Specific suggestions for improving tests to kill surviving mutants
    4. Function-by-function mutation score analysis
    5. Prioritized recommendations for test improvements

    Focus on actionable insights that will help improve test effectiveness.

    {{ ctx.output_format }}
  "#
}

// Generate specific test improvements based on surviving mutants
function GenerateTestImprovements(
  function_code: string,
  surviving_mutants: string[],
  current_tests: string
) -> string[] {
  client TestingFallback
  prompt #"
    Analyze these surviving mutants and generate specific test improvements:

    Original function:
    ```python
    {{ function_code }}
    ```

    Current tests:
    ```python
    {{ current_tests }}
    ```

    Surviving mutants that need to be killed:
    {{ surviving_mutants }}

    For each surviving mutant, provide:
    1. Why the current tests failed to catch this mutation
    2. Specific test cases that would kill this mutant
    3. The exact test code to add
    4. Explanation of what the new test validates

    Generate concrete, executable test code that will improve mutation score.

    Return an array of test improvement suggestions as strings.

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

// Test the mutation strategy generation
test sample_mutation_strategy {
  functions [GenerateMutationStrategy]
  args {
    file_path "test_calculator.py"
    function_code #"
      def add_numbers(a, b):
          """Add two numbers together."""
          if a < 0 or b < 0:
              return 0
          return a + b
      
      def multiply(x, y):
          """Multiply two numbers."""
          result = 0
          for i in range(y):
              result += x
          return result
    "#
    existing_tests #"
      def test_add_positive():
          assert add_numbers(2, 3) == 5
      
      def test_multiply_basic():
          assert multiply(3, 4) == 12
    "#
    target_functions ["add_numbers", "multiply"]
  }
}