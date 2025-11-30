"""Document retriever for RAG system."""

import logging
from typing import List, Dict, Optional
from pathlib import Path

from .embedder import Embedder
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant documents using semantic search."""
    
    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        """
        Initialize retriever.
        
        Args:
            vector_store: Vector store instance
            embedder: Embedder instance
        """
        self.vector_store = vector_store
        self.embedder = embedder
    
    def retrieve(self, query: str, top_k: int = 5, category_filter: Optional[str] = None) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            category_filter: Optional category to filter by
            
        Returns:
            List of relevant documents with metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.embed(query)
        
        # Search in vector store
        results = self.vector_store.search(query_embedding, top_k=top_k * 2)  # Get more, then filter
        
        # Filter by category if specified
        if category_filter:
            results = [r for r in results if r.get('category') == category_filter]
        
        # Return top_k
        return results[:top_k]
    
    def retrieve_with_context(self, query: str, top_k: int = 5, 
                             min_similarity: float = 0.5) -> Dict:
        """
        Retrieve documents with formatted context.
        
        Args:
            query: Search query
            top_k: Number of results
            min_similarity: Minimum similarity score threshold
            
        Returns:
            Dictionary with retrieved documents and formatted context
        """
        results = self.retrieve(query, top_k=top_k)
        
        # Filter by similarity
        filtered_results = [r for r in results if r.get('similarity_score', 0) >= min_similarity]
        
        # Format context
        context_parts = []
        sources = []
        
        for i, result in enumerate(filtered_results, 1):
            content = result.get('content', result.get('text', ''))
            source = result.get('source', 'Unknown')
            category = result.get('category', '')
            similarity = result.get('similarity_score', 0)
            
            context_parts.append(f"[{i}] {content}")
            sources.append({
                'source': source,
                'category': category,
                'similarity': similarity
            })
        
        context = "\n\n".join(context_parts)
        
        return {
            'context': context,
            'documents': filtered_results,
            'sources': sources,
            'count': len(filtered_results)
        }

