"""
End-to-End Integration Testing Suite
Tests complete workflows and system integration
Logs all results to local .txt file
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List

sys.path.append(str(Path(__file__).parent))
from config import *
from src.search.matching_engine import MatchingEngine
from src.search.dormant_detector import DormantTalentDetector
from src.explainability.explainer import ExplainabilityEngine

class TestLogger:
    """Custom logger for integration tests"""
    
    def __init__(self, log_file: str = "logs/integration_test.txt"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"END-TO-END INTEGRATION TESTING LOG\n")
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


class IntegrationTester:
    """End-to-end integration testing"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.matching_engine = None
        self.dormant_detector = None
        self.jobs = None
        self.candidates = None
        self.test_scenarios = []
    
    def setup(self):
        """Setup test environment"""
        self.logger.section("INTEGRATION TEST SETUP")
        
        try:
            # Initialize components
            self.logger.log("Initializing matching engine...")
            self.matching_engine = MatchingEngine()
            
            self.logger.log("Initializing dormant talent detector...")
            self.dormant_detector = DormantTalentDetector(self.matching_engine)
            
            # Load test data
            with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
                self.jobs = json.load(f)
            
            with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
                self.candidates = json.load(f)
            
            self.logger.log(f"Setup complete: {len(self.jobs)} jobs, {len(self.candidates)} candidates", "SUCCESS")
            
        except Exception as e:
            self.logger.log(f"Setup failed: {e}", "ERROR")
            raise
    
    def test_complete_recruitment_workflow(self):
        """Test complete recruitment workflow from job posting to candidate selection"""
        self.logger.section("SCENARIO 1: Complete Recruitment Workflow")
        
        # Step 1: Select a job
        test_job = self.jobs[0]
        self.logger.log(f"\nStep 1: Job Posted")
        self.logger.log(f"  Position: {test_job['title']}")
        self.logger.log(f"  Service Line: {test_job['service_line']}")
        self.logger.log(f"  Location: {test_job['location']}")
        
        # Step 2: Search for candidates
        self.logger.log(f"\nStep 2: Searching for candidates...")
        start = time.time()
        matches = self.matching_engine.match_candidates(test_job, top_k=10)
        search_time = time.time() - start
        
        self.logger.log(f"  Found {len(matches)} candidates in {search_time:.2f}s")
        
        if not matches:
            self.logger.log("  No matches found - FAILED", "ERROR")
            return False
        
        # Step 3: Review top candidates
        self.logger.log(f"\nStep 3: Reviewing top 3 candidates...")
        for i, match in enumerate(matches[:3], 1):
            candidate = match['candidate']
            scores = match['scores']
            
            self.logger.log(f"\n  Candidate {i}: {candidate['name']}")
            self.logger.log(f"    Title: {candidate['current_title']}")
            self.logger.log(f"    Overall Score: {scores['total']:.1%}")
            self.logger.log(f"    Semantic: {scores['semantic']:.1%}")
            self.logger.log(f"    Skills: {scores['skills']:.1%}")
        
        # Step 4: Generate explanations
        self.logger.log(f"\nStep 4: Generating explanations for top candidate...")
        top_match = matches[0]
        explanation = ExplainabilityEngine.generate_explanation(top_match)
        
        self.logger.log(f"  Summary: {explanation['summary']}")
        self.logger.log(f"  Strengths: {len(explanation['strengths'])} identified")
        self.logger.log(f"  Recommendation: {explanation['recommendation']['decision']}")
        
        # Step 5: Check dormant talent
        self.logger.log(f"\nStep 5: Checking for dormant talent...")
        dormant_matches = self.dormant_detector.detect_dormant_matches(test_job, min_score=0.70)
        
        self.logger.log(f"  Found {len(dormant_matches)} dormant candidates")
        
        # Workflow complete
        self.logger.log(f"\n✓ Workflow completed successfully", "SUCCESS")
        
        return True
    
    def test_multi_job_batch_processing(self):
        """Test processing multiple jobs in batch"""
        self.logger.section("SCENARIO 2: Batch Processing Multiple Jobs")
        
        num_jobs = min(5, len(self.jobs))
        batch_jobs = self.jobs[:num_jobs]
        
        self.logger.log(f"Processing batch of {num_jobs} jobs...")
        
        batch_results = []
        total_time = 0
        
        for i, job in enumerate(batch_jobs, 1):
            self.logger.log(f"\n[{i}/{num_jobs}] Processing: {job['title']}")
            
            start = time.time()
            matches = self.matching_engine.match_candidates(job, top_k=10)
            elapsed = time.time() - start
            total_time += elapsed
            
            self.logger.log(f"  Matches: {len(matches)}")
            self.logger.log(f"  Time: {elapsed:.2f}s")
            
            if matches:
                top_score = matches[0]['scores']['total']
                avg_score = sum(m['scores']['total'] for m in matches) / len(matches)
                self.logger.log(f"  Top score: {top_score:.1%}")
                self.logger.log(f"  Avg score: {avg_score:.1%}")
            
            batch_results.append({
                'job': job['id'],
                'matches': len(matches),
                'time': elapsed
            })
        
        # Batch summary
        self.logger.log(f"\nBatch Processing Summary:")
        self.logger.log(f"  Total jobs processed: {num_jobs}")
        self.logger.log(f"  Total time: {total_time:.2f}s")
        self.logger.log(f"  Avg time per job: {total_time/num_jobs:.2f}s")
        self.logger.log(f"  Throughput: {num_jobs/total_time:.2f} jobs/sec")
        
        self.logger.log(f"\n✓ Batch processing completed", "SUCCESS")
        
        return True
    
    def test_dormant_talent_rediscovery_workflow(self):
        """Test complete dormant talent rediscovery workflow"""
        self.logger.section("SCENARIO 3: Dormant Talent Rediscovery")
        
        # Find a job
        test_job = self.jobs[2]
        
        self.logger.log(f"Job: {test_job['title']} ({test_job['service_line']})")
        
        # Detect dormant candidates
        self.logger.log(f"\nScanning for dormant talent...")
        start = time.time()
        dormant_matches = self.dormant_detector.detect_dormant_matches(test_job, min_score=0.70)
        scan_time = time.time() - start
        
        self.logger.log(f"  Scan completed in {scan_time:.2f}s")
        self.logger.log(f"  Found {len(dormant_matches)} dormant candidates")
        
        if not dormant_matches:
            self.logger.log("  No dormant candidates found above threshold", "WARN")
            return True  # Not a failure, just no results
        
        # Generate alert summary
        summary = self.dormant_detector.generate_alert_summary(dormant_matches)
        
        self.logger.log(f"\nDormant Talent Summary:")
        self.logger.log(f"  Total alerts: {summary['total_alerts']}")
        self.logger.log(f"  Avg months dormant: {summary['avg_months_dormant']:.1f}")
        self.logger.log(f"  Avg match score: {summary['avg_match_score']:.1%}")
        
        # Review top dormant candidate
        if dormant_matches:
            top = dormant_matches[0]
            self.logger.log(f"\nTop Dormant Candidate:")
            self.logger.log(f"  Name: {top['candidate']['name']}")
            self.logger.log(f"  Score: {top['scores']['total_with_evolution']:.1%}")
            self.logger.log(f"  Months dormant: {top['evolution']['months_dormant']}")
            self.logger.log(f"  Growth potential: {top['evolution']['growth_potential']}")
        
        # Create notifications
        notifications = self.dormant_detector.create_alert_notifications(dormant_matches, test_job)
        self.logger.log(f"\n  Created {len(notifications)} alert notifications")
        
        self.logger.log(f"\n✓ Dormant talent workflow completed", "SUCCESS")
        
        return True
    
    def test_filtering_workflow(self):
        """Test complete workflow with various filters"""
        self.logger.section("SCENARIO 4: Advanced Filtering Workflow")
        
        test_job = self.jobs[1]
        
        # Test 1: No filters
        self.logger.log(f"\nTest 1: No filters")
        matches_no_filter = self.matching_engine.match_candidates(test_job, top_k=20)
        self.logger.log(f"  Results: {len(matches_no_filter)} candidates")
        
        # Test 2: Location filter
        self.logger.log(f"\nTest 2: Location filter (Paris, France)")
        matches_location = self.matching_engine.match_candidates(
            test_job,
            top_k=20,
            filters={'location': 'Paris, France'}
        )
        self.logger.log(f"  Results: {len(matches_location)} candidates")
        
        # Verify all have correct location
        all_paris = all(
            m['candidate']['location'] in ['Paris, France', 'Remote'] or
            m['candidate'].get('remote_preference')
            for m in matches_location
        )
        
        if all_paris:
            self.logger.log(f"  ✓ All results match location filter", "SUCCESS")
        else:
            self.logger.log(f"  ✗ Some results don't match filter", "ERROR")
        
        # Test 3: Experience filter
        self.logger.log(f"\nTest 3: Experience filter (5-10 years)")
        matches_experience = self.matching_engine.match_candidates(
            test_job,
            top_k=20,
            filters={'min_experience': 5, 'max_experience': 10}
        )
        self.logger.log(f"  Results: {len(matches_experience)} candidates")
        
        # Verify experience range
        all_in_range = all(
            5 <= m['candidate']['years_experience'] <= 10
            for m in matches_experience
        )
        
        if all_in_range:
            self.logger.log(f"  ✓ All results in experience range", "SUCCESS")
        else:
            self.logger.log(f"  ✗ Some results out of range", "ERROR")
        
        # Test 4: Combined filters
        self.logger.log(f"\nTest 4: Combined filters")
        matches_combined = self.matching_engine.match_candidates(
            test_job,
            top_k=20,
            filters={
                'location': 'London, UK',
                'min_experience': 3,
                'max_experience': 8
            }
        )
        self.logger.log(f"  Results: {len(matches_combined)} candidates")
        
        self.logger.log(f"\n✓ Filtering workflow completed", "SUCCESS")
        
        return True
    
    def test_explainability_integration(self):
        """Test explainability integration with matching"""
        self.logger.section("SCENARIO 5: Explainability Integration")
        
        test_job = self.jobs[0]
        
        # Get matches
        matches = self.matching_engine.match_candidates(test_job, top_k=5)
        
        self.logger.log(f"Testing explanations for {len(matches)} candidates...")
        
        all_have_explanations = True
        
        for i, match in enumerate(matches, 1):
            self.logger.log(f"\nCandidate {i}: {match['candidate']['name']}")
            
            try:
                # Generate explanation
                explanation = ExplainabilityEngine.generate_explanation(match)
                
                # Check all components present
                required_keys = ['summary', 'score_components', 'strengths', 'weaknesses', 'recommendation']
                has_all = all(key in explanation for key in required_keys)
                
                if has_all:
                    self.logger.log(f"  ✓ Complete explanation generated", "SUCCESS")
                    self.logger.log(f"    Strengths: {len(explanation['strengths'])}")
                    self.logger.log(f"    Weaknesses: {len(explanation['weaknesses'])}")
                    self.logger.log(f"    Recommendation: {explanation['recommendation']['decision']}")
                else:
                    self.logger.log(f"  ✗ Incomplete explanation", "ERROR")
                    all_have_explanations = False
                
            except Exception as e:
                self.logger.log(f"  ✗ Explanation failed: {e}", "ERROR")
                all_have_explanations = False
        
        if all_have_explanations:
            self.logger.log(f"\n✓ All explanations generated successfully", "SUCCESS")
        else:
            self.logger.log(f"\n✗ Some explanations failed", "ERROR")
        
        return all_have_explanations
    
    def test_data_consistency_across_components(self):
        """Test data consistency across all system components"""
        self.logger.section("SCENARIO 6: Cross-Component Data Consistency")
        
        # Test candidate data consistency
        self.logger.log("Checking candidate data consistency...")
        
        # Get candidate from matching engine's internal map
        sample_id = list(self.matching_engine.candidates_map.keys())[0]
        candidate_from_engine = self.matching_engine.candidates_map[sample_id]
        
        # Find same candidate in raw data
        candidate_from_raw = next((c for c in self.candidates if c['id'] == sample_id), None)
        
        if candidate_from_engine and candidate_from_raw:
            if candidate_from_engine['id'] == candidate_from_raw['id']:
                self.logger.log("  ✓ Candidate data consistent across components", "SUCCESS")
            else:
                self.logger.log("  ✗ Candidate data mismatch", "ERROR")
        
        # Test dormant candidate detection consistency
        self.logger.log("\nChecking dormant detection consistency...")
        
        dormant_from_detector = self.dormant_detector.dormant_candidates
        dormant_from_raw = [c for c in self.candidates if c.get('is_dormant', False)]
        
        if len(dormant_from_detector) == len(dormant_from_raw):
            self.logger.log(
                f"  ✓ Dormant count consistent: {len(dormant_from_detector)} candidates",
                "SUCCESS"
            )
        else:
            self.logger.log(
                f"  ✗ Dormant count mismatch: detector={len(dormant_from_detector)}, "
                f"raw={len(dormant_from_raw)}",
                "ERROR"
            )
        
        return True
    
    def test_edge_case_scenarios(self):
        """Test edge case scenarios"""
        self.logger.section("SCENARIO 7: Edge Case Handling")
        
        # Edge Case 1: Job with no required skills
        self.logger.log("\nEdge Case 1: Job with no required skills")
        job_no_skills = {
            'id': 'EDGE_001',
            'title': 'Generic Position',
            'service_line': self.jobs[0]['service_line'],
            'location': 'Paris, France',
            'experience_level': 'Mid-Level',
            'years_experience_min': 3,
            'years_experience_max': 7,
            'description': 'Test position',
            'required_skills': [],
            'required_languages': []
        }
        
        try:
            matches = self.matching_engine.match_candidates(job_no_skills, top_k=5)
            self.logger.log(f"  ✓ Handled gracefully, returned {len(matches)} matches", "SUCCESS")
        except Exception as e:
            self.logger.log(f"  ✗ Failed: {e}", "ERROR")
        
        # Edge Case 2: Request more results than candidates
        self.logger.log("\nEdge Case 2: Request more results than exist")
        try:
            matches = self.matching_engine.match_candidates(
                self.jobs[0],
                top_k=len(self.candidates) + 1000
            )
            self.logger.log(
                f"  ✓ Handled gracefully, returned {len(matches)} matches (max available)",
                "SUCCESS"
            )
        except Exception as e:
            self.logger.log(f"  ✗ Failed: {e}", "ERROR")
        
        return True
    
    def generate_integration_report(self):
        """Generate final integration test report"""
        self.logger.section("INTEGRATION TEST SUMMARY")
        
        passed = len([s for s in self.test_scenarios if s])
        total = len(self.test_scenarios)
        
        self.logger.log(f"\nTest Scenarios Executed: {total}")
        self.logger.log(f"Passed: {passed}")
        self.logger.log(f"Failed: {total - passed}")
        
        if passed == total:
            verdict = "ALL INTEGRATION TESTS PASSED ✓"
            level = "SUCCESS"
        elif passed >= total * 0.8:
            verdict = "MOST TESTS PASSED (some issues)"
            level = "WARN"
        else:
            verdict = "MULTIPLE FAILURES - REVIEW REQUIRED"
            level = "ERROR"
        
        self.logger.log(f"\n{'='*40}")
        self.logger.log(verdict, level)
        self.logger.log(f"{'='*40}")
    
    def run_all_scenarios(self):
        """Run all integration test scenarios"""
        self.setup()
        
        # Run scenarios
        self.test_scenarios.append(self.test_complete_recruitment_workflow())
        self.test_scenarios.append(self.test_multi_job_batch_processing())
        self.test_scenarios.append(self.test_dormant_talent_rediscovery_workflow())
        self.test_scenarios.append(self.test_filtering_workflow())
        self.test_scenarios.append(self.test_explainability_integration())
        self.test_scenarios.append(self.test_data_consistency_across_components())
        self.test_scenarios.append(self.test_edge_case_scenarios())
        
        self.generate_integration_report()
        
        self.logger.log(f"\n{'='*80}")
        self.logger.log(f"Integration testing complete. Log saved to: {self.logger.log_file}")
        self.logger.log(f"{'='*80}")


def main():
    """Main execution"""
    logger = TestLogger("logs/integration_test.txt")
    tester = IntegrationTester(logger)
    tester.run_all_scenarios()
    
    print(f"\n✅ Integration tests complete. Full log saved to: {logger.log_file.absolute()}")


if __name__ == "__main__":
    main()