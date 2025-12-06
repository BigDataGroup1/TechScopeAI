"""Base processor class with common utilities for all data processors."""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """Base class for all data processors."""
    
    def __init__(self, agent_name: str, output_dir: Path):
        """
        Initialize base processor.
        
        Args:
            agent_name: Name of the agent (e.g., 'competitive', 'marketing')
            output_dir: Output directory for processed data
        """
        self.agent_name = agent_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove null bytes and control characters
        text = text.replace('\x00', '').replace('\r', ' ')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        preserve_sentences: bool = True
    ) -> List[str]:
        """
        Chunk text into smaller pieces.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk (characters)
            chunk_overlap: Overlap between chunks (characters)
            preserve_sentences: If True, try to break at sentence boundaries
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        text = self.clean_text(text)
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        
        if preserve_sentences:
            # Try to break at sentence boundaries
            sentences = re.split(r'[.!?]+\s+', text)
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 <= chunk_size:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
        else:
            # Simple character-based chunking
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end]
                
                # Try to break at word boundary
                if end < len(text):
                    last_space = chunk.rfind(' ')
                    if last_space > chunk_size * 0.5:  # Only if reasonable
                        chunk = chunk[:last_space]
                        start += last_space + 1
                    else:
                        start = end
                else:
                    start = len(text)
                
                chunks.append(chunk.strip())
        
        return chunks
    
    def extract_metadata(
        self, 
        source_path: Path, 
        chunk_id: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata for a chunk.
        
        Args:
            source_path: Path to source file
            chunk_id: Unique identifier for this chunk
            additional_metadata: Additional metadata to include
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "agent": self.agent_name,
            "source": str(source_path),
            "source_file": source_path.name,
            "chunk_id": chunk_id,
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return metadata
    
    def save_chunk(
        self, 
        text: str, 
        metadata: Dict[str, Any],
        output_file: Path
    ) -> None:
        """
        Save a chunk to JSONL file.
        
        Args:
            text: Chunk text
            metadata: Chunk metadata
            output_file: Output file path
        """
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        chunk_data = {
            "text": text,
            "metadata": metadata
        }
        
        # Convert Path to string for Windows compatibility
        output_path = str(output_file)
        
        try:
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(chunk_data, ensure_ascii=False) + '\n')
        except (OSError, IOError) as e:
            logger.error(f"Error writing to {output_path}: {e}")
            raise
    
    def process_file(
        self, 
        input_path: Path, 
        output_file: Path,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> int:
        """
        Process a single file and save chunks.
        
        Args:
            input_path: Path to input file
            output_file: Path to output JSONL file
            chunk_size: Maximum chunk size
            chunk_overlap: Chunk overlap size
            
        Returns:
            Number of chunks created
        """
        raise NotImplementedError("Subclasses must implement process_file")
    
    @abstractmethod
    def process_dataset(
        self, 
        input_dir: Path,
        output_file: Optional[Path] = None
    ) -> int:
        """
        Process all files in a dataset directory.
        
        Args:
            input_dir: Directory containing raw data
            output_file: Optional output file path (defaults to agent_name.jsonl)
            
        Returns:
            Total number of chunks created
        """
        pass

