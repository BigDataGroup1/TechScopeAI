#!/usr/bin/env python3
"""
Test script to verify Weaviate migration is working correctly.

This script:
1. Connects to PostgreSQL and reads a small sample (10 documents)
2. Connects to Weaviate Cloud
3. Inserts the sample documents
4. Verifies they're actually in Weaviate by querying the count
"""

import os
import sys
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Weaviate imports
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    logger.error("Weaviate client not installed. Install with: pip install weaviate-client")


def get_postgresql_connection():
    """Get PostgreSQL connection."""
    from src.rag.db_config import get_database_url
    
    database_url = get_database_url()
    logger.info(f"Connecting to PostgreSQL...")
    
    conn = psycopg2.connect(database_url, connect_timeout=10)
    logger.info("✅ PostgreSQL connection successful")
    return conn


def get_weaviate_client():
    """Get Weaviate Cloud client."""
    if not WEAVIATE_AVAILABLE:
        raise ImportError("Weaviate client not available")
    
    weaviate_url = os.getenv("WEAVIATE_URL", "")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY", "")
    
    if not weaviate_url or not weaviate_api_key:
        raise ValueError("WEAVIATE_URL and WEAVIATE_API_KEY must be set in .env")
    
    # Normalize URL
    normalized_url = weaviate_url.replace("https://", "").replace("http://", "")
    host = normalized_url.split(":")[0]
    
    # Check if it's Weaviate Cloud
    is_cloud = ".weaviate.cloud" in host or ".weaviate.network" in host
    
    if is_cloud:
        try:
            auth_credentials = weaviate.auth.AuthApiKey(api_key=weaviate_api_key)
        except AttributeError:
            auth_credentials = weaviate_api_key
        
        try:
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=host,
                auth_credentials=auth_credentials
            )
        except AttributeError:
            client = weaviate.connect_to_wcs(
                cluster_url=host,
                auth_credentials=auth_credentials
            )
        logger.info(f"✅ Connected to Weaviate Cloud at {host}")
    else:
        url_parts = normalized_url.split(":")
        host = url_parts[0]
        port = int(url_parts[1]) if len(url_parts) > 1 else 8081
        is_secure = weaviate_url.startswith("https://")
        
        client = weaviate.connect_to_custom(
            http_host=host,
            http_port=port,
            http_secure=is_secure
        )
        logger.info(f"✅ Connected to Weaviate at {host}:{port}")
    
    return client


def read_test_sample(conn, table_name: str, limit: int = 10):
    """Read a small sample from PostgreSQL for testing."""
    documents = []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                SELECT 
                    id,
                    chunk_id,
                    text,
                    embedding::text as embedding_text,
                    metadata,
                    created_at
                FROM {table_name}
                ORDER BY id
                LIMIT %s;
            """, (limit,))
            
            rows = cur.fetchall()
            
            for row in rows:
                # Parse embedding
                embedding_text = row.get('embedding_text', '')
                embedding = []
                
                if embedding_text:
                    try:
                        embedding_str = embedding_text.strip('[]')
                        if embedding_str:
                            embedding = [float(x.strip()) for x in embedding_str.split(',')]
                    except Exception as e:
                        logger.warning(f"Could not parse embedding for {row['chunk_id']}: {e}")
                        continue
                
                # Parse metadata
                metadata = row.get('metadata')
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                elif metadata is None:
                    metadata = {}
                
                documents.append({
                    'id': row['id'],
                    'chunk_id': row['chunk_id'],
                    'text': row['text'],
                    'embedding': embedding,
                    'metadata': metadata,
                    'created_at': str(row['created_at']) if row.get('created_at') else None
                })
            
            return documents
            
    except Exception as e:
        logger.error(f"Error reading sample from {table_name}: {e}")
        return []


def test_migration():
    """Test migration with a small sample."""
    logger.info("=" * 80)
    logger.info("🧪 Testing Weaviate Migration")
    logger.info("=" * 80)
    
    # Check Weaviate availability
    if not WEAVIATE_AVAILABLE:
        logger.error("Weaviate client not installed. Install with: pip install weaviate-client")
        return False
    
    # Connect to PostgreSQL
    try:
        pg_conn = get_postgresql_connection()
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        return False
    
    # Connect to Weaviate
    try:
        weaviate_client = get_weaviate_client()
    except Exception as e:
        logger.error(f"❌ Failed to connect to Weaviate: {e}")
        pg_conn.close()
        return False
    
    try:
        # Get first table for testing
        with pg_conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%_corpus'
                ORDER BY table_name
                LIMIT 1;
            """)
            result = cur.fetchone()
            if not result:
                logger.error("❌ No corpus tables found in PostgreSQL")
                return False
            
            test_table = result[0]
            # Use the same mapping as main script
            collection_mapping = {
                "competitors_corpus": "Competitors_corpus",
                "marketing_corpus": "Marketing_corpus",
                "ip_policy_corpus": "Ip_policy_corpus",
                "policy_corpus": "Policy_corpus",
                "job_roles_corpus": "Job_roles_corpus",
                "pitch_examples_corpus": "Pitch_examples_corpus",
            }
            test_collection = collection_mapping.get(test_table, test_table.title().replace('_', '_'))
        
        logger.info(f"📋 Testing with table: {test_table} → collection: {test_collection}")
        
        # Read test sample
        logger.info("📥 Reading 10 test documents from PostgreSQL...")
        test_docs = read_test_sample(pg_conn, test_table, limit=10)
        
        if not test_docs:
            logger.error("❌ No documents found in PostgreSQL")
            return False
        
        logger.info(f"✅ Read {len(test_docs)} test documents")
        
        # Check if collection exists, create if not
        if not weaviate_client.collections.exists(test_collection):
            logger.info(f"📝 Creating test collection: {test_collection}")
            from weaviate.classes.config import Property, DataType
            
            weaviate_client.collections.create(
                name=test_collection,
                properties=[
                    Property(name="chunk_id", data_type=DataType.TEXT),
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="metadata", data_type=DataType.TEXT),
                    Property(name="created_at", data_type=DataType.TEXT),
                ],
                vectorizer_config=None,
            )
            logger.info(f"✅ Created collection: {test_collection}")
        else:
            logger.info(f"ℹ️  Collection {test_collection} already exists")
        
        # Get initial count
        collection = weaviate_client.collections.get(test_collection)
        try:
            initial_count = collection.aggregate.over_all(total_count=True).total_count
            logger.info(f"📊 Initial object count in Weaviate: {initial_count}")
        except Exception as e:
            logger.warning(f"Could not get initial count: {e}")
            initial_count = 0
        
        # Insert test documents using batch
        logger.info("📤 Inserting test documents into Weaviate...")
        successful = 0
        errors = 0
        
        with collection.batch.dynamic() as batch:
            for doc in test_docs:
                if not doc['embedding'] or len(doc['embedding']) == 0:
                    logger.warning(f"  ⚠️  Skipping {doc['chunk_id']} (no embedding)")
                    continue
                
                metadata_json = json.dumps(doc['metadata']) if doc['metadata'] else "{}"
                
                try:
                    batch.add_object(
                        properties={
                            "chunk_id": doc['chunk_id'],
                            "text": doc['text'],
                            "metadata": metadata_json,
                            "created_at": doc['created_at'] or "",
                        },
                        vector=doc['embedding']
                    )
                    successful += 1
                except Exception as e:
                    errors += 1
                    logger.error(f"  ❌ Error adding {doc['chunk_id']}: {e}")
        
        logger.info(f"✅ Added {successful} objects to batch")
        if errors > 0:
            logger.warning(f"⚠️  {errors} objects had errors")
        
        # Wait a moment for batch to flush
        import time
        time.sleep(2)
        
        # Verify count after insertion
        logger.info("🔍 Verifying objects were inserted...")
        try:
            final_count = collection.aggregate.over_all(total_count=True).total_count
            logger.info(f"📊 Final object count in Weaviate: {final_count}")
            
            expected_count = initial_count + successful
            if final_count >= expected_count:
                logger.info(f"✅ SUCCESS! Objects were inserted correctly!")
                logger.info(f"   Expected: {expected_count}, Actual: {final_count}")
                return True
            else:
                logger.error(f"❌ FAILED! Objects were not inserted correctly!")
                logger.error(f"   Expected: {expected_count}, Actual: {final_count}")
                logger.error(f"   Difference: {expected_count - final_count} objects missing")
                return False
        except Exception as e:
            logger.error(f"❌ Could not verify count: {e}")
            return False
        
    finally:
        pg_conn.close()
        weaviate_client.close()
        logger.info("🔌 Connections closed")


if __name__ == "__main__":
    success = test_migration()
    sys.exit(0 if success else 1)
