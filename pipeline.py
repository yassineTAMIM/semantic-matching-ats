"""
Complete Pipeline - End-to-end system setup
Generates data, builds embeddings, creates FAISS index
"""

import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent))

from src.data.synthetic_generator import SyntheticDataGenerator, main as generate_data
from src.models.embedding_engine import main as generate_embeddings
from src.search.faiss_indexer import main as build_index

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")

def main():
    """Run complete pipeline"""
    start_time = time.time()
    
    print_header("FORVIS MAZARS - SEMANTIC MATCHING ATS")
    print_header("COMPLETE PIPELINE EXECUTION")
    
    print("This pipeline will:")
    print("  1. Generate synthetic candidate and job data")
    print("  2. Create semantic embeddings using Sentence-BERT")
    print("  3. Build FAISS index for efficient search")
    print("  4. Validate the system")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Generate data
    print_header("STEP 1/3: GENERATING SYNTHETIC DATA")
    try:
        generate_data()
        print("✅ Data generation complete")
    except Exception as e:
        print(f"❌ Error in data generation: {e}")
        return
    
    # Step 2: Generate embeddings
    print_header("STEP 2/3: GENERATING EMBEDDINGS")
    try:
        generate_embeddings()
        print("✅ Embedding generation complete")
    except Exception as e:
        print(f"❌ Error in embedding generation: {e}")
        return
    
    # Step 3: Build index
    print_header("STEP 3/3: BUILDING FAISS INDEX")
    try:
        build_index()
        print("✅ FAISS index built successfully")
    except Exception as e:
        print(f"❌ Error in index building: {e}")
        return
    
    # Final summary
    elapsed_time = time.time() - start_time
    
    print_header("PIPELINE COMPLETE!")
    print(f"Total execution time: {elapsed_time/60:.2f} minutes")
    print("\nSystem is ready!")
    print("\nNext steps:")
    print("  1. Run the Streamlit app: streamlit run app.py")
    print("  2. Or test individual components:")
    print("     - Matching engine: python src/search/matching_engine.py")
    print("     - Dormant detector: python src/search/dormant_detector.py")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
