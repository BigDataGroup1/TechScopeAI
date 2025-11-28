"""Main script to download all datasets."""

import argparse
import logging
import os
import yaml
from pathlib import Path
from typing import Dict, List

import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logging.getLogger(__name__).info(f"Loaded environment variables from {env_path}")
except ImportError:
    pass  # python-dotenv not installed, will use system env vars

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from downloaders import (
    KaggleDownloader,
    HuggingFaceDownloader,
    GitHubDownloader,
    MendeleyDownloader,
    WebScraper,
    RedditDownloader,
    HackerNewsDownloader,
    RSSDownloader,
    ArticleScraper,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "scripts/config/dataset_config.yaml") -> dict:
    """Load dataset configuration from YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def check_data_exists(output_path: str, min_files: int = 1) -> bool:
    """
    Check if data already exists at the output path.
    
    Args:
        output_path: Path to check
        min_files: Minimum number of files to consider data as existing
        
    Returns:
        True if data exists, False otherwise
    """
    output_dir = Path(output_path)
    
    # If it's a file path (CSV, JSON, etc.)
    if output_path.endswith(('.csv', '.json', '.jsonl', '.txt', '.html')):
        return output_dir.exists() and output_dir.stat().st_size > 0
    
    # If it's a directory path
    if output_dir.exists() and output_dir.is_dir():
        # Count non-hidden files
        files = [f for f in output_dir.rglob('*') if f.is_file() and not f.name.startswith('.')]
        if len(files) >= min_files:
            # Check if files have content
            total_size = sum(f.stat().st_size for f in files)
            return total_size > 0
    
    return False


def download_kaggle_dataset(dataset_config: dict, downloader: KaggleDownloader) -> bool:
    """Download a Kaggle dataset."""
    dataset_id = dataset_config['dataset_id']
    output_path = dataset_config['output_path']
    required_columns = dataset_config.get('required_columns')
    
    # Skip if data already exists
    if check_data_exists(output_path):
        logger.info(f"⏭️  Skipping {dataset_config.get('name', dataset_id)} - data already exists at {output_path}")
        return True
    
    success = downloader.download(dataset_id, output_path)
    if success and required_columns:
        success = downloader.validate_dataset(output_path, required_columns)
    
    return success


def download_huggingface_dataset(dataset_config: dict, downloader: HuggingFaceDownloader) -> bool:
    """Download a HuggingFace dataset."""
    dataset_id = dataset_config['dataset_id']
    output_path = dataset_config['output_path']
    
    # Skip if data already exists
    if check_data_exists(output_path, min_files=1):
        logger.info(f"⏭️  Skipping {dataset_config.get('name', dataset_id)} - data already exists at {output_path}")
        return True
    
    success = downloader.download(dataset_id, output_path)
    if success:
        success = downloader.validate_dataset(output_path)
    
    return success


def download_github_dataset(dataset_config: dict, downloader: GitHubDownloader) -> bool:
    """Download a GitHub repository."""
    repo = dataset_config['repo']
    output_path = dataset_config['output_path']
    
    # Skip if data already exists
    if check_data_exists(output_path, min_files=1):
        logger.info(f"⏭️  Skipping {dataset_config.get('name', repo)} - data already exists at {output_path}")
        return True
    
    return downloader.download_repo(repo, output_path)


def download_github_repos(dataset_config: dict, downloader: GitHubDownloader) -> Dict[str, bool]:
    """Download multiple GitHub repositories."""
    repos = dataset_config.get('repos', [])
    output_path = dataset_config['output_path']
    
    return downloader.download_multiple_repos(repos, output_path)


def download_mendeley_dataset(dataset_config: dict, downloader: MendeleyDownloader) -> bool:
    """Download a Mendeley dataset."""
    dataset_id = dataset_config['dataset_id']
    output_path = dataset_config['output_path']
    
    success = downloader.download(dataset_id, output_path)
    if success:
        success = downloader.validate_dataset(output_path)
    
    return success


def download_manual_dataset(dataset_config: dict, scraper: WebScraper) -> bool:
    """Download manual datasets (web resources)."""
    urls = dataset_config.get('urls', [])
    output_path = dataset_config['output_path']
    
    if not urls:
        logger.warning(f"No URLs specified for manual dataset: {dataset_config.get('name', 'unknown')}")
        return False
    
    # Skip if data already exists
    if check_data_exists(output_path, min_files=1):
        logger.info(f"⏭️  Skipping {dataset_config.get('name', 'manual')} - data already exists at {output_path}")
        return True
    
    results = scraper.download_multiple_urls(urls, output_path)
    return all(results.values())


def download_reddit_dataset(dataset_config: dict, downloader: RedditDownloader) -> bool:
    """Download Reddit posts from subreddits."""
    subreddits = dataset_config.get('subreddits', [])
    output_path = dataset_config['output_path']
    limit = dataset_config.get('limit', 1000)
    
    if not subreddits:
        logger.warning("No subreddits specified")
        return False
    
    # Skip if data already exists
    if check_data_exists(output_path, min_files=1):
        logger.info(f"⏭️  Skipping {dataset_config.get('name', 'reddit')} - data already exists at {output_path}")
        return True
    
    results = downloader.download_multiple_subreddits(subreddits, output_path, limit=limit)
    return all(results.values())


def download_hackernews_dataset(dataset_config: dict, downloader: HackerNewsDownloader) -> bool:
    """Download Hacker News stories."""
    output_path = dataset_config['output_path']
    limit = dataset_config.get('limit', 1000)
    story_type = dataset_config.get('story_type', 'top')
    filter_startup = dataset_config.get('filter_startup', True)
    
    # Skip if data already exists
    if check_data_exists(output_path, min_files=1):
        logger.info(f"⏭️  Skipping {dataset_config.get('name', 'hackernews')} - data already exists at {output_path}")
        return True
    
    return downloader.download_stories(output_path, limit=limit, 
                                      story_type=story_type, 
                                      filter_startup=filter_startup)


def download_rss_dataset(dataset_config: dict, downloader: RSSDownloader) -> bool:
    """Download articles from RSS feeds."""
    feed_urls = dataset_config.get('feed_urls', [])
    output_path = dataset_config['output_path']
    limit = dataset_config.get('limit', 100)
    
    if not feed_urls:
        logger.warning("No RSS feed URLs specified")
        return False
    
    # Skip if data already exists (check for recent files - RSS updates daily)
    # Only skip if files are from today
    output_dir = Path(output_path)
    if output_dir.exists():
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        recent_files = list(output_dir.rglob(f'*{today}*.json'))
        if recent_files:
            logger.info(f"⏭️  Skipping {dataset_config.get('name', 'rss')} - today's data already exists")
            return True
    
    results = downloader.download_multiple_feeds(feed_urls, output_path, limit=limit)
    return all(results.values())


def download_article_dataset(dataset_config: dict, scraper: ArticleScraper) -> bool:
    """Download and scrape articles from URLs."""
    urls = dataset_config.get('urls', [])
    output_path = dataset_config['output_path']
    
    if not urls:
        logger.warning("No URLs specified for article scraping")
        return False
    
    # Skip if data already exists
    if check_data_exists(output_path, min_files=1):
        logger.info(f"⏭️  Skipping {dataset_config.get('name', 'articles')} - data already exists at {output_path}")
        return True
    
    results = scraper.scrape_multiple_articles(urls, output_path)
    return all(results.values())


def download_all_datasets(config: dict, agent_filter: List[str] = None) -> Dict[str, Dict[str, bool]]:
    """
    Download all datasets from configuration.
    
    Args:
        config: Dataset configuration dictionary
        agent_filter: Optional list of agent names to filter (e.g., ['competitive', 'marketing'])
        
    Returns:
        Dictionary mapping agent names to dataset download results
    """
    results = {}
    
    # Initialize downloaders
    kaggle_dl = KaggleDownloader()
    # Check for HuggingFace token
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    hf_dl = HuggingFaceDownloader(token=hf_token)
    github_dl = GitHubDownloader()
    mendeley_dl = MendeleyDownloader()
    web_scraper = WebScraper()
    
    # Initialize new downloaders
    try:
        reddit_dl = RedditDownloader()
    except Exception as e:
        logger.warning(f"Reddit downloader not available: {e}")
        reddit_dl = None
    
    hackernews_dl = HackerNewsDownloader()
    rss_dl = RSSDownloader()
    article_scraper = ArticleScraper()
    
    # Process each agent category
    for agent_name, datasets in config['datasets'].items():
        if agent_filter and agent_name not in agent_filter:
            logger.info(f"Skipping {agent_name} (filtered out)")
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {agent_name} datasets")
        logger.info(f"{'='*60}")
        
        agent_results = {}
        
        for dataset_config in datasets:
            dataset_name = dataset_config['name']
            source = dataset_config['source']
            
            logger.info(f"\nDownloading {dataset_name} from {source}...")
            
            try:
                if source == 'kaggle':
                    success = download_kaggle_dataset(dataset_config, kaggle_dl)
                elif source == 'huggingface':
                    success = download_huggingface_dataset(dataset_config, hf_dl)
                elif source == 'github':
                    if 'repos' in dataset_config:
                        # Multiple repos
                        repo_results = download_github_repos(dataset_config, github_dl)
                        success = all(repo_results.values())
                        agent_results[dataset_name] = repo_results
                    else:
                        success = download_github_dataset(dataset_config, github_dl)
                elif source == 'mendeley':
                    success = download_mendeley_dataset(dataset_config, mendeley_dl)
                elif source == 'manual':
                    success = download_manual_dataset(dataset_config, web_scraper)
                elif source == 'reddit':
                    if reddit_dl:
                        success = download_reddit_dataset(dataset_config, reddit_dl)
                    else:
                        logger.error("Reddit downloader not available. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
                        success = False
                elif source == 'hackernews':
                    success = download_hackernews_dataset(dataset_config, hackernews_dl)
                elif source == 'rss':
                    success = download_rss_dataset(dataset_config, rss_dl)
                elif source == 'article':
                    success = download_article_dataset(dataset_config, article_scraper)
                else:
                    logger.error(f"Unknown source: {source}")
                    success = False
                
                if 'repos' not in dataset_config:  # Don't overwrite multi-repo results
                    agent_results[dataset_name] = success
                
                if success:
                    logger.info(f"✓ Successfully downloaded {dataset_name}")
                else:
                    logger.error(f"✗ Failed to download {dataset_name}")
                    
            except Exception as e:
                logger.error(f"✗ Error downloading {dataset_name}: {e}")
                agent_results[dataset_name] = False
        
        results[agent_name] = agent_results
    
    return results


def print_summary(results: Dict[str, Dict[str, bool]]):
    """Print download summary."""
    logger.info("\n" + "="*60)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("="*60)
    
    total = 0
    successful = 0
    
    for agent_name, agent_results in results.items():
        logger.info(f"\n{agent_name.upper()}:")
        for dataset_name, success in agent_results.items():
            if isinstance(success, dict):
                # Multi-repo result
                for repo, repo_success in success.items():
                    status = "✓" if repo_success else "✗"
                    logger.info(f"  {status} {dataset_name}/{repo}")
                    total += 1
                    if repo_success:
                        successful += 1
            else:
                status = "✓" if success else "✗"
                logger.info(f"  {status} {dataset_name}")
                total += 1
                if success:
                    successful += 1
    
    logger.info(f"\nTotal: {successful}/{total} datasets downloaded successfully")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Download datasets for TechScope AI")
    parser.add_argument(
        "--config",
        default="scripts/config/dataset_config.yaml",
        help="Path to dataset configuration file"
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        help="Filter specific agents (e.g., competitive marketing)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing datasets, don't download"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    if args.validate_only:
        logger.info("Validation mode - checking existing datasets...")
        # TODO: Implement validation-only mode
        return
    
    # Download datasets
    results = download_all_datasets(config, agent_filter=args.agents)
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()

