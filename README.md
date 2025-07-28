# Software Testing MCP

A comprehensive testing toolkit that provides multiple AI-powered testing tools for software quality assurance. Currently includes an intelligent Python fuzzing tool with plans for additional testing capabilities.

## Available Tools

### Python Fuzzer
An intelligent fuzzing tool that uses Google's Gemini AI to automatically generate comprehensive test inputs for Python functions. This tool analyzes Python code, extracts functions, and uses AI to create diverse test cases including edge cases, boundary conditions, and error conditions.

### Python Fuzzer Features

- **🤖 AI-Powered Test Generation**: Uses Google Gemini to create intelligent, diverse test inputs
- **🔍 Automatic Function Discovery**: Analyzes Python files to find testable functions automatically
- **💥 Crash Analysis**: Provides AI-powered analysis of crashes and failures with suggested fixes
- **📊 Comprehensive Reporting**: Generates detailed reports showing success rates and crash analysis
- **🖥️ Command-Line Interface**: Easy-to-use CLI for fuzzing any Python file
- **🛡️ Error-Tolerant Parsing**: Uses BAML-inspired techniques to handle malformed AI responses

## Architecture

The project is designed with a modular architecture to support multiple testing tools:

- **🔧 MCP Server Support**: Integrates with MCP-compatible clients like Claude, Cursor, and more
- **🏗️ Modular Tool System**: Each testing tool is self-contained and discoverable
- **📋 Tool Registry**: Dynamic discovery and registration of available testing tools
- **🔌 Extensible Design**: Easy to add new testing tools without modifying existing code

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

This tool can also run as an MCP (Model Context Protocol) server, integrating with AI assistants like Claude, Cursor, and other MCP-compatible clients.

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

- `fuzz_python_file`: Fuzz test all functions in a Python file
- `analyze_python_code`: Analyze Python code structure and extract function information  
- `generate_test_inputs`: Generate AI-powered test inputs for specific functions

#### MCP Usage Example

Once configured, you can use commands like:
```
Please fuzz test the file main.py with 10 test cases per function
```

The MCP server will automatically handle the fuzzing and return comprehensive results.

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

### Adding New Tools

To add a new testing tool:
1. Create a new directory under `tools/` (e.g., `tools/my_tool/`)
2. Implement the tool following the `BaseTool` interface
3. Create a `tool.py` file with a `get_tool()` function
4. The tool will be automatically discovered and registered

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

## Limitations

- **API Dependency**: Requires a Google Gemini API key for AI-powered features
- **Function Scope**: Tests individual functions, not complex workflows or integrations
- **Language Features**: May not handle all Python features (decorators, async functions, metaclasses)
- **AI Quality**: Test quality depends on AI model capabilities and prompt effectiveness
- **Rate Limits**: Subject to Gemini API rate limits and quotas

## Contributing

We welcome contributions! This project is designed to be easy to understand and extend.

- **Getting Started**: See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines
- **Good First Issues**: Look for issues labeled "good first issue"
- **Code of Conduct**: Be respectful and constructive in all interactions
- **Development Setup**: Follow the contributing guide for environment setup

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Boundary ML**: Inspiration for error-tolerant JSON parsing techniques
- **Google Gemini**: AI model for intelligent test generation
- **MCP Protocol**: Framework for AI assistant integrations
- **Contributors**: Thank you to all who help improve this tool!
