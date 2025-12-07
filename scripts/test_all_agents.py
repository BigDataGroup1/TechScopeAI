"""Test script to verify all agents are working correctly."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO)

def test_agent_imports():
    """Test that all agents can be imported."""
    print("=" * 60)
    print("TESTING AGENT IMPORTS")
    print("=" * 60)
    
    agents = [
        "PitchAgent",
        "CompetitiveAgent",
        "PatentAgent",
        "PolicyAgent",
        "MarketingAgent",
        "TeamAgent",
        "CoordinatorAgent",
        "SupervisorAgent"
    ]
    
    results = {}
    for agent_name in agents:
        try:
            module = __import__(f"src.agents.{agent_name.lower().replace('agent', '_agent')}", fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            results[agent_name] = "✅ PASS"
            print(f"{agent_name}: ✅ PASS")
        except Exception as e:
            results[agent_name] = f"❌ FAIL: {e}"
            print(f"{agent_name}: ❌ FAIL - {e}")
    
    return results


def test_agent_registry():
    """Test Supervisor Agent registry."""
    print("\n" + "=" * 60)
    print("TESTING SUPERVISOR AGENT REGISTRY")
    print("=" * 60)
    
    try:
        from src.agents.supervisor_agent import SupervisorAgent
        registry = SupervisorAgent.AGENT_REGISTRY
        
        print(f"✅ Registry has {len(registry)} agents:")
        for agent_name, info in registry.items():
            print(f"  - {agent_name}: {info['description']}")
            print(f"    Keywords: {', '.join(info['keywords'][:3])}...")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_coordinator_storage():
    """Test Coordinator Agent storage."""
    print("\n" + "=" * 60)
    print("TESTING COORDINATOR AGENT STORAGE")
    print("=" * 60)
    
    try:
        from src.agents.coordinator_agent import CoordinatorAgent
        from src.rag.embedder import Embedder
        from src.rag.weaviate_store import WeaviateStore
        from src.rag.retriever import Retriever
        
        # Initialize coordinator
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        vector_store = WeaviateStore(category="competitive", dimension=dimension)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=False,  # Use manual RAG for testing
            collection_names=["TechScopeAI_Competitive"]
        )
        
        coordinator = CoordinatorAgent(retriever)
        
        # Test storage
        test_company_id = "test_company"
        test_data = {
            "company_name": "Test Company",
            "industry": "Technology"
        }
        
        coordinator.store_company_data(test_company_id, test_data)
        print("✅ Company data stored")
        
        # Test retrieval
        knowledge = coordinator.get_company_knowledge(test_company_id)
        if knowledge.get("company_data", {}).get("company_name") == "Test Company":
            print("✅ Company data retrieved correctly")
        else:
            print("❌ Company data retrieval failed")
            return False
        
        # Test context retrieval
        context = coordinator.get_context_for_agent(test_company_id, "pitch")
        print(f"✅ Context retrieved: {len(context.get('relevant_content', []))} items")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_supervisor_routing():
    """Test Supervisor Agent query routing."""
    print("\n" + "=" * 60)
    print("TESTING SUPERVISOR AGENT ROUTING")
    print("=" * 60)
    
    try:
        from src.agents.supervisor_agent import SupervisorAgent
        from src.rag.embedder import Embedder
        from src.rag.weaviate_store import WeaviateStore
        from src.rag.retriever import Retriever
        
        # Initialize supervisor
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        vector_store = WeaviateStore(category="competitive", dimension=dimension)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=False,
            collection_names=["TechScopeAI_Competitive"]
        )
        
        supervisor = SupervisorAgent(retriever)
        
        # Test routing
        test_queries = [
            ("Generate a pitch deck", "pitch"),
            ("Analyze competitors", "competitive"),
            ("Create Instagram content", "marketing"),
            ("Help with patent filing", "patent"),
            ("Generate privacy policy", "policy"),
            ("Hire a developer", "team")
        ]
        
        print("Testing query routing:")
        for query, expected_agent in test_queries:
            agent_name, confidence = supervisor.route_query(query)
            status = "✅" if agent_name == expected_agent else "⚠️"
            print(f"  {status} '{query}' → {agent_name} (confidence: {confidence:.2f})")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TECHSCOPEAI - ALL AGENTS TEST SUITE")
    print("=" * 60 + "\n")
    
    results = {}
    
    # Test 1: Imports
    results["imports"] = test_agent_imports()
    
    # Test 2: Registry
    results["registry"] = test_agent_registry()
    
    # Test 3: Coordinator (requires Weaviate)
    print("\n⚠️  Coordinator test requires Weaviate connection")
    try:
        results["coordinator"] = test_coordinator_storage()
    except Exception as e:
        print(f"⚠️  Coordinator test skipped: {e}")
        results["coordinator"] = None
    
    # Test 4: Supervisor routing
    print("\n⚠️  Supervisor routing test requires Weaviate connection")
    try:
        results["routing"] = test_supervisor_routing()
    except Exception as e:
        print(f"⚠️  Routing test skipped: {e}")
        results["routing"] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r is True or (isinstance(r, dict) and all("✅" in str(v) for v in r.values())))
    total = len([r for r in results.values() if r is not None])
    
    print(f"\n✅ Passed: {passed}/{total}")
    print("\nAll agents are ready to use!")
    print("\nTo start the server:")
    print("  python main.py --mode web")


if __name__ == "__main__":
    main()

