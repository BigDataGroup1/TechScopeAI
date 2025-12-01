"""Weaviate vector store implementation (Weaviate only, no fallback)."""

import logging
import os
import json
from typing import List, Dict, Optional
import numpy as np

try:
    import weaviate
    from weaviate.classes.config import Configure, Property, DataType, VectorDistances
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

logger = logging.getLogger(__name__)


class WeaviateStore:
    """Weaviate-based vector store for semantic search (Weaviate only, no fallback)."""
    
    def __init__(self, category: str, weaviate_url: Optional[str] = None, 
                 dimension: int = 384):
        """
        Initialize Weaviate vector store.
        
        Args:
            category: Category name (e.g., "pitch", "competitive")
            weaviate_url: Weaviate instance URL (defaults to WEAVIATE_URL env var)
            dimension: Dimension of embeddings (384 for MiniLM, 1536 for OpenAI)
            
        Raises:
            RuntimeError: If Weaviate is not available or connection fails
        """
        self.category = category
        self.dimension = dimension
        
        # Get Weaviate URL from env or parameter
        self.weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL", "http://localhost:8080")
        
        # Class name (Weaviate collection name)
        self.class_name = f"TechScopeAI_{category.capitalize()}"
        
        # Initialize Weaviate client
        self.client = None
        self.weaviate_available = False
        
        if WEAVIATE_AVAILABLE:
            try:
                # Parse URL
                if self.weaviate_url.startswith("http://"):
                    url_parts = self.weaviate_url.replace("http://", "").split(":")
                    host = url_parts[0]
                    port = int(url_parts[1]) if len(url_parts) > 1 else 8080
                    http_secure = False
                elif self.weaviate_url.startswith("https://"):
                    url_parts = self.weaviate_url.replace("https://", "").split(":")
                    host = url_parts[0]
                    port = int(url_parts[1]) if len(url_parts) > 1 else 443
                    http_secure = True
                else:
                    # Assume localhost
                    host = "localhost"
                    port = 8080
                    http_secure = False
                
                # Connect to Weaviate
                if "localhost" in host or "127.0.0.1" in host:
                    # Use skip_init_checks for local development
                    try:
                        import weaviate.classes.init as wvc
                        self.client = weaviate.connect_to_local(
                            port=port,
                            grpc_port=50051,
                            additional_config=wvc.AdditionalConfig(
                                skip_init_checks=True  # Skip gRPC health check for local dev
                            )
                        )
                    except (AttributeError, ImportError):
                        # Fallback: try without additional config
                        self.client = weaviate.connect_to_local(
                            port=port,
                            grpc_port=50051,
                            skip_init_checks=True
                        )
                else:
                    # Remote Weaviate (Google Cloud)
                    self.client = weaviate.connect_to_custom(
                        http_host=host,
                        http_port=port,
                        http_secure=http_secure,
                        grpc_host=host,
                        grpc_port=50051,
                        grpc_secure=http_secure
                    )
                
                # Create collection if it doesn't exist
                self._create_collection()
                self.weaviate_available = True
                logger.info(f"✅ Connected to Weaviate at {self.weaviate_url}")
                
            except Exception as e:
                error_msg = f"❌ Could not connect to Weaviate at {self.weaviate_url}: {e}"
                logger.error(error_msg)
                raise RuntimeError(error_msg + "\nMake sure Weaviate is running and WEAVIATE_URL is set correctly.")
        else:
            error_msg = "❌ Weaviate client not installed. Install with: pip install weaviate-client"
            logger.error(error_msg)
            raise ImportError(error_msg)
    
    def _create_collection(self):
        """Create Weaviate collection if it doesn't exist."""
        if not self.client:
            raise RuntimeError("Weaviate client not initialized")
        
        try:
            # Check if collection exists
            if self.client.collections.exists(self.class_name):
                logger.info(f"Collection {self.class_name} already exists")
                return
            
            # Create collection with vector index
            # Note: Using deprecated API for compatibility (warnings are OK)
            self.client.collections.create(
                name=self.class_name,
                vectorizer_config=Configure.Vectorizer.none(),  # We provide vectors
                properties=[
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="category", data_type=DataType.TEXT),
                    Property(name="metadata_json", data_type=DataType.TEXT),  # JSON string
                ],
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=VectorDistances.COSINE
                )
            )
            logger.info(f"✅ Created Weaviate collection: {self.class_name}")
            
        except Exception as e:
            error_msg = f"Error creating Weaviate collection: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def add(self, embeddings: np.ndarray, metadata: List[Dict]):
        """
        Add embeddings and metadata to the store.
        
        Args:
            embeddings: Array of embedding vectors (n x dimension)
            metadata: List of metadata dicts (one per embedding)
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        if self.weaviate_available and self.client:
            try:
                # Get collection
                collection = self.client.collections.get(self.class_name)
                
                # Convert embeddings to list format
                vectors = embeddings.tolist()
                
                # Prepare objects for batch insert
                objects_to_add = []
                for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                    objects_to_add.append({
                        "content": meta.get("content", meta.get("text", "")),
                        "source": meta.get("source", "unknown"),
                        "category": meta.get("category", self.category),
                        "metadata_json": json.dumps(meta),  # Store full metadata as JSON string
                    })
                
                # Batch insert with vectors
                with collection.batch.dynamic() as batch:
                    for obj, vector in zip(objects_to_add, vectors):
                        batch.add_object(
                            properties=obj,
                            vector=vector
                        )
                
                logger.info(f"✅ Added {len(embeddings)} vectors to Weaviate collection {self.class_name}")
                
            except Exception as e:
                error_msg = f"Error adding to Weaviate: {e}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        else:
            raise RuntimeError("Weaviate is not available. Check connection and configuration.")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of metadata dicts with similarity scores
        """
        if self.weaviate_available and self.client:
            try:
                collection = self.client.collections.get(self.class_name)
                
                # Convert query to list
                query_vector = query_embedding.tolist()
                
                # Search
                response = collection.query.near_vector(
                    near_vector=query_vector,
                    limit=top_k,
                    return_metadata=["distance", "certainty"]
                )
                
                # Format results
                results = []
                for obj in response.objects:
                    props = obj.properties
                    metadata_str = props.get("metadata_json", "{}")
                    
                    # Parse metadata
                    try:
                        meta = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                    except:
                        meta = {
                            "content": props.get("content", ""),
                            "source": props.get("source", "unknown"),
                            "category": props.get("category", self.category)
                        }
                    
                    # Get similarity from distance (Weaviate uses cosine distance)
                    distance = obj.metadata.distance if hasattr(obj.metadata, 'distance') else 0
                    similarity = 1 - abs(distance)  # Convert distance to similarity
                    
                    results.append({
                        **meta,
                        "similarity_score": float(similarity),
                        "distance": float(distance)
                    })
                
                logger.info(f"✅ Found {len(results)} results from Weaviate")
                return results
                
            except Exception as e:
                error_msg = f"Error searching Weaviate: {e}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        else:
            raise RuntimeError("Weaviate is not available. Check connection and configuration.")
    
    def save(self):
        """Save vector store (Weaviate persists automatically, no action needed)."""
        # Weaviate persists automatically, no need to save
        logger.debug("Weaviate persists automatically, no save needed")
    
    def load(self):
        """Load vector store (Weaviate loads automatically, no action needed)."""
        # Weaviate loads automatically, no need to load
        logger.debug("Weaviate loads automatically, no load needed")
    
    def get_count(self) -> int:
        """Get number of vectors in store."""
        if not self.weaviate_available or not self.client:
            raise RuntimeError("Weaviate is not available")
        
        try:
            collection = self.client.collections.get(self.class_name)
            result = collection.aggregate.over_all(total_count=True)
            return result.total_count if hasattr(result, 'total_count') else 0
        except Exception as e:
            error_msg = f"Error getting count from Weaviate: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def close(self):
        """Close Weaviate connection."""
        if self.client:
            try:
                self.client.close()
                logger.info("Closed Weaviate connection")
            except Exception as e:
                logger.warning(f"Error closing Weaviate connection: {e}")

