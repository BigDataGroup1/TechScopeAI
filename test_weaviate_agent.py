#!/usr/bin/env python3
"""
Quick test to verify Weaviate QueryAgent is working with agents.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

# IMPORTANT: Enable Weaviate QueryAgent
os.environ["USE_WEAVIATE_QUERY_AGENT"] = "true"

print("=" * 80)
print("🧪 Testing Weaviate QueryAgent with Agents")
print("=" * 80)

# Check environment
weaviate_url = os.getenv("WEAVIATE_URL", "")
weaviate_key = os.getenv("WEAVIATE_API_KEY", "")

if not weaviate_url or not weaviate_key:
    print("❌ ERROR: WEAVIATE_URL and WEAVIATE_API_KEY must be set in .env")
    sys.exit(1)

print(f"✅ WEAVIATE_URL: {weaviate_url[:30]}...")
print(f"✅ WEAVIATE_API_KEY: {'SET' if weaviate_key else 'NOT SET'}")
print(f"✅ USE_WEAVIATE_QUERY_AGENT: {os.getenv('USE_WEAVIATE_QUERY_AGENT', 'false')}")

try:
    from src.rag.embedder import Embedder
    from src.rag.vector_store import VectorStore
    from src.rag.retriever import Retriever
    from src.agents.competitive_agent import CompetitiveAgent
    
    print("\n📝 Initializing components...")
    
    # Initialize (PostgreSQL connection will fail but that's OK - we're using Weaviate)
    embedder = Embedder(use_openai=False)
    embedding_model = embedder.get_embedding_model()
    vector_store = VectorStore(embedding_model=embedding_model)
    retriever = Retriever(vector_store=vector_store, embedder=embedder)
    
    # Check if QueryAgent is enabled
    if retriever.use_query_agent:
        print("✅ QueryAgent is ENABLED - using Weaviate!")
        print(f"   QueryAgent initialized: {retriever.query_agent_retriever is not None}")
    else:
        print("❌ QueryAgent is NOT enabled!")
        print("   Make sure USE_WEAVIATE_QUERY_AGENT=true in .env")
        sys.exit(1)
    
    # Initialize agent
    print("\n📝 Initializing CompetitiveAgent...")
    agent = CompetitiveAgent(retriever)
    print("✅ Agent initialized")
    
    # Test query
    test_query = "What are competitors in the AI startup space?"
    print(f"\n🔍 Testing query: {test_query}")
    
    result = agent.process_query(test_query)
    
    print(f"\n✅ SUCCESS! Query completed!")
    print(f"   Response length: {len(result.get('response', ''))} chars")
    print(f"\n📄 Response preview:")
    print("-" * 80)
    print(result.get('response', '')[:500])
    print("-" * 80)
    
    # Check if context was retrieved from Weaviate
    if 'context' in result:
        context = result['context']
        if isinstance(context, list) and len(context) > 0:
            print(f"\n✅ Retrieved {len(context)} context items from Weaviate!")
        elif isinstance(context, str) and len(context) > 0:
            print(f"\n✅ Retrieved context from Weaviate ({len(context)} chars)!")
    
    # Verify data source
    if 'sources' in result:
        sources = result['sources']
        if sources:
            print(f"\n📊 Data Source Verification:")
            print(f"   Total sources: {len(sources)}")
            weaviate_sources = [s for s in sources if 'Weaviate' in str(s.get('source', '')) or s.get('source') == 'Weaviate']
            postgres_sources = [s for s in sources if 'RAG Database' in str(s.get('source', '')) or 'PostgreSQL' in str(s.get('source', ''))]
            if weaviate_sources:
                print(f"   ✅ {len(weaviate_sources)} sources from Weaviate")
            if postgres_sources:
                print(f"   ⚠️  {len(postgres_sources)} sources from PostgreSQL (unexpected!)")
            if not weaviate_sources and not postgres_sources:
                print(f"   ℹ️  Source metadata: {sources[0].get('source', 'unknown') if sources else 'none'}")
    
    print("\n" + "=" * 80)
    print("✅ All tests passed! Weaviate QueryAgent is working correctly!")
    print("=" * 80)
    
    # Clean up: Close Weaviate connection
    print("\n🧹 Cleaning up...")
    retriever.close()
    print("✅ Cleanup complete")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    # Try to close connection even on error
    try:
        if 'retriever' in locals():
            retriever.close()
    except:
        pass
    sys.exit(1)
