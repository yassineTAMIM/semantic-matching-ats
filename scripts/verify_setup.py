"""
Setup verification script
Checks if environment is correctly configured
"""

import sys
from pathlib import Path

def verify_setup():
    print("🔍 Verifying project setup...\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Python version
    checks_total += 1
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 9:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        checks_passed += 1
    else:
        print(f"❌ Python version too old: {python_version.major}.{python_version.minor}")
    
    # Check 2: Required packages
    required_packages = [
        "sentence_transformers",
        "faiss",
        "pandas",
        "numpy",
        "streamlit",
        "sklearn"
    ]
    
    for package in required_packages:
        checks_total += 1
        try:
            __import__(package)
            print(f"✅ Package '{package}' installed")
            checks_passed += 1
        except ImportError:
            print(f"❌ Package '{package}' NOT installed")
    
    # Check 3: Directory structure
    required_dirs = [
        "data/raw",
        "data/processed",
        "data/embeddings",
        "data/indices",
        "src/models",
        "src/search",
        "src/explainability",
        "src/utils"
    ]
    
    for dir_path in required_dirs:
        checks_total += 1
        if Path(dir_path).exists():
            print(f"✅ Directory '{dir_path}' exists")
            checks_passed += 1
        else:
            print(f"❌ Directory '{dir_path}' NOT found")
    
    # Check 4: Config file
    checks_total += 1
    if Path("config.py").exists():
        print("✅ Configuration file exists")
        checks_passed += 1
    else:
        print("❌ Configuration file NOT found")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Setup verification: {checks_passed}/{checks_total} checks passed")
    
    if checks_passed == checks_total:
        print("🎉 Setup complete! Ready to proceed to Phase 2.")
        return True
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    verify_setup()