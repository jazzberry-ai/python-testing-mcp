import sys
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.mutation_engine import MutationEngine
from utils.file_handlers import read_python_file
from utils.mutation_intelligence import MutationIntelligence


class MutationTestExecutor:
    """Executes mutation testing using custom mutation engine and AI analysis."""
    
    def __init__(self, target_file: str):
        self.target_file = Path(target_file).resolve()
        self.engine = MutationEngine(str(self.target_file))
        self.intelligence = MutationIntelligence()
    
    def run_full_mutation_testing(self, test_command: Optional[str] = None, max_mutations: int = 20) -> Dict:
        """
        Run complete mutation testing with AI analysis.
        
        Args:
            test_command: Custom test command (auto-detected if None)
            max_mutations: Maximum number of mutations to test
            
        Returns:
            Dictionary with comprehensive mutation testing results
        """
        try:
            # Read source code
            source_code = read_python_file(str(self.target_file))
            if not source_code:
                return self._error_result("Could not read source file")
            
            print(f"Generating mutations for {self.target_file.name}...")
            
            # Generate all possible mutations
            all_mutations = self.engine.generate_mutations(source_code)
            if not all_mutations:
                return self._error_result("No mutations could be generated")
            
            # Limit mutations for performance
            mutations_to_test = all_mutations[:max_mutations]
            print(f"Testing {len(mutations_to_test)} mutations (out of {len(all_mutations)} possible)...")
            
            # Test each mutation
            results = []
            survived_mutations = []
            killed_count = 0
            
            for i, mutation in enumerate(mutations_to_test, 1):
                print(f"Testing mutation {i}/{len(mutations_to_test)}: {mutation['original']} → {mutation['mutated']}")
                
                # Run tests against this mutation
                test_result = self.engine.run_tests_against_mutation(
                    mutation['mutated_code'], 
                    test_command
                )
                
                mutation_result = {
                    **mutation,
                    "test_result": test_result,
                    "status": "killed" if test_result.get("passed") == False else "survived",
                    "execution_time": time.time()  # Placeholder for timing
                }
                
                results.append(mutation_result)
                
                if test_result.get("passed") == False:
                    killed_count += 1
                else:
                    survived_mutations.append(mutation_result)
            
            # Calculate mutation score
            mutation_score = (killed_count / len(mutations_to_test)) * 100 if mutations_to_test else 0
            
            print(f"Mutation testing complete. Score: {mutation_score:.1f}% ({killed_count}/{len(mutations_to_test)})")
            
            # Generate AI analysis for survived mutations
            ai_analysis = {}
            if survived_mutations:
                print("Analyzing survived mutations with AI...")
                ai_analysis = self._analyze_survivors(survived_mutations, source_code)
            
            return {
                "status": "completed",
                "target_file": str(self.target_file),
                "source_code": source_code,
                "total_possible_mutations": len(all_mutations),
                "mutations_tested": len(mutations_to_test),
                "mutations_killed": killed_count,
                "mutations_survived": len(survived_mutations),
                "mutation_score": mutation_score,
                "all_results": results,
                "survived_mutations": survived_mutations,
                "ai_analysis": ai_analysis,
                "summary": {
                    "total": len(mutations_to_test),
                    "killed": killed_count,
                    "survived": len(survived_mutations),
                    "timeout": 0  # Our engine doesn't use timeouts for individual mutations
                }
            }
            
        except Exception as e:
            return self._error_result(f"Mutation testing failed: {str(e)}")
    
    def run_mutation_generation_only(self) -> Dict:
        """Generate mutations without running tests - useful for analysis."""
        try:
            source_code = read_python_file(str(self.target_file))
            if not source_code:
                return self._error_result("Could not read source file")
            
            mutations = self.engine.generate_mutations(source_code)
            
            return {
                "status": "completed",
                "target_file": str(self.target_file),
                "source_code": source_code,
                "mutations": mutations,
                "total_mutations": len(mutations)
            }
            
        except Exception as e:
            return self._error_result(f"Mutation generation failed: {str(e)}")
    
    def _analyze_survivors(self, survived_mutations: List[Dict], source_code: str) -> Dict:
        """Analyze survived mutations using AI."""
        try:
            # Convert mutations to format expected by MutationIntelligence
            mutation_data = []
            for mutation in survived_mutations:
                mutation_data.append({
                    "original": mutation.get("original", ""),
                    "mutated": mutation.get("mutated", ""),
                    "context": [f"Line {mutation.get('line_number', 0)}"],
                    "id": mutation.get("id", ""),
                    "operator": mutation.get("operator", "")
                })
            
            # Use existing AI analysis
            analysis = self.intelligence.analyze_survived_mutations(mutation_data, source_code)
            
            # Add priority scoring
            prioritized_mutations = self.intelligence.prioritize_mutations(mutation_data, source_code)
            analysis["prioritized_mutations"] = prioritized_mutations
            
            return analysis
            
        except Exception as e:
            print(f"Warning: AI analysis failed: {e}")
            return {"error": str(e)}
    
    def _error_result(self, error_message: str) -> Dict:
        """Generate error result dictionary."""
        return {
            "status": "error",
            "error": error_message,
            "mutations_tested": 0,
            "mutations_killed": 0,
            "mutations_survived": 0,
            "mutation_score": 0.0,
            "survived_mutations": [],
            "ai_analysis": {}
        }
    
    def generate_detailed_report(self, results: Dict) -> str:
        """Generate a comprehensive mutation testing report."""
        if results.get("status") == "error":
            return f"# Mutation Testing Error\n\n**Error:** {results.get('error', 'Unknown error')}"
        
        mutation_score = results.get("mutation_score", 0)
        mutations_tested = results.get("mutations_tested", 0)
        mutations_killed = results.get("mutations_killed", 0)
        mutations_survived = results.get("mutations_survived", 0)
        survived_mutations = results.get("survived_mutations", [])
        ai_analysis = results.get("ai_analysis", {})
        
        # Generate report
        report = f"""# Mutation Testing Report

**File:** `{results.get('target_file', 'Unknown')}`  
**Mutation Score:** {mutation_score:.1f}% ({mutations_killed}/{mutations_tested} mutations killed)

## Summary
- **Total Possible Mutations:** {results.get('total_possible_mutations', 0)}
- **Mutations Tested:** {mutations_tested}
- **Mutations Killed:** {mutations_killed} ✅
- **Mutations Survived:** {mutations_survived} ⚠️

## Quality Assessment
"""
        
        if mutation_score >= 80:
            report += "🎉 **Excellent** - Your test suite catches most mutations! This indicates strong test coverage.\n"
        elif mutation_score >= 60:
            report += "✅ **Good** - Your test suite is solid but has some gaps to address.\n"
        elif mutation_score >= 40:
            report += "⚠️ **Needs Improvement** - Your test suite has significant gaps that could hide bugs.\n"
        else:
            report += "❌ **Poor** - Your test suite needs major improvements to catch potential bugs.\n"
        
        # Add survived mutations details
        if survived_mutations:
            report += f"\n## Survived Mutations ({len(survived_mutations)})\n"
            report += "These mutations were **not caught** by your tests, indicating potential test gaps:\n\n"
            
            # Sort by priority if available
            sorted_mutations = survived_mutations
            if ai_analysis.get("prioritized_mutations"):
                sorted_mutations = ai_analysis["prioritized_mutations"][:10]  # Top 10
            
            for i, mutation in enumerate(sorted_mutations, 1):
                report += f"### {i}. {mutation.get('original', 'Unknown')}\n"
                report += f"- **Changed to:** {mutation.get('mutated', 'Unknown')}\n"
                report += f"- **Line:** {mutation.get('line_number', 'Unknown')}\n"
                report += f"- **Operator:** {mutation.get('operator', 'Unknown')}\n"
                
                # Add test failure details if available
                test_result = mutation.get('test_result', {})
                if test_result.get('error'):
                    report += f"- **Test Error:** {test_result['error']}\n"
                elif test_result.get('passed') is None:
                    report += f"- **Issue:** No tests were found or executed\n"
                elif test_result.get('passed') is True:
                    report += f"- **Issue:** Tests passed even with this mutation\n"
                
                report += "\n"
        
        # Add AI analysis
        if ai_analysis and not ai_analysis.get("error"):
            report += "\n## 🤖 AI Analysis\n"
            
            # Critical survivors
            critical = ai_analysis.get('critical_survivors', [])
            if critical:
                report += "### Critical Issues\n"
                for item in critical[:3]:  # Top 3
                    report += f"- {item.get('description', 'Critical mutation survived')}\n"
                report += "\n"
            
            # Test recommendations
            recommendations = ai_analysis.get('test_recommendations', [])
            if recommendations:
                report += "### Recommended Test Cases\n"
                for i, rec in enumerate(recommendations[:5], 1):  # Top 5
                    if isinstance(rec, dict):
                        report += f"{i}. {rec.get('description', 'Add test case')}\n"
                    else:
                        report += f"{i}. {rec}\n"
                report += "\n"
            
            # Overall assessment
            assessment = ai_analysis.get('overall_assessment', '')
            if assessment:
                report += "### Assessment Summary\n"
                report += f"{assessment}\n\n"
        
        # Add actionable next steps
        report += "## 🎯 Next Steps\n"
        if mutations_survived > 0:
            report += "1. **Review survived mutations above** - these represent potential test gaps\n"
            report += "2. **Add test cases** to catch the most critical mutations\n"
            report += "3. **Focus on edge cases** - boundary conditions, error handling, special values\n"
            report += "4. **Re-run mutation testing** after adding tests to verify improvements\n"
        else:
            report += "1. **Excellent work!** All tested mutations were caught\n"
            report += "2. **Consider testing more mutations** by increasing the mutation limit\n"
            report += "3. **Maintain quality** by running mutation testing regularly\n"
        
        if mutations_tested < results.get('total_possible_mutations', 0):
            remaining = results.get('total_possible_mutations', 0) - mutations_tested
            report += f"\n💡 **Note:** {remaining} additional mutations were generated but not tested. "
            report += "Consider increasing the mutation limit for more comprehensive testing.\n"
        
        return report
    
    def find_test_files(self) -> List[str]:
        """Find test files related to the target file."""
        file_stem = self.target_file.stem
        test_files = []
        
        # Look in the same directory
        for pattern in [f"test_{file_stem}.py", f"{file_stem}_test.py", f"test{file_stem}.py"]:
            test_file = self.target_file.parent / pattern
            if test_file.exists():
                test_files.append(str(test_file))
        
        # Look in a tests directory
        tests_dir = self.target_file.parent / "tests"
        if tests_dir.exists():
            for pattern in [f"test_{file_stem}.py", f"{file_stem}_test.py"]:
                test_file = tests_dir / pattern
                if test_file.exists():
                    test_files.append(str(test_file))
        
        return test_files