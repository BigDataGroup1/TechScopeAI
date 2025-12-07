"""
RAG retrieval logic.

Provides high-level interface for retrieving relevant context from vector store.
"""

import logging
from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
from .collections import AgentType, get_collection_name

logger = logging.getLogger(__name__)


class RAGRetriever:
    """High-level RAG retriever."""
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize the RAG retriever.
        
        Args:
            vector_store: VectorStore instance
        """
        self.vector_store = vector_store
    
    def retrieve(
        self,
        agent_type: AgentType,
        query: str,
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for an agent.
        
        Args:
            agent_type: Type of agent (determines which collection to query)
            query: Query text
            top_k: Number of results to return
            metadata_filter: Optional metadata filter (e.g., {"source": "yc"})
        
        Returns:
            List of retrieved documents with metadata, each as:
            {
                "text": str,
                "metadata": Dict[str, Any],
                "distance": float,
                "id": str
            }
        """
        # Get collection name for agent
        collection_name = get_collection_name(agent_type)
        if collection_name is None:
            logger.warning(f"No collection found for agent type: {agent_type}")
            return []
        
        try:
            # Query the collection
            results = self.vector_store.query(
                collection_name=collection_name,
                query_texts=[query],
                n_results=top_k,
                where=metadata_filter
            )
            
            # Format results
            retrieved_docs = []
            if results and "documents" in results and len(results["documents"]) > 0:
                documents = results["documents"][0]  # First query
                metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else [{}] * len(documents)
                distances = results.get("distances", [[]])[0] if results.get("distances") else [0.0] * len(documents)
                ids = results.get("ids", [[]])[0] if results.get("ids") else [""] * len(documents)
                
                for i, doc_text in enumerate(documents):
                    retrieved_docs.append({
                        "text": doc_text,
                        "metadata": metadatas[i] if i < len(metadatas) else {},
                        "distance": distances[i] if i < len(distances) else 0.0,
                        "id": ids[i] if i < len(ids) else f"doc_{i}"
                    })
            
            logger.debug(f"Retrieved {len(retrieved_docs)} documents for {agent_type} agent")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Error retrieving documents for {agent_type}: {e}")
            return []
    
    def retrieve_for_competitive(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Convenience method for competitive agent."""
        return self.retrieve(AgentType.COMPETITIVE, query, top_k)
    
    def retrieve_for_marketing(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Convenience method for marketing agent."""
        return self.retrieve(AgentType.MARKETING, query, top_k)
    
    def retrieve_for_ip_legal(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Convenience method for IP/legal agent."""
        return self.retrieve(AgentType.IP_LEGAL, query, top_k)
    
    def retrieve_for_policy(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Convenience method for policy agent."""
        return self.retrieve(AgentType.POLICY, query, top_k)
    
    def retrieve_for_team(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Convenience method for team agent."""
        return self.retrieve(AgentType.TEAM, query, top_k)
    
    def retrieve_for_pitch(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Convenience method for pitch agent."""
        return self.retrieve(AgentType.PITCH, query, top_k)





