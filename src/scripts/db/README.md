# Cloud SQL Database Management Scripts

This directory contains PowerShell scripts for managing PostgreSQL indexes and monitoring Cloud SQL database status.

## Scripts

### `monitor_index_progress.ps1`
Real-time monitoring of index creation progress. Shows live progress bars and percentage complete.

**Usage:**
```powershell
.\venv\Scripts\Activate.ps1
$env:CLOUD_SQL_PASSWORD="your_password"
.\src\scripts\db\monitor_index_progress.ps1
```

### `create_vector_indexes.ps1`
Creates vector indexes directly via SQL. This is faster than using pg_restore for indexes.

**Usage:**
```powershell
.\venv\Scripts\Activate.ps1
$env:CLOUD_SQL_PASSWORD="your_password"
.\src\scripts\db\create_vector_indexes.ps1
```

**Note:** Index creation can take 1-4 hours for ~2M documents. The `competitors_corpus` index alone may take 2-3 hours.

### `check_what_exists.ps1`
Checks what data and indexes already exist in Cloud SQL. Shows tables, row counts, and all indexes.

**Usage:**
```powershell
.\venv\Scripts\Activate.ps1
$env:CLOUD_SQL_PASSWORD="your_password"
.\src\scripts\db\check_what_exists.ps1
```

## Prerequisites

1. **Cloud SQL Proxy** must be running:
   ```powershell
   .\cloud_sql_proxy.exe -instances=techscopeai:us-central1:techscope-db=tcp:5433
   ```

2. **Virtual environment** must be activated and dependencies installed:
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Environment variable** for password (optional, will prompt if not set):
   ```powershell
   $env:CLOUD_SQL_PASSWORD="your_password"
   ```

## Running from Project Root

All scripts should be run from the project root directory (`TechScopeAI/`). The scripts automatically detect the project root and set up Python paths correctly.

## Collections

These scripts manage indexes for the following collections:
- `competitors_corpus`
- `marketing_corpus`
- `ip_policy_corpus`
- `policy_corpus`
- `job_roles_corpus`
- `pitch_examples_corpus`



