"""Processor for policy datasets (privacy policies, terms of service)."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class PolicyProcessor(BaseProcessor):
    """Process policy datasets (privacy policies, terms of service)."""
    
    def __init__(self, output_dir: Path = Path("data/processed/policy")):
        super().__init__("policy", output_dir)
    
    def process_markdown_policies(self, md_dir: Path, output_file: Path) -> int:
        """Process markdown policy files."""
        chunk_count = 0
        
        for md_file in md_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = self.clean_text(content)
                if not content or len(content) < 100:
                    continue
                
                # Split by markdown headers (sections)
                sections = re.split(r'\n#{1,3}\s+', content)
                
                for section_idx, section in enumerate(sections):
                    section = self.clean_text(section)
                    if not section or len(section) < 50:
                        continue
                    
                    # Chunk if section is too long
                    chunks = self.chunk_text(section, chunk_size=1000, chunk_overlap=200)
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        metadata = self.extract_metadata(
                            md_file,
                            f"{md_file.stem}_{section_idx}_{chunk_idx}",
                            additional_metadata={
                                "source_type": "privacy_policy",
                                "content_type": "policy_document",
                                "file_type": "markdown",
                                "section_index": section_idx,
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks)
                            }
                        )
                        
                        self.save_chunk(chunk, metadata, output_file)
                        chunk_count += 1
            
            except Exception as e:
                logger.error(f"Error processing markdown policy {md_file}: {e}")
        
        return chunk_count
    
    def process_json_policies(self, json_dir: Path, output_file: Path) -> int:
        """Process JSON policy files (annotated policies)."""
        chunk_count = 0
        
        for json_file in json_dir.rglob("*.json"):
            if json_file.name == 'package.json':
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = [data]
                else:
                    continue
                
                for idx, item in enumerate(items):
                    text = ""
                    
                    if isinstance(item, dict):
                        # Look for text/content fields
                        text_fields = ['text', 'content', 'policy_text', 'paragraph', 'section']
                        for field in text_fields:
                            if field in item:
                                text = str(item[field])
                                break
                        
                        # If no text field, try to extract from structure
                        if not text:
                            text = json.dumps(item, ensure_ascii=False)
                    
                    text = self.clean_text(text)
                    if not text or len(text) < 50:
                        continue
                    
                    chunks = self.chunk_text(text, chunk_size=1000, chunk_overlap=200)
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        metadata = self.extract_metadata(
                            json_file,
                            f"{json_file.stem}_{idx}_{chunk_idx}",
                            additional_metadata={
                                "source_type": "privacy_policy",
                                "content_type": "annotated_policy",
                                "file_type": "json",
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks)
                            }
                        )
                        
                        # Preserve annotations/metadata
                        if isinstance(item, dict):
                            for key, value in item.items():
                                if key not in ['text', 'content', 'policy_text', 'paragraph', 'section']:
                                    if isinstance(value, (str, int, float, bool)):
                                        metadata[key] = value
                        
                        self.save_chunk(chunk, metadata, output_file)
                        chunk_count += 1
            
            except Exception as e:
                logger.error(f"Error processing JSON policy {json_file}: {e}")
        
        return chunk_count
    
    def process_dataset(
        self, 
        input_dir: Path,
        output_file: Optional[Path] = None
    ) -> int:
        """
        Process all policy datasets.
        
        Args:
            input_dir: Directory containing raw policy data
            output_file: Optional output file path
            
        Returns:
            Total number of chunks created
        """
        if output_file is None:
            output_file = self.output_dir / "policy_data.jsonl"
        
        if output_file.exists():
            output_file.unlink()
        
        total_chunks = 0
        
        # Process historical privacy policies (markdown)
        historical_dir = input_dir / "privacy_historical"
        if historical_dir.exists():
            logger.info("Processing historical privacy policies...")
            chunks = self.process_markdown_policies(historical_dir, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process compliance/annotated policies (JSON)
        compliance_dirs = ['privacy_compliance', 'Privacy-Policies-Compliance-main']
        for subdir in compliance_dirs:
            compliance_dir = input_dir / subdir
            if compliance_dir.exists():
                logger.info(f"Processing compliance policies: {subdir}")
                chunks = self.process_json_policies(compliance_dir, output_file)
                total_chunks += chunks
                logger.info(f"  Created {chunks} chunks")
        
        # Process example policies
        examples_dir = input_dir / "examples"
        if examples_dir.exists():
            logger.info("Processing example policies...")
            chunks = self.process_markdown_policies(examples_dir, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        logger.info(f"Total chunks created: {total_chunks}")
        return total_chunks

