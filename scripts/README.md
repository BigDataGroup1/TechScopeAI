# Dataset Downloader Scripts

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# For HuggingFace gated datasets (optional):
# 1. Get token from https://huggingface.co/settings/tokens
# 2. Set environment variable:
#    PowerShell: $env:HF_TOKEN="your_token_here"
#    CMD: set HF_TOKEN=your_token_here

# Download all datasets
python scripts/download_datasets.py

# Download specific agents
python scripts/download_datasets.py --agents competitive marketing
```

## Authentication

Some datasets require authentication:
- **Kaggle**: Place `kaggle.json` in `~/.kaggle/` or set `KAGGLE_USERNAME` and `KAGGLE_KEY`
- **HuggingFace**: Set `HF_TOKEN` environment variable (see `HUGGINGFACE_AUTH.md` for details)

## Configuration

Edit `scripts/config/dataset_config.yaml` to modify dataset sources or output paths.

## Storage Location

All datasets are downloaded to `data/raw/` with the following structure:

- `data/raw/competitive/` - Startup/competitor datasets
- `data/raw/marketing/` - Ad copy and marketing datasets  
- `data/raw/ip_legal/` - IP and legal datasets
- `data/raw/policy/` - Privacy policy datasets
- `data/raw/team/` - Job/skills datasets
- `data/raw/pitch/` - Pitch examples

See `data/README.md` for detailed storage structure.

