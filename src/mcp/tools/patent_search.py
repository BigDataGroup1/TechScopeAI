"""Patent search tool for MCP server."""

import logging
from typing import Dict, Any, Optional
from ..server import MCPTool
from .web_search import WebSearchTool

logger = logging.getLogger(__name__)


class PatentSearchTool(MCPTool):
    """Tool for searching patents and prior art."""
    
    def __init__(self):
        """Initialize patent search tool."""
        super().__init__(
            name="patent_search",
            description="Search for patents and prior art. Uses specialized patent database queries and web search."
        )
        # Use web search tool for patent searches
        self.web_search_tool = WebSearchTool(max_results=10, min_relevance_score=0.2)
    
    def execute(self, query: str, technology_description: Optional[str] = None,
                company_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute patent search.
        
        Args:
            query: Search query (e.g., technology description)
            technology_description: Optional detailed technology description
            company_context: Optional company context dictionary
            
        Returns:
            Dictionary with patent search results
        """
        try:
            # Enhance query for patent databases
            patent_query = self._build_patent_query(query, technology_description, company_context)
            
            # Search using web search tool with patent-specific queries
            search_results = self.web_search_tool.execute(
                query=patent_query,
                topic_context=technology_description or query,
                max_results=10
            )
            
            if not search_results.get("success"):
                return search_results
            
            # Filter and enhance results for patent relevance
            patent_results = []
            for result in search_results.get("results", []):
                # Boost relevance for patent-related domains
                url = result.get("url", "").lower()
                title = result.get("title", "").lower()
                
                patent_domains = ["uspto.gov", "patents.google.com", "patentscope.wipo.int", 
                                "epo.org", "espacenet.com", "patent", "prior art"]
                is_patent_source = any(domain in url for domain in patent_domains) or \
                                 any(term in title for term in ["patent", "prior art", "invention"])
                
                if is_patent_source:
                    result["patent_relevant"] = True
                    result["relevance_score"] = min(1.0, result.get("relevance_score", 0) + 0.2)
                
                patent_results.append(result)
            
            # Sort by patent relevance
            patent_results.sort(key=lambda x: (
                x.get("patent_relevant", False),
                x.get("relevance_score", 0)
            ), reverse=True)
            
            return {
                "success": True,
                "results": patent_results[:10],
                "count": len(patent_results),
                "query": patent_query,
                "patent_specific": any(r.get("patent_relevant") for r in patent_results)
            }
            
        except Exception as e:
            logger.error(f"Error in patent search: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def _build_patent_query(self, query: str, technology_description: Optional[str],
                           company_context: Optional[Dict]) -> str:
        """Build enhanced patent search query."""
        # Start with base query
        patent_query = query
        
        # Add patent-specific terms
        patent_terms = ["patent", "prior art", "invention"]
        
        # Add technology description if available
        if technology_description:
            # Extract key technical terms
            tech_words = technology_description.split()[:5]
            patent_query = f"{patent_query} {' '.join(tech_words)}"
        
        # Add industry context if available
        if company_context:
            industry = company_context.get("industry", "")
            if industry:
                patent_query = f"{patent_query} {industry}"
        
        return patent_query
    
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
                        "description": "Patent search query"
                    },
                    "technology_description": {
                        "type": "string",
                        "description": "Detailed technology description"
                    },
                    "company_context": {
                        "type": "object",
                        "description": "Company context dictionary"
                    }
                },
                "required": ["query"]
            }
        }

