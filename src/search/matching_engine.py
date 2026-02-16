"""
Matching Engine - Multi-criteria semantic matching
**NEW LOGIC**: Only matches candidates who APPLIED to the specific job (realistic ATS behavior)
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
    
    **REALISTIC ATS LOGIC**: Only ranks candidates who APPLIED to the job.
    This matches real-world recruiter workflow where you review actual applicants.
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
        
        # Load application history
        app_path = PROCESSED_DATA_DIR / "applications.json"
        try:
            with open(app_path, 'r', encoding='utf-8') as f:
                self.applications = json.load(f)
            print(f"✅ Loaded {len(self.applications)} application records")
        except FileNotFoundError:
            print("⚠️  No application history found. Creating empty list.")
            self.applications = []
        
        print(f"✅ Matching engine ready with {len(self.candidates_map)} candidates")
    
    def match_candidates(self, job: Dict, top_k: int = TOP_K_CANDIDATES, 
                        filters: Dict = None) -> List[Dict]:
        """
        Find and rank candidates who APPLIED to this specific job
        
        **NEW BEHAVIOR**: Only returns applicants, NOT entire database
        
        Args:
            job: Job dictionary
            top_k: Number of top candidates to return
            filters: Optional filters (location, experience, etc.)
            
        Returns:
            List of applicant matches with scores (sorted by total score)
        """
        print(f"\n{'='*60}")
        print(f"Matching applicants for: {job['title']}")
        print(f"{'='*60}")
        
        # ⭐ KEY CHANGE: Get only candidates who applied to THIS job
        applicant_ids = self._get_applicants_for_job(job['id'])
        
        if not applicant_ids:
            print("⚠️  No applicants for this position yet.")
            return []
        
        print(f"📋 {len(applicant_ids)} applicants found for this position")
        
        # Step 1: Generate job embedding
        job_text = self.embedding_engine.create_job_text(job)
        job_embedding = self.embedding_engine.model.encode(
            [job_text],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # Step 2: FAISS search in full database (to get semantic scores)
        print(f"Computing semantic similarity...")
        distances, indices = self.faiss_indexer.search(job_embedding, k=min(TOP_K_FAISS, len(self.candidates_map)))
        all_candidate_ids = self.faiss_indexer.get_ids_from_indices(indices)[0]
        semantic_scores_map = dict(zip(all_candidate_ids, distances[0]))
        
        # Step 3: Filter to ONLY applicants and get their scores
        applicants_with_scores = []
        for applicant_id in applicant_ids:
            if applicant_id not in self.candidates_map:
                continue
            
            candidate = self.candidates_map[applicant_id]
            
            # Get semantic score (if in FAISS results, else use minimum)
            semantic_score = semantic_scores_map.get(applicant_id, 0.3)
            
            # Apply additional filters if provided
            if filters and not self._passes_filters(candidate, filters):
                continue
            
            applicants_with_scores.append((candidate, semantic_score))
        
        print(f"After optional filters: {len(applicants_with_scores)} applicants")
        
        # Step 4: Multi-criteria scoring
        print("Computing multi-criteria scores...")
        scored_applicants = []
        
        for candidate, semantic_score in applicants_with_scores:
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
                    "semantic": semantic_score,
                    "skills": skills_score,
                    "experience": experience_score,
                    "location": location_score,
                    "total": total_score
                },
                "breakdown": {
                    "semantic_similarity": {
                        "score": semantic_score,
                        "interpretation": "Strong alignment" if semantic_score >= 0.75 else "Moderate alignment" if semantic_score >= 0.6 else "Limited alignment"
                    },
                    "skills_match": {
                        "matched_skills": self._get_matching_skills(candidate, job),
                        "missing_skills": self._get_missing_skills(candidate, job),
                        "score": skills_score
                    },
                    "experience_match": {
                        "candidate_years": candidate['years_experience'],
                        "required_range": f"{job['years_experience_min']}-{job['years_experience_max']}",
                        "score": experience_score,
                        "status": "Perfect fit" if experience_score >= 0.9 else "Good fit" if experience_score >= 0.7 else "Experience gap exists"
                    },
                    "location_match": {
                        "candidate_location": candidate['location'],
                        "job_location": job['location'],
                        "score": location_score
                    }
                }
            }
            
            scored_applicants.append(match_result)
        
        # Step 5: Sort by total score
        scored_applicants.sort(key=lambda x: x['scores']['total'], reverse=True)
        
        # Step 6: Return top_k
        final_results = scored_applicants[:top_k]
        
        print(f"✅ Returning top {len(final_results)} applicants")
        if final_results:
            print(f"   Best match: {final_results[0]['candidate']['name']} ({final_results[0]['scores']['total']:.1%})")
        
        return final_results
    
    def _get_applicants_for_job(self, job_id: str) -> List[str]:
        """
        Get list of candidate IDs who applied to this specific job
        
        Args:
            job_id: Job ID to search for
            
        Returns:
            List of candidate IDs who applied
        """
        applicant_ids = [
            app['candidate_id']
            for app in self.applications
            if app['job_id'] == job_id
        ]
        
        return applicant_ids
    
    def _passes_filters(self, candidate: Dict, filters: Dict) -> bool:
        """
        Check if candidate passes optional filters
        
        Args:
            candidate: Candidate dictionary
            filters: Filter criteria dictionary
            
        Returns:
            True if candidate passes all filters
        """
        if filters.get('min_experience'):
            if candidate['years_experience'] < filters['min_experience']:
                return False
        
        if filters.get('max_experience'):
            if candidate['years_experience'] > filters['max_experience']:
                return False
        
        if filters.get('location'):
            if candidate['location'] != filters['location']:
                return False
        
        if filters.get('service_line'):
            if candidate['service_line'] != filters['service_line']:
                return False
        
        if filters.get('required_skills'):
            candidate_skills = set(skill.lower() for skill in candidate['skills'])
            required_skills = set(skill.lower() for skill in filters['required_skills'])
            if not required_skills.issubset(candidate_skills):
                return False
        
        return True
    
    def _calculate_skills_score(self, candidate: Dict, job: Dict) -> float:
        """
        Calculate skills match score
        
        Args:
            candidate: Candidate dictionary
            job: Job dictionary
            
        Returns:
            Skills score (0.0 to 1.0)
        """
        candidate_skills = set(skill.lower() for skill in candidate['skills'])
        required_skills = set(skill.lower() for skill in job.get('required_skills', []))
        
        if not required_skills:
            return 0.8  # Default score if no required skills specified
        
        matching_skills = candidate_skills.intersection(required_skills)
        match_ratio = len(matching_skills) / len(required_skills)
        
        return match_ratio
    
    def _calculate_experience_score(self, candidate: Dict, job: Dict) -> float:
        """
        Calculate experience match score
        
        Args:
            candidate: Candidate dictionary
            job: Job dictionary
            
        Returns:
            Experience score (0.0 to 1.0)
        """
        candidate_exp = candidate['years_experience']
        job_min_exp = job['years_experience_min']
        job_max_exp = job['years_experience_max']
        
        # Perfect match
        if job_min_exp <= candidate_exp <= job_max_exp:
            return 1.0
        
        # Too junior
        if candidate_exp < job_min_exp:
            gap = job_min_exp - candidate_exp
            # Penalize based on gap (up to 50% penalty)
            penalty = min(gap * 0.15, 0.5)
            return max(0.5, 1.0 - penalty)
        
        # Too senior
        if candidate_exp > job_max_exp:
            excess = candidate_exp - job_max_exp
            # Smaller penalty for being over-qualified
            penalty = min(excess * 0.05, 0.3)
            return max(0.7, 1.0 - penalty)
        
        return 0.8
    
    def _calculate_location_score(self, candidate: Dict, job: Dict) -> float:
        """
        Calculate location match score
        
        Args:
            candidate: Candidate dictionary
            job: Job dictionary
            
        Returns:
            Location score (0.0 to 1.0)
        """
        # Exact match
        if candidate['location'] == job['location']:
            return 1.0
        
        # Remote jobs
        if job.get('remote') in [True, 'Hybrid']:
            return 0.9
        
        # Different location, no remote
        return 0.3
    
    def _get_matching_skills(self, candidate: Dict, job: Dict) -> List[str]:
        """Get list of matching skills between candidate and job"""
        candidate_skills = set(skill.lower() for skill in candidate['skills'])
        required_skills = set(skill.lower() for skill in job.get('required_skills', []))
        
        matching = candidate_skills.intersection(required_skills)
        return list(matching)
    
    def _get_missing_skills(self, candidate: Dict, job: Dict) -> List[str]:
        """Get list of skills candidate is missing for job"""
        candidate_skills = set(skill.lower() for skill in candidate['skills'])
        required_skills = set(skill.lower() for skill in job.get('required_skills', []))
        
        missing = required_skills - candidate_skills
        return list(missing)


def main():
    """Main execution function for testing"""
    print("="*60)
    print("MATCHING ENGINE TEST - APPLICANTS ONLY")
    print("="*60)
    
    # Load jobs
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Initialize engine
    engine = MatchingEngine()
    
    # Test with first job
    test_job = jobs[0]
    
    print(f"\n{'='*60}")
    print(f"TEST: Matching applicants for '{test_job['title']}'")
    print(f"{'='*60}")
    
    # Get matches
    matches = engine.match_candidates(test_job, top_k=10)
    
    if matches:
        print(f"\n{'='*60}")
        print(f"TOP {min(10, len(matches))} APPLICANTS:")
        print(f"{'='*60}")
        
        for i, match in enumerate(matches[:10], 1):
            candidate = match['candidate']
            scores = match['scores']
            
            print(f"\n{i}. {candidate['name']} - {candidate['current_title']}")
            print(f"   Overall Match: {scores['total']:.1%}")
            print(f"   Scores: Semantic={scores['semantic']:.2f} | Skills={scores['skills']:.2f} | "
                  f"Experience={scores['experience']:.2f} | Location={scores['location']:.2f}")
            print(f"   Experience: {candidate['years_experience']} years | Location: {candidate['location']}")
            print(f"   Matching Skills: {len(match['breakdown']['matching_skills'])}")
            print(f"   Missing Skills: {len(match['breakdown']['missing_skills'])}")
    else:
        print("\n⚠️  No applicants found for this position")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()