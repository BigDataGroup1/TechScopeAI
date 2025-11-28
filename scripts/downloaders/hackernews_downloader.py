"""Hacker News API downloader."""

import logging
import json
import requests
from pathlib import Path
from typing import List, Optional, Dict
import time

logger = logging.getLogger(__name__)


class HackerNewsDownloader:
    """Download stories and comments from Hacker News."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, rate_limit: float = 0.5):
        """
        Initialize Hacker News downloader.
        
        Args:
            rate_limit: Seconds to wait between requests
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0

    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()

    def _get_item(self, item_id: int) -> Optional[dict]:
        """Get a single item by ID."""
        self._wait_for_rate_limit()
        try:
            response = requests.get(f"{self.BASE_URL}/item/{item_id}.json", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching item {item_id}: {e}")
            return None

    def _get_top_stories(self, limit: int = 500) -> List[int]:
        """Get IDs of top stories."""
        self._wait_for_rate_limit()
        try:
            response = requests.get(f"{self.BASE_URL}/topstories.json", timeout=10)
            response.raise_for_status()
            story_ids = response.json()
            return story_ids[:limit]
        except Exception as e:
            logger.error(f"Error fetching top stories: {e}")
            return []

    def _get_new_stories(self, limit: int = 500) -> List[int]:
        """Get IDs of new stories."""
        self._wait_for_rate_limit()
        try:
            response = requests.get(f"{self.BASE_URL}/newstories.json", timeout=10)
            response.raise_for_status()
            story_ids = response.json()
            return story_ids[:limit]
        except Exception as e:
            logger.error(f"Error fetching new stories: {e}")
            return []

    def _get_ask_hn_stories(self, limit: int = 500) -> List[int]:
        """Get IDs of Ask HN stories."""
        self._wait_for_rate_limit()
        try:
            response = requests.get(f"{self.BASE_URL}/askstories.json", timeout=10)
            response.raise_for_status()
            story_ids = response.json()
            return story_ids[:limit]
        except Exception as e:
            logger.error(f"Error fetching Ask HN stories: {e}")
            return []

    def _filter_startup_keywords(self, text: str) -> bool:
        """Check if text contains startup-related keywords."""
        if not text:
            return False
        keywords = [
            "startup", "founder", "entrepreneur", "funding", "venture", 
            "investor", "pitch", "YC", "ycombinator", "seed", "series a",
            "series b", "unicorn", "IPO", "acquisition", "exit"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

    def download_stories(self, output_path: str, limit: int = 1000, 
                        story_type: str = "top", filter_startup: bool = True) -> bool:
        """
        Download Hacker News stories.
        
        Args:
            output_path: Directory to save stories
            limit: Maximum number of stories to download
            story_type: Type of stories ("top", "new", "ask")
            filter_startup: Only download startup-related stories
            
        Returns:
            True if successful
        """
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading {limit} {story_type} stories from Hacker News...")
            
            # Get story IDs
            if story_type == "top":
                story_ids = self._get_top_stories(limit=limit)
            elif story_type == "new":
                story_ids = self._get_new_stories(limit=limit)
            elif story_type == "ask":
                story_ids = self._get_ask_hn_stories(limit=limit)
            else:
                story_ids = self._get_top_stories(limit=limit)
            
            stories_data = []
            for idx, story_id in enumerate(story_ids):
                if idx >= limit:
                    break
                
                item = self._get_item(story_id)
                if not item or item.get('type') != 'story':
                    continue
                
                # Filter for startup-related content if requested
                if filter_startup:
                    title = item.get('title', '')
                    text = item.get('text', '')
                    if not self._filter_startup_keywords(title) and not self._filter_startup_keywords(text):
                        continue
                
                story_data = {
                    "id": item.get('id'),
                    "title": item.get('title'),
                    "text": item.get('text'),
                    "url": item.get('url'),
                    "by": item.get('by'),
                    "score": item.get('score'),
                    "descendants": item.get('descendants'),
                    "time": item.get('time'),
                    "type": item.get('type')
                }
                
                # Get top-level comments (limit to 20 per story)
                kids = item.get('kids', [])[:20]
                comments = []
                for kid_id in kids:
                    comment = self._get_item(kid_id)
                    if comment and comment.get('type') == 'comment':
                        comments.append({
                            "id": comment.get('id'),
                            "text": comment.get('text'),
                            "by": comment.get('by'),
                            "score": comment.get('score'),
                            "time": comment.get('time')
                        })
                
                story_data["comments"] = comments
                stories_data.append(story_data)
                
                if (idx + 1) % 50 == 0:
                    logger.info(f"Downloaded {idx + 1} stories...")
            
            # Save to JSON file
            output_file = output_dir / f"hn_{story_type}_stories.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(stories_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully downloaded {len(stories_data)} stories to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading Hacker News stories: {e}")
            return False

