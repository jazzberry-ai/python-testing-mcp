"""
Mutation Operators for Python AST

Defines various mutation operators that can be applied to Python AST nodes.
Each operator represents a small semantic change that tests should catch.
"""

import ast
import copy
from abc import ABC, abstractmethod
from typing import List, Type, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MutationInfo:
    """Information about a specific mutation."""
    operator_name: str
    original_code: str
    mutated_code: str
    line_number: int
    column_number: int
    description: str
    category: str


class BaseMutationOperator(ABC):
    """Base class for all mutation operators."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the mutation operator."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this operator does."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Category of mutation (arithmetic, comparison, etc.)."""
        pass
    
    @property
    @abstractmethod
    def target_node_types(self) -> List[Type[ast.AST]]:
        """AST node types this operator can mutate."""
        pass
    
    @abstractmethod
    def can_mutate(self, node: ast.AST) -> bool:
        """Check if this operator can mutate the given node."""
        pass
    
    @abstractmethod
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        """Apply mutation to the node, returning list of mutated variants."""
        pass


class ArithmeticOperatorMutator(BaseMutationOperator):
    """Mutates arithmetic operators (+, -, *, /, //, %, **)."""
    
    # Mapping of original operators to their mutations
    OPERATOR_MUTATIONS = {
        ast.Add: [ast.Sub, ast.Mult],
        ast.Sub: [ast.Add, ast.Mult],
        ast.Mult: [ast.Add, ast.Sub, ast.Div],
        ast.Div: [ast.Mult, ast.FloorDiv],
        ast.FloorDiv: [ast.Div, ast.Mod],
        ast.Mod: [ast.FloorDiv, ast.Mult],
        ast.Pow: [ast.Mult, ast.Div],
    }
    
    @property
    def name(self) -> str:
        return "ArithmeticOperator"
    
    @property
    def description(self) -> str:
        return "Mutates arithmetic operators (+, -, *, /, //, %, **)"
    
    @property
    def category(self) -> str:
        return "arithmetic"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.BinOp]
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.BinOp) and 
                type(node.op) in self.OPERATOR_MUTATIONS)
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutants = []
        original_op_type = type(node.op)
        
        for new_op_type in self.OPERATOR_MUTATIONS[original_op_type]:
            mutant = copy.deepcopy(node)
            mutant.op = new_op_type()
            mutants.append(mutant)
        
        return mutants


class ComparisonOperatorMutator(BaseMutationOperator):
    """Mutates comparison operators (==, !=, <, <=, >, >=)."""
    
    OPERATOR_MUTATIONS = {
        ast.Eq: [ast.NotEq, ast.Lt, ast.Gt],
        ast.NotEq: [ast.Eq],
        ast.Lt: [ast.LtE, ast.Gt, ast.Eq],
        ast.LtE: [ast.Lt, ast.GtE, ast.NotEq],
        ast.Gt: [ast.GtE, ast.Lt, ast.Eq],
        ast.GtE: [ast.Gt, ast.LtE, ast.NotEq],
    }
    
    @property
    def name(self) -> str:
        return "ComparisonOperator"
    
    @property
    def description(self) -> str:
        return "Mutates comparison operators (==, !=, <, <=, >, >=)"
    
    @property
    def category(self) -> str:
        return "comparison"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.Compare]
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Compare) and 
                len(node.ops) == 1 and 
                type(node.ops[0]) in self.OPERATOR_MUTATIONS)
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutants = []
        original_op_type = type(node.ops[0])
        
        for new_op_type in self.OPERATOR_MUTATIONS[original_op_type]:
            mutant = copy.deepcopy(node)
            mutant.ops[0] = new_op_type()
            mutants.append(mutant)
        
        return mutants


class LogicalOperatorMutator(BaseMutationOperator):
    """Mutates logical operators (and, or)."""
    
    @property
    def name(self) -> str:
        return "LogicalOperator"
    
    @property
    def description(self) -> str:
        return "Mutates logical operators (and, or)"
    
    @property
    def category(self) -> str:
        return "logical"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.BoolOp]
    
    def can_mutate(self, node: ast.AST) -> bool:
        return isinstance(node, ast.BoolOp)
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutant = copy.deepcopy(node)
        if isinstance(node.op, ast.And):
            mutant.op = ast.Or()
        elif isinstance(node.op, ast.Or):
            mutant.op = ast.And()
        else:
            return []
        
        return [mutant]


class UnaryOperatorMutator(BaseMutationOperator):
    """Mutates unary operators (not, -, +)."""
    
    @property
    def name(self) -> str:
        return "UnaryOperator"
    
    @property
    def description(self) -> str:
        return "Mutates unary operators (not, -, +) and removes them"
    
    @property
    def category(self) -> str:
        return "logical"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.UnaryOp]
    
    def can_mutate(self, node: ast.AST) -> bool:
        return isinstance(node, ast.UnaryOp)
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutants = []
        
        # Remove the unary operator entirely
        mutants.append(node.operand)
        
        # For 'not' operator, we can also try other mutations
        if isinstance(node.op, ast.Not):
            # Just return the operand (remove 'not')
            pass  # Already added above
        elif isinstance(node.op, ast.UAdd):
            # Change +x to -x
            mutant = copy.deepcopy(node)
            mutant.op = ast.USub()
            mutants.append(mutant)
        elif isinstance(node.op, ast.USub):
            # Change -x to +x
            mutant = copy.deepcopy(node)
            mutant.op = ast.UAdd()
            mutants.append(mutant)
        
        return mutants


class BooleanMutator(BaseMutationOperator):
    """Mutates boolean constants (True/False)."""
    
    @property
    def name(self) -> str:
        return "Boolean"
    
    @property
    def description(self) -> str:
        return "Mutates boolean constants (True <-> False)"
    
    @property
    def category(self) -> str:
        return "boolean"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.Constant]
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Constant) and 
                isinstance(node.value, bool))
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutant = copy.deepcopy(node)
        mutant.value = not node.value
        return [mutant]


class NumberMutator(BaseMutationOperator):
    """Mutates numeric constants."""
    
    @property
    def name(self) -> str:
        return "Number"
    
    @property
    def description(self) -> str:
        return "Mutates numeric constants (increment/decrement, zero, one)"
    
    @property
    def category(self) -> str:
        return "constant"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.Constant]
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Constant) and 
                isinstance(node.value, (int, float)) and
                not isinstance(node.value, bool))  # bool is subclass of int
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutants = []
        original_value = node.value
        
        # Common mutations for numbers
        mutations = []
        
        if original_value == 0:
            mutations = [1, -1]
        elif original_value == 1:
            mutations = [0, 2, -1]
        elif original_value == -1:
            mutations = [0, 1, -2]
        else:
            # For other numbers, try increment/decrement and boundary values
            mutations = [
                original_value + 1,
                original_value - 1,
                0,
                1,
                -1
            ]
        
        # Remove duplicates and the original value
        mutations = list(set(mutations))
        if original_value in mutations:
            mutations.remove(original_value)
        
        for new_value in mutations:
            mutant = copy.deepcopy(node)
            mutant.value = type(original_value)(new_value)  # Preserve type (int/float)
            mutants.append(mutant)
        
        return mutants


class StringMutator(BaseMutationOperator):
    """Mutates string constants."""
    
    @property
    def name(self) -> str:
        return "String"
    
    @property
    def description(self) -> str:
        return "Mutates string constants (empty string, different content)"
    
    @property
    def category(self) -> str:
        return "constant"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.Constant]
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Constant) and 
                isinstance(node.value, str))
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutants = []
        original_value = node.value
        
        # Common string mutations
        mutations = []
        
        if original_value == "":
            mutations = ["mutant", "X", " "]
        elif len(original_value) == 1:
            mutations = ["", "XX", original_value.upper(), original_value.lower()]
        else:
            mutations = [
                "",  # Empty string
                "mutant",  # Different content
                original_value[:-1],  # Remove last char
                original_value + "X",  # Add char
                original_value.upper() if original_value.islower() else original_value.lower(),
            ]
        
        # Remove duplicates and the original value
        mutations = list(set(mutations))
        if original_value in mutations:
            mutations.remove(original_value)
        
        for new_value in mutations[:3]:  # Limit mutations to avoid too many
            mutant = copy.deepcopy(node)
            mutant.value = new_value
            mutants.append(mutant)
        
        return mutants


class ConditionalBoundaryMutator(BaseMutationOperator):
    """Mutates conditional boundaries (< to <=, > to >=, etc.)."""
    
    @property
    def name(self) -> str:
        return "ConditionalBoundary"
    
    @property
    def description(self) -> str:
        return "Mutates conditional boundaries (< to <=, > to >=)"
    
    @property
    def category(self) -> str:
        return "comparison"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.Compare]
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Compare) and 
                len(node.ops) == 1 and 
                type(node.ops[0]) in [ast.Lt, ast.LtE, ast.Gt, ast.GtE])
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutant = copy.deepcopy(node)
        original_op = node.ops[0]
        
        if isinstance(original_op, ast.Lt):
            mutant.ops[0] = ast.LtE()
        elif isinstance(original_op, ast.LtE):
            mutant.ops[0] = ast.Lt()
        elif isinstance(original_op, ast.Gt):
            mutant.ops[0] = ast.GtE()
        elif isinstance(original_op, ast.GtE):
            mutant.ops[0] = ast.Gt()
        
        return [mutant]


class StatementDeletionMutator(BaseMutationOperator):
    """Deletes statements to test if they're actually necessary."""
    
    @property
    def name(self) -> str:
        return "StatementDeletion"
    
    @property
    def description(self) -> str:
        return "Deletes statements to test necessity"
    
    @property
    def category(self) -> str:
        return "statement"
    
    @property
    def target_node_types(self) -> List[Type[ast.AST]]:
        return [ast.Assign, ast.AugAssign, ast.Expr, ast.Return]
    
    def can_mutate(self, node: ast.AST) -> bool:
        # Don't delete certain critical statements
        if isinstance(node, ast.Return):
            return True
        if isinstance(node, ast.Assign):
            return True
        if isinstance(node, ast.AugAssign):
            return True
        if isinstance(node, ast.Expr):
            # Don't delete function calls that might have side effects
            return True
        
        return False
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        # Return a Pass statement to maintain syntax validity
        return [ast.Pass()]


# Registry of all available mutation operators
MUTATION_OPERATORS: List[BaseMutationOperator] = [
    ArithmeticOperatorMutator(),
    ComparisonOperatorMutator(),
    LogicalOperatorMutator(),
    UnaryOperatorMutator(),
    BooleanMutator(),
    NumberMutator(),
    StringMutator(),
    ConditionalBoundaryMutator(),
    StatementDeletionMutator(),
]


def get_applicable_operators(node: ast.AST) -> List[BaseMutationOperator]:
    """Get all mutation operators that can be applied to the given node."""
    return [op for op in MUTATION_OPERATORS if op.can_mutate(node)]


def get_operator_by_name(name: str) -> Optional[BaseMutationOperator]:
    """Get a mutation operator by name."""
    for op in MUTATION_OPERATORS:
        if op.name == name:
            return op
    return None