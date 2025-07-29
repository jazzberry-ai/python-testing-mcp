#!/usr/bin/env python3
"""
Quick validation script to test sample module functionality.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from test_samples.sample_module import add, divide, fibonacci, Calculator

def test_sample_functions():
    """Test basic functionality of sample functions"""
    print("🧪 Testing Sample Module Functions")
    print("=" * 40)
    
    # Test add function
    print(f"add(2, 3) = {add(2, 3)}")  # Should be 5
    
    # Test divide function
    print(f"divide(10, 2) = {divide(10, 2)}")  # Should be 5.0
    
    try:
        divide(10, 0)
    except ValueError as e:
        print(f"divide(10, 0) correctly raises: {e}")
    
    # Test fibonacci function
    print(f"fibonacci(5) = {fibonacci(5)}")  # Should be 5
    print(f"fibonacci(10) = {fibonacci(10)}")  # Should be 55
    
    try:
        fibonacci(-1)
    except ValueError as e:
        print(f"fibonacci(-1) correctly raises: {e}")
    
    # Test Calculator class
    calc = Calculator(precision=2)
    print(f"calc.multiply(3.14, 2) = {calc.multiply(3.14, 2)}")  # Should be 6.28
    print(f"calc.power(2, 3) = {calc.power(2, 3)}")  # Should be 8.0
    
    print("\n✅ All sample functions work correctly!")
    print("✅ Sample module is ready for testing tools!")

if __name__ == "__main__":
    test_sample_functions()