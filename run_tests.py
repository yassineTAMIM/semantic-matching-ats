#!/usr/bin/env python3
"""
Forvis Mazars ATS - Master Test Suite Runner
Executes all test suites and generates comprehensive report
"""

import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import test modules
from tests.test_data_quality import main as run_data_quality_tests
from tests.test_embeddings import main as run_embedding_tests
from tests.test_matching_engine import main as run_matching_tests
from tests.test_integration import main as run_integration_tests


class MasterTestRunner:
    """Orchestrates all test suites"""
    
    def __init__(self):
        self.log_file = Path("logs/test_master_report.txt")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.start_time = datetime.now()
        self.results = []
        
        # Initialize master log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("FORVIS MAZARS ATS - MASTER TEST REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
    
    def log(self, message: str, level: str = "INFO"):
        """Log to master report and console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
        
        # Color output
        colors = {
            "INFO": "\033[0m",
            "SUCCESS": "\033[92m",
            "WARN": "\033[93m",
            "ERROR": "\033[91m"
        }
        
        color = colors.get(level, "\033[0m")
        reset = "\033[0m"
        print(f"{color}{log_entry}{reset}")
    
    def section(self, title: str):
        """Log section header"""
        separator = "=" * 80
        self.log("")
        self.log(separator)
        self.log(title)
        self.log(separator)
    
    def run_test_suite(self, name: str, test_func) -> dict:
        """Run a single test suite"""
        self.section(f"RUNNING: {name}")
        
        start = time.time()
        
        try:
            success = test_func()
            status = "PASSED" if success else "FAILED"
            level = "SUCCESS" if success else "ERROR"
        except Exception as e:
            success = False
            status = "ERROR"
            level = "ERROR"
            self.log(f"Exception in {name}: {str(e)}", "ERROR")
        
        elapsed = time.time() - start
        
        result = {
            'name': name,
            'success': success,
            'status': status,
            'duration': elapsed
        }
        
        self.results.append(result)
        
        self.log(f"{status}: {name} ({elapsed:.2f}s)", level)
        
        return result
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        self.section("MASTER TEST REPORT - FINAL SUMMARY")
        
        passed = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - passed
        
        self.log(f"Total Test Suites: {len(self.results)}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Total Duration: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
        
        self.log("")
        self.log("Detailed Results:")
        
        for result in self.results:
            status_symbol = "✓" if result['success'] else "✗"
            status_text = "PASS" if result['success'] else "FAIL"
            
            self.log(
                f"  {status_symbol} {status_text:6s} | {result['name']:45s} | {result['duration']:6.2f}s",
                "SUCCESS" if result['success'] else "ERROR"
            )
        
        self.log("")
        self.log("="*80)
        
        if failed == 0:
            self.log("ALL TESTS PASSED ✓✓✓", "SUCCESS")
            self.log("System is production-ready!", "SUCCESS")
            verdict = "PASS"
        else:
            self.log(f"{failed} TEST SUITE(S) FAILED", "ERROR")
            self.log("Review failed suites before deployment", "WARN")
            verdict = "FAIL"
        
        self.log("="*80)
        
        self.log("")
        self.log("Generated Log Files:")
        log_dir = Path("logs")
        if log_dir.exists():
            for log_file in sorted(log_dir.glob("test_*.txt")):
                self.log(f"  - {log_file}")
        
        self.log("")
        self.log("="*80)
        self.log(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Master report: {self.log_file.absolute()}")
        self.log("="*80)
        
        return verdict == "PASS"


def main():
    """Execute all test suites"""
    print("\n" + "="*80)
    print("FORVIS MAZARS ATS - COMPREHENSIVE TEST SUITE")
    print("="*80 + "\n")
    
    runner = MasterTestRunner()
    
    # Test suite configuration
    test_suites = [
        ("Data Quality Tests", run_data_quality_tests),
        ("Embedding Quality Tests", run_embedding_tests),
        ("Matching Engine Tests", run_matching_tests),
        ("Integration Tests", run_integration_tests)
    ]
    
    # Run all test suites
    for name, test_func in test_suites:
        runner.run_test_suite(name, test_func)
    
    # Generate final report
    all_passed = runner.generate_final_report()
    
    # Summary output
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*80)
    print(f"\nMaster Report: {runner.log_file.absolute()}")
    print("\nIndividual Test Logs:")
    print("  • logs/test_data_quality.txt")
    print("  • logs/test_embeddings.txt")
    print("  • logs/test_matching_engine.txt")
    print("  • logs/test_integration.txt")
    print("="*80 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)