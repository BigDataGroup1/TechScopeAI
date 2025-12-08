"""Test script to verify MCP web search is working."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp.client import MCPClient
import json

def test_web_search():
    """Test MCP web search tool."""
    print("=" * 60)
    print("Testing MCP Web Search Tool")
    print("=" * 60)
    
    # Initialize MCP client
    print("\n1. Initializing MCP Client...")
    try:
        client = MCPClient()
        print(f"[OK] MCP Client initialized")
        print(f"   Available tools: {client.list_tools()}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize MCP Client: {e}")
        return False
    
    # Test web search
    print("\n2. Testing web search...")
    test_query = "startup marketing trends 2025"
    print(f"   Query: '{test_query}'")
    
    try:
        result = client.web_search(
            query=test_query,
            topic_context="SaaS B2B",
            max_results=3
        )
        
        if result.get("success"):
            results = result.get("results", [])
            print(f"[OK] Web search successful!")
            print(f"   Found {len(results)} results")
            
            if results:
                print("\n   Sample results:")
                for i, res in enumerate(results[:3], 1):
                    print(f"\n   Result {i}:")
                    print(f"   - Title: {res.get('title', 'N/A')[:60]}...")
                    print(f"   - URL: {res.get('url', 'N/A')[:60]}...")
                    print(f"   - Relevance: {res.get('relevance_score', 0):.2f}")
                    print(f"   - Snippet: {res.get('snippet', 'N/A')[:80]}...")
            else:
                print("   [WARNING] No results returned (this might be normal)")
            
            return True
        else:
            print(f"[ERROR] Web search failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error during web search: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_web_search():
    """Test web search through an agent."""
    print("\n" + "=" * 60)
    print("Testing Web Search via Agent")
    print("=" * 60)
    
    try:
        from src.rag.embedder import Embedder
        from src.rag.vector_store import VectorStore
        from src.rag.retriever import Retriever
        from src.agents.marketing_agent import MarketingAgent
        
        print("\n1. Initializing Marketing Agent...")
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        
        agent = MarketingAgent(retriever)
        print("[OK] Marketing Agent initialized")
        
        # Check if MCP client is available
        if hasattr(agent, 'mcp_client'):
            print("[OK] Agent has MCP client")
            print(f"   Available tools: {agent.mcp_client.list_tools()}")
            
            # Test web search through agent
            print("\n2. Testing web search through agent...")
            result = agent.mcp_client.web_search(
                query="startup marketing best practices",
                max_results=2
            )
            
            if result.get("success"):
                print(f"[OK] Agent web search working!")
                print(f"   Found {len(result.get('results', []))} results")
                return True
            else:
                print(f"[ERROR] Agent web search failed: {result.get('error')}")
                return False
        else:
            print("[ERROR] Agent does not have MCP client")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "MCP Web Search Test" + "\n")
    
    # Test 1: Direct MCP tool test
    test1_passed = test_web_search()
    
    # Test 2: Agent integration test
    test2_passed = test_agent_web_search()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Direct MCP Tool Test: {'[PASSED]' if test1_passed else '[FAILED]'}")
    print(f"Agent Integration Test: {'[PASSED]' if test2_passed else '[FAILED]'}")
    
    if test1_passed and test2_passed:
        print("\n[SUCCESS] All tests passed! Web search is working via MCP.")
    else:
        print("\n[WARNING] Some tests failed. Check the output above for details.")
        print("\nCommon issues:")
        print("  - Make sure 'ddgs' package is installed: pip install ddgs")
        print("  - Check your internet connection")
        print("  - Verify MCP tools are properly initialized")

