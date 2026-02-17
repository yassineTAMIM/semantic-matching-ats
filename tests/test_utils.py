"""
Test Utilities - Shared testing infrastructure
Provides logging, assertions, and common test utilities
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import traceback


class TestLogger:
    """
    Professional test logger with structured output
    Writes both to console and log files
    """
    
    def __init__(self, log_file: str, test_name: str):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.test_name = test_name
        self.start_time = datetime.now()
        
        # Initialize log file
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"{test_name.upper()}\n")
            f.write("="*80 + "\n")
            f.write(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
        
        # Color output for console
        colors = {
            "INFO": "\033[0m",      # Default
            "SUCCESS": "\033[92m",  # Green
            "WARN": "\033[93m",     # Yellow
            "ERROR": "\033[91m",    # Red
            "PASS": "\033[92m",     # Green
            "FAIL": "\033[91m"      # Red
        }
        
        color = colors.get(level, "\033[0m")
        reset = "\033[0m"
        print(f"{color}{log_entry}{reset}")
    
    def section(self, title: str):
        """Log a section header"""
        separator = "=" * 80
        self.log("")
        self.log(separator)
        self.log(title)
        self.log(separator)
    
    def subsection(self, title: str):
        """Log a subsection header"""
        separator = "-" * 80
        self.log("")
        self.log(separator)
        self.log(title)
        self.log(separator)
    
    def finalize(self, passed: int, failed: int):
        """Write final summary and close log"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.section("TEST SUMMARY")
        self.log(f"Total Tests: {passed + failed}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Duration: {duration:.2f}s")
        
        if failed == 0:
            self.log("RESULT: ALL TESTS PASSED ✓", "SUCCESS")
        else:
            self.log(f"RESULT: {failed} TEST(S) FAILED ✗", "FAIL")
        
        self.log("")
        self.log("="*80)
        self.log(f"Log saved to: {self.log_file.absolute()}")
        self.log("="*80)


class TestAssertion:
    """
    Test assertion utilities with detailed reporting
    """
    
    @staticmethod
    def assert_equals(actual: Any, expected: Any, message: str = "") -> bool:
        """Assert equality with detailed error message"""
        if actual == expected:
            return True
        else:
            error = f"Expected {expected}, got {actual}"
            if message:
                error = f"{message}: {error}"
            raise AssertionError(error)
    
    @staticmethod
    def assert_in_range(value: float, min_val: float, max_val: float, 
                       message: str = "") -> bool:
        """Assert value is in range"""
        if min_val <= value <= max_val:
            return True
        else:
            error = f"Expected value in range [{min_val}, {max_val}], got {value}"
            if message:
                error = f"{message}: {error}"
            raise AssertionError(error)
    
    @staticmethod
    def assert_not_empty(collection: Any, message: str = "") -> bool:
        """Assert collection is not empty"""
        if collection and len(collection) > 0:
            return True
        else:
            error = "Expected non-empty collection"
            if message:
                error = f"{message}: {error}"
            raise AssertionError(error)
    
    @staticmethod
    def assert_type(value: Any, expected_type: type, message: str = "") -> bool:
        """Assert value is of expected type"""
        if isinstance(value, expected_type):
            return True
        else:
            error = f"Expected type {expected_type.__name__}, got {type(value).__name__}"
            if message:
                error = f"{message}: {error}"
            raise AssertionError(error)


class TestRunner:
    """
    Base test runner with consistent execution flow
    """
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """
        Run a single test with error handling
        
        Args:
            test_name: Name of the test
            test_func: Test function to execute
            *args, **kwargs: Arguments to pass to test function
            
        Returns:
            True if test passed, False otherwise
        """
        try:
            test_func(*args, **kwargs)
            self.logger.log(f"✓ {test_name}", "PASS")
            self.passed += 1
            self.test_results.append((test_name, True, None))
            return True
            
        except AssertionError as e:
            self.logger.log(f"✗ {test_name}: {str(e)}", "FAIL")
            self.failed += 1
            self.test_results.append((test_name, False, str(e)))
            return False
            
        except Exception as e:
            self.logger.log(f"✗ {test_name}: Unexpected error - {str(e)}", "ERROR")
            self.logger.log(traceback.format_exc())
            self.failed += 1
            self.test_results.append((test_name, False, f"Exception: {str(e)}"))
            return False
    
    def get_summary(self) -> Dict:
        """Get test execution summary"""
        return {
            'total': self.passed + self.failed,
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': (self.passed / (self.passed + self.failed) * 100) 
                        if (self.passed + self.failed) > 0 else 0,
            'results': self.test_results
        }


def load_test_data():
    """
    Load test data from processed files
    Returns tuple of (candidates, jobs, applications)
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import CV_DATA_FILE, JOB_DATA_FILE, PROCESSED_DATA_DIR
    
    with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    try:
        with open(PROCESSED_DATA_DIR / "applications.json", 'r', encoding='utf-8') as f:
            applications = json.load(f)
    except FileNotFoundError:
        applications = []
    
    return candidates, jobs, applications


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate statistical metrics for a list of values"""
    import numpy as np
    
    return {
        'mean': float(np.mean(values)),
        'median': float(np.median(values)),
        'std': float(np.std(values)),
        'min': float(np.min(values)),
        'max': float(np.max(values)),
        'p25': float(np.percentile(values, 25)),
        'p75': float(np.percentile(values, 75)),
        'p95': float(np.percentile(values, 95))
    }