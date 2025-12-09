"""
PostgreSQL + pgvector vector store wrapper.

Manages PostgreSQL database with pgvector extension for storing and querying embeddings.

Defaults to Cloud SQL connection. Local connection only when explicitly requested.
"""

import logging
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import psycopg2
from psycopg2.extras import execute_values, Json
from psycopg2.pool import ThreadedConnectionPool
import numpy as np

from .embeddings import EmbeddingModel
from .db_config import get_database_url

logger = logging.getLogger(__name__)


class VectorStore:
    """PostgreSQL + pgvector vector store wrapper."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        embedding_model: Optional[EmbeddingModel] = None,
        pool_size: int = 5,
        use_local: bool = False
    ):
        """
        Initialize the vector store.
        
        Args:
            database_url: PostgreSQL connection URL (overrides all other settings)
            embedding_model: Optional embedding model for custom embeddings
            pool_size: Connection pool size
            use_local: If True, use local PostgreSQL (localhost:5432). 
                      If False (default), use Cloud SQL via CLOUD_SQL_PASSWORD.
                      Ignored if database_url is provided.
        """
        self.embedding_model = embedding_model
        
        # Get database URL - defaults to Cloud SQL unless use_local=True
        self.database_url = get_database_url(use_local=use_local, database_url=database_url)
        
        # Initialize connection pool
        try:
            # Test connection first with a simple connection
            test_conn = psycopg2.connect(self.database_url, connect_timeout=5)
            test_conn.close()
            
            # If test succeeds, create pool
            self.pool = ThreadedConnectionPool(1, pool_size, dsn=self.database_url)
            logger.info(f"✅ PostgreSQL connected: {self.database_url.split('@')[-1] if '@' in self.database_url else 'local'}")
            
            # Ensure pgvector extension is enabled
            self._ensure_pgvector_extension()
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            logger.warning(f"⚠️  Failed to connect to PostgreSQL: {error_msg}")
            if "Connection refused" in error_msg:
                logger.warning("💡 Cloud SQL Proxy might not be running. Start it with: ./start_proxy_simple.sh")
            elif "server closed the connection" in error_msg:
                logger.warning("💡 Cloud SQL Proxy might have crashed. Check proxy terminal and restart it.")
            logger.warning("VectorStore will work in limited mode. Some features may not be available.")
            # Don't raise - allow graceful degradation
            self.pool = None
        except Exception as e:
            logger.warning(f"⚠️  Failed to connect to PostgreSQL: {e}")
            logger.warning("VectorStore will work in limited mode. Some features may not be available.")
            # Don't raise - allow graceful degradation
            self.pool = None
    
    def _get_connection(self):
        """Get a connection from the pool."""
        if self.pool is None:
            raise ConnectionError("PostgreSQL connection pool not initialized. Database may not be available.")
        return self.pool.getconn()
    
    def _put_connection(self, conn):
        """Return a connection to the pool."""
        if self.pool is None:
            return
        self.pool.putconn(conn)
    
    def _ensure_pgvector_extension(self):
        """Ensure pgvector extension is enabled."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                conn.commit()
                logger.debug("pgvector extension enabled")
        except Exception as e:
            logger.warning(f"Could not enable pgvector extension: {e}")
            conn.rollback()
        finally:
            self._put_connection(conn)
    
    def get_or_create_collection(
        self,
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Get or create a collection (table) in PostgreSQL.
        
        Args:
            collection_name: Name of the collection (table name)
            metadata: Optional metadata (not used in PostgreSQL schema)
        
        Returns:
            Collection name
        """
        try:
            # Get embedding dimension
            vector_size = 384  # Default for all-MiniLM-L6-v2
            if self.embedding_model:
                vector_size = self.embedding_model.get_dimension()
            
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    # Check if table exists
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s
                        );
                    """, (collection_name,))
                    
                    table_exists = cur.fetchone()[0]
                    
                    if table_exists:
                        logger.info(f"Collection '{collection_name}' exists")
                        return collection_name
                    
                    # Create new table with vector column
                    logger.info(f"Creating collection '{collection_name}'...")
                    
                    cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS {collection_name} (
                            id SERIAL PRIMARY KEY,
                            chunk_id VARCHAR(255) UNIQUE NOT NULL,
                            text TEXT NOT NULL,
                            embedding vector({vector_size}) NOT NULL,
                            metadata JSONB DEFAULT '{{}}'::jsonb,
                            created_at TIMESTAMP DEFAULT NOW()
                        );
                    """)
                    
                    # Create index for vector similarity search
                    # Using HNSW index for better performance
                    cur.execute(f"""
                        CREATE INDEX IF NOT EXISTS {collection_name}_embedding_idx 
                        ON {collection_name} 
                        USING hnsw (embedding vector_cosine_ops)
                        WITH (m = 16, ef_construction = 64);
                    """)
                    
                    # Create index on chunk_id for faster lookups
                    cur.execute(f"""
                        CREATE INDEX IF NOT EXISTS {collection_name}_chunk_id_idx 
                        ON {collection_name} (chunk_id);
                    """)
                    
                    conn.commit()
                    logger.info(f"Collection '{collection_name}' created successfully")
                    return collection_name
                    
            finally:
                self._put_connection(conn)
                
        except Exception as e:
            logger.error(f"Error getting/creating collection '{collection_name}': {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            texts: List of text documents
            metadatas: Optional list of metadata dicts (one per document)
            ids: Optional list of document IDs (auto-generated if not provided)
        """
        self.get_or_create_collection(collection_name)
        
        try:
            # Generate IDs if not provided
            if ids is None:
                ids = [f"{collection_name}_doc_{i}" for i in range(len(texts))]
            
            # Ensure metadatas is the right length
            if metadatas is None:
                metadatas = [{}] * len(texts)
            
            # Generate embeddings if we have an embedding model
            if self.embedding_model is None:
                raise ValueError("Embedding model is required for PostgreSQL")
            
            logger.debug(f"Generating embeddings for {len(texts)} documents...")
            embeddings = self.embedding_model.encode(texts)
            
            # Convert to list if numpy array
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            # Prepare data for batch insert
            values = []
            for i, text in enumerate(texts):
                metadata = metadatas[i] if i < len(metadatas) else {}
                
                # Prepare metadata JSON
                metadata_json = {
                    "agent": metadata.get("agent", collection_name.split("_")[0]),
                    "source": metadata.get("source", "processed"),
                    **{k: v for k, v in metadata.items() 
                       if k not in ["agent", "source", "text", "chunk_id"]}
                }
                
                values.append((
                    ids[i],  # chunk_id
                    text,    # text
                    embeddings[i],  # embedding (as list)
                    Json(metadata_json)  # metadata as JSONB
                ))
            
            # Batch insert using execute_values for efficiency
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        f"""
                        INSERT INTO {collection_name} (chunk_id, text, embedding, metadata)
                        VALUES %s
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            text = EXCLUDED.text,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                        """,
                        values,
                        template=None,
                        page_size=100
                    )
                    conn.commit()
                    logger.info(f"Added {len(texts)} documents to collection '{collection_name}'")
            finally:
                self._put_connection(conn)
            
        except Exception as e:
            logger.error(f"Error adding documents to '{collection_name}': {e}")
            raise
    
    def query(
        self,
        collection_name: str,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query a collection.
        
        Args:
            collection_name: Name of the collection
            query_texts: Query text(s) (will be embedded)
            query_embeddings: Pre-computed query embeddings (alternative to query_texts)
            n_results: Number of results to return
            where: Metadata filter (PostgreSQL WHERE clause conditions)
            where_document: Document content filter (text search)
        
        Returns:
            Dictionary with keys: ids, distances, documents, metadatas
        """
        self.get_or_create_collection(collection_name)
        
        try:
            # Get query vector
            if query_embeddings is not None:
                query_vector = query_embeddings[0] if isinstance(query_embeddings, list) else query_embeddings
                # Ensure it's a flat list of floats
                if isinstance(query_vector, list) and len(query_vector) > 0:
                    # Check if it's nested (list of lists)
                    if isinstance(query_vector[0], list):
                        query_vector = query_vector[0]  # Unwrap nested list
                    # Ensure all elements are floats
                    query_vector = [float(x) for x in query_vector]
                elif isinstance(query_vector, np.ndarray):
                    query_vector = query_vector.flatten().tolist()
            elif query_texts is not None and self.embedding_model is not None:
                # Generate embedding for query
                query_embedding = self.embedding_model.encode(query_texts[0])
                if isinstance(query_embedding, np.ndarray):
                    query_vector = query_embedding.flatten().tolist()
                elif isinstance(query_embedding, list):
                    # Ensure it's a flat list
                    if len(query_embedding) > 0 and isinstance(query_embedding[0], list):
                        query_vector = query_embedding[0]
                    else:
                        query_vector = query_embedding
                    # Ensure all elements are floats
                    query_vector = [float(x) for x in query_vector]
                else:
                    query_vector = [float(query_embedding)]
            else:
                raise ValueError("Either query_texts (with embedding_model) or query_embeddings must be provided")
            
            # Build WHERE clause for metadata filtering
            where_clause = ""
            where_params = []
            
            if where:
                conditions = []
                for key, value in where.items():
                    if isinstance(value, dict):
                        # Handle operators like {"$eq": value}
                        if "$eq" in value:
                            conditions.append(f"metadata->>%s = %s")
                            where_params.extend([key, str(value["$eq"])])
                        elif "$ne" in value:
                            conditions.append(f"metadata->>%s != %s")
                            where_params.extend([key, str(value["$ne"])])
                    else:
                        conditions.append(f"metadata->>%s = %s")
                        where_params.extend([key, str(value)])
                
                if conditions:
                    where_clause = "AND " + " AND ".join(conditions)
            
            # Build WHERE clause for document content filtering
            if where_document:
                if "$contains" in where_document:
                    where_clause += " AND text ILIKE %s"
                    where_params.append(f"%{where_document['$contains']}%")
            
            # Execute similarity search query
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    # Use cosine distance (1 - cosine similarity)
                    # ORDER BY embedding <=> %s uses cosine distance operator
                    # Format vector properly for pgvector: convert list to string format '[0.1,0.2,0.3]'
                    if isinstance(query_vector, list):
                        # Convert list to pgvector format: '[0.1,0.2,0.3]' (no spaces, no nested brackets)
                        vector_str = '[' + ','.join(str(float(x)) for x in query_vector) + ']'
                    elif isinstance(query_vector, np.ndarray):
                        vector_str = '[' + ','.join(str(float(x)) for x in query_vector.flatten()) + ']'
                    else:
                        # If already a string, try to parse and reformat
                        vector_str = str(query_vector).replace(' ', '').replace('[[', '[').replace(']]', ']')
                    
                    query = f"""
                        SELECT 
                            chunk_id,
                            text,
                            metadata,
                            1 - (embedding <=> %s::vector) as similarity
                        FROM {collection_name}
                        WHERE 1=1 {where_clause}
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """
                    
                    params = [vector_str, vector_str, n_results] + where_params
                    cur.execute(query, params)
                    
                    results_data = cur.fetchall()
                    
                    # Format results to match ChromaDB format
                    results = {
                        "ids": [[]],
                        "distances": [[]],
                        "documents": [[]],
                        "metadatas": [[]]
                    }
                    
                    for row in results_data:
                        chunk_id, text, metadata, similarity = row
                        # Convert similarity to distance (1 - similarity)
                        distance = 1 - similarity
                        
                        results["ids"][0].append(chunk_id)
                        results["distances"][0].append(float(distance))
                        results["documents"][0].append(text)
                        results["metadatas"][0].append(metadata if isinstance(metadata, dict) else {})
                    
                    return results
            finally:
                self._put_connection(conn)
            
        except Exception as e:
            logger.error(f"Error querying collection '{collection_name}': {e}")
            raise
    
    def delete_collection(self, collection_name: str):
        """Delete a collection (table)."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {collection_name} CASCADE;")
                conn.commit()
                logger.info(f"Deleted collection '{collection_name}'")
        except Exception as e:
            logger.warning(f"Error deleting collection '{collection_name}': {e}")
            conn.rollback()
        finally:
            self._put_connection(conn)
    
    def reset(self):
        """Reset the entire database (delete all collection tables)."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Get all tables that match collection pattern
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '%_corpus'
                """)
                
                tables = [row[0] for row in cur.fetchall()]
                
                for table in tables:
                    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                
                conn.commit()
                logger.info(f"PostgreSQL database reset: deleted {len(tables)} collections")
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            conn.rollback()
            raise
        finally:
            self._put_connection(conn)
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {collection_name};")
                count = cur.fetchone()[0]
                return count
        except Exception as e:
            logger.debug(f"Could not get count for '{collection_name}': {e}")
            return 0
        finally:
            self._put_connection(conn)
    
    def close(self):
        """Close the PostgreSQL connection pool."""
        if hasattr(self, 'pool'):
            self.pool.closeall()
            logger.info("PostgreSQL connection pool closed")
