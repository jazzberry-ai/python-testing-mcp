"""
Test file for example.py to demonstrate coverage functionality.
This provides partial coverage to show how the coverage tool works.
"""

import pytest
from example import (
    add_numbers, 
    divide_numbers, 
    find_max, 
    factorial, 
    process_string, 
    calculate_average,
    Calculator
)


class TestAddNumbers:
    """Test cases for add_numbers function."""
    
    def test_add_positive_numbers(self):
        """Test adding positive numbers."""
        assert add_numbers(2, 3) == 5
        assert add_numbers(10, 15) == 25
    
    def test_add_negative_numbers(self):
        """Test adding negative numbers."""
        assert add_numbers(-1, -2) == -3
        assert add_numbers(-5, 3) == -2


class TestDivideNumbers:
    """Test cases for divide_numbers function."""
    
    def test_divide_positive_numbers(self):
        """Test dividing positive numbers."""
        assert divide_numbers(10, 2) == 5.0
        assert divide_numbers(15, 3) == 5.0
    
    # Note: Missing test for division by zero - this leaves coverage gap


class TestFindMax:
    """Test cases for find_max function."""
    
    def test_find_max_positive_numbers(self):
        """Test finding max in positive numbers."""
        assert find_max([1, 2, 3, 4, 5]) == 5
        assert find_max([10, 5, 8, 3]) == 10
    
    def test_find_max_single_element(self):
        """Test finding max with single element."""
        assert find_max([42]) == 42
    
    # Note: Missing test for empty list - this leaves coverage gap


class TestFactorial:
    """Test cases for factorial function."""
    
    def test_factorial_positive_numbers(self):
        """Test factorial of positive numbers."""
        assert factorial(0) == 1
        assert factorial(1) == 1
        assert factorial(5) == 120
    
    # Note: Missing test for negative numbers - this leaves coverage gap


class TestProcessString:
    """Test cases for process_string function."""
    
    def test_process_string_basic(self):
        """Test basic string processing."""
        assert process_string("hello") == "hello"
        assert process_string("world", prefix="Hello ") == "Hello world"
    
    def test_process_string_uppercase(self):
        """Test string processing with uppercase."""
        assert process_string("hello", uppercase=True) == "HELLO"
    
    # Note: Missing test for non-string input - this leaves coverage gap


class TestCalculateAverage:
    """Test cases for calculate_average function."""
    
    def test_calculate_average_normal(self):
        """Test calculating average of normal numbers."""
        assert calculate_average([1, 2, 3, 4, 5]) == 3.0
        assert calculate_average([10, 20]) == 15.0
    
    # Note: Missing test for empty list - this leaves coverage gap


class TestCalculator:
    """Test cases for Calculator class."""
    
    def test_calculator_init(self):
        """Test calculator initialization."""
        calc = Calculator()
        assert calc.value == 0
        
        calc_with_value = Calculator(10)
        assert calc_with_value.value == 10
    
    def test_calculator_add(self):
        """Test calculator add method."""
        calc = Calculator(5)
        result = calc.add(3)
        assert result == 8
        assert calc.value == 8
    
    # Note: Missing tests for multiply and reset methods - this leaves coverage gaps


if __name__ == "__main__":
    pytest.main([__file__, "-v"])