import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, List, Optional
from pathlib import Path

from utils.mutation_test_executor import MutationTestExecutor
from baml_client import b


def run_mutation_testing(file_path: str, test_command: Optional[str] = None, max_mutations: int = 15) -> str:
    """
    Run intelligent mutation testing on a Python file using custom AST-based engine and AI analysis.
    
    Args:
        file_path: Path to the Python file to test
        test_command: Optional test command (auto-detected if None)
        max_mutations: Maximum number of mutations to test (default: 15)
        
    Returns:
        String with detailed mutation testing results and recommendations
    """
    try:
        # Validate file exists and is readable
        file_path = str(Path(file_path).resolve())
        if not Path(file_path).exists():
            return f"Error: File not found: {file_path}"
        
        if not file_path.endswith('.py'):
            return f"Error: File must be a Python file (.py): {file_path}"
        
        # Initialize mutation test executor
        executor = MutationTestExecutor(file_path)
        
        # Check if test files exist - if not, just generate mutations for analysis
        test_files = executor.find_test_files()
        if not test_files and not test_command:
            print(f"No test files found for {Path(file_path).name}. Generating mutations for analysis only...")
            results = executor.run_mutation_generation_only()
            return _generate_analysis_only_report(results)
        
        # Run full mutation testing with tests
        print(f"Running mutation testing on {Path(file_path).name}...")
        if test_files and not test_command:
            test_command = f"python -m pytest {test_files[0]} -v"
            print(f"Using test command: {test_command}")
        
        results = executor.run_full_mutation_testing(test_command, max_mutations)
        
        # Generate and return comprehensive report
        return executor.generate_detailed_report(results)
        
    except Exception as e:
        return f"Error running mutation testing: {str(e)}"


def run_mutation_analysis_only(file_path: str) -> str:
    """
    Generate mutations and provide AI analysis without running tests.
    Useful for understanding potential test gaps.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        String with mutation analysis and recommendations
    """
    try:
        file_path = str(Path(file_path).resolve())
        if not Path(file_path).exists():
            return f"Error: File not found: {file_path}"
        
        if not file_path.endswith('.py'):
            return f"Error: File must be a Python file (.py): {file_path}"
        
        executor = MutationTestExecutor(file_path)
        results = executor.run_mutation_generation_only()
        
        return _generate_analysis_only_report(results)
        
    except Exception as e:
        return f"Error running mutation analysis: {str(e)}"


def _generate_analysis_only_report(results: Dict) -> str:
    """Generate a report for mutation analysis without test execution."""
    if results.get("status") == "error":
        return f"# Mutation Analysis Error\n\n**Error:** {results.get('error', 'Unknown error')}"
    
    mutations = results.get("mutations", [])
    total_mutations = results.get("total_mutations", 0)
    source_code = results.get("source_code", "")
    
    report = f"""# Mutation Analysis Report

**File:** `{results.get('target_file', 'Unknown')}`  
**Total Mutations Generated:** {total_mutations}

## Summary
This analysis shows potential mutations that could be used to test your code quality. Since no test files were found, mutations were generated for analysis purposes only.

## Generated Mutations ({total_mutations})
These mutations represent potential changes that could reveal test coverage gaps:

"""
    
    if mutations:
        # Group mutations by operator type for better organization
        operator_groups = {}
        for mutation in mutations:
            operator = mutation.get('operator', 'Unknown')
            if operator not in operator_groups:
                operator_groups[operator] = []
            operator_groups[operator].append(mutation)
        
        for operator, group_mutations in operator_groups.items():
            report += f"### {operator.replace('Mutator', '')} Mutations ({len(group_mutations)})\n"
            for i, mutation in enumerate(group_mutations[:5], 1):  # Limit to 5 per group
                report += f"{i}. **Line {mutation.get('line_number', '?')}:** "
                report += f"`{mutation.get('original', 'Unknown')}` → `{mutation.get('mutated', 'Unknown')}`\n"
            
            if len(group_mutations) > 5:
                report += f"   ... and {len(group_mutations) - 5} more\n"
            report += "\n"
    
    # Add recommendations
    report += """## 🎯 Recommendations

To improve your code quality, consider:

1. **Create Test Files** - Add unit tests to validate your code behavior
   - Create `test_*.py` files in the same directory
   - Use pytest, unittest, or your preferred testing framework

2. **Focus on Key Areas** - The mutations above show critical areas to test:
   - **Binary Operations** - Test arithmetic and logical operations
   - **Comparisons** - Test boundary conditions and edge cases  
   - **Constants** - Test with different values, including edge cases
   - **Conditionals** - Test both true and false branches

3. **Run Full Mutation Testing** - Once you have tests, run mutation testing again to get a mutation score

## Next Steps
1. Create test files for this code
2. Run mutation testing again with: `run mutation testing on this file`
3. Aim for a mutation score of 80% or higher
"""
    
    return report