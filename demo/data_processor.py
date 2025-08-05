"""
Data processing pipeline with complex state management and error handling.
Showcases advanced testing scenarios including concurrency, side effects, and validation.
"""
import json
import csv
import io
import threading
import time
from typing import List, Dict, Any, Optional, Callable, Union, Iterator
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
from collections import defaultdict, Counter
import tempfile
import os


class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class ValidationLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    PARANOID = "paranoid"


@dataclass
class ProcessingJob:
    job_id: str
    data: Any
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    result: Any = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataProcessor:
    """
    Advanced data processor with state management, concurrency, and validation.
    Demonstrates complex testing scenarios including threading, file I/O, and error recovery.
    """
    
    def __init__(self, max_workers: int = 3, validation_level: ValidationLevel = ValidationLevel.BASIC):
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        
        self.max_workers = max_workers
        self.validation_level = validation_level
        self.jobs: Dict[str, ProcessingJob] = {}
        self.active_workers = 0
        self.lock = threading.RLock()
        self.shutdown_requested = False
        self.processors: Dict[str, Callable] = {
            'json_normalize': self._process_json_data,
            'csv_aggregate': self._process_csv_data,
            'text_analyze': self._process_text_data,
            'numeric_stats': self._process_numeric_data
        }
        self.stats = {
            'jobs_submitted': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
    
    def submit_job(self, job_id: str, data: Any, processor_type: str, **kwargs) -> str:
        """
        Submit a new processing job with validation and queueing.
        
        Args:
            job_id: Unique identifier for the job
            data: Data to process
            processor_type: Type of processor to use
            **kwargs: Additional processing parameters
        
        Returns:
            Job ID if successful
        
        Raises:
            ValueError: For invalid inputs or duplicate job IDs
            RuntimeError: If processor is shutting down
        """
        if self.shutdown_requested:
            raise RuntimeError("Processor is shutting down, cannot accept new jobs")
        
        if not job_id or not isinstance(job_id, str):
            raise ValueError("job_id must be a non-empty string")
        
        if processor_type not in self.processors:
            raise ValueError(f"Unknown processor type: {processor_type}. "
                           f"Available: {list(self.processors.keys())}")
        
        with self.lock:
            if job_id in self.jobs:
                raise ValueError(f"Job ID {job_id} already exists")
            
            # Validate data based on validation level
            self._validate_input_data(data, processor_type)
            
            job = ProcessingJob(
                job_id=job_id,
                data=data,
                metadata={
                    'processor_type': processor_type,
                    'validation_level': self.validation_level.value,
                    **kwargs
                }
            )
            
            self.jobs[job_id] = job
            self.stats['jobs_submitted'] += 1
        
        # Start processing if workers available
        self._try_start_processing(job_id)
        
        return job_id
    
    def _validate_input_data(self, data: Any, processor_type: str) -> None:
        """Validate input data based on processor type and validation level."""
        if self.validation_level == ValidationLevel.NONE:
            return
        
        if data is None:
            if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
                raise ValueError("Data cannot be None")
            return
        
        validations = {
            'json_normalize': self._validate_json_data,
            'csv_aggregate': self._validate_csv_data,
            'text_analyze': self._validate_text_data,
            'numeric_stats': self._validate_numeric_data
        }
        
        validator = validations.get(processor_type)
        if validator:
            validator(data)
    
    def _validate_json_data(self, data: Any) -> None:
        """Validate JSON data input."""
        if isinstance(data, str):
            try:
                json.loads(data)
            except json.JSONDecodeError as e:
                if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
                    raise ValueError(f"Invalid JSON string: {e}")
        elif not isinstance(data, (dict, list)):
            if self.validation_level == ValidationLevel.PARANOID:
                raise ValueError("JSON data must be dict, list, or valid JSON string")
    
    def _validate_csv_data(self, data: Any) -> None:
        """Validate CSV data input."""
        if isinstance(data, str):
            # Check if it looks like CSV content
            if self.validation_level == ValidationLevel.PARANOID:
                lines = data.strip().split('\n')
                if len(lines) < 2:
                    raise ValueError("CSV data must have at least header and one data row")
        elif not isinstance(data, (list, io.StringIO)):
            if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
                raise ValueError("CSV data must be string, list, or StringIO")
    
    def _validate_text_data(self, data: Any) -> None:
        """Validate text data input."""
        if not isinstance(data, str):
            if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
                raise ValueError("Text data must be a string")
        elif self.validation_level == ValidationLevel.PARANOID:
            if len(data.strip()) == 0:
                raise ValueError("Text data cannot be empty or whitespace only")
    
    def _validate_numeric_data(self, data: Any) -> None:
        """Validate numeric data input."""
        if isinstance(data, (list, tuple)):
            if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
                if not all(isinstance(x, (int, float)) for x in data):
                    raise ValueError("All elements must be numeric")
                if self.validation_level == ValidationLevel.PARANOID and len(data) == 0:
                    raise ValueError("Numeric data cannot be empty")
        elif not isinstance(data, (int, float, list, tuple)):
            if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
                raise ValueError("Numeric data must be number or list of numbers")
    
    def _try_start_processing(self, job_id: str) -> None:
        """Try to start processing a job if workers are available."""
        with self.lock:
            if self.active_workers >= self.max_workers:
                return
            
            job = self.jobs.get(job_id)
            if not job or job.status != ProcessingStatus.PENDING:
                return
            
            job.status = ProcessingStatus.PROCESSING
            job.started_at = time.time()
            self.active_workers += 1
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self._process_job, args=(job_id,))
        thread.daemon = True
        thread.start()
    
    def _process_job(self, job_id: str) -> None:
        """Process a job in a separate thread."""
        try:
            job = self.jobs[job_id]
            processor_type = job.metadata['processor_type']
            processor = self.processors[processor_type]
            
            # Simulate processing progress
            for progress in [0.1, 0.3, 0.6, 0.8, 1.0]:
                if self.shutdown_requested:
                    job.status = ProcessingStatus.CANCELLED
                    return
                
                job.progress = progress
                time.sleep(0.01)  # Simulate work
            
            # Execute the actual processor
            result = processor(job.data, job.metadata)
            
            with self.lock:
                job.result = result
                job.status = ProcessingStatus.COMPLETED
                job.completed_at = time.time()
                job.progress = 1.0
                
                processing_time = job.completed_at - job.started_at
                self.stats['jobs_completed'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['average_processing_time'] = (
                    self.stats['total_processing_time'] / self.stats['jobs_completed']
                )
        
        except Exception as e:
            with self.lock:
                job = self.jobs[job_id]
                job.status = ProcessingStatus.ERROR
                job.error_message = str(e)
                job.completed_at = time.time()
                self.stats['jobs_failed'] += 1
        
        finally:
            with self.lock:
                self.active_workers -= 1
            
            # Try to start next pending job
            self._try_start_next_job()
    
    def _try_start_next_job(self) -> None:
        """Try to start the next pending job."""
        with self.lock:
            for job_id, job in self.jobs.items():
                if job.status == ProcessingStatus.PENDING:
                    self._try_start_processing(job_id)
                    break
    
    def _process_json_data(self, data: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process JSON data - normalize and extract statistics."""
        if isinstance(data, str):
            parsed_data = json.loads(data)
        else:
            parsed_data = data
        
        def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
            """Flatten nested dictionary."""
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep).items())
                elif isinstance(v, list) and v and isinstance(v[0], dict):
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            items.extend(flatten_dict(item, f"{new_key}[{i}]", sep).items())
                        else:
                            items.append((f"{new_key}[{i}]", item))
                else:
                    items.append((new_key, v))
            return dict(items)
        
        if isinstance(parsed_data, dict):
            flattened = flatten_dict(parsed_data)
        elif isinstance(parsed_data, list):
            flattened = {}
            for i, item in enumerate(parsed_data):
                if isinstance(item, dict):
                    flattened.update(flatten_dict(item, f"item_{i}"))
                else:
                    flattened[f"item_{i}"] = item
        else:
            flattened = {"value": parsed_data}
        
        # Generate statistics
        stats = {
            'total_keys': len(flattened),
            'data_types': Counter(type(v).__name__ for v in flattened.values()),
            'null_values': sum(1 for v in flattened.values() if v is None),
            'numeric_values': sum(1 for v in flattened.values() if isinstance(v, (int, float))),
            'string_values': sum(1 for v in flattened.values() if isinstance(v, str)),
        }
        
        return {
            'normalized_data': flattened,
            'statistics': stats,
            'original_type': type(parsed_data).__name__
        }
    
    def _process_csv_data(self, data: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process CSV data - parse and generate aggregations."""
        if isinstance(data, str):
            csv_file = io.StringIO(data)
        elif isinstance(data, list):
            # Convert list to CSV format
            if not data:
                raise ValueError("CSV data list cannot be empty")
            
            # Assume first row is headers
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(data)
            csv_file = io.StringIO(output.getvalue())
        else:
            csv_file = data
        
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        
        if not rows:
            return {
                'row_count': 0,
                'columns': [],
                'aggregations': {},
                'data_types': {}
            }
        
        columns = list(rows[0].keys())
        aggregations = {}
        data_types = {}
        
        # Analyze each column
        for col in columns:
            values = [row[col] for row in rows if row[col] is not None and row[col] != '']
            
            if not values:
                data_types[col] = 'empty'
                aggregations[col] = {'count': 0}
                continue
            
            # Try to determine data type
            numeric_values = []
            for val in values:
                try:
                    numeric_values.append(float(val))
                except (ValueError, TypeError):
                    break
            
            if len(numeric_values) == len(values):
                # Numeric column
                data_types[col] = 'numeric'
                aggregations[col] = {
                    'count': len(numeric_values),
                    'sum': sum(numeric_values),
                    'mean': sum(numeric_values) / len(numeric_values),
                    'min': min(numeric_values),
                    'max': max(numeric_values),
                    'distinct_values': len(set(numeric_values))
                }
            else:
                # String column
                data_types[col] = 'string'
                value_counts = Counter(values)
                aggregations[col] = {
                    'count': len(values),
                    'distinct_values': len(value_counts),
                    'most_common': value_counts.most_common(3),
                    'avg_length': sum(len(str(v)) for v in values) / len(values)
                }
        
        return {
            'row_count': len(rows),
            'columns': columns,
            'aggregations': aggregations,
            'data_types': data_types,
            'sample_rows': rows[:5]  # First 5 rows as sample
        }
    
    def _process_text_data(self, data: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process text data - analyze and extract features."""
        if not isinstance(data, str):
            raise ValueError("Text data must be a string")
        
        # Basic text statistics
        lines = data.split('\n')
        words = data.split()
        sentences = [s.strip() for s in data.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        
        # Character analysis
        char_counts = Counter(data.lower())
        letter_counts = Counter(c for c in data.lower() if c.isalpha())
        
        # Word analysis
        word_lengths = [len(word) for word in words]
        word_counts = Counter(word.lower().strip('.,!?;:"()[]{}') for word in words)
        
        return {
            'basic_stats': {
                'total_characters': len(data),
                'total_words': len(words),
                'total_lines': len(lines),
                'total_sentences': len(sentences),
                'avg_words_per_line': len(words) / len(lines) if lines else 0,
                'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0
            },
            'character_analysis': {
                'most_common_chars': char_counts.most_common(10),
                'letter_frequency': dict(letter_counts.most_common(5)),
                'punctuation_count': sum(1 for c in data if not c.isalnum() and not c.isspace()),
                'whitespace_count': sum(1 for c in data if c.isspace())
            },
            'word_analysis': {
                'most_common_words': word_counts.most_common(10),
                'avg_word_length': sum(word_lengths) / len(word_lengths) if word_lengths else 0,
                'longest_word': max(words, key=len) if words else '',
                'shortest_word': min(words, key=len) if words else '',
                'unique_words': len(word_counts)
            },
            'readability': {
                'avg_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
                'complexity_score': len(set(words)) / len(words) if words else 0  # Unique/total ratio
            }
        }
    
    def _process_numeric_data(self, data: Union[List[float], float, int], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process numeric data - statistical analysis and outlier detection."""
        if isinstance(data, (int, float)):
            data = [data]
        
        if not data:
            raise ValueError("Numeric data cannot be empty")
        
        # Convert to floats for calculation
        try:
            numbers = [float(x) for x in data]
        except (ValueError, TypeError) as e:
            raise ValueError(f"All data must be numeric: {e}")
        
        n = len(numbers)
        sorted_nums = sorted(numbers)
        
        # Basic statistics
        total = sum(numbers)
        mean = total / n
        variance = sum((x - mean) ** 2 for x in numbers) / n
        std_dev = variance ** 0.5
        
        # Percentiles
        def percentile(nums: List[float], p: float) -> float:
            """Calculate percentile value."""
            k = (n - 1) * p
            f = int(k)
            c = k - f
            if f == n - 1:
                return nums[f]
            return nums[f] * (1 - c) + nums[f + 1] * c
        
        # Outlier detection using IQR method
        q1 = percentile(sorted_nums, 0.25)
        q3 = percentile(sorted_nums, 0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = [x for x in numbers if x < lower_bound or x > upper_bound]
        
        return {
            'basic_stats': {
                'count': n,
                'sum': total,
                'mean': mean,
                'median': percentile(sorted_nums, 0.5),
                'mode': max(set(numbers), key=numbers.count) if len(set(numbers)) < n else None,
                'min': min(numbers),
                'max': max(numbers),
                'range': max(numbers) - min(numbers)
            },
            'distribution': {
                'variance': variance,
                'std_deviation': std_dev,
                'skewness': sum((x - mean) ** 3 for x in numbers) / (n * std_dev ** 3) if std_dev > 0 else 0,
                'kurtosis': sum((x - mean) ** 4 for x in numbers) / (n * std_dev ** 4) if std_dev > 0 else 0
            },
            'percentiles': {
                'q1': q1,
                'q2_median': percentile(sorted_nums, 0.5),
                'q3': q3,
                'iqr': iqr,
                'p10': percentile(sorted_nums, 0.1),
                'p90': percentile(sorted_nums, 0.9)
            },
            'outliers': {
                'count': len(outliers),
                'values': outliers,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'percentage': len(outliers) / n * 100
            }
        }
    
    def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get the current status of a job."""
        with self.lock:
            return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> Dict[str, ProcessingJob]:
        """Get all jobs and their statuses."""
        with self.lock:
            return self.jobs.copy()
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or processing job."""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False
            
            if job.status == ProcessingStatus.PENDING:
                job.status = ProcessingStatus.CANCELLED
                job.completed_at = time.time()
                return True
            elif job.status == ProcessingStatus.PROCESSING:
                # Set flag for processing thread to check
                job.status = ProcessingStatus.CANCELLED
                return True
            
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processor statistics."""
        with self.lock:
            stats = self.stats.copy()
            stats.update({
                'active_workers': self.active_workers,
                'max_workers': self.max_workers,
                'pending_jobs': sum(1 for j in self.jobs.values() if j.status == ProcessingStatus.PENDING),
                'processing_jobs': sum(1 for j in self.jobs.values() if j.status == ProcessingStatus.PROCESSING),
                'completed_jobs': sum(1 for j in self.jobs.values() if j.status == ProcessingStatus.COMPLETED),
                'failed_jobs': sum(1 for j in self.jobs.values() if j.status == ProcessingStatus.ERROR),
                'cancelled_jobs': sum(1 for j in self.jobs.values() if j.status == ProcessingStatus.CANCELLED),
                'total_jobs': len(self.jobs)
            })
            return stats
    
    def shutdown(self, wait_for_completion: bool = True, timeout: float = 30.0) -> bool:
        """
        Shutdown the processor gracefully.
        
        Args:
            wait_for_completion: Whether to wait for active jobs to complete
            timeout: Maximum time to wait in seconds
        
        Returns:
            True if shutdown completed within timeout, False otherwise
        """
        self.shutdown_requested = True
        
        if not wait_for_completion:
            return True
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.lock:
                if self.active_workers == 0:
                    return True
            time.sleep(0.1)
        
        return False
    
    @contextmanager
    def temp_file_processor(self, data: str, processor_type: str = 'text_analyze'):
        """
        Context manager for processing data through temporary files.
        Demonstrates file I/O with proper cleanup.
        """
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(data)
                temp_file = f.name
            
            # Process the file
            with open(temp_file, 'r') as f:
                file_data = f.read()
            
            job_id = f"temp_file_{int(time.time() * 1000)}"
            self.submit_job(job_id, file_data, processor_type)
            
            # Wait for completion
            while True:
                job = self.get_job_status(job_id)
                if job and job.status in [ProcessingStatus.COMPLETED, ProcessingStatus.ERROR, ProcessingStatus.CANCELLED]:
                    break
                time.sleep(0.01)
            
            yield job
            
        finally:
            # Cleanup
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass  # Ignore cleanup failures


def create_sample_data(data_type: str, size: int = 100) -> Any:
    """
    Generate sample data for testing different processors.
    
    Args:
        data_type: Type of data to generate ('json', 'csv', 'text', 'numeric')
        size: Size of the generated data
    
    Returns:
        Sample data appropriate for the specified type
    
    Raises:
        ValueError: For unsupported data types
    """
    import random
    import string
    
    if data_type == 'json':
        # Generate nested JSON structure
        data = {
            'users': [
                {
                    'id': i,
                    'name': f"User {i}",
                    'email': f"user{i}@example.com",
                    'age': random.randint(18, 80),
                    'preferences': {
                        'theme': random.choice(['light', 'dark']),
                        'notifications': random.choice([True, False]),
                        'language': random.choice(['en', 'es', 'fr', 'de'])
                    },
                    'scores': [random.randint(0, 100) for _ in range(random.randint(1, 5))]
                }
                for i in range(min(size, 50))  # Limit to avoid huge structures
            ],
            'metadata': {
                'generated_at': time.time(),
                'total_users': min(size, 50),
                'version': '1.0'
            }
        }
        return json.dumps(data)
    
    elif data_type == 'csv':
        # Generate CSV data as string
        headers = ['id', 'name', 'age', 'salary', 'department', 'hire_date']
        departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance']
        
        csv_lines = [','.join(headers)]
        for i in range(min(size, 1000)):
            row = [
                str(i),
                f"Employee {i}",
                str(random.randint(22, 65)),
                str(random.randint(30000, 150000)),
                random.choice(departments),
                f"202{random.randint(0, 3)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            ]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    elif data_type == 'text':
        # Generate random text with various patterns
        words = ['lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit',
                'sed', 'do', 'eiusmod', 'tempor', 'incididunt', 'ut', 'labore', 'et', 'dolore',
                'magna', 'aliqua', 'enim', 'ad', 'minim', 'veniam', 'quis', 'nostrud']
        
        sentences = []
        for _ in range(min(size, 500)):
            sentence_length = random.randint(5, 20)
            sentence_words = random.choices(words, k=sentence_length)
            sentence = ' '.join(sentence_words).capitalize() + '.'
            sentences.append(sentence)
        
        # Group into paragraphs
        paragraphs = []
        current_paragraph = []
        for sentence in sentences:
            current_paragraph.append(sentence)
            if len(current_paragraph) >= random.randint(3, 8):
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
        
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        return '\n\n'.join(paragraphs)
    
    elif data_type == 'numeric':
        # Generate numeric data with some patterns and outliers
        base_data = [random.gauss(50, 15) for _ in range(min(size, 10000))]
        
        # Add some outliers
        outlier_count = max(1, len(base_data) // 20)
        for _ in range(outlier_count):
            idx = random.randint(0, len(base_data) - 1)
            base_data[idx] = random.choice([random.gauss(0, 5), random.gauss(100, 5)])
        
        return base_data
    
    else:
        raise ValueError(f"Unsupported data type: {data_type}. "
                        f"Supported types: json, csv, text, numeric")