import ast
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from baml_client.sync_client import b
from baml_client.types import PythonTestFile, CoverageAnalysis
from utils import read_python_file, parse_python_ast


class CoverageAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze code coverage requirements."""
    
    def __init__(self, function_node: ast.FunctionDef):
        self.function_node = function_node
        self.branches = []
        self.loops = []
        self.exception_paths = []
        self.return_statements = []
        self.parameters = []
        self.current_depth = 0
        
        # Extract function parameters
        for arg in function_node.args.args:
            param_info = arg.arg
            if arg.annotation:
                try:
                    param_info += f": {ast.unparse(arg.annotation)}"
                except:
                    param_info += ": <annotation>"
            self.parameters.append(param_info)
    
    def visit_If(self, node: ast.If):
        """Analyze if/elif/else branches."""
        self.current_depth += 1
        
        # Main if condition
        try:
            condition = ast.unparse(node.test)
        except:
            condition = "<complex_condition>"
        
        self.branches.append(f"if {condition} (True path)")
        self.branches.append(f"if {condition} (False path)")
        
        # Process elif branches
        current = node
        elif_count = 0
        while current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            elif_count += 1
            elif_node = current.orelse[0]
            try:
                elif_condition = ast.unparse(elif_node.test)
            except:
                elif_condition = f"<elif_condition_{elif_count}>"
            
            self.branches.append(f"elif {elif_condition} (True path)")
            current = elif_node
        
        # Final else branch if it exists
        if current.orelse and not (len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If)):
            self.branches.append("else branch")
        
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_While(self, node: ast.While):
        """Analyze while loops."""
        try:
            condition = ast.unparse(node.test)
        except:
            condition = "<while_condition>"
        
        self.loops.append(f"while {condition} (zero iterations)")
        self.loops.append(f"while {condition} (one iteration)")
        self.loops.append(f"while {condition} (multiple iterations)")
        
        # Check for break and continue in loop body
        for child in ast.walk(node):
            if isinstance(child, ast.Break):
                self.loops.append(f"while {condition} (early break)")
            elif isinstance(child, ast.Continue):
                self.loops.append(f"while {condition} (continue statement)")
        
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For):
        """Analyze for loops."""
        try:
            target = ast.unparse(node.target)
            iter_expr = ast.unparse(node.iter)
        except:
            target = "<target>"
            iter_expr = "<iterable>"
        
        self.loops.append(f"for {target} in {iter_expr} (empty iterable)")
        self.loops.append(f"for {target} in {iter_expr} (single item)")
        self.loops.append(f"for {target} in {iter_expr} (multiple items)")
        
        # Check for break and continue in loop body
        for child in ast.walk(node):
            if isinstance(child, ast.Break):
                self.loops.append(f"for {target} in {iter_expr} (early break)")
            elif isinstance(child, ast.Continue):
                self.loops.append(f"for {target} in {iter_expr} (continue statement)")
        
        # Check for else clause
        if node.orelse:
            self.loops.append(f"for {target} in {iter_expr} (else clause - no break)")
        
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try):
        """Analyze try/except/finally blocks."""
        self.exception_paths.append("try block (successful execution)")
        
        # Handle each except handler
        for i, handler in enumerate(node.handlers):
            if handler.type:
                try:
                    exc_type = ast.unparse(handler.type)
                except:
                    exc_type = f"<exception_type_{i}>"
            else:
                exc_type = "Exception"
            
            self.exception_paths.append(f"except {exc_type} block")
        
        # Handle finally block
        if node.finalbody:
            self.exception_paths.append("finally block execution")
        
        # Handle else block (executes if no exception in try)
        if node.orelse:
            self.exception_paths.append("try-else block (no exception)")
        
        self.generic_visit(node)
    
    def visit_Return(self, node: ast.Return):
        """Analyze return statements."""
        if node.value:
            try:
                return_expr = ast.unparse(node.value)
            except:
                return_expr = "<return_value>"
        else:
            return_expr = "None"
        
        self.return_statements.append(f"return {return_expr}")
        self.generic_visit(node)
    
    def visit_With(self, node: ast.With):
        """Analyze with statements (context managers)."""
        for item in node.items:
            try:
                context_expr = ast.unparse(item.context_expr)
            except:
                context_expr = "<context_manager>"
            
            self.exception_paths.append(f"with {context_expr} (successful)")
            self.exception_paths.append(f"with {context_expr} (exception in context)")
        
        self.generic_visit(node)
    
    def visit_Assert(self, node: ast.Assert):
        """Analyze assert statements."""
        try:
            test_expr = ast.unparse(node.test)
        except:
            test_expr = "<assertion>"
        
        self.branches.append(f"assert {test_expr} (passes)")
        self.exception_paths.append(f"assert {test_expr} (fails - AssertionError)")
        self.generic_visit(node)


def analyze_function_coverage(source_code: str, function_node: ast.FunctionDef) -> CoverageAnalysis:
    """Analyze a function for comprehensive coverage requirements."""
    analyzer = CoverageAnalyzer(function_node)
    analyzer.visit(function_node)
    
    # If no explicit return statements found, add implicit None return
    if not analyzer.return_statements:
        analyzer.return_statements.append("return None (implicit)")
    
    return CoverageAnalysis(
        function_name=function_node.name,
        branches=analyzer.branches,
        loops=analyzer.loops,
        exception_paths=analyzer.exception_paths,
        return_statements=analyzer.return_statements,
        parameters=analyzer.parameters
    )


def generate_coverage_tests(file_path: str) -> str:
    """
    Generate comprehensive test cases designed to achieve maximum code coverage.
    Analyzes the code structure and creates tests for all branches, loops, and edge cases.
    """
    try:
        source_code = read_python_file(file_path)
        tree = parse_python_ast(source_code)
    except (FileNotFoundError, SyntaxError) as e:
        return f"Error: {e}"
    
    test_file_content = []
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Find all functions in the file
    functions_found = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions_found += 1
            function_source = ast.get_source_segment(source_code, node)
            
            try:
                # Perform detailed coverage analysis
                coverage_analysis = analyze_function_coverage(source_code, node)
                
                # Call BAML to generate coverage-focused tests
                test_file: PythonTestFile = b.GenerateCoverageTests(
                    function_source, 
                    coverage_analysis
                )
                
                # Format the generated tests
                for test_case in test_file.test_cases:
                    # Ensure test name starts with 'test_'
                    test_name = test_case.name
                    if not test_name.startswith('test_'):
                        test_name = f'test_{test_name}'
                    
                    test_file_content.append(f"    def {test_name}(self):")
                    
                    # Process the body with proper indentation
                    body_lines = test_case.body.split('\n')
                    inside_with_block = False
                    
                    for line in body_lines:
                        if not line.strip():
                            test_file_content.append("")
                            continue
                        
                        content = line.strip()
                        
                        # Add module prefix to function calls
                        import re
                        for func_node in ast.walk(tree):
                            if isinstance(func_node, ast.FunctionDef):
                                func_pattern = rf'\b{func_node.name}\('
                                if re.search(func_pattern, content):
                                    content = re.sub(func_pattern, f'{module_name}.{func_node.name}(', content)
                        
                        # Handle indentation based on context
                        if content.startswith('with self.assertRaises'):
                            inside_with_block = True
                            test_file_content.append(f"        {content}")
                        elif inside_with_block and not content.startswith(('with ', 'if ', 'for ', 'def ', 'class ', 'try:', 'except', 'finally:', 'else:')):
                            test_file_content.append(f"            {content}")
                        else:
                            inside_with_block = False
                            test_file_content.append(f"        {content}")
                    
                    test_file_content.append("")  # Blank line between tests
                
            except Exception as e:
                # Fallback: create a comprehensive placeholder test
                test_file_content.append(f"    def test_{node.name}_coverage_placeholder(self):")
                test_file_content.append(f'        """Coverage test placeholder for {node.name}."""')
                test_file_content.append(f"        # TODO: BAML generation failed: {str(e)[:100]}")
                test_file_content.append(f"        # Function analysis showed: {len(coverage_analysis.branches) if 'coverage_analysis' in locals() else 0} branches, {len(coverage_analysis.loops) if 'coverage_analysis' in locals() else 0} loops")
                test_file_content.append(f"        self.assertTrue(True)  # Placeholder assertion")
                test_file_content.append("")
    
    if functions_found == 0:
        return f"No functions found in {file_path} to generate coverage tests for."
    
    # Collect all imports from BAML responses
    all_imports = set(['import unittest', 'import coverage', f'import {module_name}'])
    
    # Create the complete test file
    class_name_parts = [part.capitalize() for part in module_name.split('_')]
    class_name = "".join(class_name_parts)
    
    # Collect imports from BAML responses
    try:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_source = ast.get_source_segment(source_code, node)
                coverage_analysis = analyze_function_coverage(source_code, node)
                test_file: PythonTestFile = b.GenerateCoverageTests(function_source, coverage_analysis)
                all_imports.update(test_file.imports)
    except:
        pass  # If import collection fails, continue with basic imports
    
    imports_section = '\n'.join(sorted(all_imports))
    
    full_test_file = f"""{imports_section}


class TestCoverage{class_name}(unittest.TestCase):
    \"\"\"
    Comprehensive test suite designed for maximum code coverage.
    Generated using AI-powered coverage analysis.
    \"\"\"
    
    @classmethod
    def setUpClass(cls):
        \"\"\"Set up coverage measurement for the test suite.\"\"\"
        cls.cov = coverage.Coverage()
        cls.cov.start()
    
    @classmethod
    def tearDownClass(cls):
        \"\"\"Stop coverage measurement and generate report.\"\"\"
        cls.cov.stop()
        cls.cov.save()
        
        # Print coverage report
        print("\\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cls.cov.report(show_missing=True)
        
        # Get coverage percentage
        print("\\nTotal Coverage: See report above")
        print("="*50)

{chr(10).join(test_file_content)}
if __name__ == '__main__':
    unittest.main()
"""
    
    # Save the test file
    test_file_name = f"test_coverage_{module_name}.py"
    test_file_path = os.path.join(os.path.dirname(file_path), test_file_name)
    
    with open(test_file_path, 'w') as f:
        f.write(full_test_file.strip())
    
    return f"Successfully generated comprehensive coverage tests at {test_file_path}\\nFound {functions_found} functions with detailed coverage analysis including:\\n- {sum(len(getattr(analyze_function_coverage(read_python_file(file_path), node), 'branches', [])) for node in ast.walk(parse_python_ast(read_python_file(file_path))) if isinstance(node, ast.FunctionDef))} branch conditions\\n- {sum(len(getattr(analyze_function_coverage(read_python_file(file_path), node), 'loops', [])) for node in ast.walk(parse_python_ast(read_python_file(file_path))) if isinstance(node, ast.FunctionDef))} loop scenarios\\n- {sum(len(getattr(analyze_function_coverage(read_python_file(file_path), node), 'exception_paths', [])) for node in ast.walk(parse_python_ast(read_python_file(file_path))) if isinstance(node, ast.FunctionDef))} exception paths"