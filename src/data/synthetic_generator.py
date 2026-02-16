"""
Synthetic Data Generator for Forvis Mazars ATS
Generates realistic candidate profiles and job postings with REALISTIC APPLICATION VOLUMES
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import *

class SyntheticDataGenerator:
    """Generate realistic candidate and job data for Forvis Mazars"""
    
    # Job attractiveness levels (determines application volume)
    JOB_ATTRACTIVENESS = {
        # Entry-level positions (HIGH volume: 150-250 applications)
        "high_volume": [
            "Audit Intern", "Tax Intern", "Junior Auditor", "Junior Tax Consultant",
            "Junior Data Analyst", "Business Analyst", "Financial Analyst",
            "Tax Compliance Officer", "Risk Analyst", "ESG Analyst"
        ],
        
        # Mid-level positions (MEDIUM volume: 30-60 applications)
        "medium_volume": [
            "Auditor", "Senior Auditor", "Tax Consultant", "Senior Tax Advisor",
            "Data Analyst", "Senior Data Analyst", "M&A Advisor", "Strategy Consultant",
            "Cybersecurity Analyst", "Compliance Manager", "ESG Consultant",
            "IT Consultant", "Management Consultant", "Financial Due Diligence Manager"
        ],
        
        # Senior/Specialized (LOW volume: 8-20 applications)
        "low_volume": [
            "Audit Manager", "Tax Manager", "Tax Director", "Senior Data Scientist",
            "Cloud Solutions Architect", "Enterprise Risk Consultant", "Audit Partner",
            "Transfer Pricing Specialist", "Valuation Specialist", "Healthcare Auditor",
            "Banking Auditor", "Forensic Auditor", "Climate Risk Analyst",
            "Digital Transformation Lead", "IT Auditor", "Solutions Architect"
        ]
    }
    
    # Expanded job titles by service line with seniority levels
    JOB_TITLES = {
        "Audit & Assurance": [
            "Audit Intern", "Junior Auditor", "Auditor", "Senior Auditor", "Audit Manager", 
            "Senior Audit Manager", "Audit Partner", "Financial Statement Auditor", 
            "Internal Audit Specialist", "Risk Assurance Consultant", "IT Auditor",
            "Compliance Auditor", "Quality Assurance Manager", "Forensic Auditor",
            "External Auditor", "Operational Auditor", "Healthcare Auditor", "Banking Auditor"
        ],
        "Tax & Legal": [
            "Tax Intern", "Junior Tax Consultant", "Tax Consultant", "Senior Tax Advisor", 
            "Tax Manager", "Tax Director", "Tax Partner", "Transfer Pricing Specialist",
            "International Tax Expert", "VAT Specialist", "Tax Compliance Officer",
            "Corporate Tax Analyst", "Legal Counsel", "Tax Technology Consultant",
            "M&A Tax Advisor", "Indirect Tax Manager", "Tax Controversy Specialist",
            "Estate Planning Advisor", "R&D Tax Credits Consultant"
        ],
        "Financial Advisory": [
            "Financial Analyst", "M&A Advisor", "Financial Due Diligence Manager", 
            "Valuation Specialist", "Restructuring Consultant", "Transaction Services Analyst",
            "Corporate Finance Advisor", "Financial Modeling Expert", "Deal Advisory Manager",
            "Debt Advisory Specialist", "Capital Markets Consultant", "Private Equity Advisor",
            "Real Estate Advisory Consultant", "Infrastructure Finance Advisor"
        ],
        "Consulting": [
            "Business Analyst", "Strategy Consultant", "Business Transformation Manager", 
            "Change Management Consultant", "Process Excellence Consultant", 
            "Digital Transformation Lead", "Management Consultant", "Operations Consultant",
            "Performance Improvement Manager", "Organization Design Consultant",
            "IT Strategy Consultant", "Supply Chain Consultant", "HR Transformation Advisor",
            "Customer Experience Consultant", "Innovation Consultant"
        ],
        "Digital & Technology": [
            "Junior Data Analyst", "Data Analyst", "Senior Data Analyst", "Data Scientist", 
            "Senior Data Scientist", "Business Intelligence Developer", "Cloud Solutions Architect",
            "IT Consultant", "Cybersecurity Analyst", "Information Security Manager",
            "Data Engineer", "AI/ML Specialist", "Digital Analytics Manager",
            "DevOps Engineer", "Solutions Architect", "Technology Risk Manager",
            "IT Auditor", "ERP Consultant", "Blockchain Consultant"
        ],
        "Risk Management": [
            "Risk Analyst", "Risk Manager", "Enterprise Risk Consultant", "Compliance Manager",
            "Operational Risk Analyst", "Financial Risk Specialist", "Risk Advisory Consultant",
            "Credit Risk Manager", "Market Risk Analyst", "Third-Party Risk Manager",
            "Business Continuity Manager", "Regulatory Compliance Specialist"
        ],
        "Sustainability & ESG": [
            "ESG Analyst", "ESG Consultant", "Sustainability Advisor", "Climate Risk Analyst",
            "Corporate Social Responsibility Manager", "ESG Reporting Specialist",
            "Sustainable Finance Consultant", "Carbon Accounting Specialist",
            "Environmental Compliance Manager", "Social Impact Consultant"
        ]
    }
    
    # Real companies (mix of Big 4, consulting firms, corporations)
    COMPANIES = [
        "Forvis Mazars", "Deloitte", "PwC", "EY", "KPMG", "BDO", "Grant Thornton", "RSM",
        "McKinsey & Company", "Boston Consulting Group", "Bain & Company", "Accenture",
        "Capgemini", "IBM", "Microsoft", "Google", "Amazon", "Apple", "Meta",
        "JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "Citigroup", "HSBC",
        "BNP Paribas", "Société Générale", "Crédit Agricole", "Deutsche Bank",
        "L'Oréal", "LVMH", "Danone", "Schneider Electric", "TotalEnergies",
        "Airbus", "Safran", "Renault", "Peugeot", "Air France-KLM",
        "Orange", "Thales", "Atos", "Dassault Systèmes", "Publicis"
    ]
    
    # Expanded education with real institutions
    EDUCATION = [
        # Business & Finance
        "MBA - INSEAD", "MBA - HEC Paris", "MBA - London Business School", 
        "Master in Finance - HEC Paris", "Master in Management - ESSEC Business School",
        "Master of Science in Accounting - Université Paris-Dauphine",
        "Bachelor of Business Administration - ESCP Europe",
        "Master in International Business - EDHEC Business School",
        
        # Accounting & Audit
        "Master's in Accounting and Auditing - Université Paris 1 Panthéon-Sorbonne",
        "DSCG (Expert Comptable) - France", "Master CCA - Comptabilité Contrôle Audit",
        
        # Engineering & Technology
        "Master's in Data Science - École Polytechnique", 
        "Engineering Degree - École Centrale Paris",
        "Master's in Computer Science - Université Pierre et Marie Curie",
        "Master's in Artificial Intelligence - École Normale Supérieure",
        "Bachelor's in Computer Engineering - INSA Lyon",
        "Master in Telecommunications - Télécom Paris",
        
        # Economics & Mathematics
        "Master's in Economics - Paris School of Economics",
        "Master's in Applied Mathematics - École Polytechnique",
        "PhD in Economics - Toulouse School of Economics",
        "Bachelor's in Mathematics - Université de Strasbourg",
        "Master in Econometrics - Université Paris-Saclay",
        
        # Law
        "Master 2 in Business Law - Université Paris 2 Panthéon-Assas",
        "LLM in International Tax Law - King's College London",
        "Master in Corporate Law - Université Paris 1 Panthéon-Sorbonne",
        
        # Sustainability
        "Master in Sustainable Development - Sciences Po Paris",
        "Master in Environmental Management - AgroParisTech"
    ]
    
    # Expanded certifications with more variety
    CERTIFICATIONS = [
        # Accounting & Audit
        "CPA (Certified Public Accountant)", "ACCA (Association of Chartered Certified Accountants)",
        "CIA (Certified Internal Auditor)", "CISA (Certified Information Systems Auditor)",
        "CMA (Certified Management Accountant)", "Diplôme d'Expert-Comptable (DEC)",
        "DSCG (Diplôme Supérieur de Comptabilité et de Gestion)",
        
        # Finance
        "CFA (Chartered Financial Analyst)", "FRM (Financial Risk Manager)",
        "PRM (Professional Risk Manager)", "CAIA (Chartered Alternative Investment Analyst)",
        
        # Project & Process
        "PMP (Project Management Professional)", "PRINCE2 Practitioner",
        "Six Sigma Black Belt", "Lean Six Sigma Green Belt", "Agile Scrum Master",
        "Certified Scrum Product Owner (CSPO)", "SAFe Agilist",
        
        # Technology
        "AWS Certified Solutions Architect", "Azure Data Engineer Associate",
        "Google Cloud Professional Data Engineer", "CISSP (Certified Information Systems Security Professional)",
        "CEH (Certified Ethical Hacker)", "CRISC (Certified in Risk and Information Systems Control)",
        
        # Risk & Compliance
        "CRCM (Certified Regulatory Compliance Manager)", "CGMA (Chartered Global Management Accountant)",
        "Anti-Money Laundering Specialist (CAMS)",
        
        # ESG & Sustainability
        "GRI Certified Sustainability Professional", "CESGA (Certified ESG Analyst)",
        "CFA ESG Investing Certificate"
    ]
    
    # Experience levels with better granularity
    EXPERIENCE_LEVELS = {
        "Intern": (0, 0),
        "Junior": (1, 2),
        "Mid-Level": (3, 5),
        "Senior": (6, 9),
        "Lead": (10, 14),
        "Principal": (15, 20),
        "Partner": (20, 30)
    }
    
    # First names (diverse, international)
    FIRST_NAMES = [
        # French
        "Marie", "Jean", "Sophie", "Pierre", "Camille", "Thomas", "Julie", "Nicolas",
        "Emma", "Alexandre", "Léa", "Antoine", "Chloé", "Maxime", "Sarah", "Lucas",
        
        # International
        "Ahmed", "Fatima", "Mohammed", "Layla", "Hassan", "Amina",
        "Li", "Wei", "Yan", "Chen", "Ming", "Ling",
        "José", "María", "Carlos", "Ana", "Luis", "Carmen",
        "John", "Emily", "Michael", "Jessica", "David", "Sarah",
        "Hans", "Anna", "Klaus", "Petra", "Wolfgang", "Ingrid",
        "Raj", "Priya", "Arjun", "Ananya", "Vikram", "Neha"
    ]
    
    # Last names (diverse, international)
    LAST_NAMES = [
        # French
        "Dupont", "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Richard",
        "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia",
        
        # International
        "Al-Farsi", "Ben Ahmed", "El-Sayed", "Khalil", "Nassar", "Rahman",
        "Chen", "Wang", "Li", "Zhang", "Liu", "Yang",
        "García", "Rodríguez", "Martínez", "López", "González", "Hernández",
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller",
        "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer",
        "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Reddy"
    ]
    
    def __init__(self):
        """Initialize generator"""
        self.used_names = set()
        random.seed(42)  # For reproducibility
    
    def _generate_unique_name(self) -> str:
        """Generate unique candidate name"""
        max_attempts = 100
        for _ in range(max_attempts):
            first = random.choice(self.FIRST_NAMES)
            last = random.choice(self.LAST_NAMES)
            name = f"{first} {last}"
            
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        
        # Fallback: add number
        base_name = f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}"
        counter = 1
        while f"{base_name} {counter}" in self.used_names:
            counter += 1
        
        name = f"{base_name} {counter}"
        self.used_names.add(name)
        return name
    
    def _get_job_volume_category(self, job_title: str) -> str:
        """Determine application volume category for a job"""
        for category, titles in self.JOB_ATTRACTIVENESS.items():
            if any(title.lower() in job_title.lower() for title in titles):
                return category
        
        # Default to medium volume
        return "medium_volume"
    
    def _get_expected_applications(self, job_title: str, service_line: str) -> int:
        """Get realistic number of applications for a job"""
        category = self._get_job_volume_category(job_title)
        
        if category == "high_volume":
            base_range = (150, 250)
        elif category == "low_volume":
            base_range = (8, 20)
        else:  # medium_volume
            base_range = (30, 60)
        
        # Adjust for service line popularity
        popular_lines = ["Consulting", "Digital & Technology", "Financial Advisory"]
        if service_line in popular_lines:
            multiplier = 1.2
        else:
            multiplier = 1.0
        
        min_apps = int(base_range[0] * multiplier)
        max_apps = int(base_range[1] * multiplier)
        
        return random.randint(min_apps, max_apps)
    
    def generate_candidates(self, num_candidates: int) -> List[Dict]:
        """Generate candidate profiles - LARGE POOL for realistic matching"""
        print(f"\n[1/3] Generating {num_candidates} candidate profiles...")
        
        candidates = []
        service_lines = list(self.JOB_TITLES.keys())
        
        for i in range(num_candidates):
            # Select service line and title
            service_line = random.choice(service_lines)
            current_title = random.choice(self.JOB_TITLES[service_line])
            
            # Determine experience level
            exp_level = random.choice(list(self.EXPERIENCE_LEVELS.keys()))
            years_exp_min, years_exp_max = self.EXPERIENCE_LEVELS[exp_level]
            years_experience = random.randint(years_exp_min, years_exp_max)
            
            # Generate profile
            candidate = {
                "id": f"CV_{i+1:04d}",
                "name": self._generate_unique_name(),
                "email": f"candidate{i+1}@example.com",
                "phone": f"+33 6 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                "location": random.choice(FORVIS_LOCATIONS),
                "current_title": current_title,
                "service_line": service_line,
                "years_experience": years_experience,
                "experience_level": exp_level,
                "education": random.sample(self.EDUCATION, random.randint(1, 2)),
                "certifications": random.sample(self.CERTIFICATIONS, random.randint(0, 3)),
                "skills": self._get_skills_for_service_line(service_line, years_experience),
                "languages": random.sample(["English", "French", "German", "Spanish", "Arabic"], random.randint(2, 4)),
                "summary": self._generate_summary(current_title, years_experience, service_line),
                "company_history": self._generate_company_history(years_experience),
                "availability": random.choice(["Immediate", "2 weeks notice", "1 month notice", "3 months notice"]),
                "salary_expectation": self._generate_salary(years_experience, service_line),
                "remote_preference": random.choice([True, False, "Hybrid"]),
                
                # WILL BE SET BY APPLICATION GENERATOR
                "last_application_date": None,  # Placeholder
                "is_dormant": False  # Placeholder
            }
            
            candidates.append(candidate)
            
            if (i + 1) % 500 == 0:
                print(f"   Generated {i+1}/{num_candidates} candidates...")
        
        print(f"✅ Generated {len(candidates)} candidates")
        return candidates
    
    def generate_jobs(self, num_jobs: int) -> List[Dict]:
        """Generate job postings"""
        print(f"\n[2/3] Generating {num_jobs} job postings...")
        
        jobs = []
        service_lines = list(self.JOB_TITLES.keys())
        
        for i in range(num_jobs):
            service_line = random.choice(service_lines)
            title = random.choice(self.JOB_TITLES[service_line])
            
            # Determine experience level
            exp_level = random.choice(list(self.EXPERIENCE_LEVELS.keys()))
            years_min, years_max = self.EXPERIENCE_LEVELS[exp_level]
            
            job = {
                "id": f"JOB_{i+1:03d}",
                "title": title,
                "service_line": service_line,
                "location": random.choice(FORVIS_LOCATIONS),
                "years_experience_min": years_min,
                "years_experience_max": years_max,
                "experience_level": exp_level,
                "contract_type": random.choice(["Full-time", "Full-time", "Full-time", "Contract"]),
                "remote": random.choice([True, False, "Hybrid"]),
                "travel_required": random.choice(["None", "Occasional (10%)", "Frequent (25%)", "Extensive (50%)"]),
                "description": self._generate_job_description(title, service_line),
                "required_skills": self._get_skills_for_service_line(service_line, years_min + 2),
                "nice_to_have_skills": random.sample(FORVIS_SKILL_TAXONOMY.get("Technical", [])[:15], random.randint(3, 5)),
                "responsibilities": self._generate_responsibilities(title, service_line),
                "qualifications": self._generate_qualifications(exp_level, service_line),
                "salary_range": self._get_salary_range(years_min, years_max, service_line),
                "posted_date": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                "deadline": (datetime.now() + timedelta(days=random.randint(10, 45))).strftime("%Y-%m-%d"),
                
                # Application volume metadata
                "expected_applications": self._get_expected_applications(title, service_line),
                "volume_category": self._get_job_volume_category(title)
            }
            
            jobs.append(job)
        
        print(f"✅ Generated {len(jobs)} jobs")
        
        # Print volume distribution
        high_vol = sum(1 for j in jobs if j['volume_category'] == 'high_volume')
        med_vol = sum(1 for j in jobs if j['volume_category'] == 'medium_volume')
        low_vol = sum(1 for j in jobs if j['volume_category'] == 'low_volume')
        
        print(f"\n   Volume Distribution:")
        print(f"   📈 High volume jobs (150-250 apps): {high_vol}")
        print(f"   📊 Medium volume jobs (30-60 apps): {med_vol}")
        print(f"   📉 Low volume jobs (8-20 apps): {low_vol}")
        
        return jobs
    
    def generate_application_history(self, candidates: List[Dict], jobs: List[Dict]) -> List[Dict]:
        """
        Generate REALISTIC application history based on job attractiveness
        Each job gets realistic number of applicants based on seniority/type
        """
        print(f"\n[3/3] Generating realistic application history...")
        
        applications = []
        application_id = 1
        candidate_application_count = {c['id']: 0 for c in candidates}
        
        # For each job, generate appropriate number of applications
        for job in jobs:
            expected_apps = job['expected_applications']
            job_id = job['id']
            
            print(f"   {job['title']}: Generating {expected_apps} applications...")
            
            # Filter candidates that could reasonably apply for this job
            eligible_candidates = [
                c for c in candidates
                if (
                    # Service line match or adjacent
                    c['service_line'] == job['service_line'] or 
                    random.random() < 0.15  # 15% cross-service applications
                ) and (
                    # Experience level appropriate
                    abs(c['years_experience'] - job['years_experience_min']) <= 5 or
                    random.random() < 0.2  # 20% stretch applications
                )
            ]
            
            if len(eligible_candidates) < expected_apps:
                # Not enough eligible candidates, relax constraints
                eligible_candidates = candidates.copy()
            
            # Randomly select applicants (without replacement for this job)
            num_to_select = min(expected_apps, len(eligible_candidates))
            selected_candidates = random.sample(eligible_candidates, num_to_select)
            
            for candidate in selected_candidates:
                # Generate application date (spread over past 18 months)
                days_ago = random.randint(1, 540)  # 1 day to 18 months
                application_date = datetime.now() - timedelta(days=days_ago)
                
                applications.append({
                    "id": application_id,
                    "candidate_id": candidate['id'],
                    "job_id": job_id,
                    "application_date": application_date.strftime("%Y-%m-%d"),
                    "days_since_application": days_ago,
                    "created_at": application_date.strftime("%Y-%m-%d")
                })
                
                application_id += 1
                candidate_application_count[candidate['id']] += 1
        
        print(f"✅ Generated {len(applications)} total applications")
        
        # Calculate and set dormant status for each candidate
        for candidate in candidates:
            # Get all applications for this candidate
            candidate_apps = [a for a in applications if a['candidate_id'] == candidate['id']]
            
            if candidate_apps:
                # Find most recent application
                most_recent = min(candidate_apps, key=lambda x: x['days_since_application'])
                
                candidate['last_application_date'] = most_recent['application_date']
                candidate['is_dormant'] = most_recent['days_since_application'] > (DORMANT_THRESHOLD_MONTHS * 30)
            else:
                # Candidate never applied (shouldn't happen with realistic volumes)
                candidate['last_application_date'] = None
                candidate['is_dormant'] = False
        
        # Statistics
        total_dormant = sum(1 for c in candidates if c['is_dormant'])
        total_active = len(candidates) - total_dormant
        avg_apps_per_candidate = len(applications) / len(candidates)
        candidates_with_apps = sum(1 for count in candidate_application_count.values() if count > 0)
        
        print(f"\n   📊 Application Statistics:")
        print(f"   Total applications: {len(applications)}")
        print(f"   Avg per job: {len(applications)/len(jobs):.1f}")
        print(f"   Avg per candidate: {avg_apps_per_candidate:.1f}")
        print(f"   Candidates who applied: {candidates_with_apps}/{len(candidates)}")
        print(f"   Active candidates: {total_active}")
        print(f"   Dormant candidates: {total_dormant} ({total_dormant/len(candidates)*100:.1f}%)")
        
        return applications
    
    def _generate_summary(self, title: str, years_exp: int, service_line: str) -> str:
        """Generate professional summary"""
        templates = [
            f"Experienced {title} with {years_exp} years in {service_line}. Proven track record in delivering high-quality results and driving business value.",
            f"{title} professional with {years_exp}+ years of expertise in {service_line}. Strong analytical skills and client relationship management.",
            f"Results-driven {title} specializing in {service_line}. {years_exp} years of experience in complex projects and strategic initiatives.",
        ]
        return random.choice(templates)
    
    def _generate_company_history(self, years_exp: int) -> List[str]:
        """Generate work history"""
        num_companies = min(years_exp // 3 + 1, 4)
        return random.sample(self.COMPANIES, min(num_companies, len(self.COMPANIES)))
    
    def _generate_salary(self, years_exp: int, service_line: str) -> str:
        """Generate salary expectation"""
        base = 35000 + (years_exp * 7000)
        
        if service_line in ["Financial Advisory", "Consulting", "Digital & Technology"]:
            base = int(base * 1.2)
        
        return f"€{base//1000}K - €{(base+15000)//1000}K"
    
    def _generate_job_description(self, title: str, service_line: str) -> str:
        """Generate job description"""
        return f"We are seeking a talented {title} to join our {service_line} team. The ideal candidate will contribute to high-impact projects and work with leading global clients."
    
    def _generate_responsibilities(self, title: str, service_line: str) -> List[str]:
        """Generate job responsibilities"""
        return [
            f"Lead {service_line.lower()} engagements for key clients",
            "Develop and implement strategic solutions",
            "Collaborate with cross-functional teams",
            "Mentor junior team members",
            "Drive continuous improvement initiatives"
        ]
    
    def _generate_qualifications(self, exp_level: str, service_line: str) -> List[str]:
        """Generate job qualifications"""
        years_min = self.EXPERIENCE_LEVELS[exp_level][0]
        return [
            f"Minimum {years_min} years of experience in {service_line.lower()}",
            "Strong analytical and problem-solving skills",
            "Excellent communication and presentation abilities",
            "Proven track record of delivering results",
            "Bachelor's degree required; Master's preferred"
        ]
    
    def _get_salary_range(self, exp_min: int, exp_max: int, service_line: str) -> str:
        """Generate realistic salary range"""
        base_min = 30000 + (exp_min * 8000)
        base_max = 30000 + (exp_max * 8000)
        
        # Premium for certain service lines
        if service_line in ["Financial Advisory", "Consulting", "Digital & Technology"]:
            base_min = int(base_min * 1.15)
            base_max = int(base_max * 1.15)
        
        return f"€{base_min//1000}K - €{base_max//1000}K + performance bonus"
    
    def _get_skills_for_service_line(self, service_line: str, years_exp: int) -> List[str]:
        """Get relevant skills based on service line and experience"""
        skills = []
        
        # Always add soft skills
        skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Soft Skills"], random.randint(3, 5)))
        
        # Add domain-specific skills
        if "Audit" in service_line:
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Audit & Compliance"], random.randint(4, 7)))
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Financial"], random.randint(2, 4)))
        
        elif "Tax" in service_line:
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Tax & Legal"], random.randint(4, 7)))
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Financial"], random.randint(2, 3)))
        
        elif "Advisory" in service_line:
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Financial"], random.randint(4, 6)))
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Consulting"], random.randint(3, 5)))
        
        elif "Consulting" in service_line:
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Consulting"], random.randint(4, 7)))
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Financial"], random.randint(2, 3)))
        
        elif "Digital" in service_line or "Technology" in service_line:
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Technical"], random.randint(5, 8)))
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Consulting"], random.randint(2, 3)))
        
        elif "Risk" in service_line:
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Audit & Compliance"], random.randint(3, 5)))
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Financial"], random.randint(3, 4)))
        
        else:  # Sustainability & ESG
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Audit & Compliance"], random.randint(2, 3)))
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Consulting"], random.randint(3, 4)))
        
        # Add more technical skills for senior roles
        if years_exp > 5:
            skills.extend(random.sample(FORVIS_SKILL_TAXONOMY["Technical"][:10], random.randint(2, 4)))
        
        return list(set(skills))  # Remove duplicates
    
    def save_data(self, candidates: List[Dict], jobs: List[Dict]):
        """Save generated data to JSON files"""
        # Generate application history FIRST
        applications = self.generate_application_history(candidates, jobs)
        
        # Save candidates
        cv_path = CV_DATA_FILE
        with open(cv_path, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(candidates)} candidates to {cv_path}")
        
        # Save jobs
        job_path = JOB_DATA_FILE
        with open(job_path, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(jobs)} jobs to {job_path}")
        
        # Save applications
        app_path = PROCESSED_DATA_DIR / "applications.json"
        with open(app_path, 'w', encoding='utf-8') as f:
            json.dump(applications, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(applications)} applications to {app_path}")
        
        self._print_statistics(candidates, jobs, applications)
    
    def _print_statistics(self, candidates: List[Dict], jobs: List[Dict], applications: List[Dict]):
        """Print dataset statistics"""
        print("\n" + "="*60)
        print("DATASET STATISTICS")
        print("="*60)
        
        print(f"\nCANDIDATES ({len(candidates)} total):")
        print(f"  Dormant candidates: {sum(1 for c in candidates if c['is_dormant'])}")
        
        service_line_dist = {}
        exp_level_dist = {}
        for c in candidates:
            sl = c['service_line']
            service_line_dist[sl] = service_line_dist.get(sl, 0) + 1
            lvl = c['experience_level']
            exp_level_dist[lvl] = exp_level_dist.get(lvl, 0) + 1
        
        print(f"\n  Distribution by Service Line:")
        for sl, count in sorted(service_line_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"    {sl}: {count}")
        
        print(f"\n  Distribution by Experience Level:")
        for lvl, count in sorted(exp_level_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"    {lvl}: {count}")
        
        print(f"\nJOBS ({len(jobs)} total):")
        job_service_dist = {}
        job_level_dist = {}
        for j in jobs:
            sl = j['service_line']
            job_service_dist[sl] = job_service_dist.get(sl, 0) + 1
            lvl = j['experience_level']
            job_level_dist[lvl] = job_level_dist.get(lvl, 0) + 1
        
        print(f"  Distribution by Service Line:")
        for sl, count in sorted(job_service_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"    {sl}: {count}")
        
        print(f"  Distribution by Experience Level:")
        for lvl, count in sorted(job_level_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"    {lvl}: {count}")
        
        print(f"\nAPPLICATIONS ({len(applications)} total):")
        print(f"  Total applications: {len(applications)}")
        print(f"  Avg per job: {len(applications)/len(jobs):.1f}")
        print(f"  Avg per candidate: {len(applications)/len(candidates):.1f}")


def main():
    """Main execution function"""
    print("="*60)
    print("SYNTHETIC DATA GENERATION - FORVIS MAZARS ATS")
    print("REALISTIC APPLICATION VOLUMES")
    print("="*60)
    
    generator = SyntheticDataGenerator()
    
    # LARGER DATABASE: 2000 candidates, 50 jobs
    # This gives enough candidates to fill all job applications realistically
    num_candidates = 2000
    num_jobs = 50
    
    print(f"\n📊 Configuration:")
    print(f"   Candidates: {num_candidates}")
    print(f"   Jobs: {num_jobs}")
    print(f"   Expected total applications: ~3,000-4,000")
    
    print(f"\n[1/3] Generating {num_candidates} candidate profiles...")
    candidates = generator.generate_candidates(num_candidates)
    
    print(f"\n[2/3] Generating {num_jobs} job postings...")
    jobs = generator.generate_jobs(num_jobs)
    
    print(f"\n[3/3] Saving data with realistic applications...")
    generator.save_data(candidates, jobs)
    
    print("\n" + "="*60)
    print("✅ DATA GENERATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("  1. Run: python src/models/embedding_engine.py")
    print("  2. Run: python src/search/faiss_indexer.py")
    print("  3. Or: python pipeline.py (does both)")


if __name__ == "__main__":
    main()