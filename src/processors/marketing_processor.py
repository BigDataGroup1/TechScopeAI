"""Processor for marketing datasets (ad copy, taglines, creative content)."""

import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class MarketingProcessor(BaseProcessor):
    """Process marketing datasets (ad copy, taglines, creative examples)."""
    
    def __init__(self, output_dir: Path = Path("data/processed/marketing")):
        super().__init__("marketing", output_dir)
    
    def process_taglines_file(self, file_path: Path, output_file: Path) -> int:
        """Process taglines/creative copy files."""
        chunk_count = 0
        
        # Try CSV first
        if file_path.suffix == '.csv':
            try:
                df = pd.read_csv(file_path, low_memory=False)
                
                # Look for tagline/creative columns
                tagline_cols = ['tagline', 'copy', 'creative', 'ad_copy', 'text', 'description']
                tagline_col = None
                for col in tagline_cols:
                    if col in df.columns:
                        tagline_col = col
                        break
                
                if tagline_col:
                    for idx, row in df.iterrows():
                        tagline = str(row[tagline_col]) if pd.notna(row[tagline_col]) else ""
                        tagline = self.clean_text(tagline)
                        
                        if not tagline or len(tagline) < 10:
                            continue
                        
                        metadata = self.extract_metadata(
                            file_path,
                            f"{file_path.stem}_{idx}",
                            additional_metadata={
                                "source_type": "tagline",
                                "content_type": "marketing_copy"
                            }
                        )
                        
                        # Add other columns as metadata
                        for col in df.columns:
                            if col != tagline_col and pd.notna(row[col]):
                                if isinstance(row[col], (str, int, float, bool)):
                                    metadata[col] = str(row[col])
                        
                        self.save_chunk(tagline, metadata, output_file)
                        chunk_count += 1
                
            except Exception as e:
                logger.error(f"Error processing CSV taglines {file_path}: {e}")
        
        # Try JSONL
        elif file_path.suffix == '.jsonl':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for idx, line in enumerate(f):
                        try:
                            data = json.loads(line)
                            tagline = ""
                            
                            if isinstance(data, dict):
                                tagline_fields = ['tagline', 'copy', 'creative', 'ad_copy', 'text']
                                for field in tagline_fields:
                                    if field in data:
                                        tagline = str(data[field])
                                        break
                            
                            tagline = self.clean_text(tagline)
                            if not tagline or len(tagline) < 10:
                                continue
                            
                            metadata = self.extract_metadata(
                                file_path,
                                f"{file_path.stem}_{idx}",
                                additional_metadata={
                                    "source_type": "tagline",
                                    "content_type": "marketing_copy"
                                }
                            )
                            
                            if isinstance(data, dict):
                                for key, value in data.items():
                                    if key not in ['tagline', 'copy', 'creative', 'ad_copy', 'text']:
                                        if isinstance(value, (str, int, float, bool)):
                                            metadata[key] = value
                            
                            self.save_chunk(tagline, metadata, output_file)
                            chunk_count += 1
                        
                        except json.JSONDecodeError:
                            continue
            
            except Exception as e:
                logger.error(f"Error processing JSONL taglines {file_path}: {e}")
        
        return chunk_count
    
    def process_reviews_file(self, file_path: Path, output_file: Path) -> int:
        """Process review datasets (IMDB, Yelp, Amazon) for marketing insights."""
        chunk_count = 0
        
        if file_path.suffix == '.jsonl':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for idx, line in enumerate(f):
                        try:
                            data = json.loads(line)
                            text = ""
                            
                            if isinstance(data, dict):
                                text_fields = ['text', 'review', 'content', 'comment']
                                for field in text_fields:
                                    if field in data:
                                        text = str(data[field])
                                        break
                            
                            text = self.clean_text(text)
                            if not text or len(text) < 50:
                                continue
                            
                            # Chunk longer reviews
                            chunks = self.chunk_text(text, chunk_size=500, chunk_overlap=100)
                            
                            for chunk_idx, chunk in enumerate(chunks):
                                metadata = self.extract_metadata(
                                    file_path,
                                    f"{file_path.stem}_{idx}_{chunk_idx}",
                                    additional_metadata={
                                        "source_type": "review",
                                        "content_type": "user_feedback",
                                        "chunk_index": chunk_idx,
                                        "total_chunks": len(chunks)
                                    }
                                )
                                
                                if isinstance(data, dict):
                                    for key, value in data.items():
                                        if key not in ['text', 'review', 'content', 'comment']:
                                            if isinstance(value, (str, int, float, bool)):
                                                metadata[key] = value
                                
                                self.save_chunk(chunk, metadata, output_file)
                                chunk_count += 1
                        
                        except json.JSONDecodeError:
                            continue
            
            except Exception as e:
                logger.error(f"Error processing reviews {file_path}: {e}")
        
        return chunk_count
    
    def process_dataset(
        self, 
        input_dir: Path,
        output_file: Optional[Path] = None
    ) -> int:
        """Process all marketing datasets (only relevant startup-focused sources)."""
        if output_file is None:
            output_file = self.output_dir / "marketing_data.jsonl"
        
        if output_file.exists():
            output_file.unlink()
        
        total_chunks = 0
        
        # Process taglines / ad copy (Product Hunt tech startups, ad creatives)
        tagline_dirs = ['producthunt_taglines', 'ads_creative', 'ad_image_net']
        for subdir in tagline_dirs:
            tagline_dir = input_dir / subdir
            if tagline_dir.exists():
                for file_path in tagline_dir.rglob("*"):
                    if file_path.is_file() and file_path.suffix in ['.csv', '.jsonl', '.json']:
                        logger.info(f"Processing tagline file: {file_path}")
                        chunks = self.process_taglines_file(file_path, output_file)
                        total_chunks += chunks
                        logger.info(f"  Created {chunks} chunks")

        logger.info(f"Total chunks created: {total_chunks}")
        return total_chunks

