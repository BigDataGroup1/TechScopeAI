"""Vector store for storing and searching embeddings."""

import logging
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for semantic search."""
    
    def __init__(self, category: str, store_path: Optional[str] = None, dimension: int = 384):
        """
        Initialize vector store.
        
        Args:
            category: Category name (e.g., "pitch", "competitive")
            store_path: Path to save/load vector store
            dimension: Dimension of embeddings (384 for MiniLM, 1536 for OpenAI)
        """
        if not FAISS_AVAILABLE:
            raise ImportError("faiss-cpu required. Install with: pip install faiss-cpu")
        
        self.category = category
        self.dimension = dimension
        self.store_path = Path(store_path) if store_path else Path(f"data/processed/{category}/vector_store")
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        # FAISS index
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance
        
        # Metadata storage
        self.metadata: List[Dict] = []
        self.metadata_path = self.store_path / "metadata.json"
        
        # Load if exists
        self.load()
    
    def add(self, embeddings: np.ndarray, metadata: List[Dict]):
        """
        Add embeddings and metadata to the store.
        
        Args:
            embeddings: Array of embedding vectors (n x dimension)
            metadata: List of metadata dicts (one per embedding)
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Add metadata
        self.metadata.extend(metadata)
        
        logger.info(f"Added {len(embeddings)} vectors to {self.category} store")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of metadata dicts with similarity scores
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Ensure query is float32 and reshape
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Build results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                result['distance'] = float(distance)
                results.append(result)
        
        return results
    
    def save(self):
        """Save vector store to disk."""
        # Save FAISS index
        index_path = self.store_path / "index.faiss"
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved vector store to {self.store_path}")
    
    def load(self):
        """Load vector store from disk."""
        index_path = self.store_path / "index.faiss"
        
        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
            
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            
            logger.info(f"Loaded vector store: {self.index.ntotal} vectors, {len(self.metadata)} metadata entries")
        else:
            logger.info(f"Creating new vector store for {self.category}")
    
    def get_count(self) -> int:
        """Get number of vectors in store."""
        return self.index.ntotal

