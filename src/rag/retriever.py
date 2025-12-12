"""
Retriever compatibility layer for agents.

This module provides a Retriever class that wraps RAGRetriever and provides
the interface expected by agents. Supports Weaviate (primary) via HTTP v3 client.
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# #region agent log
def _debug_log(location: str, message: str, data: dict, hypothesis_id: str):
    """Write debug log - prints to stdout for Cloud Run visibility."""
    try:
        import json
        log_entry = {
            "location": location,
            "message": message,
            "data": data,
            "hypothesisId": hypothesis_id,
        }
        # Print to stdout - this will appear in Cloud Run logs
        print(f"[DEBUG-{hypothesis_id}] {location}: {message} | {json.dumps(data)}", flush=True)
    except Exception as e:
        print(f"[DEBUG-ERROR] Could not log: {e}", flush=True)
# #endregion

# Try to import weaviate v3 client (HTTP-based, no gRPC)
try:
    import weaviate
    from weaviate.auth import AuthApiKey
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    weaviate = None
    AuthApiKey = None
    logger.warning("Weaviate client not available")

# Optional imports - only needed for PostgreSQL fallback (not used with Weaviate)
try:
    from .retrieval import RAGRetriever
    from .vector_store import VectorStore
    POSTGRES_RAG_AVAILABLE = True
except ImportError:
    RAGRetriever = None
    VectorStore = None
    POSTGRES_RAG_AVAILABLE = False

# Collections are always needed
try:
    from .collections import AgentType, get_collection_name
except ImportError:
    AgentType = None
    get_collection_name = None


class Retriever:
    """
    Compatibility wrapper - uses Weaviate for RAG.
    """
    
    def __init__(self, vector_store=None, embedder=None, **kwargs):
        """
        Initialize Retriever.
        
        Args:
            vector_store: Optional VectorStore (not used with Weaviate)
            embedder: Optional embedder (not used with Weaviate)
            **kwargs: Additional arguments (ignored)
        """
        self.vector_store = vector_store
        self.embedder = embedder
        
        # RAGRetriever only needed for PostgreSQL fallback
        if POSTGRES_RAG_AVAILABLE and RAGRetriever and vector_store:
            self.rag_retriever = RAGRetriever(vector_store)
        else:
            self.rag_retriever = None
        
        # Initialize Weaviate client
        self.weaviate_client = None
        self.use_weaviate = False
        
        if WEAVIATE_AVAILABLE:
            self._initialize_weaviate()
        else:
            logger.warning("Weaviate not available")
    
    def _initialize_weaviate(self):
        """Initialize Weaviate client using v3 HTTP-based API (no gRPC issues)."""
        try:
            # Check if Weaviate should be used
            use_weaviate_env = os.getenv("USE_WEAVIATE_QUERY_AGENT", "false").lower()
            if use_weaviate_env not in ("true", "1", "yes"):
                logger.debug("Weaviate disabled via USE_WEAVIATE_QUERY_AGENT env var")
                return
            
            # Get Weaviate URL
            weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8081")
            weaviate_api_key = os.getenv("WEAVIATE_API_KEY", "")
            
            # #region agent log
            # Hypothesis A: API key has newline/carriage return corrupting HTTP header
            # Hypothesis B: API key format is wrong (not the right key for this cluster)
            # Hypothesis C: Weaviate URL format issue
            import weaviate as wv_module
            wv_version = getattr(wv_module, '__version__', 'unknown')
            key_len = len(weaviate_api_key) if weaviate_api_key else 0
            key_has_newline = '\n' in weaviate_api_key or '\r' in weaviate_api_key
            key_has_whitespace = weaviate_api_key != weaviate_api_key.strip() if weaviate_api_key else False
            key_first_10 = weaviate_api_key[:10] if weaviate_api_key else ""
            key_last_10 = weaviate_api_key[-10:] if weaviate_api_key else ""
            key_last_5_bytes = [ord(c) for c in weaviate_api_key[-5:]] if weaviate_api_key and len(weaviate_api_key) >= 5 else []
            _debug_log("retriever.py:_initialize_weaviate:entry", "Weaviate init - checking API key format", {
                "weaviate_version": wv_version,
                "api_key_length": key_len,
                "api_key_has_newline": key_has_newline,
                "api_key_has_trailing_whitespace": key_has_whitespace,
                "api_key_first_10": key_first_10,
                "api_key_last_10_repr": repr(key_last_10),
                "api_key_last_5_bytes": key_last_5_bytes,
                "weaviate_url": weaviate_url,
                "full_url_will_be": f"https://{weaviate_url.replace('https://', '').replace('http://', '')}" if ".weaviate.cloud" in weaviate_url else weaviate_url
            }, "A_B_C")
            logger.info(f"DEBUG: Weaviate version={wv_version}, key_len={key_len}, has_newline={key_has_newline}, has_trailing_ws={key_has_whitespace}")
            # #endregion
            
            # Normalize URL 
            normalized_url = weaviate_url.replace("https://", "").replace("http://", "")
            
            # Detect Weaviate Cloud
            is_cloud = ".weaviate.cloud" in normalized_url or ".weaviate.network" in normalized_url
            
            # Build the full URL
            if is_cloud:
                full_url = f"https://{normalized_url}"
            elif weaviate_url.startswith("http"):
                full_url = weaviate_url
            else:
                full_url = f"http://{normalized_url}"
            
            logger.info(f"Connecting to Weaviate at: {full_url}")
            
            # Create v3 client (HTTP-based, no gRPC!)
            # #region agent log
            # Strip the API key to remove any newlines/whitespace (fix for Hypothesis A)
            clean_api_key = weaviate_api_key.strip() if weaviate_api_key else ""
            _debug_log("retriever.py:_initialize_weaviate:before_connect", "About to create Weaviate client", {
                "full_url": full_url,
                "has_api_key": bool(clean_api_key),
                "clean_key_length": len(clean_api_key),
                "original_key_length": len(weaviate_api_key) if weaviate_api_key else 0,
                "key_was_stripped": len(clean_api_key) != len(weaviate_api_key) if weaviate_api_key else False
            }, "A")
            # #endregion
            
            if clean_api_key and clean_api_key != "your_api_key_here":
                # With authentication - use CLEANED key
                auth_config = AuthApiKey(api_key=clean_api_key)
                self.weaviate_client = weaviate.Client(
                    url=full_url,
                    auth_client_secret=auth_config,
                    timeout_config=(5, 60)  # (connect timeout, read timeout)
                )
                logger.info(f"✅ Connected to Weaviate Cloud at {full_url} (with API key)")
            else:
                # Without authentication (local)
                self.weaviate_client = weaviate.Client(
                    url=full_url,
                    timeout_config=(5, 60)
                )
                logger.info(f"✅ Connected to local Weaviate at {full_url}")
            
            # Verify connection
            # #region agent log
            try:
                is_ready = self.weaviate_client.is_ready()
                _debug_log("retriever.py:_initialize_weaviate:after_connect", "Weaviate is_ready check", {
                    "is_ready": is_ready,
                    "success": True
                }, "A_B")
            except Exception as ready_err:
                _debug_log("retriever.py:_initialize_weaviate:ready_error", "Weaviate is_ready failed", {
                    "error": str(ready_err),
                    "error_type": type(ready_err).__name__
                }, "A_B")
                is_ready = False
            # #endregion
            
            if is_ready:
                self.use_weaviate = True
                logger.info("✅ Weaviate connection verified - ready for queries")
            else:
                logger.warning("Weaviate connection established but not ready")
                self.weaviate_client = None
                
        except Exception as e:
            # #region agent log
            import traceback
            tb = traceback.format_exc()
            _debug_log("retriever.py:_initialize_weaviate:exception", "Weaviate init failed", {
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback_last_200": tb[-200:] if len(tb) > 200 else tb
            }, "A_B_C")
            # #endregion
            logger.warning(f"Error initializing Weaviate: {e}, will use PostgreSQL RAG")
            logger.debug(tb)
            self.use_weaviate = False
        
        if not self.use_weaviate:
            logger.debug("Retriever initialized (PostgreSQL-based RAG fallback)")
    
    def retrieve_with_context(
        self, 
        query: str, 
        top_k: int = 3,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve context with sources (compatibility method for agents).
        
        Uses Weaviate v3 (HTTP) if available, otherwise falls back to PostgreSQL RAG.
        
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
        # Try Weaviate first if available
        if self.use_weaviate and self.weaviate_client:
            logger.debug("🔍 Using Weaviate v3 HTTP API (NOT PostgreSQL)")
            try:
                # Map category_filter to Weaviate collection name
                weaviate_collection = None
                if category_filter:
                    weaviate_collection_map = {
                        "competitive": "Competitors_corpus",
                        "pitch": "Pitch_examples_corpus",
                        "marketing": "Marketing_corpus",
                        "ip_legal": "Ip_policy_corpus",
                        "patent": "Ip_policy_corpus",
                        "policy": "Policy_corpus",
                        "team": "Job_roles_corpus",
                    }
                    weaviate_collection = weaviate_collection_map.get(category_filter.lower())
                    
                    if not weaviate_collection:
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
                            internal_name = get_collection_name(agent_type)
                            if internal_name:
                                parts = internal_name.split("_")
                                weaviate_collection = "_".join(part.capitalize() for part in parts)
                
                # Use Weaviate v3 query API
                context_parts = []
                sources = []
                
                collections_to_search = [weaviate_collection] if weaviate_collection else [
                    "Competitors_corpus",
                    "Marketing_corpus",
                    "Ip_policy_corpus",
                    "Policy_corpus",
                    "Job_roles_corpus",
                    "Pitch_examples_corpus"
                ]
                
                for collection_name in collections_to_search:
                    try:
                        # Check if collection exists
                        schema = self.weaviate_client.schema.get()
                        class_names = [c['class'] for c in schema.get('classes', [])]
                        
                        if collection_name not in class_names:
                            logger.debug(f"Collection {collection_name} not found, skipping")
                            continue
                        
                        # Use nearText for semantic search (Weaviate v3 API)
                        result = (
                            self.weaviate_client.query
                            .get(collection_name, ["content", "text", "body", "description", "source", "title", "url"])
                            .with_near_text({"concepts": [query]})
                            .with_limit(top_k)
                            .with_additional(["certainty", "distance"])
                            .do()
                        )
                        
                        # Process results
                        if result and 'data' in result and 'Get' in result['data']:
                            objects = result['data']['Get'].get(collection_name, [])
                            
                            for obj in objects:
                                # Extract text content
                                text = (
                                    obj.get("content", "") or
                                    obj.get("text", "") or
                                    obj.get("body", "") or
                                    str(obj.get("description", ""))
                                )
                                
                                if not text:
                                    text = str(obj)
                                
                                if text:
                                    context_parts.append(text)
                                    
                                    # Extract similarity from _additional
                                    additional = obj.get("_additional", {})
                                    certainty = additional.get("certainty", 0.0)
                                    
                                    sources.append({
                                        "source": obj.get("source", obj.get("url", "Weaviate")),
                                        "title": obj.get("title", obj.get("name", "")),
                                        "text": text[:200] + "..." if len(text) > 200 else text,
                                        "similarity": certainty if certainty else 0.5,
                                        "metadata": obj,
                                        "id": str(obj.get("_additional", {}).get("id", ""))
                                    })
                                    
                    except Exception as coll_err:
                        logger.debug(f"Error querying collection {collection_name}: {coll_err}")
                        continue
                
                if sources:
                    logger.info(f"✅ Weaviate v3 retrieved {len(sources)} documents")
                    return {
                        "context": "\n\n".join(context_parts),
                        "sources": sources,
                        "count": len(sources)
                    }
                else:
                    logger.info(f"ℹ️ Weaviate returned no results for query: {query[:50]}...")
                    return {
                        "context": "",
                        "sources": [],
                        "count": 0
                    }
            
            except Exception as e:
                logger.warning(f"Weaviate search failed: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return {
                    "context": "",
                    "sources": [],
                    "count": 0
                }
        
        # Fallback to PostgreSQL if Weaviate is not enabled and PostgreSQL is available
        if not self.use_weaviate and POSTGRES_RAG_AVAILABLE and self.rag_retriever:
            logger.debug("🔍 Using PostgreSQL RAG (Weaviate not enabled)")
            return self._retrieve_with_postgresql(query, top_k, category_filter)
        else:
            logger.warning("No RAG backend available, returning empty results")
            return {
                "context": "",
                "sources": [],
                "count": 0
            }
    
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
    
    def close(self):
        """
        Close Weaviate connection to prevent resource warnings.
        Should be called when done using the retriever.
        Note: Weaviate v3 client doesn't have an explicit close method.
        """
        if self.weaviate_client:
            try:
                # v3 client doesn't have close(), just set to None
                logger.debug("✅ Weaviate client reference cleared")
            except Exception as e:
                logger.warning(f"Error clearing Weaviate connection: {e}")
            finally:
                self.weaviate_client = None


