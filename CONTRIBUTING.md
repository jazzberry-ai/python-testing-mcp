# Contributing to Python AI Fuzzing Tool

Thank you for your interest in contributing to the Python AI Fuzzing Tool! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Git

### Setting Up Development Environment

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/software-testing-agent.git
   cd software-testing-agent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**:
   ```bash
   export GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Run tests to verify setup**:
   ```bash
   python -m pytest test_example.py -v
   python local_fuzz_test.py
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues in existing code
- **Feature additions**: Add new functionality
- **Documentation improvements**: Enhance README, comments, or guides
- **Test improvements**: Add or improve test cases
- **Performance optimizations**: Make the tool faster or more efficient
- **Error handling**: Improve robustness and error messages

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   # Run local tests
   python local_fuzz_test.py
   
   # Test with API (if you have a key)
   python main.py example.py --num-tests 3
   
   # Test MCP server
   python mcp_server.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your descriptive commit message"
   ```

5. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and reasonably sized

### Code Structure

- **Error handling**: Use try-catch blocks appropriately
- **Type hints**: Add type hints where helpful
- **Comments**: Explain complex logic, not obvious code
- **Logging**: Use print statements for user feedback, not debugging

### Example Code Style

```python
def generate_test_inputs(self, function_signature: str, function_code: str, num_inputs: int = 10) -> List[Dict[str, Any]]:
    """Generate fuzzing inputs for a Python function.
    
    Args:
        function_signature: The function signature to analyze
        function_code: The complete function code
        num_inputs: Number of test inputs to generate
        
    Returns:
        List of dictionaries containing test inputs and expected behavior
        
    Raises:
        ValueError: If function_code is empty or invalid
    """
    if not function_code.strip():
        raise ValueError("Function code cannot be empty")
        
    try:
        # Implementation here
        return results
    except Exception as e:
        print(f"Error generating test inputs: {e}")
        return []
```

## Testing Guidelines

### Test Coverage

- Add tests for new functions
- Test both success and failure cases
- Include edge cases and boundary conditions
- Test with and without API access

### Test Structure

```python
def test_new_feature():
    """Test description of what this test verifies."""
    # Arrange
    input_data = "test input"
    expected_result = "expected output"
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected_result
```

## Documentation

### README Updates

- Update feature lists when adding functionality
- Add usage examples for new features
- Update installation instructions if needed

### Code Documentation

- Add docstrings to all public functions
- Document complex algorithms or logic
- Include examples in docstrings when helpful

### Configuration Examples

When adding new MCP integrations or configurations:
- Provide complete, working examples
- Use placeholder paths like `/path/to/your/project/`
- Test configurations work on different platforms

## Submitting Changes

### Pull Request Guidelines

1. **Clear title**: Describe what the PR does
2. **Description**: Explain why the change is needed
3. **Testing**: Describe how you tested the changes
4. **Breaking changes**: Clearly mark any breaking changes

### Pull Request Template

```markdown
## Description
Brief description of what this PR accomplishes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Tested with local fuzzing script
- [ ] Tested with API integration
- [ ] Tested MCP server functionality
- [ ] Added/updated tests

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

## Issue Reporting

### Bug Reports

Include the following information:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)
- Minimal code example

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Additional context

## Project Structure

Understanding the codebase:

```
software-testing-agent/
├── fuzzer/
│   ├── analyzer.py      # Code analysis and AST parsing
│   ├── gemini_client.py # Gemini API integration
│   └── fuzzer.py        # Core fuzzing logic
├── main.py              # CLI interface
├── mcp_server.py        # MCP server implementation
├── example.py           # Example code for testing
├── local_fuzz_test.py   # Local testing without API
├── requirements.txt     # Dependencies
└── README.md            # Main documentation
```

## Community

- Be respectful and constructive in discussions
- Help others when you can
- Follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/)

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing issues for similar questions
- Review the documentation thoroughly first

Thank you for contributing to make this tool better for everyone!