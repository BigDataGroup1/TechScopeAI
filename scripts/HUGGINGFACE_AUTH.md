# HuggingFace Authentication Guide

## Problem
Some HuggingFace datasets (like `AdImageNet`) are "gated" and require authentication to download.

## Solution Options

### Option 1: Use Environment Variable (Recommended)

1. Get your HuggingFace token:
   - Visit: https://huggingface.co/settings/tokens
   - Create a new token (read access is enough)
   - Copy the token

2. Set environment variable:
   ```powershell
   # Windows PowerShell
   $env:HF_TOKEN="your_token_here"
   
   # Or permanently (PowerShell)
   [System.Environment]::SetEnvironmentVariable('HF_TOKEN', 'your_token_here', 'User')
   ```

3. Run the downloader:
   ```bash
   python scripts/download_datasets.py
   ```

### Option 2: Use Python Login

Create a small script `auth_hf.py`:
```python
from huggingface_hub import login

# Get token from: https://huggingface.co/settings/tokens
token = "your_token_here"
login(token=token)
print("Authenticated!")
```

Run it:
```bash
python auth_hf.py
```

Then run the downloader.

### Option 3: Skip Gated Datasets

If you don't need the gated datasets, you can skip them. The downloader will continue with other datasets.

### Option 4: Manual Download

For gated datasets, you can:
1. Visit the dataset page: https://huggingface.co/datasets/PeterBrendan/AdImageNet
2. Accept the terms
3. Download manually
4. Place files in `data/raw/marketing/ad_image_net/`

## Getting Your Token

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it a name (e.g., "TechScopeAI")
4. Select "Read" access
5. Copy the token (starts with `hf_...`)

## Verify Authentication

Check if you're authenticated:
```python
from huggingface_hub import whoami
print(whoami())
```

If it shows your username, you're authenticated!


