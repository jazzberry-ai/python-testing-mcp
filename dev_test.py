#!/usr/bin/env python3
"""
Developer Testing Script for Software Testing Agent

This script provides easy testing and validation for developers working on the codebase.
Run this script to validate tool implementations, BAML integration, and overall system health.

Usage:
    python dev_test.py                    # Run all tests
    python dev_test.py --tools-only       # Test only tool implementations
    python dev_test.py --baml-only        # Test only BAML integration
    python dev_test.py --mcp-only         # Test only MCP server
    python dev_test.py --quick            # Quick validation tests
    python dev_test.py --verbose          # Detailed output
"""

import argparse
import asyncio
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def colored_print(message: str, color: str = "white", end: str = "\n"):
    """Print colored output for better visibility"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m", 
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}", end=end)

class DevTestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []
        self.project_root = Path(__file__).parent
        
    def log(self, message: str, level: str = "info"):
        """Log messages with appropriate formatting"""
        if level == "error":
            colored_print(f"❌ {message}", "red")
        elif level == "success":
            colored_print(f"✅ {message}", "green")
        elif level == "warning":
            colored_print(f"⚠️  {message}", "yellow")
        elif level == "info":
            if self.verbose:
                colored_print(f"ℹ️  {message}", "blue")
        else:
            print(message)
    
    def test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        
        if passed:
            self.log(f"{test_name}: PASSED {details}", "success")
        else:
            self.log(f"{test_name}: FAILED {details}", "error")
    
    def test_project_structure(self) -> bool:
        """Test that all required project files exist"""
        colored_print("\n🏗️  Testing Project Structure", "cyan")
        
        required_files = [
            "mcp_server.py",
            "main.py", 
            "tools/registry.py",
            "tools/fuzzer/tool.py",
            "tools/coverage/tool.py",
            "tools/unittest/tool.py",
            "tools/mutation/tool.py",
            "baml_src/testing.baml",
            "baml_src/clients.baml",
            "requirements.txt"
        ]
        
        all_passed = True
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.test_result(f"File exists: {file_path}", True)
            else:
                self.test_result(f"File exists: {file_path}", False, "Missing required file")
                all_passed = False
        
        return all_passed
    
    def test_baml_integration(self) -> bool:
        """Test BAML client and schema integration"""
        colored_print("\n🤖 Testing BAML Integration", "cyan")
        
        all_passed = True
        
        # Test BAML client import
        try:
            from baml_client.sync_client import b
            self.test_result("BAML client import", True)
        except ImportError as e:
            self.test_result("BAML client import", False, f"Import error: {e}")
            return False
        except Exception as e:
            self.test_result("BAML client import", False, f"Unexpected error: {e}")
            return False
        
        # Test BAML types import
        try:
            from baml_client.types import (
                FuzzTestInput, UnitTestCase, CrashAnalysis, 
                CoverageImprovement, MutationOperator, MutationReport
            )
            self.test_result("BAML types import", True)
        except ImportError as e:
            self.test_result("BAML types import", False, f"Types not generated: {e}")
            all_passed = False
        
        # Test BAML function availability (without API call)
        try:
            # Check if BAML functions are defined without calling them
            baml_functions = [
                "GenerateFuzzingInputs",
                "AnalyzeCrash", 
                "GenerateUnitTestCases",
                "GenerateCoverageImprovements",
                "GenerateMutationStrategy",
                "AnalyzeMutationResults"
            ]
            
            for func_name in baml_functions:
                if hasattr(b, func_name):
                    self.test_result(f"BAML function: {func_name}", True)
                else:
                    self.test_result(f"BAML function: {func_name}", False, "Function not found")
                    all_passed = False
                    
        except Exception as e:
            self.test_result("BAML function check", False, f"Error: {e}")
            all_passed = False
        
        return all_passed
    
    def test_tool_registry(self) -> bool:
        """Test tool registry and tool discovery"""
        colored_print("\n🔧 Testing Tool Registry", "cyan")
        
        all_passed = True
        
        try:
            from tools.registry import ToolRegistry, BaseTool
            registry = ToolRegistry()
            
            # Test tool discovery - ToolRegistry auto-discovers on init
            tool_names = registry.list_tools()
            self.test_result("Tool discovery", len(tool_names) > 0, f"Found {len(tool_names)} tools")
            
            # Check for expected tool types (use partial matching since tool names may vary)
            expected_tool_patterns = {
                "fuzzer": ["fuzzer", "python-fuzzer"],
                "coverage": ["coverage", "python-coverage"],
                "unittest": ["unittest", "unit_testing_tool", "unit-test"],
                "mutation": ["mutation", "mutation-testing"]
            }
            
            for expected_category, patterns in expected_tool_patterns.items():
                found = any(any(pattern in tool_name.lower() for pattern in patterns) for tool_name in tool_names)
                if found:
                    self.test_result(f"Tool category: {expected_category}", True)
                else:
                    self.test_result(f"Tool category: {expected_category}", False, "Tool category not found")
                    all_passed = False
            
            # Test each tool's interface compliance
            for tool_name in tool_names:
                try:
                    tool = registry.get_tool(tool_name)
                    
                    if tool is None:
                        self.test_result(f"Tool retrieval: {tool_name}", False, "Tool is None")
                        all_passed = False
                        continue
                    
                    # Test BaseTool interface
                    if isinstance(tool, BaseTool):
                        self.test_result(f"Tool interface: {tool_name}", True)
                    else:
                        self.test_result(f"Tool interface: {tool_name}", False, "Not BaseTool instance")
                        all_passed = False
                    
                    # Test MCP tool definitions
                    mcp_tools = tool.get_mcp_tools()
                    if isinstance(mcp_tools, list) and len(mcp_tools) > 0:
                        self.test_result(f"MCP tools: {tool_name}", True, f"{len(mcp_tools)} tools")
                    else:
                        self.test_result(f"MCP tools: {tool_name}", False, "No MCP tools defined")
                        all_passed = False
                        
                except Exception as e:
                    self.test_result(f"Tool validation: {tool_name}", False, f"Error: {e}")
                    all_passed = False
                    
        except Exception as e:
            self.test_result("Tool registry", False, f"Error: {e}")
            all_passed = False
        
        return all_passed
    
    def test_sample_functionality(self) -> bool:
        """Test sample functionality without API calls"""
        colored_print("\n🧪 Testing Sample Functionality", "cyan")
        
        all_passed = True
        
        # Create sample test file
        sample_code = '''
def add(a, b):
    """Add two numbers"""
    return a + b

def divide(x, y):
    """Divide x by y"""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

class Calculator:
    def multiply(self, a, b):
        """Multiply two numbers"""
        return a * b
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code)
            sample_file = f.name
        
        try:
            # Test Python code analysis
            from tools.fuzzer.analyzer import CodeAnalyzer
            analyzer = CodeAnalyzer(sample_file)
            functions = analyzer.extract_functions()
            
            if len(functions) >= 3:  # add, divide, multiply
                self.test_result("Code analysis", True, f"Found {len(functions)} functions")
            else:
                self.test_result("Code analysis", False, f"Expected 3+ functions, found {len(functions)}")
                all_passed = False
            
            # Test that functions have correct signatures
            function_names = [f.name for f in functions]  # FunctionInfo is a dataclass, use dot notation
            expected_functions = ['add', 'divide', 'multiply']
            
            for expected in expected_functions:
                if expected in function_names:
                    self.test_result(f"Function extracted: {expected}", True)
                else:
                    self.test_result(f"Function extracted: {expected}", False)
                    all_passed = False
                    
        except Exception as e:
            self.test_result("Code analysis", False, f"Error: {e}")
            all_passed = False
        finally:
            # Clean up
            os.unlink(sample_file)
        
        return all_passed
    
    async def test_mcp_server(self) -> bool:
        """Test MCP server initialization and tool listing"""
        colored_print("\n🖥️  Testing MCP Server", "cyan")
        
        all_passed = True
        
        try:
            # Import MCP server components
            import mcp_server
            from tools.registry import ToolRegistry
            
            # Test tool registry in MCP context
            registry = ToolRegistry()
            tool_names = registry.list_tools()
            
            if len(tool_names) > 0:
                self.test_result("MCP tool registration", True, f"{len(tool_names)} tools registered")
            else:
                self.test_result("MCP tool registration", False, "No tools registered")
                all_passed = False
            
            # Test MCP tool schema generation
            all_mcp_tools = registry.get_all_mcp_tools()
            
            if len(all_mcp_tools) > 0:
                self.test_result("Total MCP tools", True, f"{len(all_mcp_tools)} tools available")
            else:
                self.test_result("Total MCP tools", False, "No MCP tools generated")
                all_passed = False
            
            # Test individual tool schemas
            for tool_name in tool_names:
                try:
                    tool = registry.get_tool(tool_name)
                    if tool:
                        mcp_tools = tool.get_mcp_tools()
                        self.test_result(f"MCP schema: {tool_name}", True, f"{len(mcp_tools)} tools")
                    else:
                        self.test_result(f"MCP schema: {tool_name}", False, "Tool not found")
                        all_passed = False
                except Exception as e:
                    self.test_result(f"MCP schema: {tool_name}", False, f"Error: {e}")
                    all_passed = False
                
        except Exception as e:
            self.test_result("MCP server", False, f"Error: {e}")
            all_passed = False
        
        return all_passed
    
    def test_dependencies(self) -> bool:
        """Test that all required dependencies are installed"""
        colored_print("\n📦 Testing Dependencies", "cyan")
        
        required_packages = [
            ("mcp", "Model Context Protocol"),
            ("google.generativeai", "Google Gemini API"),
            ("coverage", "Code coverage analysis"),
            ("pytest", "Testing framework"),
            ("pydantic", "Data validation"),
            ("baml_py", "BAML Python client")
        ]
        
        all_passed = True
        missing_packages = []
        
        for package, description in required_packages:
            try:
                importlib.import_module(package)
                self.test_result(f"Package: {package}", True, description)
            except ImportError:
                self.test_result(f"Package: {package}", False, f"Missing: {description}")
                missing_packages.append(package)
                all_passed = False
        
        # Provide installation suggestions for missing packages
        if missing_packages:
            self.log("", "info")
            self.log("💡 Installation suggestions:", "warning")
            self.log("", "info")
            
            # Check if requirements.txt exists
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                self.log("Install all dependencies:", "warning")
                colored_print("   pip install -r requirements.txt", "yellow")
            else:
                self.log("Install missing packages individually:", "warning")
                for package in missing_packages:
                    colored_print(f"   pip install {package}", "yellow")
            
            self.log("", "info")
            self.log("Or activate your virtual environment if you have one:", "warning")
            colored_print("   source .venv/bin/activate  # Linux/macOS", "yellow")
            colored_print("   .venv\\Scripts\\activate     # Windows", "yellow")
        
        return all_passed
    
    def test_environment(self) -> bool:
        """Test environment configuration"""
        colored_print("\n🌍 Testing Environment", "cyan")
        
        all_passed = True
        
        # Check for API key (warn if missing, don't fail)
        if os.getenv('GEMINI_API_KEY'):
            self.test_result("GEMINI_API_KEY", True, "API key configured")
        else:
            self.test_result("GEMINI_API_KEY", True, "Not set (AI features will use fallback)")
            self.log("Set GEMINI_API_KEY for full AI functionality", "warning")
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.test_result("Python version", True, f"Python {python_version.major}.{python_version.minor}")
        else:
            self.test_result("Python version", False, f"Python {python_version.major}.{python_version.minor} < 3.8")
            all_passed = False
        
        return all_passed
    
    def generate_report(self):
        """Generate and display test report"""
        colored_print("\n📊 Test Report", "purple")
        colored_print("=" * 50, "purple")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        failed_tests = total_tests - passed_tests
        
        colored_print(f"Total Tests: {total_tests}", "white")
        colored_print(f"Passed: {passed_tests}", "green")
        colored_print(f"Failed: {failed_tests}", "red")
        colored_print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%", "cyan")
        
        if failed_tests > 0:
            colored_print("\n❌ Failed Tests:", "red")
            for result in self.results:
                if not result['passed']:
                    colored_print(f"  • {result['test']}: {result['details']}", "red")
        
        colored_print("=" * 50, "purple")
        
        if failed_tests == 0:
            colored_print("🎉 All tests passed! Your development environment is ready.", "green")
            return True
        else:
            colored_print(f"⚠️  {failed_tests} test(s) failed. Please fix issues above.", "yellow")
            return False

async def main():
    parser = argparse.ArgumentParser(description="Developer testing script for Software Testing Agent")
    parser.add_argument("--tools-only", action="store_true", help="Test only tool implementations")
    parser.add_argument("--baml-only", action="store_true", help="Test only BAML integration") 
    parser.add_argument("--mcp-only", action="store_true", help="Test only MCP server")
    parser.add_argument("--quick", action="store_true", help="Quick validation tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Detailed output")
    
    args = parser.parse_args()
    
    runner = DevTestRunner(verbose=args.verbose)
    
    colored_print("🚀 Software Testing Agent - Developer Testing", "purple")
    colored_print("=" * 60, "purple")
    
    success = True
    
    if not any([args.tools_only, args.baml_only, args.mcp_only, args.quick]):
        # Run all tests
        success &= runner.test_environment()
        success &= runner.test_dependencies() 
        success &= runner.test_project_structure()
        success &= runner.test_baml_integration()
        success &= runner.test_tool_registry()
        success &= runner.test_sample_functionality()
        success &= await runner.test_mcp_server()
    else:
        # Run selected tests
        if args.quick:
            success &= runner.test_dependencies()
            success &= runner.test_baml_integration()
            success &= runner.test_tool_registry()
        
        if args.baml_only:
            success &= runner.test_baml_integration()
        
        if args.tools_only:
            success &= runner.test_tool_registry()
            success &= runner.test_sample_functionality()
        
        if args.mcp_only:
            success &= await runner.test_mcp_server()
    
    # Generate report
    overall_success = runner.generate_report()
    
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    asyncio.run(main())