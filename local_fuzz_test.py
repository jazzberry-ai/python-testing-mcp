#!/usr/bin/env python3
"""
Local fuzzing test for example.py that uses the PythonFuzzer.
"""

import os
from tools.fuzzer.fuzzer import PythonFuzzer


def main():
    """Run all fuzz tests."""
    print("🔍 Local Fuzzing Test Results for example.py")
    print("=" * 50)

    # Get the Gemini API key from the environment
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    # Create a PythonFuzzer instance
    fuzzer = PythonFuzzer(gemini_api_key=gemini_api_key)

    # Fuzz all the functions in the example.py file
    reports = fuzzer.fuzz_all_functions("example.py")

    # Print the reports
    for report in reports:
        print(report)


if __name__ == "__main__":
    main()
