"""Downloaders for various data sources."""

from .kaggle_downloader import KaggleDownloader
from .huggingface_downloader import HuggingFaceDownloader
from .github_downloader import GitHubDownloader
from .mendeley_downloader import MendeleyDownloader
from .web_scraper import WebScraper

__all__ = [
    "KaggleDownloader",
    "HuggingFaceDownloader",
    "GitHubDownloader",
    "MendeleyDownloader",
    "WebScraper",
]


