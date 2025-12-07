# Cloud SQL Migration Guide

## Step-by-Step Migration Process

### Step 1: Create Cloud SQL Instance

```powershell
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create techscope-db `
  --database-version=POSTGRES_15 `
  --tier=db-n1-standard-1 `
  --region=us-central1 `
  --root-password=YourSecurePassword123! `
  --storage-type=SSD `
  --storage-size=100GB `
  --backup-start-time=03:00 `
  --enable-bin-log `
  --maintenance-window-day=SUN `
  --maintenance-window-hour=04
```

**Note:** Replace `YourSecurePassword123!` with a strong password.

### Step 2: Enable pgvector Extension

```powershell
# Connect to Cloud SQL
gcloud sql connect techscope-db --user=postgres

# Then run SQL:
CREATE DATABASE techscope;
\c techscope
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Step 3: Set Up Cloud SQL Proxy

```powershell
# Download Cloud SQL Proxy (if not already downloaded)
# Windows: https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe

# Get connection name
$CONNECTION_NAME = gcloud sql instances describe techscope-db --format="value(connectionName)"
echo "Connection name: $CONNECTION_NAME"

# Run proxy (use port 5433 to avoid conflict with local PostgreSQL on 5432)
# Keep this running in a separate terminal
.\cloud_sql_proxy.exe -instances=$CONNECTION_NAME=tcp:5433
```

### Step 4: Export Data from Local PostgreSQL

```powershell
# Export entire database
docker exec postgres-pgvector pg_dump -U postgres techscope > techscope_backup.sql

# Check file size
Get-Item techscope_backup.sql | Select-Object Name, Length
```

### Step 5: Import to Cloud SQL

```powershell
# Set password environment variable (replace with your Cloud SQL password)
$env:PGPASSWORD="YourSecurePassword123!"

# Import via Cloud SQL Proxy (running on port 5433)
psql -h localhost -p 5433 -U postgres -d techscope -f techscope_backup.sql

# Or if psql is not available, use pg_restore:
pg_restore -h localhost -p 5433 -U postgres -d techscope techscope_backup.sql
```

### Step 6: Verify Migration

```powershell
# Connect to Cloud SQL via proxy
psql -h localhost -p 5433 -U postgres -d techscope

# Check collections
SELECT 'competitors_corpus' as collection, COUNT(*) FROM competitors_corpus
UNION ALL SELECT 'marketing_corpus', COUNT(*) FROM marketing_corpus
UNION ALL SELECT 'ip_policy_corpus', COUNT(*) FROM ip_policy_corpus
UNION ALL SELECT 'policy_corpus', COUNT(*) FROM policy_corpus
UNION ALL SELECT 'job_roles_corpus', COUNT(*) FROM job_roles_corpus
UNION ALL SELECT 'pitch_examples_corpus', COUNT(*) FROM pitch_examples_corpus
ORDER BY collection;
```

### Step 7: Update Environment Variable

```powershell
# For local development (with Cloud SQL Proxy)
$env:DATABASE_URL="postgresql://postgres:YourPassword@localhost:5433/techscope"

# For production (Cloud Run)
# DATABASE_URL="postgresql://postgres:password@/techscope?host=/cloudsql/techscopeai:us-central1:techscope-db"
```

## Troubleshooting

### Issue: Cloud SQL Proxy connection failed
- Make sure Cloud SQL Proxy is running
- Check connection name is correct
- Verify firewall rules allow connection

### Issue: Import fails due to size
- Use `pg_dump` with compression: `pg_dump -Fc` (custom format)
- Use `pg_restore` instead of `psql` for large databases

### Issue: pgvector extension error
- Make sure you're using PostgreSQL 11+
- Cloud SQL supports pgvector natively

## Next Steps

After migration:
1. ✅ Test agents with Cloud SQL connection
2. ✅ Update agent code to use DATABASE_URL
3. ✅ Build FastAPI with Cloud SQL
4. ✅ Deploy to Cloud Run

