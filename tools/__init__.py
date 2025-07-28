"""
Software Testing Agent - Tools Package

This package contains various testing tools that can be used independently
or through the MCP server interface.

Available tools:
- fuzzer: AI-powered Python function fuzzing tool
"""

from .registry import ToolRegistry

__version__ = "1.0.0"
__all__ = ["ToolRegistry"]