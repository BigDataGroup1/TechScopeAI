"""Kaggle dataset downloader."""

import os
import subprocess
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class KaggleDownloader:
    """Download datasets from Kaggle using Kaggle API."""

    def __init__(self, kaggle_username: Optional[str] = None, kaggle_key: Optional[str] = None):
        """
        Initialize Kaggle downloader.
        
        Args:
            kaggle_username: Kaggle username (or from KAGGLE_USERNAME env var)
            kaggle_key: Kaggle API key (or from KAGGLE_KEY env var)
        """
        self.username = kaggle_username or os.getenv("KAGGLE_USERNAME")
        self.key = kaggle_key or os.getenv("KAGGLE_KEY")
        
        # Check for kaggle.json in ~/.kaggle/
        kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
        if kaggle_config.exists():
            logger.info(f"Found Kaggle config at {kaggle_config}")
        elif not (self.username and self.key):
            logger.warning(
                "No Kaggle credentials found. Please set KAGGLE_USERNAME and KAGGLE_KEY "
                "environment variables or create ~/.kaggle/kaggle.json"
            )

    def download(self, dataset_id: str, output_path: str, unzip: bool = True) -> bool:
        """
        Download a Kaggle dataset.
        
        Args:
            dataset_id: Kaggle dataset identifier (e.g., "username/dataset-name")
            output_path: Path to save the dataset
            unzip: Whether to unzip the downloaded file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading Kaggle dataset: {dataset_id} to {output_path}")
            
            # Use kaggle CLI if available
            cmd = ["kaggle", "datasets", "download", "-d", dataset_id, "-p", str(output_dir)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                # Try alternative: pip install kaggle and use Python API
                logger.warning("Kaggle CLI not found, trying Python API...")
                try:
                    from kaggle.api.kaggle_api_extended import KaggleApi
                    api = KaggleApi()
                    api.authenticate()
                    api.dataset_download_files(dataset_id, path=str(output_dir), unzip=unzip)
                    logger.info(f"Successfully downloaded {dataset_id}")
                    return True
                except ImportError:
                    logger.error("kaggle package not installed. Install with: pip install kaggle")
                    return False
                except Exception as e:
                    logger.error(f"Failed to download via Python API: {e}")
                    return False
            
            if unzip and result.returncode == 0:
                # Unzip if needed
                zip_files = list(output_dir.glob("*.zip"))
                for zip_file in zip_files:
                    import zipfile
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(output_dir)
                    zip_file.unlink()  # Remove zip file after extraction
                
                # If output_path is a specific file, try to find it
                expected_file = Path(output_path)
                if expected_file.suffix == '.csv' and not expected_file.exists():
                    # Look for CSV files in the directory
                    csv_files = list(output_dir.glob("*.csv"))
                    if csv_files:
                        # If multiple CSVs, use the largest one or first one
                        if len(csv_files) == 1:
                            csv_files[0].rename(expected_file)
                        else:
                            # Find the main dataset file (usually the largest)
                            largest = max(csv_files, key=lambda p: p.stat().st_size)
                            largest.rename(expected_file)
                            logger.info(f"Found and renamed main CSV file: {largest.name} -> {expected_file.name}")
            
            logger.info(f"Successfully downloaded {dataset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading Kaggle dataset {dataset_id}: {e}")
            return False

    def validate_dataset(self, dataset_path: str, required_columns: list = None) -> bool:
        """
        Validate downloaded dataset.
        
        Args:
            dataset_path: Path to the dataset file
            required_columns: List of required column names
            
        Returns:
            True if valid, False otherwise
        """
        try:
            import pandas as pd
            
            path = Path(dataset_path)
            if not path.exists():
                # Try to find CSV files in the parent directory
                parent_dir = path.parent
                csv_files = list(parent_dir.glob("*.csv"))
                if csv_files:
                    logger.warning(f"Expected file {dataset_path} not found, but found {len(csv_files)} CSV files in directory")
                    # Use the first/largest CSV found
                    path = csv_files[0] if len(csv_files) == 1 else max(csv_files, key=lambda p: p.stat().st_size)
                    logger.info(f"Validating found file: {path}")
                else:
                    logger.error(f"Dataset file not found: {dataset_path}")
                    return False
            
            # Try to read the file
            if path.suffix == '.csv':
                df = pd.read_csv(path, nrows=5)  # Read first 5 rows for validation
            elif path.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(path, nrows=5)
            else:
                logger.warning(f"Unknown file type: {path.suffix}")
                return True  # Assume valid if we can't check
            
            # Check required columns
            if required_columns:
                missing = set(required_columns) - set(df.columns)
                if missing:
                    logger.error(f"Missing required columns: {missing}")
                    return False
            
            logger.info(f"Dataset validation passed: {dataset_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating dataset {dataset_path}: {e}")
            return False

