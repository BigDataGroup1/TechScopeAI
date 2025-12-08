# MCP Server Implementation

## Overview

The MCP (Model Context Protocol) server has been successfully implemented for TechScopeAI. This provides a standardized way for agents to access external tools like web search, image search, patent search, and content extraction.

## Architecture

```
src/mcp/
├── __init__.py              # Exports MCPServer and MCPClient
├── server.py                 # MCP server implementation
├── client.py                 # MCP client wrapper for agents
└── tools/
    ├── __init__.py
    ├── web_search.py         # Web search tool (DuckDuckGo)
    ├── image_search.py       # Image search tool (Pexels/Unsplash)
    ├── patent_search.py      # Patent search tool (specialized)
    └── content_extractor.py  # Web content extraction tool
```

## Tools Implemented

### 1. Web Search Tool (`web_search`)
- **Purpose**: Search the web using DuckDuckGo
- **Features**:
  - Relevance scoring
  - Topic context filtering
  - Configurable max results
- **Usage**: Used by all agents as fallback when RAG doesn't have enough results

### 2. Image Search Tool (`image_search`)
- **Purpose**: Search for professional images for pitch deck slides
- **Features**:
  - Supports Pexels and Unsplash APIs
  - Image caching
  - Professional/business keyword filtering
- **Usage**: Used by PitchAgent for slide images

### 3. Patent Search Tool (`patent_search`)
- **Purpose**: Specialized patent and prior art search
- **Features**:
  - Patent database domain detection
  - Enhanced patent-specific queries
  - Patent relevance boosting
- **Usage**: Used by PatentAgent for patent searches

### 4. Content Extractor Tool (`content_extractor`)
- **Purpose**: Extract main content from web pages
- **Features**:
  - Removes scripts and styles
  - Cleans whitespace
  - Configurable max length
- **Usage**: Available for future use when agents need to extract content from URLs

## Integration with Agents

All agents now use MCP tools instead of direct API calls:

### Updated Agents:
1. **PatentAgent** - Uses `patent_search` and `web_search` tools
2. **MarketingAgent** - Uses `web_search` tool
3. **PolicyAgent** - Uses `web_search` tool
4. **TeamAgent** - Uses `web_search` tool
5. **PitchAgent** - Uses `image_search` tool

### BaseAgent Changes:
- Added `MCPClient` initialization in `BaseAgent.__init__()`
- All agents inherit `self.mcp_client` for tool access

## Usage Examples

### For Agents:
```python
# Web search
result = self.mcp_client.web_search(
    query="startup marketing trends",
    topic_context="SaaS B2B",
    max_results=5
)

# Image search
result = self.mcp_client.image_search(
    slide_title="Problem Statement",
    slide_content="Our customers struggle with...",
    keywords=["business", "problem"]
)

# Patent search
result = self.mcp_client.patent_search(
    query="AI-powered recommendation system",
    technology_description="Machine learning recommendation engine",
    company_context={"industry": "SaaS"}
)
```

## Benefits

1. **Separation of Concerns**: Tools are separate from agent logic
2. **Reusability**: Tools can be used by multiple agents
3. **Testability**: Tools can be tested independently
4. **Scalability**: Tools can be deployed separately (future FastAPI integration)
5. **Standardization**: Consistent interface for all external services

## Migration Notes

### Replaced Components:
- `WebSearcher` class → `web_search` MCP tool
- `ImageFetcher` class → `image_search` MCP tool
- Direct API calls → MCP tool calls

### Backward Compatibility:
- Old `WebSearcher` and `ImageFetcher` classes still exist in `src/utils/`
- They are no longer used by agents but kept for reference
- Can be removed in future cleanup if desired

## Next Steps

1. **FastAPI Integration**: Expose MCP tools as REST endpoints
2. **React Frontend**: Connect to FastAPI endpoints
3. **HITL Features**: Add human-in-the-loop workflows
4. **Additional Tools**: Add more tools as needed (e.g., document parsing, API integrations)

## Testing

Test the MCP server:
```bash
python -c "from src.mcp.client import MCPClient; client = MCPClient(); print(client.list_tools())"
```

Expected output:
```
['web_search', 'image_search', 'patent_search', 'content_extractor']
```

## Environment Variables

Optional environment variables for enhanced functionality:
- `PEXELS_API_KEY` - For better Pexels image search
- `UNSPLASH_ACCESS_KEY` - For better Unsplash image search

## Dependencies

All required dependencies are already in `requirements.txt`:
- `ddgs` - Web search
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

No additional dependencies needed for MCP server itself (it's a custom implementation).

