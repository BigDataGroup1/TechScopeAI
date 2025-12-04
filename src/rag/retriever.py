"""Document retriever for RAG system - supports both manual and QueryAgent modes."""

import logging
import os
from typing import List, Dict, Optional
from pathlib import Path

from .embedder import Embedder

# Try to import QueryAgent retriever
try:
    from .query_agent_retriever import QueryAgentRetriever
    QUERY_AGENT_AVAILABLE = True
except ImportError:
    QUERY_AGENT_AVAILABLE = False

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant documents using semantic search."""
    
    def __init__(self, vector_store=None, embedder=None, 
                 use_query_agent: bool = True,
                 collection_names: Optional[List[str]] = None):
        """
        Initialize retriever.
        
        Args:
            vector_store: Vector store instance (for manual mode)
            embedder: Embedder instance (for manual mode)
            use_query_agent: Whether to use QueryAgent (True) or manual search (False)
            collection_names: Collection names for QueryAgent (e.g., ["TechScopeAI_Pitch"])
        """
        self.use_query_agent = use_query_agent and QUERY_AGENT_AVAILABLE
        
        if self.use_query_agent:
            # Use QueryAgent (only works with Weaviate Cloud, not local instances)
            try:
                # Check if using local Weaviate (QueryAgent requires Weaviate Cloud)
                weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8081")
                is_local = "localhost" in weaviate_url or "127.0.0.1" in weaviate_url or not weaviate_url.startswith("https://")
                
                if is_local:
                    logger.warning("QueryAgent requires Weaviate Cloud. Local instance detected, using manual RAG instead.")
                    self.use_query_agent = False
                    if not vector_store or not embedder:
                        raise ValueError("QueryAgent not available for local Weaviate. Provide vector_store and embedder for manual RAG.")
                    self.vector_store = vector_store
                    self.embedder = embedder
                else:
                    # Try to initialize QueryAgent for Weaviate Cloud
                    self.query_agent_retriever = QueryAgentRetriever(
                        collection_names=collection_names or []
                    )
                    logger.info(f"✅ Using Weaviate QueryAgent for retrieval (collections: {collection_names or 'all'})")
            except Exception as e:
                logger.warning(f"Could not initialize QueryAgent: {e}, falling back to manual mode")
                self.use_query_agent = False
                if not vector_store or not embedder:
                    raise ValueError("QueryAgent failed and vector_store/embedder not provided")
                self.vector_store = vector_store
                self.embedder = embedder
        else:
            # Use manual RAG
            if not vector_store or not embedder:
                raise ValueError("vector_store and embedder required when not using QueryAgent")
            self.vector_store = vector_store
            self.embedder = embedder
            logger.info("Using manual RAG (embedding + vector search)")
    
    def retrieve(self, query: str, top_k: int = 5, category_filter: Optional[str] = None) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query (natural language for QueryAgent)
            top_k: Number of results to return
            category_filter: Optional category/collection to filter by
            
        Returns:
            List of relevant documents with metadata
        """
        if self.use_query_agent:
            # QueryAgent doesn't have separate retrieve method, use search
            result = self.query_agent_retriever.search(
                query=query,
                top_k=top_k,
                collection_filter=category_filter
            )
            return result.get('documents', [])
        else:
            # Manual mode
            query_embedding = self.embedder.embed(query)
            results = self.vector_store.search(query_embedding, top_k=top_k * 2)
            
            if category_filter:
                results = [r for r in results if r.get('category') == category_filter]
            
            return results[:top_k]
    
    def retrieve_with_context(self, query: str, top_k: int = 5, 
                             min_similarity: float = 0.5,
                             category_filter: Optional[str] = None) -> Dict:
        """
        Retrieve documents with formatted context.
        
        Args:
            query: Search query (natural language for QueryAgent)
            top_k: Number of results
            min_similarity: Minimum similarity score threshold (ignored for QueryAgent)
            category_filter: Optional category/collection filter
            
        Returns:
            Dictionary with retrieved documents and formatted context
        """
        if self.use_query_agent:
            # Use QueryAgent search mode
            return self.query_agent_retriever.search(
                query=query,
                top_k=top_k,
                collection_filter=category_filter
            )
        else:
            # Manual RAG (existing code)
            results = self.retrieve(query, top_k=top_k, category_filter=category_filter)
            
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

