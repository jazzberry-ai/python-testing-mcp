#!/usr/bin/env python3
"""
Local fuzzing test for example.py that doesn't require API connectivity.
This demonstrates basic fuzzing capabilities without external dependencies.
"""

import sys
import traceback
from example import add_numbers, divide_numbers, find_max, factorial, process_string, calculate_average, Calculator

def test_add_numbers():
    """Test add_numbers with various inputs."""
    test_cases = [
        (1, 2),
        (0, 0),
        (-5, 5),
        (1.5, 2.5),
        (float('inf'), 1),
        (-float('inf'), float('inf')),
        (1e308, 1e308),  # Large numbers
    ]
    
    results = []
    for args in test_cases:
        try:
            result = add_numbers(*args)
            results.append(f"✅ add_numbers{args} = {result}")
        except Exception as e:
            results.append(f"❌ add_numbers{args} failed: {type(e).__name__}: {e}")
    
    return results

def test_divide_numbers():
    """Test divide_numbers with various inputs."""
    test_cases = [
        (10, 2),
        (1, 3),
        (0, 1),
        (1, 0),  # Division by zero
        (-10, -2),
        (float('inf'), 2),
        (1, float('inf')),
    ]
    
    results = []
    for args in test_cases:
        try:
            result = divide_numbers(*args)
            results.append(f"✅ divide_numbers{args} = {result}")
        except Exception as e:
            results.append(f"❌ divide_numbers{args} failed: {type(e).__name__}: {e}")
    
    return results

def test_find_max():
    """Test find_max with various inputs."""
    test_cases = [
        ([1, 2, 3]),
        ([]),  # Empty list
        ([-1, -2, -3]),
        ([0]),
        ([1.5, 2.7, 0.1]),
        ([float('inf'), 1, 2]),
        (None,),  # Invalid input type
    ]
    
    results = []
    for args in test_cases:
        try:
            result = find_max(*args) if args != (None,) else find_max(None)
            results.append(f"✅ find_max{args} = {result}")
        except Exception as e:
            results.append(f"❌ find_max{args} failed: {type(e).__name__}: {e}")
    
    return results

def test_factorial():
    """Test factorial with various inputs."""
    test_cases = [
        (5,),
        (0,),
        (1,),
        (-1,),  # Negative number
        (20,),  # Large number
        (1.5,),  # Float
        ("5",),  # String
    ]
    
    results = []
    for args in test_cases:
        try:
            result = factorial(*args)
            results.append(f"✅ factorial{args} = {result}")
        except Exception as e:
            results.append(f"❌ factorial{args} failed: {type(e).__name__}: {e}")
    
    return results

def test_process_string():
    """Test process_string with various inputs."""
    test_cases = [
        ("hello",),
        ("hello", True),
        ("hello", False, "PREFIX: "),
        ("", True, "Empty: "),
        (None,),  # Invalid type
        (123,),  # Invalid type
        ("unicode: 🚀",),
    ]
    
    results = []
    for args in test_cases:
        try:
            if len(args) == 1:
                result = process_string(args[0])
            elif len(args) == 2:
                result = process_string(args[0], args[1])
            else:
                result = process_string(args[0], args[1], args[2])
            results.append(f"✅ process_string{args} = '{result}'")
        except Exception as e:
            results.append(f"❌ process_string{args} failed: {type(e).__name__}: {e}")
    
    return results

def test_calculate_average():
    """Test calculate_average with various inputs."""
    test_cases = [
        ([1, 2, 3]),
        ([]),  # Empty list
        ([0]),
        ([-1, 1]),
        ([1.5, 2.5, 3.5]),
        ([float('inf')]),
        (None,),  # Invalid type
    ]
    
    results = []
    for args in test_cases:
        try:
            result = calculate_average(*args) if args != (None,) else calculate_average(None)
            results.append(f"✅ calculate_average{args} = {result}")
        except Exception as e:
            results.append(f"❌ calculate_average{args} failed: {type(e).__name__}: {e}")
    
    return results

def test_calculator_class():
    """Test Calculator class with various inputs."""
    results = []
    
    try:
        # Test initialization
        calc = Calculator()
        results.append(f"✅ Calculator() created with value: {calc.value}")
        
        calc2 = Calculator(10)
        results.append(f"✅ Calculator(10) created with value: {calc2.value}")
        
        # Test methods
        test_operations = [
            ('add', 5),
            ('add', -3),
            ('multiply', 2),
            ('multiply', 0),
            ('reset', None),
            ('add', float('inf')),
        ]
        
        for op, value in test_operations:
            try:
                if op == 'reset':
                    result = calc.reset()
                elif op == 'add':
                    result = calc.add(value)
                elif op == 'multiply':
                    result = calc.multiply(value)
                results.append(f"✅ calc.{op}({value if value is not None else ''}) = {result}")
            except Exception as e:
                results.append(f"❌ calc.{op}({value if value is not None else ''}) failed: {type(e).__name__}: {e}")
                
    except Exception as e:
        results.append(f"❌ Calculator class test failed: {type(e).__name__}: {e}")
    
    return results

def main():
    """Run all fuzz tests."""
    print("🔍 Local Fuzzing Test Results for example.py")
    print("=" * 50)
    
    test_functions = [
        ("add_numbers", test_add_numbers),
        ("divide_numbers", test_divide_numbers),
        ("find_max", test_find_max),
        ("factorial", test_factorial),
        ("process_string", test_process_string),
        ("calculate_average", test_calculate_average),
        ("Calculator class", test_calculator_class),
    ]
    
    total_tests = 0
    total_failures = 0
    
    for func_name, test_func in test_functions:
        print(f"\n📋 Testing {func_name}:")
        print("-" * 30)
        
        results = test_func()
        func_tests = len(results)
        func_failures = len([r for r in results if r.startswith("❌")])
        
        total_tests += func_tests
        total_failures += func_failures
        
        for result in results:
            print(f"  {result}")
        
        print(f"  📊 {func_tests - func_failures}/{func_tests} tests passed")
    
    print(f"\n🎯 Summary:")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_tests - total_failures}")
    print(f"Failed: {total_failures}")
    print(f"Success rate: {((total_tests - total_failures) / total_tests * 100):.1f}%")
    
    if total_failures > 0:
        print(f"\n⚠️  Found {total_failures} potential issues that may need investigation!")
    else:
        print(f"\n✅ All tests passed!")

if __name__ == "__main__":
    main()