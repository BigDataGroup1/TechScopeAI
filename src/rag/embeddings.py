"""
Embedding generation using sentence-transformers.

Uses the all-MiniLM-L6-v2 model (384 dimensions) for fast, efficient embeddings.
Supports both GPU and CPU with automatic fallback.
"""

import logging
from typing import List, Union, Optional
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


def detect_device(device_preference: Optional[str] = None) -> str:
    """
    Detect available device (GPU/CPU) with fallback.
    
    Args:
        device_preference: Preferred device ('cuda', 'cpu', or None for auto-detect)
    
    Returns:
        Device string ('cuda' or 'cpu')
    """
    if device_preference == 'cpu':
        logger.info("Using CPU (forced by user)")
        return 'cpu'
    
    if device_preference == 'cuda':
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
                return 'cuda'
            else:
                logger.warning("CUDA requested but not available. Falling back to CPU.")
                return 'cpu'
        except ImportError:
            logger.warning("PyTorch not installed. Falling back to CPU.")
            return 'cpu'
    
    # Auto-detect
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            logger.info(f"GPU detected: {device_name}. Using GPU for faster processing.")
            return 'cuda'
        else:
            logger.info("No GPU detected. Using CPU.")
            return 'cpu'
    except ImportError:
        logger.info("PyTorch not installed. Using CPU.")
        return 'cpu'


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model with GPU/CPU support."""
    
    def __init__(
        self, 
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: Optional[str] = None
    ):
        """
        Initialize the embedding model.
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.model_name = model_name
        self.device = detect_device(device)
        self.model: SentenceTransformer = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence-transformers model on the specified device."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            logger.info(f"Device: {self.device}")
            
            # Load model and move to device
            self.model = SentenceTransformer(self.model_name, device=self.device)
            
            logger.info(f"Model loaded successfully on {self.device}")
            logger.info(f"Embedding dimension: {self.get_dimension()}")
            
            if self.device == 'cuda':
                import torch
                logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            # Fallback to CPU if GPU fails
            if self.device == 'cuda':
                logger.warning("GPU loading failed. Falling back to CPU...")
                self.device = 'cpu'
                self.model = SentenceTransformer(self.model_name, device='cpu')
                logger.info("Model loaded successfully on CPU (fallback)")
            else:
                raise
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        if self.model is None:
            return 384  # Default for all-MiniLM-L6-v2
        return self.model.get_sentence_embedding_dimension()
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False,
        normalize_embeddings: bool = True
    ) -> np.ndarray:
        """
        Encode text(s) into embeddings.
        
        Args:
            texts: Single text string or list of texts
            batch_size: Batch size for encoding (larger for GPU, smaller for CPU)
            show_progress_bar: Whether to show progress bar
            normalize_embeddings: Whether to normalize embeddings (L2 norm)
        
        Returns:
            numpy array of embeddings (shape: [n_texts, embedding_dim])
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        # Handle single string
        if isinstance(texts, str):
            texts = [texts]
        
        # Adjust batch size based on device
        if self.device == 'cuda' and batch_size < 64:
            # GPU can handle larger batches
            effective_batch_size = max(batch_size, 64)
        else:
            effective_batch_size = batch_size
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=effective_batch_size,
                show_progress_bar=show_progress_bar,
                normalize_embeddings=normalize_embeddings,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            # Fallback to CPU if GPU error occurs
            if self.device == 'cuda':
                logger.warning("GPU encoding failed. Falling back to CPU...")
                self.device = 'cpu'
                self.model = SentenceTransformer(self.model_name, device='cpu')
                return self.encode(texts, batch_size, show_progress_bar, normalize_embeddings)
            raise
    
    def get_device(self) -> str:
        """Get the current device being used."""
        return self.device
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a single query string (convenience method).
        
        Args:
            query: Query text
        
        Returns:
            numpy array of embedding (shape: [1, embedding_dim])
        """
        return self.encode(query)





