"""Retriever using Weaviate QueryAgent for natural language queries."""

import logging
from typing import Dict, List, Optional
import os

try:
    import weaviate
    from weaviate.agents.query import QueryAgent
    QUERY_AGENT_AVAILABLE = True
except ImportError:
    QUERY_AGENT_AVAILABLE = False

logger = logging.getLogger(__name__)


class QueryAgentRetriever:
    """Retriever using Weaviate QueryAgent for intelligent querying."""
    
    def __init__(self, weaviate_url: Optional[str] = None, 
                 collection_names: Optional[List[str]] = None):
        """
        Initialize QueryAgent retriever.
        
        Args:
            weaviate_url: Weaviate instance URL
            collection_names: List of collection names to search across
        """
        if not QUERY_AGENT_AVAILABLE:
            raise ImportError(
                "Weaviate QueryAgent not available. Install with: pip install weaviate-client[agents]"
            )
        
        self.weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL", "http://localhost:8081")
        self.collection_names = collection_names or []
        
        # Connect to Weaviate
        self._connect()
        
        # Initialize QueryAgent (uses 'collections' parameter, not 'collection_names')
        self.query_agent = QueryAgent(
            client=self.client,
            collections=self.collection_names if self.collection_names else None
        )
        
        logger.info(f"✅ QueryAgent initialized for collections: {self.collection_names or 'all'}")
    
    def _connect(self):
        """Connect to Weaviate."""
        try:
            # Parse URL
            if self.weaviate_url.startswith("http://"):
                url_parts = self.weaviate_url.replace("http://", "").split(":")
                host = url_parts[0]
                port = int(url_parts[1]) if len(url_parts) > 1 else 8081
                http_secure = False
            elif self.weaviate_url.startswith("https://"):
                url_parts = self.weaviate_url.replace("https://", "").split(":")
                host = url_parts[0]
                port = int(url_parts[1]) if len(url_parts) > 1 else 443
                http_secure = True
            else:
                host = "localhost"
                port = 8081
                http_secure = False
            
            # Connect
            if "localhost" in host or "127.0.0.1" in host:
                try:
                    import weaviate.classes.init as wvc
                    self.client = weaviate.connect_to_local(
                        port=port,
                        grpc_port=50051,
                        additional_config=wvc.AdditionalConfig(skip_init_checks=True)
                    )
                except (AttributeError, ImportError):
                    # Fallback without additional config
                    self.client = weaviate.connect_to_local(
                        port=port,
                        grpc_port=50051,
                        skip_init_checks=True
                    )
            else:
                self.client = weaviate.connect_to_custom(
                    http_host=host,
                    http_port=port,
                    http_secure=http_secure,
                    grpc_host=host,
                    grpc_port=50051,
                    grpc_secure=http_secure
                )
            
            logger.info(f"✅ Connected to Weaviate at {self.weaviate_url}")
            
        except Exception as e:
            error_msg = f"❌ Could not connect to Weaviate: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def search(self, query: str, top_k: int = 5, 
               collection_filter: Optional[str] = None) -> Dict:
        """
        Search using QueryAgent (search mode - retrieval only).
        
        Args:
            query: Natural language query
            top_k: Number of results
            collection_filter: Optional collection to filter by
            
        Returns:
            Dictionary with results and sources
        """
        try:
            # Determine which collections to search
            collections_to_search = [collection_filter] if collection_filter else self.collection_names
            
            # Use search mode (retrieval only, no answer generation)
            search_response = self.query_agent.search(
                query=query,
                limit=top_k,
                collections=collections_to_search if collections_to_search else None
            )
            
            # Format results
            documents = []
            sources = []
            
            # Access objects from search_response.search_results (QueryReturn object)
            objects = []
            if hasattr(search_response, 'search_results'):
                search_results = search_response.search_results
                # QueryReturn has 'objects' attribute
                if hasattr(search_results, 'objects'):
                    objects = search_results.objects
                elif hasattr(search_results, 'data'):
                    objects = search_results.data
            elif hasattr(search_response, 'objects'):
                objects = search_response.objects
            
            for obj in objects:
                props = obj.properties
                content = props.get("content", props.get("text", ""))
                source = props.get("source", "unknown")
                category = props.get("category", "")
                
                # Get metadata if available
                metadata_str = props.get("metadata_json", "{}")
                try:
                    import json
                    meta = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                except:
                    meta = {}
                
                documents.append({
                    "content": content,
                    "source": source,
                    "category": category,
                    **meta
                })
                
                sources.append({
                    "source": source,
                    "category": category,
                    "similarity": 1.0  # QueryAgent doesn't provide similarity scores directly
                })
            
            # Format context
            context_parts = [f"[{i+1}] {doc['content']}" for i, doc in enumerate(documents)]
            context = "\n\n".join(context_parts)
            
            logger.info(f"✅ QueryAgent search returned {len(documents)} results")
            
            return {
                "context": context,
                "documents": documents,
                "sources": sources,
                "count": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error in QueryAgent search: {e}")
            raise
    
    def ask(self, query: str, top_k: int = 5,
            collection_filter: Optional[str] = None) -> Dict:
        """
        Ask QueryAgent (ask mode - with answer generation).
        
        Args:
            query: Natural language question
            top_k: Number of results to use
            collection_filter: Optional collection to filter by
            
        Returns:
            Dictionary with answer, results, and sources
        """
        try:
            # Determine which collections to search
            collections_to_search = [collection_filter] if collection_filter else self.collection_names
            
            # Use ask mode (with answer generation)
            response = self.query_agent.ask(
                query=query,
                limit=top_k,
                collections=collections_to_search if collections_to_search else None
            )
            
            # Format results (AskModeResponse has final_answer, sources, and searches)
            documents = []
            sources = []
            
            # Get answer (AskModeResponse has 'final_answer')
            answer = response.final_answer if hasattr(response, 'final_answer') else ""
            
            # Get sources (AskModeResponse has 'sources')
            response_sources = []
            if hasattr(response, 'sources') and response.sources:
                response_sources = response.sources
            
            # Get objects from searches (list of QueryResultWithCollectionNormalized)
            objects = []
            if hasattr(response, 'searches') and response.searches:
                for search_result in response.searches:
                    # Each search_result has objects
                    if hasattr(search_result, 'objects'):
                        objects.extend(search_result.objects)
                    elif hasattr(search_result, 'data'):
                        objects.extend(search_result.data)
            
            for obj in objects:
                props = obj.properties
                content = props.get("content", props.get("text", ""))
                source = props.get("source", "unknown")
                category = props.get("category", "")
                
                documents.append({
                    "content": content,
                    "source": source,
                    "category": category
                })
                
                sources.append({
                    "source": source,
                    "category": category
                })
            
            logger.info(f"✅ QueryAgent ask returned answer with {len(documents)} sources")
            
            return {
                "answer": answer,  # Generated answer
                "context": answer,  # Use answer as context
                "documents": documents,
                "sources": sources,
                "count": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error in QueryAgent ask: {e}")
            raise
    
    def close(self):
        """Close Weaviate connection."""
        if self.client:
            try:
                self.client.close()
                logger.info("Closed Weaviate connection")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

