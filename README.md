# 🎯 Semantic Candidate Matching System

AI-powered recruitment matching engine with dormant talent rediscovery.

## 🚀 Features

- **Semantic Matching**: Uses Sentence-BERT embeddings for intelligent CV-job matching
- **Dormant Talent Rediscovery**: Automatically identifies relevant past candidates
- **Explainable Scoring**: Transparent breakdown of match scores
- **Fast & Scalable**: FAISS-powered vector search (< 2s for 1000+ CVs)

## 📦 Installation

### Option 1: Using Conda (Recommended for Windows)
```bash
# Clone repository
git clone <your-repo-url>
cd semantic-matching-ats

# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate matching-ats
```

### Option 2: Using pip (Linux/Mac)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ▶️ Quick Start
```bash
# Activate environment
conda activate matching-ats

# Verify setup
python scripts/verify_setup.py
```

## 🛠️ Development Status

- [x] Phase 1: Project setup
- [ ] Phase 2: Mock data generation
- [ ] Phase 3: Embedding pipeline
- [ ] Phase 4: FAISS indexing
- [ ] Phase 5: Matching logic
- [ ] Phase 6: Dormant talent detection
- [ ] Phase 7: Explainability module
- [ ] Phase 8: Streamlit UI

## 👥 Team

ABSRI Imad, EL BAHA Ali, EL MAIMOUNI Kenza, RAMDANI Nabil, TAMIM Yassine

## 📝 License

Academic project - École Centrale Casablanca