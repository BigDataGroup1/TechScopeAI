"""HuggingFace dataset downloader."""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class HuggingFaceDownloader:
    """Download datasets from HuggingFace."""

    def __init__(self, cache_dir: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize HuggingFace downloader.
        
        Args:
            cache_dir: Directory to cache datasets (default: ~/.cache/huggingface)
            token: HuggingFace access token (or from HF_TOKEN env var)
        """
        self.cache_dir = cache_dir
        self.token = token or os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
        
        # Try to login if token is available
        if self.token:
            try:
                from huggingface_hub import login
                login(token=self.token, add_to_git_credential=False)
                logger.info("Authenticated with HuggingFace using token")
            except Exception as e:
                logger.warning(f"Could not authenticate with token: {e}")

    def download(self, dataset_id: str, output_path: str, split: Optional[str] = None) -> bool:
        """
        Download a HuggingFace dataset.
        
        Args:
            dataset_id: HuggingFace dataset identifier (e.g., "username/dataset-name")
            output_path: Directory to save the dataset
            split: Dataset split to download (e.g., "train", "test")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from datasets import load_dataset
            from huggingface_hub import login
            
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading HuggingFace dataset: {dataset_id} to {output_path}")
            
            # Try to load dataset - handle gated datasets
            try:
                # Handle dataset with config version (e.g., "dataset_name:3.0.0")
                if ':' in dataset_id:
                    dataset_name, config_name = dataset_id.split(':', 1)
                    dataset = load_dataset(
                        dataset_name,
                        config_name,
                        cache_dir=self.cache_dir,
                        token=self.token
                    )
                else:
                # Use token if available
                dataset = load_dataset(
                    dataset_id, 
                    cache_dir=self.cache_dir,
                    token=self.token
                )
            except Exception as e:
                error_msg = str(e).lower()
                if "gated" in error_msg or "authentication" in error_msg or "401" in str(e):
                    logger.warning(
                        f"Dataset {dataset_id} is gated and requires authentication."
                    )
                    logger.info(
                        f"Please visit https://huggingface.co/datasets/{dataset_id} to accept terms."
                    )
                    logger.info(
                        "Then authenticate using one of these methods:\n"
                        "  1. Set environment variable: set HF_TOKEN=your_token_here\n"
                        "  2. Use Python: from huggingface_hub import login; login(token='your_token')\n"
                        "  3. Get token from: https://huggingface.co/settings/tokens"
                    )
                    return False
                raise
            
            # Save dataset
            if split:
                if split in dataset:
                    dataset[split].to_json(f"{output_path}/{split}.jsonl")
                    logger.info(f"Saved {split} split to {output_path}")
                else:
                    logger.warning(f"Split '{split}' not found. Available splits: {list(dataset.keys())}")
                    # Save all splits
                    for split_name in dataset.keys():
                        dataset[split_name].to_json(f"{output_path}/{split_name}.jsonl")
            else:
                # Save all splits
                for split_name in dataset.keys():
                    dataset[split_name].to_json(f"{output_path}/{split_name}.jsonl")
            
            logger.info(f"Successfully downloaded {dataset_id}")
            return True
            
        except ImportError:
            logger.error("datasets package not installed. Install with: pip install datasets")
            return False
        except Exception as e:
            logger.error(f"Error downloading HuggingFace dataset {dataset_id}: {e}")
            return False

    def validate_dataset(self, dataset_path: str) -> bool:
        """
        Validate downloaded dataset.
        
        Args:
            dataset_path: Path to the dataset directory or file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            path = Path(dataset_path)
            if not path.exists():
                logger.error(f"Dataset path not found: {dataset_path}")
                return False
            
            # Check for JSONL files
            jsonl_files = list(path.glob("*.jsonl"))
            if not jsonl_files:
                logger.warning(f"No JSONL files found in {dataset_path}")
                return False
            
            logger.info(f"Dataset validation passed: {dataset_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating dataset {dataset_path}: {e}")
            return False

