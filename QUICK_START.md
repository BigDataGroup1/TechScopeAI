# Quick Start - TechScopeAI

## 🚀 Fast Setup (5 Minutes)

### 1. Setup Environment
```bash
# Create and activate venv
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure `.env` File
Create `.env` in project root:
```env
OPENAI_API_KEY=your_key_here
CLOUD_SQL_PASSWORD=your_password_here
CLOUD_SQL_HOST=localhost
CLOUD_SQL_PORT=5433
CLOUD_SQL_DB=techscope
CLOUD_SQL_USER=postgres
```

### 3. Start Cloud SQL Proxy
```bash
# In a separate terminal (keep running)
cloud_sql_proxy.exe -instances=PROJECT:REGION:INSTANCE=tcp:5433
```

### 4. Start Application
```bash
# Start Streamlit
python main.py web
```

### 5. Verify
- Open `http://localhost:8501`
- Check sidebar shows: **✅ Cloud SQL (GCP)**
- Ask a question to test agents

---

## ✅ Verification Commands

```bash
# Test database connection
python -c "from src.rag.db_config import get_database_url; print('OK')"

# Test MCP web search
python test_mcp_web_search.py

# Test agent initialization
python -c "from src.rag.embedder import Embedder; from src.rag.vector_store import VectorStore; from src.rag.retriever import Retriever; from src.agents.pitch_agent import PitchAgent; e = Embedder(); vs = VectorStore(embedding_model=e.get_embedding_model()); r = Retriever(vs, e); a = PitchAgent(r); print('OK')"
```

---

## 🔧 Common Issues

| Issue | Solution |
|-------|----------|
| `CLOUD_SQL_PASSWORD not found` | Check `.env` file exists and has password |
| `Failed to connect` | Start Cloud SQL Proxy in separate terminal |
| `ModuleNotFoundError` | Run from project root, activate venv |
| `Web search not available` | `pip install ddgs` |

---

## 📚 Full Documentation

- **Complete Guide:** `GETTING_STARTED.md`
- **Cloud SQL Details:** `CLOUD_SQL_INTEGRATION.md`
- **Web Search Verification:** `HOW_TO_VERIFY_WEB_SEARCH.md`
- **MCP Server:** `MCP_SERVER_IMPLEMENTATION.md`

---

**Need Help?** Check `GETTING_STARTED.md` for detailed troubleshooting.

