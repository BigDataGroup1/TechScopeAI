"""
Retriever compatibility layer for agents.

This module provides a Retriever class that wraps RAGRetriever and provides
the interface expected by agents. RAG uses PostgreSQL, but agents can use
Weaviate for personalization (separate from RAG).
"""

import logging
from typing import Dict, List, Optional, Any
from .retrieval import RAGRetriever
from .vector_store import VectorStore
from .collections import AgentType

logger = logging.getLogger(__name__)


class Retriever:
    """
    Compatibility wrapper for RAGRetriever.
    
    Provides the interface expected by agents while using PostgreSQL for RAG.
    Agents can use Weaviate PersonalizationAgent separately for personalization.
    """
    
    def __init__(self, vector_store: VectorStore, embedder=None, **kwargs):
        """
        Initialize Retriever.
        
        Args:
            vector_store: VectorStore instance (PostgreSQL-based)
            embedder: Optional embedder (not used, kept for compatibility)
            **kwargs: Additional arguments (ignored, kept for compatibility)
        """
        self.vector_store = vector_store
        self.rag_retriever = RAGRetriever(vector_store)
        # Store embedder for compatibility (not used for RAG, but agents may expect it)
        self.embedder = embedder
        
        # Compatibility attributes that agents might check
        self.query_agent_retriever = None  # Not used with PostgreSQL RAG
        
        logger.debug("Retriever initialized (PostgreSQL-based RAG)")
    
    def retrieve_with_context(
        self, 
        query: str, 
        top_k: int = 3,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve context with sources (compatibility method for agents).
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            category_filter: Optional category filter (e.g., "competitive", "pitch")
        
        Returns:
            Dictionary with:
            {
                "context": str,  # Combined text from retrieved documents
                "sources": List[Dict],  # List of source documents with metadata
                "count": int  # Number of documents retrieved
            }
        """
        # Map category filter to AgentType if provided
        agent_type = None
        if category_filter:
            category_map = {
                "competitive": AgentType.COMPETITIVE,
                "pitch": AgentType.PITCH,
                "marketing": AgentType.MARKETING,
                "ip_legal": AgentType.IP_LEGAL,
                "patent": AgentType.IP_LEGAL,
                "policy": AgentType.POLICY,
                "team": AgentType.TEAM,
            }
            agent_type = category_map.get(category_filter.lower())
        
        # If no agent_type determined, try to infer from query or use default
        if agent_type is None:
            # Default to competitive for backward compatibility
            agent_type = AgentType.COMPETITIVE
        
        # Retrieve documents using RAGRetriever
        retrieved_docs = self.rag_retriever.retrieve(
            agent_type=agent_type,
            query=query,
            top_k=top_k
        )
        
        # Format response for agents
        context_parts = []
        sources = []
        
        for doc in retrieved_docs:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            distance = doc.get("distance", 0.0)
            doc_id = doc.get("id", "")
            
            context_parts.append(text)
            
            sources.append({
                "source": metadata.get("source", "RAG Database"),
                "title": metadata.get("title", ""),
                "text": text[:200] + "..." if len(text) > 200 else text,
                "similarity": 1.0 - distance,  # Convert distance to similarity
                "metadata": metadata,
                "id": doc_id
            })
        
        context = "\n\n".join(context_parts)
        
        return {
            "context": context,
            "sources": sources,
            "count": len(retrieved_docs)
        }
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Simple retrieve method (compatibility).
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            List of retrieved documents
        """
        return self.rag_retriever.retrieve(
            agent_type=AgentType.COMPETITIVE,  # Default
            query=query,
            top_k=top_k
        )


