"""Build RAG index from processed data."""

import logging
import json
from pathlib import Path
from typing import List, Dict
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag.embedder import Embedder
from src.rag.weaviate_store import WeaviateStore

logger = logging.getLogger(__name__)


def build_index(category: str, processed_data_path: Path, batch_size: int = 32):
    """
    Build RAG index for a category.
    
    Args:
        category: Category name (e.g., "pitch")
        processed_data_path: Path to processed data JSON file
        batch_size: Batch size for embedding generation
    """
    logger.info(f"Building RAG index for {category}")
    
    # Load processed data
    if not processed_data_path.exists():
        raise FileNotFoundError(f"Processed data not found: {processed_data_path}")
    
    with open(processed_data_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    if not chunks:
        logger.warning(f"No chunks found in {processed_data_path}")
        return
    
    logger.info(f"Loaded {len(chunks)} chunks")
    
    # Initialize embedder (using free sentence-transformers)
    logger.info("Initializing embedder...")
    embedder = Embedder(use_openai=False)  # Use free embeddings
    dimension = embedder.get_embedding_dimension()
    
    # Initialize vector store (Weaviate only, required)
    logger.info(f"Initializing Weaviate vector store (dimension: {dimension})...")
    vector_store = WeaviateStore(
        category=category,
        dimension=dimension
    )
    logger.info("✅ Using WeaviateStore (Weaviate only, no fallback)")
    
    # Extract texts and metadata
    texts = [chunk['content'] for chunk in chunks]
    metadata = [
        {
            'content': chunk['content'],
            'source': chunk.get('source', 'unknown'),
            'category': chunk.get('category', category),
            **chunk.get('metadata', {})
        }
        for chunk in chunks
    ]
    
    # Generate embeddings in batches
    logger.info("Generating embeddings...")
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = embedder.embed_batch(batch_texts, batch_size=batch_size)
        all_embeddings.append(batch_embeddings)
        logger.info(f"  Processed {min(i+batch_size, len(texts))}/{len(texts)} chunks")
    
    # Combine all embeddings
    import numpy as np
    embeddings = np.vstack(all_embeddings)
    
    # Add to vector store
    logger.info("Adding to vector store...")
    vector_store.add(embeddings, metadata)
    
    # Save
    logger.info("Saving vector store...")
    vector_store.save()
    
    logger.info(f"✅ Built index with {vector_store.get_count()} vectors")


if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Build RAG index from processed data")
    parser.add_argument("--category", default="pitch", help="Category name")
    parser.add_argument("--data", default="data/processed/pitch/processed_chunks.json",
                       help="Path to processed data JSON")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for embeddings")
    
    args = parser.parse_args()
    
    data_path = Path(args.data)
    build_index(args.category, data_path, batch_size=args.batch_size)

