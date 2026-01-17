from datasets import load_dataset
import pandas as pd
from pathlib import Path
from typing import Dict, List
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import RAW_DATA_DIR

class DatasetLoader:
    
    @staticmethod
    def load_resumes(num_samples: int = 1000) -> pd.DataFrame:
        print(f"Loading resume dataset from HuggingFace...")
        
        try:
            dataset = load_dataset("Divyaamith/Kaggle-Resume", split="train")
            df = pd.DataFrame(dataset)
            
            if num_samples:
                df = df.head(num_samples)
            
            df = df.rename(columns={
                'ID': 'id',
                'Resume_str': 'resume_text',
                'Category': 'category'
            })
            
            print(f"Loaded {len(df)} resumes across {df['category'].nunique()} categories")
            return df
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def load_jobs(num_samples: int = 500) -> pd.DataFrame:
        print(f"Loading job postings dataset from HuggingFace...")
        
        try:
            dataset = load_dataset("lukebarousse/data_jobs", split="train")
            df = pd.DataFrame(dataset)
            
            print(f"Dataset columns: {df.columns.tolist()}")
            
            if num_samples:
                df = df.head(num_samples)
            
            df = df.dropna(subset=['job_title_short'])
            
            print(f"Loaded {len(df)} job postings")
            return df
            
        except Exception as e:
            print(f"Error loading job dataset: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def save_to_json(df: pd.DataFrame, filename: str):
        filepath = RAW_DATA_DIR / filename
        df.to_json(filepath, orient='records', indent=2)
        print(f"Saved {len(df)} records to {filepath}")


if __name__ == "__main__":
    loader = DatasetLoader()
    
    resumes_df = loader.load_resumes(num_samples=1000)
    if not resumes_df.empty:
        loader.save_to_json(resumes_df, "resumes_raw.json")
    
    jobs_df = loader.load_jobs(num_samples=300)
    if not jobs_df.empty:
        loader.save_to_json(jobs_df, "jobs_raw.json")