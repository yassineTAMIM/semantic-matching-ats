import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.data_loader import DatasetLoader

def main():
    print("=" * 60)
    print("DATASET DOWNLOAD SCRIPT")
    print("=" * 60)
    
    loader = DatasetLoader()
    
    print("\n[1/2] Downloading Resumes...")
    resumes_df = loader.load_resumes(num_samples=1000)
    
    if not resumes_df.empty:
        loader.save_to_json(resumes_df, "resumes_raw.json")
        print(f"Categories: {resumes_df['category'].value_counts().to_dict()}")
    
    print("\n[2/2] Downloading Job Postings...")
    jobs_df = loader.load_jobs(num_samples=300)
    
    if not jobs_df.empty:
        loader.save_to_json(jobs_df, "jobs_raw.json")
        print(f"Sample job titles: {jobs_df['job_title_short'].value_counts().head()}")
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()