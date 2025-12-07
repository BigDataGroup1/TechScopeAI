# Real-time monitoring of index creation progress
# Shows live progress bars and percentage complete

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Real-Time Index Creation Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

# Check if Cloud SQL Proxy is running
$proxyTest = Test-NetConnection -ComputerName localhost -Port 5433 -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $proxyTest) {
    Write-Host "ERROR: Cloud SQL Proxy is not running" -ForegroundColor Red
    Write-Host "Start it with:" -ForegroundColor Yellow
    Write-Host "  .\cloud_sql_proxy.exe -instances=techscopeai:us-central1:techscope-db=tcp:5433" -ForegroundColor White
    exit 1
}

$PASSWORD = $env:CLOUD_SQL_PASSWORD
if (-not $PASSWORD) {
    $PASSWORD = "Huskies@123"
}

# Get project root (3 levels up from script location)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $scriptDir))

$pythonScript = @'
import sys
import os
import time
from urllib.parse import quote_plus
from datetime import datetime

# Get project root from environment variable set by PowerShell
project_root = os.environ.get('PROJECT_ROOT', os.getcwd())
sys.path.insert(0, project_root)

from src.rag.vector_store import VectorStore

password = os.environ.get('CLOUD_SQL_PASSWORD', 'Huskies@123')
password_encoded = quote_plus(password)
os.environ['DATABASE_URL'] = f'postgresql://postgres:{password_encoded}@localhost:5433/techscope'

vs = VectorStore()
conn = vs._get_connection()

collections = [
    'competitors_corpus',
    'marketing_corpus',
    'ip_policy_corpus',
    'policy_corpus',
    'job_roles_corpus',
    'pitch_examples_corpus'
]

try:
    while True:
        cur = conn.cursor()
        
        # Check for active index creation
        cur.execute("""
            SELECT 
                pid,
                datname,
                relid::regclass as index_name,
                phase,
                COALESCE(blocks_total, 0) as blocks_total,
                COALESCE(blocks_done, 0) as blocks_done,
                COALESCE(tuples_total, 0) as tuples_total,
                COALESCE(tuples_done, 0) as tuples_done,
                COALESCE(partitions_total, 0) as partitions_total,
                COALESCE(partitions_done, 0) as partitions_done
            FROM pg_stat_progress_create_index
            ORDER BY index_name;
        """)
        
        active_indexes = cur.fetchall()
        
        # Clear screen (ANSI escape codes)
        print('\033[2J\033[H', end='')
        print('=' * 70)
        print(f'Index Creation Progress - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('=' * 70)
        print()
        
        if active_indexes:
            for row in active_indexes:
                pid, db, index_name, phase, blocks_total, blocks_done, tuples_total, tuples_done, partitions_total, partitions_done = row
                
                print(f'Index: {index_name}')
                print(f'  Phase: {phase}')
                
                if tuples_total > 0:
                    pct = (tuples_done / tuples_total) * 100
                    print(f'  Progress: {tuples_done:,} / {tuples_total:,} tuples ({pct:.2f}%)')
                    # Create a simple progress bar
                    bar_length = 50
                    filled = int(bar_length * pct / 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f'  [{bar}]')
                elif blocks_total > 0:
                    pct = (blocks_done / blocks_total) * 100 if blocks_total > 0 else 0
                    print(f'  Progress: {blocks_done:,} / {blocks_total:,} blocks ({pct:.2f}%)')
                    bar_length = 50
                    filled = int(bar_length * pct / 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f'  [{bar}]')
                else:
                    print(f'  Status: {phase} (no progress info available)')
                
                print()
        else:
            # Check which indexes exist
            cur.execute("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexname LIKE '%_embedding_idx'
                ORDER BY indexname;
            """)
            existing = [row[0] for row in cur.fetchall()]
            
            print('Current Status:')
            print()
            completed = 0
            pending = 0
            
            for collection in collections:
                index_name = f'{collection}_embedding_idx'
                if index_name in existing:
                    print(f'  [OK] {index_name}')
                    completed += 1
                else:
                    print(f'  [PENDING] {index_name}')
                    pending += 1
            
            print()
            print('=' * 70)
            print(f'Summary: {completed}/{len(collections)} indexes completed, {pending} pending')
            
            if pending == 0:
                print('All indexes are complete!')
            else:
                print('No active index creation detected.')
                print('Index creation may be between phases or not started yet.')
                print('Check back in a few minutes or verify the create script is running.')
        
        cur.close()
        
        print()
        print('=' * 70)
        print('Refreshing in 5 seconds... (Ctrl+C to stop)')
        time.sleep(5)
        
except KeyboardInterrupt:
    print('\n\nMonitoring stopped.')
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



