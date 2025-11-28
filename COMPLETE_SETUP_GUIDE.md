# Complete Setup Guide - TechScopeAI Data Downloader

## ✅ **What's Done**

1. ✅ **StackOverflow removed** from config (you have better job data)
2. ✅ **Skip logic added** - Won't re-download existing data
3. ✅ **All broken datasets fixed** in config
4. ✅ **New downloaders created** (Hacker News, RSS, Reddit, Article Scraper)

---

## 🚀 **How to Run**

### **Download All Data:**
```bash
./venv/bin/python scripts/download_datasets.py
```

### **Download Specific Categories:**
```bash
# Only competitive data
./venv/bin/python scripts/download_datasets.py --agents competitive

# Only pitch data
./venv/bin/python scripts/download_datasets.py --agents pitch

# Multiple categories
./venv/bin/python scripts/download_datasets.py --agents competitive pitch marketing
```

---

## ⏭️ **Skip Logic (NEW!)**

The script now **automatically skips** data that already exists!

**What happens:**
- ✅ Checks if files/directories exist with content
- ✅ Skips download if data is already there
- ✅ Shows: `⏭️  Skipping {name} - data already exists`
- ✅ Safe to run multiple times!

**Example output:**
```
Downloading hacker-news-startups...
⏭️  Skipping hacker-news-startups - data already exists
✓ Successfully downloaded hacker-news-startups
```

---

## 📊 **Current Status**

### **Working Datasets (28+):**
- ✅ Hacker News stories
- ✅ RSS feeds (TechCrunch, VentureBeat)
- ✅ Kaggle datasets (with credentials)
- ✅ HuggingFace datasets
- ✅ GitHub repos
- ✅ Web scraping (YC blogs, investor blogs, etc.)

### **Needs Manual Setup:**
- ⚠️ **AdImageNet** - Needs HuggingFace token (optional)
- ⚠️ **Reddit** - Needs API credentials (optional, commented out)

### **Removed/Fixed:**
- ❌ StackOverflow - Removed (you have better job data)
- ❌ Deprecated HuggingFace datasets - Commented out
- ❌ Broken GitHub repos - Commented out
- ❌ Product Hunt - Commented out (blocks scrapers)

---

## 🔧 **Optional Setup**

### **1. HuggingFace Token (for gated datasets):**
```bash
# Get token from: https://huggingface.co/settings/tokens
# Add to .env:
echo "HF_TOKEN=your_token_here" >> .env
```

### **2. Reddit API (if you want Reddit data):**
```bash
# Get credentials from: https://www.reddit.com/prefs/apps
# Add to .env:
echo "REDDIT_CLIENT_ID=your_id" >> .env
echo "REDDIT_CLIENT_SECRET=your_secret" >> .env
# Then uncomment reddit-startups in config
```

---

## 📁 **Where Data Goes**

All data saved to: `data/raw/`

```
data/raw/
├── competitive/     # Startup intelligence (Hacker News, RSS, etc.)
├── marketing/       # Marketing datasets
├── pitch/           # Pitch examples, investor blogs
├── ip_legal/        # Legal/IP data
├── policy/          # Policy documents
└── team/            # Job postings, hiring guides
```

---

## 🎯 **Quick Reference**

### **Main Script:**
```bash
./venv/bin/python scripts/download_datasets.py
```

### **Config File:**
`scripts/config/dataset_config.yaml`

### **Skip Existing Data:**
✅ Automatic! No flags needed.

### **Force Re-download:**
Delete the directory/file first, then run:
```bash
rm -rf data/raw/competitive/hackernews/
./venv/bin/python scripts/download_datasets.py --agents competitive
```

---

## 📋 **What Gets Downloaded**

### **Competitive (Startup Intelligence):**
- Hacker News stories (13+ startup-related)
- TechCrunch RSS articles
- VentureBeat RSS articles
- YC Library articles
- Startup blogs (YC, Paul Graham)
- Indie Hackers content
- News datasets (BBC, AG News)
- Kaggle startup datasets

### **Pitch:**
- Pitch examples
- Investor blogs (a16z, Sequoia, First Round)
- Startup failure post-mortems
- YC pitch templates
- Podcast pages

### **Marketing:**
- Ad creative examples
- Review datasets (IMDB, Yelp, Amazon)

### **IP/Legal:**
- Privacy QA datasets
- OSS policies
- Patent guides

### **Policy:**
- Privacy compliance data
- Historical privacy policies

### **Team:**
- Job postings
- Job skill sets

---

## ✅ **That's It!**

Just run:
```bash
./venv/bin/python scripts/download_datasets.py
```

The script will:
1. ✅ Skip existing data automatically
2. ✅ Download only what's missing
3. ✅ Show progress with ✓ or ✗
4. ✅ Print summary at the end

**Safe to run multiple times!** It won't re-download what you already have.

