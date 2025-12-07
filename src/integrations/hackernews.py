"""HackerNews API integration for market sentiment and discussions."""

import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HackerNewsAPI:
    """HackerNews API client (free, no API key needed)."""
    
    def __init__(self):
        """Initialize HackerNews API client."""
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.algolia_url = "https://hn.algolia.com/api/v1"
        logger.info("HackerNews API initialized (free, no key required)")
    
    def search_stories(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search HackerNews stories.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of story dictionaries
        """
        try:
            url = f"{self.algolia_url}/search"
            params = {
                "query": query,
                "tags": "story",
                "hitsPerPage": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                stories = []
                for hit in data.get("hits", [])[:limit]:
                    stories.append({
                        "title": hit.get("title", ""),
                        "url": hit.get("url", ""),
                        "points": hit.get("points", 0),
                        "comments": hit.get("num_comments", 0),
                        "created_at": hit.get("created_at", ""),
                        "author": hit.get("author", ""),
                        "objectID": hit.get("objectID", "")
                    })
                logger.info(f"Found {len(stories)} HackerNews stories for: {query}")
                return stories
                
        except Exception as e:
            logger.error(f"Error searching HackerNews: {e}")
        
        return []
    
    def get_top_stories(self, limit: int = 30) -> List[Dict]:
        """
        Get top stories from HackerNews.
        
        Args:
            limit: Maximum number of stories
            
        Returns:
            List of top stories
        """
        try:
            # Get top story IDs
            response = requests.get(f"{self.base_url}/topstories.json", timeout=10)
            
            if response.status_code == 200:
                story_ids = response.json()[:limit]
                stories = []
                
                # Fetch details for each story
                for story_id in story_ids:
                    story_response = requests.get(
                        f"{self.base_url}/item/{story_id}.json",
                        timeout=5
                    )
                    if story_response.status_code == 200:
                        story = story_response.json()
                        if story and story.get("type") == "story":
                            stories.append({
                                "id": story.get("id"),
                                "title": story.get("title", ""),
                                "url": story.get("url", ""),
                                "score": story.get("score", 0),
                                "comments": story.get("descendants", 0),
                                "time": story.get("time", 0),
                                "by": story.get("by", "")
                            })
                
                return stories
                
        except Exception as e:
            logger.error(f"Error getting top stories: {e}")
        
        return []
    
    def search_startup_discussions(self, topic: str, limit: int = 10) -> List[Dict]:
        """
        Search for startup-related discussions.
        
        Args:
            topic: Topic to search for (e.g., "startup funding", "SaaS")
            limit: Maximum number of results
            
        Returns:
            List of relevant discussions
        """
        # Search with startup-related keywords
        query = f"{topic} startup"
        return self.search_stories(query, limit=limit)
    
    def get_market_sentiment(self, company_name: str, product_name: Optional[str] = None) -> Dict:
        """
        Get market sentiment about a company/product from HackerNews.
        
        Args:
            company_name: Company name
            product_name: Optional product name
            
        Returns:
            Dictionary with sentiment analysis
        """
        query = company_name
        if product_name:
            query = f"{company_name} {product_name}"
        
        stories = self.search_stories(query, limit=20)
        
        # Analyze sentiment (simple: positive = high score/comments)
        total_score = sum(s.get("points", 0) for s in stories)
        total_comments = sum(s.get("comments", 0) for s in stories)
        avg_score = total_score / len(stories) if stories else 0
        
        sentiment = "positive" if avg_score > 10 else "neutral" if avg_score > 5 else "negative"
        
        return {
            "company": company_name,
            "stories_found": len(stories),
            "total_score": total_score,
            "total_comments": total_comments,
            "average_score": round(avg_score, 2),
            "sentiment": sentiment,
            "recent_stories": stories[:5]  # Top 5 most recent
        }


