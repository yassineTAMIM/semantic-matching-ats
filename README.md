# Semantic Candidate Matching System

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![NLP](https://img.shields.io/badge/NLP-Sentence--BERT-orange.svg)](https://www.sbert.net/)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()

AI-powered recruitment matching engine with semantic understanding and dormant talent rediscovery capabilities.

## Overview

This system implements an intelligent candidate-job matching engine using state-of-the-art Natural Language Processing techniques. Built for Forvis Mazars as part of a final-year engineering project at École Centrale Casablanca, it addresses inefficiencies in traditional keyword-based recruitment systems by leveraging semantic embeddings and vector search.

### Key Capabilities

- **Semantic Matching**: Sentence-BERT embeddings capture contextual meaning beyond keyword matching
- **Dormant Talent Rediscovery**: Automatic identification of previously inactive candidates relevant to new positions
- **Explainable AI**: Transparent score decomposition with skill gap analysis
- **Performance**: Sub-2-second search across 1000+ candidates using FAISS vector indexing
- **Scalability**: CPU-optimized architecture suitable for production deployment

## Architecture
```
Data Pipeline → Embedding Generation → Vector Indexing → Semantic Search → Explainability
     ↓                    ↓                   ↓                ↓                ↓
HuggingFace      Sentence-BERT          FAISS          Cosine Similarity   Score Breakdown
```

## Dataset

### Resume Corpus

| Metric | Value |
|--------|-------|
| Source | [Divyaamith/Kaggle-Resume](https://huggingface.co/datasets/Divyaamith/Kaggle-Resume) |
| Total Records | 1,000 CVs |
| Categories | 11 professional domains |
| Dormant Candidates | 774 (>6 months inactive) |
| Fields | ID, raw text, category, skills, experience, location, last active date |

**Category Distribution:**
- Information Technology: 120
- Business Development: 120
- Legal/Advocate: 118
- Fitness: 117
- Healthcare: 115
- Human Resources: 110
- Designer: 107
- Education: 102
- Agriculture: 63
- BPO: 22
- Sales: 6

### Job Postings

| Metric | Value |
|--------|-------|
| Source | [lukebarousse/data_jobs](https://huggingface.co/datasets/lukebarousse/data_jobs) |
| Total Records | 300 positions |
| Unique Titles | 10 distinct roles |
| Fields | ID, title, description, company, skills, location, schedule, remote flag |

**Primary Roles:**
- Senior Data Engineer
- Data Analyst
- Data Scientist
- Business Intelligence Analyst
- Machine Learning Engineer

## Installation

### Prerequisites

- Python 3.10 or higher
- Conda (recommended) or virtualenv
- 4GB RAM minimum
- CPU-only compatible (no GPU required)

### Setup with Conda (Recommended)
```bash
git clone https://github.com/yassineTAMIM/semantic-matching-ats.git
cd semantic-matching-ats

conda env create -f environment.yml
conda activate matching-ats

python scripts/verify_setup.py
```

### Setup with pip
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python scripts/verify_setup.py
```

## Project Structure
```
semantic-matching-ats/
├── config.py                   # Central configuration
├── data/
│   ├── raw/                    # Original HuggingFace datasets
│   ├── processed/              # Cleaned and standardized data
│   ├── embeddings/             # Sentence-BERT vector representations
│   └── indices/                # FAISS search indices
├── src/
│   ├── models/                 # Embedding generation modules
│   ├── search/                 # FAISS-based matching engine
│   ├── explainability/         # Score decomposition logic
│   └── utils/                  # Data loaders and preprocessing
├── scripts/
│   ├── download_datasets.py    # Fetch data from HuggingFace
│   ├── preprocess_data.py      # Transform and standardize
│   └── inspect_data.py         # Data quality verification
├── ui/                         # Streamlit web interface
└── tests/                      # Unit and integration tests
```

## Usage

### Data Acquisition
```bash
python scripts/download_datasets.py
python scripts/preprocess_data.py
```

### Verification
```bash
python scripts/inspect_data.py
```

Expected output:
```
CVS DATASET
----------------------------------------
Total CVs: 1000
Dormant CVs (6+ months): 774
Categories: 11

JOBS DATASET
----------------------------------------
Total Jobs: 300
Unique Titles: 10
```

## Development Roadmap

- [x] Phase 1: Environment setup and dependency management
- [x] Phase 2: Data acquisition from HuggingFace
- [x] Phase 2: Data preprocessing and standardization
- [ ] Phase 3: Sentence-BERT embedding generation
- [ ] Phase 4: FAISS vector index construction
- [ ] Phase 5: Semantic matching algorithm
- [ ] Phase 6: Dormant talent detection module
- [ ] Phase 7: Explainability engine
- [ ] Phase 8: Streamlit user interface
- [ ] Phase 9: Testing and validation
- [ ] Phase 10: Documentation and deployment

## Technical Stack

**Core Libraries:**
- `sentence-transformers==2.2.2` - Semantic embeddings
- `faiss-cpu==1.7.4` - Vector similarity search
- `transformers==4.35.0` - BERT model infrastructure
- `streamlit==1.28.2` - Web interface
- `pandas==2.0.3` - Data manipulation
- `scikit-learn==1.3.2` - Additional ML utilities

**Model:**
- `all-MiniLM-L6-v2` (384 dimensions, CPU-optimized)

## Team

**École Centrale Casablanca - Class of 2026**

- ABSRI Imad
- EL BAHA Ali
- EL MAIMOUNI Kenza
- RAMDANI Nabil
- TAMIM Yassine

**Partner:** Forvis Mazars

## License

MIT License

Copyright (c) 2026 École Centrale Casablanca