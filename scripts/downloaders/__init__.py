"""Downloaders for various data sources."""

from .kaggle_downloader import KaggleDownloader
from .huggingface_downloader import HuggingFaceDownloader
from .github_downloader import GitHubDownloader
from .mendeley_downloader import MendeleyDownloader
from .web_scraper import WebScraper
from .reddit_downloader import RedditDownloader
from .hackernews_downloader import HackerNewsDownloader
from .rss_downloader import RSSDownloader
from .article_scraper import ArticleScraper

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


