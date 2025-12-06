"""Enhanced article scraper using newspaper3k and BeautifulSoup."""

import logging
import json
from pathlib import Path
from typing import List, Optional, Dict
import time

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    import requests
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

logger = logging.getLogger(__name__)


class ArticleScraper:
    """Scrape and extract articles from web pages."""

    def __init__(self, rate_limit: float = 2.0):
        """
        Initialize article scraper.
        
        Args:
            rate_limit: Seconds to wait between requests
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        if not NEWSPAPER_AVAILABLE:
            logger.warning("newspaper3k not available. Install with: pip install newspaper3k")
        if not BS4_AVAILABLE:
            logger.warning("beautifulsoup4 not available. Install with: pip install beautifulsoup4")

    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()

    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article.
        
        Args:
            url: URL of article to scrape
            
        Returns:
            Dictionary with article data or None
        """
        try:
            self._wait_for_rate_limit()
            
            if NEWSPAPER_AVAILABLE:
                article = Article(url)
                article.download()
                article.parse()
                
                return {
                    "url": url,
                    "title": article.title,
                    "text": article.text,
                    "authors": article.authors,
                    "publish_date": str(article.publish_date) if article.publish_date else None,
                    "summary": article.summary if hasattr(article, 'summary') else '',
                    "images": article.images,
                    "keywords": article.keywords if hasattr(article, 'keywords') else []
                }
            elif BS4_AVAILABLE:
                # Fallback to BeautifulSoup
                response = requests.get(url, timeout=30, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract title
                title = soup.find('title')
                title_text = title.get_text() if title else ''
                
                # Try to extract main content
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
                if main_content:
                    text = main_content.get_text(separator='\n', strip=True)
                else:
                    # Fallback: get all paragraph text
                    paragraphs = soup.find_all('p')
                    text = '\n'.join([p.get_text() for p in paragraphs])
                
                return {
                    "url": url,
                    "title": title_text,
                    "text": text,
                    "authors": [],
                    "publish_date": None,
                    "summary": text[:500] if text else '',
                    "images": [],
                    "keywords": []
                }
            else:
                logger.error("No article scraping library available")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None

    def scrape_multiple_articles(self, urls: List[str], output_path: str) -> Dict[str, bool]:
        """
        Scrape multiple articles.
        
        Args:
            urls: List of article URLs
            output_path: Directory to save articles
            
        Returns:
            Dictionary mapping URLs to success status
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        articles_data = []
        
        for idx, url in enumerate(urls):
            logger.info(f"Scraping article {idx + 1}/{len(urls)}: {url}")
            article_data = self.scrape_article(url)
            
            if article_data:
                articles_data.append(article_data)
                results[url] = True
            else:
                results[url] = False
        
        # Save all articles to JSON file
        if articles_data:
            output_file = output_dir / "articles.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(articles_data)} articles to {output_file}")
        
        return results

