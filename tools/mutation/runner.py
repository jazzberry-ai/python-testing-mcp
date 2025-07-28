"""
Mutation Test Runner

Executes tests against mutants and collects results.
Ensures safe execution with timeouts and proper cleanup.
"""

import os
import sys
import subprocess
import time
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .mutator import Mutant


class MutationStatus(Enum):
    """Status of a mutant after testing."""
    KILLED = "killed"          # Test failed, mutant was detected
    SURVIVED = "survived"      # Test passed, mutant was not detected
    TIMEOUT = "timeout"        # Test took too long
    ERROR = "error"           # Test execution error


@dataclass
class MutationResult:
    """Result of testing a single mutant."""
    mutant_id: str
    status: MutationStatus
    execution_time_ms: int
    test_output: str
    failing_tests: List[str]
    error_message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mutant_id": self.mutant_id,
            "status": self.status.value,
            "execution_time_ms": self.execution_time_ms,
            "test_output": self.test_output,
            "failing_tests": self.failing_tests,
            "error_message": self.error_message
        }


@dataclass
class MutationTestReport:
    """Complete mutation testing report."""
    file_path: str
    total_mutants: int
    results: List[MutationResult]
    execution_time_ms: int
    
    @property
    def killed_mutants(self) -> int:
        return len([r for r in self.results if r.status == MutationStatus.KILLED])
    
    @property
    def survived_mutants(self) -> int:
        return len([r for r in self.results if r.status == MutationStatus.SURVIVED])
    
    @property
    def timeout_mutants(self) -> int:
        return len([r for r in self.results if r.status == MutationStatus.TIMEOUT])
    
    @property
    def error_mutants(self) -> int:
        return len([r for r in self.results if r.status == MutationStatus.ERROR])
    
    @property
    def mutation_score(self) -> float:
        """Calculate mutation score (percentage of killed mutants)."""
        if self.total_mutants == 0:
            return 0.0
        
        # Only count killed and survived mutants for score calculation
        # (timeouts and errors are excluded from the standard score)
        valid_mutants = self.killed_mutants + self.survived_mutants
        if valid_mutants == 0:
            return 0.0
        
        return (self.killed_mutants / valid_mutants) * 100.0
    
    def get_function_scores(self) -> Dict[str, float]:
        """Get mutation scores by function."""
        function_results = {}
        
        # Group results by function (need to get this from mutants)
        # This would require access to the original mutants
        # For now, return empty dict - can be enhanced later
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "file_path": self.file_path,
            "total_mutants": self.total_mutants,
            "killed_mutants": self.killed_mutants,
            "survived_mutants": self.survived_mutants,
            "timeout_mutants": self.timeout_mutants,
            "error_mutants": self.error_mutants,
            "mutation_score": self.mutation_score,
            "execution_time_ms": self.execution_time_ms,
            "results": [r.to_dict() for r in self.results]
        }


class MutationTestRunner:
    """
    Runs tests against mutants and collects results.
    
    This runner:
    1. Sets up isolated test environments for each mutant
    2. Executes tests with proper timeouts
    3. Collects and analyzes test results
    4. Ensures complete cleanup after testing
    """
    
    def __init__(self, test_command: str = "python -m pytest", timeout_seconds: int = 30):
        """
        Initialize the mutation test runner.
        
        Args:
            test_command: Command to run tests (e.g., "python -m pytest", "python -m unittest")
            timeout_seconds: Maximum time to wait for each test run
        """
        self.test_command = test_command
        self.timeout_seconds = timeout_seconds
    
    def run_mutation_tests(
        self, 
        mutants: List[Mutant], 
        original_file_path: str,
        test_file_pattern: Optional[str] = None
    ) -> MutationTestReport:
        """
        Run tests against all mutants and generate a comprehensive report.
        
        Args:
            mutants: List of mutants to test
            original_file_path: Path to the original source file
            test_file_pattern: Optional pattern to find test files
            
        Returns:
            Complete mutation testing report
        """
        start_time = time.time()
        results = []
        
        # Discover test files if not specified
        test_files = self._discover_test_files(original_file_path, test_file_pattern)
        
        if not test_files:
            # Create a dummy result indicating no tests found
            dummy_result = MutationResult(
                mutant_id="no_tests",
                status=MutationStatus.ERROR,
                execution_time_ms=0,
                test_output="No test files found",
                failing_tests=[],
                error_message="No test files found for mutation testing"
            )
            results.append(dummy_result)
        else:
            # Test each mutant
            for i, mutant in enumerate(mutants):
                print(f"Testing mutant {i+1}/{len(mutants)}: {mutant.id}")
                result = self._test_single_mutant(mutant, original_file_path, test_files)
                results.append(result)
        
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        return MutationTestReport(
            file_path=original_file_path,
            total_mutants=len(mutants),
            results=results,
            execution_time_ms=execution_time_ms
        )
    
    def _test_single_mutant(
        self, 
        mutant: Mutant, 
        original_file_path: str, 
        test_files: List[str]
    ) -> MutationResult:
        """Test a single mutant against the test suite."""
        start_time = time.time()
        
        try:
            # Create isolated test environment
            with self._create_test_environment(mutant, original_file_path) as env_info:
                test_dir, mutant_file_path = env_info
                
                # Run tests
                result = self._execute_tests(test_dir, test_files, mutant.id)
                
                end_time = time.time()
                execution_time_ms = int((end_time - start_time) * 1000)
                
                return MutationResult(
                    mutant_id=mutant.id,
                    status=result["status"],
                    execution_time_ms=execution_time_ms,
                    test_output=result["output"],
                    failing_tests=result["failing_tests"],
                    error_message=result["error_message"]
                )
        
        except Exception as e:
            end_time = time.time()
            execution_time_ms = int((end_time - start_time) * 1000)
            
            return MutationResult(
                mutant_id=mutant.id,
                status=MutationStatus.ERROR,
                execution_time_ms=execution_time_ms,
                test_output="",
                failing_tests=[],
                error_message=f"Test execution error: {str(e)}"
            )
    
    def _create_test_environment(self, mutant: Mutant, original_file_path: str):
        """Create an isolated test environment for the mutant."""
        class TestEnvironment:
            def __init__(self, runner, mutant, original_file_path):
                self.runner = runner
                self.mutant = mutant
                self.original_file_path = original_file_path
                self.test_dir = None
                self.mutant_file_path = None
            
            def __enter__(self):
                # Create temporary directory for testing
                self.test_dir = tempfile.mkdtemp(prefix="mutation_test_env_")
                
                # Copy the mutant file to the test directory with the original name
                original_name = os.path.basename(self.original_file_path)
                self.mutant_file_path = os.path.join(self.test_dir, original_name)
                
                # Copy mutant code to the new location
                if self.mutant.temp_file_path and os.path.exists(self.mutant.temp_file_path):
                    shutil.copy2(self.mutant.temp_file_path, self.mutant_file_path)
                else:
                    # Fallback: create file with mutated code
                    with open(self.mutant_file_path, 'w', encoding='utf-8') as f:
                        f.write(self.mutant.mutated_code)
                
                return self.test_dir, self.mutant_file_path
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Clean up test environment
                if self.test_dir and os.path.exists(self.test_dir):
                    try:
                        shutil.rmtree(self.test_dir)
                    except Exception as e:
                        print(f"Warning: Could not remove test directory {self.test_dir}: {e}")
        
        return TestEnvironment(self, mutant, original_file_path)
    
    def _execute_tests(self, test_dir: str, test_files: List[str], mutant_id: str) -> Dict[str, Any]:
        """Execute tests in the isolated environment."""
        try:
            # Copy test files to the test directory
            for test_file in test_files:
                if os.path.exists(test_file):
                    dest_path = os.path.join(test_dir, os.path.basename(test_file))
                    shutil.copy2(test_file, dest_path)
            
            # Change to test directory and run tests
            original_cwd = os.getcwd()
            os.chdir(test_dir)
            
            try:
                # Execute test command
                cmd = self.test_command.split()
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    cwd=test_dir
                )
                
                # Analyze results
                output = process.stdout + process.stderr
                return_code = process.returncode
                
                # Determine status based on return code
                if return_code == 0:
                    status = MutationStatus.SURVIVED  # Tests passed, mutant survived
                else:
                    status = MutationStatus.KILLED     # Tests failed, mutant was killed
                
                # Extract failing test names (this is test framework specific)
                failing_tests = self._extract_failing_tests(output)
                
                return {
                    "status": status,
                    "output": output,
                    "failing_tests": failing_tests,
                    "error_message": ""
                }
            
            finally:
                os.chdir(original_cwd)
        
        except subprocess.TimeoutExpired:
            return {
                "status": MutationStatus.TIMEOUT,
                "output": "Test execution timed out",
                "failing_tests": [],
                "error_message": f"Test execution exceeded {self.timeout_seconds} seconds"
            }
        
        except Exception as e:
            return {
                "status": MutationStatus.ERROR,
                "output": "",
                "failing_tests": [],
                "error_message": str(e)
            }
    
    def _discover_test_files(self, source_file_path: str, pattern: Optional[str] = None) -> List[str]:
        """Discover test files related to the source file."""
        source_dir = os.path.dirname(source_file_path)
        source_name = os.path.splitext(os.path.basename(source_file_path))[0]
        
        test_files = []
        
        # Common test file patterns
        patterns = [
            f"test_{source_name}.py",
            f"{source_name}_test.py",
            f"test*.py" if pattern is None else pattern
        ]
        
        # Search in the same directory and common test directories
        search_dirs = [
            source_dir,
            os.path.join(source_dir, "tests"),
            os.path.join(source_dir, "test"),
            os.path.join(os.path.dirname(source_dir), "tests"),
            os.path.join(os.path.dirname(source_dir), "test"),
        ]
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            for pattern in patterns:
                if "*" in pattern:
                    # Use glob for wildcard patterns
                    import glob
                    matches = glob.glob(os.path.join(search_dir, pattern))
                    test_files.extend(matches)
                else:
                    # Direct file check
                    test_file = os.path.join(search_dir, pattern)
                    if os.path.exists(test_file):
                        test_files.append(test_file)
        
        # Remove duplicates and return
        return list(set(test_files))
    
    def _extract_failing_tests(self, test_output: str) -> List[str]:
        """Extract names of failing tests from test output."""
        failing_tests = []
        
        # This is a simplified implementation that works with common test frameworks
        # Could be enhanced to better parse specific test framework outputs
        
        lines = test_output.split('\n')
        for line in lines:
            line = line.strip()
            
            # Common patterns for failing tests
            if "FAILED " in line:
                # Extract test name after "FAILED "
                parts = line.split("FAILED ")
                if len(parts) > 1:
                    test_name = parts[1].split()[0]
                    failing_tests.append(test_name)
            elif "FAIL: " in line:
                # Unittest format
                parts = line.split("FAIL: ")
                if len(parts) > 1:
                    test_name = parts[1].strip()
                    failing_tests.append(test_name)
        
        return failing_tests