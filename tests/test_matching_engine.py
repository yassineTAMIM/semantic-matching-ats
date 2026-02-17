"""
Matching Engine Tests
Tests core matching algorithms, scoring functions, and integration
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_utils import TestLogger, TestAssertion, TestRunner, load_test_data, calculate_statistics
from src.search.matching_engine import MatchingEngine
from config import WEIGHTS


class MatchingEngineTests:
    """Test matching engine components"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.runner = TestRunner(logger)
        self.engine = None
        self.candidates = []
        self.jobs = []
        self.applications = []
    
    def setup(self):
        """Initialize matching engine"""
        self.logger.section("INITIALIZING MATCHING ENGINE")
        
        start = time.time()
        self.engine = MatchingEngine()
        init_time = time.time() - start
        
        self.logger.log(f"Engine initialized in {init_time:.2f}s")
        
        # Load test data
        self.candidates, self.jobs, self.applications = load_test_data()
        
        self.logger.log(f"Loaded {len(self.candidates)} candidates")
        self.logger.log(f"Loaded {len(self.jobs)} jobs")
    
    def test_skills_scoring_perfect_match(self):
        """Test skills scoring with perfect match"""
        candidate = {'skills': ['Python', 'SQL', 'Machine Learning']}
        job = {'required_skills': ['Python', 'SQL', 'Machine Learning']}
        
        score = self.engine._calculate_skills_score(candidate, job)
        
        TestAssertion.assert_equals(score, 1.0, "Perfect skills match")
    
    def test_skills_scoring_partial_match(self):
        """Test skills scoring with partial match"""
        candidate = {'skills': ['Python', 'SQL']}
        job = {'required_skills': ['Python', 'SQL', 'R', 'Tableau']}
        
        score = self.engine._calculate_skills_score(candidate, job)
        
        # Should be 0.5 (2 out of 4)
        TestAssertion.assert_equals(score, 0.5, "Partial skills match")
    
    def test_skills_scoring_no_match(self):
        """Test skills scoring with no match"""
        candidate = {'skills': ['Java', 'C++']}
        job = {'required_skills': ['Python', 'R']}
        
        score = self.engine._calculate_skills_score(candidate, job)
        
        TestAssertion.assert_equals(score, 0.0, "No skills match")
    
    def test_skills_scoring_case_insensitive(self):
        """Test skills matching is case-insensitive"""
        candidate = {'skills': ['PYTHON', 'sql']}
        job = {'required_skills': ['python', 'SQL']}
        
        score = self.engine._calculate_skills_score(candidate, job)
        
        TestAssertion.assert_equals(score, 1.0, "Case-insensitive matching")
    
    def test_skills_scoring_empty_requirements(self):
        """Test skills scoring with no requirements"""
        candidate = {'skills': ['Python']}
        job = {'required_skills': []}
        
        score = self.engine._calculate_skills_score(candidate, job)
        
        # Should default to 0.8 when no skills required
        TestAssertion.assert_in_range(score, 0.7, 1.0, "No required skills")
    
    def test_experience_scoring_in_range(self):
        """Test experience scoring within range"""
        candidate = {'years_experience': 5}
        job = {'years_experience_min': 3, 'years_experience_max': 7}
        
        score = self.engine._calculate_experience_score(candidate, job)
        
        TestAssertion.assert_equals(score, 1.0, "Experience in range")
    
    def test_experience_scoring_at_boundaries(self):
        """Test experience scoring at min/max boundaries"""
        candidate_min = {'years_experience': 3}
        candidate_max = {'years_experience': 7}
        job = {'years_experience_min': 3, 'years_experience_max': 7}
        
        score_min = self.engine._calculate_experience_score(candidate_min, job)
        score_max = self.engine._calculate_experience_score(candidate_max, job)
        
        TestAssertion.assert_equals(score_min, 1.0, "Experience at minimum")
        TestAssertion.assert_equals(score_max, 1.0, "Experience at maximum")
    
    def test_experience_scoring_underqualified(self):
        """Test experience scoring for underqualified candidate"""
        candidate = {'years_experience': 1}
        job = {'years_experience_min': 5, 'years_experience_max': 10}
        
        score = self.engine._calculate_experience_score(candidate, job)
        
        # Should be penalized but not zero
        TestAssertion.assert_in_range(score, 0.1, 0.7, "Underqualified penalty")
    
    def test_experience_scoring_overqualified(self):
        """Test experience scoring for overqualified candidate"""
        candidate = {'years_experience': 20}
        job = {'years_experience_min': 3, 'years_experience_max': 7}
        
        score = self.engine._calculate_experience_score(candidate, job)
        
        # Should be penalized but less than underqualified
        TestAssertion.assert_in_range(score, 0.5, 1.0, "Overqualified penalty")
    
    def test_location_scoring_exact_match(self):
        """Test location scoring with exact match"""
        candidate = {'location': 'Paris, France', 'remote_preference': False}
        job = {'location': 'Paris, France', 'remote': False}
        
        score = self.engine._calculate_location_score(candidate, job)
        
        TestAssertion.assert_equals(score, 1.0, "Exact location match")
    
    def test_location_scoring_remote_job(self):
        """Test location scoring for remote job"""
        candidate = {'location': 'London, UK', 'remote_preference': False}
        job = {'location': 'Paris, France', 'remote': True}
        
        score = self.engine._calculate_location_score(candidate, job)
        
        # Remote jobs should score high regardless of location
        TestAssertion.assert_in_range(score, 0.8, 1.0, "Remote job flexibility")
    
    def test_location_scoring_mismatch(self):
        """Test location scoring with mismatch"""
        candidate = {'location': 'Madrid, Spain', 'remote_preference': False}
        job = {'location': 'Berlin, Germany', 'remote': False}
        
        score = self.engine._calculate_location_score(candidate, job)
        
        # Should be low for non-remote mismatch
        TestAssertion.assert_in_range(score, 0.0, 0.5, "Location mismatch penalty")
    
    def test_weighted_scoring(self):
        """Test weighted total score calculation"""
        # Verify weights sum to 1
        total_weight = sum(WEIGHTS.values())
        
        TestAssertion.assert_in_range(
            total_weight, 0.99, 1.01, 
            "Weights sum to 1.0"
        )
    
    def test_end_to_end_matching(self):
        """Test complete matching workflow"""
        test_job = self.jobs[0]
        
        start = time.time()
        matches = self.engine.match_candidates(test_job, top_k=10)
        elapsed = time.time() - start
        
        # Should return results
        TestAssertion.assert_not_empty(matches, "Returns matches")
        
        # Should return requested number (or less if not enough applicants)
        if len(matches) > 10:
            raise AssertionError(f"Returned {len(matches)} matches, requested max 10")
        
        # Should be sorted by score
        scores = [m['scores']['total'] for m in matches]
        for i in range(len(scores) - 1):
            if scores[i] < scores[i + 1]:
                raise AssertionError("Results not sorted by score descending")
        
        # Scores should be in valid range
        for score in scores:
            TestAssertion.assert_in_range(score, 0.0, 1.0, "Score in valid range")
        
        # Should be fast (<2 seconds for real-time use)
        if elapsed > 2.0:
            self.logger.log(f"Performance warning: {elapsed:.2f}s (expected <2s)", "WARN")
        
        self.logger.log(f"Matching completed in {elapsed:.3f}s")
    
    def test_match_result_structure(self):
        """Test match result contains all required fields"""
        test_job = self.jobs[0]
        matches = self.engine.match_candidates(test_job, top_k=1)
        
        if not matches:
            # No applicants - skip test
            self.logger.log("No applicants for job - skipping structure test", "WARN")
            return
        
        match = matches[0]
        
        # Check required top-level fields
        required_fields = ['candidate', 'scores', 'breakdown']
        for field in required_fields:
            if field not in match:
                raise AssertionError(f"Missing field '{field}' in match result")
        
        # Check scores structure
        score_fields = ['semantic', 'skills', 'experience', 'location', 'total']
        for field in score_fields:
            if field not in match['scores']:
                raise AssertionError(f"Missing score '{field}'")
        
        # Check breakdown structure
        breakdown_fields = ['semantic_similarity', 'skills_match', 'experience_match', 'location_match']
        for field in breakdown_fields:
            if field not in match['breakdown']:
                raise AssertionError(f"Missing breakdown '{field}'")
    
    def test_location_filtering(self):
        """Test location filter works correctly"""
        test_job = self.jobs[0]
        target_location = 'Paris, France'
        
        matches = self.engine.match_candidates(
            test_job,
            top_k=20,
            filters={'location': target_location}
        )
        
        # All results should match location (or be remote)
        for match in matches:
            candidate_loc = match['candidate']['location']
            if candidate_loc != target_location and candidate_loc != 'Remote':
                # Check if remote preference
                if not match['candidate'].get('remote_preference'):
                    raise AssertionError(
                        f"Location filter failed: got {candidate_loc}"
                    )
    
    def test_experience_filtering(self):
        """Test experience filter works correctly"""
        test_job = self.jobs[0]
        min_exp, max_exp = 5, 10
        
        matches = self.engine.match_candidates(
            test_job,
            top_k=20,
            filters={'min_experience': min_exp, 'max_experience': max_exp}
        )
        
        # All results should be in experience range
        for match in matches:
            exp = match['candidate']['years_experience']
            TestAssertion.assert_in_range(
                exp, min_exp, max_exp,
                f"Experience filter for candidate {match['candidate']['id']}"
            )
    
    def test_performance_benchmark(self):
        """Benchmark matching performance"""
        self.logger.subsection("PERFORMANCE BENCHMARK")
        
        test_job = self.jobs[0]
        times = []
        
        # Run 10 queries
        for i in range(10):
            start = time.time()
            self.engine.match_candidates(test_job, top_k=10)
            times.append(time.time() - start)
        
        stats = calculate_statistics(times)
        
        self.logger.log(f"Avg query time: {stats['mean']:.3f}s")
        self.logger.log(f"P95 query time: {stats['p95']:.3f}s")
        self.logger.log(f"Max query time: {stats['max']:.3f}s")
        
        # Performance requirement: <2s average
        if stats['mean'] > 2.0:
            self.logger.log(f"Performance below target: {stats['mean']:.3f}s", "WARN")
    
    def run_all(self):
        """Execute all matching engine tests"""
        self.setup()
        
        self.logger.section("SKILLS SCORING TESTS")
        self.runner.run_test("Perfect Skills Match", self.test_skills_scoring_perfect_match)
        self.runner.run_test("Partial Skills Match", self.test_skills_scoring_partial_match)
        self.runner.run_test("No Skills Match", self.test_skills_scoring_no_match)
        self.runner.run_test("Case Insensitive Matching", self.test_skills_scoring_case_insensitive)
        self.runner.run_test("Empty Requirements", self.test_skills_scoring_empty_requirements)
        
        self.logger.section("EXPERIENCE SCORING TESTS")
        self.runner.run_test("Experience In Range", self.test_experience_scoring_in_range)
        self.runner.run_test("Experience At Boundaries", self.test_experience_scoring_at_boundaries)
        self.runner.run_test("Underqualified Penalty", self.test_experience_scoring_underqualified)
        self.runner.run_test("Overqualified Penalty", self.test_experience_scoring_overqualified)
        
        self.logger.section("LOCATION SCORING TESTS")
        self.runner.run_test("Exact Location Match", self.test_location_scoring_exact_match)
        self.runner.run_test("Remote Job Flexibility", self.test_location_scoring_remote_job)
        self.runner.run_test("Location Mismatch", self.test_location_scoring_mismatch)
        
        self.logger.section("INTEGRATION TESTS")
        self.runner.run_test("Weighted Scoring", self.test_weighted_scoring)
        self.runner.run_test("End-to-End Matching", self.test_end_to_end_matching)
        self.runner.run_test("Match Result Structure", self.test_match_result_structure)
        
        self.logger.section("FILTERING TESTS")
        self.runner.run_test("Location Filtering", self.test_location_filtering)
        self.runner.run_test("Experience Filtering", self.test_experience_filtering)
        
        self.test_performance_benchmark()
        
        return self.runner.get_summary()


def main():
    """Execute matching engine tests"""
    logger = TestLogger("logs/test_matching_engine.txt", "Matching Engine Tests")
    
    tests = MatchingEngineTests(logger)
    summary = tests.run_all()
    
    logger.finalize(summary['passed'], summary['failed'])
    
    return summary['failed'] == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)