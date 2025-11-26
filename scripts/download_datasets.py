"""Main script to download all datasets."""

import argparse
import logging
import os
import yaml
from pathlib import Path
from typing import Dict, List

import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from downloaders import (
    KaggleDownloader,
    HuggingFaceDownloader,
    GitHubDownloader,
    MendeleyDownloader,
    WebScraper,
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


def download_kaggle_dataset(dataset_config: dict, downloader: KaggleDownloader) -> bool:
    """Download a Kaggle dataset."""
    dataset_id = dataset_config['dataset_id']
    output_path = dataset_config['output_path']
    required_columns = dataset_config.get('required_columns')
    
    success = downloader.download(dataset_id, output_path)
    if success and required_columns:
        success = downloader.validate_dataset(output_path, required_columns)
    
    return success


def download_huggingface_dataset(dataset_config: dict, downloader: HuggingFaceDownloader) -> bool:
    """Download a HuggingFace dataset."""
    dataset_id = dataset_config['dataset_id']
    output_path = dataset_config['output_path']
    
    success = downloader.download(dataset_id, output_path)
    if success:
        success = downloader.validate_dataset(output_path)
    
    return success


def download_github_dataset(dataset_config: dict, downloader: GitHubDownloader) -> bool:
    """Download a GitHub repository."""
    repo = dataset_config['repo']
    output_path = dataset_config['output_path']
    
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
    
    results = scraper.download_multiple_urls(urls, output_path)
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

