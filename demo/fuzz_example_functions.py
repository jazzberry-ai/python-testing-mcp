import sys
import os
import traceback

# Add the demo directory to Python path to import example_functions
sys.path.insert(0, os.path.dirname(__file__))
from basic_example_functions import add, subtract

def fuzz_test_add():
    """Fuzz test the add function with diverse inputs."""
    print("Fuzz testing add() function...")
    
    # Test cases with various edge cases and challenging inputs
    test_cases = [
        # Normal cases
        (1, 2),
        (0, 0),
        (-1, 1),
        
        # Large numbers
        (1000000, 2000000),
        (-1000000, -2000000),
        
        # Float precision edge cases
        (0.1, 0.2),
        (1e10, 1e-10),
        (float('inf'), 1),
        (float('-inf'), 1),
        (float('inf'), float('-inf')),
        
        # Special float values
        (float('nan'), 1),
        (1, float('nan')),
        (float('nan'), float('nan')),
        
        # Type mixing
        (1, 1.5),
        (True, False),
        (True, 1),
        
        # String concatenation (if supported)
        ("hello", "world"),
        ("", "test"),
        
        # List concatenation (if supported)
        ([1, 2], [3, 4]),
        ([], [1, 2, 3]),
        
        # None values
        (None, 1),
        (1, None),
        (None, None),
        
        # Complex numbers
        (1+2j, 3+4j),
        (complex(1, 2), 5),
    ]
    
    crashes = []
    passed = 0
    
    for i, (a, b) in enumerate(test_cases):
        try:
            result = add(a, b)
            print(f"Test {i+1}: add({a}, {b}) = {result}")
            passed += 1
        except Exception as e:
            error_info = {
                "test_case": i+1,
                "input": (a, b),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            crashes.append(error_info)
            print(f"Test {i+1}: add({a}, {b}) CRASHED: {e}")
    
    print(f"\nFuzz test results for add(): {passed} passed, {len(crashes)} crashed")
    return crashes

def fuzz_test_subtract():
    """Fuzz test the subtract function with diverse inputs."""
    print("\nFuzz testing subtract() function...")
    
    # Test cases with various edge cases and challenging inputs
    test_cases = [
        # Normal cases
        (5, 3),
        (0, 0),
        (-1, 1),
        (1, -1),
        
        # Large numbers
        (3000000, 1000000),
        (-1000000, -2000000),
        
        # Float precision edge cases
        (0.3, 0.1),
        (1e10, 1e-10),
        (float('inf'), 1),
        (float('-inf'), 1),
        (float('inf'), float('inf')),
        (float('-inf'), float('-inf')),
        
        # Special float values
        (float('nan'), 1),
        (1, float('nan')),
        (float('nan'), float('nan')),
        
        # Type mixing
        (5, 2.5),
        (True, False),
        (False, True),
        
        # String operations (might cause errors)
        ("hello", "world"),
        ("test", ""),
        
        # List operations (might cause errors)
        ([1, 2, 3], [1]),
        ([5, 4, 3], [1, 2]),
        
        # None values
        (None, 1),
        (1, None),
        (None, None),
        
        # Complex numbers
        (5+6j, 1+2j),
        (complex(5, 3), 2),
    ]
    
    crashes = []
    passed = 0
    
    for i, (a, b) in enumerate(test_cases):
        try:
            result = subtract(a, b)
            print(f"Test {i+1}: subtract({a}, {b}) = {result}")
            passed += 1
        except Exception as e:
            error_info = {
                "test_case": i+1,
                "input": (a, b),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            crashes.append(error_info)
            print(f"Test {i+1}: subtract({a}, {b}) CRASHED: {e}")
    
    print(f"\nFuzz test results for subtract(): {passed} passed, {len(crashes)} crashed")
    return crashes

def generate_fuzz_report(add_crashes, subtract_crashes):
    """Generate a comprehensive fuzz testing report."""
    total_tests = 50  # 25 tests per function
    total_crashes = len(add_crashes) + len(subtract_crashes)
    
    print(f"\n{'='*60}")
    print("FUZZ TESTING SUMMARY REPORT")
    print(f"{'='*60}")
    print(f"Total tests run: {total_tests}")
    print(f"Total crashes found: {total_crashes}")
    print(f"Success rate: {((total_tests - total_crashes) / total_tests * 100):.1f}%")
    
    if add_crashes:
        print(f"\nADD FUNCTION CRASHES ({len(add_crashes)}):")
        for crash in add_crashes:
            print(f"  - Test {crash['test_case']}: {crash['input']} -> {crash['error']}")
    
    if subtract_crashes:
        print(f"\nSUBTRACT FUNCTION CRASHES ({len(subtract_crashes)}):")
        for crash in subtract_crashes:
            print(f"  - Test {crash['test_case']}: {crash['input']} -> {crash['error']}")
    
    if not add_crashes and not subtract_crashes:
        print("\n✅ No crashes found! Both functions handled all test cases gracefully.")
    else:
        print(f"\n⚠️  Found {total_crashes} potential issues that should be investigated.")

if __name__ == "__main__":
    print("Starting comprehensive fuzz testing for example_functions.py")
    print("="*60)
    
    # Run fuzz tests
    add_crashes = fuzz_test_add()
    subtract_crashes = fuzz_test_subtract()
    
    # Generate report
    generate_fuzz_report(add_crashes, subtract_crashes)