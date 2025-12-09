"""
Compatibility wrapper for Embedder (legacy interface).

Wraps EmbeddingModel to provide the old Embedder interface for backward compatibility.
"""

from .embeddings import EmbeddingModel

class Embedder:
    """
    Compatibility wrapper for EmbeddingModel.
    
    Provides the old Embedder interface while using EmbeddingModel internally.
    """
    
    def __init__(self, use_openai: bool = False, **kwargs):
        """
        Initialize Embedder (compatibility wrapper).
        
        Args:
            use_openai: If True, use OpenAI embeddings (not implemented, uses sentence-transformers)
            **kwargs: Additional arguments passed to EmbeddingModel
        """
        # Always use sentence-transformers (free embeddings)
        # OpenAI embeddings not implemented in this wrapper
        self.embedding_model = EmbeddingModel(**kwargs)
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_model.get_dimension()
    
    def encode(self, texts, **kwargs):
        """Encode texts to embeddings."""
        return self.embedding_model.encode(texts, **kwargs)
    
    def get_embedding_model(self):
        """Get the underlying EmbeddingModel instance."""
        return self.embedding_model


