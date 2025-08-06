import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, List, Optional, Tuple
from baml_client.sync_client import b
from baml_client.types import MutationAnalysis


class MutationIntelligence:
    """AI-powered analysis of mutation testing results using BAML."""
    
    def __init__(self):
        pass  # BAML client is imported as 'b'
    
    def analyze_survived_mutations(self, mutations: List[Dict], source_code: str) -> Dict:
        """
        Analyze survived mutations to understand their significance and suggest fixes.
        
        Args:
            mutations: List of survived mutation objects
            source_code: Original source code of the file
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        if not mutations:
            return {
                "critical_survivors": [],
                "edge_case_gaps": [],
                "test_recommendations": [],
                "overall_assessment": "All mutations were successfully caught by tests."
            }
        
        try:
            # Format survived mutations for BAML
            survived_mutations_text = self._format_mutations_for_baml(mutations)
            mutation_details = self._format_mutation_details(mutations)
            
            # Call BAML function for analysis
            analysis: MutationAnalysis = b.AnalyzeMutationResults(
                source_code=source_code,
                survived_mutations=survived_mutations_text,
                mutation_details=mutation_details
            )
            
            return {
                "critical_survivors": analysis.critical_survivors,
                "edge_case_gaps": analysis.edge_case_gaps,
                "test_recommendations": analysis.test_recommendations,
                "overall_assessment": analysis.overall_assessment
            }
            
        except Exception as e:
            return {
                "error": f"Failed to analyze mutations: {str(e)}",
                "critical_survivors": [f"{m.get('original', 'Unknown')} -> {m.get('mutated', 'Unknown')}" for m in mutations],
                "edge_case_gaps": ["Analysis failed - manual review required"],
                "test_recommendations": ["Review all survived mutations manually"],
                "overall_assessment": f"Analysis failed due to error: {str(e)}"
            }
    
    def _format_mutations_for_baml(self, mutations: List[Dict]) -> str:
        """Format mutations for BAML input."""
        mutations_text = ""
        for i, mutation in enumerate(mutations, 1):
            mutations_text += f"""Mutation {i}:
- Line {mutation.get('line_number', '?')}: {mutation.get('original', 'Unknown')} → {mutation.get('mutated', 'Unknown')}
- Operator: {mutation.get('operator', 'Unknown')}
"""
        return mutations_text.strip()
    
    def _format_mutation_details(self, mutations: List[Dict]) -> str:
        """Format detailed mutation information for BAML."""
        details_text = ""
        for i, mutation in enumerate(mutations, 1):
            details_text += f"""Mutation {i} Details:
- ID: {mutation.get('id', f'mutation_{i}')}
- Line: {mutation.get('line_number', 'Unknown')}
- Operator: {mutation.get('operator', 'Unknown')}
- Original: {mutation.get('original', 'Unknown')}
- Mutated: {mutation.get('mutated', 'Unknown')}
- Status: Survived (test did not detect this change)

"""
        return details_text.strip()
    
    def generate_test_suggestions(self, mutation: Dict, source_code: str) -> List[str]:
        """
        Generate specific test case suggestions for a survived mutation using BAML.
        
        Args:
            mutation: Single mutation that survived
            source_code: Original source code
            
        Returns:
            List of specific test case suggestions
        """
        try:
            # Format single mutation for analysis
            mutation_text = f"Line {mutation.get('line_number', '?')}: {mutation.get('original', 'Unknown')} → {mutation.get('mutated', 'Unknown')}"
            mutation_details = f"""Mutation Details:
- Operator: {mutation.get('operator', 'Unknown')}
- Original: {mutation.get('original', 'Unknown')}  
- Mutated: {mutation.get('mutated', 'Unknown')}
- Line: {mutation.get('line_number', 'Unknown')}"""

            # Use BAML for analysis of single mutation
            analysis: MutationAnalysis = b.AnalyzeMutationResults(
                source_code=source_code,
                survived_mutations=mutation_text,
                mutation_details=mutation_details
            )
            
            # Extract actionable recommendations
            suggestions = []
            for rec in analysis.test_recommendations:
                suggestions.append(rec)
            
            return suggestions if suggestions else [f"Add tests for mutation: {mutation.get('original', 'Unknown')} -> {mutation.get('mutated', 'Unknown')}"]
            
        except Exception as e:
            return [f"Manual review needed for mutation: {mutation.get('original', 'Unknown')} -> {mutation.get('mutated', 'Unknown')} (Error: {str(e)})"]
    
    def prioritize_mutations(self, mutations: List[Dict], source_code: str) -> List[Dict]:
        """
        Prioritize mutations by their potential impact and likelihood of revealing real bugs.
        
        Args:
            mutations: List of survived mutations
            source_code: Original source code
            
        Returns:
            List of mutations sorted by priority (highest first)
        """
        if not mutations:
            return []
        
        try:
            # Add priority scoring to each mutation
            for mutation in mutations:
                mutation["priority_score"] = self._calculate_priority_score(mutation, source_code)
            
            # Sort by priority score (highest first)
            return sorted(mutations, key=lambda m: m.get("priority_score", 0), reverse=True)
            
        except Exception as e:
            print(f"Warning: Failed to prioritize mutations: {e}")
            return mutations
    
    def _calculate_priority_score(self, mutation: Dict, source_code: str) -> int:
        """Calculate priority score for a mutation (higher = more important)."""
        score = 50  # Base score
        
        original = mutation.get("original", "").lower()
        mutated = mutation.get("mutated", "").lower()
        
        # Higher priority for logic operators
        if any(op in original or op in mutated for op in ["and", "or", "not", "==", "!=", "<", ">", "<=", ">="]):
            score += 30
        
        # Higher priority for error handling
        if any(keyword in original or keyword in mutated for keyword in ["try", "except", "raise", "assert"]):
            score += 25
        
        # Higher priority for boundary conditions
        if any(boundary in original or boundary in mutated for boundary in ["0", "1", "-1", "len(", "range("]):
            score += 20
        
        # Higher priority for return statements
        if "return" in original or "return" in mutated:
            score += 15
        
        # Lower priority for simple value changes (unless boundary values)
        if original.isdigit() and mutated.isdigit():
            if abs(int(original) - int(mutated)) == 1:
                score += 10  # Off-by-one errors are important
            else:
                score -= 10
        
        return score