"""
Core Mutation Engine

Safely generates mutants of Python code using AST manipulation.
CRITICAL: Original source files are NEVER modified - all mutations are applied
to temporary files that are automatically cleaned up.
"""

import ast
import copy
import os
import tempfile
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
import contextlib

from .operators import MUTATION_OPERATORS, BaseMutationOperator, get_applicable_operators


@dataclass
class Mutant:
    """Represents a single mutant of the original code."""
    id: str
    operator_name: str
    original_code: str
    mutated_code: str
    line_number: int
    column_number: int
    function_name: str
    description: str
    temp_file_path: Optional[str] = None


@dataclass
class MutationPoint:
    """Represents a location in the code where a mutation can be applied."""
    node: ast.AST
    function_name: str
    line_number: int
    column_number: int
    applicable_operators: List[BaseMutationOperator] = field(default_factory=list)


class SafeMutationEngine:
    """
    Safe mutation engine that generates mutants without modifying original files.
    
    This engine:
    1. Parses original code into AST
    2. Identifies mutation points
    3. Applies mutations to AST copies
    4. Generates temporary files with mutated code
    5. Ensures complete cleanup of temporary files
    """
    
    def __init__(self):
        self.temp_files: Set[str] = set()
        self.temp_dir: Optional[str] = None
    
    def __enter__(self):
        """Context manager entry - create temporary directory."""
        self.temp_dir = tempfile.mkdtemp(prefix="mutation_test_")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup all temporary files."""
        self.cleanup()
    
    def cleanup(self):
        """Remove all temporary files and directories created by this engine."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Warning: Could not remove temporary file {temp_file}: {e}")
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except Exception as e:
                print(f"Warning: Could not remove temporary directory {self.temp_dir}: {e}")
        
        self.temp_files.clear()
        self.temp_dir = None
    
    def analyze_file(self, file_path: str) -> Tuple[ast.AST, str]:
        """
        Safely analyze a Python file and return its AST and source code.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            Tuple of (AST tree, source code)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has invalid Python syntax
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax in {file_path}: {e}")
        
        return tree, source_code
    
    def find_mutation_points(self, tree: ast.AST, target_functions: Optional[List[str]] = None) -> List[MutationPoint]:
        """
        Identify all potential mutation points in the AST.
        
        Args:
            tree: AST tree to analyze
            target_functions: Optional list of function names to limit mutations to
            
        Returns:
            List of mutation points
        """
        mutation_points = []
        
        # Walk through all nodes in the AST
        for node in ast.walk(tree):
            # Skip nodes without position information
            if not hasattr(node, 'lineno'):
                continue
            
            # Find the function containing this node
            function_name = self._find_containing_function(tree, node)
            
            # Skip if we're limiting to specific functions and this isn't one of them
            if target_functions and function_name not in target_functions:
                continue
            
            # Get applicable mutation operators for this node
            applicable_operators = get_applicable_operators(node)
            
            if applicable_operators:
                mutation_point = MutationPoint(
                    node=node,
                    function_name=function_name or "module_level",
                    line_number=node.lineno,
                    column_number=getattr(node, 'col_offset', 0),
                    applicable_operators=applicable_operators
                )
                mutation_points.append(mutation_point)
        
        return mutation_points
    
    def generate_mutants(
        self, 
        file_path: str, 
        target_functions: Optional[List[str]] = None,
        operator_names: Optional[List[str]] = None,
        max_mutants: int = 100
    ) -> List[Mutant]:
        """
        Generate mutants for a Python file.
        
        Args:
            file_path: Path to the original Python file
            target_functions: Optional list of functions to mutate
            operator_names: Optional list of operator names to use
            max_mutants: Maximum number of mutants to generate
            
        Returns:
            List of generated mutants
        """
        # Parse the original file
        tree, source_code = self.analyze_file(file_path)
        
        # Find mutation points
        mutation_points = self.find_mutation_points(tree, target_functions)
        
        # Filter operators if specified
        if operator_names:
            filtered_points = []
            for point in mutation_points:
                filtered_operators = [
                    op for op in point.applicable_operators 
                    if op.name in operator_names
                ]
                if filtered_operators:
                    point.applicable_operators = filtered_operators
                    filtered_points.append(point)
            mutation_points = filtered_points
        
        # Generate mutants
        mutants = []
        mutant_count = 0
        
        for mutation_point in mutation_points:
            if mutant_count >= max_mutants:
                break
                
            for operator in mutation_point.applicable_operators:
                if mutant_count >= max_mutants:
                    break
                
                # Apply mutation to get mutated AST nodes
                mutated_nodes = operator.mutate(mutation_point.node)
                
                for mutated_node in mutated_nodes:
                    if mutant_count >= max_mutants:
                        break
                    
                    # Create mutant
                    mutant = self._create_mutant(
                        tree=tree,
                        original_node=mutation_point.node,
                        mutated_node=mutated_node,
                        operator=operator,
                        mutation_point=mutation_point
                    )
                    
                    if mutant:
                        mutants.append(mutant)
                        mutant_count += 1
        
        return mutants
    
    def _create_mutant(
        self,
        tree: ast.AST,
        original_node: ast.AST,
        mutated_node: ast.AST,
        operator: BaseMutationOperator,
        mutation_point: MutationPoint
    ) -> Optional[Mutant]:
        """Create a mutant by replacing a node in the AST and generating temporary file."""
        try:
            # Create a deep copy of the entire AST
            mutated_tree = copy.deepcopy(tree)
            
            # Find the corresponding node in the copied tree and replace it
            if self._replace_node_in_tree(mutated_tree, original_node, mutated_node):
                # Generate code from the mutated AST
                try:
                    mutated_code = ast.unparse(mutated_tree)
                    original_code = ast.unparse(original_node)
                except Exception:
                    # Fallback if unparsing fails
                    return None
                
                # Create temporary file with mutated code
                temp_file_path = self._create_temp_file(mutated_code)
                
                # Create mutant object
                mutant_id = str(uuid.uuid4())[:8]
                mutant = Mutant(
                    id=mutant_id,
                    operator_name=operator.name,
                    original_code=original_code,
                    mutated_code=ast.unparse(mutated_node),
                    line_number=mutation_point.line_number,
                    column_number=mutation_point.column_number,
                    function_name=mutation_point.function_name,
                    description=f"{operator.description} at line {mutation_point.line_number}",
                    temp_file_path=temp_file_path
                )
                
                return mutant
            
        except Exception as e:
            print(f"Error creating mutant with {operator.name}: {e}")
            return None
        
        return None
    
    def _replace_node_in_tree(self, tree: ast.AST, target_node: ast.AST, replacement_node: ast.AST) -> bool:
        """Replace a specific node in the AST tree with a new node."""
        # Since we're working with a copied tree, we need to find the corresponding node
        # by matching attributes rather than identity
        target_line = getattr(target_node, 'lineno', None)
        target_col = getattr(target_node, 'col_offset', None)
        target_type = type(target_node)
        
        for parent in ast.walk(tree):
            for field_name, field_value in ast.iter_fields(parent):
                if self._nodes_match(field_value, target_node):
                    setattr(parent, field_name, replacement_node)
                    # Copy position information
                    if hasattr(target_node, 'lineno'):
                        replacement_node.lineno = target_node.lineno
                    if hasattr(target_node, 'col_offset'):
                        replacement_node.col_offset = target_node.col_offset
                    return True
                elif isinstance(field_value, list):
                    for i, item in enumerate(field_value):
                        if self._nodes_match(item, target_node):
                            field_value[i] = replacement_node
                            # Copy position information
                            if hasattr(target_node, 'lineno'):
                                replacement_node.lineno = target_node.lineno
                            if hasattr(target_node, 'col_offset'):
                                replacement_node.col_offset = target_node.col_offset
                            return True
        
        return False
    
    def _nodes_match(self, node1: ast.AST, node2: ast.AST) -> bool:
        """Check if two AST nodes match based on type and location."""
        if type(node1) != type(node2):
            return False
        
        # Compare line numbers if available
        line1 = getattr(node1, 'lineno', None)
        line2 = getattr(node2, 'lineno', None)
        if line1 is not None and line2 is not None and line1 != line2:
            return False
        
        # Compare column offsets if available
        col1 = getattr(node1, 'col_offset', None)
        col2 = getattr(node2, 'col_offset', None)
        if col1 is not None and col2 is not None and col1 != col2:
            return False
        
        # For constants, also compare values
        if isinstance(node1, ast.Constant) and isinstance(node2, ast.Constant):
            return node1.value == node2.value
        
        # For binary operations, compare operator types
        if isinstance(node1, ast.BinOp) and isinstance(node2, ast.BinOp):
            return type(node1.op) == type(node2.op)
        
        # For comparisons, compare operator types
        if isinstance(node1, ast.Compare) and isinstance(node2, ast.Compare):
            return (len(node1.ops) == len(node2.ops) and 
                    all(type(op1) == type(op2) for op1, op2 in zip(node1.ops, node2.ops)))
        
        return True
    
    def _create_temp_file(self, code: str) -> str:
        """Create a temporary file with the given code."""
        if not self.temp_dir:
            raise RuntimeError("Mutation engine must be used as context manager")
        
        # Create unique temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            dir=self.temp_dir,
            delete=False,
            encoding='utf-8'
        )
        
        with temp_file:
            temp_file.write(code)
        
        self.temp_files.add(temp_file.name)
        return temp_file.name
    
    def _find_containing_function(self, tree: ast.AST, target_node: ast.AST) -> Optional[str]:
        """Find the name of the function containing the target node."""
        # Walk through all function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if target_node is within this function
                for child in ast.walk(node):
                    if child is target_node:
                        return node.name
        
        return None
    
    def get_mutant_code(self, mutant: Mutant) -> str:
        """Get the full mutated code for a mutant."""
        if mutant.temp_file_path and os.path.exists(mutant.temp_file_path):
            with open(mutant.temp_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def save_mutant_to_file(self, mutant: Mutant, output_path: str) -> None:
        """Save a mutant's code to a specific file (for debugging purposes)."""
        mutated_code = self.get_mutant_code(mutant)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mutated_code)


@contextlib.contextmanager
def safe_mutation_engine():
    """Context manager for safe mutation engine usage."""
    engine = SafeMutationEngine()
    try:
        yield engine.__enter__()
    finally:
        engine.__exit__(None, None, None)