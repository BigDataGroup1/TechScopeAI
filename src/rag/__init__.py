"""
RAG (Retrieval-Augmented Generation) infrastructure for TechScope AI.

This module provides:
- Vector store (PostgreSQL + pgvector) management
- Embedding generation
- Collection definitions
- Retrieval logic for RAG queries
"""

from .vector_store import VectorStore
from .embeddings import EmbeddingModel
from .collections import CollectionConfig, get_collection_name
from .retrieval import RAGRetriever

__all__ = [
    "VectorStore",
    "EmbeddingModel",
    "CollectionConfig",
    "get_collection_name",
    "RAGRetriever",
]




