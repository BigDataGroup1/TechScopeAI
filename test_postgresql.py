"""Test PostgreSQL connection."""
import psycopg2
import os

try:
    conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/techscope')
    print('[OK] PostgreSQL connection successful!')
    
    # Test pgvector extension
    cur = conn.cursor()
    cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
    result = cur.fetchone()
    if result:
        print(f'[OK] pgvector extension enabled (version {result[5]})')
    else:
        print('[ERROR] pgvector extension not found')
    
    cur.close()
    conn.close()
except Exception as e:
    print(f'[ERROR] Connection failed: {e}')

