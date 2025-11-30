"""Image fetcher for pitch deck illustrations using free APIs."""

import logging
import requests
from pathlib import Path
from typing import Optional, List
import hashlib
import time

logger = logging.getLogger(__name__)


class ImageFetcher:
    """Fetch relevant images for pitch deck slides."""
    
    def __init__(self):
        self.cache_dir = Path("exports/images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.unsplash_access_key = None  # Optional - works without key for basic usage
        self.pexels_api_key = None  # Optional
    
    def get_image_for_slide(self, slide_title: str, slide_content: str, 
                           keywords: Optional[List[str]] = None) -> Optional[str]:
        """
        Get a relevant image for a slide.
        
        Args:
            slide_title: Title of the slide
            slide_content: Content of the slide
            keywords: Optional list of keywords to search for
            
        Returns:
            Path to downloaded image file, or None if not found
        """
        # Build search query
        if keywords:
            query = " ".join(keywords[:3])  # Use first 3 keywords
        else:
            # Extract keywords from title
            query = slide_title.lower()
            # Remove common words
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            words = [w for w in query.split() if w not in stop_words]
            query = " ".join(words[:3]) if words else slide_title.lower()
        
        # Try Pexels first (free, no key needed for basic usage)
        image_path = self._fetch_from_pexels(query)
        if image_path:
            return image_path
        
        # Fallback to Unsplash
        image_path = self._fetch_from_unsplash(query)
        if image_path:
            return image_path
        
        logger.warning(f"No image found for query: {query}")
        return None
    
    def _fetch_from_pexels(self, query: str) -> Optional[str]:
        """Fetch image from Pexels API (free, no key required for basic usage)."""
        try:
            # Pexels allows basic usage without API key, but with rate limits
            # For better results, get free API key from https://www.pexels.com/api/
            url = "https://api.pexels.com/v1/search"
            headers = {}
            
            # Try with API key if available
            import os
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("PEXELS_API_KEY")
            if api_key:
                headers["Authorization"] = api_key  # Pexels uses API key directly as Authorization header
            
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape",
                "size": "large"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("photos"):
                    photo = data["photos"][0]
                    image_url = photo["src"]["large"]
                    return self._download_image(image_url, query, "pexels")
            elif response.status_code == 401:
                # No API key, try without auth (may have rate limits)
                logger.info("Pexels API key not set. Using basic access (may have rate limits)")
                # For now, skip if no key
                return None
            else:
                logger.warning(f"Pexels API error: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error fetching from Pexels: {e}")
        
        return None
    
    def _fetch_from_unsplash(self, query: str) -> Optional[str]:
        """Fetch image from Unsplash API."""
        try:
            # Unsplash Source API (free, no key needed)
            # Using Unsplash Source for simple image fetching
            # Format: https://source.unsplash.com/featured/?{keywords}
            # This is deprecated but still works for basic usage
            
            # Better: Use Unsplash API with access key (free tier available)
            import os
            from dotenv import load_dotenv
            load_dotenv()
            access_key = os.getenv("UNSPLASH_ACCESS_KEY")
            
            if access_key:
                url = "https://api.unsplash.com/search/photos"
                headers = {"Authorization": f"Client-ID {access_key}"}
                params = {
                    "query": query,
                    "per_page": 1,
                    "orientation": "landscape"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results"):
                        photo = data["results"][0]
                        image_url = photo["urls"]["regular"]
                        return self._download_image(image_url, query, "unsplash")
            else:
                # Fallback: Use Unsplash Source (simple, no key needed)
                # Note: This is less reliable but works without API key
                image_url = f"https://source.unsplash.com/1920x1080/?{query.replace(' ', ',')}"
                return self._download_image(image_url, query, "unsplash_source")
                
        except Exception as e:
            logger.warning(f"Error fetching from Unsplash: {e}")
        
        return None
    
    def _download_image(self, image_url: str, query: str, source: str) -> Optional[str]:
        """Download image and save to cache."""
        try:
            # Create filename from query hash
            query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
            filename = f"{source}_{query_hash}.jpg"
            filepath = self.cache_dir / filename
            
            # Skip if already cached
            if filepath.exists():
                logger.info(f"Using cached image: {filepath}")
                return str(filepath)
            
            # Download image
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
    
    def get_slide_keywords(self, slide_title: str, slide_content: str) -> List[str]:
        """Extract relevant keywords from slide for image search."""
        keywords = []
        
        # Add title words (filtered)
        title_words = slide_title.lower().split()
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "slide"}
        keywords.extend([w for w in title_words if w not in stop_words and len(w) > 2])
        
        # Add content keywords (first few meaningful words)
        content_words = slide_content.lower().split()[:10]
        keywords.extend([w for w in content_words if w not in stop_words and len(w) > 3])
        
        # Map common pitch deck terms to image-friendly keywords
        keyword_map = {
            "problem": "business problem solution",
            "solution": "innovation technology",
            "market": "market growth chart",
            "traction": "growth success metrics",
            "team": "team collaboration",
            "competition": "competition business",
            "financial": "finance money growth",
            "vision": "future vision",
            "product": "product technology",
            "revenue": "revenue growth chart"
        }
        
        for key, mapped in keyword_map.items():
            if key in slide_title.lower() or key in slide_content.lower():
                keywords.append(mapped)
        
        # Return unique keywords, limit to 3
        return list(dict.fromkeys(keywords))[:3]

