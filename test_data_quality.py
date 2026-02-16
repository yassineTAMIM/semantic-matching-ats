"""
Data Quality Validation Suite
Validates the integrity and quality of synthetic candidate and job data
Logs all results to local .txt file
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import Dict, List, Tuple
import re

sys.path.append(str(Path(__file__).parent))
from config import *

# Logger class for local file logging
class TestLogger:
    """Custom logger that writes to local .txt file"""
    
    def __init__(self, log_file: str = "logs/data_quality_test.txt"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Clear previous log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"DATA QUALITY VALIDATION LOG\n")
            f.write(f"{'='*80}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
    
    def log(self, message: str, level: str = "INFO"):
        """Log message to file and print to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Write to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Print to console
        print(f"[{level}] {message}")
    
    def section(self, title: str):
        """Log section header"""
        separator = "=" * 80
        self.log(f"\n{separator}")
        self.log(title)
        self.log(separator)


class DataQualityValidator:
    """Comprehensive data quality validation"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.candidates = []
        self.jobs = []
        self.issues = []
        self.warnings = []
        self.stats = {}
    
    def load_data(self):
        """Load candidate and job data"""
        self.logger.section("LOADING DATA")
        
        try:
            with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
                self.candidates = json.load(f)
            self.logger.log(f"Loaded {len(self.candidates)} candidates from {CV_DATA_FILE}", "SUCCESS")
        except Exception as e:
            self.logger.log(f"Failed to load candidates: {e}", "ERROR")
            self.issues.append(f"Candidate data loading failed: {e}")
        
        try:
            with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
                self.jobs = json.load(f)
            self.logger.log(f"Loaded {len(self.jobs)} jobs from {JOB_DATA_FILE}", "SUCCESS")
        except Exception as e:
            self.logger.log(f"Failed to load jobs: {e}", "ERROR")
            self.issues.append(f"Job data loading failed: {e}")
    
    def validate_candidate_schema(self) -> Tuple[int, int]:
        """Validate candidate data schema and required fields"""
        self.logger.section("VALIDATING CANDIDATE SCHEMA")
        
        required_fields = [
            'id', 'name', 'email', 'phone', 'current_title', 'service_line',
            'years_experience', 'experience_level', 'location', 'skills',
            'last_application_date', 'is_dormant'
        ]
        
        errors = 0
        warnings = 0
        
        for i, candidate in enumerate(self.candidates):
            # Check required fields
            missing_fields = [f for f in required_fields if f not in candidate]
            if missing_fields:
                self.logger.log(
                    f"Candidate {candidate.get('id', i)}: Missing fields {missing_fields}",
                    "ERROR"
                )
                errors += 1
            
            # Validate email format
            if 'email' in candidate:
                if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', candidate['email']):
                    self.logger.log(
                        f"Candidate {candidate['id']}: Invalid email format",
                        "WARN"
                    )
                    warnings += 1
            
            # Validate years_experience is non-negative
            if candidate.get('years_experience', -1) < 0:
                self.logger.log(
                    f"Candidate {candidate['id']}: Negative years_experience",
                    "ERROR"
                )
                errors += 1
            
            # Check skills is a list and not empty
            if not isinstance(candidate.get('skills', []), list):
                self.logger.log(
                    f"Candidate {candidate['id']}: Skills is not a list",
                    "ERROR"
                )
                errors += 1
            elif len(candidate.get('skills', [])) == 0:
                self.logger.log(
                    f"Candidate {candidate['id']}: No skills listed",
                    "WARN"
                )
                warnings += 1
        
        self.logger.log(f"Schema validation: {errors} errors, {warnings} warnings")
        return errors, warnings
    
    def validate_job_schema(self) -> Tuple[int, int]:
        """Validate job data schema"""
        self.logger.section("VALIDATING JOB SCHEMA")
        
        required_fields = [
            'id', 'title', 'service_line', 'location', 'experience_level',
            'years_experience_min', 'years_experience_max', 'description',
            'required_skills'
        ]
        
        errors = 0
        warnings = 0
        
        for i, job in enumerate(self.jobs):
            # Check required fields
            missing_fields = [f for f in required_fields if f not in job]
            if missing_fields:
                self.logger.log(
                    f"Job {job.get('id', i)}: Missing fields {missing_fields}",
                    "ERROR"
                )
                errors += 1
            
            # Validate experience range
            exp_min = job.get('years_experience_min', 0)
            exp_max = job.get('years_experience_max', 0)
            
            if exp_min > exp_max:
                self.logger.log(
                    f"Job {job['id']}: Min experience ({exp_min}) > max ({exp_max})",
                    "ERROR"
                )
                errors += 1
            
            # Check required_skills is list and not empty
            if not isinstance(job.get('required_skills', []), list):
                self.logger.log(
                    f"Job {job['id']}: required_skills is not a list",
                    "ERROR"
                )
                errors += 1
            elif len(job.get('required_skills', [])) == 0:
                self.logger.log(
                    f"Job {job['id']}: No required skills",
                    "WARN"
                )
                warnings += 1
        
        self.logger.log(f"Schema validation: {errors} errors, {warnings} warnings")
        return errors, warnings
    
    def analyze_data_distributions(self):
        """Analyze and report data distributions"""
        self.logger.section("DATA DISTRIBUTION ANALYSIS")
        
        # Candidate distributions
        self.logger.log("\nCANDIDATE DISTRIBUTIONS:")
        
        # Service line distribution
        service_lines = Counter(c['service_line'] for c in self.candidates)
        self.logger.log(f"\nService Line Distribution:")
        for sl, count in service_lines.most_common():
            pct = (count / len(self.candidates)) * 100
            self.logger.log(f"  {sl}: {count} ({pct:.1f}%)")
        
        # Experience level distribution
        exp_levels = Counter(c['experience_level'] for c in self.candidates)
        self.logger.log(f"\nExperience Level Distribution:")
        for level, count in exp_levels.most_common():
            pct = (count / len(self.candidates)) * 100
            self.logger.log(f"  {level}: {count} ({pct:.1f}%)")
        
        # Dormant status
        dormant_count = sum(1 for c in self.candidates if c.get('is_dormant', False))
        active_count = len(self.candidates) - dormant_count
        self.logger.log(f"\nDormant Status:")
        self.logger.log(f"  Active: {active_count} ({active_count/len(self.candidates)*100:.1f}%)")
        self.logger.log(f"  Dormant: {dormant_count} ({dormant_count/len(self.candidates)*100:.1f}%)")
        
        # Years of experience distribution
        years_exp = [c['years_experience'] for c in self.candidates]
        self.logger.log(f"\nYears of Experience Statistics:")
        self.logger.log(f"  Min: {min(years_exp)}")
        self.logger.log(f"  Max: {max(years_exp)}")
        self.logger.log(f"  Mean: {sum(years_exp)/len(years_exp):.2f}")
        self.logger.log(f"  Median: {sorted(years_exp)[len(years_exp)//2]}")
        
        # Skills analysis
        all_skills = []
        for c in self.candidates:
            all_skills.extend(c.get('skills', []))
        
        skill_counts = Counter(all_skills)
        self.logger.log(f"\nSkills Statistics:")
        self.logger.log(f"  Total unique skills: {len(skill_counts)}")
        self.logger.log(f"  Top 10 most common skills:")
        for skill, count in skill_counts.most_common(10):
            self.logger.log(f"    {skill}: {count}")
        
        # Job distributions
        self.logger.log("\n\nJOB DISTRIBUTIONS:")
        
        job_service_lines = Counter(j['service_line'] for j in self.jobs)
        self.logger.log(f"\nService Line Distribution:")
        for sl, count in job_service_lines.most_common():
            pct = (count / len(self.jobs)) * 100
            self.logger.log(f"  {sl}: {count} ({pct:.1f}%)")
        
        job_exp_levels = Counter(j['experience_level'] for j in self.jobs)
        self.logger.log(f"\nExperience Level Distribution:")
        for level, count in job_exp_levels.most_common():
            pct = (count / len(self.jobs)) * 100
            self.logger.log(f"  {level}: {count} ({pct:.1f}%)")
    
    def check_data_quality_issues(self):
        """Check for common data quality issues"""
        self.logger.section("DATA QUALITY CHECKS")
        
        # Check for duplicates
        candidate_ids = [c['id'] for c in self.candidates]
        duplicate_ids = [id_ for id_, count in Counter(candidate_ids).items() if count > 1]
        
        if duplicate_ids:
            self.logger.log(f"Found {len(duplicate_ids)} duplicate candidate IDs", "ERROR")
            self.issues.append(f"Duplicate candidate IDs: {duplicate_ids[:5]}")
        else:
            self.logger.log("No duplicate candidate IDs found", "SUCCESS")
        
        job_ids = [j['id'] for j in self.jobs]
        duplicate_job_ids = [id_ for id_, count in Counter(job_ids).items() if count > 1]
        
        if duplicate_job_ids:
            self.logger.log(f"Found {len(duplicate_job_ids)} duplicate job IDs", "ERROR")
            self.issues.append(f"Duplicate job IDs: {duplicate_job_ids}")
        else:
            self.logger.log("No duplicate job IDs found", "SUCCESS")
        
        # Check for inconsistent data
        for candidate in self.candidates:
            # Experience level vs years mismatch
            years = candidate.get('years_experience', 0)
            level = candidate.get('experience_level', '')
            
            expected_ranges = {
                'Intern': (0, 0),
                'Junior': (1, 2),
                'Mid-Level': (3, 5),
                'Senior': (6, 9),
                'Lead': (10, 14),
                'Principal': (15, 20),
                'Partner': (20, 30)
            }
            
            if level in expected_ranges:
                min_exp, max_exp = expected_ranges[level]
                if not (min_exp <= years <= max_exp):
                    self.logger.log(
                        f"Candidate {candidate['id']}: Experience mismatch - "
                        f"{years} years but level is {level}",
                        "WARN"
                    )
                    self.warnings.append(f"{candidate['id']}: Experience/level mismatch")
        
        # Check for empty or very short descriptions
        for job in self.jobs:
            desc = job.get('description', '')
            if len(desc) < 50:
                self.logger.log(
                    f"Job {job['id']}: Very short description ({len(desc)} chars)",
                    "WARN"
                )
                self.warnings.append(f"{job['id']}: Short description")
    
    def validate_data_consistency(self):
        """Validate data consistency across candidates and jobs"""
        self.logger.section("DATA CONSISTENCY VALIDATION")
        
        # Collect all service lines from candidates and jobs
        candidate_service_lines = set(c['service_line'] for c in self.candidates)
        job_service_lines = set(j['service_line'] for j in self.jobs)
        
        self.logger.log(f"Unique service lines in candidates: {len(candidate_service_lines)}")
        self.logger.log(f"Unique service lines in jobs: {len(job_service_lines)}")
        
        # Check for service lines in jobs but not in candidates
        orphan_service_lines = job_service_lines - candidate_service_lines
        if orphan_service_lines:
            self.logger.log(
                f"Service lines in jobs but not in candidates: {orphan_service_lines}",
                "WARN"
            )
        
        # Check for reasonable skill overlap
        candidate_skills = set()
        for c in self.candidates:
            candidate_skills.update(s.lower() for s in c.get('skills', []))
        
        job_skills = set()
        for j in self.jobs:
            job_skills.update(s.lower() for s in j.get('required_skills', []))
        
        common_skills = candidate_skills & job_skills
        overlap_pct = (len(common_skills) / len(job_skills)) * 100 if job_skills else 0
        
        self.logger.log(f"\nSkill Overlap Analysis:")
        self.logger.log(f"  Unique candidate skills: {len(candidate_skills)}")
        self.logger.log(f"  Unique job required skills: {len(job_skills)}")
        self.logger.log(f"  Common skills: {len(common_skills)} ({overlap_pct:.1f}% of job skills)")
        
        if overlap_pct < 50:
            self.logger.log(
                "WARNING: Low skill overlap between candidates and jobs",
                "WARN"
            )
            self.warnings.append("Low skill overlap (<50%)")
    
    def generate_summary_report(self):
        """Generate final summary report"""
        self.logger.section("VALIDATION SUMMARY")
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        self.logger.log(f"\nTotal Critical Issues: {total_issues}")
        if self.issues:
            self.logger.log("Critical Issues:")
            for issue in self.issues[:10]:  # Show first 10
                self.logger.log(f"  - {issue}")
        
        self.logger.log(f"\nTotal Warnings: {total_warnings}")
        if self.warnings:
            self.logger.log("Warnings:")
            for warning in self.warnings[:10]:  # Show first 10
                self.logger.log(f"  - {warning}")
        
        # Overall verdict
        if total_issues == 0 and total_warnings == 0:
            verdict = "EXCELLENT - No issues found"
            level = "SUCCESS"
        elif total_issues == 0:
            verdict = f"GOOD - {total_warnings} warnings but no critical issues"
            level = "SUCCESS"
        elif total_issues < 10:
            verdict = f"FAIR - {total_issues} critical issues need attention"
            level = "WARN"
        else:
            verdict = f"POOR - {total_issues} critical issues found"
            level = "ERROR"
        
        self.logger.log(f"\nOVERALL DATA QUALITY: {verdict}", level)
        
        # Save summary stats
        self.stats = {
            'total_candidates': len(self.candidates),
            'total_jobs': len(self.jobs),
            'critical_issues': total_issues,
            'warnings': total_warnings,
            'verdict': verdict
        }
    
    def run_all_validations(self):
        """Run all validation tests"""
        self.load_data()
        
        if not self.candidates or not self.jobs:
            self.logger.log("Cannot proceed - data loading failed", "ERROR")
            return
        
        # Run all validations
        cand_errors, cand_warnings = self.validate_candidate_schema()
        job_errors, job_warnings = self.validate_job_schema()
        
        self.analyze_data_distributions()
        self.check_data_quality_issues()
        self.validate_data_consistency()
        self.generate_summary_report()
        
        self.logger.log(f"\n{'='*80}")
        self.logger.log(f"Data quality validation complete. Log saved to: {self.logger.log_file}")
        self.logger.log(f"{'='*80}")


def main():
    """Main execution"""
    logger = TestLogger("logs/data_quality_test.txt")
    validator = DataQualityValidator(logger)
    validator.run_all_validations()
    
    print(f"\n✅ Validation complete. Full log saved to: {logger.log_file.absolute()}")


if __name__ == "__main__":
    main()