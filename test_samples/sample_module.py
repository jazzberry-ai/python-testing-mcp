"""
Sample Python module for testing the Software Testing Agent tools.

This module contains various function types and patterns commonly found in Python codebases,
designed to test different aspects of the testing tools:
- Simple functions
- Functions with edge cases
- Functions with error conditions
- Class methods
- Complex logic patterns
"""

import math
from typing import List, Optional, Dict, Any


def add(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b


def divide(x: float, y: float) -> float:
    """Divide x by y with error handling.
    
    Args:
        x: Numerator
        y: Denominator
        
    Returns:
        Result of x / y
        
    Raises:
        ValueError: If y is zero
        TypeError: If inputs are not numeric
    """
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise TypeError("Inputs must be numeric")
    
    if y == 0:
        raise ValueError("Cannot divide by zero")
    
    return x / y


def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.
    
    Args:
        n: Position in Fibonacci sequence (0-indexed)
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b


def process_list(items: List[Any], operation: str = "sum") -> Any:
    """Process a list of items with the specified operation.
    
    Args:
        items: List of items to process
        operation: Operation to perform ("sum", "max", "min", "avg")
        
    Returns:
        Result of the operation
        
    Raises:
        ValueError: If operation is not supported or list is empty
    """
    if not items:
        raise ValueError("Cannot process empty list")
    
    if operation == "sum":
        return sum(items)
    elif operation == "max":
        return max(items)
    elif operation == "min":
        return min(items)
    elif operation == "avg":
        return sum(items) / len(items)
    else:
        raise ValueError(f"Unsupported operation: {operation}")


def find_prime_factors(n: int) -> List[int]:
    """Find all prime factors of a number.
    
    Args:
        n: Number to factorize
        
    Returns:
        List of prime factors in ascending order
        
    Raises:
        ValueError: If n is less than 2
    """
    if n < 2:
        raise ValueError("Number must be >= 2")
    
    factors = []
    d = 2
    
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    
    if n > 1:
        factors.append(n)
    
    return factors


def validate_email(email: str) -> bool:
    """Simple email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email appears valid, False otherwise
    """
    if not isinstance(email, str):
        return False
    
    if "@" not in email:
        return False
    
    parts = email.split("@")
    if len(parts) != 2:
        return False
    
    local, domain = parts
    if not local or not domain:
        return False
    
    if "." not in domain:
        return False
    
    return True


class Calculator:
    """A simple calculator class for testing class method handling."""
    
    def __init__(self, precision: int = 2):
        """Initialize calculator with specified precision.
        
        Args:
            precision: Number of decimal places for results
        """
        self.precision = precision
        self.history = []
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b, rounded to precision
        """
        result = round(a * b, self.precision)
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """Calculate base raised to exponent.
        
        Args:
            base: Base number
            exponent: Exponent
            
        Returns:
            base ** exponent, rounded to precision
            
        Raises:
            ValueError: If result would be invalid (e.g., negative base with fractional exponent)
        """
        try:
            result = round(math.pow(base, exponent), self.precision)
            self.history.append(f"{base} ** {exponent} = {result}")
            return result
        except ValueError as e:
            raise ValueError(f"Invalid calculation: {e}")
    
    def get_history(self) -> List[str]:
        """Get calculation history.
        
        Returns:
            List of calculation strings
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()


class DataProcessor:
    """Data processing utilities for testing complex scenarios."""
    
    @staticmethod
    def filter_and_transform(data: List[Dict[str, Any]], 
                           filter_key: str, 
                           filter_value: Any,
                           transform_key: str,
                           transform_func: callable) -> List[Dict[str, Any]]:
        """Filter data by key-value pair and transform another key.
        
        Args:
            data: List of dictionaries to process
            filter_key: Key to filter on
            filter_value: Value to match for filtering
            transform_key: Key to transform
            transform_func: Function to apply to transform_key values
            
        Returns:
            Filtered and transformed data
            
        Raises:
            KeyError: If required keys are missing
            TypeError: If transform_func is not callable
        """
        if not callable(transform_func):
            raise TypeError("transform_func must be callable")
        
        result = []
        for item in data:
            if filter_key not in item:
                raise KeyError(f"Filter key '{filter_key}' not found in item")
            
            if item[filter_key] == filter_value:
                if transform_key not in item:
                    raise KeyError(f"Transform key '{transform_key}' not found in item")
                
                transformed_item = item.copy()
                transformed_item[transform_key] = transform_func(item[transform_key])
                result.append(transformed_item)
        
        return result
    
    @classmethod
    def aggregate_by_key(cls, data: List[Dict[str, Any]], 
                        group_key: str, 
                        value_key: str,
                        operation: str = "sum") -> Dict[str, float]:
        """Aggregate data by grouping key.
        
        Args:
            data: List of dictionaries to aggregate
            group_key: Key to group by
            value_key: Key containing values to aggregate
            operation: Aggregation operation ("sum", "avg", "count")
            
        Returns:
            Dictionary mapping group values to aggregated results
            
        Raises:
            ValueError: If operation is not supported
            KeyError: If required keys are missing
        """
        if operation not in ["sum", "avg", "count"]:
            raise ValueError(f"Unsupported operation: {operation}")
        
        groups = {}
        
        for item in data:
            if group_key not in item:
                raise KeyError(f"Group key '{group_key}' not found in item")
            
            group_value = item[group_key]
            
            if group_value not in groups:
                groups[group_value] = []
            
            if operation == "count":
                groups[group_value].append(1)
            else:
                if value_key not in item:
                    raise KeyError(f"Value key '{value_key}' not found in item")
                groups[group_value].append(item[value_key])
        
        # Calculate final aggregations
        result = {}
        for group, values in groups.items():
            if operation == "sum" or operation == "count":
                result[group] = sum(values)
            elif operation == "avg":
                result[group] = sum(values) / len(values)
        
        return result


def complex_algorithm(data: List[int], threshold: int = 10) -> Dict[str, Any]:
    """A complex algorithm that combines multiple operations.
    
    This function demonstrates complex logic patterns for testing:
    - Multiple conditional branches
    - Nested loops
    - Exception handling
    - Complex return types
    
    Args:
        data: List of integers to process
        threshold: Threshold value for processing decisions
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        ValueError: If data is empty or contains non-integers
    """
    if not data:
        raise ValueError("Data cannot be empty")
    
    if not all(isinstance(x, int) for x in data):
        raise ValueError("All data items must be integers")
    
    result = {
        "input_size": len(data),
        "threshold": threshold,
        "stats": {},
        "processed_items": [],
        "warnings": []
    }
    
    # Basic statistics
    result["stats"]["sum"] = sum(data)
    result["stats"]["avg"] = sum(data) / len(data)
    result["stats"]["min"] = min(data)
    result["stats"]["max"] = max(data)
    
    # Complex processing logic
    for i, value in enumerate(data):
        item_info = {
            "index": i,
            "value": value,
            "category": None,
            "processed_value": None
        }
        
        # Categorize values
        if value < 0:
            item_info["category"] = "negative"
            item_info["processed_value"] = abs(value)
        elif value == 0:
            item_info["category"] = "zero"
            item_info["processed_value"] = 1  # Special handling
            result["warnings"].append(f"Zero value at index {i} converted to 1")
        elif value < threshold:
            item_info["category"] = "low"
            item_info["processed_value"] = value * 2
        else:
            item_info["category"] = "high"
            item_info["processed_value"] = value // 2
        
        result["processed_items"].append(item_info)
    
    # Additional analysis
    categories = {}
    for item in result["processed_items"]:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "total_processed": 0}
        categories[cat]["count"] += 1
        categories[cat]["total_processed"] += item["processed_value"]
    
    result["category_analysis"] = categories
    
    return result