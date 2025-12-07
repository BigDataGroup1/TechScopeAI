"""Download all competitive-analysis datasets for TechScope AI.

This script focuses ONLY on the `competitive` datasets section from
`scripts/config/dataset_config.yaml` and uses the existing downloaders:
- KaggleDownloader
- HuggingFaceDownloader

Usage (from project root):
    python scripts/download_competitive_datasets.py
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

import yaml

# Ensure we can import from scripts/downloaders
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from downloaders import (  # type: ignore
    KaggleDownloader,
    HuggingFaceDownloader,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "scripts/config/dataset_config.yaml") -> dict:
    """Load dataset configuration from YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_data_exists(output_path: str, min_files: int = 1) -> bool:
    """Check if data already exists at the output path."""
    path = Path(output_path)

    # File path (csv/json/etc.)
    if output_path.endswith((".csv", ".json", ".jsonl", ".txt", ".html")):
        return path.exists() and path.stat().st_size > 0

    # Directory path
    if path.exists() and path.is_dir():
        files = [f for f in path.rglob("*") if f.is_file() and not f.name.startswith(".")]
        if len(files) >= min_files:
            total_size = sum(f.stat().st_size for f in files)
            return total_size > 0

    return False


def download_kaggle_dataset(dataset_config: dict, downloader: KaggleDownloader) -> bool:
    """Download a Kaggle dataset."""
    dataset_id = dataset_config["dataset_id"]
    output_path = dataset_config["output_path"]
    required_columns = dataset_config.get("required_columns")

    if check_data_exists(output_path):
        logger.info(
            f"⏭️  Skipping {dataset_config.get('name', dataset_id)} - "
            f"data already exists at {output_path}"
        )
        return True

    success = downloader.download(dataset_id, output_path)
    if success and required_columns:
        success = downloader.validate_dataset(output_path, required_columns)

    return success


def download_huggingface_dataset(
    dataset_config: dict, downloader: HuggingFaceDownloader
) -> bool:
    """Download a HuggingFace dataset."""
    dataset_id = dataset_config["dataset_id"]
    output_path = dataset_config["output_path"]

    if check_data_exists(output_path, min_files=1):
        logger.info(
            f"⏭️  Skipping {dataset_config.get('name', dataset_id)} - "
            f"data already exists at {output_path}"
        )
        return True

    success = downloader.download(dataset_id, output_path)
    if success:
        success = downloader.validate_dataset(output_path)

    return success


def download_all_competitive(config: dict) -> Dict[str, bool]:
    """Download all competitive datasets from config."""
    results: Dict[str, bool] = {}

    kaggle_dl = KaggleDownloader()
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    hf_dl = HuggingFaceDownloader(token=hf_token)

    competitive_datasets: List[dict] = config.get("datasets", {}).get("competitive", [])

    logger.info("\n" + "=" * 60)
    logger.info("Processing COMPETITIVE datasets")
    logger.info("=" * 60)

    for ds in competitive_datasets:
        name = ds["name"]
        source = ds["source"]
        logger.info(f"\nDownloading {name} from {source}...")

        try:
            if source == "kaggle":
                success = download_kaggle_dataset(ds, kaggle_dl)
            elif source == "huggingface":
                success = download_huggingface_dataset(ds, hf_dl)
            else:
                logger.warning(f"Source {source} not supported in competitive downloader.")
                success = False

            results[name] = success

            if success:
                logger.info(f"✓ Successfully downloaded {name}")
            else:
                logger.error(f"✗ Failed to download {name}")

        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"✗ Error downloading {name}: {exc}")
            results[name] = False

    return results


def print_summary(results: Dict[str, bool]) -> None:
    """Print a simple summary."""
    logger.info("\n" + "=" * 60)
    logger.info("COMPETITIVE DATASETS SUMMARY")
    logger.info("=" * 60)

    total = len(results)
    successful = sum(1 for ok in results.values() if ok)

    for name, ok in results.items():
        status = "✓" if ok else "✗"
        logger.info(f"  {status} {name}")

    logger.info(f"\nTotal: {successful}/{total} competitive datasets downloaded successfully")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download competitive-analysis datasets for TechScope AI"
    )
    parser.add_argument(
        "--config",
        default="scripts/config/dataset_config.yaml",
        help="Path to dataset configuration file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    results = download_all_competitive(config)
    print_summary(results)


if __name__ == "__main__":
    main()



