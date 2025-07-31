import ast
import os

def read_python_file(file_path: str) -> str:
    """
    Read and return the contents of a Python file.
    
    Args:
        file_path (str): Path to the Python file
        
    Returns:
        str: Contents of the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If the file cannot be decoded as UTF-8
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_python_ast(source_code: str) -> ast.AST:
    """
    Parse Python source code and return its AST.
    
    Args:
        source_code (str): Python source code to parse
        
    Returns:
        ast.AST: Abstract syntax tree of the code
        
    Raises:
        SyntaxError: If the source code has syntax errors
    """
    try:
        return ast.parse(source_code)
    except SyntaxError as e:
        raise SyntaxError(f"Invalid Python syntax: {e}")