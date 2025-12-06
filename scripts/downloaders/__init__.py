"""Downloaders for various data sources."""

from .kaggle_downloader import KaggleDownloader
from .huggingface_downloader import HuggingFaceDownloader
from .github_downloader import GitHubDownloader
from .mendeley_downloader import MendeleyDownloader
from .web_scraper import WebScraper

# Optional downloaders - import only if available
try:
    from .reddit_downloader import RedditDownloader
except ImportError:
    RedditDownloader = None

try:
    from .hackernews_downloader import HackerNewsDownloader
except ImportError:
    HackerNewsDownloader = None

try:
    from .rss_downloader import RSSDownloader
except ImportError:
    RSSDownloader = None

try:
    from .article_scraper import ArticleScraper
except ImportError:
    ArticleScraper = None

__all__ = [
    "KaggleDownloader",
    "HuggingFaceDownloader",
    "GitHubDownloader",
    "MendeleyDownloader",
    "WebScraper",
    "RedditDownloader",
    "HackerNewsDownloader",
    "RSSDownloader",
    "ArticleScraper",
]




