# Software Testing Tools MCP Server

This project provides a modular MCP server for various software testing tools. The server is designed to be easily extensible with a clean, professional structure that scales well as new tools are added.

## Features

- **Unit Test Generation**: Automatically generate unit tests for Python functions using AI
- **Fuzz Testing**: Intelligent fuzz testing with AI-generated test cases
- **Modular Architecture**: Clean separation of concerns with categorized tools
- **Shared Utilities**: Common functionality for AI clients and file handling
- **Configuration Management**: Environment-based configuration system

## Directory Structure

```
mcp_test/
├── mcp_server.py                  # Main MCP server entry point
├── tools/                         # Testing tool modules
│   ├── unit_test_generator.py     # Unit test generation
│   └── fuzz_tester.py            # Fuzz testing functionality
├── utils/                         # Shared utilities
│   ├── __init__.py               # Module exports
│   ├── ai_clients.py             # Gemini API client setup
│   └── file_handlers.py          # File I/O operations
├── example_functions.py           # Example functions for testing
└── README.md                      # This file
```

## Configuration

The server uses environment variables for configuration:

- `GEMINI_API_KEY`: Required - Your Google Gemini API key
- `GEMINI_MODEL`: Optional - Gemini model to use (default: gemini-1.5-flash)
- `MAX_FUZZ_INPUTS`: Optional - Number of fuzz test inputs to generate (default: 20)
- `MCP_SERVER_NAME`: Optional - Server name (default: software_testing_tools)

## Installation

1. Install dependencies:
```bash
pip install fastmcp google-generativeai
```

2. Set your Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Running the Server

To run the MCP server:

```bash
python mcp_server.py
```

## Available Tools

### Unit Test Generator
- **Function**: `generate_unit_tests_tool`
- **Description**: Generates comprehensive unit tests for Python functions
- **Parameters**: `file_path` (str) - Path to the Python file

### Fuzz Tester
- **Function**: `fuzz_test_function_tool`
- **Description**: Performs intelligent fuzz testing on specific functions
- **Parameters**: 
  - `file_path` (str) - Path to the Python file
  - `function_name` (str) - Name of the function to test

## Adding New Tools

To add a new tool:

1. Create a new Python file in the `tools/` directory
2. Implement your tool function with proper imports from `utils`
3. Import and register the tool in `mcp_server.py`

Example:
```python
# tools/code_quality.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import get_gemini_client, read_python_file

def analyze_code_quality(file_path: str) -> str:
    # Your implementation here
    pass

# Add to mcp_server.py
from code_quality import analyze_code_quality

@mcp.tool
def analyze_code_quality_tool(file_path: str) -> str:
    return analyze_code_quality(file_path)
```

## Development

For development, install additional dependencies:
```bash
pip install pytest black isort mypy
```

Format code:
```bash
black tools/ utils/ *.py
isort tools/ utils/ *.py
```

Type checking:
```bash
mypy tools/ utils/ *.py
```
