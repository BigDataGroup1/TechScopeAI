"""
Setup script to initialize PostgreSQL + pgvector and load processed data.

This script:
1. Initializes PostgreSQL vector store with pgvector extension
2. Loads processed JSONL files for each agent
3. Generates embeddings and indexes them in PostgreSQL collections
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Import from same package (handle both module and script execution)
try:
    from .vector_store import VectorStore
    from .embeddings import EmbeddingModel
    from .collections import get_all_collections, CollectionConfig
except ImportError:
    # If running as script, add parent to path
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.rag.vector_store import VectorStore
    from src.rag.embeddings import EmbeddingModel
    from src.rag.collections import get_all_collections, CollectionConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_jsonl(file_path: Path) -> list:
    """Load a JSONL file and return list of dicts."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        return data
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return []


def process_chunk_for_indexing(chunk: Dict[str, Any]) -> tuple:
    """
    Extract text and metadata from a processed chunk.
    
    Returns:
        (text, metadata, id) tuple
    """
    text = chunk.get("text", "")
    metadata = chunk.get("metadata", {})
    chunk_id = chunk.get("chunk_id", chunk.get("id", ""))
    
    # Ensure chunk_id is a string
    if not chunk_id:
        import uuid
        chunk_id = str(uuid.uuid4())
    
    return text, metadata, chunk_id


def index_collection(
    vector_store: VectorStore,
    collection_config: CollectionConfig,
    batch_size: int = 100,
    skip_existing: bool = False
):
    """
    Index a collection from its processed JSONL file.
    
    Args:
        vector_store: VectorStore instance
        collection_config: Collection configuration
        batch_size: Batch size for adding documents
        skip_existing: If True, skip collections that already have data (for parallel mode)
    """
    collection_name = collection_config.name
    processed_path = Path(collection_config.processed_data_path)
    
    logger.info(f"[{collection_name}] Starting indexing...")
    logger.info(f"[{collection_name}] Source: {processed_path}")
    
    # Check if file exists
    if not processed_path.exists():
        logger.warning(f"[{collection_name}] Processed data file not found: {processed_path}")
        return False
    
    # Load processed data
    logger.info(f"[{collection_name}] Loading processed data...")
    chunks = load_jsonl(processed_path)
    
    if not chunks:
        logger.warning(f"[{collection_name}] No data found in {processed_path}")
        return False
    
    logger.info(f"[{collection_name}] Loaded {len(chunks)} chunks")
    
    # Check if collection already has data
    existing_count = vector_store.get_collection_count(collection_name)
    if existing_count > 0:
        if skip_existing:
            logger.info(f"[{collection_name}] Already has {existing_count} documents, skipping...")
            return False
        else:
            logger.info(f"[{collection_name}] Already has {existing_count} documents")
            # Check if reset was requested (via environment variable set during reset)
            if os.getenv('FORCE_RESET') == '1':
                logger.info(f"[{collection_name}] Force reset: deleting existing collection...")
                vector_store.delete_collection(collection_name)
                logger.info(f"[{collection_name}] Deleted existing collection")
            # In non-parallel mode, we can ask interactively (only if not force reset)
            elif not os.getenv('PARALLEL_MODE'):
                try:
                    response = input(f"Delete existing data and re-index {collection_name}? (y/n): ").strip().lower()
                    if response == 'y':
                        vector_store.delete_collection(collection_name)
                        logger.info(f"[{collection_name}] Deleted existing collection")
                    else:
                        logger.info(f"[{collection_name}] Skipping (already indexed)")
                        return False
                except (EOFError, KeyboardInterrupt):
                    # Non-interactive mode (e.g., script running)
                    logger.info(f"[{collection_name}] Skipping (non-interactive mode, use --reset to force re-index)")
                    return False
            else:
                # In parallel mode, skip by default
                logger.info(f"[{collection_name}] Skipping (already indexed, use --reset to re-index)")
                return False
    
    # Process chunks in batches
    texts = []
    metadatas = []
    ids = []
    
    logger.info(f"[{collection_name}] Processing {len(chunks)} chunks in batches of {batch_size}...")
    
    for i, chunk in enumerate(tqdm(chunks, desc=f"[{collection_name}]", leave=False)):
        text, metadata, chunk_id = process_chunk_for_indexing(chunk)
        
        # Skip empty texts
        if not text or not text.strip():
            continue
        
        texts.append(text)
        # Ensure metadata is not empty (ChromaDB requirement)
        if not metadata:
            metadata = {"agent": collection_config.agent_type.value, "source": "processed"}
        metadatas.append(metadata)
        ids.append(f"{collection_name}_{chunk_id}")
        
        # Add batch when full
        if len(texts) >= batch_size:
            try:
                vector_store.add_documents(
                    collection_name=collection_name,
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                texts = []
                metadatas = []
                ids = []
            except Exception as e:
                logger.error(f"[{collection_name}] Error adding batch: {e}")
                texts = []
                metadatas = []
                ids = []
    
    # Add remaining documents
    if texts:
        try:
            vector_store.add_documents(
                collection_name=collection_name,
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            logger.error(f"[{collection_name}] Error adding final batch: {e}")
    
    # Verify indexing
    final_count = vector_store.get_collection_count(collection_name)
    logger.info(f"[{collection_name}] ✓ Indexed {final_count} documents")
    return True


def index_collection_worker(args_tuple: Tuple) -> Tuple[str, bool, Optional[str]]:
    """
    Worker function for parallel indexing.
    Each worker gets its own VectorStore instance for thread safety.
    
    Args:
        args_tuple: (collection_name, collection_config, database_url, batch_size, embedding_model, skip_existing)
    
    Returns:
        (collection_name, success, error_message)
    """
    collection_name, collection_config, database_url, batch_size, embedding_model, skip_existing = args_tuple
    
    # Create a separate VectorStore instance for each thread (thread-safe)
    # Note: EmbeddingModel is shared, but sentence-transformers is thread-safe
    use_local = False
    if database_url and 'localhost:5432' in database_url:
        use_local = True
    
    vector_store = VectorStore(
        database_url=database_url,
        embedding_model=embedding_model,
        use_local=use_local
    )
    
    try:
        success = index_collection(
            vector_store=vector_store,
            collection_config=collection_config,
            batch_size=batch_size,
            skip_existing=skip_existing
        )
        return (collection_name, success, None)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[{collection_name}] Failed: {error_msg}")
        return (collection_name, False, error_msg)


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup RAG infrastructure (PostgreSQL + pgvector + embeddings)")
    parser.add_argument(
        "--collections",
        nargs="+",
        help="Specific collections to index (default: all)",
        choices=["competitors_corpus", "marketing_corpus", "ip_policy_corpus", 
                 "policy_corpus", "job_roles_corpus", "pitch_examples_corpus"]
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset PostgreSQL (delete all collections) before indexing"
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="PostgreSQL database URL (default: from DATABASE_URL env var or localhost)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="Batch size for indexing (default: 200 for CPU parallel processing)"
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of collections to process in parallel (default: 1 = sequential)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip collections that already have data (useful for parallel mode)"
    )
    parser.add_argument(
        "--device",
        choices=["auto", "cuda", "cpu"],
        default="auto",
        help="Device to use for embeddings: 'auto' (detect GPU/CPU), 'cuda' (GPU), 'cpu' (CPU). Default: auto"
    )
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("TechScope AI - RAG Setup")
    logger.info("="*60)
    
    # Set parallel mode environment variable
    if args.parallel > 1:
        os.environ['PARALLEL_MODE'] = '1'
    
    # Initialize embedding model (shared across threads)
    logger.info("\nInitializing embedding model...")
    device = None if args.device == "auto" else args.device
    embedding_model = EmbeddingModel(device=device)
    logger.info(f"Using device: {embedding_model.get_device()}")
    
    # Initialize a temporary vector store for reset/check operations
    logger.info(f"\nInitializing PostgreSQL + pgvector...")
    # Get database URL from argument, environment, or use default
    # Defaults to Cloud SQL unless --database-url is explicitly set to local
    database_url = getattr(args, 'database_url', None)
    use_local = False
    if database_url and 'localhost:5432' in database_url:
        use_local = True
    
    temp_vector_store = VectorStore(
        database_url=database_url,
        embedding_model=embedding_model,
        use_local=use_local
    )
    
    # Reset if requested
    if args.reset:
        logger.warning("Resetting PostgreSQL (deleting all collections)...")
        temp_vector_store.reset()
        # Set environment variable to force re-indexing even if collections exist
        os.environ['FORCE_RESET'] = '1'
    
    # Get collections to index
    all_collections = get_all_collections()
    
    if args.collections:
        collections_to_index = {
            name: config for name, config in all_collections.items()
            if name in args.collections
        }
    else:
        collections_to_index = all_collections
    
    logger.info(f"\nWill index {len(collections_to_index)} collection(s)")
    logger.info(f"Parallel workers: {args.parallel}")
    logger.info(f"Batch size: {args.batch_size}")
    for name in collections_to_index.keys():
        logger.info(f"  - {name}")
    
    # Determine if we should use parallel processing
    use_parallel = args.parallel > 1 and len(collections_to_index) > 1
    
    if use_parallel:
        # Parallel indexing
        logger.info(f"\n{'='*60}")
        logger.info("PARALLEL MODE: Processing collections simultaneously")
        logger.info(f"{'='*60}\n")
        
        max_workers = min(args.parallel, len(collections_to_index))
        
        # Prepare arguments for each worker
        worker_args = [
            (
                name,
                config,
                database_url,
                args.batch_size,
                embedding_model,
                args.skip_existing
            )
            for name, config in collections_to_index.items()
        ]
        
        # Process in parallel
        results = {}
        completed = 0
        total = len(worker_args)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_collection = {
                executor.submit(index_collection_worker, args): args[0]
                for args in worker_args
            }
            
            for future in as_completed(future_to_collection):
                collection_name = future_to_collection[future]
                completed += 1
                try:
                    name, success, error = future.result()
                    results[name] = (success, error)
                    status = "✓" if success else "✗"
                    logger.info(f"\n[{completed}/{total}] {status} {name} {'completed' if success else 'failed'}")
                except Exception as e:
                    logger.error(f"[{collection_name}] Exception: {e}")
                    results[collection_name] = (False, str(e))
        
        # Log results summary
        successful = sum(1 for success, _ in results.values() if success)
        logger.info(f"\n{'='*60}")
        logger.info(f"Parallel processing complete: {successful}/{len(results)} collections indexed successfully")
        logger.info(f"{'='*60}")
        
    else:
        # Sequential indexing (original behavior)
        logger.info(f"\n{'='*60}")
        logger.info("SEQUENTIAL MODE: Processing collections one by one")
        logger.info(f"{'='*60}\n")
        
        for collection_name, collection_config in collections_to_index.items():
            try:
                index_collection(
                    vector_store=temp_vector_store,
                    collection_config=collection_config,
                    batch_size=args.batch_size,
                    skip_existing=args.skip_existing
                )
            except Exception as e:
                logger.error(f"Failed to index {collection_name}: {e}")
                continue
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Setup Complete!")
    logger.info("="*60)
    logger.info("\nCollection counts:")
    
    # Use temp_vector_store for final counts
    use_local = False
    if database_url and 'localhost:5432' in database_url:
        use_local = True
    
    final_vector_store = VectorStore(
        database_url=database_url,
        embedding_model=embedding_model,
        use_local=use_local
    )
    
    for collection_name in collections_to_index.keys():
        count = final_vector_store.get_collection_count(collection_name)
        logger.info(f"  {collection_name}: {count} documents")


if __name__ == "__main__":
    main()

