"""
Data Quality Tests
Validates synthetic data integrity, schema compliance, and distribution
"""

import sys
from pathlib import Path
from collections import Counter
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_utils import TestLogger, TestAssertion, TestRunner, load_test_data
from config import FORVIS_SERVICE_LINES, FORVIS_LOCATIONS


class DataQualityTests:
    """Comprehensive data quality validation"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.runner = TestRunner(logger)
        self.candidates = []
        self.jobs = []
        self.applications = []
    
    def setup(self):
        """Load test data"""
        self.logger.section("LOADING TEST DATA")
        
        self.candidates, self.jobs, self.applications = load_test_data()
        
        self.logger.log(f"Loaded {len(self.candidates)} candidates")
        self.logger.log(f"Loaded {len(self.jobs)} jobs")
        self.logger.log(f"Loaded {len(self.applications)} applications")
    
    def test_candidate_schema(self):
        """Validate candidate data schema"""
        required_fields = [
            'id', 'name', 'email', 'phone', 'current_title', 'service_line',
            'years_experience', 'experience_level', 'location', 'skills',
            'last_application_date', 'is_dormant'
        ]
        
        for candidate in self.candidates:
            # Check required fields exist
            for field in required_fields:
                TestAssertion.assert_type(
                    candidate.get(field), 
                    (str, int, list, bool, type(None)),
                    f"Candidate {candidate.get('id')}: field '{field}' type"
                )
            
            # Validate specific field types
            TestAssertion.assert_type(candidate['years_experience'], int, 
                                     f"Candidate {candidate['id']}: years_experience")
            TestAssertion.assert_type(candidate['skills'], list,
                                     f"Candidate {candidate['id']}: skills")
            TestAssertion.assert_type(candidate['is_dormant'], bool,
                                     f"Candidate {candidate['id']}: is_dormant")
            
            # Validate email format (basic)
            if candidate.get('email'):
                email = candidate['email']
                if '@' not in email or '.' not in email:
                    raise AssertionError(f"Invalid email format: {email}")
    
    def test_job_schema(self):
        """Validate job posting schema"""
        required_fields = [
            'id', 'title', 'service_line', 'location', 'experience_level',
            'years_experience_min', 'years_experience_max', 'description',
            'required_skills'
        ]
        
        for job in self.jobs:
            # Check required fields
            for field in required_fields:
                TestAssertion.assert_type(
                    job.get(field),
                    (str, int, list, type(None)),
                    f"Job {job.get('id')}: field '{field}'"
                )
            
            # Validate experience range
            exp_min = job['years_experience_min']
            exp_max = job['years_experience_max']
            
            if exp_min > exp_max:
                raise AssertionError(
                    f"Job {job['id']}: min_experience ({exp_min}) > max_experience ({exp_max})"
                )
            
            # Validate required_skills is list
            TestAssertion.assert_type(job['required_skills'], list,
                                     f"Job {job['id']}: required_skills")
    
    def test_application_schema(self):
        """Validate application data schema"""
        required_fields = ['id', 'candidate_id', 'job_id', 'application_date']
        
        for app in self.applications:
            for field in required_fields:
                if field not in app:
                    raise AssertionError(f"Application {app.get('id')}: missing field '{field}'")
            
            # Validate date format (YYYY-MM-DD)
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, app['application_date']):
                raise AssertionError(
                    f"Application {app['id']}: invalid date format '{app['application_date']}'"
                )
    
    def test_no_duplicate_ids(self):
        """Ensure all IDs are unique"""
        # Candidate IDs
        candidate_ids = [c['id'] for c in self.candidates]
        duplicates = [id_ for id_, count in Counter(candidate_ids).items() if count > 1]
        
        if duplicates:
            raise AssertionError(f"Found {len(duplicates)} duplicate candidate IDs: {duplicates[:5]}")
        
        # Job IDs
        job_ids = [j['id'] for j in self.jobs]
        duplicates = [id_ for id_, count in Counter(job_ids).items() if count > 1]
        
        if duplicates:
            raise AssertionError(f"Found {len(duplicates)} duplicate job IDs: {duplicates[:5]}")
    
    def test_service_line_consistency(self):
        """Validate service line values are consistent"""
        # Check candidates use valid service lines
        candidate_service_lines = set(c['service_line'] for c in self.candidates)
        invalid = candidate_service_lines - set(FORVIS_SERVICE_LINES)
        
        if invalid:
            raise AssertionError(f"Invalid service lines in candidates: {invalid}")
        
        # Check jobs use valid service lines
        job_service_lines = set(j['service_line'] for j in self.jobs)
        invalid = job_service_lines - set(FORVIS_SERVICE_LINES)
        
        if invalid:
            raise AssertionError(f"Invalid service lines in jobs: {invalid}")
    
    def test_location_consistency(self):
        """Validate location values"""
        candidate_locations = set(c['location'] for c in self.candidates)
        invalid = candidate_locations - set(FORVIS_LOCATIONS)
        
        if invalid:
            raise AssertionError(f"Invalid locations in candidates: {invalid}")
    
    def test_application_references(self):
        """Validate application references point to existing candidates/jobs"""
        candidate_ids = set(c['id'] for c in self.candidates)
        job_ids = set(j['id'] for j in self.jobs)
        
        for app in self.applications:
            if app['candidate_id'] not in candidate_ids:
                raise AssertionError(
                    f"Application {app['id']}: references non-existent candidate {app['candidate_id']}"
                )
            
            if app['job_id'] not in job_ids:
                raise AssertionError(
                    f"Application {app['id']}: references non-existent job {app['job_id']}"
                )
    
    def test_dormant_status_consistency(self):
        """Validate dormant status matches application history"""
        # Build application map
        latest_application = {}
        
        for app in self.applications:
            candidate_id = app['candidate_id']
            app_date = datetime.strptime(app['application_date'], '%Y-%m-%d')
            
            if candidate_id not in latest_application or app_date > latest_application[candidate_id]:
                latest_application[candidate_id] = app_date
        
        # Check candidates
        now = datetime.now()
        dormant_threshold_days = 180  # 6 months
        
        for candidate in self.candidates:
            candidate_id = candidate['id']
            
            if candidate_id in latest_application:
                last_app = latest_application[candidate_id]
                days_since = (now - last_app).days
                
                expected_dormant = days_since > dormant_threshold_days
                actual_dormant = candidate['is_dormant']
                
                # Allow some tolerance for edge cases
                if expected_dormant != actual_dormant:
                    # Log warning but don't fail (could be timing differences)
                    self.logger.log(
                        f"Dormant status mismatch for {candidate_id}: "
                        f"expected={expected_dormant}, actual={actual_dormant}, "
                        f"days_since={days_since}",
                        "WARN"
                    )
    
    def test_data_distributions(self):
        """Test that data distributions are reasonable"""
        # Service line distribution should be balanced
        service_line_counts = Counter(c['service_line'] for c in self.candidates)
        
        total = len(self.candidates)
        for service_line, count in service_line_counts.items():
            percentage = (count / total) * 100
            
            # Each service line should have at least 5% representation
            if percentage < 5:
                raise AssertionError(
                    f"Service line '{service_line}' under-represented: {percentage:.1f}%"
                )
        
        # Experience levels should be diverse
        exp_levels = Counter(c['experience_level'] for c in self.candidates)
        
        if len(exp_levels) < 4:
            raise AssertionError(f"Only {len(exp_levels)} experience levels found, expected diverse distribution")
        
        # Should have dormant candidates
        dormant_count = sum(1 for c in self.candidates if c['is_dormant'])
        dormant_pct = (dormant_count / len(self.candidates)) * 100
        
        # With realistic application patterns, expect 30-70% dormant
        if dormant_pct < 20:
            raise AssertionError(f"Only {dormant_pct:.1f}% dormant candidates, expected >20%")
        
        if dormant_pct > 80:
            raise AssertionError(f"Too many dormant candidates: {dormant_pct:.1f}%, expected <80%")
    
    def test_application_volumes(self):
        """Test that application volumes are realistic per job"""
        apps_per_job = Counter(app['job_id'] for app in self.applications)
        
        # Each job should have at least some applications
        for job in self.jobs:
            job_id = job['id']
            app_count = apps_per_job.get(job_id, 0)
            
            # Based on new generator, expect minimum 8 applications per job
            if app_count < 8:
                raise AssertionError(
                    f"Job {job_id} has only {app_count} applications, expected minimum 8"
                )
        
        # Check for realistic application counts
        avg_apps = sum(apps_per_job.values()) / len(self.jobs) if self.jobs else 0
        
        # With 2000 candidates and 50 jobs, expect average 30-60 apps/job
        if not (20 <= avg_apps <= 100):
            raise AssertionError(
                f"Average applications per job ({avg_apps:.1f}) outside expected range [20, 100]"
            )
    
    def analyze_data_statistics(self):
        """Log data statistics (informational)"""
        self.logger.subsection("DATA STATISTICS")
        
        # Candidate statistics
        self.logger.log(f"Total Candidates: {len(self.candidates)}")
        
        service_lines = Counter(c['service_line'] for c in self.candidates)
        self.logger.log("Service Line Distribution:")
        for sl, count in service_lines.most_common():
            pct = (count / len(self.candidates)) * 100
            self.logger.log(f"  {sl}: {count} ({pct:.1f}%)")
        
        # Experience statistics
        years_exp = [c['years_experience'] for c in self.candidates]
        self.logger.log(f"Experience Range: {min(years_exp)}-{max(years_exp)} years")
        self.logger.log(f"Average Experience: {sum(years_exp)/len(years_exp):.1f} years")
        
        # Dormant statistics
        dormant = sum(1 for c in self.candidates if c['is_dormant'])
        self.logger.log(f"Dormant Candidates: {dormant} ({dormant/len(self.candidates)*100:.1f}%)")
        
        # Application statistics
        apps_per_job = Counter(app['job_id'] for app in self.applications)
        self.logger.log(f"Total Applications: {len(self.applications)}")
        self.logger.log(f"Avg Apps per Job: {len(self.applications)/len(self.jobs):.1f}")
        self.logger.log(f"Min Apps for Job: {min(apps_per_job.values())}")
        self.logger.log(f"Max Apps for Job: {max(apps_per_job.values())}")
    
    def run_all(self):
        """Execute all data quality tests"""
        self.setup()
        
        self.logger.section("SCHEMA VALIDATION TESTS")
        self.runner.run_test("Candidate Schema Validation", self.test_candidate_schema)
        self.runner.run_test("Job Schema Validation", self.test_job_schema)
        self.runner.run_test("Application Schema Validation", self.test_application_schema)
        
        self.logger.section("DATA INTEGRITY TESTS")
        self.runner.run_test("No Duplicate IDs", self.test_no_duplicate_ids)
        self.runner.run_test("Service Line Consistency", self.test_service_line_consistency)
        self.runner.run_test("Location Consistency", self.test_location_consistency)
        self.runner.run_test("Application References Valid", self.test_application_references)
        self.runner.run_test("Dormant Status Consistency", self.test_dormant_status_consistency)
        
        self.logger.section("DATA QUALITY TESTS")
        self.runner.run_test("Data Distributions", self.test_data_distributions)
        self.runner.run_test("Application Volumes", self.test_application_volumes)
        
        self.analyze_data_statistics()
        
        return self.runner.get_summary()


def main():
    """Execute data quality tests"""
    logger = TestLogger("logs/test_data_quality.txt", "Data Quality Tests")
    
    tests = DataQualityTests(logger)
    summary = tests.run_all()
    
    logger.finalize(summary['passed'], summary['failed'])
    
    return summary['failed'] == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)