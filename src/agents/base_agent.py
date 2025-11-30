"""Base agent class for all TechScopeAI agents."""

import logging
import os
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..rag.retriever import Retriever

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all TechScopeAI agents."""
    
    def __init__(self, category: str, retriever: Retriever, 
                 model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        """
        Initialize base agent.
        
        Args:
            category: Agent category (e.g., "pitch", "competitive")
            retriever: Retriever instance for RAG
            model: LLM model name
            temperature: LLM temperature
        """
        self.category = category
        self.retriever = retriever
        self.model = model
        self.temperature = temperature
        
        # Initialize LLM client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment. Add it to .env file")
        
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package required. Install with: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized {category} agent with model {model}")
    
    def retrieve_context(self, query: str, top_k: int = 5, 
                        category_filter: Optional[str] = None) -> Dict:
        """
        Retrieve relevant context using RAG.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            category_filter: Optional category filter
            
        Returns:
            Dictionary with context and sources
        """
        return self.retriever.retrieve_with_context(query, top_k=top_k)
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate response using LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLM response text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def format_response(self, response: str, sources: List[Dict]) -> Dict:
        """
        Format agent response with sources.
        
        Args:
            response: LLM response text
            sources: List of source documents
            
        Returns:
            Formatted response dictionary
        """
        return {
            "response": response,
            "sources": sources,
            "agent": self.category
        }
    
    @abstractmethod
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a user query (to be implemented by subclasses).
        
        Args:
            query: User query
            context: Optional additional context
            
        Returns:
            Agent response
        """
        pass

