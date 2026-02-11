"""
Embedding Engine - Sentence-BERT based semantic embeddings
Generates and manages vector representations of candidates and jobs
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *


class EmbeddingEngine:
    """Generate and manage semantic embeddings using Sentence-BERT"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        """
        Initialize the embedding engine
        
        Args:
            model_name: HuggingFace model identifier
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.model.max_seq_length = MAX_SEQ_LENGTH
        print(f"✅ Model loaded successfully. Embedding dimension: {EMBEDDING_DIMENSION}")
    
    def create_candidate_text(self, candidate: Dict) -> str:
        """
        Create a rich text representation of a candidate for embedding
        
        Args:
            candidate: Candidate dictionary
            
        Returns:
            Formatted text string
        """
        parts = []
        
        # Title and summary
        parts.append(f"Title: {candidate.get('current_title', '')}")
        parts.append(f"Summary: {candidate.get('summary', '')}")
        
        # Service line and experience
        parts.append(f"Service Line: {candidate.get('service_line', '')}")
        parts.append(f"Experience: {candidate.get('years_experience', 0)} years as {candidate.get('experience_level', '')}")
        
        # Education (handle list or string)
        education = candidate.get('education', [])
        if isinstance(education, list):
            parts.append(f"Education: {'; '.join(education)}")
        else:
            parts.append(f"Education: {education}")
        
        # Certifications
        if candidate.get('certifications'):
            parts.append(f"Certifications: {', '.join(candidate['certifications'])}")
        
        # Skills
        if candidate.get('skills'):
            parts.append(f"Skills: {', '.join(candidate['skills'][:15])}")  # Top 15 skills
        
        # Languages
        if candidate.get('languages'):
            parts.append(f"Languages: {', '.join(candidate['languages'])}")
        
        # Work history - include recent positions and achievements
        if candidate.get('work_history'):
            work_texts = []
            for work in candidate['work_history'][:3]:  # Last 3 positions
                work_text = f"{work.get('title', '')} at {work.get('company', '')}"
                if work.get('achievements'):
                    # Include first achievement for context
                    work_text += f". {work['achievements'][0]}"
                work_texts.append(work_text)
            parts.append(f"Work History: {'; '.join(work_texts)}")
        
        # Projects - include recent projects
        if candidate.get('projects'):
            project_texts = [p.get('description', '') for p in candidate['projects'][:2]]
            if project_texts:
                parts.append(f"Key Projects: {'; '.join(project_texts)}")
        
        # Location and availability
        parts.append(f"Location: {candidate.get('location', '')}")
        parts.append(f"Remote: {candidate.get('remote_preference', 'No')}")
        
        return ". ".join(parts)
    
    def create_job_text(self, job: Dict) -> str:
        """
        Create a rich text representation of a job for embedding
        
        Args:
            job: Job dictionary
            
        Returns:
            Formatted text string
        """
        parts = []
        
        # Title and service line
        parts.append(f"Position: {job.get('title', '')}")
        parts.append(f"Service Line: {job.get('service_line', '')}")
        
        # Description
        parts.append(f"Description: {job.get('description', '')}")
        
        # Experience requirements
        exp_min = job.get('years_experience_min', 0)
        exp_max = job.get('years_experience_max', 0)
        parts.append(f"Required Experience: {exp_min} to {exp_max} years, {job.get('experience_level', '')} level")
        
        # Education and certifications
        education = job.get('preferred_education', '')
        if isinstance(education, list):
            parts.append(f"Preferred Education: {'; '.join(education)}")
        else:
            parts.append(f"Preferred Education: {education}")
        
        if job.get('preferred_certifications'):
            parts.append(f"Preferred Certifications: {', '.join(job['preferred_certifications'])}")
        
        # Skills
        if job.get('required_skills'):
            parts.append(f"Required Skills: {', '.join(job['required_skills'][:15])}")  # Top 15
        
        # Languages
        if job.get('required_languages'):
            parts.append(f"Required Languages: {', '.join(job['required_languages'])}")
        
        # Responsibilities (first 5)
        if job.get('responsibilities'):
            parts.append(f"Responsibilities: {'; '.join(job['responsibilities'][:5])}")
        
        # Requirements (first 5)
        if job.get('requirements'):
            parts.append(f"Requirements: {'; '.join(job['requirements'][:5])}")
        
        # Location and remote
        parts.append(f"Location: {job.get('location', '')}")
        parts.append(f"Remote Work: {job.get('remote', 'No')}")
        
        # Travel
        if job.get('travel_required'):
            parts.append(f"Travel: {job['travel_required']}")
        
        return ". ".join(parts)
    
    def generate_embeddings(self, texts: List[str], batch_size: int = BATCH_SIZE, 
                          desc: str = "Generating embeddings") -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            desc: Description for progress bar
            
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        embeddings = []
        
        # Process in batches with progress bar
        for i in tqdm(range(0, len(texts), batch_size), desc=desc):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(
                batch,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )
            embeddings.append(batch_embeddings)
        
        # Concatenate all batches
        embeddings = np.vstack(embeddings)
        
        print(f"✅ Generated {len(embeddings)} embeddings of dimension {embeddings.shape[1]}")
        return embeddings
    
    def process_candidates(self, candidates: List[Dict]) -> Tuple[np.ndarray, List[str]]:
        """
        Process candidates and generate embeddings
        
        Args:
            candidates: List of candidate dictionaries
            
        Returns:
            Tuple of (embeddings array, list of candidate IDs)
        """
        print(f"\n{'='*60}")
        print(f"Processing {len(candidates)} candidates...")
        print(f"{'='*60}")
        
        # Create text representations
        print("Creating text representations...")
        texts = [self.create_candidate_text(c) for c in candidates]
        ids = [c['id'] for c in candidates]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(
            texts, 
            batch_size=BATCH_SIZE,
            desc="Encoding candidates"
        )
        
        return embeddings, ids
    
    def process_jobs(self, jobs: List[Dict]) -> Tuple[np.ndarray, List[str]]:
        """
        Process jobs and generate embeddings
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Tuple of (embeddings array, list of job IDs)
        """
        print(f"\n{'='*60}")
        print(f"Processing {len(jobs)} jobs...")
        print(f"{'='*60}")
        
        # Create text representations
        print("Creating text representations...")
        texts = [self.create_job_text(j) for j in jobs]
        ids = [j['id'] for j in jobs]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(
            texts,
            batch_size=BATCH_SIZE,
            desc="Encoding jobs"
        )
        
        return embeddings, ids
    
    def save_embeddings(self, embeddings: np.ndarray, ids: List[str], 
                       embeddings_file: Path, ids_file: Path):
        """
        Save embeddings and IDs to files
        
        Args:
            embeddings: numpy array of embeddings
            ids: list of IDs
            embeddings_file: path to save embeddings (.npy)
            ids_file: path to save IDs (.json)
        """
        # Save embeddings as numpy array
        np.save(embeddings_file, embeddings)
        print(f"✅ Saved embeddings to {embeddings_file}")
        
        # Save IDs as JSON
        with open(ids_file, 'w') as f:
            json.dump(ids, f, indent=2)
        print(f"✅ Saved IDs to {ids_file}")
    
    def load_embeddings(self, embeddings_file: Path, ids_file: Path) -> Tuple[np.ndarray, List[str]]:
        """
        Load embeddings and IDs from files
        
        Args:
            embeddings_file: path to embeddings file
            ids_file: path to IDs file
            
        Returns:
            Tuple of (embeddings array, list of IDs)
        """
        embeddings = np.load(embeddings_file)
        
        with open(ids_file, 'r') as f:
            ids = json.load(f)
        
        print(f"✅ Loaded {len(embeddings)} embeddings from {embeddings_file}")
        return embeddings, ids


def main():
    """Main execution function"""
    print("="*60)
    print("EMBEDDING GENERATION - SENTENCE-BERT")
    print("="*60)
    
    # Load data
    print("\nLoading candidate and job data...")
    with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    print(f"Loaded {len(candidates)} candidates and {len(jobs)} jobs")
    
    # Initialize embedding engine
    engine = EmbeddingEngine()
    
    # Process candidates
    print("\n[1/2] Processing candidates...")
    cv_embeddings, cv_ids = engine.process_candidates(candidates)
    engine.save_embeddings(cv_embeddings, cv_ids, CV_EMBEDDINGS_FILE, CV_IDS_FILE)
    
    # Process jobs
    print("\n[2/2] Processing jobs...")
    job_embeddings, job_ids = engine.process_jobs(jobs)
    engine.save_embeddings(job_embeddings, job_ids, JOB_EMBEDDINGS_FILE, JOB_IDS_FILE)
    
    # Print statistics
    print("\n" + "="*60)
    print("EMBEDDING GENERATION COMPLETE")
    print("="*60)
    print(f"Candidate embeddings: {cv_embeddings.shape}")
    print(f"Job embeddings: {job_embeddings.shape}")
    print(f"Embedding dimension: {EMBEDDING_DIMENSION}")
    print(f"Total memory: ~{(cv_embeddings.nbytes + job_embeddings.nbytes) / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()