"""
Synthetic Data Generator for Forvis Mazars ATS
Generates realistic candidate profiles and job postings
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
    
    # Projects/achievements templates
    PROJECT_TEMPLATES = [
        "Led audit of multinational {industry} company with revenues exceeding €{revenue}M",
        "Managed tax compliance project for {client_count} international clients across {country_count} jurisdictions",
        "Implemented {system} system resulting in {improvement}% efficiency improvement",
        "Conducted due diligence for €{deal_size}M {deal_type} transaction",
        "Developed predictive analytics model improving forecast accuracy by {improvement}%",
        "Restructured operations for distressed {industry} client, achieving €{savings}M cost reduction",
        "Delivered digital transformation roadmap for Fortune 500 {industry} company",
        "Performed forensic investigation uncovering €{amount}M in financial irregularities",
        "Designed ESG reporting framework adopted by {client_count} portfolio companies"
    ]
    
    INDUSTRIES = [
        "automotive", "banking", "insurance", "retail", "manufacturing", "technology",
        "pharmaceuticals", "energy", "telecommunications", "hospitality", "real estate",
        "healthcare", "aerospace", "logistics", "consumer goods", "media"
    ]
    
    def __init__(self):
        # Expanded international names
        self.first_names = [
            # French
            "Alexandre", "Antoine", "Baptiste", "Camille", "Charlotte", "Chloé", "Claire", "Élise",
            "Emma", "François", "Gabrielle", "Guillaume", "Hugo", "Julie", "Laura", "Lucas",
            "Léa", "Marie", "Mathilde", "Maxime", "Nicolas", "Paul", "Pierre", "Sophie", "Théo",
            
            # Arabic/Maghreb
            "Amine", "Fatima", "Hassan", "Karim", "Leila", "Mehdi", "Mohamed", "Nadia",
            "Omar", "Rachid", "Samir", "Sara", "Yasmine", "Youssef", "Zineb",
            
            # Anglo-Saxon
            "Alexander", "Alice", "Benjamin", "Catherine", "Daniel", "David", "Emily",
            "James", "John", "Laura", "Michael", "Olivia", "Rachel", "Robert", "Sarah",
            "Thomas", "William",
            
            # Spanish
            "Carlos", "Carmen", "Diego", "Elena", "Isabel", "Javier", "José", "Luis", "María",
            
            # German
            "Anna", "Felix", "Hannah", "Jonas", "Julia", "Lukas", "Maximilian", "Sophie",
            
            # International
            "Aisha", "Ali", "Chen", "Dmitri", "Ivan", "Kenji", "Mei", "Ravi", "Yuki"
        ]
        
        self.last_names = [
            # French
            "Bernard", "Dubois", "Dupont", "Durand", "Fontaine", "Fournier", "Garcia",
            "Lambert", "Lefebvre", "Leroy", "Martin", "Moreau", "Petit", "Richard",
            "Robert", "Roux", "Simon", "Thomas",
            
            # Maghreb
            "Alami", "Amrani", "Benali", "Bouazza", "El Amrani", "El Fassi", "Hassani",
            "Idrissi", "Khalil", "Mansouri", "Oulahcen", "Tazi", "Zerouali",
            
            # Anglo-Saxon
            "Anderson", "Brown", "Davis", "Johnson", "Jones", "Miller", "Moore",
            "Smith", "Taylor", "Thomas", "White", "Williams", "Wilson",
            
            # Spanish
            "Díaz", "Fernández", "García", "González", "Hernández", "López",
            "Martínez", "Pérez", "Rodríguez", "Sánchez",
            
            # German
            "Fischer", "Hoffman", "Klein", "Müller", "Schmidt", "Schneider", "Wagner", "Weber",
            
            # Other European
            "Ivanov", "Kowalski", "Nielsen", "Petrov", "Rossi", "Van den Berg",
            
            # Asian
            "Chen", "Khan", "Kim", "Lee", "Nguyen", "Patel", "Wang", "Xu", "Zhang"
        ]
    
    def generate_candidates(self, num_candidates: int = 1000) -> List[Dict]:
        """Generate realistic candidate profiles with rich details"""
        candidates = []
        
        for i in range(num_candidates):
            service_line = random.choice(FORVIS_SERVICE_LINES)
            job_titles_pool = self.JOB_TITLES.get(service_line, ["Consultant"])
            job_title = random.choice(job_titles_pool)
            
            # Determine experience level from title
            if any(x in job_title.lower() for x in ["intern", "junior", "analyst"]):
                experience_level = random.choice(["Intern", "Junior"])
            elif any(x in job_title.lower() for x in ["senior", "lead"]):
                experience_level = random.choice(["Senior", "Lead"])
            elif any(x in job_title.lower() for x in ["partner", "director"]):
                experience_level = random.choice(["Principal", "Partner"])
            else:
                experience_level = random.choice(["Mid-Level", "Senior"])
            
            exp_min, exp_max = self.EXPERIENCE_LEVELS[experience_level]
            years_experience = random.randint(exp_min, exp_max)
            
            # Generate application date (random within last 3 years)
            days_ago = random.randint(30, 1095)
            last_application = datetime.now() - timedelta(days=days_ago)
            is_dormant = days_ago > (DORMANT_THRESHOLD_MONTHS * 30)
            
            # Select skills with proficiency
            skills = self._get_skills_for_service_line(service_line, years_experience)
            
            # Generate 2-4 certifications for experienced professionals
            num_certs = 0 if years_experience < 2 else random.randint(1, min(4, 1 + years_experience // 3))
            certifications = random.sample(self.CERTIFICATIONS, num_certs) if num_certs > 0 else []
            
            # Languages with proficiency
            num_languages = random.randint(2, 4)
            languages = random.sample(FORVIS_SKILL_TAXONOMY["Languages"], num_languages)
            language_prof = [f"{lang} ({random.choice(['Native', 'Fluent', 'Professional', 'Intermediate'])})" 
                           for lang in languages]
            
            # Generate education (1-2 degrees)
            num_degrees = 1 if years_experience < 5 else random.randint(1, 2)
            education_list = random.sample(self.EDUCATION, num_degrees)
            
            # Generate detailed work history
            work_history = self._generate_detailed_work_history(years_experience, service_line, job_titles_pool)
            
            # Generate key achievements/projects
            projects = self._generate_projects(service_line, years_experience)
            
            candidate = {
                "id": f"CV_{i:04d}",
                "name": f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                "email": f"{random.choice(self.first_names).lower()}.{random.choice(self.last_names).lower()}{random.randint(1,99)}@email.com",
                "phone": f"+{random.choice(['33', '44', '49', '34', '212'])} {random.randint(600000000, 799999999)}",
                "current_title": job_title,
                "service_line": service_line,
                "years_experience": years_experience,
                "experience_level": experience_level,
                "location": random.choice(FORVIS_LOCATIONS),
                "education": education_list,
                "certifications": certifications,
                "skills": skills,
                "languages": language_prof,
                "summary": self._generate_detailed_summary(job_title, years_experience, service_line, certifications),
                "work_history": work_history,
                "projects": projects,
                "last_application_date": last_application.strftime("%Y-%m-%d"),
                "is_dormant": is_dormant,
                "availability": random.choice(["Immediate", "2 weeks", "1 month", "2 months", "3 months"]),
                "expected_salary": self._calculate_salary(years_experience, experience_level, service_line),
                "remote_preference": random.choice([True, False, "Hybrid"]),
                "willing_to_relocate": random.choice([True, False]),
                "notice_period": random.choice(["None", "1 month", "2 months", "3 months"]),
                "created_at": last_application.strftime("%Y-%m-%d")
            }
            
            candidates.append(candidate)
        
        return candidates
    
    def _calculate_salary(self, years_exp: int, level: str, service_line: str) -> int:
        """Calculate realistic salary based on experience and role"""
        base_salaries = {
            "Intern": 25000,
            "Junior": 35000,
            "Mid-Level": 50000,
            "Senior": 70000,
            "Lead": 95000,
            "Principal": 120000,
            "Partner": 180000
        }
        
        # Premium for certain service lines
        premium_lines = ["Financial Advisory", "Consulting", "Digital & Technology"]
        multiplier = 1.15 if service_line in premium_lines else 1.0
        
        base = base_salaries.get(level, 50000)
        # Add variation
        salary = int(base * multiplier * random.uniform(0.9, 1.2))
        
        return salary
    
    def _generate_detailed_summary(self, title: str, years: int, service_line: str, certs: List[str]) -> str:
        """Generate a compelling professional summary"""
        templates = [
            f"Results-driven {title} with {years} years of expertise in {service_line.lower()}. "
            f"Proven track record of delivering high-impact solutions to Fortune 500 clients across EMEA region. "
            f"Strong background in financial analysis, regulatory compliance, and stakeholder management. "
            f"{self._get_cert_summary(certs)}",
            
            f"Accomplished {title} bringing {years} years of progressive experience in {service_line.lower()}. "
            f"Specialized in complex cross-border transactions, risk assessment, and strategic advisory. "
            f"Track record of managing multimillion-euro engagements and leading teams of up to {random.randint(5,15)} professionals. "
            f"{self._get_cert_summary(certs)}",
            
            f"Strategic {title} with {years} years navigating the evolving landscape of {service_line.lower()}. "
            f"Deep expertise in regulatory frameworks (IFRS, GDPR, SOX), digital transformation, and process optimization. "
            f"Known for building trusted client relationships and delivering measurable business value. "
            f"{self._get_cert_summary(certs)}",
            
            f"Experienced {title} professional with {years} years of hands-on experience in {service_line.lower()}. "
            f"Demonstrated ability to lead complex projects from inception to completion while maintaining highest quality standards. "
            f"Expertise spans financial modeling, due diligence, technology implementation, and change management. "
            f"{self._get_cert_summary(certs)}"
        ]
        
        return random.choice(templates)
    
    def _get_cert_summary(self, certs: List[str]) -> str:
        """Generate certification summary"""
        if not certs:
            return "Committed to continuous professional development."
        elif len(certs) == 1:
            return f"Holds {certs[0]} certification."
        else:
            return f"Holds multiple professional certifications including {certs[0]} and {certs[1]}."
    
    def _generate_detailed_work_history(self, years: int, service_line: str, titles_pool: List[str]) -> List[Dict]:
        """Generate realistic work history with career progression"""
        history = []
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Determine number of positions based on experience
        if years <= 2:
            num_positions = 1
        elif years <= 5:
            num_positions = 2
        elif years <= 10:
            num_positions = random.randint(2, 3)
        else:
            num_positions = random.randint(3, 5)
        
        years_remaining = years
        
        for i in range(num_positions):
            # Duration of this position (shorter for recent roles, longer for earlier)
            if i == 0:  # Current position
                duration = min(random.randint(2, 5), years_remaining)
            else:
                duration = min(random.randint(2, 4), years_remaining)
            
            years_remaining = max(0, years_remaining - duration)
            
            # Calculate dates
            end_year = current_year - sum(h.get('duration_years', 0) for h in history)
            end_month = current_month if i == 0 else random.randint(1, 12)
            start_year = end_year - duration
            start_month = random.randint(1, 12)
            
            # Select title (more senior for earlier positions if experienced)
            if i == 0:  # Current role
                title_idx = -1  # Most senior available
            else:
                # Progressive titles
                title_idx = max(0, len(titles_pool) - 1 - i * 2)
            
            title = titles_pool[min(title_idx, len(titles_pool) - 1)]
            
            # Select company (mix of Forvis Mazars and others)
            if i == 0 and random.random() < 0.3:
                company = "Forvis Mazars"
            else:
                company = random.choice(self.COMPANIES)
            
            # Generate achievements (2-4 per role)
            achievements = self._generate_achievements(title, service_line, duration)
            
            position = {
                "company": company,
                "title": title,
                "start_date": f"{start_year}-{start_month:02d}",
                "end_date": f"{end_year}-{end_month:02d}" if i > 0 else "Present",
                "duration_years": duration,
                "location": random.choice(FORVIS_LOCATIONS),
                "description": f"{'Led' if 'Senior' in title or 'Manager' in title else 'Supported'} {service_line.lower()} initiatives including client engagement, technical delivery, and team collaboration.",
                "achievements": achievements,
                "team_size": random.randint(1, 20) if any(x in title.lower() for x in ['manager', 'lead', 'director']) else None
            }
            
            history.append(position)
            
            if years_remaining <= 0:
                break
        
        return history
    
    def _generate_achievements(self, title: str, service_line: str, duration: int) -> List[str]:
        """Generate specific achievements for a role"""
        num_achievements = min(2 + duration, 5)
        
        achievement_pool = [
            f"Delivered {random.randint(5,30)} client engagements with average satisfaction score of {random.randint(85,98)}%",
            f"Reduced audit completion time by {random.randint(15,35)}% through process optimization",
            f"Identified cost savings opportunities totaling €{random.randint(1,10)}M for key clients",
            f"Led cross-functional team of {random.randint(4,12)} professionals across {random.randint(2,5)} countries",
            f"Developed automated reporting solution reducing manual effort by {random.randint(30,60)} hours/month",
            f"Achieved {random.randint(95,100)}% on-time delivery rate across all assigned projects",
            f"Mentored {random.randint(3,10)} junior staff members, {random.randint(2,5)} promoted within 18 months",
            f"Contributed to winning {random.randint(2,8)} new client proposals valued at €{random.randint(5,50)}M+",
            f"Implemented risk assessment framework adopted across {random.randint(15,40)} client engagements",
            f"Received '{random.choice(['Excellence Award', 'Top Performer Award', 'Client Impact Award'])}' for outstanding contributions"
        ]
        
        return random.sample(achievement_pool, num_achievements)
    
    def _generate_projects(self, service_line: str, years_exp: int) -> List[Dict]:
        """Generate notable projects/case studies"""
        if years_exp < 2:
            num_projects = random.randint(1, 2)
        elif years_exp < 5:
            num_projects = random.randint(2, 3)
        else:
            num_projects = random.randint(3, 5)
        
        projects = []
        
        for _ in range(num_projects):
            template = random.choice(self.PROJECT_TEMPLATES)
            
            # Fill template with realistic values
            project_desc = template.format(
                industry=random.choice(self.INDUSTRIES),
                revenue=random.randint(50, 5000),
                client_count=random.randint(5, 100),
                country_count=random.randint(3, 25),
                system=random.choice(["ERP", "CRM", "BI", "Data Analytics", "Cloud Migration", "Automation"]),
                improvement=random.randint(15, 50),
                deal_size=random.randint(10, 500),
                deal_type=random.choice(["M&A", "acquisition", "divestiture", "IPO", "restructuring"]),
                savings=random.randint(1, 50),
                amount=random.randint(1, 20)
            )
            
            projects.append({
                "description": project_desc,
                "year": datetime.now().year - random.randint(0, min(years_exp, 5)),
                "role": random.choice(["Project Lead", "Senior Consultant", "Technical Lead", "Team Member"])
            })
        
        return projects
    
    def generate_jobs(self, num_jobs: int = 50) -> List[Dict]:
        """Generate realistic job postings with detailed requirements"""
        jobs = []
        
        for i in range(num_jobs):
            service_line = random.choice(FORVIS_SERVICE_LINES)
            job_titles_pool = self.JOB_TITLES.get(service_line, ["Consultant"])
            job_title = random.choice(job_titles_pool)
            
            # Determine experience level from title
            if any(x in job_title.lower() for x in ["intern", "junior", "analyst"]):
                experience_level = random.choice(["Intern", "Junior"])
            elif any(x in job_title.lower() for x in ["senior", "lead"]):
                experience_level = random.choice(["Senior", "Lead"])
            elif any(x in job_title.lower() for x in ["partner", "director"]):
                experience_level = random.choice(["Principal", "Partner"])
            else:
                experience_level = random.choice(["Mid-Level", "Senior"])
            
            exp_min, exp_max = self.EXPERIENCE_LEVELS[experience_level]
            
            # Required skills (5-10 skills)
            required_skills = self._get_skills_for_service_line(service_line, exp_min + 2)
            required_languages = random.sample(FORVIS_SKILL_TAXONOMY["Languages"], random.randint(2, 3))
            
            # Preferred certifications
            preferred_certs = random.sample(self.CERTIFICATIONS, random.randint(1, 3))
            
            # Responsibilities (6-10 items)
            responsibilities = self._generate_detailed_responsibilities(job_title, service_line, experience_level)
            
            # Requirements
            requirements = self._generate_requirements(experience_level, service_line)
            
            # Benefits
            benefits = self._generate_benefits()
            
            job = {
                "id": f"JOB_{i:04d}",
                "title": job_title,
                "service_line": service_line,
                "location": random.choice(FORVIS_LOCATIONS),
                "experience_level": experience_level,
                "years_experience_min": exp_min,
                "years_experience_max": exp_max,
                "description": self._generate_detailed_job_description(job_title, service_line, experience_level),
                "responsibilities": responsibilities,
                "requirements": requirements,
                "required_skills": required_skills,
                "required_languages": required_languages,
                "preferred_certifications": preferred_certs,
                "preferred_education": random.choice(self.EDUCATION),
                "salary_range": self._get_salary_range(exp_min, exp_max, service_line),
                "benefits": benefits,
                "contract_type": random.choice(["Full-time", "Full-time", "Full-time", "Contract"]),  # 75% full-time
                "remote": random.choice([True, False, "Hybrid", "Hybrid"]),  # 50% hybrid
                "travel_required": random.choice(["None", "Occasional (10-25%)", "Frequent (25-50%)", "Extensive (50%+)"]),
                "team_size": random.randint(5, 50),
                "reports_to": random.choice(["Partner", "Director", "Senior Manager", "Manager"]),
                "posted_date": datetime.now().strftime("%Y-%m-%d"),
                "application_deadline": (datetime.now() + timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d"),
                "positions_available": random.randint(1, 5),
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            
            jobs.append(job)
        
        return jobs
    
    def _generate_detailed_job_description(self, title: str, service_line: str, level: str) -> str:
        """Generate compelling job description"""
        return f"""About Forvis Mazars
Forvis Mazars is a leading international audit, tax, and advisory firm operating in over 100 countries. We are committed to building a sustainable and prosperous future for our clients, people, and communities.

The Opportunity
We are seeking a talented {level} {title} to join our {service_line} team. In this role, you will work with a diverse portfolio of clients ranging from multinational corporations to high-growth startups, providing high-quality professional services and strategic advisory that makes a real impact.

What Makes This Role Unique
You will be part of a collaborative, innovation-driven environment that values diversity, integrity, and professional excellence. This position offers exposure to complex, cross-border engagements, cutting-edge methodologies, and opportunities for accelerated career development.

Our Culture
We foster a culture of continuous learning, work-life balance, and inclusion. With flexible working arrangements, comprehensive learning programs, and clear career progression paths, you'll have the support and resources to reach your full potential.

Impact
The work you do will directly contribute to our clients' success and societal progress. Join us in shaping the future of professional services."""
    
    def _generate_detailed_responsibilities(self, title: str, service_line: str, level: str) -> List[str]:
        """Generate detailed key responsibilities"""
        base_resp = [
            f"Lead and execute {service_line.lower()} engagements for multinational clients across diverse industries",
            "Develop and maintain strong, trusted relationships with C-level executives and key stakeholders",
            "Prepare high-quality deliverables including reports, presentations, and technical documentation",
            "Identify business development opportunities and contribute to proposal development",
            "Stay current with industry trends, regulatory changes, and emerging technologies",
            "Collaborate with cross-functional teams across multiple geographies and service lines"
        ]
        
        if any(x in level for x in ["Senior", "Lead", "Principal", "Partner"]):
            base_resp.extend([
                f"Mentor and coach teams of {random.randint(3,10)} junior professionals, fostering their professional growth",
                "Drive innovation and thought leadership through whitepapers, webinars, and conference presentations",
                "Participate in strategic planning and service line development initiatives",
                "Manage complex stakeholder relationships and navigate challenging client situations"
            ])
        else:
            base_resp.extend([
                "Support senior team members in executing complex projects and client deliverables",
                "Conduct research and analysis to support advisory recommendations",
                "Participate in team meetings, knowledge sharing sessions, and learning programs"
            ])
        
        return base_resp
    
    def _generate_requirements(self, level: str, service_line: str) -> List[str]:
        """Generate job requirements"""
        reqs = []
        
        if "Digital" in service_line or "Technology" in service_line:
            reqs.append(f"Bachelor's or Master's degree in Computer Science, Data Science, Engineering, or related field")
        else:
            reqs.append(f"Bachelor's or Master's degree in Business, Finance, Accounting, Economics, or related field")
        
        if "Junior" in level or "Intern" in level:
            reqs.extend([
                "Strong academic record (GPA 3.0+)",
                "Excellent analytical and problem-solving abilities",
                "Outstanding communication skills in English (written and verbal)",
                "Proficiency in Microsoft Office Suite (Excel, PowerPoint, Word)",
                "Demonstrated interest in professional services and client advisory"
            ])
        else:
            reqs.extend([
                "Proven track record of delivering high-quality work in fast-paced environments",
                "Exceptional analytical, critical thinking, and problem-solving skills",
                "Outstanding written and verbal communication abilities",
                "Advanced proficiency in relevant technical tools and software",
                "Strong project management and organizational capabilities",
                "Ability to work independently and as part of multicultural teams",
                "Client-focused mindset with ability to build lasting relationships"
            ])
        
        if any(x in level for x in ["Senior", "Lead", "Principal"]):
            reqs.append("Demonstrated leadership experience managing teams and complex projects")
        
        return reqs
    
    def _generate_benefits(self) -> List[str]:
        """Generate comprehensive benefits package"""
        all_benefits = [
            "Competitive salary and performance-based bonuses",
            "Comprehensive health insurance (medical, dental, vision)",
            "Retirement savings plan with employer matching",
            "25+ days annual leave plus public holidays",
            "Flexible/hybrid working arrangements",
            "Professional development budget (€2,000-5,000/year)",
            "Reimbursement for professional certifications (CPA, CFA, etc.)",
            "Sabbatical leave options after 5 years",
            "Employee assistance program and wellness initiatives",
            "Parental leave (maternity and paternity)",
            "Commuter benefits and bike-to-work schemes",
            "Technology allowance for home office setup",
            "Annual team offsites and social events",
            "Mentorship and coaching programs",
            "Internal mobility opportunities across global offices",
            "Discounted gym memberships",
            "Learning platform access (Coursera, LinkedIn Learning, etc.)",
            "Diversity and inclusion initiatives"
        ]
        
        return random.sample(all_benefits, random.randint(10, 15))
    
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
        # Save candidates
        cv_path = CV_DATA_FILE
        with open(cv_path, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(candidates)} candidates to {cv_path}")
        
        # Save jobs
        job_path = JOB_DATA_FILE
        with open(job_path, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(jobs)} jobs to {job_path}")
        
        # Generate statistics
        self._print_statistics(candidates, jobs)
    
    def _print_statistics(self, candidates: List[Dict], jobs: List[Dict]):
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


def main():
    """Main execution function"""
    print("="*60)
    print("SYNTHETIC DATA GENERATION - FORVIS MAZARS ATS")
    print("="*60)
    
    generator = SyntheticDataGenerator()
    
    print(f"\n[1/2] Generating {NUM_SYNTHETIC_CVS} candidate profiles...")
    candidates = generator.generate_candidates(NUM_SYNTHETIC_CVS)
    
    print(f"\n[2/2] Generating {NUM_SYNTHETIC_JOBS} job postings...")
    jobs = generator.generate_jobs(NUM_SYNTHETIC_JOBS)
    
    print(f"\n[3/3] Saving data...")
    generator.save_data(candidates, jobs)
    
    print("\n" + "="*60)
    print("✅ DATA GENERATION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()