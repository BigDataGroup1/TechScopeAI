"""Text embedding generator for RAG system."""

import logging
import os

# Fix tokenizers parallelism warning - MUST be set before importing sentence_transformers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from typing import List, Optional
import numpy as np

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class Embedder:
    """Generate embeddings for text using sentence transformers or OpenAI."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", 
                 use_openai: bool = False, openai_api_key: Optional[str] = None):
        """
        Initialize embedder.
        
        Args:
            model_name: Model name for sentence transformers, or "text-embedding-3-small" for OpenAI
            use_openai: Whether to use OpenAI embeddings (requires API key)
            openai_api_key: OpenAI API key (if using OpenAI)
        """
        self.use_openai = use_openai
        self.model_name = model_name
        
        if use_openai:
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package required. Install with: pip install openai")
            if not openai_api_key:
                import os
                openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY in .env")
            
            self.client = OpenAI(api_key=openai_api_key)
            self.model_name = model_name or "text-embedding-3-small"
            logger.info(f"Using OpenAI embeddings: {self.model_name}")
        else:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError("sentence-transformers required. Install with: pip install sentence-transformers")
            
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded")
    
    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        if self.use_openai:
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name
            )
            return np.array(response.data[0].embedding)
        else:
            return self.model.encode(text, convert_to_numpy=True)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            Array of embedding vectors
        """
        if self.use_openai:
            # OpenAI handles batching internally
            response = self.client.embeddings.create(
                input=texts,
                model=self.model_name
            )
            return np.array([item.embedding for item in response.data])
        else:
            return self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=True)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        if self.use_openai:
            # OpenAI text-embedding-3-small: 1536, ada-002: 1536
            return 1536
        else:
            # Test with dummy text to get dimension
            test_embedding = self.embed("test")
            return len(test_embedding)

