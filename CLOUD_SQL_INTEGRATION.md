# Cloud SQL Integration - Default Configuration

## Overview

The project has been updated to **default to Cloud SQL** for all RAG operations. Local PostgreSQL is only used when explicitly requested via the `use_local=True` parameter.

## Changes Made

### 1. New Database Configuration Module (`src/rag/db_config.py`)

Created a helper function `get_database_url()` that:
- **Defaults to Cloud SQL** (via `CLOUD_SQL_PASSWORD` environment variable)
- Only uses local PostgreSQL when `use_local=True` is explicitly set
- Supports explicit `DATABASE_URL` environment variable (highest priority)

**Priority Order:**
1. Explicit `database_url` parameter
2. `DATABASE_URL` environment variable
3. Cloud SQL (via `CLOUD_SQL_PASSWORD`) - **DEFAULT**
4. Local PostgreSQL (only if `use_local=True`)

### 2. Updated VectorStore (`src/rag/vector_store.py`)

- Added `use_local` parameter (defaults to `False`)
- Now uses `get_database_url()` helper for connection string resolution
- Defaults to Cloud SQL unless explicitly told otherwise

**Usage:**
```python
# Cloud SQL (default)
vector_store = VectorStore(embedding_model=embedding_model)

# Local PostgreSQL (explicit)
vector_store = VectorStore(embedding_model=embedding_model, use_local=True)

# Explicit URL (overrides everything)
vector_store = VectorStore(database_url="postgresql://...")
```

### 3. Updated Files

- ✅ `src/rag/vector_store.py` - Defaults to Cloud SQL
- ✅ `src/rag/db_config.py` - New helper module
- ✅ `main.py` - Updated to use Cloud SQL by default
- ✅ `src/rag/setup_rag.py` - Updated to use Cloud SQL by default

### 4. Files That Still Need Updates

The following files reference non-existent classes (`WeaviateStore`, `Embedder`, `Retriever`) and need to be updated:

- ⚠️ `src/api/chat_interface.py` - Uses `WeaviateStore` (should use `VectorStore`)
- ⚠️ `src/agents/*.py` - Import `Retriever` from `..rag.retriever` (should use `RAGRetriever`)

## Environment Variables

### Cloud SQL (Default)

Set these environment variables for Cloud SQL:

```powershell
# Cloud SQL password (required for default Cloud SQL connection)
$env:CLOUD_SQL_PASSWORD="YourPassword"

# Optional: Override defaults
$env:CLOUD_SQL_HOST="localhost"      # Default: localhost (via proxy)
$env:CLOUD_SQL_PORT="5433"           # Default: 5433
$env:CLOUD_SQL_DB="techscope"        # Default: techscope
$env:CLOUD_SQL_USER="postgres"       # Default: postgres

# OR use explicit DATABASE_URL (highest priority)
$env:DATABASE_URL="postgresql://postgres:password@localhost:5433/techscope"
```

### Local PostgreSQL (Optional)

Only needed if you want to use local PostgreSQL:

```powershell
# Set use_local=True in code, OR set these env vars:
$env:LOCAL_POSTGRES_PASSWORD="postgres"
$env:LOCAL_POSTGRES_HOST="localhost"
$env:LOCAL_POSTGRES_PORT="5432"
$env:LOCAL_POSTGRES_DB="techscope"
$env:LOCAL_POSTGRES_USER="postgres"
```

## Usage Examples

### Default (Cloud SQL)

```python
from src.rag.embeddings import EmbeddingModel
from src.rag.vector_store import VectorStore

# Automatically uses Cloud SQL
embedding_model = EmbeddingModel()
vector_store = VectorStore(embedding_model=embedding_model)
```

### Explicit Local PostgreSQL

```python
# Only if you explicitly want local
vector_store = VectorStore(embedding_model=embedding_model, use_local=True)
```

### Explicit Database URL

```python
# Override with explicit URL
vector_store = VectorStore(
    database_url="postgresql://user:pass@host:port/db",
    embedding_model=embedding_model
)
```

## Cloud SQL Proxy Setup

For local development, you need Cloud SQL Proxy running:

```powershell
# Start Cloud SQL Proxy (keep running in separate terminal)
.\cloud_sql_proxy.exe -instances=techscopeai:us-central1:techscope-db=tcp:5433

# Set password
$env:CLOUD_SQL_PASSWORD="YourPassword"

# Now all agents will use Cloud SQL by default
python main.py
```

## Migration Checklist

- [x] Create `db_config.py` helper module
- [x] Update `VectorStore` to default to Cloud SQL
- [x] Update `main.py` to use Cloud SQL
- [x] Update `setup_rag.py` to use Cloud SQL
- [ ] Update `chat_interface.py` (needs `WeaviateStore` → `VectorStore` migration)
- [ ] Update agent files (need `Retriever` → `RAGRetriever` migration)
- [ ] Update test scripts
- [ ] Update documentation

## Important Notes

1. **No Fallback to Local**: The system will NOT fallback to local PostgreSQL. Cloud SQL is the default, and local is opt-in only.

2. **Environment Variable Priority**: `DATABASE_URL` takes highest priority if set.

3. **Cloud SQL Proxy Required**: For local development, Cloud SQL Proxy must be running on port 5433.

4. **Password URL Encoding**: Passwords with special characters (like `@`) are automatically URL-encoded.

5. **Breaking Changes**: Code that relied on defaulting to local PostgreSQL will now use Cloud SQL. Set `use_local=True` to restore old behavior.

## Troubleshooting

### Error: "No database configuration found"

**Solution**: Set `CLOUD_SQL_PASSWORD` environment variable:
```powershell
$env:CLOUD_SQL_PASSWORD="YourPassword"
```

### Error: "Connection refused" or "Connection timeout"

**Solution**: Make sure Cloud SQL Proxy is running:
```powershell
.\cloud_sql_proxy.exe -instances=techscopeai:us-central1:techscope-db=tcp:5433
```

### Want to use local PostgreSQL instead?

**Solution**: Explicitly set `use_local=True`:
```python
vector_store = VectorStore(embedding_model=embedding_model, use_local=True)
```


