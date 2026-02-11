# 🚀 QUICK START GUIDE

## Get Started in 5 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### Step 2: Verify Setup (30 seconds)

```bash
python verify_setup.py
```

Expected output:
```
✅ Python 3.10.x
✅ sentence_transformers
✅ faiss
...
⚠️  SETUP INCOMPLETE - Data not generated yet
```

### Step 3: Generate Data & Build System (5-10 minutes)

```bash
python pipeline.py
```

This will:
1. Generate 1000 realistic CVs + 50 jobs
2. Create semantic embeddings
3. Build FAISS search index

**Note:** First run downloads the Sentence-BERT model (~90MB). Grab a coffee! ☕

### Step 4: Launch the App (30 seconds)

```bash
streamlit run app.py
```

Opens at: `http://localhost:8501`

---

## What Can I Do Now?

### 🔍 Search Candidates
1. Go to "Candidate Search" page
2. Select a job position
3. Click "Find Candidates"
4. View top 10 matches with scores

### 🔔 Discover Dormant Talents
1. Go to "Dormant Talent Alerts"
2. Select a job position
3. Click "Scan Dormant Candidates"
4. See candidates who applied 6+ months ago

### 📊 View Analytics
1. Go to "Analytics Dashboard"
2. See system statistics
3. Distribution charts

---

## Testing Individual Components

### Test Matching Engine
```bash
python src/search/matching_engine.py
```

Output: Top 10 candidates for a sample job

### Test Dormant Detector
```bash
python src/search/dormant_detector.py
```

Output: Dormant talent alerts for a sample job

### Test Embeddings
```bash
python src/models/embedding_engine.py
```

Output: Embedding statistics

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'sentence_transformers'"
```bash
pip install -r requirements.txt
```

### "FileNotFoundError: data/processed/candidates.json"
```bash
python pipeline.py
```

### "Model download is slow"
Be patient - first run downloads 90MB model (one-time only)

---

## Next Steps

1. **Customize**: Edit `config.py` to adjust scoring weights
2. **Evaluate**: Check matching quality with your own test cases
3. **Extend**: Add new features (see README.md roadmap)

---

**Need Help?**
- Check README.md for full documentation
- Run `python verify_setup.py` to diagnose issues
- Contact team: centrale-matching-ats@gmail.com

---

**Enjoy! 🎉**
