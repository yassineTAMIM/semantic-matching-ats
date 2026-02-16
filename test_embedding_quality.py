"""
Embedding Quality Assessment Suite
Evaluates semantic embeddings quality, distribution, and clustering properties
Logs all results to local .txt file
"""

import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt

sys.path.append(str(Path(__file__).parent))
from config import *

class TestLogger:
    """Custom logger for embedding tests"""
    
    def __init__(self, log_file: str = "logs/embedding_quality_test.txt"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"EMBEDDING QUALITY ASSESSMENT LOG\n")
            f.write(f"{'='*80}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"[{level}] {message}")
    
    def section(self, title: str):
        separator = "=" * 80
        self.log(f"\n{separator}")
        self.log(title)
        self.log(separator)


class EmbeddingQualityAssessor:
    """Comprehensive embedding quality assessment"""
    
    def __init__(self, logger: TestLogger):
        self.logger = logger
        self.cv_embeddings = None
        self.cv_ids = None
        self.job_embeddings = None
        self.job_ids = None
        self.candidates = None
        self.jobs = None
        self.results = {}
    
    def load_data(self):
        """Load embeddings and metadata"""
        self.logger.section("LOADING EMBEDDINGS AND METADATA")
        
        try:
            # Load candidate embeddings
            self.cv_embeddings = np.load(CV_EMBEDDINGS_FILE)
            with open(CV_IDS_FILE, 'r') as f:
                self.cv_ids = json.load(f)
            
            self.logger.log(
                f"Loaded {len(self.cv_embeddings)} candidate embeddings "
                f"({self.cv_embeddings.shape[1]} dims)",
                "SUCCESS"
            )
            
            # Load job embeddings
            self.job_embeddings = np.load(JOB_EMBEDDINGS_FILE)
            with open(JOB_IDS_FILE, 'r') as f:
                self.job_ids = json.load(f)
            
            self.logger.log(
                f"Loaded {len(self.job_embeddings)} job embeddings "
                f"({self.job_embeddings.shape[1]} dims)",
                "SUCCESS"
            )
            
            # Load metadata
            with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
                self.candidates = {c['id']: c for c in json.load(f)}
            
            with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
                self.jobs = {j['id']: j for j in json.load(f)}
            
            self.logger.log("Loaded candidate and job metadata", "SUCCESS")
            
        except Exception as e:
            self.logger.log(f"Failed to load data: {e}", "ERROR")
            raise
    
    def validate_embedding_properties(self):
        """Validate basic embedding properties"""
        self.logger.section("VALIDATING EMBEDDING PROPERTIES")
        
        # Check dimensions
        expected_dim = EMBEDDING_DIMENSION
        cv_dim = self.cv_embeddings.shape[1]
        job_dim = self.job_embeddings.shape[1]
        
        if cv_dim != expected_dim:
            self.logger.log(
                f"Candidate embedding dimension mismatch: {cv_dim} vs {expected_dim}",
                "ERROR"
            )
        else:
            self.logger.log(f"Candidate embedding dimension: {cv_dim} ✓", "SUCCESS")
        
        if job_dim != expected_dim:
            self.logger.log(
                f"Job embedding dimension mismatch: {job_dim} vs {expected_dim}",
                "ERROR"
            )
        else:
            self.logger.log(f"Job embedding dimension: {job_dim} ✓", "SUCCESS")
        
        # Check for NaN or Inf values
        cv_nan = np.isnan(self.cv_embeddings).any()
        cv_inf = np.isinf(self.cv_embeddings).any()
        job_nan = np.isnan(self.job_embeddings).any()
        job_inf = np.isinf(self.job_embeddings).any()
        
        if cv_nan or cv_inf:
            self.logger.log("Candidate embeddings contain NaN or Inf values", "ERROR")
        else:
            self.logger.log("Candidate embeddings: No NaN/Inf values ✓", "SUCCESS")
        
        if job_nan or job_inf:
            self.logger.log("Job embeddings contain NaN or Inf values", "ERROR")
        else:
            self.logger.log("Job embeddings: No NaN/Inf values ✓", "SUCCESS")
        
        # Check normalization (L2 norm should be ~1 for normalized embeddings)
        cv_norms = np.linalg.norm(self.cv_embeddings, axis=1)
        job_norms = np.linalg.norm(self.job_embeddings, axis=1)
        
        cv_normalized = np.allclose(cv_norms, 1.0, atol=0.01)
        job_normalized = np.allclose(job_norms, 1.0, atol=0.01)
        
        self.logger.log(f"\nCandidate embedding norms:")
        self.logger.log(f"  Mean: {cv_norms.mean():.6f}")
        self.logger.log(f"  Std: {cv_norms.std():.6f}")
        self.logger.log(f"  Min: {cv_norms.min():.6f}")
        self.logger.log(f"  Max: {cv_norms.max():.6f}")
        
        if cv_normalized:
            self.logger.log("  Status: Normalized ✓", "SUCCESS")
        else:
            self.logger.log("  Status: Not normalized", "WARN")
        
        self.logger.log(f"\nJob embedding norms:")
        self.logger.log(f"  Mean: {job_norms.mean():.6f}")
        self.logger.log(f"  Std: {job_norms.std():.6f}")
        self.logger.log(f"  Min: {job_norms.min():.6f}")
        self.logger.log(f"  Max: {job_norms.max():.6f}")
        
        if job_normalized:
            self.logger.log("  Status: Normalized ✓", "SUCCESS")
        else:
            self.logger.log("  Status: Not normalized", "WARN")
    
    def analyze_embedding_distributions(self):
        """Analyze embedding value distributions"""
        self.logger.section("ANALYZING EMBEDDING DISTRIBUTIONS")
        
        # Flatten all embeddings
        cv_flat = self.cv_embeddings.flatten()
        job_flat = self.job_embeddings.flatten()
        
        self.logger.log("\nCandidate Embedding Statistics:")
        self.logger.log(f"  Mean: {cv_flat.mean():.6f}")
        self.logger.log(f"  Std: {cv_flat.std():.6f}")
        self.logger.log(f"  Min: {cv_flat.min():.6f}")
        self.logger.log(f"  Max: {cv_flat.max():.6f}")
        self.logger.log(f"  Median: {np.median(cv_flat):.6f}")
        
        self.logger.log("\nJob Embedding Statistics:")
        self.logger.log(f"  Mean: {job_flat.mean():.6f}")
        self.logger.log(f"  Std: {job_flat.std():.6f}")
        self.logger.log(f"  Min: {job_flat.min():.6f}")
        self.logger.log(f"  Max: {job_flat.max():.6f}")
        self.logger.log(f"  Median: {np.median(job_flat):.6f}")
        
        # Check for reasonable distribution (should be roughly centered around 0)
        if abs(cv_flat.mean()) > 0.1:
            self.logger.log(
                f"Candidate embeddings may not be centered (mean={cv_flat.mean():.4f})",
                "WARN"
            )
        
        if abs(job_flat.mean()) > 0.1:
            self.logger.log(
                f"Job embeddings may not be centered (mean={job_flat.mean():.4f})",
                "WARN"
            )
    
    def analyze_similarity_distributions(self):
        """Analyze pairwise similarity distributions"""
        self.logger.section("ANALYZING SIMILARITY DISTRIBUTIONS")
        
        # Sample for performance (full pairwise is expensive)
        sample_size = min(200, len(self.cv_embeddings))
        sample_indices = np.random.choice(len(self.cv_embeddings), sample_size, replace=False)
        sample_embeddings = self.cv_embeddings[sample_indices]
        
        self.logger.log(f"Computing pairwise similarities for {sample_size} samples...")
        
        # Compute pairwise similarities
        similarities = cosine_similarity(sample_embeddings)
        
        # Remove diagonal (self-similarities)
        mask = np.ones(similarities.shape, dtype=bool)
        np.fill_diagonal(mask, False)
        similarities_no_diag = similarities[mask]
        
        self.logger.log("\nPairwise Similarity Statistics:")
        self.logger.log(f"  Mean: {similarities_no_diag.mean():.4f}")
        self.logger.log(f"  Std: {similarities_no_diag.std():.4f}")
        self.logger.log(f"  Min: {similarities_no_diag.min():.4f}")
        self.logger.log(f"  Max: {similarities_no_diag.max():.4f}")
        self.logger.log(f"  Median: {np.median(similarities_no_diag):.4f}")
        
        # Percentiles
        p25 = np.percentile(similarities_no_diag, 25)
        p75 = np.percentile(similarities_no_diag, 75)
        p90 = np.percentile(similarities_no_diag, 90)
        
        self.logger.log(f"  25th percentile: {p25:.4f}")
        self.logger.log(f"  75th percentile: {p75:.4f}")
        self.logger.log(f"  90th percentile: {p90:.4f}")
        
        # Quality checks
        if similarities_no_diag.mean() > 0.9:
            self.logger.log(
                "WARNING: Very high average similarity - embeddings may lack discrimination",
                "WARN"
            )
        elif similarities_no_diag.mean() < 0.3:
            self.logger.log(
                "WARNING: Very low average similarity - embeddings may be too dispersed",
                "WARN"
            )
        else:
            self.logger.log("Similarity distribution looks healthy", "SUCCESS")
        
        # Check for duplicate embeddings
        high_sim_pairs = np.sum(similarities_no_diag > 0.99)
        if high_sim_pairs > 0:
            self.logger.log(
                f"Found {high_sim_pairs} pairs with >99% similarity (potential duplicates)",
                "WARN"
            )
        
        self.results['similarity_stats'] = {
            'mean': float(similarities_no_diag.mean()),
            'std': float(similarities_no_diag.std()),
            'min': float(similarities_no_diag.min()),
            'max': float(similarities_no_diag.max())
        }
    
    def test_semantic_clustering(self):
        """Test if embeddings cluster by semantic categories"""
        self.logger.section("TESTING SEMANTIC CLUSTERING")
        
        # Group candidates by service line
        service_line_embeddings = {}
        
        for idx, cv_id in enumerate(self.cv_ids):
            candidate = self.candidates[cv_id]
            service_line = candidate['service_line']
            
            if service_line not in service_line_embeddings:
                service_line_embeddings[service_line] = []
            
            service_line_embeddings[service_line].append(self.cv_embeddings[idx])
        
        self.logger.log(f"Analyzing clustering for {len(service_line_embeddings)} service lines...")
        
        # Calculate intra-cluster vs inter-cluster similarities
        intra_similarities = []
        inter_similarities = []
        
        service_lines = list(service_line_embeddings.keys())
        
        for i, sl1 in enumerate(service_lines):
            embeddings1 = np.array(service_line_embeddings[sl1])
            
            # Intra-cluster similarities
            if len(embeddings1) > 1:
                intra_sim = cosine_similarity(embeddings1)
                mask = np.ones(intra_sim.shape, dtype=bool)
                np.fill_diagonal(mask, False)
                intra_similarities.extend(intra_sim[mask].tolist())
            
            # Inter-cluster similarities
            for j, sl2 in enumerate(service_lines):
                if i >= j:  # Only compute once per pair
                    continue
                
                embeddings2 = np.array(service_line_embeddings[sl2])
                inter_sim = cosine_similarity(embeddings1, embeddings2)
                inter_similarities.extend(inter_sim.flatten().tolist())
        
        intra_mean = np.mean(intra_similarities) if intra_similarities else 0
        inter_mean = np.mean(inter_similarities) if inter_similarities else 0
        
        self.logger.log("\nClustering Quality:")
        self.logger.log(f"  Intra-cluster similarity (same service line): {intra_mean:.4f}")
        self.logger.log(f"  Inter-cluster similarity (different service lines): {inter_mean:.4f}")
        self.logger.log(f"  Separation ratio: {intra_mean / inter_mean if inter_mean > 0 else 0:.4f}")
        
        if intra_mean > inter_mean:
            self.logger.log(
                "✓ Embeddings show good semantic clustering (intra > inter)",
                "SUCCESS"
            )
        else:
            self.logger.log(
                "⚠ Weak semantic clustering (intra ≤ inter)",
                "WARN"
            )
        
        self.results['clustering'] = {
            'intra_similarity': float(intra_mean),
            'inter_similarity': float(inter_mean),
            'separation_ratio': float(intra_mean / inter_mean) if inter_mean > 0 else 0
        }
    
    def test_cross_domain_matching(self):
        """Test candidate-job matching quality"""
        self.logger.section("TESTING CROSS-DOMAIN MATCHING")
        
        # Sample jobs and compute their similarities with candidates
        sample_jobs = min(10, len(self.job_embeddings))
        
        self.logger.log(f"Testing matching quality for {sample_jobs} sample jobs...")
        
        match_quality_scores = []
        
        for job_idx in range(sample_jobs):
            job_id = self.job_ids[job_idx]
            job = self.jobs[job_id]
            job_embedding = self.job_embeddings[job_idx].reshape(1, -1)
            
            # Compute similarities with all candidates
            similarities = cosine_similarity(job_embedding, self.cv_embeddings)[0]
            
            # Get top 10 matches
            top_indices = np.argsort(similarities)[::-1][:10]
            top_scores = similarities[top_indices]
            
            # Check if top matches have same service line
            same_service_line_count = 0
            for idx in top_indices:
                cv_id = self.cv_ids[idx]
                candidate = self.candidates[cv_id]
                if candidate['service_line'] == job['service_line']:
                    same_service_line_count += 1
            
            match_quality = same_service_line_count / 10
            match_quality_scores.append(match_quality)
            
            self.logger.log(
                f"  Job {job_id} ({job['service_line']}): "
                f"{same_service_line_count}/10 top matches same service line "
                f"(avg score: {top_scores.mean():.4f})"
            )
        
        avg_match_quality = np.mean(match_quality_scores)
        
        self.logger.log(f"\nAverage Match Quality: {avg_match_quality:.2%}")
        
        if avg_match_quality >= 0.7:
            self.logger.log("✓ Excellent matching quality", "SUCCESS")
        elif avg_match_quality >= 0.5:
            self.logger.log("Good matching quality", "SUCCESS")
        elif avg_match_quality >= 0.3:
            self.logger.log("Fair matching quality", "WARN")
        else:
            self.logger.log("⚠ Poor matching quality", "WARN")
        
        self.results['match_quality'] = float(avg_match_quality)
    
    def visualize_embeddings(self):
        """Create PCA visualization of embeddings"""
        self.logger.section("GENERATING EMBEDDING VISUALIZATIONS")
        
        try:
            # Sample for visualization
            sample_size = min(500, len(self.cv_embeddings))
            sample_indices = np.random.choice(len(self.cv_embeddings), sample_size, replace=False)
            sample_embeddings = self.cv_embeddings[sample_indices]
            sample_ids = [self.cv_ids[i] for i in sample_indices]
            
            # Get service lines for coloring
            service_lines = [self.candidates[id_]['service_line'] for id_ in sample_ids]
            unique_service_lines = list(set(service_lines))
            color_map = {sl: i for i, sl in enumerate(unique_service_lines)}
            colors = [color_map[sl] for sl in service_lines]
            
            # PCA to 2D
            self.logger.log("Computing PCA projection to 2D...")
            pca = PCA(n_components=2)
            embeddings_2d = pca.fit_transform(sample_embeddings)
            
            # Create plot
            plt.figure(figsize=(12, 8))
            scatter = plt.scatter(
                embeddings_2d[:, 0],
                embeddings_2d[:, 1],
                c=colors,
                alpha=0.6,
                s=30
            )
            
            plt.title('Candidate Embeddings - PCA Projection', fontsize=14, fontweight='bold')
            plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', fontsize=12)
            plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)', fontsize=12)
            
            # Add legend
            plt.legend(
                handles=scatter.legend_elements()[0],
                labels=unique_service_lines[:10],  # First 10 to avoid clutter
                title="Service Line",
                loc='best',
                fontsize=8
            )
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save plot
            plot_path = Path("logs/embedding_pca_visualization.png")
            plot_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.logger.log(f"Saved PCA visualization to: {plot_path}", "SUCCESS")
            self.logger.log(
                f"Explained variance: PC1={pca.explained_variance_ratio_[0]:.2%}, "
                f"PC2={pca.explained_variance_ratio_[1]:.2%}, "
                f"Total={pca.explained_variance_ratio_[:2].sum():.2%}"
            )
            
        except Exception as e:
            self.logger.log(f"Failed to create visualization: {e}", "WARN")
    
    def generate_summary_report(self):
        """Generate final summary"""
        self.logger.section("EMBEDDING QUALITY SUMMARY")
        
        # Overall score based on collected metrics
        score_components = []
        
        # Similarity distribution score
        if 'similarity_stats' in self.results:
            sim_mean = self.results['similarity_stats']['mean']
            if 0.3 <= sim_mean <= 0.7:
                sim_score = 100
            elif 0.2 <= sim_mean < 0.3 or 0.7 < sim_mean <= 0.8:
                sim_score = 75
            elif 0.1 <= sim_mean < 0.2 or 0.8 < sim_mean <= 0.9:
                sim_score = 50
            else:
                sim_score = 25
            score_components.append(sim_score)
            self.logger.log(f"Similarity Distribution Score: {sim_score}/100")
        
        # Clustering score
        if 'clustering' in self.results:
            sep_ratio = self.results['clustering']['separation_ratio']
            if sep_ratio >= 1.2:
                cluster_score = 100
            elif sep_ratio >= 1.1:
                cluster_score = 75
            elif sep_ratio >= 1.0:
                cluster_score = 50
            else:
                cluster_score = 25
            score_components.append(cluster_score)
            self.logger.log(f"Semantic Clustering Score: {cluster_score}/100")
        
        # Match quality score
        if 'match_quality' in self.results:
            match_quality = self.results['match_quality']
            match_score = int(match_quality * 100)
            score_components.append(match_score)
            self.logger.log(f"Cross-Domain Matching Score: {match_score}/100")
        
        # Overall score
        if score_components:
            overall_score = sum(score_components) / len(score_components)
            self.logger.log(f"\n{'='*40}")
            self.logger.log(f"OVERALL EMBEDDING QUALITY SCORE: {overall_score:.1f}/100")
            self.logger.log(f"{'='*40}")
            
            if overall_score >= 80:
                verdict = "EXCELLENT"
                level = "SUCCESS"
            elif overall_score >= 60:
                verdict = "GOOD"
                level = "SUCCESS"
            elif overall_score >= 40:
                verdict = "FAIR"
                level = "WARN"
            else:
                verdict = "POOR"
                level = "WARN"
            
            self.logger.log(f"Verdict: {verdict}", level)
    
    def run_all_assessments(self):
        """Run all quality assessments"""
        self.load_data()
        self.validate_embedding_properties()
        self.analyze_embedding_distributions()
        self.analyze_similarity_distributions()
        self.test_semantic_clustering()
        self.test_cross_domain_matching()
        self.visualize_embeddings()
        self.generate_summary_report()
        
        self.logger.log(f"\n{'='*80}")
        self.logger.log(f"Embedding assessment complete. Log saved to: {self.logger.log_file}")
        self.logger.log(f"{'='*80}")


def main():
    """Main execution"""
    logger = TestLogger("logs/embedding_quality_test.txt")
    assessor = EmbeddingQualityAssessor(logger)
    assessor.run_all_assessments()
    
    print(f"\n✅ Assessment complete. Full log saved to: {logger.log_file.absolute()}")


if __name__ == "__main__":
    main()