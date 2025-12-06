"""Processor for IP/Legal datasets (privacy Q&A, OSS policies, patent guides)."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class IPLegalProcessor(BaseProcessor):
    """Process IP/Legal datasets (privacy Q&A, OSS policies, patent guides)."""
    
    def __init__(self, output_dir: Path = Path("data/processed/ip_legal")):
        super().__init__("ip_legal", output_dir)
    
    def process_qa_dataset(self, qa_dir: Path, output_file: Path) -> int:
        """Process PrivacyQA dataset (Q&A pairs)."""
        chunk_count = 0
        
        # Look for common Q&A file patterns
        qa_files = list(qa_dir.rglob("*.json")) + list(qa_dir.rglob("*.jsonl"))
        
        for qa_file in qa_files:
            try:
                if qa_file.suffix == '.jsonl':
                    with open(qa_file, 'r', encoding='utf-8') as f:
                        for idx, line in enumerate(f):
                            try:
                                data = json.loads(line)
                                
                                question = ""
                                answer = ""
                                
                                if isinstance(data, dict):
                                    question = data.get('question', data.get('query', ''))
                                    answer = data.get('answer', data.get('response', data.get('text', '')))
                                
                                if question and answer:
                                    # Combine Q&A as one chunk
                                    text = f"Question: {question}\n\nAnswer: {answer}"
                                    text = self.clean_text(text)
                                    
                                    if text and len(text) > 50:
                                        metadata = self.extract_metadata(
                                            qa_file,
                                            f"{qa_file.stem}_{idx}",
                                            additional_metadata={
                                                "source_type": "qa_pair",
                                                "content_type": "privacy_qa"
                                            }
                                        )
                                        
                                        self.save_chunk(text, metadata, output_file)
                                        chunk_count += 1
                            
                            except json.JSONDecodeError:
                                continue
                
                elif qa_file.suffix == '.json':
                    with open(qa_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Handle different JSON structures
                        if isinstance(data, list):
                            items = data
                        elif isinstance(data, dict):
                            items = [data]
                        else:
                            continue
                        
                        for idx, item in enumerate(items):
                            if isinstance(item, dict):
                                question = item.get('question', item.get('query', ''))
                                answer = item.get('answer', item.get('response', item.get('text', '')))
                                
                                if question and answer:
                                    text = f"Question: {question}\n\nAnswer: {answer}"
                                    text = self.clean_text(text)
                                    
                                    if text and len(text) > 50:
                                        metadata = self.extract_metadata(
                                            qa_file,
                                            f"{qa_file.stem}_{idx}",
                                            additional_metadata={
                                                "source_type": "qa_pair",
                                                "content_type": "privacy_qa"
                                            }
                                        )
                                        
                                        self.save_chunk(text, metadata, output_file)
                                        chunk_count += 1
            
            except Exception as e:
                logger.error(f"Error processing Q&A file {qa_file}: {e}")
        
        return chunk_count
    
    def process_policy_files(self, policy_dir: Path, output_file: Path) -> int:
        """Process OSS policy files (markdown, text, etc.)."""
        chunk_count = 0
        
        # Process markdown files
        for md_file in policy_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = self.clean_text(content)
                if not content or len(content) < 100:
                    continue
                
                # Chunk by sections (markdown headers)
                sections = re.split(r'\n#{1,3}\s+', content)
                
                for section_idx, section in enumerate(sections):
                    section = self.clean_text(section)
                    if not section or len(section) < 50:
                        continue
                    
                    # Further chunk if too long
                    chunks = self.chunk_text(section, chunk_size=1000, chunk_overlap=200)
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        metadata = self.extract_metadata(
                            md_file,
                            f"{md_file.stem}_{section_idx}_{chunk_idx}",
                            additional_metadata={
                                "source_type": "policy_document",
                                "content_type": "oss_policy",
                                "file_type": "markdown",
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks)
                            }
                        )
                        
                        self.save_chunk(chunk, metadata, output_file)
                        chunk_count += 1
            
            except Exception as e:
                logger.error(f"Error processing markdown file {md_file}: {e}")
        
        # Process text files
        for txt_file in policy_dir.rglob("*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = self.clean_text(content)
                if not content or len(content) < 100:
                    continue
                
                chunks = self.chunk_text(content, chunk_size=1000, chunk_overlap=200)
                
                for chunk_idx, chunk in enumerate(chunks):
                    metadata = self.extract_metadata(
                        txt_file,
                        f"{txt_file.stem}_{chunk_idx}",
                        additional_metadata={
                            "source_type": "policy_document",
                            "content_type": "oss_policy",
                            "file_type": "text",
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks)
                        }
                    )
                    
                    self.save_chunk(chunk, metadata, output_file)
                    chunk_count += 1
            
            except Exception as e:
                logger.error(f"Error processing text file {txt_file}: {e}")
        
        return chunk_count
    
    def process_patent_guides(self, guides_dir: Path, output_file: Path) -> int:
        """Process patent guide documents."""
        chunk_count = 0
        
        for file_path in guides_dir.rglob("*"):
            if not file_path.is_file():
                continue
            
            if file_path.suffix in ['.html', '.htm']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic HTML cleaning (remove tags)
                    content = re.sub(r'<[^>]+>', ' ', content)
                    content = self.clean_text(content)
                    
                    if not content or len(content) < 100:
                        continue
                    
                    chunks = self.chunk_text(content, chunk_size=1000, chunk_overlap=200)
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        metadata = self.extract_metadata(
                            file_path,
                            f"{file_path.stem}_{chunk_idx}",
                            additional_metadata={
                                "source_type": "patent_guide",
                                "content_type": "patent_information",
                                "file_type": "html",
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks)
                            }
                        )
                        
                        self.save_chunk(chunk, metadata, output_file)
                        chunk_count += 1
                
                except Exception as e:
                    logger.error(f"Error processing HTML file {file_path}: {e}")
        
        return chunk_count
    
    def process_dataset(
        self, 
        input_dir: Path,
        output_file: Optional[Path] = None
    ) -> int:
        """
        Process all IP/Legal datasets.
        
        Args:
            input_dir: Directory containing raw IP/Legal data
            output_file: Optional output file path
            
        Returns:
            Total number of chunks created
        """
        if output_file is None:
            output_file = self.output_dir / "ip_legal_data.jsonl"
        
        if output_file.exists():
            output_file.unlink()
        
        total_chunks = 0
        
        # Process PrivacyQA dataset
        privacy_qa_dir = input_dir / "privacy_qa"
        if privacy_qa_dir.exists():
            logger.info("Processing PrivacyQA dataset...")
            chunks = self.process_qa_dataset(privacy_qa_dir, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        # Process OSS policies
        oss_policy_dirs = ['oss_policies', 'government-open-source-policies-main']
        for subdir in oss_policy_dirs:
            policy_dir = input_dir / subdir
            if policy_dir.exists():
                logger.info(f"Processing OSS policies: {subdir}")
                chunks = self.process_policy_files(policy_dir, output_file)
                total_chunks += chunks
                logger.info(f"  Created {chunks} chunks")
        
        # Process patent guides
        patent_guides_dir = input_dir / "patent_guides"
        if patent_guides_dir.exists():
            logger.info("Processing patent guides...")
            chunks = self.process_patent_guides(patent_guides_dir, output_file)
            total_chunks += chunks
            logger.info(f"  Created {chunks} chunks")
        
        logger.info(f"Total chunks created: {total_chunks}")
        return total_chunks

