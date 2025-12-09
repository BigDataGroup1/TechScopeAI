"""
Quick test script for Team Agent only
Tests the fixed get_role_market_data method with company context
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import test data
from test_agent_endpoints import TEAM_COMPANY_CONTEXT, TEAM_ROLE_CONTEXT

# Import Team Agent
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.agents.team_agent import TeamAgent

def test_team_agent():
    """Test Team Agent endpoints."""
    print("\n" + "="*80)
    print("  TESTING TEAM AGENT ONLY")
    print("="*80 + "\n")
    
    try:
        # Initialize
        print("1. Initializing Team Agent...")
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = TeamAgent(retriever)
        print("   ✅ Team Agent initialized\n")
        
        # Test 1: get_role_market_data with company context
        print("2. Testing get_role_market_data WITH company context...")
        print("   Role: Senior Product Manager")
        print("   Location: San Francisco, CA")
        print("   Industry: SaaS")
        print("   Company: AIFlow Solutions (Seed stage)")
        print("   ⏳ This may take a moment...\n")
        
        result = agent.get_role_market_data(
            "Senior Product Manager", 
            "San Francisco, CA", 
            "SaaS",
            company_context=TEAM_COMPANY_CONTEXT
        )
        
        print(f"   ✅ Retrieved role market data")
        print(f"   Response length: {len(result.get('response', ''))} chars")
        print(f"   Sources: {len(result.get('sources', []))}")
        print(f"\n   📊 Market Data Preview:")
        preview = result.get('response', '')[:300]
        print(f"   {preview}...\n")
        
        # Test 2: get_role_market_data without company context (should still work)
        print("3. Testing get_role_market_data WITHOUT company context...")
        result2 = agent.get_role_market_data(
            "Senior Product Manager", 
            "Remote", 
            "SaaS"
        )
        print(f"   ✅ Retrieved role market data (no company context)")
        print(f"   Response length: {len(result2.get('response', ''))} chars\n")
        
        # Test 3: analyze_team_needs
        print("4. Testing analyze_team_needs...")
        result3 = agent.analyze_team_needs(TEAM_COMPANY_CONTEXT, {})
        print(f"   ✅ Analyzed team needs")
        print(f"   Response length: {len(result3.get('response', ''))} chars\n")
        
        # Test 4: generate_job_description
        print("5. Testing generate_job_description...")
        result4 = agent.generate_job_description(
            "Senior Product Manager",
            TEAM_COMPANY_CONTEXT,
            {},
            TEAM_ROLE_CONTEXT
        )
        print(f"   ✅ Generated job description")
        print(f"   Response length: {len(result4.get('response', ''))} chars\n")
        
        print("="*80)
        print("✅ ALL TEAM AGENT TESTS PASSED!")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Team Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_team_agent()
    sys.exit(0 if success else 1)


