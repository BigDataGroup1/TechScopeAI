# How to Verify Web Search is Working

## Quick Test (Command Line)

Run the test script:
```bash
python test_mcp_web_search.py
```

Expected output:
- `[OK] MCP Client initialized`
- `[OK] Web search successful!`
- `Found X results` with titles, URLs, and relevance scores

## Verify in Streamlit App

### Method 1: Check Logs When Using Agents

1. **Start your Streamlit app:**
   ```bash
   python main.py web
   ```

2. **Ask a question that requires web search** (when RAG has < 3 results):
   - "What are the latest marketing trends for SaaS startups?"
   - "Find me patent information about AI recommendation systems"
   - "What are the best practices for startup hiring?"

3. **Look for these log messages:**
   ```
   INFO: RAG results insufficient, using web search fallback
   INFO: Found X relevant web results for: [your query]
   ```

4. **Check the Sources section** in the chat:
   - Sources should show URLs from web search
   - Each source will be labeled "Cloud SQL Collection" or show web URLs
   - Web search results will have URLs like `https://...`

### Method 2: Test Specific Agents

#### Marketing Agent
Ask: "What are Instagram marketing best practices for B2B SaaS?"

**What to look for:**
- Response includes current/trending information
- Sources section shows web URLs (not just database sources)
- Logs show: `Found X relevant web results`

#### Patent Agent
Ask: "Search for patents related to machine learning recommendation systems"

**What to look for:**
- Response includes patent database references
- Sources include URLs from USPTO, Google Patents, etc.
- Logs show: `Found X relevant web results` or `patent_search` tool usage

#### Team Agent
Ask: "What's the average salary for a startup CTO in 2025?"

**What to look for:**
- Response includes current salary data
- Sources show web URLs with salary information
- Logs show web search activity

### Method 3: Check Database Status

In the Streamlit sidebar, you'll see:
- **Database Status** section
- Should show "Cloud SQL (GCP)" ✅
- When agents use web search, it's a **fallback** - so you'll see:
  - First: RAG search from Cloud SQL
  - Then: Web search if RAG has < 3 results

## What Success Looks Like

✅ **Working correctly:**
- Agents respond with current information
- Sources section shows web URLs
- Logs show "Found X relevant web results"
- No errors in console

❌ **Not working:**
- Agents only return database results
- No web URLs in sources
- Logs show: "Web search not available" or errors
- Responses seem outdated

## Troubleshooting

### If web search isn't working:

1. **Check if `ddgs` is installed:**
   ```bash
   pip install ddgs
   ```

2. **Verify MCP tools are initialized:**
   ```python
   from src.mcp.client import MCPClient
   client = MCPClient()
   print(client.list_tools())  # Should show ['web_search', ...]
   ```

3. **Test web search directly:**
   ```python
   from src.mcp.client import MCPClient
   client = MCPClient()
   result = client.web_search(query="test query", max_results=3)
   print(result)
   ```

4. **Check internet connection:**
   - Web search requires internet access
   - DuckDuckGo API needs to be reachable

5. **Check logs for errors:**
   - Look for `[ERROR]` or `[WARNING]` messages
   - Check if DuckDuckGo API is blocked/filtered

## Expected Behavior

### When RAG has enough results (≥3):
- ✅ Uses Cloud SQL data only
- ✅ No web search needed
- ✅ Sources show "Cloud SQL Collection"

### When RAG has insufficient results (<3):
- ✅ Falls back to web search automatically
- ✅ Combines RAG + web search results
- ✅ Sources show both database and web URLs
- ✅ Logs show: "RAG results insufficient, using web search fallback"

## Quick Verification Commands

```bash
# Test MCP web search directly
python -c "from src.mcp.client import MCPClient; c = MCPClient(); r = c.web_search('startup trends', max_results=2); print('Success!' if r.get('success') else 'Failed:', r.get('error'))"

# Test through an agent
python -c "from src.rag.embedder import Embedder; from src.rag.vector_store import VectorStore; from src.rag.retriever import Retriever; from src.agents.marketing_agent import MarketingAgent; e = Embedder(); vs = VectorStore(embedding_model=e.get_embedding_model()); r = Retriever(vs, e); a = MarketingAgent(r); print('MCP available!' if hasattr(a, 'mcp_client') else 'No MCP')"
```

## Summary

**Web search is working if:**
1. ✅ Test script passes (`test_mcp_web_search.py`)
2. ✅ Agents show web URLs in sources
3. ✅ Logs show "Found X relevant web results"
4. ✅ Responses include current/trending information

**The test script confirmed:**
- ✅ MCP Client initialized
- ✅ Web search tool working
- ✅ Found 3 relevant results
- ✅ Agent integration working
- ✅ All tests passed!

Your web search is **working correctly** via MCP! 🎉

