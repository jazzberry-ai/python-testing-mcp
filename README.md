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

#### Available MCP Tools

**Python Fuzzing Tools:**
- `fuzz_python_file`: Comprehensive fuzzing of all functions in a Python file
- `analyze_python_code`: Code structure analysis and function extraction
- `generate_test_inputs`: AI-powered test case generation for specific functions

**Python Coverage Tools:**
- `run_python_coverage`: Execute coverage analysis with configurable test commands
- `analyze_coverage_report`: Parse and analyze existing coverage JSON reports
- `suggest_coverage_improvements`: Generate targeted recommendations for improving coverage

#### MCP Usage Examples

Once configured with an AI client, you can use natural language commands like:

**Fuzzing:**
```
Please fuzz test the file main.py with 10 test cases per function
```

**Coverage Analysis:**
```
Run coverage analysis on my src/ directory and suggest improvements
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

## Testing

Run the included tests:
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

## Current Limitations & Roadmap

### Current Limitations
- **Language Support**: Currently focused on Python (JavaScript, Go, Rust support planned)
- **AI Dependency**: Some features require API keys for cloud-based AI models
- **Integration Scope**: Individual function testing (end-to-end testing tools planned)
- **Advanced Features**: Some Python language features may need additional support

### Planned Enhancements
- **📝 Multi-Language Support**: JavaScript, TypeScript, Go, Rust testing tools
- **🔄 Integration Testing**: End-to-end and integration testing capabilities
- **🎯 Performance Testing**: Load testing and performance analysis tools
- **🔐 Security Testing**: Static analysis and vulnerability scanning tools
- **📊 Test Management**: Test suite organization and execution management
- **🤖 Local AI Models**: Support for local/offline AI model execution

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
