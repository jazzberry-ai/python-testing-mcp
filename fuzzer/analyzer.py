"""
Python code analyzer for extracting functions to fuzz.
"""

import ast
import inspect
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """Information about a function to be fuzzed."""
    name: str
    signature: str
    code: str
    docstring: str
    line_number: int
    args: List[str]
    defaults: List[Any]
    is_method: bool


class CodeAnalyzer:
    """Analyzes Python code to extract functions for fuzzing."""
    
    def __init__(self, file_path: str):
        """Initialize analyzer with a Python file."""
        self.file_path = file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            self.source_code = f.read()
        self.tree = ast.parse(self.source_code)
    
    def extract_functions(self) -> List[FunctionInfo]:
        """Extract all functions from the Python file."""
        functions = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._analyze_function(node)
                if func_info:
                    functions.append(func_info)
        
        return functions
    
    def _analyze_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Analyze a single function node."""
        # Extract function signature
        args = []
        defaults = []
        
        for arg in node.args.args:
            args.append(arg.arg)
        
        # Handle default values
        if node.args.defaults:
            defaults = [ast.unparse(default) for default in node.args.defaults]
        
        # Build signature string
        signature_parts = []
        num_defaults = len(defaults)
        
        for i, arg in enumerate(args):
            if i >= len(args) - num_defaults:
                default_index = i - (len(args) - num_defaults)
                signature_parts.append(f"{arg}={defaults[default_index]}")
            else:
                signature_parts.append(arg)
        
        signature = f"{node.name}({', '.join(signature_parts)})"
        
        # Extract function code
        function_code = ast.unparse(node)
        
        # Extract docstring
        docstring = ""
        if (node.body and isinstance(node.body[0], ast.Expr) 
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        # Check if it's a method (inside a class)
        is_method = self._is_method(node)
        
        return FunctionInfo(
            name=node.name,
            signature=signature,
            code=function_code,
            docstring=docstring,
            line_number=node.lineno,
            args=args,
            defaults=defaults,
            is_method=is_method
        )
    
    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is a method inside a class."""
        # Walk up the AST to see if this function is inside a class
        for parent in ast.walk(self.tree):
            if isinstance(parent, ast.ClassDef):
                for child in ast.walk(parent):
                    if child is node:
                        return True
        return False
    
    def get_imports(self) -> List[str]:
        """Extract all import statements from the file."""
        imports = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        
        return imports
    
    def get_classes(self) -> List[str]:
        """Extract all class definitions."""
        classes = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return classes
