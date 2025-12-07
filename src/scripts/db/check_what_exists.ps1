# Check what data/indexes already exist in Cloud SQL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Checking Cloud SQL Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Cloud SQL Proxy is running
$proxyTest = Test-NetConnection -ComputerName localhost -Port 5433 -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $proxyTest) {
    Write-Host "ERROR: Cloud SQL Proxy is not running" -ForegroundColor Red
    exit 1
}

$PASSWORD = $env:CLOUD_SQL_PASSWORD
if (-not $PASSWORD) {
    $PASSWORD = "Huskies@123"
}

$env:DATABASE_URL = "postgresql://postgres:$PASSWORD@localhost:5433/techscope"

Write-Host "Checking tables and row counts..." -ForegroundColor Yellow

# Get project root (3 levels up from script location)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $scriptDir))

# Create a temporary Python script file to avoid quote escaping issues
$pythonScript = @'
import sys
import os

# Get project root from environment variable set by PowerShell
project_root = os.environ.get('PROJECT_ROOT', os.getcwd())
sys.path.insert(0, project_root)

try:
    from src.rag.vector_store import VectorStore
    from urllib.parse import quote_plus
    
    # Set database URL with password from environment (URL-encode password)
    password = os.environ.get('CLOUD_SQL_PASSWORD', 'Huskies@123')
    password_encoded = quote_plus(password)
    os.environ['DATABASE_URL'] = f'postgresql://postgres:{password_encoded}@localhost:5433/techscope'
    
    vs = VectorStore()
    
    # Collections to check
    collections = [
        'competitors_corpus',
        'marketing_corpus',
        'ip_policy_corpus',
        'policy_corpus',
        'job_roles_corpus',
        'pitch_examples_corpus'
    ]
    
    print('Tables and Row Counts:')
    total = 0
    for c in collections:
        try:
            count = vs.get_collection_count(c)
            print(f'  {c}: {count:,} rows')
            total += count
        except Exception as e:
            print(f'  {c}: ERROR - {e}')
    
    print(f'\nTotal documents: {total:,}')
    
    # Check indexes using direct connection
    try:
        conn = vs._get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT indexname, tablename 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        indexes = cur.fetchall()
        
        print('\nIndexes:')
        if indexes:
            for idx_name, tbl_name in indexes:
                print(f'  {tbl_name}.{idx_name}')
        else:
            print('  No indexes found')
        
        cur.close()
        vs._put_connection(conn)
    except Exception as e:
        print(f'\nCould not check indexes: {e}')
    
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
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



