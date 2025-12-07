#!/usr/bin/env python3
"""Test script for Weaviate local setup."""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag.embedder import Embedder
from src.rag.weaviate_store import WeaviateStore
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_weaviate():
    """Test Weaviate connection and operations."""
    print("=" * 60)
    print("Testing Weaviate Local Setup")
    print("=" * 60)
    
    try:
        # Initialize embedder
        print("\n1. Initializing embedder...")
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        print(f"   ✅ Embedder initialized (dimension: {dimension})")
        
        # Initialize WeaviateStore
        print("\n2. Connecting to Weaviate...")
        vector_store = WeaviateStore(
            category="test",
            dimension=dimension
        )
        print(f"   ✅ Connected to Weaviate at {vector_store.weaviate_url}")
        print(f"   📊 Collection: {vector_store.class_name}")
        
        # Test adding vectors
        print("\n3. Testing add operation...")
        test_embeddings = np.random.rand(5, dimension).astype('float32')
        test_metadata = [
            {
                "content": f"Test content {i+1}",
                "source": "test_script",
                "category": "test",
                "test_id": i+1
            }
            for i in range(5)
        ]
        vector_store.add(test_embeddings, test_metadata)
        print(f"   ✅ Added {len(test_embeddings)} vectors to Weaviate")
        
        # Test search
        print("\n4. Testing search operation...")
        query_embedding = np.random.rand(dimension).astype('float32')
        results = vector_store.search(query_embedding, top_k=3)
        print(f"   ✅ Search completed: {len(results)} results")
        if results:
            print(f"   📄 Top result: {results[0].get('content', 'N/A')}")
            print(f"   📊 Similarity: {results[0].get('similarity_score', 0):.4f}")
        
        # Get count
        print("\n5. Testing get_count...")
        count = vector_store.get_count()
        print(f"   ✅ Vector count in Weaviate: {count}")
        
        # Close connection
        print("\n6. Closing connection...")
        vector_store.close()
        print("   ✅ Connection closed")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Weaviate is working correctly!")
        print("=" * 60)
        return True
        
    except RuntimeError as e:
        print(f"\n❌ Weaviate connection error: {e}")
        print("\n💡 Make sure:")
        print("   1. Docker Desktop is running")
        print("   2. Weaviate is started: ./setup_weaviate_local.sh")
        print("   3. Check logs: docker-compose -f docker-compose.weaviate.yml logs")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_weaviate()
    sys.exit(0 if success else 1)

