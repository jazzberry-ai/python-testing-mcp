"""
Gemini API client for generating fuzzing inputs.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai


class GeminiClient:
    """Client for interacting with Google's Gemini API to generate fuzzing inputs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini client.
        
        Args:
            api_key: Google API key. If not provided, will look for GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY env var or pass api_key.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _parse_json_tolerant(self, text: str) -> List[Dict[str, Any]]:
        """Error-tolerant JSON parser inspired by BAML techniques.
        
        Handles common LLM JSON formatting issues:
        - Trailing commas
        - Unquoted keys
        - Missing quotes around strings
        - Extra markdown formatting
        - Newlines in strings
        - Missing commas between objects
        """
        # Step 1: Extract JSON from markdown if present
        if '```json' in text.lower():
            start_marker = text.lower().find('```json')
            start = text.find('\n', start_marker) + 1
            if start == 0:
                start = start_marker + 7
            end = text.find('```', start)
            if end == -1:
                end = len(text)
            json_text = text[start:end].strip()
        elif '```' in text and '[' in text:
            start = text.find('[')
            end = text.rfind(']') + 1
            json_text = text[start:end]
        elif '[' in text and ']' in text:
            start = text.find('[')
            end = text.rfind(']') + 1
            json_text = text[start:end]
        else:
            json_text = text.strip()
        
        # Step 2: Apply error corrections
        corrected_text = self._apply_json_corrections(json_text)
        
        # Step 3: Try parsing with standard library
        try:
            return json.loads(corrected_text)
        except json.JSONDecodeError as e:
            # Step 4: Try more aggressive corrections
            aggressively_corrected = self._aggressive_json_corrections(corrected_text)
            try:
                return json.loads(aggressively_corrected)
            except json.JSONDecodeError:
                # Step 5: Last resort - extract individual objects
                return self._extract_json_objects(json_text)
    
    def _apply_json_corrections(self, text: str) -> str:
        """Apply basic JSON corrections for common LLM issues."""
        # Remove trailing commas before closing brackets/braces
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Fix unquoted keys (simple cases)
        text = re.sub(r'(\w+)(\s*:)', r'"\1"\2', text)
        
        # Fix single quotes to double quotes
        text = text.replace("'", '"')
        
        # Fix common boolean/null values
        text = re.sub(r'\btrue\b', 'true', text, flags=re.IGNORECASE)
        text = re.sub(r'\bfalse\b', 'false', text, flags=re.IGNORECASE)
        text = re.sub(r'\bnull\b', 'null', text, flags=re.IGNORECASE)
        
        # Handle Python-style values that aren't JSON
        text = re.sub(r'\bNone\b', 'null', text)
        text = re.sub(r'\bTrue\b', 'true', text)
        text = re.sub(r'\bFalse\b', 'false', text)
        
        return text
    
    def _aggressive_json_corrections(self, text: str) -> str:
        """Apply more aggressive corrections for severely malformed JSON."""
        # Try to fix missing commas between objects
        text = re.sub(r'}(\s*){\s*"', r'},\1{"', text)
        
        # Fix missing commas between array elements
        text = re.sub(r'}(\s*){', r'},\1{', text)
        
        # Remove any non-JSON text before first [ or {
        match = re.search(r'[{\[]', text)
        if match:
            text = text[match.start():]
        
        # Remove any non-JSON text after last ] or }
        for i in range(len(text) - 1, -1, -1):
            if text[i] in ']}':
                text = text[:i + 1]
                break
        
        return text
    
    def _extract_json_objects(self, text: str) -> List[Dict[str, Any]]:
        """Extract individual JSON objects as fallback."""
        objects = []
        
        # Try to find individual object patterns
        pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(pattern, text)
        
        for match in matches:
            try:
                corrected = self._apply_json_corrections(match)
                obj = json.loads(corrected)
                objects.append(obj)
            except:
                continue
        
        return objects
    
    def generate_fuzzing_inputs(self, function_signature: str, function_code: str, num_inputs: int = 10) -> List[Dict[str, Any]]:
        """Generate fuzzing inputs for a Python function.
        
        Args:
            function_signature: The function signature to analyze
            function_code: The complete function code
            num_inputs: Number of test inputs to generate
            
        Returns:
            List of dictionaries containing test inputs and expected behavior
        """
        prompt = f"""
        Analyze this Python function and generate {num_inputs} diverse fuzzing test inputs.
        Focus on edge cases, boundary conditions, and potential error conditions.

        Function signature: {function_signature}
        Function code:
        ```python
        {function_code}
        ```

        Generate test inputs that cover:
        1. Normal valid inputs
        2. Edge cases (empty, null, boundary values)
        3. Invalid inputs that might cause errors
        4. Large inputs that might cause performance issues
        5. Unusual data types or formats

        Return the inputs as a JSON array where each item has:
        - "args": list of positional arguments
        - "kwargs": dictionary of keyword arguments
        - "description": brief description of what this test case covers
        - "expected_behavior": "normal", "error", or "edge_case"

        IMPORTANT: Use only valid JSON values. For special values use:
        - For infinity: use string "infinity" not float('inf')
        - For None/null: use null
        - For very large numbers: use regular integers like 999999999
        - Use only standard JSON types: string, number, boolean, null, array, object

        Example format:
        [
            {{
                "args": [1, 2],
                "kwargs": {{}},
                "description": "Normal positive integers",
                "expected_behavior": "normal"
            }},
            {{
                "args": [null],
                "kwargs": {{}},
                "description": "Null input test",
                "expected_behavior": "error"
            }}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Use error-tolerant JSON parser
            inputs = self._parse_json_tolerant(response.text)
            return inputs
            
        except Exception as e:
            print(f"Error generating fuzzing inputs: {e}")
            print(f"Raw response (first 500 chars): {response.text[:500]}...")
            return []
    
    def analyze_crash(self, function_code: str, error_info: str, test_input: Dict[str, Any]) -> str:
        """Analyze a crash and provide insights.
        
        Args:
            function_code: The function that crashed
            error_info: Error message and traceback
            test_input: The input that caused the crash
            
        Returns:
            Analysis of the crash and potential fixes
        """
        prompt = f"""
        Analyze this Python function crash and provide insights:

        Function code:
        ```python
        {function_code}
        ```

        Error:
        {error_info}

        Test input that caused the crash:
        {json.dumps(test_input, indent=2)}

        Provide:
        1. Root cause analysis
        2. Severity assessment (low/medium/high/critical)
        3. Suggested fix
        4. Additional test cases to prevent similar issues
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: Failed to analyze crash using Gemini API: {e}"
