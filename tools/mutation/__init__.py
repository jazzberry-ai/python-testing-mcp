"""
Mutation Testing Tool

Provides comprehensive mutation testing capabilities for Python code using AST-based
mutations with complete safety guarantees - original source files are never modified.
"""

from .tool import MutationTestingTool

__version__ = "1.0.0"
__all__ = ["MutationTestingTool"]