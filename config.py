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
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EMBEDDINGS_DIR, INDICES_DIR, SYNTHETIC_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Model configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # 384 dimensions, CPU-friendly
EMBEDDING_DIMENSION = 384
BATCH_SIZE = 32  # For CPU processing
MAX_SEQ_LENGTH = 512  # Maximum token length

# Matching parameters
TOP_K_CANDIDATES = 10  # Number of top candidates to return
TOP_K_FAISS = 50  # Number of candidates to retrieve from FAISS before re-ranking
SIMILARITY_THRESHOLD = 0.60  # Minimum similarity score (0-1)
MIN_SKILLS_OVERLAP = 0.1  # Minimum skill overlap ratio

# Dormant talent detection
DORMANT_THRESHOLD_MONTHS = 6  # Consider CV dormant after 6 months
DORMANT_EVOLUTION_WEIGHT = 0.2  # Weight for evolution score
DORMANT_MIN_SCORE = 0.75  # Minimum score to trigger dormant alert

# Scoring weights
WEIGHTS = {
    "semantic": 0.70,      # Semantic similarity weight
    "skills": 0.20,        # Skill overlap weight
    "experience": 0.07,    # Experience match weight
    "location": 0.03       # Location match weight
}

# FAISS configuration
FAISS_INDEX_TYPE = "IVFFlat"  # Index type
FAISS_NLIST = 100  # Number of clusters for IVF
FAISS_NPROBE = 10  # Number of clusters to search

# File paths
CV_DATA_FILE = PROCESSED_DATA_DIR / "candidates.json"
JOB_DATA_FILE = PROCESSED_DATA_DIR / "jobs.json"
APPLICATIONS_FILE = PROCESSED_DATA_DIR / "applications.json"
CV_EMBEDDINGS_FILE = EMBEDDINGS_DIR / "cv_embeddings.npy"
JOB_EMBEDDINGS_FILE = EMBEDDINGS_DIR / "job_embeddings.npy"
CV_IDS_FILE = EMBEDDINGS_DIR / "cv_ids.json"
JOB_IDS_FILE = EMBEDDINGS_DIR / "job_ids.json"
FAISS_INDEX_FILE = INDICES_DIR / "cv_index.faiss"
METADATA_DB_FILE = PROCESSED_DATA_DIR / "metadata.sqlite"

# Synthetic data generation
NUM_SYNTHETIC_CVS = 1000
NUM_SYNTHETIC_JOBS = 50
SYNTHETIC_DATE_RANGE_YEARS = 3

# Forvis Mazars specific
FORVIS_LOCATIONS = [
    "Paris, France", "London, UK", "Frankfurt, Germany", 
    "Madrid, Spain", "Amsterdam, Netherlands", "Brussels, Belgium",
    "Casablanca, Morocco", "Dubai, UAE", "Singapore", "New York, USA",
    "Remote"
]

FORVIS_SERVICE_LINES = [
    "Audit & Assurance",
    "Tax & Legal",
    "Financial Advisory",
    "Consulting",
    "Outsourcing",
    "Digital & Technology",
    "Risk Management",
    "Sustainability & ESG"
]

FORVIS_SKILL_TAXONOMY = {
    "Technical": [
        "Python", "R", "SQL", "Java", "JavaScript", "C++",
        "Power BI", "Tableau", "Excel", "SAP", "Oracle",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Data Engineering", "ETL", "Spark", "Hadoop"
    ],
    "Audit & Compliance": [
        "IFRS", "GAAP", "ISA", "SOX Compliance", "Internal Audit",
        "Risk Assessment", "Financial Reporting", "Regulatory Compliance",
        "COSO Framework", "ISO Standards", "GDPR", "Anti-Money Laundering"
    ],
    "Tax & Legal": [
        "Corporate Tax", "VAT/GST", "Transfer Pricing", "Tax Planning",
        "International Tax", "M&A Tax", "Tax Compliance", "Tax Technology",
        "Legal Drafting", "Contract Law", "Corporate Law"
    ],
    "Consulting": [
        "Strategy Consulting", "Change Management", "Business Transformation",
        "Process Optimization", "M&A Advisory", "Due Diligence",
        "Financial Modeling", "Valuation", "Feasibility Studies",
        "Project Management", "Agile", "Scrum", "Lean Six Sigma"
    ],
    "Financial": [
        "Financial Analysis", "Budgeting", "Forecasting", "FP&A",
        "Treasury Management", "Cash Flow Analysis", "Cost Accounting",
        "Management Accounting", "Financial Planning"
    ],
    "Soft Skills": [
        "Leadership", "Communication", "Teamwork", "Problem Solving",
        "Critical Thinking", "Stakeholder Management", "Presentation",
        "Negotiation", "Client Relationship Management", "Analytical Thinking"
    ],
    "Languages": [
        "English", "French", "German", "Spanish", "Arabic",
        "Dutch", "Italian", "Portuguese", "Mandarin"
    ]
}

# UI configuration
APP_TITLE = "🎯 Forvis Mazars - Semantic Candidate Matching System"
APP_DESCRIPTION = "AI-powered recruitment matching with dormant talent rediscovery"
APP_ICON = "🎯"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = PROJECT_ROOT / "logs" / "app.log"

# Create logs directory
(PROJECT_ROOT / "logs").mkdir(exist_ok=True)

# Evaluation metrics
EVALUATION_METRICS = [
    "precision@10",
    "recall@10",
    "mrr",  # Mean Reciprocal Rank
    "ndcg@10"  # Normalized Discounted Cumulative Gain
]

print(f"✅ Configuration loaded. Project root: {PROJECT_ROOT}")
