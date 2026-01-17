import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from src.utils.preprocessor import DataPreprocessor
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def main():
    print("=" * 60)
    print("DATA PREPROCESSING")
    print("=" * 60)
    
    print("\n[1/2] Processing Resumes...")
    resumes_raw = pd.read_json(RAW_DATA_DIR / "resumes_raw.json")
    resumes_processed = DataPreprocessor.process_resumes(resumes_raw)
    
    output_path = PROCESSED_DATA_DIR / "cvs.json"
    resumes_processed.to_json(output_path, orient='records', indent=2)
    print(f"Saved {len(resumes_processed)} processed resumes to {output_path}")
    print(f"Dormant CVs: {resumes_processed['is_dormant'].sum()}")
    
    print("\n[2/2] Processing Jobs...")
    jobs_raw = pd.read_json(RAW_DATA_DIR / "jobs_raw.json")
    jobs_processed = DataPreprocessor.process_jobs(jobs_raw)
    
    output_path = PROCESSED_DATA_DIR / "jobs.json"
    jobs_processed.to_json(output_path, orient='records', indent=2)
    print(f"Saved {len(jobs_processed)} processed jobs to {output_path}")
    
    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()