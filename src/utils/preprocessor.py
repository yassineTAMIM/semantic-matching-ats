import pandas as pd
import re
from typing import List
from datetime import datetime, timedelta
import random

class DataPreprocessor:
    
    @staticmethod
    def clean_text(text: str) -> str:
        if not isinstance(text, str):
            return ""
        
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-.,]', '', text)
        return text.strip()
    
    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        common_skills = [
            'python', 'java', 'sql', 'javascript', 'react', 'node', 'aws',
            'azure', 'docker', 'kubernetes', 'machine learning', 'data analysis',
            'excel', 'tableau', 'power bi', 'spark', 'hadoop', 'git',
            'agile', 'scrum', 'leadership', 'communication', 'project management',
            'r', 'sas', 'stata', 'spss', 'matlab', 'tensorflow', 'pytorch',
            'scikit-learn', 'pandas', 'numpy', 'data engineering', 'etl',
            'api', 'rest', 'microservices', 'ci/cd', 'jenkins', 'terraform'
        ]
        
        text_lower = text.lower()
        found_skills = [skill for skill in common_skills if skill in text_lower]
        return found_skills if found_skills else ['general']
    
    @staticmethod
    def process_resumes(df: pd.DataFrame) -> pd.DataFrame:
        processed = []
        
        for idx, row in df.iterrows():
            resume_text = row.get('resume_text', '')
            
            months_ago = random.randint(1, 24)
            last_active = datetime.now() - timedelta(days=months_ago * 30)
            
            skills = DataPreprocessor.extract_skills_from_text(resume_text)
            
            processed_cv = {
                'id': f"CV_{idx:04d}",
                'raw_text': resume_text,
                'category': row.get('category', 'Unknown'),
                'skills': skills,
                'experience_years': random.randint(1, 15),
                'location': random.choice(['Paris', 'London', 'Berlin', 'Madrid', 'Remote']),
                'last_active_date': last_active.strftime('%Y-%m-%d'),
                'is_dormant': months_ago >= 6
            }
            
            processed.append(processed_cv)
        
        return pd.DataFrame(processed)
    
    @staticmethod
    def process_jobs(df: pd.DataFrame) -> pd.DataFrame:
        processed = []
        
        for idx, row in df.iterrows():
            job_title_short = str(row.get('job_title_short', 'Unknown'))
            job_title_full = str(row.get('job_title', job_title_short))
            
            job_location = str(row.get('job_location', 'Remote'))
            company_name = str(row.get('company_name', 'Unknown Company'))
            
            description_parts = [
                f"Position: {job_title_full}",
                f"Company: {company_name}",
                f"Location: {job_location}"
            ]
            
            if pd.notna(row.get('job_schedule_type')):
                description_parts.append(f"Schedule: {row['job_schedule_type']}")
            
            job_description = ". ".join(description_parts)
            
            skills = DataPreprocessor.extract_skills_from_text(job_title_full)
            
            processed_job = {
                'id': f"JOB_{idx:04d}",
                'title': job_title_short,
                'description': job_description,
                'full_title': job_title_full,
                'company': company_name,
                'required_skills': skills,
                'location': job_location,
                'schedule': str(row.get('job_schedule_type', 'Full-time')),
                'remote': bool(row.get('job_work_from_home', False)),
                'posted_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            processed.append(processed_job)
        
        return pd.DataFrame(processed)