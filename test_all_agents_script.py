"""
Script to test all agent endpoints with fake data
Run this to verify all agents are working correctly
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
from test_agent_endpoints import (
    PITCH_COMPANY_DATA, PITCH_OUTLINE, PITCH_TEXT_FOR_EVALUATION,
    MARKETING_CONTEXT,
    PATENT_INVENTION_CONTEXT, PATENT_SEARCH_QUERY,
    TEAM_COMPANY_CONTEXT, TEAM_ROLE_CONTEXT,
    POLICY_COMPANY_CONTEXT,
    COMPETITIVE_COMPANY_CONTEXT, COMPETITOR_COMPARISON,
    TEST_QUERIES
)

# Import agents
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.agents.pitch_agent import PitchAgent
from src.agents.marketing_agent import MarketingAgent
from src.agents.patent_agent import PatentAgent
from src.agents.team_agent import TeamAgent
from src.agents.policy_agent import PolicyAgent
from src.agents.competitive_agent import CompetitiveAgent

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_pitch_agent():
    """Test all Pitch Agent endpoints."""
    print_section("TESTING PITCH AGENT")
    
    try:
        # Initialize
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = PitchAgent(retriever)
        
        print("✅ Pitch Agent initialized")
        
        # Test endpoints
        print("\n1. Testing generate_from_details...")
        result = agent.generate_from_details(PITCH_COMPANY_DATA)
        print(f"   ✅ Generated pitch (length: {len(result.get('response', ''))} chars)")
        
        print("\n2. Testing generate_from_outline...")
        result = agent.generate_from_outline(PITCH_OUTLINE, PITCH_COMPANY_DATA)
        print(f"   ✅ Generated pitch from outline (length: {len(result.get('response', ''))} chars)")
        
        print("\n3. Testing generate_slides (normal PPT, skipping Gamma)...")
        # Skip Gamma generation for faster testing - set gamma_only=True to skip
        # Or set GAMMA_API_KEY to test Gamma integration
        test_data = PITCH_COMPANY_DATA.copy()
        test_data["skip_gamma"] = True  # Add flag to skip Gamma if needed
        result = agent.generate_slides(test_data, gamma_only=False)
        print(f"   ✅ Generated {result.get('total_slides', 0)} slides")
        if result.get('gamma_presentation'):
            gamma_status = result['gamma_presentation'].get('success', False)
            print(f"   ℹ️  Gamma generation: {'✅ Success' if gamma_status else '⏭️ Skipped/Failed'}")
        
        print("\n4. Testing generate_elevator_pitch...")
        result = agent.generate_elevator_pitch(PITCH_COMPANY_DATA, duration_seconds=60)
        print(f"   ✅ Generated elevator pitch")
        
        print("\n5. Testing evaluate_pitch...")
        result = agent.evaluate_pitch(PITCH_TEXT_FOR_EVALUATION, PITCH_COMPANY_DATA)
        print(f"   ✅ Evaluated pitch")
        
        print("\n6. Testing process_query...")
        result = agent.process_query(TEST_QUERIES["pitch"][0], PITCH_COMPANY_DATA)
        print(f"   ✅ Processed query: '{TEST_QUERIES['pitch'][0]}'")
        
        print("\n✅ All Pitch Agent endpoints tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Pitch Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_marketing_agent():
    """Test all Marketing Agent endpoints."""
    print_section("TESTING MARKETING AGENT")
    
    try:
        # Initialize
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = MarketingAgent(retriever)
        
        print("✅ Marketing Agent initialized")
        
        print("\n1. Testing generate_instagram_content...")
        result = agent.generate_instagram_content(MARKETING_CONTEXT)
        print(f"   ✅ Generated Instagram content")
        
        print("\n2. Testing generate_linkedin_content...")
        result = agent.generate_linkedin_content(MARKETING_CONTEXT)
        print(f"   ✅ Generated LinkedIn content")
        
        print("\n3. Testing suggest_marketing_strategies...")
        result = agent.suggest_marketing_strategies(MARKETING_CONTEXT)
        print(f"   ✅ Generated marketing strategies")
        
        print("\n4. Testing process_query...")
        result = agent.process_query(TEST_QUERIES["marketing"][0], MARKETING_CONTEXT)
        print(f"   ✅ Processed query: '{TEST_QUERIES['marketing'][0]}'")
        
        print("\n✅ All Marketing Agent endpoints tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Marketing Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_patent_agent():
    """Test all Patent Agent endpoints."""
    print_section("TESTING PATENT AGENT")
    
    try:
        # Initialize
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = PatentAgent(retriever)
        
        print("✅ Patent Agent initialized")
        
        print("\n1. Testing search_patents...")
        result = agent.search_patents(PATENT_SEARCH_QUERY, PATENT_INVENTION_CONTEXT)
        print(f"   ✅ Searched patents")
        
        print("\n2. Testing assess_patentability...")
        result = agent.assess_patentability(
            PATENT_INVENTION_CONTEXT["invention_description"],
            PATENT_INVENTION_CONTEXT
        )
        print(f"   ✅ Assessed patentability")
        
        print("\n3. Testing filing_strategy...")
        result = agent.filing_strategy(PATENT_INVENTION_CONTEXT)
        print(f"   ✅ Generated filing strategy")
        
        print("\n4. Testing prior_art_search...")
        result = agent.prior_art_search(
            PATENT_INVENTION_CONTEXT["invention_description"],
            PATENT_INVENTION_CONTEXT
        )
        print(f"   ✅ Searched prior art")
        
        print("\n5. Testing process_query...")
        result = agent.process_query(TEST_QUERIES["patent"][0], PATENT_INVENTION_CONTEXT)
        print(f"   ✅ Processed query: '{TEST_QUERIES['patent'][0]}'")
        
        print("\n✅ All Patent Agent endpoints tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Patent Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_team_agent():
    """Test all Team Agent endpoints."""
    print_section("TESTING TEAM AGENT")
    
    try:
        # Initialize
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = TeamAgent(retriever)
        
        print("✅ Team Agent initialized")
        
        print("\n1. Testing analyze_team_needs...")
        result = agent.analyze_team_needs(TEAM_COMPANY_CONTEXT, {})
        print(f"   ✅ Analyzed team needs")
        
        print("\n2. Testing get_role_market_data...")
        result = agent.get_role_market_data("Senior Product Manager", "San Francisco, CA", "SaaS", company_context=TEAM_COMPANY_CONTEXT)
        print(f"   ✅ Retrieved role market data")
        
        print("\n3. Testing generate_job_description...")
        result = agent.generate_job_description(
            "Senior Product Manager",
            TEAM_COMPANY_CONTEXT,
            TEAM_ROLE_CONTEXT
        )
        print(f"   ✅ Generated job description")
        
        print("\n4. Testing process_query...")
        result = agent.process_query(TEST_QUERIES["team"][0], TEAM_COMPANY_CONTEXT)
        print(f"   ✅ Processed query: '{TEST_QUERIES['team'][0]}'")
        
        print("\n✅ All Team Agent endpoints tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Team Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_policy_agent():
    """Test all Policy Agent endpoints."""
    print_section("TESTING POLICY AGENT")
    
    try:
        # Initialize
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = PolicyAgent(retriever)
        
        print("✅ Policy Agent initialized")
        
        print("\n1. Testing generate_privacy_policy...")
        result = agent.generate_privacy_policy(POLICY_COMPANY_CONTEXT)
        print(f"   ✅ Generated privacy policy")
        
        print("\n2. Testing generate_terms_of_service...")
        result = agent.generate_terms_of_service(POLICY_COMPANY_CONTEXT)
        print(f"   ✅ Generated terms of service")
        
        print("\n3. Testing check_compliance...")
        result = agent.check_compliance(POLICY_COMPANY_CONTEXT, "privacy")
        print(f"   ✅ Checked compliance")
        
        print("\n4. Testing generate_hr_policies...")
        result = agent.generate_hr_policies(POLICY_COMPANY_CONTEXT)
        print(f"   ✅ Generated HR policies")
        
        print("\n5. Testing process_query...")
        result = agent.process_query(TEST_QUERIES["policy"][0], POLICY_COMPANY_CONTEXT)
        print(f"   ✅ Processed query: '{TEST_QUERIES['policy'][0]}'")
        
        print("\n✅ All Policy Agent endpoints tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Policy Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_competitive_agent():
    """Test all Competitive Agent endpoints."""
    print_section("TESTING COMPETITIVE AGENT")
    
    try:
        # Initialize
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = CompetitiveAgent(retriever)
        
        print("✅ Competitive Agent initialized")
        
        print("\n1. Testing analyze_competitors...")
        result = agent.analyze_competitors(COMPETITIVE_COMPANY_CONTEXT)
        print(f"   ✅ Analyzed competitors")
        
        print("\n2. Testing compare_to_competitors...")
        result = agent.compare_to_competitors(COMPETITIVE_COMPANY_CONTEXT, "Zapier")
        print(f"   ✅ Compared to competitor")
        
        print("\n3. Testing identify_competitive_advantages...")
        result = agent.identify_competitive_advantages(COMPETITIVE_COMPANY_CONTEXT)
        print(f"   ✅ Identified competitive advantages")
        
        print("\n4. Testing process_query...")
        result = agent.process_query(TEST_QUERIES["competitive"][0], COMPETITIVE_COMPANY_CONTEXT)
        print(f"   ✅ Processed query: '{TEST_QUERIES['competitive'][0]}'")
        
        print("\n✅ All Competitive Agent endpoints tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Competitive Agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all agent tests."""
    print("\n" + "="*80)
    print("  TECH SCOPE AI - AGENT ENDPOINT TESTING")
    print("="*80)
    print("\nThis script tests all agent endpoints with fake data.")
    print("Make sure you have:")
    print("  - OPENAI_API_KEY set in .env file")
    print("  - Database connection configured")
    print("  - RAG data processed\n")
    
    results = {}
    
    # Test all agents
    results["pitch"] = test_pitch_agent()
    results["marketing"] = test_marketing_agent()
    results["patent"] = test_patent_agent()
    results["team"] = test_team_agent()
    results["policy"] = test_policy_agent()
    results["competitive"] = test_competitive_agent()
    
    # Summary
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"Total Agents Tested: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    print("\nDetailed Results:")
    for agent_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {agent_name.upper():15} {status}")
    
    if failed == 0:
        print("\n🎉 All agents tested successfully!")
    else:
        print(f"\n⚠️  {failed} agent(s) failed. Check errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

