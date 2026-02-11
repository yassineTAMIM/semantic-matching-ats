"""
Matching Engine - Multi-criteria semantic matching
Combines FAISS semantic search with skill, experience, and location scoring
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import math
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *
from src.models.embedding_engine import EmbeddingEngine
from src.search.faiss_indexer import FAISSIndexer


class MatchingEngine:
    """
    Core matching engine combining semantic similarity with multi-criteria scoring
    """
    
    def __init__(self):
        """Initialize matching engine"""
        print("Initializing Matching Engine...")
        
        # Load embedding model
        self.embedding_engine = EmbeddingEngine()
        
        # Load FAISS index
        self.faiss_indexer = FAISSIndexer()
        
        # Load candidate embeddings and IDs
        print("Loading candidate data...")
        with open(CV_IDS_FILE, 'r') as f:
            cv_ids = json.load(f)
        
        self.faiss_indexer.load_index(FAISS_INDEX_FILE, cv_ids)
        
        # Load candidate metadata
        with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
        
        # Create ID to candidate mapping
        self.candidates_map = {c['id']: c for c in candidates}
        
        print(f"✅ Matching engine ready with {len(self.candidates_map)} candidates")
    
    def match_candidates(self, job: Dict, top_k: int = TOP_K_CANDIDATES, 
                        filters: Dict = None) -> List[Dict]:
        """
        Find and rank candidates for a job posting
        
        Args:
            job: Job dictionary
            top_k: Number of top candidates to return
            filters: Optional filters (location, experience, etc.)
            
        Returns:
            List of candidate matches with scores
        """
        print(f"\n{'='*60}")
        print(f"Matching candidates for: {job['title']}")
        print(f"{'='*60}")
        
        # Step 1: Generate job embedding
        job_text = self.embedding_engine.create_job_text(job)
        job_embedding = self.embedding_engine.model.encode(
            [job_text],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # Step 2: FAISS search for top candidates
        print(f"Searching {TOP_K_FAISS} semantic matches...")
        distances, indices = self.faiss_indexer.search(job_embedding, k=TOP_K_FAISS)
        candidate_ids = self.faiss_indexer.get_ids_from_indices(indices)[0]
        semantic_scores = distances[0]  # Already normalized (inner product of L2-normalized vectors)
        
        # Step 3: Apply filters if provided
        filtered_candidates = []
        for cand_id, sem_score in zip(candidate_ids, semantic_scores):
            candidate = self.candidates_map[cand_id]
            
            if filters and not self._passes_filters(candidate, filters):
                continue
            
            filtered_candidates.append((candidate, sem_score))
        
        print(f"After filtering: {len(filtered_candidates)} candidates")
        
        # Step 4: Multi-criteria scoring
        print("Computing multi-criteria scores...")
        scored_candidates = []
        
        for candidate, semantic_score in filtered_candidates:
            # Calculate individual scores
            skills_score = self._calculate_skills_score(candidate, job)
            experience_score = self._calculate_experience_score(candidate, job)
            location_score = self._calculate_location_score(candidate, job)
            
            # Weighted total score
            total_score = (
                WEIGHTS["semantic"] * semantic_score +
                WEIGHTS["skills"] * skills_score +
                WEIGHTS["experience"] * experience_score +
                WEIGHTS["location"] * location_score
            )
            
            match_result = {
                "candidate": candidate,
                "scores": {
                    "total": float(total_score),
                    "semantic": float(semantic_score),
                    "skills": float(skills_score),
                    "experience": float(experience_score),
                    "location": float(location_score)
                },
                "breakdown": self._generate_score_breakdown(
                    candidate, job, semantic_score, skills_score, 
                    experience_score, location_score
                )
            }
            
            scored_candidates.append(match_result)
        
        # Step 5: Sort by total score and return top K
        scored_candidates.sort(key=lambda x: x["scores"]["total"], reverse=True)
        top_candidates = scored_candidates[:top_k]
        
        print(f"✅ Returning top {len(top_candidates)} candidates")
        
        return top_candidates
    
    def _passes_filters(self, candidate: Dict, filters: Dict) -> bool:
        """Check if candidate passes filters"""
        
        # Location filter
        if filters.get('location') and candidate['location'] != filters['location']:
            if candidate['location'] != 'Remote' and not candidate.get('remote_preference'):
                return False
        
        # Experience filter
        if filters.get('min_experience'):
            if candidate['years_experience'] < filters['min_experience']:
                return False
        
        if filters.get('max_experience'):
            if candidate['years_experience'] > filters['max_experience']:
                return False
        
        # Availability filter
        if filters.get('availability'):
            if candidate['availability'] not in filters['availability']:
                return False
        
        return True
    
    def _calculate_skills_score(self, candidate: Dict, job: Dict) -> float:
        """
        Calculate skill overlap score using Jaccard similarity
        
        Args:
            candidate: Candidate dictionary
            job: Job dictionary
            
        Returns:
            Skill score (0-1)
        """
        candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
        required_skills = set([s.lower() for s in job.get('required_skills', [])])
        
        if not required_skills:
            return 1.0  # No specific skills required
        
        # Jaccard similarity
        intersection = len(candidate_skills & required_skills)
        union = len(candidate_skills | required_skills)
        
        if union == 0:
            return 0.0
        
        jaccard = intersection / union
        
        # Boost for high overlap
        overlap_ratio = intersection / len(required_skills) if required_skills else 0
        
        # Weighted score: 60% Jaccard + 40% overlap ratio
        score = 0.6 * jaccard + 0.4 * overlap_ratio
        
        return min(score, 1.0)
    
    def _calculate_experience_score(self, candidate: Dict, job: Dict) -> float:
        """
        Calculate experience match score using Gaussian function
        
        Args:
            candidate: Candidate dictionary
            job: Job dictionary
            
        Returns:
            Experience score (0-1)
        """
        candidate_exp = candidate.get('years_experience', 0)
        required_min = job.get('years_experience_min', 0)
        required_max = job.get('years_experience_max', 100)
        
        # Perfect match if within range
        if required_min <= candidate_exp <= required_max:
            return 1.0
        
        # Gaussian penalty for being outside range
        if candidate_exp < required_min:
            gap = required_min - candidate_exp
            # Less penalty for slightly under-qualified
            score = math.exp(-(gap ** 2) / (2 * 3 ** 2))  # sigma=3 years
        else:
            gap = candidate_exp - required_max
            # More penalty for over-qualified (might leave)
            score = math.exp(-(gap ** 2) / (2 * 2 ** 2))  # sigma=2 years
        
        return max(score, 0.0)
    
    def _calculate_location_score(self, candidate: Dict, job: Dict) -> float:
        """
        Calculate location match score
        
        Args:
            candidate: Candidate dictionary
            job: Job dictionary
            
        Returns:
            Location score (0-1)
        """
        candidate_location = candidate.get('location', '').lower()
        job_location = job.get('location', '').lower()
        
        # Perfect match
        if candidate_location == job_location:
            return 1.0
        
        # Remote positions
        if 'remote' in job_location or job.get('remote') == True:
            return 1.0
        
        # Candidate is remote or prefers remote
        if 'remote' in candidate_location or candidate.get('remote_preference') == True:
            return 0.8
        
        # Same country (basic heuristic)
        candidate_parts = candidate_location.split(',')
        job_parts = job_location.split(',')
        
        if len(candidate_parts) > 1 and len(job_parts) > 1:
            if candidate_parts[-1].strip() == job_parts[-1].strip():
                return 0.6  # Same country
        
        # Different location
        return 0.2
    
    def _generate_score_breakdown(self, candidate: Dict, job: Dict,
                                  semantic_score: float, skills_score: float,
                                  experience_score: float, location_score: float) -> Dict:
        """
        Generate detailed score breakdown for explainability
        
        Returns:
            Dictionary with detailed breakdown
        """
        # Identify matched and missing skills
        candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
        required_skills = set([s.lower() for s in job.get('required_skills', [])])
        
        matched_skills = list(candidate_skills & required_skills)
        missing_skills = list(required_skills - candidate_skills)
        
        # Experience analysis
        candidate_exp = candidate.get('years_experience', 0)
        required_min = job.get('years_experience_min', 0)
        required_max = job.get('years_experience_max', 100)
        
        if candidate_exp < required_min:
            exp_status = f"Under-qualified by {required_min - candidate_exp} years"
        elif candidate_exp > required_max:
            exp_status = f"Over-qualified by {candidate_exp - required_max} years"
        else:
            exp_status = "Perfect match"
        
        breakdown = {
            "semantic_similarity": {
                "score": semantic_score,
                "interpretation": self._interpret_semantic_score(semantic_score),
                "weight": WEIGHTS["semantic"]
            },
            "skills_match": {
                "score": skills_score,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "match_rate": f"{len(matched_skills)}/{len(required_skills)}" if required_skills else "N/A",
                "weight": WEIGHTS["skills"]
            },
            "experience_match": {
                "score": experience_score,
                "candidate_years": candidate_exp,
                "required_range": f"{required_min}-{required_max}",
                "status": exp_status,
                "weight": WEIGHTS["experience"]
            },
            "location_match": {
                "score": location_score,
                "candidate_location": candidate.get('location'),
                "job_location": job.get('location'),
                "weight": WEIGHTS["location"]
            }
        }
        
        return breakdown
    
    def _interpret_semantic_score(self, score: float) -> str:
        """Interpret semantic similarity score"""
        if score >= 0.85:
            return "Excellent semantic match"
        elif score >= 0.75:
            return "Strong semantic match"
        elif score >= 0.65:
            return "Good semantic match"
        elif score >= 0.55:
            return "Moderate semantic match"
        else:
            return "Weak semantic match"


def main():
    """Main execution function for testing"""
    print("="*60)
    print("MATCHING ENGINE TEST")
    print("="*60)
    
    # Load a sample job
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    test_job = jobs[0]  # First job as test
    
    # Initialize matching engine
    engine = MatchingEngine()
    
    # Find matches
    matches = engine.match_candidates(test_job, top_k=10)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"TOP 10 CANDIDATES FOR: {test_job['title']}")
    print(f"{'='*60}")
    
    for i, match in enumerate(matches, 1):
        candidate = match['candidate']
        scores = match['scores']
        
        print(f"\n{i}. {candidate['name']} ({candidate['id']})")
        print(f"   Title: {candidate['current_title']}")
        print(f"   Total Score: {scores['total']:.3f}")
        print(f"   - Semantic: {scores['semantic']:.3f} (weight: {WEIGHTS['semantic']})")
        print(f"   - Skills: {scores['skills']:.3f} (weight: {WEIGHTS['skills']})")
        print(f"   - Experience: {scores['experience']:.3f} (weight: {WEIGHTS['experience']})")
        print(f"   - Location: {scores['location']:.3f} (weight: {WEIGHTS['location']})")


if __name__ == "__main__":
    main()
