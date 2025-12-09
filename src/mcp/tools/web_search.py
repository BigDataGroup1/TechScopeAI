"""Web search tool for MCP server."""

import logging
import warnings
from typing import List, Dict, Optional, Any
from ..server import MCPTool

logger = logging.getLogger(__name__)

# Suppress duckduckgo_search deprecation warning
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*")

# Try to import web search libraries
try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False
        logger.warning("ddgs/duckduckgo_search not available. Install with: pip install ddgs")


class WebSearchTool(MCPTool):
    """Tool for searching the web using DuckDuckGo."""
    
    def __init__(self, max_results: int = 5, min_relevance_score: float = 0.3):
        """
        Initialize web search tool.
        
        Args:
            max_results: Maximum number of results to return
            min_relevance_score: Minimum relevance score (0-1)
        """
        super().__init__(
            name="web_search",
            description="Search the web for information using DuckDuckGo. Returns relevant results with titles, snippets, URLs, and relevance scores."
        )
        self.max_results = max_results
        self.min_relevance_score = min_relevance_score
        self.ddgs = None
        
        if DDGS_AVAILABLE:
            try:
                self.ddgs = DDGS()
                logger.info("✅ Web search tool initialized (DuckDuckGo)")
            except Exception as e:
                logger.warning(f"Could not initialize DuckDuckGo search: {e}")
        else:
            logger.warning("Web search tool not available - install ddgs")
    
    def execute(self, query: str, topic_context: Optional[str] = None, 
                max_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute web search.
        
        Args:
            query: Search query
            topic_context: Optional context to filter results by relevance
            max_results: Override default max_results
            
        Returns:
            Dictionary with search results
        """
        if not self.ddgs:
            return {
                "success": False,
                "error": "Web search not available. Install ddgs package.",
                "results": []
            }
        
        max_results = max_results or self.max_results
        
        try:
            # Perform search with multiple API attempts
            results = []
            try:
                results = list(self.ddgs.text(query, max_results=max_results * 2))
            except (TypeError, Exception) as e1:
                try:
                    results = list(self.ddgs.text(query=query, max_results=max_results * 2))
                except (TypeError, Exception) as e2:
                    try:
                        results = list(self.ddgs.text(keywords=query, max_results=max_results * 2))
                    except Exception as e3:
                        logger.error(f"All web search API attempts failed: {e1}, {e2}, {e3}")
                        return {
                            "success": False,
                            "error": f"Search API failed: {str(e3)}",
                            "results": []
                        }
            
            if not results:
                return {
                    "success": True,
                    "results": [],
                    "count": 0
                }
            
            # Filter and score results by relevance
            scored_results = []
            for result in results:
                relevance = self._calculate_relevance(result, query, topic_context)
                
                if relevance >= self.min_relevance_score:
                    scored_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('href', ''),
                        'relevance_score': relevance
                    })
            
            # Sort by relevance and limit
            scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            final_results = scored_results[:max_results]
            
            logger.info(f"Found {len(final_results)} relevant web results for: {query}")
            
            return {
                "success": True,
                "results": final_results,
                "count": len(final_results),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def _calculate_relevance(self, result: Dict, query: str, 
                            topic_context: Optional[str] = None) -> float:
        """Calculate relevance score for a search result."""
        title = result.get('title', '').lower()
        body = result.get('body', '').lower()
        query_lower = query.lower()
        
        # Extract key terms from query
        query_terms = set(query_lower.split())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        query_terms = {t for t in query_terms if t not in stop_words and len(t) > 2}
        
        if not query_terms:
            return 0.5
        
        # Count matches in title (weighted higher)
        title_matches = sum(1 for term in query_terms if term in title)
        title_score = (title_matches / len(query_terms)) * 0.6
        
        # Count matches in body
        body_matches = sum(1 for term in query_terms if term in body)
        body_score = (body_matches / len(query_terms)) * 0.4
        
        base_score = title_score + body_score
        
        # Boost if topic context matches
        if topic_context:
            context_lower = topic_context.lower()
            context_terms = set(context_lower.split())
            context_terms = {t for t in context_terms if t not in stop_words and len(t) > 2}
            
            if context_terms:
                context_matches = sum(1 for term in context_terms 
                                    if term in title or term in body)
                context_score = (context_matches / len(context_terms)) * 0.2
                base_score = min(1.0, base_score + context_score)
        
        return min(1.0, base_score)
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for tool arguments."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "topic_context": {
                        "type": "string",
                        "description": "Optional context to filter results by relevance"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }


