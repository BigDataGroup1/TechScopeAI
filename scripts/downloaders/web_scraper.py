"""Web scraper for public resources."""

import logging
import requests
from pathlib import Path
from typing import List, Optional
import time

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrape public web resources with rate limiting."""

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize web scraper.
        
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

    def download_url(self, url: str, output_path: str, headers: Optional[dict] = None) -> bool:
        """
        Download content from a URL.
        
        Args:
            url: URL to download
            output_path: Path to save the content
            headers: Optional HTTP headers
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._wait_for_rate_limit()
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading from URL: {url}")
            
            default_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            if headers:
                default_headers.update(headers)
            
            response = requests.get(url, headers=default_headers, timeout=30)
            response.raise_for_status()
            
            # Save content
            if output_path.endswith('.html') or 'text/html' in response.headers.get('content-type', ''):
                output_file.write_text(response.text, encoding='utf-8')
            else:
                output_file.write_bytes(response.content)
            
            logger.info(f"Successfully downloaded {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading from {url}: {e}")
            return False

    def download_multiple_urls(self, urls: List[str], base_output_path: str, 
                               filename_pattern: str = "file_{index}.txt") -> dict:
        """
        Download multiple URLs.
        
        Args:
            urls: List of URLs to download
            base_output_path: Base directory to save files
            filename_pattern: Pattern for filenames (use {index} placeholder)
            
        Returns:
            Dictionary mapping URLs to success status
        """
        results = {}
        base_path = Path(base_output_path)
        base_path.mkdir(parents=True, exist_ok=True)
        
        for index, url in enumerate(urls):
            # Extract filename from URL or use pattern
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                filename = Path(parsed.path).name or filename_pattern.format(index=index)
            except:
                filename = filename_pattern.format(index=index)
            
            output_path = base_path / filename
            results[url] = self.download_url(url, str(output_path))
        
        return results


