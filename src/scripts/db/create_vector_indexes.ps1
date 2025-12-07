# Create vector indexes directly via SQL
# This is faster than using pg_restore for indexes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Create Vector Indexes in Cloud SQL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Cloud SQL Proxy is running
Write-Host "[1/3] Checking Cloud SQL Proxy..." -ForegroundColor Yellow
$proxyTest = Test-NetConnection -ComputerName localhost -Port 5433 -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $proxyTest) {
    Write-Host "  ERROR: Cloud SQL Proxy is not running on port 5433" -ForegroundColor Red
    Write-Host "  Start it with:" -ForegroundColor Yellow
    Write-Host "    .\cloud_sql_proxy.exe -instances=techscopeai:us-central1:techscope-db=tcp:5433" -ForegroundColor White
    exit 1
}
Write-Host "  Cloud SQL Proxy is running" -ForegroundColor Green

# Get password
$PASSWORD = $env:CLOUD_SQL_PASSWORD
if (-not $PASSWORD) {
    $PASSWORD = Read-Host "Enter Cloud SQL password"
    if (-not $PASSWORD) {
        Write-Host "Password required!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[2/3] Creating vector indexes..." -ForegroundColor Yellow
Write-Host "  WARNING: This will take 1-4 hours for ~2M documents!" -ForegroundColor Red
Write-Host "  The competitors_corpus index alone may take 2-3 hours." -ForegroundColor Yellow
Write-Host "  You can monitor progress in Cloud SQL Console or run check script." -ForegroundColor Cyan
Write-Host ""

$confirm = Read-Host "Continue? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[3/3] Creating indexes via Python..." -ForegroundColor Yellow

# Get project root (3 levels up from script location)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $scriptDir))

$pythonScript = @'
import sys
import os
from urllib.parse import quote_plus

# Get project root from environment variable set by PowerShell
project_root = os.environ.get('PROJECT_ROOT', os.getcwd())
sys.path.insert(0, project_root)

from src.rag.vector_store import VectorStore

# Set database URL with URL-encoded password
password = os.environ.get('CLOUD_SQL_PASSWORD', 'Huskies@123')
password_encoded = quote_plus(password)
os.environ['DATABASE_URL'] = f'postgresql://postgres:{password_encoded}@localhost:5433/techscope'

vs = VectorStore()

# Collections that need vector indexes
collections = [
    'competitors_corpus',
    'marketing_corpus',
    'ip_policy_corpus',
    'policy_corpus',
    'job_roles_corpus',
    'pitch_examples_corpus'
]

print('Creating vector indexes...')
print('This will take a long time - be patient!')
print('')

conn = vs._get_connection()
try:
    cur = conn.cursor()
    
    for collection in collections:
        print(f'Creating index for {collection}...')
        try:
            # Check if index already exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND indexname = %s
                );
            """, (f'{collection}_embedding_idx',))
            
            exists = cur.fetchone()[0]
            
            if exists:
                print(f'  Index already exists, skipping {collection}')
                continue
            
            # Get row count for progress estimate
            cur.execute(f'SELECT COUNT(*) FROM {collection}')
            count = cur.fetchone()[0]
            print(f'  {collection}: {count:,} rows - this will take a while...')
            
            # Create HNSW vector index
            cur.execute(f"""
                CREATE INDEX {collection}_embedding_idx 
                ON {collection} 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            
            conn.commit()
            print(f'  ✓ Index created for {collection}')
            print('')
            
        except Exception as e:
            print(f'  ✗ Error creating index for {collection}: {e}')
            conn.rollback()
            print('')
    
    cur.close()
    print('========================================')
    print('All indexes created!')
    print('========================================')
    
finally:
    vs._put_connection(conn)
'@

$tempScript = [System.IO.Path]::GetTempFileName() + ".py"
$pythonScript | Out-File -FilePath $tempScript -Encoding utf8

try {
    $env:CLOUD_SQL_PASSWORD = $PASSWORD
    $env:PROJECT_ROOT = $projectRoot
    python $tempScript
} finally {
    Remove-Item $tempScript -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Note: Index creation runs on Cloud SQL server." -ForegroundColor Cyan
Write-Host "Even if this script finishes, indexes may still be building." -ForegroundColor Cyan
Write-Host "Check status with: .\src\scripts\db\check_what_exists.ps1" -ForegroundColor White



