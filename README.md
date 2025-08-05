# Python Testing Tools MCP Server

An advanced Model Context Protocol (MCP) server that provides AI-powered Python testing tools. This project leverages both Google's Gemini AI and BAML (Boundary ML) to intelligently generate comprehensive unit tests and perform sophisticated fuzz testing on Python code.

## Overview

This MCP server offers automated testing capabilities through four main tools:
1. **Intelligent Unit Test Generation** - Automatically creates comprehensive test suites with proper edge cases, assertions, and error handling
2. **AI-Powered Fuzz Testing** - Generates diverse, challenging inputs to test function robustness and discover potential crashes
3. **Advanced Coverage Testing** - Generates comprehensive test suites designed to achieve maximum code coverage with intelligent branch, loop, and exception path analysis
4. **Intelligent Mutation Testing** - Uses custom AST-based mutation engine with AI analysis to evaluate test suite quality and identify test gaps

The server uses a hybrid AI approach: BAML for structured test generation and Gemini for intelligent input generation, ensuring high-quality, reliable test outputs.

## Key Features

- **AI-Powered Unit Test Generation**: Uses BAML with Gemini to generate comprehensive unittest suites covering normal cases, edge cases, and error conditions
- **Intelligent Fuzz Testing**: Leverages AI to generate diverse, challenging inputs that test function boundaries and error handling
- **Advanced Coverage Testing**: AST-based code analysis with AI-generated tests targeting specific coverage scenarios for maximum line and branch coverage
- **Intelligent Mutation Testing**: Custom AST-based mutation engine that generates code mutations and uses AI to analyze test suite quality and suggest improvements
- **Built-in Coverage Measurement**: Integrates coverage.py library for real-time coverage reporting and analysis
- **BAML Integration**: Structured AI responses using BAML (Boundary ML) for consistent, parseable test generation
- **FastMCP Framework**: Built on FastMCP for efficient MCP server implementation
- **Robust Error Handling**: Graceful fallbacks and detailed error reporting throughout the testing pipeline
- **Modular Architecture**: Clean separation between tools, utilities, and AI clients for easy extension
- **Advanced Code Analysis**: Uses Python AST parsing for accurate function extraction, branch detection, and control flow analysis

## Architecture

The project follows a clean, modular architecture:
- **FastMCP Server**: Main entry point using the FastMCP framework
- **BAML Integration**: Structured AI prompts and response parsing via BAML
- **Dual AI Backend**: Combines BAML's structured generation with Gemini's language understanding
- **Utility Layer**: Shared functionality for file handling, AST parsing, and AI client management

## Directory Structure

```
python-testing-mcp/
├── python_testing_mcp_server.py   # Main FastMCP server entry point
├── baml_src/                      # BAML configuration and prompts
│   └── main.baml                  # AI function definitions and prompts
├── baml_client/                   # Generated BAML client code
│   ├── sync_client.py             # Synchronous BAML client
│   ├── types.py                   # Generated type definitions
│   └── [other generated files]    # Additional BAML runtime files
├── tools/                         # Core testing tool implementations
│   ├── unit_test_generator.py     # AI-powered unit test generation
│   ├── fuzz_tester.py             # Intelligent fuzz testing engine
│   ├── coverage_tester.py         # Advanced coverage testing with AST analysis
│   └── mutation_tester.py         # Intelligent mutation testing with AI analysis
├── utils/                         # Shared utilities and helpers
│   ├── __init__.py                # Module exports
│   ├── ai_clients.py              # Gemini AI client configuration
│   ├── file_handlers.py           # File I/O and AST parsing utilities
│   ├── mutation_engine.py         # Custom AST-based mutation engine
│   ├── mutation_test_executor.py  # Mutation test execution and reporting
│   └── mutation_intelligence.py   # AI-powered mutation analysis
├── demo/                          # Example files for testing
│   ├── basic_example_functions.py # Simple functions for basic testing
│   ├── medium_complexity.py       # Moderate complexity validation logic
│   ├── advanced_algorithms.py     # Complex algorithms (search, sort, math)
│   ├── data_processor.py          # Concurrent processing & state management
│   └── security_analyzer.py       # Security analysis & validation framework
├── pyproject.toml                 # Python project configuration and dependencies
├── uv.lock                        # Dependency lock file for reproducible builds
├── LICENSE                        # Apache 2.0 license
└── README.md                      # This documentation
```

## Configuration

The server uses environment variables for configuration:

- `GEMINI_API_KEY`: **Required** - Your Google Gemini API key for AI-powered test generation
- `GEMINI_MODEL`: Optional - Gemini model to use (default: `gemini-2.5-flash`)

The BAML configuration in `baml_src/main.baml` defines:
- AI function signatures for test generation, fuzz input creation, and coverage-focused test generation
- Structured response formats using BAML classes (PythonTestFile, FuzzInput, CoverageAnalysis)
- Detailed prompts for comprehensive test coverage, including branch and path analysis

## Installation

1. Install dependencies using uv:
```bash
uv sync
```

This will automatically create a virtual environment and install all dependencies from `pyproject.toml`.

3. Set your Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Running the Server

To run the MCP server:

```bash
uv run python python_testing_mcp_server.py
```

## Running the Server in Claude Code

Claude Code provides native MCP server support. Here are the recommended installation methods:

### Method 1: Using Claude Code's Native MCP Command (Recommended)

1. **Navigate to your project directory**:
```bash
cd /path/to/python-testing-mcp
```

2. **Install dependencies**:
```bash
uv sync
```

3. **Add the MCP server to Claude Code**:
```bash
claude mcp add python_testing_tools --env GEMINI_API_KEY=your-api-key-here -- uv run python python_testing_mcp_server.py
```

4. **Verify the server is connected**:
```bash
claude mcp list
```

You should see output like:
```
python_testing_tools: uv run python python_testing_mcp_server.py - ✓ Connected
```

### Method 2: Using FastMCP (Alternative)

If you prefer using FastMCP, you can try:
```bash
uv run fastmcp install python_testing_mcp_server.py --env-var GEMINI_API_KEY=your-api-key-here
```

**Note**: If FastMCP can't detect your Claude Code installation automatically, use Method 1 instead.

### Method 3: Manual Configuration

If the above methods don't work, you can manually configure the server by editing your `.claude.json` file:

```json
{
  "/path/to/your/project": {
    "mcpServers": {
      "python_testing_tools": {
        "type": "stdio",
        "command": "uv",
        "args": [
          "run",
          "python",
          "/path/to/your/project/python_testing_mcp_server.py"
        ],
        "env": {
          "GEMINI_API_KEY": "your-api-key-here"
        }
      }
    }
  }
}
```

### Verifying Installation

1. **Start Claude Code**:
```bash
claude
```

2. **Check MCP server status**:
```bash
/mcp
```

You should see "Reconnected to python_testing_tools" or similar confirmation.

### Testing the Tools

The demo files showcase increasingly sophisticated testing scenarios:

**Basic Testing (Simple Functions):**
```bash
create unit tests for @demo/basic_example_functions.py
fuzz test the add function in @demo/basic_example_functions.py
```

**Advanced Algorithm Testing (Complex Logic):**
```bash
generate coverage tests for @demo/advanced_algorithms.py
fuzz test the binary_search_with_analytics function in @demo/advanced_algorithms.py
run mutation testing on @demo/advanced_algorithms.py
```

**Concurrent Systems Testing (Threading & State):**
```bash
create unit tests for @demo/data_processor.py
generate coverage tests for @demo/data_processor.py
```

**Security Testing (Defensive Analysis):**
```bash
generate coverage tests for @demo/security_analyzer.py
run mutation testing on @demo/security_analyzer.py
```

These advanced demo files will demonstrate the full power of the MCP testing tools with:
- Complex branching logic and edge case handling
- Multi-threaded operations and state management
- Security vulnerability detection and input validation
- Sophisticated algorithmic implementations
- Advanced error handling and recovery patterns

## Available Tools

### Unit Test Generator
- **Function**: `generate_unit_tests_tool`
- **Description**: Generates comprehensive unit tests for all functions in a Python file using AI
- **Parameters**: 
  - `file_path` (str) - Path to the Python file to generate tests for
- **Features**:
  - Generates 4-6 test cases per function covering normal, edge, and error cases
  - Uses proper unittest framework with `self.assertRaises()` for exception testing
  - Automatically handles module imports and class naming conventions
  - Creates properly formatted test files with correct indentation

### Fuzz Tester
- **Function**: `fuzz_test_function_tool`
- **Description**: Performs intelligent fuzz testing on a specific function using AI-generated inputs
- **Parameters**: 
  - `file_path` (str) - Path to the Python file containing the function
  - `function_name` (str) - Name of the specific function to fuzz test
- **Features**:
  - Generates 20 diverse test inputs including edge cases and malformed data
  - Tests with boundary values, large inputs, and unusual data combinations
  - Reports crashes with detailed error traces and input values
  - Uses `ast.literal_eval()` for safe input parsing

### Coverage Tester
- **Function**: `generate_coverage_tests_tool`
- **Description**: Generates comprehensive test cases designed to achieve maximum code coverage using advanced AST analysis and AI-powered test generation
- **Parameters**: 
  - `file_path` (str) - Path to the Python file to generate coverage tests for
- **Features**:
  - **Advanced AST Analysis**: Automatically detects branches, loops, exception paths, and return statements
  - **Intelligent Coverage Targeting**: Generates tests specifically designed to cover all code paths
  - **Built-in Coverage Measurement**: Integrates coverage.py for real-time coverage reporting
  - **Comprehensive Test Scenarios**: Creates tests for:
    - Branch coverage (if/elif/else conditions)
    - Loop coverage (zero, one, multiple iterations, break/continue)
    - Exception coverage (try/except/finally blocks)
    - Return path coverage (all possible return statements)
    - Parameter coverage (different types, boundary values, edge cases)
    - Type compatibility testing (invalid inputs, TypeError scenarios)
  - **State-of-the-Art Testing**: Includes infinity/NaN testing, large number handling, empty collections
  - **Automatic Import Resolution**: Properly includes all necessary imports (sys, math, etc.)
  - **Coverage Reporting**: Generates detailed coverage reports showing achieved coverage percentages

### Mutation Tester
- **Function**: `mutation_testing_tool`
- **Description**: Performs intelligent mutation testing using a custom AST-based engine combined with AI analysis to evaluate test suite quality
- **Parameters**: 
  - `file_path` (str) - Path to the Python file to test
- **Features**:
  - **Custom AST-Based Mutation Engine**: Pure Python implementation without external dependencies
  - **Smart Mutation Operators**: 
    - Binary operators (`+` ↔ `-`, `==` ↔ `!=`, `and` ↔ `or`)
    - Constants (numbers, booleans, strings with intelligent variations)
    - Conditionals (negated conditions, always true/false branches)
  - **Intelligent Test Execution**: Automatic test discovery and safe file backup/restore
  - **AI-Powered Analysis**: Analyzes survived mutations and provides specific recommendations
  - **Comprehensive Reporting**: 
    - Mutation score calculation (% of mutations caught by tests)
    - Detailed analysis of test gaps and weaknesses
    - Prioritized recommendations for test improvements
    - Analysis-only mode when no tests are found
  - **Flexible Operation**: Works with or without existing test files

## Adding New Tools

The modular architecture makes it easy to extend the server with new testing tools:

1. **Create Tool Implementation**: Add a new Python file in the `tools/` directory
2. **Use Shared Utilities**: Import common functionality from `utils` module
3. **Integrate BAML (Optional)**: Add new AI functions to `baml_src/main.baml` for AI-powered tools
4. **Register Tool**: Import and register the tool in `python_testing_mcp_server.py`

Example:
```python
# tools/performance_tester.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import read_python_file, parse_python_ast

def analyze_performance(file_path: str) -> str:
    # Your implementation here
    source_code = read_python_file(file_path)
    # ... performance analysis logic
    return "Performance analysis results"

# Add to python_testing_mcp_server.py
from performance_tester import analyze_performance

@mcp.tool
def analyze_performance_tool(file_path: str) -> str:
    """Analyze performance characteristics of the given Python file."""
    return analyze_performance(file_path)
```

## Development

### Dependencies
All dependencies are managed in `pyproject.toml` including:
- `fastmcp` - MCP server framework
- `baml` & `baml-cli` - BAML AI integration
- `google-generativeai` - Gemini AI client
- `coverage` - Code coverage measurement and reporting
- `astunparse` - AST-to-source conversion for code analysis
- `pytest`, `black`, `isort`, `mypy` - Development tools

### Code Quality
Format code:
```bash
uv run black tools/ utils/ *.py
uv run isort tools/ utils/ *.py
```

Type checking:
```bash
uv run mypy tools/ utils/ *.py
```

### BAML Development
To modify AI prompts or add new AI functions:
1. Edit `baml_src/main.baml`
2. Run `uv run baml-cli generate --from baml_src` to update the client code
3. Test changes with the demo functions

### Testing the Tools
To test the various testing tools with the sophisticated demo files:

```bash
# Generate unit tests for complex algorithms
uv run python -c "from tools.unit_test_generator import generate_unit_tests; print(generate_unit_tests('demo/advanced_algorithms.py'))"

# Generate coverage tests for security framework
uv run python -c "from tools.coverage_tester import generate_coverage_tests; print(generate_coverage_tests('demo/security_analyzer.py'))"

# Run mutation testing on concurrent data processor
uv run python -c "from tools.mutation_tester import run_mutation_testing; print(run_mutation_testing('demo/data_processor.py'))"

# Run fuzz testing on complex algorithm functions
uv run python -c "from tools.fuzz_tester import fuzz_test_function; print(fuzz_test_function('demo/advanced_algorithms.py', 'binary_search_with_analytics'))"

# Test with different demo files to showcase various scenarios
uv run python -c "from tools.coverage_tester import generate_coverage_tests; print(generate_coverage_tests('demo/advanced_algorithms.py'))"
```

**Demo File Complexity Levels:**
- `basic_example_functions.py` - Simple arithmetic functions for initial testing
- `medium_complexity.py` - Input validation with moderate branching logic  
- `advanced_algorithms.py` - Complex algorithms with extensive error handling
- `data_processor.py` - Multi-threaded processing with state management
- `security_analyzer.py` - Security analysis with comprehensive validation

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
