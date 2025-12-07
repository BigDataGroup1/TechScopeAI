"""Real-time data layer that combines multiple data sources."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from .product_hunt import ProductHuntAPI
from .hackernews import HackerNewsAPI
from ..utils.web_search import WebSearcher

logger = logging.getLogger(__name__)


class RealDataLayer:
    """
    Unified interface for real-time data from multiple sources.
    Integrates with RAG system to provide live data alongside static knowledge.
    """
    
    def __init__(self):
        """Initialize real data layer with all integrations."""
        self.product_hunt = ProductHuntAPI()
        self.hackernews = HackerNewsAPI()
        self.web_searcher = WebSearcher(max_results=10)
        logger.info("RealDataLayer initialized")
    
    def get_competitor_intelligence(self, competitor_name: str, 
                                   industry: Optional[str] = None) -> Dict:
        """
        Get comprehensive competitor intelligence from multiple sources.
        
        Args:
            competitor_name: Name of competitor
            industry: Optional industry filter
            
        Returns:
            Dictionary with competitor data from all sources
        """
        logger.info(f"Fetching competitor intelligence for: {competitor_name}")
        
        intelligence = {
            "competitor_name": competitor_name,
            "sources": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. Product Hunt data
        try:
            ph_competitors = self.product_hunt.find_competitors(competitor_name, industry)
            intelligence["sources"]["product_hunt"] = {
                "products": ph_competitors,
                "count": len(ph_competitors)
            }
        except Exception as e:
            logger.warning(f"Error fetching Product Hunt data: {e}")
            intelligence["sources"]["product_hunt"] = {"error": str(e)}
        
        # 2. HackerNews discussions
        try:
            hn_stories = self.hackernews.search_stories(competitor_name, limit=10)
            intelligence["sources"]["hackernews"] = {
                "stories": hn_stories,
                "count": len(hn_stories)
            }
        except Exception as e:
            logger.warning(f"Error fetching HackerNews data: {e}")
            intelligence["sources"]["hackernews"] = {"error": str(e)}
        
        # 3. Web search (for latest news)
        try:
            web_results = self.web_searcher.search(
                f"{competitor_name} startup funding news",
                topic_context=industry or ""
            )
            intelligence["sources"]["web_search"] = {
                "results": web_results,
                "count": len(web_results)
            }
        except Exception as e:
            logger.warning(f"Error fetching web search data: {e}")
            intelligence["sources"]["web_search"] = {"error": str(e)}
        
        return intelligence
    
    def get_market_trends(self, industry: str, limit: int = 10) -> Dict:
        """
        Get market trends for an industry.
        
        Args:
            industry: Industry name
            limit: Maximum results per source
            
        Returns:
            Dictionary with market trends
        """
        logger.info(f"Fetching market trends for: {industry}")
        
        trends = {
            "industry": industry,
            "sources": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. Trending products on Product Hunt
        try:
            trending = self.product_hunt.get_trending_products(category=industry, limit=limit)
            trends["sources"]["product_hunt_trending"] = trending
        except Exception as e:
            logger.warning(f"Error fetching trending products: {e}")
        
        # 2. HackerNews discussions
        try:
            discussions = self.hackernews.search_startup_discussions(industry, limit=limit)
            trends["sources"]["hackernews_discussions"] = discussions
        except Exception as e:
            logger.warning(f"Error fetching HN discussions: {e}")
        
        # 3. Web search for latest news
        try:
            web_results = self.web_searcher.search(
                f"{industry} startup trends 2025",
                topic_context=industry
            )
            trends["sources"]["web_news"] = web_results
        except Exception as e:
            logger.warning(f"Error fetching web news: {e}")
        
        return trends
    
    def get_investor_sentiment(self, company_name: str) -> Dict:
        """
        Get investor and market sentiment about a company.
        
        Args:
            company_name: Company name
            
        Returns:
            Dictionary with sentiment analysis
        """
        logger.info(f"Fetching investor sentiment for: {company_name}")
        
        # Get HackerNews sentiment
        hn_sentiment = self.hackernews.get_market_sentiment(company_name)
        
        # Search for funding news
        funding_news = self.web_searcher.search(
            f"{company_name} funding investment raise",
            topic_context="startup funding"
        )
        
        return {
            "company": company_name,
            "hackernews_sentiment": hn_sentiment,
            "funding_news": funding_news,
            "timestamp": datetime.now().isoformat()
        }
    
    def format_for_rag(self, data: Dict) -> str:
        """
        Format real-time data for RAG context.
        
        Args:
            data: Data dictionary from any method
            
        Returns:
            Formatted string for RAG context
        """
        formatted_parts = []
        
        if "sources" in data:
            for source_name, source_data in data["sources"].items():
                if "error" in source_data:
                    continue
                
                formatted_parts.append(f"\n=== {source_name.upper().replace('_', ' ')} ===")
                
                if "products" in source_data:
                    for product in source_data["products"][:5]:  # Top 5
                        formatted_parts.append(
                            f"- {product.get('name', 'Unknown')}: {product.get('tagline', '')} "
                            f"(Votes: {product.get('votes', 0)})"
                        )
                
                elif "stories" in source_data:
                    for story in source_data["stories"][:5]:  # Top 5
                        formatted_parts.append(
                            f"- {story.get('title', 'Unknown')} "
                            f"(Score: {story.get('points', story.get('score', 0))}, "
                            f"Comments: {story.get('comments', 0)})"
                        )
                
                elif "results" in source_data:
                    for result in source_data["results"][:5]:  # Top 5
                        formatted_parts.append(
                            f"- {result.get('title', 'Unknown')}: {result.get('snippet', '')[:100]}..."
                        )
        
        return "\n".join(formatted_parts) if formatted_parts else "No real-time data available."


