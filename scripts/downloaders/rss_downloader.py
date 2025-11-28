"""RSS feed downloader for news articles."""

import logging
import feedparser
import requests
from pathlib import Path
from typing import List, Optional, Dict
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class RSSDownloader:
    """Download articles from RSS feeds."""

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize RSS downloader.
        
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

    def download_feed(self, feed_url: str, output_path: str, 
                     limit: Optional[int] = None) -> bool:
        """
        Download articles from an RSS feed.
        
        Args:
            feed_url: URL of RSS feed
            output_path: Directory to save articles
            limit: Maximum number of articles to download
            
        Returns:
            True if successful
        """
        try:
            self._wait_for_rate_limit()
            
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading RSS feed: {feed_url}")
            
            # Download feed with requests to handle SSL issues
            import ssl
            import urllib.request
            import urllib.error
            
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Download feed content
            try:
                req = urllib.request.Request(feed_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                    feed_content = response.read()
                # Parse RSS feed
                feed = feedparser.parse(feed_content)
            except Exception as e:
                logger.warning(f"Failed to download with SSL context, trying direct parse: {e}")
                # Fallback to direct parse
                feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warnings: {feed.bozo_exception}")
            
            entries = feed.entries
            if limit:
                entries = entries[:limit]
            
            articles = []
            for entry in entries:
                article = {
                    "title": entry.get('title', ''),
                    "link": entry.get('link', ''),
                    "published": entry.get('published', ''),
                    "summary": entry.get('summary', ''),
                    "content": entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                    "author": entry.get('author', ''),
                    "tags": [tag.get('term', '') for tag in entry.get('tags', [])]
                }
                articles.append(article)
            
            # Save to JSON file
            feed_name = feed_url.split('/')[-1] or feed_url.split('/')[-2] or "feed"
            output_file = output_dir / f"{feed_name}_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                import json
                json.dump({
                    "feed_title": feed.feed.get('title', ''),
                    "feed_link": feed.feed.get('link', ''),
                    "articles": articles
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully downloaded {len(articles)} articles to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading RSS feed {feed_url}: {e}")
            return False

    def download_multiple_feeds(self, feed_urls: List[str], 
                               output_path: str, limit: Optional[int] = None) -> Dict[str, bool]:
        """
        Download from multiple RSS feeds.
        
        Args:
            feed_urls: List of RSS feed URLs
            output_path: Base directory to save feeds
            limit: Maximum articles per feed
            
        Returns:
            Dictionary mapping feed URLs to success status
        """
        results = {}
        for feed_url in feed_urls:
            feed_name = feed_url.split('/')[-1] or feed_url.split('/')[-2] or "feed"
            feed_path = str(Path(output_path) / feed_name)
            results[feed_url] = self.download_feed(feed_url, feed_path, limit=limit)
            time.sleep(1)  # Rate limiting between feeds
        
        return results

