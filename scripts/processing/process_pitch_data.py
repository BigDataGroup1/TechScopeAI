"""Process pitch data for RAG indexing."""

import logging
import json
import csv
from pathlib import Path
from typing import List, Dict
import re

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\-()]', '', text)
    return text.strip()


def process_csv_file(file_path: Path) -> List[Dict]:
    """Process CSV file and extract text chunks."""
    chunks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract relevant fields
                content_parts = []
                
                # One-line pitch
                if 'One_Line_Pitch' in row and row['One_Line_Pitch']:
                    content_parts.append(f"One-line pitch: {row['One_Line_Pitch']}")
                
                # Company info
                company_info = []
                if row.get('Company_Name'):
                    company_info.append(f"Company: {row['Company_Name']}")
                if row.get('Industry'):
                    company_info.append(f"Industry: {row['Industry']}")
                if row.get('Funding_Stage'):
                    company_info.append(f"Stage: {row['Funding_Stage']}")
                
                if company_info:
                    content_parts.append(" | ".join(company_info))
                
                if content_parts:
                    content = " | ".join(content_parts)
                    chunks.append({
                        'content': clean_text(content),
                        'source': str(file_path.name),
                        'category': 'pitch_examples',
                        'metadata': {
                            'company_name': row.get('Company_Name', ''),
                            'industry': row.get('Industry', ''),
                            'stage': row.get('Funding_Stage', '')
                        }
                    })
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
    
    return chunks


def process_text_file(file_path: Path, category: str = "pitch") -> List[Dict]:
    """Process text file and extract chunks."""
    chunks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Split into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            for para in paragraphs:
                if len(para) > 100:  # Only include substantial paragraphs
                    chunks.append({
                        'content': clean_text(para),
                        'source': str(file_path.name),
                        'category': category,
                        'metadata': {}
                    })
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
    
    return chunks


def process_pitch_data(raw_data_path: Path, output_path: Path) -> List[Dict]:
    """
    Process all pitch data from raw directory.
    
    Args:
        raw_data_path: Path to raw pitch data
        output_path: Path to save processed data
        
    Returns:
        List of processed chunks
    """
    output_path.mkdir(parents=True, exist_ok=True)
    all_chunks = []
    
    logger.info(f"Processing pitch data from {raw_data_path}")
    
    # Process CSV files
    csv_files = [
        raw_data_path / "pitch_examples.csv",
        raw_data_path / "startup_company_one_line_pitches.csv"
    ]
    
    for csv_file in csv_files:
        if csv_file.exists():
            logger.info(f"Processing CSV: {csv_file.name}")
            chunks = process_csv_file(csv_file)
            all_chunks.extend(chunks)
            logger.info(f"  Extracted {len(chunks)} chunks")
    
    # Process text files
    text_dirs = {
        "pitch_examples": ["pitch_examples.csv"],
        "templates": ["templates"],
        "investor_blogs": ["investor_blogs"],
        "failures": ["failures"],
        "startup_blogs": ["startup_blogs"],
        "yc_library": ["yc_library"]
    }
    
    for category, dirs in text_dirs.items():
        for dir_name in dirs:
            dir_path = raw_data_path / dir_name
            if dir_path.exists():
                logger.info(f"Processing directory: {dir_name} (category: {category})")
                
                # Process all files in directory
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        if file_path.suffix in ['.txt', '.md', '.html']:
                            chunks = process_text_file(file_path, category=category)
                            all_chunks.extend(chunks)
                        elif file_path.suffix == '.csv':
                            chunks = process_csv_file(file_path)
                            all_chunks.extend(chunks)
    
    # Save processed data
    output_file = output_path / "processed_chunks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Processed {len(all_chunks)} chunks. Saved to {output_file}")
    
    return all_chunks


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    raw_path = Path("data/raw/pitch")
    output_path = Path("data/processed/pitch")
    
    if len(sys.argv) > 1:
        raw_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    
    chunks = process_pitch_data(raw_path, output_path)
    print(f"\n✅ Processed {len(chunks)} chunks from pitch data")

