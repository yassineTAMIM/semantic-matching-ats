import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from config import PROCESSED_DATA_DIR

def inspect_data():
    cvs = pd.read_json(PROCESSED_DATA_DIR / "cvs.json")
    jobs = pd.read_json(PROCESSED_DATA_DIR / "jobs.json")
    
    print("CVS DATASET")
    print("-" * 40)
    print(f"Total CVs: {len(cvs)}")
    print(f"Dormant CVs (6+ months): {cvs['is_dormant'].sum()}")
    print(f"Categories: {cvs['category'].nunique()}")
    print(f"\nSample CV:")
    print(cvs.iloc[0].to_dict())
    
    print("\n\nJOBS DATASET")
    print("-" * 40)
    print(f"Total Jobs: {len(jobs)}")
    print(f"Unique Titles: {jobs['title'].nunique()}")
    print(f"\nSample Job:")
    print(jobs.iloc[0].to_dict())

if __name__ == "__main__":
    inspect_data()