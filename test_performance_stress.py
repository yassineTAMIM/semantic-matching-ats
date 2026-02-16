"""
Performance & Stress Testing Suite
Tests system performance under various load conditions
Logs all results to local .txt file
"""

import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List
import traceback

sys.path.append(str(Path(__file__).parent))
from config import *
from src.search.matching_engine import MatchingEngine
from src.search.dormant_detector import DormantTalentDetector

class TestLogger:
    """Custom logger for performance tests"""
    
    def __init__(self, log_file: str = "logs/performance_stress_test.txt"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"PERFORMANCE & STRESS TESTING LOG\n")
            f.write(f"{'='*80}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"[{level}] {message}")
    
    def section(self, title: str):
        separator = "=" * 80
        self.log(f"\n{separator}")
        self.log(title)
        self.log(separator)


class PerformanceStressTester:
    """Performance and stress testing for matching system"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.engine = None
        self.dormant_detector = None
        self.jobs = None
        self.candidates = None
        self.results = {}
    
    def setup(self):
        """Setup test environment"""
        self.logger.section("TEST ENVIRONMENT SETUP")
        
        try:
            # Initialize engines
            self.logger.log("Initializing matching engine...")
            start = time.time()
            self.engine = MatchingEngine()
            init_time = time.time() - start
            self.logger.log(f"Matching engine initialized in {init_time:.2f}s", "SUCCESS")
            
            self.logger.log("Initializing dormant talent detector...")
            start = time.time()
            self.dormant_detector = DormantTalentDetector(self.engine)
            init_time = time.time() - start
            self.logger.log(f"Dormant detector initialized in {init_time:.2f}s", "SUCCESS")
            
            # Load test data
            with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
                self.jobs = json.load(f)
            
            with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
                self.candidates = json.load(f)
            
            self.logger.log(f"Loaded {len(self.jobs)} jobs and {len(self.candidates)} candidates")
            
        except Exception as e:
            self.logger.log(f"Setup failed: {e}", "ERROR")
            raise
    
    def test_single_query_performance(self):
        """Test performance of single matching query"""
        self.logger.section("TEST: Single Query Performance")
        
        test_job = self.jobs[0]
        times = []
        
        # Warm-up run
        self.logger.log("Performing warm-up run...")
        _ = self.engine.match_candidates(test_job, top_k=10)
        
        # Multiple runs for average
        num_runs = 10
        self.logger.log(f"Running {num_runs} matching queries...")
        
        for i in range(num_runs):
            start = time.time()
            matches = self.engine.match_candidates(test_job, top_k=10)
            elapsed = time.time() - start
            times.append(elapsed)
            
            self.logger.log(f"  Run {i+1}/{num_runs}: {elapsed:.3f}s ({len(matches)} matches)")
        
        # Statistics
        avg_time = np.mean(times)
        std_time = np.std(times)
        min_time = np.min(times)
        max_time = np.max(times)
        p95_time = np.percentile(times, 95)
        
        self.logger.log(f"\nPerformance Statistics:")
        self.logger.log(f"  Average: {avg_time:.3f}s")
        self.logger.log(f"  Std Dev: {std_time:.3f}s")
        self.logger.log(f"  Min: {min_time:.3f}s")
        self.logger.log(f"  Max: {max_time:.3f}s")
        self.logger.log(f"  95th percentile: {p95_time:.3f}s")
        
        # Performance verdict
        if avg_time < 1.0:
            verdict = "EXCELLENT (< 1s)"
            level = "SUCCESS"
        elif avg_time < 2.0:
            verdict = "GOOD (< 2s)"
            level = "SUCCESS"
        elif avg_time < 5.0:
            verdict = "ACCEPTABLE (< 5s)"
            level = "WARN"
        else:
            verdict = "POOR (≥ 5s)"
            level = "WARN"
        
        self.logger.log(f"\nVerdict: {verdict}", level)
        
        self.results['single_query'] = {
            'avg_time': avg_time,
            'p95_time': p95_time,
            'verdict': verdict
        }
    
    def test_batch_performance(self):
        """Test performance with multiple queries"""
        self.logger.section("TEST: Batch Query Performance")
        
        batch_sizes = [5, 10, 20]
        
        for batch_size in batch_sizes:
            self.logger.log(f"\nTesting with {batch_size} jobs...")
            
            test_jobs = self.jobs[:batch_size]
            start = time.time()
            
            total_matches = 0
            for i, job in enumerate(test_jobs):
                matches = self.engine.match_candidates(job, top_k=10)
                total_matches += len(matches)
                
                if (i + 1) % 5 == 0:
                    elapsed = time.time() - start
                    rate = (i + 1) / elapsed
                    self.logger.log(f"  Processed {i+1}/{batch_size} jobs ({rate:.2f} jobs/sec)")
            
            elapsed = time.time() - start
            avg_per_job = elapsed / batch_size
            throughput = batch_size / elapsed
            
            self.logger.log(f"\nBatch {batch_size} Results:")
            self.logger.log(f"  Total time: {elapsed:.2f}s")
            self.logger.log(f"  Avg per job: {avg_per_job:.3f}s")
            self.logger.log(f"  Throughput: {throughput:.2f} jobs/sec")
            self.logger.log(f"  Total matches: {total_matches}")
            
            self.results[f'batch_{batch_size}'] = {
                'total_time': elapsed,
                'avg_per_job': avg_per_job,
                'throughput': throughput
            }
    
    def test_varying_top_k(self):
        """Test performance with varying number of results requested"""
        self.logger.section("TEST: Performance vs Top-K Results")
        
        test_job = self.jobs[0]
        top_k_values = [5, 10, 20, 50, 100]
        
        for top_k in top_k_values:
            times = []
            
            # Run 5 times for average
            for _ in range(5):
                start = time.time()
                matches = self.engine.match_candidates(test_job, top_k=top_k)
                elapsed = time.time() - start
                times.append(elapsed)
            
            avg_time = np.mean(times)
            
            self.logger.log(f"Top-K={top_k:3d}: {avg_time:.3f}s avg")
            
            self.results[f'top_k_{top_k}'] = avg_time
    
    def test_filtering_impact(self):
        """Test performance impact of filters"""
        self.logger.section("TEST: Filtering Performance Impact")
        
        test_job = self.jobs[0]
        
        # No filters
        times_no_filter = []
        for _ in range(5):
            start = time.time()
            _ = self.engine.match_candidates(test_job, top_k=10, filters=None)
            times_no_filter.append(time.time() - start)
        
        avg_no_filter = np.mean(times_no_filter)
        self.logger.log(f"No filters: {avg_no_filter:.3f}s avg")
        
        # Location filter
        times_location = []
        for _ in range(5):
            start = time.time()
            _ = self.engine.match_candidates(
                test_job, 
                top_k=10, 
                filters={'location': 'Paris, France'}
            )
            times_location.append(time.time() - start)
        
        avg_location = np.mean(times_location)
        overhead = ((avg_location - avg_no_filter) / avg_no_filter) * 100
        self.logger.log(f"Location filter: {avg_location:.3f}s avg ({overhead:+.1f}% overhead)")
        
        # Experience filter
        times_experience = []
        for _ in range(5):
            start = time.time()
            _ = self.engine.match_candidates(
                test_job,
                top_k=10,
                filters={'min_experience': 3, 'max_experience': 7}
            )
            times_experience.append(time.time() - start)
        
        avg_experience = np.mean(times_experience)
        overhead = ((avg_experience - avg_no_filter) / avg_no_filter) * 100
        self.logger.log(f"Experience filter: {avg_experience:.3f}s avg ({overhead:+.1f}% overhead)")
        
        # Combined filters
        times_combined = []
        for _ in range(5):
            start = time.time()
            _ = self.engine.match_candidates(
                test_job,
                top_k=10,
                filters={
                    'location': 'Paris, France',
                    'min_experience': 3,
                    'max_experience': 7
                }
            )
            times_combined.append(time.time() - start)
        
        avg_combined = np.mean(times_combined)
        overhead = ((avg_combined - avg_no_filter) / avg_no_filter) * 100
        self.logger.log(f"Combined filters: {avg_combined:.3f}s avg ({overhead:+.1f}% overhead)")
    
    def test_dormant_detection_performance(self):
        """Test dormant talent detection performance"""
        self.logger.section("TEST: Dormant Talent Detection Performance")
        
        test_job = self.jobs[0]
        
        # Test with different thresholds
        thresholds = [0.60, 0.70, 0.75, 0.80]
        
        for threshold in thresholds:
            self.logger.log(f"\nTesting with threshold {threshold:.2f}...")
            
            start = time.time()
            dormant_matches = self.dormant_detector.detect_dormant_matches(
                test_job,
                min_score=threshold
            )
            elapsed = time.time() - start
            
            self.logger.log(
                f"  Found {len(dormant_matches)} matches in {elapsed:.2f}s "
                f"({len(dormant_matches)/elapsed:.1f} matches/sec)"
            )
            
            if dormant_matches:
                summary = self.dormant_detector.generate_alert_summary(dormant_matches)
                self.logger.log(f"  Avg months dormant: {summary['avg_months_dormant']:.1f}")
                self.logger.log(f"  Avg match score: {summary['avg_match_score']:.3f}")
    
    def test_concurrent_queries(self):
        """Simulate concurrent query load"""
        self.logger.section("TEST: Concurrent Query Simulation")
        
        num_concurrent = 10
        self.logger.log(f"Simulating {num_concurrent} sequential queries...")
        
        start = time.time()
        
        for i in range(num_concurrent):
            job_idx = i % len(self.jobs)
            job = self.jobs[job_idx]
            _ = self.engine.match_candidates(job, top_k=10)
            
            if (i + 1) % 5 == 0:
                elapsed = time.time() - start
                self.logger.log(f"  Completed {i+1}/{num_concurrent} queries ({elapsed:.2f}s)")
        
        total_time = time.time() - start
        avg_time = total_time / num_concurrent
        throughput = num_concurrent / total_time
        
        self.logger.log(f"\nConcurrent Simulation Results:")
        self.logger.log(f"  Total time: {total_time:.2f}s")
        self.logger.log(f"  Avg per query: {avg_time:.3f}s")
        self.logger.log(f"  Throughput: {throughput:.2f} queries/sec")
        
        self.results['concurrent'] = {
            'num_queries': num_concurrent,
            'total_time': total_time,
            'throughput': throughput
        }
    
    def test_memory_usage(self):
        """Test memory footprint"""
        self.logger.section("TEST: Memory Usage")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # Before query
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            self.logger.log(f"Memory before queries: {mem_before:.1f} MB")
            
            # Run multiple queries
            for i in range(20):
                job = self.jobs[i % len(self.jobs)]
                _ = self.engine.match_candidates(job, top_k=10)
            
            # After queries
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            mem_increase = mem_after - mem_before
            
            self.logger.log(f"Memory after 20 queries: {mem_after:.1f} MB")
            self.logger.log(f"Memory increase: {mem_increase:.1f} MB")
            
            if mem_increase < 50:
                self.logger.log("Memory usage: EXCELLENT (< 50 MB increase)", "SUCCESS")
            elif mem_increase < 100:
                self.logger.log("Memory usage: GOOD (< 100 MB increase)", "SUCCESS")
            else:
                self.logger.log(f"Memory usage: HIGH ({mem_increase:.1f} MB increase)", "WARN")
            
            self.results['memory'] = {
                'before': mem_before,
                'after': mem_after,
                'increase': mem_increase
            }
            
        except ImportError:
            self.logger.log("psutil not installed - skipping memory test", "WARN")
    
    def test_error_recovery(self):
        """Test system robustness and error handling"""
        self.logger.section("TEST: Error Recovery & Robustness")
        
        # Test 1: Invalid job data
        self.logger.log("\nTest 1: Handling invalid job data...")
        try:
            invalid_job = {'id': 'INVALID', 'title': 'Test'}  # Missing required fields
            matches = self.engine.match_candidates(invalid_job, top_k=10)
            self.logger.log("Handled invalid job gracefully", "SUCCESS")
        except Exception as e:
            self.logger.log(f"Exception on invalid job: {type(e).__name__}", "WARN")
        
        # Test 2: Edge case values
        self.logger.log("\nTest 2: Handling edge case values...")
        try:
            edge_case_job = {
                'id': 'EDGE_001',
                'title': 'Test',
                'service_line': 'Unknown Service',
                'location': 'Nowhere',
                'experience_level': 'Extreme',
                'years_experience_min': -5,
                'years_experience_max': 1000,
                'description': '',
                'required_skills': [],
                'required_languages': []
            }
            matches = self.engine.match_candidates(edge_case_job, top_k=10)
            self.logger.log(f"Handled edge cases, returned {len(matches)} matches", "SUCCESS")
        except Exception as e:
            self.logger.log(f"Exception on edge cases: {type(e).__name__}", "WARN")
        
        # Test 3: Large top_k value
        self.logger.log("\nTest 3: Handling very large top_k...")
        try:
            test_job = self.jobs[0]
            matches = self.engine.match_candidates(test_job, top_k=10000)
            actual_returned = len(matches)
            self.logger.log(
                f"Requested 10000, returned {actual_returned} (OK - limited by data)",
                "SUCCESS"
            )
        except Exception as e:
            self.logger.log(f"Exception on large top_k: {type(e).__name__}", "WARN")
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        self.logger.section("PERFORMANCE TEST SUMMARY")
        
        self.logger.log("\nKey Performance Metrics:")
        
        if 'single_query' in self.results:
            sq = self.results['single_query']
            self.logger.log(f"  Single Query Avg: {sq['avg_time']:.3f}s")
            self.logger.log(f"  Single Query P95: {sq['p95_time']:.3f}s")
            self.logger.log(f"  Verdict: {sq['verdict']}")
        
        if 'concurrent' in self.results:
            cc = self.results['concurrent']
            self.logger.log(f"\n  Concurrent Throughput: {cc['throughput']:.2f} queries/sec")
        
        if 'memory' in self.results:
            mem = self.results['memory']
            self.logger.log(f"\n  Memory Usage: {mem['after']:.1f} MB")
            self.logger.log(f"  Memory Overhead: {mem['increase']:.1f} MB")
        
        # Overall performance grade
        self.logger.log(f"\n{'='*40}")
        
        if 'single_query' in self.results:
            avg_time = self.results['single_query']['avg_time']
            
            if avg_time < 1.0:
                grade = "A+ (Excellent)"
            elif avg_time < 2.0:
                grade = "A (Very Good)"
            elif avg_time < 3.0:
                grade = "B (Good)"
            elif avg_time < 5.0:
                grade = "C (Acceptable)"
            else:
                grade = "D (Needs Optimization)"
            
            self.logger.log(f"OVERALL PERFORMANCE GRADE: {grade}")
        
        self.logger.log(f"{'='*40}")
    
    def run_all_tests(self):
        """Run all performance tests"""
        self.setup()
        
        try:
            self.test_single_query_performance()
            self.test_batch_performance()
            self.test_varying_top_k()
            self.test_filtering_impact()
            self.test_dormant_detection_performance()
            self.test_concurrent_queries()
            self.test_memory_usage()
            self.test_error_recovery()
            
            self.generate_performance_report()
            
        except Exception as e:
            self.logger.log(f"Test execution failed: {e}", "ERROR")
            self.logger.log(traceback.format_exc())
        
        self.logger.log(f"\n{'='*80}")
        self.logger.log(f"Performance testing complete. Log saved to: {self.logger.log_file}")
        self.logger.log(f"{'='*80}")


def main():
    """Main execution"""
    logger = TestLogger("logs/performance_stress_test.txt")
    tester = PerformanceStressTester(logger)
    tester.run_all_tests()
    
    print(f"\n✅ Performance tests complete. Full log saved to: {logger.log_file.absolute()}")


if __name__ == "__main__":
    main()