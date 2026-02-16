"""
Matching Engine Unit Tests
Comprehensive testing of matching algorithms and scoring functions
Logs all results to local .txt file
"""

import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import time

sys.path.append(str(Path(__file__).parent))
from config import *
from src.search.matching_engine import MatchingEngine

class TestLogger:
    """Custom logger for unit tests"""
    
    def __init__(self, log_file: str = "logs/matching_engine_tests.txt"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"MATCHING ENGINE UNIT TESTS LOG\n")
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
    
    def test_result(self, test_name: str, passed: bool, details: str = ""):
        level = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        self.log(f"{symbol} {test_name}: {details}", level)
        return passed


class MatchingEngineTests:
    """Unit tests for matching engine components"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.engine = None
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def setup(self):
        """Setup test environment"""
        self.logger.section("TEST SETUP")
        
        try:
            self.engine = MatchingEngine()
            self.logger.log("Matching engine initialized successfully", "SUCCESS")
            
            # Load test data
            with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
                self.jobs = json.load(f)
            
            with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
                self.candidates = json.load(f)
            
            self.logger.log(f"Loaded {len(self.jobs)} jobs and {len(self.candidates)} candidates", "SUCCESS")
            
        except Exception as e:
            self.logger.log(f"Setup failed: {e}", "ERROR")
            raise
    
    def test_skills_scoring(self):
        """Test skills overlap scoring function"""
        self.logger.section("TEST: Skills Scoring Function")
        
        # Test Case 1: Perfect match
        candidate1 = {
            'skills': ['Python', 'SQL', 'Machine Learning', 'Data Analysis']
        }
        job1 = {
            'required_skills': ['Python', 'SQL', 'Machine Learning', 'Data Analysis']
        }
        
        score1 = self.engine._calculate_skills_score(candidate1, job1)
        passed = self.logger.test_result(
            "Perfect skills match",
            score1 == 1.0,
            f"Expected 1.0, got {score1:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 2: Partial match
        candidate2 = {
            'skills': ['Python', 'SQL']
        }
        job2 = {
            'required_skills': ['Python', 'SQL', 'R', 'Tableau']
        }
        
        score2 = self.engine._calculate_skills_score(candidate2, job2)
        passed = self.logger.test_result(
            "Partial skills match (50%)",
            0.3 <= score2 <= 0.7,  # Should be around 0.5
            f"Expected ~0.5, got {score2:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 3: No match
        candidate3 = {
            'skills': ['Java', 'C++', 'Ruby']
        }
        job3 = {
            'required_skills': ['Python', 'R', 'SPSS']
        }
        
        score3 = self.engine._calculate_skills_score(candidate3, job3)
        passed = self.logger.test_result(
            "No skills match",
            score3 < 0.3,
            f"Expected <0.3, got {score3:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 4: Case insensitivity
        candidate4 = {
            'skills': ['PYTHON', 'sql', 'Machine Learning']
        }
        job4 = {
            'required_skills': ['python', 'SQL', 'machine learning']
        }
        
        score4 = self.engine._calculate_skills_score(candidate4, job4)
        passed = self.logger.test_result(
            "Case-insensitive matching",
            score4 == 1.0,
            f"Expected 1.0, got {score4:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 5: Empty required skills
        candidate5 = {
            'skills': ['Python', 'SQL']
        }
        job5 = {
            'required_skills': []
        }
        
        score5 = self.engine._calculate_skills_score(candidate5, job5)
        passed = self.logger.test_result(
            "No required skills (should be 1.0)",
            score5 == 1.0,
            f"Expected 1.0, got {score5:.4f}"
        )
        self.record_result(passed)
    
    def test_experience_scoring(self):
        """Test experience matching scoring function"""
        self.logger.section("TEST: Experience Scoring Function")
        
        # Test Case 1: Within range
        candidate1 = {'years_experience': 5}
        job1 = {'years_experience_min': 3, 'years_experience_max': 7}
        
        score1 = self.engine._calculate_experience_score(candidate1, job1)
        passed = self.logger.test_result(
            "Experience within range",
            score1 == 1.0,
            f"Expected 1.0, got {score1:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 2: At minimum
        candidate2 = {'years_experience': 3}
        job2 = {'years_experience_min': 3, 'years_experience_max': 7}
        
        score2 = self.engine._calculate_experience_score(candidate2, job2)
        passed = self.logger.test_result(
            "Experience at minimum",
            score2 == 1.0,
            f"Expected 1.0, got {score2:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 3: Slightly under-qualified
        candidate3 = {'years_experience': 2}
        job3 = {'years_experience_min': 3, 'years_experience_max': 7}
        
        score3 = self.engine._calculate_experience_score(candidate3, job3)
        passed = self.logger.test_result(
            "Slightly under-qualified",
            0.6 <= score3 < 1.0,
            f"Expected 0.6-1.0, got {score3:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 4: Significantly under-qualified
        candidate4 = {'years_experience': 0}
        job4 = {'years_experience_min': 5, 'years_experience_max': 10}
        
        score4 = self.engine._calculate_experience_score(candidate4, job4)
        passed = self.logger.test_result(
            "Significantly under-qualified",
            score4 < 0.3,
            f"Expected <0.3, got {score4:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 5: Over-qualified
        candidate5 = {'years_experience': 15}
        job5 = {'years_experience_min': 3, 'years_experience_max': 7}
        
        score5 = self.engine._calculate_experience_score(candidate5, job5)
        passed = self.logger.test_result(
            "Over-qualified",
            score5 < 1.0,
            f"Expected <1.0, got {score5:.4f}"
        )
        self.record_result(passed)
    
    def test_location_scoring(self):
        """Test location matching scoring function"""
        self.logger.section("TEST: Location Scoring Function")
        
        # Test Case 1: Exact match
        candidate1 = {'location': 'Paris, France', 'remote_preference': False}
        job1 = {'location': 'Paris, France', 'remote': False}
        
        score1 = self.engine._calculate_location_score(candidate1, job1)
        passed = self.logger.test_result(
            "Exact location match",
            score1 == 1.0,
            f"Expected 1.0, got {score1:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 2: Remote job
        candidate2 = {'location': 'London, UK', 'remote_preference': False}
        job2 = {'location': 'Remote', 'remote': True}
        
        score2 = self.engine._calculate_location_score(candidate2, job2)
        passed = self.logger.test_result(
            "Remote job (any location)",
            score2 == 1.0,
            f"Expected 1.0, got {score2:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 3: Remote candidate
        candidate3 = {'location': 'Remote', 'remote_preference': True}
        job3 = {'location': 'Paris, France', 'remote': False}
        
        score3 = self.engine._calculate_location_score(candidate3, job3)
        passed = self.logger.test_result(
            "Remote candidate for office job",
            score3 >= 0.6,  # Should get partial credit
            f"Expected >=0.6, got {score3:.4f}"
        )
        self.record_result(passed)
        
        # Test Case 4: Different locations
        candidate4 = {'location': 'Madrid, Spain', 'remote_preference': False}
        job4 = {'location': 'Berlin, Germany', 'remote': False}
        
        score4 = self.engine._calculate_location_score(candidate4, job4)
        passed = self.logger.test_result(
            "Different locations",
            score4 < 0.5,
            f"Expected <0.5, got {score4:.4f}"
        )
        self.record_result(passed)
    
    def test_weighted_scoring(self):
        """Test weighted total score calculation"""
        self.logger.section("TEST: Weighted Total Scoring")
        
        # Verify weights sum to 1.0
        total_weight = sum(WEIGHTS.values())
        passed = self.logger.test_result(
            "Weights sum to 1.0",
            abs(total_weight - 1.0) < 0.001,
            f"Expected 1.0, got {total_weight:.6f}"
        )
        self.record_result(passed)
        
        # Test weighted calculation
        semantic_score = 0.8
        skills_score = 0.9
        experience_score = 1.0
        location_score = 0.7
        
        expected_total = (
            WEIGHTS['semantic'] * semantic_score +
            WEIGHTS['skills'] * skills_score +
            WEIGHTS['experience'] * experience_score +
            WEIGHTS['location'] * location_score
        )
        
        # Manual calculation to verify
        manual_total = (0.70 * 0.8) + (0.20 * 0.9) + (0.07 * 1.0) + (0.03 * 0.7)
        
        passed = self.logger.test_result(
            "Weighted score calculation",
            abs(expected_total - manual_total) < 0.001,
            f"Expected {manual_total:.4f}, got {expected_total:.4f}"
        )
        self.record_result(passed)
    
    def test_end_to_end_matching(self):
        """Test end-to-end matching with real data"""
        self.logger.section("TEST: End-to-End Matching")
        
        # Test with first job
        test_job = self.jobs[0]
        
        try:
            start_time = time.time()
            matches = self.engine.match_candidates(test_job, top_k=10)
            elapsed = time.time() - start_time
            
            # Test 1: Returns results
            passed = self.logger.test_result(
                "Returns matching results",
                len(matches) > 0,
                f"Got {len(matches)} matches"
            )
            self.record_result(passed)
            
            # Test 2: Returns correct number
            passed = self.logger.test_result(
                "Returns requested number of results",
                len(matches) <= 10,
                f"Requested 10, got {len(matches)}"
            )
            self.record_result(passed)
            
            # Test 3: Results are sorted
            scores = [m['scores']['total'] for m in matches]
            is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
            passed = self.logger.test_result(
                "Results sorted by score (descending)",
                is_sorted,
                f"Scores: {[f'{s:.3f}' for s in scores[:5]]}"
            )
            self.record_result(passed)
            
            # Test 4: Scores in valid range
            all_valid = all(0 <= m['scores']['total'] <= 1 for m in matches)
            passed = self.logger.test_result(
                "All scores in range [0,1]",
                all_valid,
                f"Range: [{min(scores):.3f}, {max(scores):.3f}]"
            )
            self.record_result(passed)
            
            # Test 5: Performance
            passed = self.logger.test_result(
                "Performance < 5 seconds",
                elapsed < 5.0,
                f"Took {elapsed:.2f}s"
            )
            self.record_result(passed)
            
            # Test 6: Required fields present
            required_fields = ['candidate', 'scores', 'breakdown']
            all_present = all(
                all(field in match for field in required_fields)
                for match in matches
            )
            passed = self.logger.test_result(
                "All required fields present",
                all_present,
                f"Fields: {required_fields}"
            )
            self.record_result(passed)
            
        except Exception as e:
            self.logger.log(f"End-to-end matching failed: {e}", "ERROR")
            self.record_result(False)
    
    def test_filtering(self):
        """Test filtering functionality"""
        self.logger.section("TEST: Filtering Functionality")
        
        test_job = self.jobs[0]
        
        # Test location filter
        try:
            filters = {'location': 'Paris, France'}
            matches = self.engine.match_candidates(test_job, top_k=10, filters=filters)
            
            # Check all matches have correct location or are remote
            valid_locations = all(
                m['candidate']['location'] == 'Paris, France' or
                m['candidate']['location'] == 'Remote' or
                m['candidate'].get('remote_preference')
                for m in matches
            )
            
            passed = self.logger.test_result(
                "Location filtering works",
                valid_locations,
                f"All {len(matches)} matches have valid locations"
            )
            self.record_result(passed)
            
        except Exception as e:
            self.logger.log(f"Location filtering failed: {e}", "ERROR")
            self.record_result(False)
        
        # Test experience filter
        try:
            filters = {'min_experience': 5, 'max_experience': 10}
            matches = self.engine.match_candidates(test_job, top_k=10, filters=filters)
            
            valid_experience = all(
                5 <= m['candidate']['years_experience'] <= 10
                for m in matches
            )
            
            passed = self.logger.test_result(
                "Experience filtering works",
                valid_experience,
                f"All {len(matches)} matches have 5-10 years experience"
            )
            self.record_result(passed)
            
        except Exception as e:
            self.logger.log(f"Experience filtering failed: {e}", "ERROR")
            self.record_result(False)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        self.logger.section("TEST: Edge Cases")
        
        # Test Case 1: Empty skills
        candidate_empty_skills = {
            'id': 'TEST_001',
            'skills': [],
            'years_experience': 5,
            'location': 'Paris, France'
        }
        
        job_with_skills = {
            'required_skills': ['Python', 'SQL'],
            'years_experience_min': 3,
            'years_experience_max': 7,
            'location': 'Paris, France'
        }
        
        try:
            score = self.engine._calculate_skills_score(candidate_empty_skills, job_with_skills)
            passed = self.logger.test_result(
                "Handles empty candidate skills",
                0 <= score <= 1,
                f"Score: {score:.4f}"
            )
            self.record_result(passed)
        except Exception as e:
            self.logger.log(f"Failed on empty skills: {e}", "FAIL")
            self.record_result(False)
        
        # Test Case 2: Extreme experience values
        candidate_extreme = {'years_experience': 50}
        job_normal = {'years_experience_min': 3, 'years_experience_max': 7}
        
        try:
            score = self.engine._calculate_experience_score(candidate_extreme, job_normal)
            passed = self.logger.test_result(
                "Handles extreme experience values",
                0 <= score <= 1,
                f"Score: {score:.4f}"
            )
            self.record_result(passed)
        except Exception as e:
            self.logger.log(f"Failed on extreme experience: {e}", "FAIL")
            self.record_result(False)
    
    def test_score_breakdown(self):
        """Test score breakdown generation"""
        self.logger.section("TEST: Score Breakdown")
        
        test_job = self.jobs[0]
        matches = self.engine.match_candidates(test_job, top_k=1)
        
        if matches:
            breakdown = matches[0]['breakdown']
            
            # Check all components present
            required_components = ['semantic_similarity', 'skills_match', 'experience_match', 'location_match']
            all_present = all(comp in breakdown for comp in required_components)
            
            passed = self.logger.test_result(
                "All breakdown components present",
                all_present,
                f"Components: {list(breakdown.keys())}"
            )
            self.record_result(passed)
            
            # Check matched/missing skills reported
            if 'skills_match' in breakdown:
                has_matched = 'matched_skills' in breakdown['skills_match']
                has_missing = 'missing_skills' in breakdown['skills_match']
                
                passed = self.logger.test_result(
                    "Skills breakdown has matched and missing",
                    has_matched and has_missing,
                    f"Has matched: {has_matched}, Has missing: {has_missing}"
                )
                self.record_result(passed)
    
    def record_result(self, passed: bool):
        """Record test result"""
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        self.test_results.append(passed)
    
    def generate_summary(self):
        """Generate test summary"""
        self.logger.section("TEST SUMMARY")
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.logger.log(f"Total Tests Run: {total_tests}")
        self.logger.log(f"Passed: {self.passed_tests}")
        self.logger.log(f"Failed: {self.failed_tests}")
        self.logger.log(f"Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate == 100:
            verdict = "ALL TESTS PASSED ✓"
            level = "SUCCESS"
        elif pass_rate >= 80:
            verdict = "MOSTLY PASSING (some failures)"
            level = "WARN"
        else:
            verdict = "MULTIPLE FAILURES - ATTENTION NEEDED"
            level = "ERROR"
        
        self.logger.log(f"\n{'='*40}")
        self.logger.log(verdict, level)
        self.logger.log(f"{'='*40}")
    
    def run_all_tests(self):
        """Run all unit tests"""
        self.setup()
        
        self.test_skills_scoring()
        self.test_experience_scoring()
        self.test_location_scoring()
        self.test_weighted_scoring()
        self.test_end_to_end_matching()
        self.test_filtering()
        self.test_edge_cases()
        self.test_score_breakdown()
        
        self.generate_summary()
        
        self.logger.log(f"\n{'='*80}")
        self.logger.log(f"Unit tests complete. Log saved to: {self.logger.log_file}")
        self.logger.log(f"{'='*80}")


def main():
    """Main execution"""
    logger = TestLogger("logs/matching_engine_tests.txt")
    tests = MatchingEngineTests(logger)
    tests.run_all_tests()
    
    print(f"\n✅ Tests complete. Full log saved to: {logger.log_file.absolute()}")


if __name__ == "__main__":
    main()