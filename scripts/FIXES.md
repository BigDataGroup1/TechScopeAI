# Downloader Fixes Applied

## Issues Fixed

### 1. Kaggle Downloader
- **Problem**: Downloaded files were in subdirectories or had different names than expected
- **Fix**: Added logic to find and rename CSV files after extraction. If the expected file doesn't exist, it searches for CSV files in the directory and uses the largest one.

### 2. GitHub Downloader
- **Problem**: 
  - 404 errors for repos that might use "master" instead of "main"
  - Windows file access permission errors with git operations
- **Fix**: 
  - Now tries multiple branches (main, master) automatically
  - Better error handling for Windows file locks
  - Improved ZIP extraction with temp directory to avoid conflicts
  - Removes existing directories before download to prevent permission issues

### 3. HuggingFace Downloader
- **Problem**: Gated datasets require authentication but error wasn't clear
- **Fix**: Added detection for gated datasets with clear instructions on how to authenticate using `huggingface-cli login`

### 4. Configuration Updates
- **Problem**: Some GitHub repos had incorrect names or didn't exist
- **Fix**: Updated repo names to correct casing and added manual URLs for patent guides and pitch templates

## Known Limitations

1. **AdImageNet (HuggingFace)**: Requires authentication - run `huggingface-cli login` first
2. **Mendeley datasets**: May require manual download - the API endpoint might need adjustment
3. **Some GitHub repos**: May still fail if they don't exist or are private - check manually

## Next Steps

1. For gated HuggingFace datasets, authenticate first:
   ```bash
   huggingface-cli login
   ```

2. For Mendeley datasets that fail, download manually from the provided URL

3. Run the downloader again:
   ```bash
   python scripts/download_datasets.py
   ```


