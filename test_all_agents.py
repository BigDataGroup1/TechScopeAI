#!/usr/bin/env python3
"""
Test script to verify all agents are working properly.
Run this to check if all agents can be initialized and respond.
"""

import os
import sys
from pathlib import Path

# Fix tokenizers warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.agents.pitch_agent import PitchAgent
from src.agents.competitive_agent import CompetitiveAgent
from src.agents.marketing_agent import MarketingAgent
from src.agents.patent_agent import PatentAgent
from src.agents.policy_agent import PolicyAgent
from src.agents.team_agent import TeamAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.supervisor_agent import SupervisorAgent

def test_agent(agent_name, agent_class, retriever, test_query):
    """Test a single agent."""
    print(f"\n{'='*80}")
    print(f"Testing {agent_name}...")
    print('='*80)
    
    try:
        agent = agent_class(retriever)
        print(f"✅ {agent_name} initialized successfully")
        
        # Test query
        print(f"\n📝 Test Query: {test_query}")
        response = agent.process_query(test_query)
        
        if response and response.get('response'):
            print(f"✅ {agent_name} responded successfully")
            print(f"📄 Response preview: {response['response'][:200]}...")
            return True
        else:
            print(f"⚠️  {agent_name} returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ {agent_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test all agents."""
    print("\n" + "="*80)
    print("🧪 TESTING ALL TECHSCOPEAI AGENTS")
    print("="*80)
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY not found!")
        print("   Please add it to your .env file")
        return
    
    print("\n✅ OpenAI API key found")
    
    # Initialize RAG components
    print("\n📚 Initializing RAG components...")
    try:
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        vector_store = VectorStore(category="pitch", dimension=dimension)
        retriever = Retriever(vector_store, embedder)
        print("✅ RAG components initialized")
    except Exception as e:
        print(f"❌ RAG initialization failed: {e}")
        return
    
    # Test results
    results = {}
    
    # Test Pitch Agent
    results['Pitch Agent'] = test_agent(
        "Pitch Agent",
        PitchAgent,
        retriever,
        "What makes a good pitch deck?"
    )
    
    # Test Competitive Agent
    results['Competitive Agent'] = test_agent(
        "Competitive Agent",
        CompetitiveAgent,
        retriever,
        "How do I analyze my competitors?"
    )
    
    # Test Marketing Agent
    results['Marketing Agent'] = test_agent(
        "Marketing Agent",
        MarketingAgent,
        retriever,
        "How do I create engaging social media content?"
    )
    
    # Test Patent Agent
    results['Patent Agent'] = test_agent(
        "Patent Agent",
        PatentAgent,
        retriever,
        "What is patentability?"
    )
    
    # Test Policy Agent
    results['Policy Agent'] = test_agent(
        "Policy Agent",
        PolicyAgent,
        retriever,
        "What should be in a privacy policy?"
    )
    
    # Test Team Agent
    results['Team Agent'] = test_agent(
        "Team Agent",
        TeamAgent,
        retriever,
        "How do I write a good job description?"
    )
    
    # Test Coordinator Agent
    try:
        coordinator = CoordinatorAgent(retriever)
        print(f"\n✅ Coordinator Agent initialized")
        results['Coordinator Agent'] = True
    except Exception as e:
        print(f"\n❌ Coordinator Agent failed: {e}")
        results['Coordinator Agent'] = False
    
    # Test Supervisor Agent
    try:
        supervisor = SupervisorAgent(retriever)
        print(f"\n✅ Supervisor Agent initialized")
        
        # Register a test agent
        pitch_agent = PitchAgent(retriever)
        supervisor.register_agent("pitch", pitch_agent)
        print("✅ Supervisor Agent registered test agent")
        
        # Test routing
        test_response = supervisor.process_query("What is a pitch deck?")
        if test_response and test_response.get('response'):
            print("✅ Supervisor Agent routing works")
            results['Supervisor Agent'] = True
        else:
            print("⚠️  Supervisor Agent routing returned empty response")
            results['Supervisor Agent'] = False
    except Exception as e:
        print(f"\n❌ Supervisor Agent failed: {e}")
        results['Supervisor Agent'] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for agent_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {agent_name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All agents are working!")
    else:
        print(f"\n⚠️  {total - passed} agent(s) need attention")

if __name__ == "__main__":
    main()

