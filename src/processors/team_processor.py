"""Processor for team datasets (job descriptions, skills, hiring guides)."""

import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class TeamProcessor(BaseProcessor):
    """Process team datasets (job descriptions, skills, hiring guides)."""
    
    def __init__(self, output_dir: Path = Path("data/processed/team")):
        super().__init__("team", output_dir)
    
    def process_job_skills_csv(self, csv_path: Path, output_file: Path) -> int:
        """Process job skills CSV file."""
        chunk_count = 0
        
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            logger.info(f"Processing {csv_path.name}: {len(df)} rows")
        except Exception as e:
            logger.error(f"Error reading {csv_path}: {e}")
            return 0
        
        # Look for job description columns
        desc_cols = ['description', 'job_description', 'responsibilities', 'requirements', 'skills']
        desc_col = None
        for col in desc_cols:
            if col in df.columns:
                desc_col = col
                break
        
        # Look for job title column
        title_cols = ['title', 'job_title', 'role', 'position']
        title_col = None
        for col in title_cols:
            if col in df.columns:
                title_col = col
                break
        
        for idx, row in df.iterrows():
            # Extract job description
            description = ""
            if desc_col:
                description = str(row[desc_col]) if pd.notna(row[desc_col]) else ""
            else:
                # Combine all text columns
                text_parts = []
                for col in df.columns:
                    if pd.notna(row[col]) and isinstance(row[col], str):
                        text_parts.append(f"{col}: {row[col]}")
                description = " | ".join(text_parts)
            
            description = self.clean_text(description)
            if not description or len(description) < 50:
                continue
            
            # Extract job title
            job_title = ""
            if title_col:
                job_title = str(row[title_col]) if pd.notna(row[title_col]) else ""
            
            metadata = self.extract_metadata(
                csv_path,
                f"{csv_path.stem}_{idx}",
                additional_metadata={
                    "source_type": "job_description",
                    "content_type": "job_posting",
                    "job_title": job_title
                }
            )
            
            # Add other columns as metadata
            for col in df.columns:
                if col != desc_col and col != title_col:
                    if pd.notna(row[col]):
                        if isinstance(row[col], (str, int, float, bool)):
                            metadata[col] = str(row[col])
            
            # Save as single chunk (preserve full job description context)
            self.save_chunk(description, metadata, output_file)
            chunk_count += 1
        
        return chunk_count
    
    def process_hiring_guides(self, guides_dir: Path, output_file: Path) -> int:
        """Process hiring guide articles (text, HTML, markdown)."""
        chunk_count = 0
        
        for file_path in guides_dir.rglob("*"):
            if not file_path.is_file():
                continue
            
            if file_path.suffix in ['.txt', '.md']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
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
                                "source_type": "hiring_guide",
                                "content_type": "hiring_advice",
                                "file_type": file_path.suffix[1:],
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks)
                            }
                        )
                        
                        self.save_chunk(chunk, metadata, output_file)
                        chunk_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing guide file {file_path}: {e}")
        
        return chunk_count
    
    def process_dataset(
        self, 
        input_dir: Path,
        output_file: Optional[Path] = None
    ) -> int:
        """
        Process all team datasets.
        
        Args:
            input_dir: Directory containing raw team data
            output_file: Optional output file path
            
        Returns:
            Total number of chunks created
        """
        if output_file is None:
            output_file = self.output_dir / "team_data.jsonl"
        
        if output_file.exists():
            output_file.unlink()
        
        total_chunks = 0
        
        # Process job skills CSV
        job_skills_file = input_dir / "job_skill_set.csv"
        if job_skills_file.exists():
            logger.info("Processing job skills CSV...")
            chunks = self.process_job_skills_csv(job_skills_file, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process hiring guides
        hiring_dir = input_dir / "hiring_articles"
        if hiring_dir.exists():
            logger.info("Processing hiring guides...")
            chunks = self.process_hiring_guides(hiring_dir, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        logger.info(f"Total chunks created: {total_chunks}")
        return total_chunks








