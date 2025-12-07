"""Product Hunt API integration for real-time product and competitor data."""

import logging
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ProductHuntAPI:
    """Product Hunt API client for fetching product launches and competitor data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Product Hunt API client.
        
        Args:
            api_key: Product Hunt API key (or from PRODUCT_HUNT_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("PRODUCT_HUNT_API_KEY")
        self.base_url = "https://api.producthunt.com/v2/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            logger.warning("Product Hunt API key not found. Some features may be limited.")
    
    def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for products on Product Hunt.
        
        Args:
            query: Search query (product name, category, etc.)
            limit: Maximum number of results
            
        Returns:
            List of product dictionaries
        """
        if not self.api_key:
            logger.warning("Product Hunt API key required for search")
            return []
        
        try:
            # Product Hunt GraphQL query
            graphql_query = """
            query SearchProducts($query: String!, $first: Int!) {
                posts(first: $first, search: $query) {
                    edges {
                        node {
                            id
                            name
                            tagline
                            description
                            votesCount
                            commentsCount
                            createdAt
                            website
                            topics {
                                edges {
                                    node {
                                        name
                                    }
                                }
                            }
                            user {
                                name
                            }
                        }
                    }
                }
            }
            """
            
            variables = {
                "query": query,
                "first": limit
            }
            
            response = requests.post(
                self.base_url,
                json={"query": graphql_query, "variables": variables},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "posts" in data["data"]:
                    products = []
                    for edge in data["data"]["posts"]["edges"]:
                        node = edge["node"]
                        products.append({
                            "name": node.get("name", ""),
                            "tagline": node.get("tagline", ""),
                            "description": node.get("description", ""),
                            "votes": node.get("votesCount", 0),
                            "comments": node.get("commentsCount", 0),
                            "created_at": node.get("createdAt", ""),
                            "website": node.get("website", ""),
                            "topics": [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])],
                            "maker": node.get("user", {}).get("name", "")
                        })
                    logger.info(f"Found {len(products)} products for query: {query}")
                    return products
            else:
                logger.warning(f"Product Hunt API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error searching Product Hunt: {e}")
        
        return []
    
    def get_trending_products(self, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get trending products on Product Hunt.
        
        Args:
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of trending products
        """
        if not self.api_key:
            logger.warning("Product Hunt API key required")
            return []
        
        try:
            # Get today's top products
            graphql_query = """
            query GetTrendingProducts($first: Int!) {
                posts(first: $first, order: VOTES) {
                    edges {
                        node {
                            id
                            name
                            tagline
                            votesCount
                            createdAt
                            website
                            topics {
                                edges {
                                    node {
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            
            variables = {"first": limit}
            
            response = requests.post(
                self.base_url,
                json={"query": graphql_query, "variables": variables},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "posts" in data["data"]:
                    products = []
                    for edge in data["data"]["posts"]["edges"]:
                        node = edge["node"]
                        products.append({
                            "name": node.get("name", ""),
                            "tagline": node.get("tagline", ""),
                            "votes": node.get("votesCount", 0),
                            "created_at": node.get("createdAt", ""),
                            "website": node.get("website", ""),
                            "topics": [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])]
                        })
                    return products
                    
        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
        
        return []
    
    def find_competitors(self, product_name: str, industry: Optional[str] = None) -> List[Dict]:
        """
        Find competitor products on Product Hunt.
        
        Args:
            product_name: Your product name
            industry: Optional industry/category filter
            
        Returns:
            List of competitor products
        """
        # Search for similar products
        query = product_name
        if industry:
            query = f"{product_name} {industry}"
        
        competitors = self.search_products(query, limit=20)
        
        # Filter out exact matches (your own product)
        competitors = [c for c in competitors if c["name"].lower() != product_name.lower()]
        
        # Sort by votes (popularity)
        competitors.sort(key=lambda x: x.get("votes", 0), reverse=True)
        
        return competitors[:10]  # Top 10 competitors


