"""
Agent Service - Singleton pattern for loading and caching agents
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

# Global agent instances (lazy loaded)
_agents: Dict[str, Any] = {}
_retriever = None
_initialized = False


def _initialize_retriever():
    """Initialize the RAG retriever (shared across agents)"""
    global _retriever
    
    if _retriever is not None:
        return _retriever
    
    try:
        from src.rag.embedder import Embedder
        from src.rag.vector_store import VectorStore
        from src.rag.retriever import Retriever
        import os
        
        # Check if using Weaviate QueryAgent - if so, skip embedding model loading
        use_weaviate = os.getenv("USE_WEAVIATE_QUERY_AGENT", "true").lower() in ("true", "1", "yes")
        
        if use_weaviate:
            # For Weaviate QueryAgent, we don't need the embedding model
            # Weaviate handles embeddings internally
            logger.info("Using Weaviate QueryAgent - skipping embedding model and PostgreSQL")
            embedder = None
            embedding_model = None
            vector_store = VectorStore(embedding_model=None, skip_connection=True)
        else:
            # For PostgreSQL RAG, need embedding model
            embedder = Embedder(use_openai=False)
            embedding_model = embedder.get_embedding_model()
            vector_store = VectorStore(embedding_model=embedding_model)
        
        _retriever = Retriever(vector_store=vector_store, embedder=embedder)
        
        logger.info("✅ Retriever initialized")
        return _retriever
    except Exception as e:
        logger.error(f"❌ Failed to initialize retriever: {e}", exc_info=True)
        # Fallback: force Weaviate path to avoid HF downloads
        try:
            logger.warning("Attempting fallback retriever initialization (skip HF embeddings)...")
            from src.rag.vector_store import VectorStore
            from src.rag.retriever import Retriever
            
            vector_store = VectorStore(embedding_model=None, skip_connection=True)
            _retriever = Retriever(vector_store=vector_store, embedder=None)
            logger.info("✅ Fallback retriever initialized without embeddings (Weaviate only)")
            return _retriever
        except Exception as fallback_error:
            logger.error(f"❌ Fallback retriever also failed: {fallback_error}")
            return None


def get_pitch_agent():
    """Get or create PitchAgent instance"""
    if "pitch" not in _agents:
        try:
            from src.agents.pitch_agent import PitchAgent
            retriever = _initialize_retriever()
            if retriever:
                _agents["pitch"] = PitchAgent(retriever, ai_provider="auto")
                logger.info("✅ PitchAgent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load PitchAgent: {e}")
            return None
    return _agents.get("pitch")


def get_marketing_agent():
    """Get or create MarketingAgent instance"""
    if "marketing" not in _agents:
        try:
            from src.agents.marketing_agent import MarketingAgent
            retriever = _initialize_retriever()
            if retriever:
                _agents["marketing"] = MarketingAgent(retriever, ai_provider="auto")
                logger.info("✅ MarketingAgent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load MarketingAgent: {e}")
            return None
    return _agents.get("marketing")


def get_patent_agent():
    """Get or create PatentAgent instance"""
    if "patent" not in _agents:
        try:
            from src.agents.patent_agent import PatentAgent
            retriever = _initialize_retriever()
            if retriever:
                _agents["patent"] = PatentAgent(retriever, ai_provider="auto")
                logger.info("✅ PatentAgent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load PatentAgent: {e}")
            return None
    return _agents.get("patent")


def get_policy_agent():
    """Get or create PolicyAgent instance"""
    if "policy" not in _agents:
        try:
            from src.agents.policy_agent import PolicyAgent
            retriever = _initialize_retriever()
            if retriever:
                _agents["policy"] = PolicyAgent(retriever, ai_provider="auto")
                logger.info("✅ PolicyAgent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load PolicyAgent: {e}")
            return None
    return _agents.get("policy")


def get_team_agent():
    """Get or create TeamAgent instance"""
    if "team" not in _agents:
        try:
            from src.agents.team_agent import TeamAgent
            retriever = _initialize_retriever()
            if retriever:
                _agents["team"] = TeamAgent(retriever, ai_provider="auto")
                logger.info("✅ TeamAgent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load TeamAgent: {e}")
            return None
    return _agents.get("team")


def get_competitive_agent():
    """Get or create CompetitiveAgent instance"""
    if "competitive" not in _agents:
        try:
            from src.agents.competitive_agent import CompetitiveAgent
            retriever = _initialize_retriever()
            if retriever:
                _agents["competitive"] = CompetitiveAgent(retriever, ai_provider="auto")
                logger.info("✅ CompetitiveAgent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load CompetitiveAgent: {e}")
            return None
    return _agents.get("competitive")


def get_supervisor_agent():
    """Get or create SupervisorAgent instance (for chat routing)"""
    if "supervisor" not in _agents:
        try:
            from src.agents.supervisor_agent import SupervisorAgent
            retriever = _initialize_retriever()
            if retriever:
                supervisor = SupervisorAgent(retriever)
                
                # Register all agents
                pitch = get_pitch_agent()
                if pitch:
                    supervisor.register_agent("pitch", pitch)
                
                marketing = get_marketing_agent()
                if marketing:
                    supervisor.register_agent("marketing", marketing)
                
                patent = get_patent_agent()
                if patent:
                    supervisor.register_agent("patent", patent)
                
                policy = get_policy_agent()
                if policy:
                    supervisor.register_agent("policy", policy)
                
                team = get_team_agent()
                if team:
                    supervisor.register_agent("team", team)
                
                competitive = get_competitive_agent()
                if competitive:
                    supervisor.register_agent("competitive", competitive)
                
                _agents["supervisor"] = supervisor
                logger.info("✅ SupervisorAgent initialized with all agents")
        except Exception as e:
            logger.error(f"❌ Failed to load SupervisorAgent: {e}")
            return None
    return _agents.get("supervisor")




