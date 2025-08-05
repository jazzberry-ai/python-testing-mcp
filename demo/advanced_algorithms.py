"""
Advanced algorithmic implementations showcasing complex testing scenarios.
Demonstrates multiple code paths, edge cases, and error conditions.
"""
import math
from typing import List, Optional, Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class SortingStrategy(Enum):
    QUICKSORT = "quicksort"
    MERGESORT = "mergesort"
    HEAPSORT = "heapsort"


@dataclass
class SearchResult:
    found: bool
    index: Optional[int] = None
    comparisons: int = 0
    path_taken: List[int] = None
    
    def __post_init__(self):
        if self.path_taken is None:
            self.path_taken = []


def binary_search_with_analytics(arr: List[int], target: int, start: int = 0, end: Optional[int] = None) -> SearchResult:
    """
    Enhanced binary search with comprehensive analytics and edge case handling.
    
    Args:
        arr: Sorted list of integers to search
        target: Value to find
        start: Starting index for search
        end: Ending index for search (exclusive)
    
    Returns:
        SearchResult with detailed information about the search process
    
    Raises:
        ValueError: If array is not sorted or indices are invalid
        TypeError: If inputs are wrong type
    """
    if not isinstance(arr, list):
        raise TypeError("Array must be a list")
    
    if not arr:
        return SearchResult(found=False, comparisons=0)
    
    if not all(isinstance(x, (int, float)) for x in arr):
        raise TypeError("Array must contain only numbers")
    
    if end is None:
        end = len(arr)
    
    if start < 0 or end > len(arr) or start >= end:
        raise ValueError(f"Invalid indices: start={start}, end={end}, array_length={len(arr)}")
    
    # Verify array is sorted in the given range
    for i in range(start, end - 1):
        if arr[i] > arr[i + 1]:
            raise ValueError(f"Array not sorted at indices {i} and {i + 1}")
    
    result = SearchResult(found=False)
    left, right = start, end - 1
    
    while left <= right:
        result.comparisons += 1
        mid = left + (right - left) // 2  # Avoid overflow
        result.path_taken.append(mid)
        
        if arr[mid] == target:
            result.found = True
            result.index = mid
            return result
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result


def adaptive_quicksort(arr: List[int], strategy: SortingStrategy = SortingStrategy.QUICKSORT, 
                      threshold: int = 10) -> Tuple[List[int], Dict[str, Any]]:
    """
    Adaptive sorting algorithm that switches strategies based on input characteristics.
    
    Args:
        arr: List to sort
        strategy: Primary sorting strategy
        threshold: Threshold for switching to insertion sort
    
    Returns:
        Tuple of (sorted_array, statistics_dict)
    
    Raises:
        ValueError: For invalid inputs
        RecursionError: If recursion depth exceeded
    """
    if not isinstance(arr, list):
        raise TypeError("Input must be a list")
    
    if not arr:
        return [], {"strategy_used": "none", "swaps": 0, "comparisons": 0, "recursion_depth": 0}
    
    if not all(isinstance(x, (int, float)) for x in arr):
        raise TypeError("Array must contain only numbers")
    
    if threshold < 1:
        raise ValueError("Threshold must be positive")
    
    # Deep copy to avoid modifying original
    working_array = arr.copy()
    stats = {
        "strategy_used": strategy.value,
        "swaps": 0,
        "comparisons": 0,
        "recursion_depth": 0,
        "threshold_switches": 0
    }
    
    def insertion_sort(arr_slice: List[int], start: int, end: int) -> None:
        """Insertion sort for small subarrays."""
        for i in range(start + 1, end + 1):
            key = arr_slice[i]
            j = i - 1
            while j >= start and arr_slice[j] > key:
                stats["comparisons"] += 1
                arr_slice[j + 1] = arr_slice[j]
                stats["swaps"] += 1
                j -= 1
            if j >= start:
                stats["comparisons"] += 1  # Final comparison that failed
            arr_slice[j + 1] = key
    
    def partition(arr_slice: List[int], low: int, high: int) -> int:
        """Partition function for quicksort with median-of-three pivot selection."""
        if high - low >= 2:
            # Median-of-three pivot selection
            mid = (low + high) // 2
            stats["comparisons"] += 2
            
            if arr_slice[mid] < arr_slice[low]:
                arr_slice[low], arr_slice[mid] = arr_slice[mid], arr_slice[low]
                stats["swaps"] += 1
            if arr_slice[high] < arr_slice[low]:
                arr_slice[low], arr_slice[high] = arr_slice[high], arr_slice[low]
                stats["swaps"] += 1
            if arr_slice[high] < arr_slice[mid]:
                arr_slice[mid], arr_slice[high] = arr_slice[high], arr_slice[mid]
                stats["swaps"] += 1
        
        pivot = arr_slice[high]
        i = low - 1
        
        for j in range(low, high):
            stats["comparisons"] += 1
            if arr_slice[j] <= pivot:
                i += 1
                if i != j:
                    arr_slice[i], arr_slice[j] = arr_slice[j], arr_slice[i]
                    stats["swaps"] += 1
        
        arr_slice[i + 1], arr_slice[high] = arr_slice[high], arr_slice[i + 1]
        stats["swaps"] += 1
        return i + 1
    
    def quicksort_recursive(arr_slice: List[int], low: int, high: int, depth: int = 0) -> None:
        """Recursive quicksort with adaptive threshold switching."""
        stats["recursion_depth"] = max(stats["recursion_depth"], depth)
        
        if depth > len(arr_slice) * 2:  # Prevent infinite recursion
            raise RecursionError("Maximum recursion depth exceeded")
        
        if low < high:
            # Switch to insertion sort for small subarrays
            if high - low + 1 <= threshold:
                stats["threshold_switches"] += 1
                insertion_sort(arr_slice, low, high)
                return
            
            pivot_index = partition(arr_slice, low, high)
            quicksort_recursive(arr_slice, low, pivot_index - 1, depth + 1)
            quicksort_recursive(arr_slice, pivot_index + 1, high, depth + 1)
    
    try:
        if strategy == SortingStrategy.QUICKSORT:
            quicksort_recursive(working_array, 0, len(working_array) - 1)
        elif strategy == SortingStrategy.MERGESORT:
            # Simplified mergesort implementation
            working_array.sort()  # Using built-in for demonstration
            stats["strategy_used"] = "mergesort_builtin"
        else:
            # Heapsort or other strategies
            working_array.sort()
            stats["strategy_used"] = "heapsort_builtin"
    
    except RecursionError as e:
        stats["error"] = str(e)
        # Fallback to built-in sort
        working_array.sort()
        stats["strategy_used"] = "fallback_builtin"
    
    return working_array, stats


def fibonacci_with_memoization(n: int, cache: Optional[Dict[int, int]] = None) -> Tuple[int, Dict[str, int]]:
    """
    Fibonacci calculation with memoization and detailed statistics.
    
    Args:
        n: Fibonacci number to calculate (0-indexed)
        cache: Optional pre-populated cache
    
    Returns:
        Tuple of (fibonacci_value, computation_stats)
    
    Raises:
        ValueError: For negative inputs
        OverflowError: For excessively large inputs
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    
    if n > 1000:  # Prevent excessive computation
        raise OverflowError("Input too large for computation")
    
    if cache is None:
        cache = {}
    
    stats = {
        "cache_hits": 0,
        "cache_misses": 0,
        "recursive_calls": 0,
        "max_depth": 0
    }
    
    def fib_recursive(num: int, depth: int = 0) -> int:
        stats["recursive_calls"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth)
        
        if num in cache:
            stats["cache_hits"] += 1
            return cache[num]
        
        stats["cache_misses"] += 1
        
        if num <= 1:
            result = num
        else:
            result = fib_recursive(num - 1, depth + 1) + fib_recursive(num - 2, depth + 1)
        
        cache[num] = result
        return result
    
    try:
        result = fib_recursive(n)
        return result, stats
    except RecursionError:
        # Fallback to iterative approach
        stats["fallback_used"] = True
        if n <= 1:
            return n, stats
        
        a, b = 0, 1
        for i in range(2, n + 1):
            a, b = b, a + b
            stats["recursive_calls"] += 1  # Count iterations as "calls"
        
        return b, stats


def matrix_operations(matrix_a: List[List[float]], matrix_b: List[List[float]], 
                     operation: str = "multiply") -> Tuple[List[List[float]], Dict[str, Any]]:
    """
    Perform matrix operations with comprehensive validation and error handling.
    
    Args:
        matrix_a: First matrix
        matrix_b: Second matrix  
        operation: Type of operation ("multiply", "add", "subtract")
    
    Returns:
        Tuple of (result_matrix, operation_stats)
    
    Raises:
        ValueError: For incompatible matrix dimensions or invalid operations
        TypeError: For invalid input types
    """
    if not isinstance(matrix_a, list) or not isinstance(matrix_b, list):
        raise TypeError("Matrices must be lists")
    
    if not matrix_a or not matrix_b:
        raise ValueError("Matrices cannot be empty")
    
    # Validate matrix structure
    def validate_matrix(matrix: List[List[float]], name: str) -> Tuple[int, int]:
        if not all(isinstance(row, list) for row in matrix):
            raise TypeError(f"{name} must be a list of lists")
        
        if not matrix[0]:
            raise ValueError(f"{name} cannot have empty rows")
        
        cols = len(matrix[0])
        for i, row in enumerate(matrix):
            if len(row) != cols:
                raise ValueError(f"{name} row {i} has {len(row)} columns, expected {cols}")
            
            if not all(isinstance(x, (int, float)) for x in row):
                raise TypeError(f"{name} must contain only numbers")
        
        return len(matrix), cols
    
    rows_a, cols_a = validate_matrix(matrix_a, "Matrix A")
    rows_b, cols_b = validate_matrix(matrix_b, "Matrix B")
    
    stats = {
        "operation": operation,
        "matrix_a_shape": (rows_a, cols_a),
        "matrix_b_shape": (rows_b, cols_b),
        "operations_performed": 0,
        "memory_allocated": 0
    }
    
    if operation == "multiply":
        if cols_a != rows_b:
            raise ValueError(f"Cannot multiply {rows_a}x{cols_a} matrix by {rows_b}x{cols_b} matrix")
        
        result = [[0.0 for _ in range(cols_b)] for _ in range(rows_a)]
        stats["memory_allocated"] = rows_a * cols_b
        
        for i in range(rows_a):
            for j in range(cols_b):
                for k in range(cols_a):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]
                    stats["operations_performed"] += 2  # multiply and add
        
        stats["result_shape"] = (rows_a, cols_b)
    
    elif operation in ["add", "subtract"]:
        if rows_a != rows_b or cols_a != cols_b:
            raise ValueError(f"Cannot {operation} matrices of different shapes: "
                           f"{rows_a}x{cols_a} and {rows_b}x{cols_b}")
        
        result = [[0.0 for _ in range(cols_a)] for _ in range(rows_a)]
        stats["memory_allocated"] = rows_a * cols_a
        
        for i in range(rows_a):
            for j in range(cols_a):
                if operation == "add":
                    result[i][j] = matrix_a[i][j] + matrix_b[i][j]
                else:  # subtract
                    result[i][j] = matrix_a[i][j] - matrix_b[i][j]
                stats["operations_performed"] += 1
        
        stats["result_shape"] = (rows_a, cols_a)
    
    else:
        raise ValueError(f"Unsupported operation: {operation}")
    
    return result, stats


def prime_factorization_advanced(n: int, max_iterations: int = 10000) -> Dict[str, Any]:
    """
    Advanced prime factorization with multiple algorithms and detailed analysis.
    
    Args:
        n: Number to factorize
        max_iterations: Maximum iterations to prevent infinite loops
    
    Returns:
        Dictionary with factors and analysis details
    
    Raises:
        ValueError: For invalid inputs
        TimeoutError: If computation takes too long
    """
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    
    if n < 1:
        raise ValueError("Input must be positive")
    
    if n == 1:
        return {
            "factors": {},
            "is_prime": False,
            "algorithm_used": "trivial",
            "iterations": 0,
            "largest_prime_factor": None
        }
    
    original_n = n
    factors = {}
    iterations = 0
    algorithm_stages = []
    
    # Trial division for small factors
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        iterations += 1
        if iterations > max_iterations:
            raise TimeoutError(f"Exceeded maximum iterations: {max_iterations}")
        
        if n % p == 0:
            algorithm_stages.append(f"trial_division_{p}")
            factors[p] = 0
            while n % p == 0:
                factors[p] += 1
                n //= p
                iterations += 1
                
                if iterations > max_iterations:
                    raise TimeoutError(f"Exceeded maximum iterations: {max_iterations}")
    
    # Check if number is now 1 (completely factored)
    if n == 1:
        largest_prime = max(factors.keys()) if factors else None
        return {
            "factors": factors,
            "is_prime": len(factors) == 1 and list(factors.values())[0] == 1,
            "algorithm_used": "trial_division",
            "iterations": iterations,
            "largest_prime_factor": largest_prime,
            "algorithm_stages": algorithm_stages
        }
    
    # Advanced factorization for larger numbers
    algorithm_stages.append("advanced_search")
    
    # Check perfect squares
    sqrt_n = int(math.sqrt(n))
    if sqrt_n * sqrt_n == n:
        algorithm_stages.append("perfect_square_detection")
        # Recursively factor the square root
        sqrt_factors = prime_factorization_advanced(sqrt_n, max_iterations - iterations)
        for prime, count in sqrt_factors["factors"].items():
            factors[prime] = factors.get(prime, 0) + count * 2
        iterations += sqrt_factors["iterations"]
        n = 1
    
    # Continue with remaining number if not completely factored
    if n > 1:
        # Simple trial division up to sqrt(n)
        i = 37  # Continue from where we left off
        while i * i <= n and iterations < max_iterations:
            if n % i == 0:
                algorithm_stages.append(f"extended_trial_division_{i}")
                factors[i] = factors.get(i, 0) + 1
                n //= i
            else:
                i += 2 if i > 2 else 1  # Skip even numbers after 2
            iterations += 1
        
        # If n is still > 1, it's a prime factor
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
            algorithm_stages.append("remaining_prime")
    
    largest_prime = max(factors.keys()) if factors else None
    is_prime = (original_n > 1 and len(factors) == 1 and 
                list(factors.values())[0] == 1 and list(factors.keys())[0] == original_n)
    
    return {
        "factors": factors,
        "is_prime": is_prime,
        "algorithm_used": "hybrid",
        "iterations": iterations,
        "largest_prime_factor": largest_prime,
        "algorithm_stages": algorithm_stages,
        "original_number": original_n
    }