"""Processor for pitch datasets (pitch examples, investor blogs, templates)."""

import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class PitchProcessor(BaseProcessor):
    """Process pitch datasets (pitch examples, investor blogs, templates)."""
    
    def __init__(self, output_dir: Path = Path("data/processed/pitch")):
        super().__init__("pitch", output_dir)
    
    def process_pitch_csv(self, csv_path: Path, output_file: Path) -> int:
        """Process pitch CSV files (one-line pitches, pitch examples)."""
        chunk_count = 0
        
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            logger.info(f"Processing {csv_path.name}: {len(df)} rows")
        except Exception as e:
            logger.error(f"Error reading {csv_path}: {e}")
            return 0
        
        # Look for pitch text columns
        pitch_cols = ['pitch', 'one_liner', 'description', 'tagline', 'summary', 'text']
        pitch_col = None
        for col in pitch_cols:
            if col in df.columns:
                pitch_col = col
                break
        
        # Look for company name
        name_cols = ['name', 'company_name', 'company', 'startup_name']
        name_col = None
        for col in name_cols:
            if col in df.columns:
                name_col = col
                break
        
        for idx, row in df.iterrows():
            # Extract pitch text
            pitch_text = ""
            if pitch_col:
                pitch_text = str(row[pitch_col]) if pd.notna(row[pitch_col]) else ""
            else:
                # Combine all text columns
                text_parts = []
                for col in df.columns:
                    if pd.notna(row[col]) and isinstance(row[col], str):
                        text_parts.append(f"{col}: {row[col]}")
                pitch_text = " | ".join(text_parts)
            
            pitch_text = self.clean_text(pitch_text)
            if not pitch_text or len(pitch_text) < 20:
                continue
            
            # Extract company name
            company_name = ""
            if name_col:
                company_name = str(row[name_col]) if pd.notna(row[name_col]) else ""
            
            metadata = self.extract_metadata(
                csv_path,
                f"{csv_path.stem}_{idx}",
                additional_metadata={
                    "source_type": "pitch_example",
                    "content_type": "startup_pitch",
                    "company_name": company_name
                }
            )
            
            # Add other columns as metadata
            for col in df.columns:
                if col != pitch_col and col != name_col:
                    if pd.notna(row[col]):
                        if isinstance(row[col], (str, int, float, bool)):
                            metadata[col] = str(row[col])
            
            # Save as single chunk (preserve full pitch context)
            self.save_chunk(pitch_text, metadata, output_file)
            chunk_count += 1
        
        return chunk_count
    
    def process_blog_articles(self, blog_dir: Path, output_file: Path) -> int:
        """Process blog articles (investor blogs, startup blogs, templates)."""
        chunk_count = 0
        
        for file_path in blog_dir.rglob("*"):
            if not file_path.is_file():
                continue
            
            if file_path.suffix in ['.txt', '.md', '.html']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic HTML cleaning if needed
                    if file_path.suffix == '.html':
                        import re
                        content = re.sub(r'<[^>]+>', ' ', content)
                    
                    content = self.clean_text(content)
                    if not content or len(content) < 100:
                        continue
                    
                    # Chunk by paragraphs or sections
                    chunks = self.chunk_text(content, chunk_size=1000, chunk_overlap=200)
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        metadata = self.extract_metadata(
                            file_path,
                            f"{file_path.stem}_{chunk_idx}",
                            additional_metadata={
                                "source_type": "blog_article",
                                "content_type": "pitch_advice",
                                "file_type": file_path.suffix[1:],
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks)
                            }
                        )
                        
                        self.save_chunk(chunk, metadata, output_file)
                        chunk_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing blog file {file_path}: {e}")
        
        return chunk_count
    
    def process_json_pitches(self, json_path: Path, output_file: Path) -> int:
        """Process JSON pitch files."""
        chunk_count = 0
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = [data]
            else:
                return 0
            
            for idx, item in enumerate(items):
                pitch_text = ""
                
                if isinstance(item, dict):
                    pitch_fields = ['pitch', 'one_liner', 'description', 'text', 'content']
                    for field in pitch_fields:
                        if field in item:
                            pitch_text = str(item[field])
                            break
                    
                    if not pitch_text:
                        pitch_text = json.dumps(item, ensure_ascii=False)
                else:
                    pitch_text = str(item)
                
                pitch_text = self.clean_text(pitch_text)
                if not pitch_text or len(pitch_text) < 20:
                    continue
                
                metadata = self.extract_metadata(
                    json_path,
                    f"{json_path.stem}_{idx}",
                    additional_metadata={
                        "source_type": "pitch_example",
                        "content_type": "startup_pitch"
                    }
                )
                
                if isinstance(item, dict):
                    for key, value in item.items():
                        if key not in ['pitch', 'one_liner', 'description', 'text', 'content']:
                            if isinstance(value, (str, int, float, bool)):
                                metadata[key] = value
                
                self.save_chunk(pitch_text, metadata, output_file)
                chunk_count += 1
        
        except Exception as e:
            logger.error(f"Error processing JSON pitches {json_path}: {e}")
        
        return chunk_count
    
    def process_excel_file(self, excel_path: Path, output_file: Path) -> int:
        """Process Excel files (XLSX, XLS) with pitch data."""
        import pandas as pd
        
        chunk_count = 0
        
        try:
            # Read first sheet
            df = pd.read_excel(excel_path, sheet_name=0, engine='openpyxl')
            logger.info(f"Processing Excel: {excel_path.name}: {len(df)} rows")
        except Exception as e:
            logger.error(f"Error reading Excel {excel_path}: {e}")
            return 0
        
        # Look for pitch text columns
        pitch_cols = ['pitch', 'one_liner', 'description', 'tagline', 'summary', 'text', 'One_Liner']
        pitch_col = None
        for col in pitch_cols:
            if col in df.columns:
                pitch_col = col
                break
        
        # Look for company name
        name_cols = ['name', 'company_name', 'company', 'startup_name', 'Company_Name']
        name_col = None
        for col in name_cols:
            if col in df.columns:
                name_col = col
                break
        
        for idx, row in df.iterrows():
            # Extract pitch text
            pitch_text = ""
            if pitch_col:
                pitch_text = str(row[pitch_col]) if pd.notna(row[pitch_col]) else ""
            else:
                # Combine all text columns
                text_parts = []
                for col in df.columns:
                    if pd.notna(row[col]) and isinstance(row[col], str):
                        text_parts.append(f"{col}: {row[col]}")
                pitch_text = " | ".join(text_parts)
            
            pitch_text = self.clean_text(pitch_text)
            if not pitch_text or len(pitch_text) < 20:
                continue
            
            # Extract company name
            company_name = ""
            if name_col:
                company_name = str(row[name_col]) if pd.notna(row[name_col]) else ""
            
            metadata = self.extract_metadata(
                excel_path,
                f"{excel_path.stem}_{idx}",
                additional_metadata={
                    "source_type": "pitch_example",
                    "content_type": "startup_pitch",
                    "company_name": company_name
                }
            )
            
            # Add other columns as metadata
            for col in df.columns:
                if col != pitch_col and col != name_col:
                    if pd.notna(row[col]):
                        if isinstance(row[col], (str, int, float, bool)):
                            metadata[col] = str(row[col])
            
            # Save as single chunk (preserve full pitch context)
            self.save_chunk(pitch_text, metadata, output_file)
            chunk_count += 1
        
        return chunk_count
    
    def process_dataset(
        self, 
        input_dir: Path,
        output_file: Optional[Path] = None
    ) -> int:
        """
        Process all pitch datasets.
        
        Args:
            input_dir: Directory containing raw pitch data
            output_file: Optional output file path
            
        Returns:
            Total number of chunks created
        """
        if output_file is None:
            output_file = self.output_dir / "pitch_data.jsonl"
        
        if output_file.exists():
            output_file.unlink()
        
        total_chunks = 0
        
        # Process pitch CSV files
        pitch_csv = input_dir / "pitch_examples.csv"
        if pitch_csv.exists():
            logger.info("Processing pitch CSV...")
            chunks = self.process_pitch_csv(pitch_csv, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process Excel files (XLSX, XLS)
        for excel_file in input_dir.rglob("*.xlsx"):
            if excel_file.name.startswith('.'):
                continue
            logger.info(f"Processing Excel: {excel_file}")
            chunks = self.process_excel_file(excel_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        for excel_file in input_dir.rglob("*.xls"):
            if excel_file.name.startswith('.'):
                continue
            logger.info(f"Processing Excel: {excel_file}")
            chunks = self.process_excel_file(excel_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process JSON pitch files
        for json_file in input_dir.rglob("*.json"):
            if json_file.name.startswith('.') or json_file.name == 'package.json':
                continue
            logger.info(f"Processing JSON pitches: {json_file}")
            chunks = self.process_json_pitches(json_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process blog articles
        blog_dirs = ['startup_blogs', 'investor_blogs', 'entrepreneur_articles', 
                     'templates', 'failures', 'podcasts']
        for subdir in blog_dirs:
            blog_dir = input_dir / subdir
            if blog_dir.exists():
                logger.info(f"Processing blog articles: {subdir}")
                chunks = self.process_blog_articles(blog_dir, output_file)
                total_chunks += chunks
                logger.info(f"  Created {chunks} chunks")
        
        logger.info(f"Total chunks created: {total_chunks}")
        return total_chunks

