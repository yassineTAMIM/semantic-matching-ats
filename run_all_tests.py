"""
Master Test Suite Runner
Executes all test suites and generates comprehensive report
Logs all results to local .txt file
"""

import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.append(str(Path(__file__).parent))

# Import test modules
import test_data_quality
import test_embedding_quality
import test_matching_engine
import test_performance_stress
import test_integration

class MasterTestLogger:
    """Master logger for all tests"""
    
    def __init__(self):
        self.log_file = Path("logs/master_test_report.txt")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"FORVIS MAZARS ATS - MASTER TEST REPORT\n")
            f.write(f"{'='*80}\n")
            f.write(f"Test Execution Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
    
    def log(self, message: str):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
        print(message)
    
    def section(self, title: str):
        separator = "=" * 80
        self.log(f"\n{separator}")
        self.log(title)
        self.log(separator)


def run_test_suite(suite_name: str, test_function, logger: MasterTestLogger):
    """Run a test suite and capture results"""
    logger.section(f"RUNNING: {suite_name}")
    logger.log(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    success = False
    error_message = None
    
    try:
        test_function()
        success = True
        logger.log(f"✓ {suite_name} PASSED")
    except Exception as e:
        error_message = str(e)
        logger.log(f"✗ {suite_name} FAILED: {error_message}")
    
    elapsed = time.time() - start_time
    logger.log(f"Duration: {elapsed:.2f}s")
    logger.log(f"Completed at: {datetime.now().strftime('%H:%M:%S')}")
    
    return {
        'name': suite_name,
        'success': success,
        'duration': elapsed,
        'error': error_message
    }


def main():
    """Execute all test suites"""
    print("\n" + "="*80)
    print("FORVIS MAZARS ATS - COMPREHENSIVE TEST SUITE")
    print("="*80 + "\n")
    
    logger = MasterTestLogger()
    results = []
    
    overall_start = time.time()
    
    # Test Suite 1: Data Quality
    print("\n[1/5] Running Data Quality Tests...")
    results.append(run_test_suite(
        "Data Quality Validation",
        test_data_quality.main,
        logger
    ))
    
    # Test Suite 2: Embedding Quality
    print("\n[2/5] Running Embedding Quality Tests...")
    results.append(run_test_suite(
        "Embedding Quality Assessment",
        test_embedding_quality.main,
        logger
    ))
    
    # Test Suite 3: Matching Engine Unit Tests
    print("\n[3/5] Running Matching Engine Unit Tests...")
    results.append(run_test_suite(
        "Matching Engine Unit Tests",
        test_matching_engine.main,
        logger
    ))
    
    # Test Suite 4: Performance & Stress Tests
    print("\n[4/5] Running Performance & Stress Tests...")
    results.append(run_test_suite(
        "Performance & Stress Testing",
        test_performance_stress.main,
        logger
    ))
    
    # Test Suite 5: Integration Tests
    print("\n[5/5] Running Integration Tests...")
    results.append(run_test_suite(
        "End-to-End Integration Testing",
        test_integration.main,
        logger
    ))
    
    # Generate Final Report
    overall_elapsed = time.time() - overall_start
    
    logger.section("MASTER TEST REPORT - FINAL SUMMARY")
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    logger.log(f"\nTest Execution Summary:")
    logger.log(f"  Total Test Suites: {len(results)}")
    logger.log(f"  Passed: {passed}")
    logger.log(f"  Failed: {failed}")
    logger.log(f"  Total Duration: {overall_elapsed/60:.2f} minutes")
    
    logger.log(f"\nDetailed Results:")
    for result in results:
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        logger.log(f"  {status:8s} | {result['name']:40s} | {result['duration']:6.2f}s")
        if result['error']:
            logger.log(f"           Error: {result['error']}")
    
    # Overall verdict
    logger.log(f"\n{'='*80}")
    
    if failed == 0:
        verdict = "ALL TESTS PASSED ✓✓✓"
        level = "SUCCESS"
        logger.log(verdict)
        logger.log("System is production-ready!")
    elif failed == 1:
        verdict = "1 TEST SUITE FAILED"
        level = "WARN"
        logger.log(verdict)
        logger.log("Review failed suite before deployment")
    else:
        verdict = f"{failed} TEST SUITES FAILED"
        level = "ERROR"
        logger.log(verdict)
        logger.log("Multiple issues detected - investigation required")
    
    logger.log(f"{'='*80}")
    
    # List all log files
    logger.log(f"\nGenerated Log Files:")
    log_dir = Path("logs")
    if log_dir.exists():
        for log_file in sorted(log_dir.glob("*.txt")):
            logger.log(f"  - {log_file}")
    
    logger.log(f"\n{'='*80}")
    logger.log(f"Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.log(f"Master report saved to: {logger.log_file}")
    logger.log(f"{'='*80}\n")
    
    print(f"\n{'='*80}")
    print(f"✅ All tests completed!")
    print(f"{'='*80}")
    print(f"\nMaster Report: {logger.log_file.absolute()}")
    print(f"\nIndividual Test Logs:")
    print(f"  1. Data Quality:        logs/data_quality_test.txt")
    print(f"  2. Embedding Quality:   logs/embedding_quality_test.txt")
    print(f"  3. Matching Engine:     logs/matching_engine_tests.txt")
    print(f"  4. Performance/Stress:  logs/performance_stress_test.txt")
    print(f"  5. Integration Tests:   logs/integration_test.txt")
    print(f"\nTest Summary: {passed}/{len(results)} suites passed")
    print(f"Total Duration: {overall_elapsed/60:.2f} minutes")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()