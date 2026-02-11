"""
FAISS Indexer - Efficient similarity search using Facebook AI Similarity Search
"""

import numpy as np
import faiss
import json
from pathlib import Path
from typing import List, Tuple
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *


class FAISSIndexer:
    """Manage FAISS index for efficient similarity search"""
    
    def __init__(self):
        """Initialize FAISS indexer"""
        self.index = None
        self.ids = None
        self.dimension = EMBEDDING_DIMENSION
    
    def build_index(self, embeddings: np.ndarray, ids: List[str], 
                   index_type: str = FAISS_INDEX_TYPE) -> faiss.Index:
        """
        Build FAISS index from embeddings
        
        Args:
            embeddings: numpy array of shape (n_samples, dimension)
            ids: list of IDs corresponding to embeddings
            index_type: type of FAISS index to build
            
        Returns:
            FAISS index
        """
        print(f"\n{'='*60}")
        print(f"Building FAISS index...")
        print(f"{'='*60}")
        print(f"Index type: {index_type}")
        print(f"Number of vectors: {len(embeddings)}")
        print(f"Dimension: {embeddings.shape[1]}")
        
        # Ensure embeddings are float32 and C-contiguous
        embeddings = np.ascontiguousarray(embeddings.astype('float32'))
        
        # Store IDs
        self.ids = ids
        
        if index_type == "Flat":
            # Exact search (baseline)
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (for normalized vectors = cosine)
            self.index.add(embeddings)
            print(f"✅ Built Flat index (exact search)")
        
        elif index_type == "IVFFlat":
            # Inverted file index with flat quantizer
            nlist = min(FAISS_NLIST, len(embeddings) // 39)  # Rule of thumb: n/39
            
            if nlist < 2:
                print(f"⚠️  Too few vectors for IVF, using Flat index instead")
                self.index = faiss.IndexFlatIP(self.dimension)
                self.index.add(embeddings)
            else:
                quantizer = faiss.IndexFlatIP(self.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist, faiss.METRIC_INNER_PRODUCT)
                
                # Train the index
                print(f"Training IVF index with {nlist} clusters...")
                self.index.train(embeddings)
                
                # Add vectors
                self.index.add(embeddings)
                
                # Set search parameters
                self.index.nprobe = FAISS_NPROBE
                
                print(f"✅ Built IVF index with {nlist} clusters, nprobe={FAISS_NPROBE}")
        
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        print(f"Total vectors in index: {self.index.ntotal}")
        
        return self.index
    
    def search(self, query_embeddings: np.ndarray, k: int = TOP_K_FAISS) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for k nearest neighbors
        
        Args:
            query_embeddings: numpy array of shape (n_queries, dimension)
            k: number of neighbors to return
            
        Returns:
            Tuple of (distances, indices)
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Ensure query is float32 and C-contiguous
        query_embeddings = np.ascontiguousarray(query_embeddings.astype('float32'))
        
        # Ensure k doesn't exceed total vectors
        k = min(k, self.index.ntotal)
        
        # Search
        distances, indices = self.index.search(query_embeddings, k)
        
        return distances, indices
    
    def get_ids_from_indices(self, indices: np.ndarray) -> List[List[str]]:
        """
        Convert FAISS indices to IDs
        
        Args:
            indices: numpy array of shape (n_queries, k)
            
        Returns:
            List of lists of IDs
        """
        result = []
        for query_indices in indices:
            query_ids = [self.ids[idx] for idx in query_indices if idx != -1]
            result.append(query_ids)
        
        return result
    
    def save_index(self, filepath: Path):
        """
        Save FAISS index to disk
        
        Args:
            filepath: path to save index
        """
        if self.index is None:
            raise ValueError("No index to save")
        
        faiss.write_index(self.index, str(filepath))
        print(f"✅ Saved FAISS index to {filepath}")
    
    def load_index(self, filepath: Path, ids: List[str]):
        """
        Load FAISS index from disk
        
        Args:
            filepath: path to index file
            ids: list of IDs corresponding to index
        """
        self.index = faiss.read_index(str(filepath))
        self.ids = ids
        print(f"✅ Loaded FAISS index from {filepath}")
        print(f"Total vectors: {self.index.ntotal}")


def main():
    """Main execution function"""
    print("="*60)
    print("FAISS INDEX CONSTRUCTION")
    print("="*60)
    
    # Load embeddings
    print("\nLoading candidate embeddings...")
    cv_embeddings = np.load(CV_EMBEDDINGS_FILE)
    
    with open(CV_IDS_FILE, 'r') as f:
        cv_ids = json.load(f)
    
    print(f"Loaded {len(cv_embeddings)} embeddings")
    
    # Build index
    indexer = FAISSIndexer()
    indexer.build_index(cv_embeddings, cv_ids, index_type=FAISS_INDEX_TYPE)
    
    # Save index
    print(f"\nSaving index...")
    indexer.save_index(FAISS_INDEX_FILE)
    
    # Test search
    print(f"\n{'='*60}")
    print("Testing index with sample query...")
    print(f"{'='*60}")
    
    # Use first embedding as test query
    test_query = cv_embeddings[0:1]
    distances, indices = indexer.search(test_query, k=5)
    result_ids = indexer.get_ids_from_indices(indices)
    
    print(f"Query: {cv_ids[0]}")
    print(f"Top 5 results:")
    for i, (id_, dist) in enumerate(zip(result_ids[0], distances[0])):
        print(f"  {i+1}. {id_} (score: {dist:.4f})")
    
    print("\n" + "="*60)
    print("✅ FAISS INDEX READY")
    print("="*60)


if __name__ == "__main__":
    main()
