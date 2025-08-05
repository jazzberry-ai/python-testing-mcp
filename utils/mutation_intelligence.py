import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, List, Optional, Tuple
from utils.ai_clients import get_gemini_client


class MutationIntelligence:
    """AI-powered analysis of mutation testing results."""
    
    def __init__(self):
        self.client = get_gemini_client()
    
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
                "recommendations": [],
                "overall_assessment": "All mutations were successfully caught by tests."
            }
        
        try:
            analysis_prompt = self._build_analysis_prompt(mutations, source_code)
            response = self.client.chat.completions.create(
                model="gemini-2.0-flash-exp",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3
            )
            
            return self._parse_analysis_response(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "error": f"Failed to analyze mutations: {str(e)}",
                "critical_survivors": mutations,  # Fallback: treat all as critical
                "recommendations": ["Review all survived mutations manually"],
                "overall_assessment": "Analysis failed - manual review required"
            }
    
    def _build_analysis_prompt(self, mutations: List[Dict], source_code: str) -> str:
        """Build prompt for mutation analysis."""
        mutations_text = ""
        for i, mutation in enumerate(mutations, 1):
            mutations_text += f"""
Mutation {i}:
- Original: {mutation.get('original', 'Unknown')}
- Mutated to: {mutation.get('mutated', 'Unknown')}
- Context: {' '.join(mutation.get('context', [])[:3])}
"""
        
        return f"""
Analyze these survived mutations from mutation testing. A "survived mutation" means the tests didn't catch when this code change was made, indicating a potential gap in test coverage.

SOURCE CODE:
```python
{source_code}
```

SURVIVED MUTATIONS:
{mutations_text}

Please provide a detailed analysis in the following format:

CRITICAL_SURVIVORS: (List mutations that could cause real bugs in production)
- For each critical mutation, explain why it's dangerous and what real-world bug it could cause

EDGE_CASE_GAPS: (Mutations that reveal missing edge case testing)
- Identify boundary conditions, error handling, or special cases not being tested

TEST_RECOMMENDATIONS: (Specific test cases to add)
- For each important survived mutation, suggest exactly what test case should be added
- Provide concrete test scenarios, not just general advice

OVERALL_ASSESSMENT: (Summary of test suite quality and most important actions)

Focus on practical, actionable insights that will help improve the test suite.
"""
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse the AI analysis response into structured data."""
        try:
            sections = self._split_response_sections(response)
            
            return {
                "critical_survivors": self._parse_critical_survivors(sections.get("CRITICAL_SURVIVORS", "")),
                "edge_case_gaps": self._parse_edge_case_gaps(sections.get("EDGE_CASE_GAPS", "")),
                "test_recommendations": self._parse_test_recommendations(sections.get("TEST_RECOMMENDATIONS", "")),
                "overall_assessment": sections.get("OVERALL_ASSESSMENT", "").strip(),
                "raw_analysis": response
            }
        except Exception as e:
            return {
                "error": f"Failed to parse analysis: {str(e)}",
                "raw_analysis": response,
                "critical_survivors": [],
                "recommendations": [],
                "overall_assessment": "Analysis parsing failed"
            }
    
    def _split_response_sections(self, response: str) -> Dict[str, str]:
        """Split response into named sections."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            line = line.strip()
            if line.endswith(':') and line.replace(':', '').replace('_', '').replace(' ', '').isupper():
                # New section found
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.replace(':', '').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _parse_critical_survivors(self, text: str) -> List[Dict]:
        """Parse critical survivors section."""
        survivors = []
        current_survivor = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- ') and 'Original:' in line:
                if current_survivor:
                    survivors.append(current_survivor)
                current_survivor = {"description": line[2:], "severity": "high"}
            elif line.startswith('  ') and current_survivor:
                current_survivor["description"] += " " + line.strip()
        
        if current_survivor:
            survivors.append(current_survivor)
        
        return survivors
    
    def _parse_edge_case_gaps(self, text: str) -> List[str]:
        """Parse edge case gaps section."""
        gaps = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                gaps.append(line[2:])
        return gaps
    
    def _parse_test_recommendations(self, text: str) -> List[Dict]:
        """Parse test recommendations section."""
        recommendations = []
        current_rec = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {"description": line[2:], "priority": "medium"}
            elif line.startswith('  ') and current_rec:
                current_rec["description"] += " " + line.strip()
        
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations
    
    def generate_test_suggestions(self, mutation: Dict, source_code: str) -> List[str]:
        """
        Generate specific test case suggestions for a survived mutation.
        
        Args:
            mutation: Single mutation that survived
            source_code: Original source code
            
        Returns:
            List of specific test case suggestions
        """
        try:
            prompt = f"""
Given this survived mutation in Python code, suggest specific test cases that would catch it:

ORIGINAL CODE:
```python
{source_code}
```

SURVIVED MUTATION:
- Original: {mutation.get('original', 'Unknown')}
- Mutated to: {mutation.get('mutated', 'Unknown')}

Generate 2-3 specific test cases (with concrete input values and expected outputs) that would detect this mutation. Focus on:
1. What specific inputs would behave differently with the mutation
2. What assertions would fail
3. Edge cases this mutation might affect

Format each suggestion as:
TEST: Brief description
INPUT: Specific test inputs
EXPECTED: Expected behavior that would fail with mutation
ASSERTION: Specific assertion to add

Be concrete and actionable.
"""
            
            response = self.client.chat.completions.create(
                model="gemini-2.0-flash-exp",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            
            return self._parse_test_suggestions(response.choices[0].message.content)
            
        except Exception as e:
            return [f"Manual review needed for mutation: {mutation.get('original', 'Unknown')} -> {mutation.get('mutated', 'Unknown')}"]
    
    def _parse_test_suggestions(self, response: str) -> List[str]:
        """Parse test suggestions from AI response."""
        suggestions = []
        current_test = {}
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('TEST:'):
                if current_test:
                    suggestions.append(self._format_test_suggestion(current_test))
                current_test = {"test": line[5:].strip()}
            elif line.startswith('INPUT:'):
                current_test["input"] = line[6:].strip()
            elif line.startswith('EXPECTED:'):
                current_test["expected"] = line[9:].strip()
            elif line.startswith('ASSERTION:'):
                current_test["assertion"] = line[10:].strip()
        
        if current_test:
            suggestions.append(self._format_test_suggestion(current_test))
        
        return suggestions or [response]  # Fallback to raw response
    
    def _format_test_suggestion(self, test_data: Dict) -> str:
        """Format a test suggestion into readable text."""
        parts = []
        if test_data.get("test"):
            parts.append(f"Test: {test_data['test']}")
        if test_data.get("input"):
            parts.append(f"Input: {test_data['input']}")
        if test_data.get("expected"):
            parts.append(f"Expected: {test_data['expected']}")
        if test_data.get("assertion"):
            parts.append(f"Assertion: {test_data['assertion']}")
        
        return " | ".join(parts)
    
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