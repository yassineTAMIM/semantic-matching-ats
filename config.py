"""
Configuration file for Semantic Matching ATS
Centralized settings for models, paths, and parameters
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
INDICES_DIR = DATA_DIR / "indices"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EMBEDDINGS_DIR, INDICES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Model configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # 384 dimensions, CPU-friendly
EMBEDDING_DIMENSION = 384
BATCH_SIZE = 32  # For CPU processing

# Matching parameters
TOP_K_CANDIDATES = 10  # Number of top candidates to return
SIMILARITY_THRESHOLD = 0.65  # Minimum similarity score (0-1)

# Dormant talent detection
DORMANT_THRESHOLD_MONTHS = 6  # Consider CV dormant after 6 months

# Scoring weights
WEIGHTS = {
    "semantic": 0.60,      # Semantic similarity weight
    "skills": 0.25,        # Skill overlap weight
    "experience": 0.10,    # Experience match weight
    "location": 0.05       # Location match weight
}

# File paths
CV_DATA_FILE = RAW_DATA_DIR / "cvs.json"
JOB_DATA_FILE = RAW_DATA_DIR / "jobs.json"
CV_EMBEDDINGS_FILE = EMBEDDINGS_DIR / "cv_embeddings.npy"
JOB_EMBEDDINGS_FILE = EMBEDDINGS_DIR / "job_embeddings.npy"
FAISS_INDEX_FILE = INDICES_DIR / "cv_index.bin"
METADATA_DB_FILE = PROCESSED_DATA_DIR / "metadata.db"

# UI configuration
APP_TITLE = "🎯 Semantic Candidate Matching System"
APP_DESCRIPTION = "AI-powered recruitment matching with dormant talent rediscovery"

# Logging
LOG_LEVEL = "INFO"

print(f"✅ Configuration loaded. Project root: {PROJECT_ROOT}")