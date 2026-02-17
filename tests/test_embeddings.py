"""
Embedding Quality Tests
Validates semantic embeddings quality, normalization, and clustering
"""

import sys
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_utils import TestLogger, TestAssertion, TestRunner, load_test_data, calculate_statistics
from config import CV_EMBEDDINGS_FILE, JOB_EMBEDDINGS_FILE, CV_IDS_FILE, JOB_IDS_FILE, EMBEDDING_DIMENSION
import json


class EmbeddingQualityTests:
    """Test embedding quality and properties"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.runner = TestRunner(logger)
        self.cv_embeddings = None
        self.job_embeddings = None
        self.cv_ids = None
        self.job_ids = None
        self.candidates = None
        self.jobs = None
    
    def setup(self):
        """Load embeddings and metadata"""
        self.logger.section("LOADING EMBEDDINGS")
        
        # Load embeddings
        self.cv_embeddings = np.load(CV_EMBEDDINGS_FILE)
        self.job_embeddings = np.load(JOB_EMBEDDINGS_FILE)
        
        with open(CV_IDS_FILE, 'r') as f:
            self.cv_ids = json.load(f)
        
        with open(JOB_IDS_FILE, 'r') as f:
            self.job_ids = json.load(f)
        
        # Load metadata
        self.candidates, self.jobs, _ = load_test_data()
        self.candidates = {c['id']: c for c in self.candidates}
        self.jobs = {j['id']: j for j in self.jobs}
        
        self.logger.log(f"Candidate embeddings: {self.cv_embeddings.shape}")
        self.logger.log(f"Job embeddings: {self.job_embeddings.shape}")
    
    def test_embedding_dimensions(self):
        """Test embedding dimensions match expected"""
        TestAssertion.assert_equals(
            self.cv_embeddings.shape[1], 
            EMBEDDING_DIMENSION,
            "Candidate embedding dimension"
        )
        
        TestAssertion.assert_equals(
            self.job_embeddings.shape[1],
            EMBEDDING_DIMENSION,
            "Job embedding dimension"
        )
    
    def test_no_nan_or_inf(self):
        """Test embeddings contain no NaN or Inf values"""
        if np.isnan(self.cv_embeddings).any():
            raise AssertionError("Candidate embeddings contain NaN values")
        
        if np.isinf(self.cv_embeddings).any():
            raise AssertionError("Candidate embeddings contain Inf values")
        
        if np.isnan(self.job_embeddings).any():
            raise AssertionError("Job embeddings contain NaN values")
        
        if np.isinf(self.job_embeddings).any():
            raise AssertionError("Job embeddings contain Inf values")
    
    def test_embeddings_normalized(self):
        """Test embeddings are L2 normalized"""
        cv_norms = np.linalg.norm(self.cv_embeddings, axis=1)
        job_norms = np.linalg.norm(self.job_embeddings, axis=1)
        
        # Should be very close to 1.0
        if not np.allclose(cv_norms, 1.0, atol=0.01):
            raise AssertionError(
                f"Candidate embeddings not normalized: mean norm = {cv_norms.mean():.6f}"
            )
        
        if not np.allclose(job_norms, 1.0, atol=0.01):
            raise AssertionError(
                f"Job embeddings not normalized: mean norm = {job_norms.mean():.6f}"
            )
    
    def test_embedding_distribution(self):
        """Test embedding value distribution is reasonable"""
        cv_flat = self.cv_embeddings.flatten()
        job_flat = self.job_embeddings.flatten()
        
        # Mean should be close to 0 (centered)
        cv_mean = cv_flat.mean()
        job_mean = job_flat.mean()
        
        if abs(cv_mean) > 0.1:
            raise AssertionError(
                f"Candidate embeddings not centered: mean = {cv_mean:.6f}"
            )
        
        if abs(job_mean) > 0.1:
            raise AssertionError(
                f"Job embeddings not centered: mean = {job_mean:.6f}"
            )
        
        # Standard deviation should be reasonable
        cv_std = cv_flat.std()
        job_std = job_flat.std()
        
        # For normalized embeddings, std should be around 0.05-0.15
        if not (0.03 <= cv_std <= 0.2):
            raise AssertionError(
                f"Candidate embedding std out of range: {cv_std:.6f}"
            )
        
        if not (0.03 <= job_std <= 0.2):
            raise AssertionError(
                f"Job embedding std out of range: {job_std:.6f}"
            )
    
    def test_similarity_distribution(self):
        """Test pairwise similarity distribution"""
        # Sample for performance
        sample_size = min(200, len(self.cv_embeddings))
        indices = np.random.choice(len(self.cv_embeddings), sample_size, replace=False)
        sample = self.cv_embeddings[indices]
        
        # Compute pairwise similarities
        similarities = cosine_similarity(sample)
        
        # Remove diagonal
        mask = np.ones(similarities.shape, dtype=bool)
        np.fill_diagonal(mask, False)
        sims = similarities[mask]
        
        # Calculate stats
        stats = calculate_statistics(sims.tolist())
        
        self.logger.log(f"Similarity stats: mean={stats['mean']:.4f}, std={stats['std']:.4f}")
        
        # Mean similarity should be in reasonable range (0.4-0.7)
        if not (0.3 <= stats['mean'] <= 0.8):
            raise AssertionError(
                f"Similarity mean out of range: {stats['mean']:.4f}"
            )
        
        # Should have diversity (std > 0.05)
        if stats['std'] < 0.05:
            raise AssertionError(
                f"Similarities lack diversity: std = {stats['std']:.4f}"
            )
    
    def test_semantic_clustering(self):
        """Test embeddings cluster by semantic categories"""
        # Group by service line
        service_line_embeddings = {}
        
        for idx, cv_id in enumerate(self.cv_ids):
            candidate = self.candidates[cv_id]
            sl = candidate['service_line']
            
            if sl not in service_line_embeddings:
                service_line_embeddings[sl] = []
            
            service_line_embeddings[sl].append(self.cv_embeddings[idx])
        
        # Calculate intra vs inter cluster similarity
        intra_sims = []
        inter_sims = []
        
        service_lines = list(service_line_embeddings.keys())
        
        for i, sl1 in enumerate(service_lines):
            embeddings1 = np.array(service_line_embeddings[sl1])
            
            # Intra-cluster
            if len(embeddings1) > 1:
                intra_sim = cosine_similarity(embeddings1)
                mask = np.ones(intra_sim.shape, dtype=bool)
                np.fill_diagonal(mask, False)
                intra_sims.extend(intra_sim[mask].tolist())
            
            # Inter-cluster
            for j, sl2 in enumerate(service_lines):
                if i >= j:
                    continue
                
                embeddings2 = np.array(service_line_embeddings[sl2])
                inter_sim = cosine_similarity(embeddings1, embeddings2)
                inter_sims.extend(inter_sim.flatten().tolist())
        
        intra_mean = np.mean(intra_sims)
        inter_mean = np.mean(inter_sims)
        separation = intra_mean / inter_mean if inter_mean > 0 else 0
        
        self.logger.log(f"Intra-cluster similarity: {intra_mean:.4f}")
        self.logger.log(f"Inter-cluster similarity: {inter_mean:.4f}")
        self.logger.log(f"Separation ratio: {separation:.4f}")
        
        # Intra should be higher than inter
        if intra_mean <= inter_mean:
            raise AssertionError(
                f"Poor clustering: intra ({intra_mean:.4f}) <= inter ({inter_mean:.4f})"
            )
    
    def test_cross_domain_matching(self):
        """Test job-candidate matching quality"""
        # Sample jobs
        sample_jobs = min(10, len(self.job_embeddings))
        match_quality_scores = []
        
        for job_idx in range(sample_jobs):
            job_id = self.job_ids[job_idx]
            job = self.jobs[job_id]
            job_emb = self.job_embeddings[job_idx].reshape(1, -1)
            
            # Get similarities
            sims = cosine_similarity(job_emb, self.cv_embeddings)[0]
            
            # Top 10 matches
            top_indices = np.argsort(sims)[::-1][:10]
            
            # Count same service line
            same_sl = 0
            for idx in top_indices:
                cv_id = self.cv_ids[idx]
                candidate = self.candidates[cv_id]
                if candidate['service_line'] == job['service_line']:
                    same_sl += 1
            
            match_quality = same_sl / 10
            match_quality_scores.append(match_quality)
        
        avg_quality = np.mean(match_quality_scores)
        
        self.logger.log(f"Average match quality: {avg_quality:.2%}")
        
        # Should have reasonable matching (>50%)
        if avg_quality < 0.5:
            raise AssertionError(
                f"Poor cross-domain matching: {avg_quality:.2%}"
            )
    
    def analyze_embedding_statistics(self):
        """Log detailed embedding statistics"""
        self.logger.subsection("EMBEDDING STATISTICS")
        
        # Value ranges
        cv_min, cv_max = self.cv_embeddings.min(), self.cv_embeddings.max()
        job_min, job_max = self.job_embeddings.min(), self.job_embeddings.max()
        
        self.logger.log(f"Candidate embedding range: [{cv_min:.6f}, {cv_max:.6f}]")
        self.logger.log(f"Job embedding range: [{job_min:.6f}, {job_max:.6f}]")
        
        # Memory usage
        cv_memory = self.cv_embeddings.nbytes / 1024 / 1024
        job_memory = self.job_embeddings.nbytes / 1024 / 1024
        
        self.logger.log(f"Candidate embeddings memory: {cv_memory:.2f} MB")
        self.logger.log(f"Job embeddings memory: {job_memory:.2f} MB")
        self.logger.log(f"Total memory: {cv_memory + job_memory:.2f} MB")
    
    def run_all(self):
        """Execute all embedding quality tests"""
        self.setup()
        
        self.logger.section("EMBEDDING PROPERTY TESTS")
        self.runner.run_test("Correct Dimensions", self.test_embedding_dimensions)
        self.runner.run_test("No NaN or Inf Values", self.test_no_nan_or_inf)
        self.runner.run_test("Embeddings Normalized", self.test_embeddings_normalized)
        self.runner.run_test("Value Distribution", self.test_embedding_distribution)
        
        self.logger.section("EMBEDDING QUALITY TESTS")
        self.runner.run_test("Similarity Distribution", self.test_similarity_distribution)
        self.runner.run_test("Semantic Clustering", self.test_semantic_clustering)
        self.runner.run_test("Cross-Domain Matching", self.test_cross_domain_matching)
        
        self.analyze_embedding_statistics()
        
        return self.runner.get_summary()


def main():
    """Execute embedding quality tests"""
    logger = TestLogger("logs/test_embeddings.txt", "Embedding Quality Tests")
    
    tests = EmbeddingQualityTests(logger)
    summary = tests.run_all()
    
    logger.finalize(summary['passed'], summary['failed'])
    
    return summary['failed'] == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)