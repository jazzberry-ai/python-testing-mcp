# Software Testing MCP Server

An open-source Model Context Protocol (MCP) server that provides AI agents with access to professional software testing tools and techniques. This extensible testing toolkit enables AI assistants like Claude, Cursor, and other MCP-compatible clients to perform comprehensive software quality assurance tasks.

## Vision

We're building a comprehensive testing ecosystem that bridges the gap between AI capabilities and established software testing methodologies. By providing AI agents with access to industry-standard testing tools through a unified MCP interface, we enable intelligent, automated testing workflows that combine human expertise with AI-powered analysis.

## Available Testing Tools

### 🎯 Python Fuzzer
AI-powered fuzzing tool that automatically generates comprehensive test inputs for Python functions. Uses advanced language models to create intelligent test cases covering edge cases, boundary conditions, and error scenarios.

**Key Features:**
- **🤖 AI-Generated Test Cases**: Leverages Google Gemini for intelligent test input generation
- **🔍 Automatic Function Discovery**: Analyzes Python files to identify testable functions
- **💥 Crash Analysis**: AI-powered analysis of failures with improvement suggestions
- **📊 Detailed Reporting**: Comprehensive test results with success rates and insights
- **🛡️ Error-Tolerant Parsing**: Robust handling of malformed AI responses

### 🧬 Mutation Testing Suite
Comprehensive mutation testing framework that evaluates test suite quality by introducing artificial bugs (mutants) and measuring how many are detected by your tests. This advanced testing technique provides deep insights into test effectiveness.

**Key Features:**
- **🎯 Intelligent Mutant Generation**: Creates realistic code mutations using 9+ mutation operators
- **📊 Quality Assessment**: Mutation score calculation and detailed test quality metrics
- **🤖 AI-Powered Analysis**: Advanced insights into test weaknesses and improvement strategies
- **🛡️ Production-Safe**: Isolated execution environment with automatic cleanup
- **⚡ Configurable Execution**: Customizable test commands, timeouts, and targeting options
- **💡 Actionable Insights**: Specific recommendations for improving test coverage and quality

### 🧪 Unit Test Generator
Automated unit test generation tool that creates comprehensive test suites for Python code using AI-powered analysis. Generates production-ready test files with proper fixtures, edge cases, and error handling.

**Key Features:**
- **📝 Complete Test Files**: Generates ready-to-run test files with pytest or unittest frameworks
- **🎯 Intelligent Test Cases**: AI-generated tests covering normal, edge, and error scenarios
- **🔍 Coverage Gap Analysis**: Identifies missing test coverage and suggests specific improvements
- **📋 Multiple Frameworks**: Support for pytest and unittest testing frameworks
- **🤖 Context-Aware**: Understands code patterns and generates appropriate test strategies

### 📈 Python Coverage Analyzer
Comprehensive code coverage analysis tool that integrates with existing Python testing frameworks to provide detailed coverage insights and improvement suggestions.

**Key Features:**
- **📊 Coverage Analysis**: Detailed line, branch, and function coverage reporting
- **🔍 Gap Identification**: Automatically identifies critical coverage gaps
- **💡 Test Suggestions**: AI-powered recommendations for improving test coverage
- **📈 Coverage Tracking**: Historical coverage analysis and trend monitoring
- **🎯 Targeted Testing**: Prioritized suggestions based on code criticality

## MCP Server Architecture

Built as a Model Context Protocol server with a plugin-based architecture that makes it easy to add new testing capabilities:

- **🔧 MCP Integration**: Native support for Claude, Cursor, and other MCP-compatible AI clients
- **🏗️ Plugin Architecture**: Self-contained testing tools with automatic discovery
- **📋 Tool Registry**: Dynamic tool registration and routing system
- **🔌 Extensible Framework**: Add new testing tools without modifying core server code
- **⚡ Async Operations**: Non-blocking execution for better performance
- **🛡️ Error Handling**: Robust error management and graceful failure recovery

## Installation

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd software-testing-agent
   ```

2. **Set up Python environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Get a Gemini API key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Set it as an environment variable:
   
   **Linux/macOS**:
   ```bash
   export GEMINI_API_KEY=your_actual_api_key_here
   ```
   
   **Windows**:
   ```cmd
   set GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Test installation**:
   ```bash
   # Test without API (uses local test cases)
   python local_fuzz_test.py
   
   # Test with API (requires valid key)
   python main.py example.py --num-tests 3
   ```

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 512MB RAM
- **Dependencies**: See `requirements.txt`

## Usage

### Standalone CLI Usage

Fuzz all functions in a Python file:
```bash
python main.py example.py
```

### Advanced CLI Options

```bash
# Generate 20 test cases per function
python main.py example.py -n 20

# Fuzz only a specific function
python main.py example.py -f divide_numbers

# Save detailed report to JSON file
python main.py example.py -o report.json

# Use a specific API key
python main.py example.py --api-key your_actual_api_key
```

### MCP Server Integration

The primary interface for this testing toolkit is through the MCP (Model Context Protocol) server, which enables seamless integration with AI assistants like Claude, Cursor, and other MCP-compatible clients. This allows AI agents to leverage professional testing tools directly in their workflows.

#### Setup for MCP Clients

1. **For Claude Desktop**, add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "python-fuzzing-tool": {
      "command": "python",
      "args": ["/path/to/your/software-testing-agent/mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

2. **For Cursor**, add to your MCP configuration:
```json
{
  "servers": {
    "python-fuzzing-tool": {
      "command": "python",
      "args": ["/path/to/your/software-testing-agent/mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

#### Available MCP Tools (13 Total)

**🔍 Code Analysis:**
- `analyze_python_code`: Code structure analysis and function extraction

**🎯 Fuzzing & Test Generation:**
- `fuzz_python_file`: Comprehensive fuzzing of all functions in a Python file
- `generate_test_inputs`: AI-powered test case generation for specific functions

**🧬 Mutation Testing:**
- `run_python_mutation_tests`: Run comprehensive mutation tests to assess test quality
- `analyze_mutation_results`: AI-powered analysis of mutation testing results
- `generate_mutation_strategy`: Generate optimal mutation testing strategies
- `suggest_mutation_test_improvements`: Get specific recommendations for test improvements

**🧪 Unit Test Generation:**
- `generate_unit_tests`: Generate complete test files with comprehensive test cases
- `generate_test_file_content`: Generate test file content without saving to disk
- `analyze_test_coverage_gaps`: Identify missing test coverage and suggest improvements

**📊 Coverage Analysis:**
- `run_python_coverage`: Execute coverage analysis with configurable test commands
- `analyze_coverage_report`: Parse and analyze existing coverage JSON reports
- `suggest_coverage_improvements`: Generate targeted recommendations for improving coverage

#### MCP Usage Examples

Once configured with an AI client, you can use natural language commands like:

**Fuzzing:**
```
Please fuzz test the file main.py with 10 test cases per function
```

**Mutation Testing:**
```
Run mutation tests on my calculator.py file and analyze the results
Generate a mutation testing strategy for my authentication module
```

**Unit Test Generation:**
```
Generate comprehensive unit tests for my utils.py file using pytest
Analyze test coverage gaps in my data_processor.py file
```

**Coverage Analysis:**
```
Run coverage analysis on my src/ directory and suggest improvements
Analyze my existing coverage report and provide insights
```

**Code Analysis:**
```
Analyze the Python file utils.py and show me its function structure
```

The MCP server automatically routes requests to the appropriate testing tools and returns comprehensive, formatted results.

### Example Output

```
Initializing fuzzer for: example.py
Found 6 functions to fuzz:
  - add_numbers (line 7)
  - divide_numbers (line 12)
  - find_max (line 17)
  - factorial (line 23)
  - process_string (line 34)
  - calculate_average (line 48)

Fuzzing function: add_numbers
Running 10 test cases...
  Test 1/10: Normal positive integers
  Test 2/10: Zero values test
  ...

============================================================
FUZZING SUMMARY
============================================================
Functions tested: 6
Total test cases: 60
Successful tests: 52
Total crashes: 8
Success rate: 86.7%

Per-function results:
  ✓ add_numbers: 10/10 passed, 0 crashes
  ✗ divide_numbers: 8/10 passed, 2 crashes
  ✓ find_max: 9/10 passed, 1 crash
  ...

⚠️  Found 8 crashes that need investigation!
```

## How It Works

1. **Code Analysis**: The tool parses Python files using the AST module to extract function signatures, documentation, and code structure
2. **AI Test Generation**: Gemini analyzes each function and generates diverse test inputs covering:
   - Normal valid inputs
   - Edge cases (empty, null, boundary values)  
   - Invalid inputs that might cause errors
   - Large inputs for performance testing
   - Unusual data types or formats
3. **Error-Tolerant Parsing**: Uses BAML-inspired techniques to parse malformed JSON responses from AI, handling:
   - Trailing commas and missing quotes
   - Python-style values (True/False/None)
   - Markdown-wrapped JSON responses
   - Unquoted keys and syntax errors
4. **Test Execution**: Each generated test case is executed against the target function with proper error handling
5. **Crash Analysis**: Any crashes are analyzed by Gemini to provide insights on root causes and potential fixes
6. **Reporting**: Comprehensive reports show success rates, crash details, and AI-powered analysis

## Project Structure

The project is organized with a modular architecture:

### Core Components
- **`tools/`**: Main directory containing all testing tools
  - **`registry.py`**: Tool discovery and registration system
  - **`fuzzer/`**: Python fuzzing tool implementation
    - **`analyzer.py`**: Python code analysis and AST parsing
    - **`gemini_client.py`**: AI API communication with error-tolerant parsing
    - **`fuzzer.py`**: Core fuzzing logic and test execution
    - **`tool.py`**: MCP integration for the fuzzer tool
  - **`mutation/`**: Mutation testing framework
    - **`mutator.py`**: Safe mutation engine with 9+ operators
    - **`operators.py`**: Collection of mutation operators
    - **`runner.py`**: Mutation test execution and reporting
    - **`baml_client.py`**: BAML-powered AI analysis
    - **`tool.py`**: MCP integration for mutation testing
  - **`unittest/`**: Unit test generation toolkit
    - **`generator.py`**: AI-powered test case generation
    - **`baml_client.py`**: BAML client for test generation
    - **`tool.py`**: MCP integration for unit test generation
  - **`coverage/`**: Coverage analysis tools
    - **`analyzer.py`**: Coverage data analysis and reporting
    - **`runner.py`**: Coverage execution and data collection
    - **`tool.py`**: MCP integration for coverage analysis
- **`baml_src/`**: BAML configuration for AI model interactions
- **`mcp_server.py`**: MCP server that routes requests to appropriate tools
- **`main.py`**: Command-line interface for standalone tool usage

### Adding New Testing Tools

The modular architecture makes it simple to extend the server with new testing capabilities:

1. **Create Tool Directory**: Add a new directory under `tools/` (e.g., `tools/my_testing_tool/`)
2. **Implement BaseTool Interface**: Follow the `BaseTool` abstract class contract
3. **Define MCP Tools**: Specify the MCP tool definitions your tool provides
4. **Add Entry Point**: Create a `tool.py` file with a `get_tool()` function
5. **Automatic Discovery**: The tool registry will automatically discover and register your tool

**Example Tool Structure:**
```
tools/my_testing_tool/
├── __init__.py
├── tool.py          # MCP integration
├── analyzer.py      # Core functionality
└── runner.py        # Test execution
```

## Developer Testing

For developers working on the codebase, we provide comprehensive testing tools to validate your development environment and tool implementations.

### Quick Development Validation

Run the developer testing script to validate your setup:

```bash
# Run all development tests
python dev_test.py

# Quick validation (recommended for frequent testing)
python dev_test.py --quick

# Test only specific components
python dev_test.py --baml-only      # Test BAML integration
python dev_test.py --tools-only     # Test tool implementations  
python dev_test.py --mcp-only       # Test MCP server

# Verbose output for debugging
python dev_test.py --verbose
```

### What the Developer Tests Cover

**🏗️ Project Structure**: Validates all required files exist
**🤖 BAML Integration**: Tests AI client setup and schema validation  
**🔧 Tool Registry**: Validates tool discovery and MCP integration
**🧪 Sample Functionality**: Tests core logic with sample data
**🖥️ MCP Server**: Tests server initialization and tool routing
**📦 Dependencies**: Validates all required packages are installed
**🌍 Environment**: Checks Python version and API key setup

### Sample Testing Data

Use the provided sample module for testing your tools:

```bash
# Test fuzzing with sample data
python main.py test_samples/sample_module.py --num-tests 5

# Generate unit tests for sample module
# (via MCP client): "Generate unit tests for test_samples/sample_module.py"

# Run mutation tests on sample module  
# (via MCP client): "Run mutation tests on test_samples/sample_module.py"
```

The `test_samples/sample_module.py` includes:
- **Simple functions** (add, divide) for basic testing
- **Complex algorithms** with multiple branches and edge cases
- **Class methods** for testing object-oriented code
- **Error handling patterns** for exception testing
- **Type hints and documentation** for comprehensive analysis

### Development Workflow

```bash
# 1. Set up development environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run development tests after changes
python dev_test.py --quick

# 3. Test specific functionality you're working on
python dev_test.py --tools-only     # When working on tools
python dev_test.py --baml-only      # When working on AI integration

# 4. Run full test suite before committing
python dev_test.py --verbose
```

### Test Results Interpretation

The developer test script provides colored output:
- ✅ **Green**: Tests passed successfully
- ❌ **Red**: Tests failed - needs attention  
- ⚠️ **Yellow**: Warnings - may impact functionality
- ℹ️ **Blue**: Informational messages (verbose mode)

**Success Criteria**: All tests should pass for a healthy development environment. If tests fail, the script provides specific error details and suggestions for resolution.

### Legacy Testing

Run the included pytest test suite:
```bash
python -m pytest test_example.py -v
```

Note: Some tests require a valid `GEMINI_API_KEY` environment variable.

## Example Target File

The repository includes `example.py` with various functions to demonstrate the fuzzer:

```python
def divide_numbers(x, y):
    """Divide x by y."""
    return x / y

def find_max(numbers):
    """Find the maximum number in a list."""
    if not numbers:
        raise ValueError("List cannot be empty")
    return max(numbers)
```

## Troubleshooting

### Common Issues

**API Key Issues**:
```bash
# Error: "Gemini API key required"
export GEMINI_API_KEY=your_actual_key  # Make sure key is set
echo $GEMINI_API_KEY                    # Verify key is set correctly
```

**Import Errors**:
```bash
# Error: "ModuleNotFoundError"
pip install -r requirements.txt        # Reinstall dependencies
python -c "import google.generativeai"  # Test specific import
```

**Permission Issues**:
```bash
# Error: "Permission denied"
chmod +x mcp_server.py                  # Make script executable
python mcp_server.py                    # Run with python directly
```

**JSON Parsing Issues**:
- The tool includes error-tolerant parsing that handles most malformed AI responses
- If issues persist, try reducing the number of test cases with `--num-tests 3`

### Getting Help

1. Check existing [Issues](../../issues) for similar problems
2. Review the [Contributing Guide](CONTRIBUTING.md) for setup details  
3. Create a new issue with:
   - Error message
   - Python version (`python --version`)
   - Operating system
   - Steps to reproduce

## Recent Major Updates

### ✨ What's New (Latest Release)
- **🧬 Mutation Testing Suite**: Complete mutation testing framework with 9+ operators
- **🧪 Unit Test Generator**: AI-powered test file generation with pytest/unittest support
- **🤖 BAML Integration**: Advanced AI model interactions with multi-provider fallback
- **🛡️ Production Safety**: Bulletproof safety guarantees with isolated execution
- **📊 Enhanced Analysis**: Deeper insights and actionable improvement recommendations
- **🎯 13 MCP Tools**: Comprehensive testing toolkit with specialized capabilities

## Current Limitations & Roadmap

### Current Limitations
- **Language Support**: Currently focused on Python (JavaScript, Go, Rust support planned)
- **AI Dependency**: Some features require API keys for cloud-based AI models (local models planned)
- **Integration Scope**: Individual function and unit testing (end-to-end testing tools planned)
- **Advanced Features**: Some Python language features may need additional support

### Planned Enhancements
- **📝 Multi-Language Support**: JavaScript, TypeScript, Go, Rust testing tools
- **🔄 Integration Testing**: End-to-end and integration testing capabilities
- **🎯 Performance Testing**: Load testing and performance analysis tools
- **🔐 Security Testing**: Static analysis and vulnerability scanning tools
- **📊 Test Management**: Test suite organization and execution management
- **🤖 Local AI Models**: Support for local/offline AI model execution
- **🚀 CI/CD Integration**: GitHub Actions, Jenkins, and other CI/CD platform support

## Contributing to the Testing Ecosystem

We're building an open-source community around AI-powered software testing. Whether you're interested in testing methodologies, AI integration, or developer tooling, there are many ways to contribute:

### Ways to Contribute
- **🔧 Tool Development**: Create new testing tools for different languages or methodologies
- **🤖 AI Integration**: Improve AI model integration and prompt engineering
- **📚 Documentation**: Help document testing best practices and tool usage
- **🐛 Bug Reports**: Report issues and help improve tool reliability
- **💡 Feature Requests**: Suggest new testing capabilities and improvements

### Getting Started
- **Setup Guide**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development environment setup
- **Architecture Guide**: Understand the MCP server and tool registry architecture
- **Good First Issues**: Look for issues labeled "good first issue" and "help wanted"
- **Community**: Join discussions about software testing automation and AI integration

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Boundary ML**: Inspiration for error-tolerant JSON parsing techniques
- **Google Gemini**: AI model for intelligent test generation
- **MCP Protocol**: Framework for AI assistant integrations
- **Contributors**: Thank you to all who help improve this tool!
