import ast
import sys
import os
import tempfile
import subprocess
import shutil
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import importlib.util


class MutationOperator:
    """Base class for mutation operators."""
    
    def can_mutate(self, node: ast.AST) -> bool:
        """Check if this operator can mutate the given AST node."""
        raise NotImplementedError
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        """Generate mutated versions of the node."""
        raise NotImplementedError
    
    def describe_mutation(self, original: ast.AST, mutated: ast.AST) -> Tuple[str, str]:
        """Return (original_description, mutated_description) for the mutation."""
        raise NotImplementedError


class BinaryOperatorMutator(MutationOperator):
    """Mutates binary operators like +, -, *, /, ==, !=, <, >, etc."""
    
    MUTATIONS = {
        ast.Add: [ast.Sub, ast.Mult],
        ast.Sub: [ast.Add, ast.Div],
        ast.Mult: [ast.Add, ast.Div],
        ast.Div: [ast.Mult, ast.Sub],
        ast.Eq: [ast.NotEq, ast.Lt, ast.Gt],
        ast.NotEq: [ast.Eq],
        ast.Lt: [ast.LtE, ast.Gt, ast.Eq],
        ast.LtE: [ast.Lt, ast.Gt],
        ast.Gt: [ast.GtE, ast.Lt, ast.Eq],
        ast.GtE: [ast.Gt, ast.Lt],
        ast.And: [ast.Or],
        ast.Or: [ast.And],
    }
    
    def can_mutate(self, node: ast.AST) -> bool:
        return isinstance(node, (ast.BinOp, ast.Compare, ast.BoolOp)) and \
               type(node.op if hasattr(node, 'op') else 
                   node.ops[0] if hasattr(node, 'ops') and node.ops else None) in self.MUTATIONS
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        mutations: List[ast.AST] = []
        
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in self.MUTATIONS:
                for new_op_type in self.MUTATIONS[op_type]:
                    mutated = ast.copy_location(
                        ast.BinOp(left=node.left, op=new_op_type(), right=node.right),
                        node
                    )
                    mutations.append(mutated)
                    
        elif isinstance(node, ast.Compare) and node.ops:
            op_type = type(node.ops[0])
            if op_type in self.MUTATIONS:
                for new_op_type in self.MUTATIONS[op_type]:
                    mutated = ast.copy_location(
                        ast.Compare(left=node.left, ops=[new_op_type()], comparators=node.comparators),
                        node
                    )
                    mutations.append(mutated)
                    
        elif isinstance(node, ast.BoolOp):
            op_type = type(node.op)
            if op_type in self.MUTATIONS:
                for new_op_type in self.MUTATIONS[op_type]:
                    mutated = ast.copy_location(
                        ast.BoolOp(op=new_op_type(), values=node.values),
                        node
                    )
                    mutations.append(mutated)
        
        return mutations
    
    def describe_mutation(self, original: ast.AST, mutated: ast.AST) -> Tuple[str, str]:
        def get_op_symbol(op):
            op_symbols = {
                ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/',
                ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=',
                ast.Gt: '>', ast.GtE: '>=', ast.And: 'and', ast.Or: 'or'
            }
            return op_symbols.get(type(op), str(type(op).__name__))
        
        if isinstance(original, ast.BinOp):
            orig_op = get_op_symbol(original.op)
            mut_op = get_op_symbol(mutated.op)
            return f"binary operator '{orig_op}'", f"binary operator '{mut_op}'"
        elif isinstance(original, ast.Compare):
            orig_op = get_op_symbol(original.ops[0])
            mut_op = get_op_symbol(mutated.ops[0])
            return f"comparison '{orig_op}'", f"comparison '{mut_op}'"
        elif isinstance(original, ast.BoolOp):
            orig_op = get_op_symbol(original.op)
            mut_op = get_op_symbol(mutated.op)
            return f"boolean operator '{orig_op}'", f"boolean operator '{mut_op}'"
        
        return "unknown operator", "unknown operator"


class ConstantMutator(MutationOperator):
    """Mutates constants like numbers, booleans, and strings."""
    
    def can_mutate(self, node: ast.AST) -> bool:
        return isinstance(node, (ast.Constant, ast.Num, ast.Str, ast.NameConstant))
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        mutations: List[ast.AST] = []
        
        # Get the value based on node type (compatibility with different Python versions)
        if isinstance(node, ast.Constant):
            value = node.value
        elif isinstance(node, ast.Num):
            value = node.n
        elif isinstance(node, ast.Str):
            value = node.s
        elif isinstance(node, ast.NameConstant):
            value = node.value
        else:
            return mutations
        
        # Generate mutations based on value type
        if isinstance(value, bool):
            mutated = ast.copy_location(ast.Constant(value=not value), node)
            mutations.append(mutated)
        elif isinstance(value, int):
            for new_val in [value + 1, value - 1, 0, 1, -1]:
                if new_val != value:
                    mutated = ast.copy_location(ast.Constant(value=new_val), node)
                    mutations.append(mutated)
        elif isinstance(value, float):
            for new_val in [value + 1.0, value - 1.0, 0.0, 1.0]:
                if new_val != value:
                    mutated = ast.copy_location(ast.Constant(value=new_val), node)
                    mutations.append(mutated)
        elif isinstance(value, str) and value:
            # String mutations
            mutated = ast.copy_location(ast.Constant(value=""), node)
            mutations.append(mutated)
            if len(value) > 1:
                mutated = ast.copy_location(ast.Constant(value=value[:-1]), node)
                mutations.append(mutated)
        
        return mutations
    
    def describe_mutation(self, original: ast.AST, mutated: ast.AST) -> Tuple[str, str]:
        def get_value(node):
            if isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Num):
                return str(node.n)
            elif isinstance(node, ast.Str):
                return repr(node.s)
            elif isinstance(node, ast.NameConstant):
                return str(node.value)
            return "unknown"
        
        orig_val = get_value(original)
        mut_val = get_value(mutated)
        return f"constant {orig_val}", f"constant {mut_val}"


class ConditionalMutator(MutationOperator):
    """Mutates conditional expressions and statements."""
    
    def can_mutate(self, node: ast.AST) -> bool:
        return isinstance(node, (ast.If, ast.While, ast.IfExp))
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        mutations: List[ast.AST] = []
        
        if isinstance(node, ast.If):
            # Negate the condition
            negated_test = ast.UnaryOp(op=ast.Not(), operand=node.test)
            mutated = ast.copy_location(
                ast.If(test=negated_test, body=node.body, orelse=node.orelse),
                node
            )
            mutations.append(mutated)
            
            # Always true condition
            true_mutated = ast.copy_location(
                ast.If(test=ast.Constant(value=True), body=node.body, orelse=node.orelse),
                node
            )
            mutations.append(true_mutated)
            
            # Always false condition
            false_mutated = ast.copy_location(
                ast.If(test=ast.Constant(value=False), body=node.body, orelse=node.orelse),
                node
            )
            mutations.append(false_mutated)
            
        elif isinstance(node, ast.While):
            # Negate the condition
            negated_test = ast.UnaryOp(op=ast.Not(), operand=node.test)
            mutated = ast.copy_location(
                ast.While(test=negated_test, body=node.body, orelse=node.orelse),
                node
            )
            mutations.append(mutated)
            
        elif isinstance(node, ast.IfExp):
            # Negate the condition
            negated_test = ast.UnaryOp(op=ast.Not(), operand=node.test)
            mutated = ast.copy_location(
                ast.IfExp(test=negated_test, body=node.body, orelse=node.orelse),
                node
            )
            mutations.append(mutated)
        
        return mutations
    
    def describe_mutation(self, original: ast.AST, mutated: ast.AST) -> Tuple[str, str]:
        if isinstance(original, ast.If):
            return "if condition", "negated if condition"
        elif isinstance(original, ast.While):
            return "while condition", "negated while condition"
        elif isinstance(original, ast.IfExp):
            return "conditional expression", "negated conditional expression"
        return "conditional", "mutated conditional"


class MutationEngine:
    """Mutation testing engine using AST manipulation."""
    
    def __init__(self, target_file: str):
        self.target_file = Path(target_file).resolve()
        self.operators = [
            BinaryOperatorMutator(),
            ConstantMutator(),
            ConditionalMutator()
        ]
    
    def generate_mutations(self, source_code: str) -> List[Dict]:
        """Generate all possible mutations for the source code."""
        try:
            tree = ast.parse(source_code)
            mutations: List[Dict] = []
            
            for node in ast.walk(tree):
                for operator in self.operators:
                    if operator.can_mutate(node):
                        mutated_nodes = operator.mutate(node)
                        for mutated_node in mutated_nodes:
                            # Create a copy of the tree with the mutation
                            mutated_tree = self._apply_mutation(tree, node, mutated_node)
                            if mutated_tree:
                                mutated_code = ast.unparse(mutated_tree)
                                original_desc, mutated_desc = operator.describe_mutation(node, mutated_node)
                                
                                mutations.append({
                                    "id": f"mutation_{len(mutations) + 1}",
                                    "original": original_desc,
                                    "mutated": mutated_desc,
                                    "original_code": source_code,
                                    "mutated_code": mutated_code,
                                    "line_number": getattr(node, 'lineno', 0),
                                    "operator": operator.__class__.__name__
                                })
            
            return mutations
            
        except Exception as e:
            print(f"Error generating mutations: {e}")
            return []
    
    def _apply_mutation(self, tree: ast.AST, target_node: ast.AST, replacement: ast.AST) -> Optional[ast.AST]:
        """Apply a single mutation to the AST tree."""
        try:
            # Create a deep copy of the tree
            mutated_tree = ast.parse(ast.unparse(tree))
            
            # Find and replace the target node in the mutated tree
            for node in ast.walk(mutated_tree):
                if self._nodes_equivalent(node, target_node):
                    # Replace the node's attributes with the replacement
                    for attr in node._fields:
                        if hasattr(replacement, attr):
                            setattr(node, attr, getattr(replacement, attr))
                    break
            
            return mutated_tree
            
        except Exception as e:
            print(f"Error applying mutation: {e}")
            return None
    
    def _nodes_equivalent(self, node1: ast.AST, node2: ast.AST) -> bool:
        """Check if two AST nodes are equivalent for mutation purposes."""
        if type(node1) != type(node2):
            return False
        
        # Compare line numbers if available
        if hasattr(node1, 'lineno') and hasattr(node2, 'lineno'):
            return node1.lineno == node2.lineno
        
        # For nodes without line numbers, compare structure
        return ast.dump(node1) == ast.dump(node2)
    
    def run_tests_against_mutation(self, mutated_code: str, test_command: Optional[str] = None) -> Dict:
        """Run tests against a mutated version of the code."""
        original_content = None
        try:
            # Backup original file
            original_content = self.target_file.read_text()
            
            # Write mutated code
            self.target_file.write_text(mutated_code)
            
            # Run tests
            if not test_command:
                # Try to find test files automatically
                test_command = self._find_test_command()
            
            if test_command:
                result = subprocess.run(
                    test_command.split(),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.target_file.parent
                )
                
                return {
                    "passed": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            else:
                return {
                    "passed": None,
                    "error": "No test command found"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "error": "Test execution timed out"
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
        finally:
            # Restore original file
            if original_content is not None:
                self.target_file.write_text(original_content)
    
    def _find_test_command(self) -> Optional[str]:
        """Automatically find an appropriate test command."""
        file_stem = self.target_file.stem
        test_files = []
        
        # Look for test files in the same directory
        for pattern in [f"test_{file_stem}.py", f"{file_stem}_test.py", f"test{file_stem}.py"]:
            test_file = self.target_file.parent / pattern
            if test_file.exists():
                test_files.append(str(test_file))
        
        if test_files:
            return f"python -m pytest {test_files[0]} -v"
        
        # Try running the file directly if it has a main block
        try:
            content = self.target_file.read_text()
            if 'if __name__ == "__main__"' in content:
                return f"python {self.target_file}"
        except:
            pass
        
        return None