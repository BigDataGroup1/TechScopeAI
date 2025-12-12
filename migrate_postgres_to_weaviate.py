#!/usr/bin/env python3
"""
Migration script to migrate data from PostgreSQL + pgvector to Weaviate Cloud.

This script:
1. Connects to PostgreSQL and reads all collections
2. Connects to Weaviate Cloud
3. Creates Weaviate collections with proper schema
4. Migrates all documents with embeddings and metadata
"""

import os
import sys
import logging
import json
import time
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
import requests

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
    from weaviate.classes.config import Configure, Property, DataType
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    logger.error("Weaviate client not installed. Install with: pip install weaviate-client")

# Collection mapping: PostgreSQL table -> Weaviate collection (PascalCase)
COLLECTION_MAPPING = {
    "competitors_corpus": "Competitors_corpus",
    "marketing_corpus": "Marketing_corpus",
    "ip_policy_corpus": "Ip_policy_corpus",
    "policy_corpus": "Policy_corpus",
    "job_roles_corpus": "Job_roles_corpus",
    "pitch_examples_corpus": "Pitch_examples_corpus",
}


def get_postgresql_connection():
    """Get PostgreSQL connection."""
    from src.rag.db_config import get_database_url
    
    # Try to get database URL
    try:
        database_url = get_database_url()
    except Exception as e:
        logger.error(f"Failed to get database URL: {e}")
        logger.info("\n💡 Options to fix:")
        logger.info("   1. Start Cloud SQL Proxy: ./start_proxy_simple.sh")
        logger.info("   2. Set DATABASE_URL in .env with direct connection")
        logger.info("   3. Set CLOUD_SQL_PASSWORD and ensure proxy is running")
        raise
    
    logger.info(f"Connecting to PostgreSQL: {database_url.split('@')[-1] if '@' in database_url else 'local'}")
    
    try:
        conn = psycopg2.connect(database_url, connect_timeout=10)
        # Test connection
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
        logger.info("✅ PostgreSQL connection successful")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        logger.info("\n💡 Troubleshooting:")
        logger.info("   1. If using Cloud SQL Proxy, ensure it's running:")
        logger.info("      ./start_proxy_simple.sh")
        logger.info("   2. Check your .env file has correct credentials:")
        logger.info("      - CLOUD_SQL_PASSWORD")
        logger.info("      - Or DATABASE_URL for direct connection")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        raise


def get_weaviate_client():
    """Get Weaviate Cloud client."""
    if not WEAVIATE_AVAILABLE:
        raise ImportError("Weaviate client not available")
    
    weaviate_url = os.getenv("WEAVIATE_URL", "")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY", "")
    
    if not weaviate_url or not weaviate_api_key:
        raise ValueError("WEAVIATE_URL and WEAVIATE_API_KEY must be set in .env")
    
    if weaviate_api_key == "your_api_key_here":
        raise ValueError("Please set a valid WEAVIATE_API_KEY in .env")
    
    # Normalize URL (remove protocol if present)
    normalized_url = weaviate_url.replace("https://", "").replace("http://", "")
    url_parts = normalized_url.split(":")
    host = url_parts[0]
    
    # Check if it's Weaviate Cloud
    is_cloud = ".weaviate.cloud" in host or ".weaviate.network" in host
    
    if is_cloud:
        # Try to use weaviate.auth if available
        try:
            auth_credentials = weaviate.auth.AuthApiKey(api_key=weaviate_api_key)
        except AttributeError:
            auth_credentials = weaviate_api_key
        
        # Use connect_to_weaviate_cloud (new) or connect_to_wcs (deprecated)
        try:
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=host,
                auth_credentials=auth_credentials
            )
        except AttributeError:
            # Fallback to deprecated method
            client = weaviate.connect_to_wcs(
                cluster_url=host,
                auth_credentials=auth_credentials
            )
        logger.info(f"✅ Connected to Weaviate Cloud at {host}")
    else:
        # Local or custom Weaviate
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


def get_postgresql_tables(conn) -> List[str]:
    """Get list of all PostgreSQL tables (collections)."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%_corpus'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
    return tables


def get_collection_count(conn, table_name: str) -> int:
    """Get total count of documents in a collection."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as count FROM {table_name};")
            result = cur.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Error getting count for {table_name}: {e}")
        return 0


def read_postgresql_collection_chunk(conn, table_name: str, last_id: Optional[int] = None, batch_size: int = 500) -> List[Dict[str, Any]]:
    """
    Read a chunk of documents from PostgreSQL using cursor-based pagination.
    This uses ID-based pagination which is much faster than OFFSET for large datasets.
    
    Args:
        conn: PostgreSQL connection
        table_name: Table name to read from
        last_id: Last ID from previous chunk (None for first chunk)
        batch_size: Number of documents to fetch
        
    Returns:
        List of documents with their data
    """
    documents = []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Use cursor-based pagination (ID > last_id) instead of OFFSET
            # This is much faster for large datasets
            if last_id is None:
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
                """, (batch_size,))
            else:
                cur.execute(f"""
                    SELECT 
                        id,
                        chunk_id,
                        text,
                        embedding::text as embedding_text,
                        metadata,
                        created_at
                    FROM {table_name}
                    WHERE id > %s
                    ORDER BY id
                    LIMIT %s;
                """, (last_id, batch_size))
            
            rows = cur.fetchall()
            
            for row in rows:
                # Convert embedding from PostgreSQL vector format to list
                embedding_text = row.get('embedding_text', '')
                embedding = []
                
                if embedding_text:
                    try:
                        # Parse string format: '[0.1,0.2,0.3]'
                        embedding_str = embedding_text.strip('[]')
                        if embedding_str:
                            embedding = [float(x.strip()) for x in embedding_str.split(',')]
                    except Exception as e:
                        logger.warning(f"Could not parse embedding for {row['chunk_id']}: {e}")
                        continue
                else:
                    # Try direct embedding field if text conversion failed
                    embedding_raw = row.get('embedding')
                    if embedding_raw:
                        if isinstance(embedding_raw, str):
                            embedding = [float(x) for x in embedding_raw.strip('[]').split(',')]
                        elif isinstance(embedding_raw, (list, np.ndarray)):
                            embedding = [float(x) for x in embedding_raw]
                
                # Parse metadata JSON
                metadata = row.get('metadata')
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                elif metadata is None:
                    metadata = {}
                elif hasattr(metadata, '__dict__'):
                    metadata = dict(metadata)
                
                documents.append({
                    'id': row['id'],  # Store DB ID for cursor pagination
                    'chunk_id': row['chunk_id'],
                    'text': row['text'],
                    'embedding': embedding,
                    'metadata': metadata,
                    'created_at': str(row['created_at']) if row.get('created_at') else None
                })
            
            return documents
            
    except Exception as e:
        logger.error(f"Error reading chunk from {table_name}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return []


def create_weaviate_collection(client, collection_name: str, vectorizer: Optional[str] = None):
    """Create a Weaviate collection with proper schema."""
    logger.info(f"Creating Weaviate collection: {collection_name}")
    
    # Check if collection already exists
    if client.collections.exists(collection_name):
        logger.warning(f"  Collection {collection_name} already exists. Skipping creation.")
        return
    
    # Define properties for the collection
    # Note: metadata is stored as TEXT (JSON string) because Weaviate requires
    # nested properties for OBJECT type, but our metadata is dynamic JSON
    properties = [
        Property(name="chunk_id", data_type=DataType.TEXT, description="Unique document chunk identifier"),
        Property(name="text", data_type=DataType.TEXT, description="Document text content"),
        Property(name="metadata", data_type=DataType.TEXT, description="Document metadata (JSON string)"),
        Property(name="created_at", data_type=DataType.TEXT, description="Creation timestamp"),
    ]
    
    # Create collection with custom vectors (no vectorizer)
    # We provide our own embeddings from PostgreSQL
    try:
        client.collections.create(
            name=collection_name,
            properties=properties,
            vectorizer_config=None,  # No vectorizer - we provide vectors
        )
        logger.info(f"✅ Created collection: {collection_name}")
    except Exception as e:
        logger.error(f"❌ Failed to create collection {collection_name}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        raise


def save_checkpoint(pg_table: str, last_id: int, checkpoint_dir: Path):
    """Save migration checkpoint to resume later."""
    checkpoint_dir.mkdir(exist_ok=True)
    checkpoint_file = checkpoint_dir / f"{pg_table}.json"
    checkpoint_data = {
        'table': pg_table,
        'last_id': last_id,
        'timestamp': time.time()
    }
    checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2))
    logger.debug(f"💾 Checkpoint saved: {pg_table} at last_id {last_id}")


def load_checkpoint(pg_table: str, checkpoint_dir: Path) -> Optional[int]:
    """Load migration checkpoint to resume from."""
    checkpoint_file = checkpoint_dir / f"{pg_table}.json"
    if checkpoint_file.exists():
        try:
            data = json.loads(checkpoint_file.read_text())
            if data.get('table') == pg_table and 'last_id' in data:
                last_id = data['last_id']
                logger.info(f"📂 Resuming {pg_table} from checkpoint: last_id={last_id}")
                return last_id
        except Exception as e:
            logger.warning(f"⚠️  Could not load checkpoint: {e}")
    return None


def migrate_collection(
    conn,
    client,
    pg_table: str,
    weaviate_collection: str,
    chunk_size: int = 500,
    insert_batch_size: int = 100,
    checkpoint_dir: Optional[Path] = None,
    resume: bool = False
):
    """
    Migrate a single collection from PostgreSQL to Weaviate using streaming.
    Processes data in chunks to avoid loading everything into memory.
    
    Args:
        conn: PostgreSQL connection
        client: Weaviate client
        pg_table: PostgreSQL table name
        weaviate_collection: Weaviate collection name
        chunk_size: Number of documents to read per chunk from PostgreSQL
        insert_batch_size: Number of documents to insert per batch to Weaviate
        checkpoint_dir: Directory to save checkpoints (optional)
        resume: Whether to resume from checkpoint if available
    """
    logger.info("=" * 80)
    logger.info(f"Migrating: {pg_table} → {weaviate_collection}")
    logger.info("=" * 80)
    
    # Get total count (only once, not before every operation)
    total_count = get_collection_count(conn, pg_table)
    if total_count == 0:
        logger.warning(f"  No documents to migrate for {pg_table}")
        return 0
    
    logger.info(f"  Found {total_count:,} documents to migrate")
    logger.info(f"  Processing in chunks of {chunk_size} documents...")
    
    # Create Weaviate collection (only once)
    create_weaviate_collection(client, weaviate_collection)
    
    # Get collection object (only once)
    collection = client.collections.get(weaviate_collection)
    
    # Load checkpoint if resuming (checkpoint_dir is always available now)
    last_id = None
    if resume and checkpoint_dir:
        last_id = load_checkpoint(pg_table, checkpoint_dir)
        if last_id:
            logger.info(f"  🔄 Resuming from last_id={last_id}")
        else:
            logger.info(f"  ℹ️  No checkpoint found, starting from beginning")
    
    # Stream and process documents in chunks
    inserted_count = 0
    chunk_number = 0
    start_time = time.time()
    last_checkpoint_time = start_time
    
    try:
        while True:
            # Read next chunk from PostgreSQL (streaming - doesn't load everything)
            chunk_start = time.time()
            documents = read_postgresql_collection_chunk(conn, pg_table, last_id=last_id, batch_size=chunk_size)
            
            if not documents:
                logger.info(f"  No more documents to process")
                break
            
            chunk_read_time = time.time() - chunk_start
            logger.info(f"  📥 Read chunk {chunk_number + 1}: {len(documents)} documents ({chunk_read_time:.2f}s)")
            
            # Use Weaviate client's batch import method (proper way to insert)
            # This ensures objects are actually committed to Weaviate
            try:
                with collection.batch.dynamic() as batch:
                    batch_errors = 0
                    successful_adds = 0
                    skipped = 0
                    
                    for doc in documents:
                        # Prepare Weaviate object
                        metadata_dict = doc.get('metadata', {})
                        if not isinstance(metadata_dict, dict):
                            metadata_dict = {}
                        metadata_json = json.dumps(metadata_dict) if metadata_dict else "{}"
                        
                        weaviate_obj = {
                            "chunk_id": doc['chunk_id'],
                            "text": doc['text'],
                            "metadata": metadata_json,
                            "created_at": doc['created_at'] or "",
                        }
                        
                        # Get embedding
                        vector = doc['embedding']
                        
                        # Ensure vector is a list of floats
                        if isinstance(vector, np.ndarray):
                            vector = vector.tolist()
                        elif not vector or len(vector) == 0:
                            skipped += 1
                            logger.warning(f"  Empty embedding for {doc['chunk_id']}, skipping...")
                            continue
                        
                        vector = [float(x) for x in vector]
                        
                        # Add to batch
                        try:
                            batch.add_object(
                                properties=weaviate_obj,
                                vector=vector
                            )
                            successful_adds += 1
                        except Exception as e:
                            batch_errors += 1
                            if batch_errors <= 3:  # Log first 3 errors
                                logger.error(f"  ❌ Error adding object to batch: {e}")
                            
                            # If too many errors, stop
                            if batch_errors > 10:
                                logger.error(f"  ❌ Too many batch errors ({batch_errors}), stopping batch")
                                break
                    
                    # Batch is automatically flushed when exiting context manager
                    # Log summary
                    if batch_errors > 0:
                        logger.warning(f"  ⚠️  {batch_errors} objects had errors during batch add")
                    if skipped > 0:
                        logger.info(f"  ℹ️  {skipped} objects skipped (empty embeddings)")
                    
                    # Count successful inserts (objects that were added to batch)
                    inserted_count += successful_adds
                    
                    # Progress update
                    progress_pct = (inserted_count / total_count * 100) if total_count > 0 else 0
                    elapsed = time.time() - start_time
                    rate = inserted_count / elapsed if elapsed > 0 else 0
                    remaining = (total_count - inserted_count) / rate if rate > 0 else 0
                    
                    logger.info(f"  ✅ Inserted {inserted_count:,}/{total_count:,} ({progress_pct:.1f}%) | "
                              f"Rate: {rate:.0f} docs/s | ETA: {remaining/60:.1f}m")
                    
                    # Verify insertion by checking collection count periodically
                    if chunk_number % 10 == 0:
                        try:
                            actual_count = collection.aggregate.over_all(total_count=True).total_count
                            logger.info(f"  🔍 Verification: Weaviate reports {actual_count} objects in collection")
                            if actual_count < inserted_count:
                                logger.warning(f"  ⚠️  WARNING: Expected {inserted_count} but Weaviate shows {actual_count}!")
                        except Exception as e:
                            logger.debug(f"  Could not verify count: {e}")
                    
            except Exception as e:
                error_msg = str(e).lower()
                logger.error(f"  ❌ Error in batch insert: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                
                # Check if it's a 503 error - wait and retry
                is_503_error = "503" in str(e) or "service unavailable" in error_msg
                if is_503_error:
                    logger.warning(f"  💡 503 error detected. Waiting 30 seconds before retrying...")
                    time.sleep(30)
                    # Retry this chunk
                    continue
                
                # For other errors, log and continue
                logger.warning(f"  ⚠️  Continuing with next chunk after error...")
            
            # Update last_id for next chunk (cursor-based pagination)
            last_id = max(doc['id'] for doc in documents)
            chunk_number += 1
            
            # Save checkpoint every 5 minutes or every 10 chunks
            if checkpoint_dir and (time.time() - last_checkpoint_time > 300 or chunk_number % 10 == 0):
                save_checkpoint(pg_table, last_id, checkpoint_dir)
                last_checkpoint_time = time.time()
            
            # Free memory immediately after processing chunk
            del documents
            gc.collect()
            
            # Small delay to prevent overwhelming the database
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        # Save checkpoint on interrupt
        logger.warning(f"\n⚠️  Migration interrupted by user")
        if checkpoint_dir and last_id:
            save_checkpoint(pg_table, last_id, checkpoint_dir)
            logger.info(f"💾 Checkpoint saved at last_id={last_id}. Resume with --resume")
        # Re-raise to let main() handle it
        raise
    finally:
        # Verify final count
        try:
            actual_count = collection.aggregate.over_all(total_count=True).total_count
            logger.info(f"  🔍 Final verification: Weaviate reports {actual_count} objects in collection")
            if actual_count != inserted_count:
                logger.warning(f"  ⚠️  WARNING: Script counted {inserted_count} but Weaviate shows {actual_count}!")
        except Exception as e:
            logger.warning(f"  Could not verify final count: {e}")
    
    # Clear checkpoint on successful completion
    if checkpoint_dir:
        checkpoint_file = checkpoint_dir / f"{pg_table}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            logger.debug(f"🗑️  Checkpoint cleared for {pg_table}")
    
    elapsed_total = time.time() - start_time
    rate = inserted_count / elapsed_total if elapsed_total > 0 else 0
    logger.info(f"✅ Successfully migrated {inserted_count:,} documents to {weaviate_collection}")
    logger.info(f"   Total time: {elapsed_total/60:.1f} minutes | Average rate: {rate:.0f} docs/s")
    return inserted_count


def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate PostgreSQL to Weaviate')
    parser.add_argument('--resume', action='store_true', 
                       help='Resume from checkpoint if available')
    parser.add_argument('--checkpoint-dir', type=str, default='.migration_checkpoints',
                       help='Directory for checkpoint files (default: .migration_checkpoints)')
    parser.add_argument('--chunk-size', type=int, default=500,
                       help='Number of documents per chunk from PostgreSQL (default: 500)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of documents per batch to Weaviate (default: 100 for paid plans)')
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("🚀 PostgreSQL to Weaviate Migration (Optimized Streaming)")
    logger.info("=" * 80)
    logger.info(f"Chunk size: {args.chunk_size} | Batch size: {args.batch_size}")
    logger.info(f"Resume mode: {args.resume}")
    logger.info("=" * 80)
    
    # Check Weaviate availability
    if not WEAVIATE_AVAILABLE:
        logger.error("Weaviate client not installed. Install with: pip install weaviate-client")
        sys.exit(1)
    
    # Check environment variables
    logger.info("\n🔍 Checking environment variables...")
    weaviate_url = os.getenv("WEAVIATE_URL", "")
    weaviate_key = os.getenv("WEAVIATE_API_KEY", "")
    
    if not weaviate_url:
        logger.error("❌ WEAVIATE_URL not set in .env")
        sys.exit(1)
    if not weaviate_key or weaviate_key == "your_api_key_here":
        logger.error("❌ WEAVIATE_API_KEY not set or invalid in .env")
        sys.exit(1)
    
    logger.info(f"   ✅ WEAVIATE_URL: {weaviate_url.split('.')[0] if '.' in weaviate_url else weaviate_url[:20]}...")
    logger.info(f"   ✅ WEAVIATE_API_KEY: {'***SET***' if weaviate_key else 'NOT SET'}")
    
    # Connect to PostgreSQL (only once, no repeated checks)
    logger.info("\n📊 Connecting to PostgreSQL...")
    logger.info("   💡 If connection fails, ensure Cloud SQL Proxy is running: ./start_proxy_simple.sh")
    try:
        pg_conn = get_postgresql_connection()
    except Exception as e:
        logger.error(f"\n❌ Failed to connect to PostgreSQL: {e}")
        logger.info("\n📝 To fix this:")
        logger.info("   1. Make sure Cloud SQL Proxy is running:")
        logger.info("      ./start_proxy_simple.sh")
        logger.info("   2. Or set DATABASE_URL in .env for direct connection")
        sys.exit(1)
    
    # Connect to Weaviate (only once)
    logger.info("\n🔗 Connecting to Weaviate...")
    try:
        weaviate_client = get_weaviate_client()
    except Exception as e:
        logger.error(f"Failed to connect to Weaviate: {e}")
        pg_conn.close()
        sys.exit(1)
    
    # Setup checkpoint directory - ALWAYS create it so checkpoints are saved
    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(exist_ok=True)  # Always create, not just when resuming
    
    try:
        # Get PostgreSQL tables (only once)
        logger.info("\n📋 Discovering PostgreSQL collections...")
        pg_tables = get_postgresql_tables(pg_conn)
        logger.info(f"Found {len(pg_tables)} collections: {', '.join(pg_tables)}")
        
        if not pg_tables:
            logger.warning("No collections found in PostgreSQL!")
            return
        
        # Migrate each collection
        total_migrated = 0
        for pg_table in pg_tables:
            if pg_table in COLLECTION_MAPPING:
                weaviate_collection = COLLECTION_MAPPING[pg_table]
                try:
                    count = migrate_collection(
                        pg_conn, 
                        weaviate_client, 
                        pg_table, 
                        weaviate_collection,
                        chunk_size=args.chunk_size,
                        insert_batch_size=args.batch_size,
                        checkpoint_dir=checkpoint_dir,
                        resume=args.resume
                    )
                    total_migrated += count
                except KeyboardInterrupt:
                    logger.warning(f"\n⚠️  Migration interrupted by user")
                    if checkpoint_dir:
                        logger.info(f"💾 Progress saved. Resume with: --resume")
                    break
                except Exception as e:
                    logger.error(f"Failed to migrate {pg_table}: {e}")
                    import traceback
                    traceback.print_exc()
                    if checkpoint_dir:
                        logger.info(f"💾 Progress saved. Resume with: --resume")
                    continue
            else:
                logger.warning(f"Skipping {pg_table} (not in COLLECTION_MAPPING)")
        
        logger.info("=" * 80)
        logger.info(f"✅ Migration Complete! Migrated {total_migrated:,} total documents")
        logger.info("=" * 80)
    
    finally:
        # Close connections
        pg_conn.close()
        weaviate_client.close()
        logger.info("\n🔌 Connections closed")


if __name__ == "__main__":
    main()

