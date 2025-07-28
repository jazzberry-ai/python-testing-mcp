#!/usr/bin/env python3
"""
Python Fuzzing Tool - Command Line Interface

A basic fuzzing tool that uses Gemini to generate test inputs for Python functions.
"""

import argparse
import os
import sys
from pathlib import Path

from fuzzer.fuzzer import PythonFuzzer


def print_summary(reports):
    """Print a summary of the fuzzing results."""
    print("\n" + "="*60)
    print("FUZZING SUMMARY")
    print("="*60)
    
    total_functions = len(reports)
    total_tests = sum(report.total_tests for report in reports)
    total_crashes = sum(len(report.crashes) for report in reports)
    total_successful = sum(report.successful_tests for report in reports)
    
    print(f"Functions tested: {total_functions}")
    print(f"Total test cases: {total_tests}")
    print(f"Successful tests: {total_successful}")
    print(f"Total crashes: {total_crashes}")
    
    if total_tests > 0:
        success_rate = (total_successful / total_tests) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    print("\nPer-function results:")
    for report in reports:
        status = "✓" if len(report.crashes) == 0 else "✗"
        print(f"  {status} {report.function_name}: {report.successful_tests}/{report.total_tests} passed, {len(report.crashes)} crashes")
    
    if total_crashes > 0:
        print(f"\n⚠️  Found {total_crashes} crashes that need investigation!")


def main():
    parser = argparse.ArgumentParser(
        description="Python Fuzzing Tool using Gemini for test input generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s example.py                    # Fuzz all functions in example.py
  %(prog)s example.py -n 20              # Generate 20 test cases per function
  %(prog)s example.py -o report.json     # Save detailed report to file
  %(prog)s example.py -f calculate       # Fuzz only the 'calculate' function

Environment Variables:
  GEMINI_API_KEY    Your Google Gemini API key (required)
        """
    )
    
    parser.add_argument(
        "file",
        help="Python file to fuzz (.py)"
    )
    
    parser.add_argument(
        "-n", "--num-tests",
        type=int,
        default=10,
        help="Number of test cases to generate per function (default: 10)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file for detailed JSON report"
    )
    
    parser.add_argument(
        "-f", "--function",
        help="Specific function name to fuzz (default: all functions)"
    )
    
    parser.add_argument(
        "--api-key",
        help="Gemini API key (can also use GEMINI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    if not args.file.endswith('.py'):
        print(f"Error: File must be a Python file (.py)")
        sys.exit(1)
    
    # Check for API key
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: Gemini API key required.")
        print("Set GEMINI_API_KEY environment variable or use --api-key option")
        print("\nTo get an API key:")
        print("1. Visit https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Set it as an environment variable: export GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    try:
        # Initialize fuzzer
        print(f"Initializing fuzzer for: {args.file}")
        fuzzer = PythonFuzzer(api_key)
        
        if args.function:
            # Fuzz specific function
            fuzzer.load_target_file(args.file)
            functions = fuzzer.analyzer.extract_functions()
            
            target_func = None
            for func in functions:
                if func.name == args.function:
                    target_func = func
                    break
            
            if not target_func:
                print(f"Error: Function '{args.function}' not found in {args.file}")
                available_functions = [f.name for f in functions]
                print(f"Available functions: {', '.join(available_functions)}")
                sys.exit(1)
            
            print(f"Fuzzing function: {args.function}")
            report = fuzzer.fuzz_function(target_func, args.num_tests)
            reports = [report]
        else:
            # Fuzz all functions
            print("Fuzzing all functions...")
            reports = fuzzer.fuzz_all_functions(args.file, args.num_tests)
        
        # Print summary
        print_summary(reports)
        
        # Save detailed report if requested
        if args.output:
            fuzzer.save_report(reports, args.output)
        
        # Exit with error code if crashes were found
        total_crashes = sum(len(report.crashes) for report in reports)
        if total_crashes > 0:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nFuzzing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
