# MCP Server Setup Guide

This guide explains how to connect the Python Fuzzing Tool as an MCP server to various tools like Cursor, Claude Desktop, and other MCP-compatible clients.

## Prerequisites

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up Gemini API key**:
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
```

## Available MCP Tools

The server exposes three tools:

### 1. `fuzz_python_file`
Fuzz test all functions in a Python file using AI-generated test cases.

### 2. `analyze_python_code`  
Analyze a Python file to extract function information and structure.

### 3. `generate_test_inputs`
Generate AI-powered test inputs for a specific function.

## Connection Setup

### For AMP Code

1. **Create the configuration file** or add to existing configuration:
   - **Linux/macOS**: `~/.config/amp/settings.json`
   - **Windows**: `%APPDATA%\amp\settings.json`

2. **Add this configuration**:
```json
{
  "amp.mcpServers": {
    "python-fuzzing-tool": {
      "command": "python",
      "args": ["/path/to/your/software-testing-agent/mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

3. **Alternative**: Use the provided `amp_mcp_config.json` file as a reference

### For Claude Desktop

1. **Locate config**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

2. **Add this configuration**:
```json
{
  "mcpServers": {
    "python-fuzzing-tool": {
      "command": "python",
      "args": ["/path/to/your/software-testing-agent/mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "your_api_key"
      }
    }
  }
}
```

### For Cursor+

1. **Settings > Extensions > MCP Servers**
2. **Add the same configuration**
3. **Restart Cursor**

## Testing

```bash
python mcp_server.py  # Test server
```

Then ask in your MCP client: "Analyze the code in example.py"
