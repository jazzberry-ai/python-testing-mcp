# Python Testing Tools MCP Server

An advanced Model Context Protocol (MCP) server that provides AI-powered Python testing tools. This project leverages both Google's Gemini AI and BAML (Boundary ML) to intelligently generate comprehensive unit tests and perform sophisticated fuzz testing on Python code.

## Overview

This MCP server offers automated testing capabilities through two main tools:
1. **Intelligent Unit Test Generation** - Automatically creates comprehensive test suites with proper edge cases, assertions, and error handling
2. **AI-Powered Fuzz Testing** - Generates diverse, challenging inputs to test function robustness and discover potential crashes

The server uses a hybrid AI approach: BAML for structured test generation and Gemini for intelligent input generation, ensuring high-quality, reliable test outputs.

## Key Features

- **AI-Powered Unit Test Generation**: Uses BAML with Gemini to generate comprehensive unittest suites covering normal cases, edge cases, and error conditions
- **Intelligent Fuzz Testing**: Leverages AI to generate diverse, challenging inputs that test function boundaries and error handling
- **BAML Integration**: Structured AI responses using BAML (Boundary ML) for consistent, parseable test generation
- **FastMCP Framework**: Built on FastMCP for efficient MCP server implementation
- **Robust Error Handling**: Graceful fallbacks and detailed error reporting throughout the testing pipeline
- **Modular Architecture**: Clean separation between tools, utilities, and AI clients for easy extension
- **Code Analysis**: Uses Python AST parsing for accurate function extraction and analysis

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
│   └── fuzz_tester.py            # Intelligent fuzz testing engine
├── utils/                         # Shared utilities and helpers
│   ├── __init__.py               # Module exports
│   ├── ai_clients.py             # Gemini AI client configuration
│   └── file_handlers.py          # File I/O and AST parsing utilities
├── demo/                          # Example files for testing
│   └── basic_example_functions.py # Simple functions for demonstration
├── requirements.txt               # Python dependencies
├── LICENSE                        # Apache 2.0 license
└── README.md                      # This documentation
```

## Configuration

The server uses environment variables for configuration:

- `GEMINI_API_KEY`: **Required** - Your Google Gemini API key for AI-powered test generation
- `GEMINI_MODEL`: Optional - Gemini model to use (default: `gemini-2.5-flash`)

The BAML configuration in `baml_src/main.baml` defines:
- AI function signatures for test generation and fuzz input creation
- Structured response formats using BAML classes
- Detailed prompts for comprehensive test coverage

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

3. Set your Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Running the Server

To run the MCP server:

```bash
python mcp_server.py
```

## Running the Server in Claude Code

The documentation for FastMCP and Claude Code can be found here: https://gofastmcp.com/integrations/claude-code

### Step 1: Install the MCP Server

Install the server using FastMCP:
```bash
fastmcp install claude-code python_testing_mcp_server.py --env GEMINI_API_KEY='your-api-key-here'
```

### Step 2: Configure Claude Code

Your `.claude.json` configuration should look like this:

```json
{
  "/path/to/your/project": {
    "allowedTools": [],
    "history": [],
    "mcpContextUris": [],
    "mcpServers": {
      "python_testing_tools": {
        "type": "stdio",
        "command": "uv",
        "args": [
          "run",
          "--with",
          "fastmcp",
          "fastmcp",
          "run",
          "/path/to/your/project/python_testing_mcp_server.py"
        ],
        "env": {
          "GEMINI_API_KEY": "your-api-key-here"
        }
      }
    },
    "enabledMcpjsonServers": [],
    "disabledMcpjsonServers": [],
    "hasTrustDialogAccepted": false,
    "projectOnboardingSeenCount": 0,
    "hasClaudeMdExternalIncludesApproved": false,
    "hasClaudeMdExternalIncludesWarningShown": false
  }
}
```

**Note**: Replace `/path/to/your/project` with the actual path to your project directory, and `your-api-key-here` with your actual Gemini API key.

### Step 3: Start Claude Code

Start Claude Code:
```bash
claude
```

### Step 4: Verify Connection

Check if the MCP server is connected:
```bash
/mcp
```

### Step 5: Test the Tools

Test the unit test generation tool:
```bash
create unit tests for @demo/basic_example_functions.py
```

This should create a file called `test_basic_example_functions.py` in the demo folder.

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

## Adding New Tools

The modular architecture makes it easy to extend the server with new testing tools:

1. **Create Tool Implementation**: Add a new Python file in the `tools/` directory
2. **Use Shared Utilities**: Import common functionality from `utils` module
3. **Integrate BAML (Optional)**: Add new AI functions to `baml_src/main.baml` for AI-powered tools
4. **Register Tool**: Import and register the tool in `python_testing_mcp_server.py`

Example:
```python
# tools/code_coverage.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import read_python_file, parse_python_ast

def analyze_code_coverage(file_path: str) -> str:
    # Your implementation here
    source_code = read_python_file(file_path)
    # ... analysis logic
    return "Coverage analysis results"

# Add to python_testing_mcp_server.py
from code_coverage import analyze_code_coverage

@mcp.tool
def analyze_code_coverage_tool(file_path: str) -> str:
    """Analyze code coverage for the given Python file."""
    return analyze_code_coverage(file_path)
```

## Development

### Dependencies
All dependencies are managed in `requirements.txt` including:
- `fastmcp` - MCP server framework
- `baml` & `baml-cli` - BAML AI integration
- `google-generativeai` - Gemini AI client
- `pytest`, `black`, `isort`, `mypy` - Development tools

### Code Quality
Format code:
```bash
black tools/ utils/ *.py
isort tools/ utils/ *.py
```

Type checking:
```bash
mypy tools/ utils/ *.py
```

### BAML Development
To modify AI prompts or add new AI functions:
1. Edit `baml_src/main.baml`
2. Run `baml generate` to update the client code
3. Test changes with the demo functions

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
