"""
Retriever compatibility layer for agents.

This module provides a Retriever class that wraps RAGRetriever and provides
the interface expected by agents. Supports both Weaviate QueryAgent (primary)
and PostgreSQL RAG (fallback).
"""

import logging
import os
from typing import Dict, List, Optional, Any
from .retrieval import RAGRetriever
from .vector_store import VectorStore
from .collections import AgentType, get_collection_name

logger = logging.getLogger(__name__)

# Try to import QueryAgent from weaviate-agents
try:
    from weaviate_agents.query import QueryAgent
    import weaviate
    QUERY_AGENT_AVAILABLE = True
except ImportError:
    QUERY_AGENT_AVAILABLE = False
    QueryAgent = None
    weaviate = None


class Retriever:
    """
    Compatibility wrapper for RAGRetriever.
    
    Supports both Weaviate QueryAgent (primary) and PostgreSQL RAG (fallback).
    Automatically uses QueryAgent if available and configured, otherwise falls back to PostgreSQL.
    """
    
    def __init__(self, vector_store: VectorStore, embedder=None, **kwargs):
        """
        Initialize Retriever.
        
        Args:
            vector_store: VectorStore instance (PostgreSQL-based, used as fallback)
            embedder: Optional embedder (not used, kept for compatibility)
            **kwargs: Additional arguments (ignored, kept for compatibility)
        """
        self.vector_store = vector_store
        self.rag_retriever = RAGRetriever(vector_store)
        # Store embedder for compatibility (not used for RAG, but agents may expect it)
        self.embedder = embedder
        
        # Initialize QueryAgent if available
        self.query_agent_retriever = None
        self.use_query_agent = False
        
        if QUERY_AGENT_AVAILABLE:
            self._initialize_query_agent()
        else:
            logger.debug("QueryAgent not available - will use PostgreSQL RAG")
    
    def _initialize_query_agent(self):
        """Initialize Weaviate QueryAgent if available and configured."""
        try:
            # Check if QueryAgent should be used
            use_query_agent_env = os.getenv("USE_WEAVIATE_QUERY_AGENT", "false").lower()
            if use_query_agent_env not in ("true", "1", "yes"):
                logger.debug("QueryAgent disabled via USE_WEAVIATE_QUERY_AGENT env var")
                return
            
            # Get Weaviate URL
            weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8081")
            
            # Connect to Weaviate
            weaviate_client = None
            if weaviate_url.startswith("http://localhost") or weaviate_url.startswith("http://127.0.0.1"):
                # Local Weaviate
                try:
                    weaviate_client = weaviate.connect_to_local(
                        host="localhost",
                        port=8081
                    )
                    logger.info("✅ Connected to local Weaviate")
                except Exception as e:
                    logger.warning(f"Failed to connect to local Weaviate: {e}")
                    return
            elif weaviate_url.startswith("https://"):
                # Weaviate Cloud
                weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
                if not weaviate_api_key or weaviate_api_key == "your_api_key_here":
                    logger.warning("WEAVIATE_API_KEY required for Weaviate Cloud")
                    return
                
                try:
                    # Parse URL: https://xxx.weaviate.cloud or https://xxx.weaviate.cloud:443
                    url_parts = weaviate_url.replace("https://", "").split(":")
                    host = url_parts[0]
                    
                    # Try to use weaviate.auth if available
                    try:
                        auth_credentials = weaviate.auth.AuthApiKey(api_key=weaviate_api_key)
                    except AttributeError:
                        # Fallback if auth module structure is different
                        auth_credentials = weaviate_api_key
                    
                    headers = {}
                    openai_key = os.getenv("OPENAI_API_KEY")
                    if openai_key:
                        headers["X-OpenAI-Api-Key"] = openai_key
                    
                    weaviate_client = weaviate.connect_to_wcs(
                        cluster_url=host,
                        auth_credentials=auth_credentials,
                        headers=headers if headers else None
                    )
                    logger.info("✅ Connected to Weaviate Cloud")
                except Exception as e:
                    logger.warning(f"Failed to connect to Weaviate Cloud: {e}")
                    return
            else:
                # Custom URL
                try:
                    url_parts = weaviate_url.replace("http://", "").replace("https://", "").split(":")
                    host = url_parts[0]
                    port = int(url_parts[1]) if len(url_parts) > 1 else 8081
                    is_secure = weaviate_url.startswith("https://")
                    
                    weaviate_client = weaviate.connect_to_custom(
                        http_host=host,
                        http_port=port,
                        http_secure=is_secure,
                        grpc_host=host,
                        grpc_port=50051 if not is_secure else 443,
                        grpc_secure=is_secure
                    )
                    logger.info(f"✅ Connected to custom Weaviate at {weaviate_url}")
                except Exception as e:
                    logger.warning(f"Failed to connect to custom Weaviate: {e}")
                    return
            
            # Initialize QueryAgent
            if weaviate_client:
                try:
                    self.query_agent_retriever = QueryAgent(client=weaviate_client)
                    self.use_query_agent = True
                    logger.info("✅ QueryAgent initialized - using Weaviate for RAG")
                except Exception as e:
                    logger.warning(f"Failed to initialize QueryAgent: {e}, falling back to PostgreSQL")
                    self.use_query_agent = False
        
        except Exception as e:
            logger.warning(f"Error initializing QueryAgent: {e}, will use PostgreSQL RAG")
            self.use_query_agent = False
        
        if not self.use_query_agent:
            logger.debug("Retriever initialized (PostgreSQL-based RAG fallback)")
    
    def retrieve_with_context(
        self, 
        query: str, 
        top_k: int = 3,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve context with sources (compatibility method for agents).
        
        Uses QueryAgent (Weaviate) if available, otherwise falls back to PostgreSQL RAG.
        
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
        # Try QueryAgent first if available
        if self.use_query_agent and self.query_agent_retriever:
            try:
                # Map category_filter to Weaviate collection name
                weaviate_collection = None
                if category_filter:
                    # Map category_filter to AgentType first
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
                    if agent_type:
                        weaviate_collection = get_collection_name(agent_type)
                
                # Use QueryAgent search() method
                # QueryAgent handles natural language to Weaviate query conversion
                search_params = {"query": query, "limit": top_k}
                if weaviate_collection:
                    # Note: QueryAgent may handle collection routing automatically
                    # But we can pass it as context if needed
                    pass
                
                results = self.query_agent_retriever.search(**search_params)
                
                # Format QueryAgent response to match expected format
                context_parts = []
                sources = []
                
                # QueryAgent.search() returns objects with properties
                if hasattr(results, 'objects') and results.objects:
                    for obj in results.objects:
                        # Extract text content from object properties
                        text = ""
                        if hasattr(obj, 'properties'):
                            # Try common property names for text content
                            text = (
                                obj.properties.get("content", "") or
                                obj.properties.get("text", "") or
                                obj.properties.get("body", "") or
                                str(obj.properties.get("description", ""))
                            )
                        
                        if not text:
                            # If no text property, use all properties as text
                            text = str(obj.properties) if hasattr(obj, 'properties') else str(obj)
                        
                        context_parts.append(text)
                        
                        # Extract metadata
                        metadata = obj.properties if hasattr(obj, 'properties') else {}
                        similarity = getattr(obj, 'certainty', getattr(obj, 'distance', 0.0))
                        if hasattr(similarity, '__float__'):
                            # If distance, convert to similarity (higher is better)
                            similarity_float = float(similarity)
                            if similarity_float > 1.0:
                                similarity_float = 1.0 / (1.0 + similarity_float)  # Distance to similarity
                        else:
                            similarity_float = 0.0
                        
                        obj_id = str(getattr(obj, 'uuid', getattr(obj, 'id', '')))
                        
                        sources.append({
                            "source": metadata.get("source", metadata.get("url", "Weaviate")),
                            "title": metadata.get("title", metadata.get("name", "")),
                            "text": text[:200] + "..." if len(text) > 200 else text,
                            "similarity": similarity_float,
                            "metadata": metadata,
                            "id": obj_id
                        })
                    
                    logger.debug(f"QueryAgent retrieved {len(sources)} documents")
                    
                    return {
                        "context": "\n\n".join(context_parts),
                        "sources": sources,
                        "count": len(sources)
                    }
                else:
                    logger.warning("QueryAgent returned no results, falling back to PostgreSQL")
            
            except Exception as e:
                logger.warning(f"QueryAgent search failed: {e}, falling back to PostgreSQL RAG")
                # Fall through to PostgreSQL fallback
        
        # Fallback to PostgreSQL RAG (existing implementation)
        return self._retrieve_with_postgresql(query, top_k, category_filter)
    
    def _retrieve_with_postgresql(
        self,
        query: str,
        top_k: int,
        category_filter: Optional[str]
    ) -> Dict[str, Any]:
        """
        Fallback method using PostgreSQL RAG.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            category_filter: Optional category filter
        
        Returns:
            Dictionary with context and sources
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
        # Use retrieve_with_context and extract documents
        result = self.retrieve_with_context(query, top_k=top_k)
        
        # Convert to list format for backward compatibility
        documents = []
        for source in result.get("sources", []):
            documents.append({
                "text": source.get("text", ""),
                "metadata": source.get("metadata", {}),
                "distance": 1.0 - source.get("similarity", 0.0),  # Convert back to distance
                "id": source.get("id", "")
            })
        
        return documents


