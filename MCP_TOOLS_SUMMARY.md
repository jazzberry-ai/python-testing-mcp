# MCP Tools Summary

This document lists all available MCP tools that AI models can use through this software testing server.

## 🎯 Available Tools (13 Total)

### 🔍 Code Analysis
- **`analyze_python_code`**: Analyze a Python file to extract function information and structure
  - Returns: Function signatures, docstrings, line numbers, imports, classes

### 🎲 Fuzzing & Test Generation  
- **`fuzz_python_file`**: Fuzz test all functions in a Python file using AI-generated test cases
  - Parameters: `file_path`, `num_tests` (default: 10), `specific_function` (optional)
  - Returns: Comprehensive fuzzing report with crash analysis

- **`generate_test_inputs`**: Generate AI-powered test inputs for a specific function
  - Parameters: `function_code`, `function_signature`, `num_tests` (default: 5)
  - Returns: Structured test inputs with descriptions and expected behaviors

### 🧬 Mutation Testing (NEW)
- **`run_python_mutation_tests`**: Run comprehensive mutation tests on Python code to assess test quality
  - Parameters: `file_path`, `test_command` (default: "python -m pytest"), `target_functions` (optional), `operator_names` (optional), `max_mutants` (default: 50), `timeout_seconds` (default: 30)
  - Returns: Detailed mutation testing report with mutation score and analysis

- **`analyze_mutation_results`**: Analyze mutation testing results and provide AI-powered insights
  - Parameters: `file_path`, `results_json`
  - Returns: AI-powered analysis of test quality and weaknesses

- **`generate_mutation_strategy`**: Generate an AI-powered mutation testing strategy for Python code
  - Parameters: `file_path`, `target_functions` (optional)
  - Returns: Recommended mutation operators and testing strategy

- **`suggest_mutation_test_improvements`**: Suggest specific test improvements based on mutation testing results
  - Parameters: `file_path`, `results_json`
  - Returns: Specific, actionable test improvement recommendations

### 🧪 Unit Test Generation
- **`generate_unit_tests`**: Generate comprehensive unit tests for a Python file. Returns complete test file content that can be saved and used immediately
  - Parameters: `file_path`, `test_framework` (default: "pytest"), `output_file` (optional)
  - Returns: Complete executable test file content

- **`generate_test_file_content`**: Generate unit test file content without saving to disk. Returns the complete test file as a string
  - Parameters: `file_path`, `test_framework` (default: "pytest")
  - Returns: Test file content as string

- **`analyze_test_coverage_gaps`**: Analyze a Python file and suggest specific unit tests needed to improve coverage
  - Parameters: `file_path`
  - Returns: Detailed analysis of missing test coverage with specific recommendations

### 📊 Coverage Analysis
- **`run_python_coverage`**: Run coverage analysis on Python code with optional test execution
  - Parameters: `source_path`, `test_path` (optional), `test_command` (optional), `include_patterns` (optional), `exclude_patterns` (optional)
  - Returns: Comprehensive coverage report with line-by-line analysis

- **`analyze_coverage_report`**: Analyze an existing coverage JSON report and provide insights
  - Parameters: `coverage_json_path`
  - Returns: Analysis of existing coverage data with insights

- **`suggest_coverage_improvements`**: Analyze code coverage and suggest specific test improvements
  - Parameters: `source_path`, `coverage_threshold` (default: 80)
  - Returns: Prioritized suggestions for improving test coverage

## 🔧 Tool Usage Patterns

### For AI Models/Clients:
```
# Comprehensive testing workflow
1. analyze_python_code → understand code structure
2. generate_unit_tests → create initial test suite  
3. run_python_coverage → assess coverage
4. run_python_mutation_tests → evaluate test quality
5. analyze_mutation_results → get improvement insights
6. suggest_mutation_test_improvements → get specific fixes

# Quick fuzzing
fuzz_python_file → immediate bug discovery

# Targeted testing
generate_test_inputs → specific function testing
analyze_test_coverage_gaps → identify missing tests
```

### Safety Guarantees:
- ✅ **Original files never modified** - all tools operate safely
- ✅ **Temporary file isolation** - mutations in isolated environments  
- ✅ **Automatic cleanup** - no file system pollution
- ✅ **Error boundaries** - robust error handling prevents corruption

### AI Integration:
- 🤖 **BAML-powered responses** - structured, type-safe AI interactions
- 🔄 **Multi-provider fallback** - Gemini → OpenAI → Claude
- 📊 **Rich analysis** - detailed insights and recommendations
- 🎯 **Context-aware** - intelligent suggestions based on code patterns

## 🚀 Recent Additions:
- **Mutation Testing Suite**: Complete mutation testing capabilities with 9 operator types
- **AI-Powered Analysis**: Advanced insights for test quality assessment  
- **Safety Architecture**: Bulletproof safety guarantees for production use