# Getting Started Guide - TechScopeAI Agents & Cloud SQL

Complete guide to set up and run TechScopeAI agents with Cloud SQL integration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Cloud SQL Connection Setup](#cloud-sql-connection-setup)
4. [Install Dependencies](#install-dependencies)
5. [Verify Cloud SQL Connection](#verify-cloud-sql-connection)
6. [Start Agents & Streamlit](#start-agents--streamlit)
7. [Verify Everything Works](#verify-everything-works)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **PostgreSQL Client** (for Cloud SQL Proxy)
   - Windows: Download from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)
   - Or use Cloud SQL Proxy (included in project)

3. **Git** (if cloning repository)

### Required Accounts & Access

1. **Google Cloud Platform (GCP) Account**
   - Cloud SQL instance created
   - Cloud SQL password
   - Instance connection name

2. **OpenAI API Key**
   - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

3. **Optional: Image API Keys** (for better image search)
   - Pexels API Key: [Pexels API](https://www.pexels.com/api/)
   - Unsplash Access Key: [Unsplash Developers](https://unsplash.com/developers)

---

## Environment Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Create `.env` File

Create a `.env` file in the project root with the following variables:

```env
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Cloud SQL Configuration (REQUIRED)
CLOUD_SQL_PASSWORD=your_cloud_sql_password
CLOUD_SQL_HOST=localhost
CLOUD_SQL_PORT=5433
CLOUD_SQL_DB=techscope
CLOUD_SQL_USER=postgres

# Optional: Cloud SQL Connection Name (for Cloud Run)
# CLOUD_SQL_CONNECTION_NAME=project:region:instance

# Optional: Weaviate (for agents personalization)
WEAVIATE_URL=http://localhost:8081

# Optional: Image APIs (for better image search)
PEXELS_API_KEY=your_pexels_api_key
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
```

**Important:** Replace placeholder values with your actual credentials.

---

## Cloud SQL Connection Setup

### Option 1: Cloud SQL Proxy (Recommended for Local Development)

1. **Download Cloud SQL Proxy** (if not already in project)
   - Windows: Download from [Cloud SQL Proxy Releases](https://github.com/GoogleCloudPlatform/cloud-sql-proxy/releases)
   - Or use the included `cloud_sql_proxy.exe` in project root

2. **Get Your Cloud SQL Instance Connection Name**
   - Format: `project-id:region:instance-name`
   - Find in GCP Console → SQL → Your Instance → Overview

3. **Start Cloud SQL Proxy**
   ```bash
   # Windows
   cloud_sql_proxy.exe -instances=YOUR_CONNECTION_NAME=tcp:5433
   
   # Example:
   cloud_sql_proxy.exe -instances=my-project:us-central1:techscope-db=tcp:5433
   ```

4. **Keep Proxy Running**
   - Leave this terminal window open
   - The proxy forwards `localhost:5433` to your Cloud SQL instance

### Option 2: Direct Connection (Production)

For Cloud Run or production deployments, use Unix socket connection:

```env
DATABASE_URL=postgresql://postgres:password@/techscope?host=/cloudsql/PROJECT:REGION:INSTANCE
```

---

## Install Dependencies

### 1. Install Python Packages

```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### 2. Verify Key Dependencies

```bash
# Check if critical packages are installed
python -c "import openai; print('OpenAI:', openai.__version__)"
python -c "import psycopg2; print('PostgreSQL:', 'OK')"
python -c "from ddgs import DDGS; print('Web Search:', 'OK')"
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
```

---

## Verify Cloud SQL Connection

### Test Database Connection

```bash
# Test Cloud SQL connection
python -c "from src.rag.db_config import get_database_url; print('Database URL:', get_database_url().split('@')[-1])"
```

Expected output:
```
Database URL: localhost:5433/techscope
```

### Test VectorStore Connection

```bash
# Test VectorStore initialization
python -c "from src.rag.embeddings import EmbeddingModel; from src.rag.vector_store import VectorStore; em = EmbeddingModel(); vs = VectorStore(embedding_model=em); print('[OK] VectorStore connected to Cloud SQL')"
```

Expected output:
```
[OK] VectorStore connected to Cloud SQL
```

### Check Database Status in Streamlit

When you start Streamlit, check the sidebar:
- Should show: **✅ Cloud SQL (GCP)**
- Connection: `localhost:5433/techscope`
- Document count (if data is indexed)

---

## Start Agents & Streamlit

### Method 1: Using main.py (Recommended)

```bash
# Start Streamlit web interface
python main.py web

# Or start CLI mode
python main.py cli
```

### Method 2: Direct Streamlit Command

```bash
# Make sure you're in the project root directory
streamlit run src/api/chat_interface.py
```

### What Happens When Starting

1. **Environment Loading**
   - Loads `.env` file
   - Validates required environment variables

2. **Database Connection**
   - Connects to Cloud SQL via proxy (localhost:5433)
   - Initializes pgvector extension
   - Checks collections

3. **Agent Initialization**
   - Loads RAG components (VectorStore, Retriever)
   - Initializes MCP tools (web search, image search, etc.)
   - Sets up all agents (Pitch, Marketing, Patent, Policy, Team, Supervisor)

4. **Streamlit Server**
   - Starts on `http://localhost:8501`
   - Opens in your default browser

---

## Verify Everything Works

### 1. Test MCP Tools

```bash
# Test MCP web search
python test_mcp_web_search.py
```

Expected: `[SUCCESS] All tests passed!`

### 2. Test Agent Initialization

```bash
# Test agent initialization
python -c "from src.rag.embedder import Embedder; from src.rag.vector_store import VectorStore; from src.rag.retriever import Retriever; from src.agents.pitch_agent import PitchAgent; e = Embedder(); vs = VectorStore(embedding_model=e.get_embedding_model()); r = Retriever(vs, e); a = PitchAgent(r); print('[OK] Agent initialized')"
```

### 3. Test in Streamlit UI

1. **Open Streamlit** (should auto-open at `http://localhost:8501`)

2. **Check Sidebar:**
   - Database Status: ✅ Cloud SQL (GCP)
   - Connection active
   - Document count (if indexed)

3. **Test Agent Query:**
   - Enter company details in sidebar
   - Ask a question like: "Generate a pitch deck for my startup"
   - Check sources show "Cloud SQL Collection"

4. **Test Web Search Fallback:**
   - Ask: "What are the latest marketing trends?"
   - Should see web URLs in sources
   - Logs show: "Found X relevant web results"

---

## Troubleshooting

### Issue: "CLOUD_SQL_PASSWORD not found"

**Solution:**
```bash
# Check .env file exists and has CLOUD_SQL_PASSWORD
# Make sure .env is in project root (same directory as main.py)
```

### Issue: "Failed to connect to PostgreSQL"

**Solutions:**
1. **Check Cloud SQL Proxy is running:**
   ```bash
   # Should see proxy running in another terminal
   cloud_sql_proxy.exe -instances=YOUR_CONNECTION_NAME=tcp:5433
   ```

2. **Verify connection details:**
   ```bash
   # Test connection
   python -c "from src.rag.db_config import get_database_url; print(get_database_url())"
   ```

3. **Check firewall/network:**
   - Ensure port 5433 is not blocked
   - Verify Cloud SQL instance allows connections

### Issue: "ModuleNotFoundError: No module named 'src.rag'"

**Solution:**
```bash
# Make sure you're in project root directory
cd D:\Bigdata_Assig\TechScopeAI

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Issue: "Web search not available"

**Solution:**
```bash
# Install ddgs package
pip install ddgs

# Verify installation
python -c "from ddgs import DDGS; print('OK')"
```

### Issue: "OPENAI_API_KEY not found"

**Solution:**
```bash
# Check .env file has OPENAI_API_KEY
# Verify .env is loaded:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

### Issue: "No documents indexed" in Streamlit

**Solution:**
```bash
# Index data into Cloud SQL
python src/rag/setup_rag.py

# Or process and index your data
python scripts/processing/process_pitch_data.py
python scripts/processing/build_rag_index.py
```

### Issue: Agents show "Local PostgreSQL" instead of "Cloud SQL"

**Solution:**
- Check `.env` file has `CLOUD_SQL_PASSWORD` set
- Verify Cloud SQL Proxy is running
- Check logs for connection errors

---

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] `.env` file created with all required variables
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Cloud SQL Proxy running (if using local development)
- [ ] Cloud SQL connection tested
- [ ] MCP tools tested (`python test_mcp_web_search.py`)
- [ ] Streamlit started (`python main.py web`)
- [ ] Database status shows "Cloud SQL (GCP)" in sidebar
- [ ] Agent query returns results

---

## Common Commands Reference

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start Cloud SQL Proxy
cloud_sql_proxy.exe -instances=PROJECT:REGION:INSTANCE=tcp:5433

# Start Streamlit
python main.py web

# Test MCP web search
python test_mcp_web_search.py

# Test database connection
python -c "from src.rag.db_config import get_database_url; print(get_database_url())"

# Test VectorStore
python -c "from src.rag.embeddings import EmbeddingModel; from src.rag.vector_store import VectorStore; em = EmbeddingModel(); vs = VectorStore(embedding_model=em); print('OK')"
```

---

## Next Steps

1. **Index Data:** Process and index your data into Cloud SQL
2. **Test Agents:** Try different agents (Marketing, Patent, Policy, Team)
3. **Use MCP Tools:** Agents automatically use web search when needed
4. **Build FastAPI:** Next phase - expose agents as REST API
5. **React Frontend:** Build modern UI on top of FastAPI

---

## Support

If you encounter issues:

1. Check logs in terminal/console
2. Verify all environment variables are set
3. Ensure Cloud SQL Proxy is running
4. Test individual components (database, MCP, agents)
5. Review `HOW_TO_VERIFY_WEB_SEARCH.md` for web search verification
6. Review `CLOUD_SQL_INTEGRATION.md` for Cloud SQL details

---

## Architecture Overview

```
┌─────────────────┐
│   Streamlit UI  │
└────────┬────────┘
         │
┌────────▼────────┐
│     Agents      │
│  (Pitch, etc.)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│  RAG  │ │  MCP  │
│(Cloud │ │ Tools │
│  SQL) │ │(Web,  │
│       │ │Image) │
└───────┘ └───────┘
```

- **RAG**: Retrieves from Cloud SQL (PostgreSQL + pgvector)
- **MCP Tools**: Web search, image search, patent search (external APIs)
- **Agents**: Use both RAG and MCP tools to answer questions

---

**Last Updated:** December 2024
**Version:** 1.0

