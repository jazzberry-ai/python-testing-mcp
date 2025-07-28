"""
Example Python file for testing the fuzzer.
Contains various functions with different complexity levels and potential edge cases.
"""

def add_numbers(a, b):
    """Add two numbers together."""
    return a + b


def divide_numbers(x, y):
    """Divide x by y."""
    return x / y


def find_max(numbers):
    """Find the maximum number in a list."""
    if not numbers:
        raise ValueError("List cannot be empty")
    return max(numbers)


def factorial(n):
    """Calculate factorial of n."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def process_string(text, uppercase=False, prefix=""):
    """Process a string with various options."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    result = prefix + text
    
    if uppercase:
        result = result.upper()
    
    return result


def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


class Calculator:
    """Simple calculator class."""
    
    def __init__(self, initial_value=0):
        self.value = initial_value
    
    def add(self, n):
        """Add n to the current value."""
        self.value += n
        return self.value
    
    def multiply(self, n):
        """Multiply current value by n."""
        self.value *= n
        return self.value
    
    def reset(self):
        """Reset value to 0."""
        self.value = 0
        return self.value
