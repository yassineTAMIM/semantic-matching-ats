"""
Integration Tests
End-to-end workflow testing and system integration validation
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_utils import TestLogger, TestAssertion, TestRunner, load_test_data
from src.search.matching_engine import MatchingEngine
from src.search.dormant_detector import DormantTalentDetector
from src.explainability.explainer import ExplainabilityEngine


class IntegrationTests:
    """End-to-end integration testing"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.runner = TestRunner(logger)
        self.engine = None
        self.dormant_detector = None
        self.candidates = []
        self.jobs = []
        self.applications = []
    
    def setup(self):
        """Initialize all components"""
        self.logger.section("SYSTEM INITIALIZATION")
        
        # Initialize engines
        self.engine = MatchingEngine()
        self.dormant_detector = DormantTalentDetector(self.engine)
        
        # Load data
        self.candidates, self.jobs, self.applications = load_test_data()
        
        self.logger.log(f"Matching engine ready")
        self.logger.log(f"Dormant detector ready")
        self.logger.log(f"Test data loaded: {len(self.jobs)} jobs, {len(self.candidates)} candidates")
    
    def test_complete_recruitment_workflow(self):
        """Test complete recruitment workflow"""
        test_job = self.jobs[0]
        
        self.logger.log(f"Testing workflow for: {test_job['title']}")
        
        # Step 1: Find candidates
        matches = self.engine.match_candidates(test_job, top_k=10)
        
        if not matches:
            self.logger.log("No applicants for this job - workflow limited", "WARN")
            return
        
        TestAssertion.assert_not_empty(matches, "Step 1: Find candidates")
        
        # Step 2: Generate explanations
        top_match = matches[0]
        explanation = ExplainabilityEngine.generate_explanation(top_match)
        
        # Verify explanation structure
        required_keys = ['summary', 'strengths', 'weaknesses', 'recommendation']
        for key in required_keys:
            if key not in explanation:
                raise AssertionError(f"Missing explanation component: {key}")
        
        self.logger.log("Step 2: Explanations generated")
        
        # Step 3: Check dormant talent
        dormant_matches = self.dormant_detector.detect_dormant_matches(test_job, min_score=0.70)
        
        self.logger.log(f"Step 3: Dormant scan complete - {len(dormant_matches)} matches")
        
        # Workflow successful
        self.logger.log("Complete workflow executed successfully")
    
    def test_batch_job_processing(self):
        """Test processing multiple jobs"""
        num_jobs = min(5, len(self.jobs))
        batch_jobs = self.jobs[:num_jobs]
        
        self.logger.log(f"Processing batch of {num_jobs} jobs...")
        
        start = time.time()
        results = []
        
        for job in batch_jobs:
            matches = self.engine.match_candidates(job, top_k=10)
            results.append({
                'job_id': job['id'],
                'matches': len(matches)
            })
        
        elapsed = time.time() - start
        throughput = num_jobs / elapsed
        
        self.logger.log(f"Processed {num_jobs} jobs in {elapsed:.2f}s ({throughput:.2f} jobs/sec)")
        
        # Should process efficiently
        if elapsed > num_jobs * 2:  # Max 2s per job
            raise AssertionError(f"Batch processing too slow: {elapsed:.2f}s for {num_jobs} jobs")
    
    def test_dormant_talent_workflow(self):
        """Test dormant talent detection workflow"""
        test_job = self.jobs[1]
        
        self.logger.log(f"Testing dormant workflow for: {test_job['title']}")
        
        # Detect dormant candidates
        dormant_matches = self.dormant_detector.detect_dormant_matches(test_job, min_score=0.65)
        
        self.logger.log(f"Found {len(dormant_matches)} dormant matches")
        
        if dormant_matches:
            # Generate summary
            summary = self.dormant_detector.generate_alert_summary(dormant_matches)
            
            TestAssertion.assert_type(summary, dict, "Dormant summary")
            TestAssertion.assert_type(summary.get('total_alerts'), int, "Alert count")
            
            # Create notifications
            notifications = self.dormant_detector.create_alert_notifications(dormant_matches, test_job)
            
            TestAssertion.assert_not_empty(notifications, "Notifications created")
            
            self.logger.log(f"Generated {len(notifications)} notifications")
    
    def test_filtering_integration(self):
        """Test filtering across the system"""
        test_job = self.jobs[0]
        
        # Test various filter combinations
        filter_configs = [
            {'location': 'Paris, France'},
            {'min_experience': 3, 'max_experience': 7},
            {'location': 'London, UK', 'min_experience': 5}
        ]
        
        for filters in filter_configs:
            matches = self.engine.match_candidates(test_job, top_k=20, filters=filters)
            
            # Verify filters applied
            for match in matches:
                candidate = match['candidate']
                
                if 'location' in filters:
                    if candidate['location'] not in [filters['location'], 'Remote']:
                        if not candidate.get('remote_preference'):
                            raise AssertionError(f"Location filter violated by {candidate['id']}")
                
                if 'min_experience' in filters:
                    if candidate['years_experience'] < filters['min_experience']:
                        raise AssertionError(f"Min experience filter violated by {candidate['id']}")
                
                if 'max_experience' in filters:
                    if candidate['years_experience'] > filters['max_experience']:
                        raise AssertionError(f"Max experience filter violated by {candidate['id']}")
        
        self.logger.log(f"Tested {len(filter_configs)} filter configurations")
    
    def test_explainability_integration(self):
        """Test explainability system integration"""
        test_job = self.jobs[0]
        matches = self.engine.match_candidates(test_job, top_k=5)
        
        if not matches:
            self.logger.log("No matches to explain - skipping", "WARN")
            return
        
        explained_count = 0
        
        for match in matches:
            explanation = ExplainabilityEngine.generate_explanation(match)
            
            # Verify all components present
            if 'summary' in explanation and 'recommendation' in explanation:
                explained_count += 1
        
        if explained_count != len(matches):
            raise AssertionError(
                f"Only {explained_count}/{len(matches)} matches explained successfully"
            )
        
        self.logger.log(f"Successfully explained {explained_count} matches")
    
    def test_data_consistency(self):
        """Test data consistency across components"""
        # Verify engine has correct candidate count
        engine_count = len(self.engine.candidates_map)
        actual_count = len(self.candidates)
        
        TestAssertion.assert_equals(
            engine_count, actual_count,
            "Engine candidate count matches data"
        )
        
        # Verify dormant detector has correct count
        dormant_actual = sum(1 for c in self.candidates if c['is_dormant'])
        dormant_detector = len(self.dormant_detector.dormant_candidates)
        
        TestAssertion.assert_equals(
            dormant_detector, dormant_actual,
            "Dormant detector count matches data"
        )
        
        self.logger.log("Data consistency verified across components")
    
    def test_concurrent_query_simulation(self):
        """Simulate concurrent query load"""
        num_queries = 10
        
        self.logger.log(f"Simulating {num_queries} concurrent queries...")
        
        start = time.time()
        
        for i in range(num_queries):
            job = self.jobs[i % len(self.jobs)]
            self.engine.match_candidates(job, top_k=10)
        
        elapsed = time.time() - start
        avg_time = elapsed / num_queries
        throughput = num_queries / elapsed
        
        self.logger.log(f"Completed in {elapsed:.2f}s")
        self.logger.log(f"Avg: {avg_time:.3f}s per query")
        self.logger.log(f"Throughput: {throughput:.2f} queries/sec")
        
        # Should maintain reasonable performance
        if avg_time > 2.0:
            raise AssertionError(f"Performance degraded: {avg_time:.3f}s avg")
    
    def test_error_recovery(self):
        """Test system handles errors gracefully"""
        # Test 1: Invalid job data
        try:
            invalid_job = {'id': 'INVALID', 'title': 'Test'}
            matches = self.engine.match_candidates(invalid_job, top_k=10)
            # Should handle gracefully without crashing
        except Exception as e:
            self.logger.log(f"Handled invalid job: {type(e).__name__}", "INFO")
        
        # Test 2: Extreme values
        try:
            extreme_job = {
                'id': 'EXTREME',
                'title': 'Test',
                'service_line': 'Digital & Technology',
                'location': 'Paris, France',
                'experience_level': 'Senior',
                'years_experience_min': 0,
                'years_experience_max': 100,
                'description': 'Test',
                'required_skills': []
            }
            matches = self.engine.match_candidates(extreme_job, top_k=10)
            self.logger.log("Handled extreme values successfully")
        except Exception as e:
            self.logger.log(f"Error on extreme values: {e}", "WARN")
    
    def run_all(self):
        """Execute all integration tests"""
        self.setup()
        
        self.logger.section("WORKFLOW TESTS")
        self.runner.run_test("Complete Recruitment Workflow", self.test_complete_recruitment_workflow)
        self.runner.run_test("Batch Job Processing", self.test_batch_job_processing)
        self.runner.run_test("Dormant Talent Workflow", self.test_dormant_talent_workflow)
        
        self.logger.section("INTEGRATION TESTS")
        self.runner.run_test("Filtering Integration", self.test_filtering_integration)
        self.runner.run_test("Explainability Integration", self.test_explainability_integration)
        self.runner.run_test("Data Consistency", self.test_data_consistency)
        
        self.logger.section("PERFORMANCE TESTS")
        self.runner.run_test("Concurrent Query Simulation", self.test_concurrent_query_simulation)
        
        self.logger.section("ROBUSTNESS TESTS")
        self.runner.run_test("Error Recovery", self.test_error_recovery)
        
        return self.runner.get_summary()


def main():
    """Execute integration tests"""
    logger = TestLogger("logs/test_integration.txt", "Integration Tests")
    
    tests = IntegrationTests(logger)
    summary = tests.run_all()
    
    logger.finalize(summary['passed'], summary['failed'])
    
    return summary['failed'] == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)