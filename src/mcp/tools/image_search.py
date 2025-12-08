"""Image search tool for MCP server."""

import logging
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
import hashlib
import os
from ..server import MCPTool

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class ImageSearchTool(MCPTool):
    """Tool for searching and downloading images for pitch decks."""
    
    def __init__(self):
        """Initialize image search tool."""
        super().__init__(
            name="image_search",
            description="Search for professional images suitable for pitch deck slides. Supports Pexels and Unsplash APIs."
        )
        self.cache_dir = Path("exports/images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    
    def execute(self, query: str, slide_title: Optional[str] = None,
                slide_content: Optional[str] = None, 
                keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute image search.
        
        Args:
            query: Search query (or will be generated from slide_title/content)
            slide_title: Optional slide title for context
            slide_content: Optional slide content for context
            keywords: Optional list of keywords
            
        Returns:
            Dictionary with image path and metadata
        """
        try:
            # Build search query
            if keywords:
                professional_keywords = ["professional", "business", "corporate"]
                search_query = " ".join(keywords[:3] + professional_keywords[:1])
            elif slide_title:
                query_lower = slide_title.lower()
                stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
                words = [w for w in query_lower.split() if w not in stop_words]
                search_query = " ".join(words[:3] + ["professional", "business"]) if words else slide_title.lower() + " professional business"
            else:
                search_query = query if query else "business professional"
            
            # Try Pexels first
            image_path = self._fetch_from_pexels(search_query)
            if image_path:
                return {
                    "success": True,
                    "image_path": image_path,
                    "source": "pexels",
                    "query": search_query
                }
            
            # Fallback to Unsplash
            image_path = self._fetch_from_unsplash(search_query)
            if image_path:
                return {
                    "success": True,
                    "image_path": image_path,
                    "source": "unsplash",
                    "query": search_query
                }
            
            return {
                "success": False,
                "error": "No image found",
                "query": search_query
            }
            
        except Exception as e:
            logger.error(f"Error in image search: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _fetch_from_pexels(self, query: str) -> Optional[str]:
        """Fetch image from Pexels API."""
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {}
            
            if self.pexels_api_key:
                headers["Authorization"] = self.pexels_api_key
            
            professional_query = f"{query} professional business corporate presentation"
            params = {
                "query": professional_query,
                "per_page": 5,
                "orientation": "landscape",
                "size": "large"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("photos"):
                    professional_keywords = ["business", "professional", "corporate", "office", "presentation", "meeting"]
                    selected_photo = None
                    
                    for photo in data["photos"]:
                        photo_text = (photo.get("alt", "") + " " + str(photo.get("photographer", ""))).lower()
                        if any(keyword in photo_text for keyword in professional_keywords):
                            selected_photo = photo
                            break
                    
                    if not selected_photo:
                        selected_photo = data["photos"][0]
                    
                    image_url = selected_photo["src"]["large"]
                    return self._download_image(image_url, professional_query, "pexels")
            elif response.status_code == 401:
                logger.info("Pexels API key not set or invalid")
                
        except Exception as e:
            logger.warning(f"Error fetching from Pexels: {e}")
        
        return None
    
    def _fetch_from_unsplash(self, query: str) -> Optional[str]:
        """Fetch image from Unsplash API."""
        try:
            if self.unsplash_access_key:
                url = "https://api.unsplash.com/search/photos"
                headers = {"Authorization": f"Client-ID {self.unsplash_access_key}"}
                professional_query = f"{query} professional business corporate presentation"
                params = {
                    "query": professional_query,
                    "per_page": 5,
                    "orientation": "landscape"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results"):
                        professional_keywords = ["business", "professional", "corporate", "office", "presentation", "meeting"]
                        selected_photo = None
                        
                        for photo in data["results"]:
                            photo_text = (photo.get("description", "") + " " + str(photo.get("tags", []))).lower()
                            if any(keyword in photo_text for keyword in professional_keywords):
                                selected_photo = photo
                                break
                        
                        if not selected_photo:
                            selected_photo = data["results"][0]
                        
                        image_url = selected_photo["urls"]["regular"]
                        return self._download_image(image_url, query, "unsplash")
            else:
                # Fallback: Unsplash Source (simple, no key needed)
                image_url = f"https://source.unsplash.com/1920x1080/?{query.replace(' ', ',')}"
                return self._download_image(image_url, query, "unsplash_source")
                
        except Exception as e:
            logger.warning(f"Error fetching from Unsplash: {e}")
        
        return None
    
    def _download_image(self, image_url: str, query: str, source: str) -> Optional[str]:
        """Download image and save to cache."""
        try:
            query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
            filename = f"{source}_{query_hash}.jpg"
            filepath = self.cache_dir / filename
            
            if filepath.exists():
                logger.info(f"Using cached image: {filepath}")
                return str(filepath)
            
            response = requests.get(image_url, timeout=15, stream=True)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"Downloaded image: {filepath}")
                return str(filepath)
            else:
                logger.warning(f"Failed to download image: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error downloading image: {e}")
        
        return None
    
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
                        "description": "Search query for image"
                    },
                    "slide_title": {
                        "type": "string",
                        "description": "Slide title for context"
                    },
                    "slide_content": {
                        "type": "string",
                        "description": "Slide content for context"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of keywords for image search"
                    }
                },
                "required": []
            }
        }

