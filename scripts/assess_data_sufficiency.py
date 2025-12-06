"""Assess if we have sufficient data for all agents."""

import os
from pathlib import Path
import pandas as pd

def get_file_info(filepath):
    """Get file size and row count if CSV."""
    path = Path(filepath)
    if not path.exists():
        return None
    
    size_mb = path.stat().st_size / (1024 * 1024)
    
    row_count = None
    if path.suffix == '.csv':
        try:
            # Quick row count (read first 1000 to estimate)
            df = pd.read_csv(path, nrows=1000)
            row_count = len(df)
            # Try to get total if file is small
            if size_mb < 10:
                df_full = pd.read_csv(path)
                row_count = len(df_full)
        except:
            pass
    
    return {'size_mb': size_mb, 'rows': row_count}

def assess_agent_data(agent_name, dir_path):
    """Assess data for a specific agent."""
    agent_dir = Path(dir_path)
    if not agent_dir.exists():
        return {'status': 'MISSING', 'files': [], 'total_size_mb': 0, 'total_rows': 0}
    
    files = []
    total_size = 0
    total_rows = 0
    
    for item in agent_dir.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            info = get_file_info(item)
            if info:
                files.append({
                    'name': item.name,
                    'size_mb': info['size_mb'],
                    'rows': info['rows']
                })
                total_size += info['size_mb']
                if info['rows']:
                    total_rows += info['rows']
        elif item.is_dir():
            # Count files in subdirectories
            subfiles = list(item.rglob('*'))
            file_count = len([f for f in subfiles if f.is_file() and not f.name.startswith('.')])
            if file_count > 0:
                files.append({
                    'name': f"{item.name}/ ({file_count} files)",
                    'size_mb': sum(f.stat().st_size for f in subfiles if f.is_file()) / (1024 * 1024),
                    'rows': None
                })
                total_size += files[-1]['size_mb']
    
    # Determine status
    if total_size == 0:
        status = 'MISSING'
    elif total_size < 1:
        status = 'MINIMAL'
    elif total_size < 10:
        status = 'ADEQUATE'
    else:
        status = 'GOOD'
    
    return {
        'status': status,
        'files': files,
        'total_size_mb': total_size,
        'total_rows': total_rows
    }

# Agent requirements (minimum expectations)
AGENT_REQUIREMENTS = {
    'competitive': {
        'min_size_mb': 50,
        'min_rows': 10000,
        'description': 'Need: Startup/competitor data, funding info, market analysis'
    },
    'marketing': {
        'min_size_mb': 10,
        'min_rows': 1000,
        'description': 'Need: Ad copy examples, marketing content, positioning statements'
    },
    'ip_legal': {
        'min_size_mb': 5,
        'min_rows': 500,
        'description': 'Need: Patent info, IP guidance, OSS license examples'
    },
    'policy': {
        'min_size_mb': 10,
        'min_rows': 100,
        'description': 'Need: Privacy policies, ToS examples, compliance docs'
    },
    'team': {
        'min_size_mb': 5,
        'min_rows': 1000,
        'description': 'Need: Job descriptions, role requirements, hiring patterns'
    },
    'pitch': {
        'min_size_mb': 5,
        'min_rows': 500,
        'description': 'Need: Pitch examples, deck templates, founder stories'
    }
}

def main():
    print("=" * 70)
    print("DATA SUFFICIENCY ASSESSMENT FOR TECH SCOPE AI")
    print("=" * 70)
    
    base_dir = Path("data/raw")
    results = {}
    
    for agent_name, requirements in AGENT_REQUIREMENTS.items():
        agent_dir = base_dir / agent_name
        assessment = assess_agent_data(agent_name, agent_dir)
        results[agent_name] = assessment
        
        print(f"\n{'='*70}")
        print(f"AGENT: {agent_name.upper()}")
        print(f"{'='*70}")
        print(f"Status: {assessment['status']}")
        print(f"Total Size: {assessment['total_size_mb']:.2f} MB")
        if assessment['total_rows']:
            print(f"Total Rows: {assessment['total_rows']:,}")
        print(f"\nRequirement: {requirements['description']}")
        print(f"Minimum Expected: {requirements['min_size_mb']} MB, {requirements['min_rows']:,} rows")
        
        if assessment['files']:
            print(f"\nFiles ({len(assessment['files'])}):")
            for f in assessment['files'][:10]:  # Show first 10
                size_str = f"{f['size_mb']:.2f} MB"
                rows_str = f", {f['rows']:,} rows" if f['rows'] else ""
                print(f"  - {f['name']}: {size_str}{rows_str}")
            if len(assessment['files']) > 10:
                print(f"  ... and {len(assessment['files']) - 10} more files")
        else:
            print("\nNo files found!")
        
        # Sufficiency check
        is_sufficient = (
            assessment['total_size_mb'] >= requirements['min_size_mb'] and
            (not assessment['total_rows'] or assessment['total_rows'] >= requirements['min_rows'])
        )
        
        if is_sufficient:
            print(f"\n[OK] SUFFICIENT - Meets minimum requirements")
        else:
            print(f"\n[!] INSUFFICIENT - Below minimum requirements")
            if assessment['total_size_mb'] < requirements['min_size_mb']:
                print(f"   Need {requirements['min_size_mb'] - assessment['total_size_mb']:.2f} MB more")
            if assessment['total_rows'] and assessment['total_rows'] < requirements['min_rows']:
                print(f"   Need {requirements['min_rows'] - assessment['total_rows']:,} more rows")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    sufficient = sum(1 for r in results.values() if r['status'] in ['ADEQUATE', 'GOOD'])
    total = len(results)
    
    print(f"\nAgents with sufficient data: {sufficient}/{total}")
    
    print("\nAgents needing more data:")
    for agent_name, assessment in results.items():
        req = AGENT_REQUIREMENTS[agent_name]
        is_sufficient = (
            assessment['total_size_mb'] >= req['min_size_mb'] and
            (not assessment['total_rows'] or assessment['total_rows'] >= req['min_rows'])
        )
        if not is_sufficient:
            print(f"  - {agent_name}: {assessment['status']} ({assessment['total_size_mb']:.2f} MB)")

if __name__ == "__main__":
    main()

