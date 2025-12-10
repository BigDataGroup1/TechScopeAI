"""General Assistant Agent - Handles general questions and conversations."""

import logging
import json
from typing import Dict, List, Optional

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class GeneralAssistantAgent(BaseAgent):
    """
    General-purpose assistant agent that can handle any question or conversation.
    This is like ChatGPT - can answer general questions, have conversations,
    and optionally route to specialized agents when appropriate.
    """
    
    def __init__(self, retriever, model: str = "gpt-4-turbo-preview", ai_provider: str = "openai"):
        """Initialize General Assistant Agent."""
        super().__init__("general_assistant", retriever, model=model, ai_provider=ai_provider)
        logger.info("GeneralAssistantAgent initialized")
    
    def process_query(self, query: str, context: Optional[Dict] = None, 
                     use_specialized_agents: bool = True,
                     supervisor_agent=None) -> Dict:
        """
        Process a general query - can handle anything!
        
        Args:
            query: User query
            context: Optional company context
            use_specialized_agents: Whether to route to specialized agents when appropriate
            supervisor_agent: Optional supervisor agent for routing to specialized agents
            
        Returns:
            Agent response
        """
        logger.info(f"Processing general query: {query[:50]}...")
        
        # Check if this should be routed to a specialized agent
        if use_specialized_agents and supervisor_agent:
            agent_name, confidence = supervisor_agent.route_query(query, context)
            
            # If confidence is high (>0.6), route to specialized agent
            # Otherwise, handle as general conversation
            if confidence > 0.6 and agent_name != "coordinator":
                logger.info(f"High confidence routing to {agent_name}, delegating...")
                try:
                    specialized_response = supervisor_agent.execute_with_agent(
                        query, agent_name, context
                    )
                    # Add note that it was routed
                    specialized_response["routed_to"] = agent_name
                    specialized_response["routing_confidence"] = confidence
                    return specialized_response
                except Exception as e:
                    logger.warning(f"Error routing to {agent_name}, falling back to general: {e}")
                    # Fall through to general handling
        
        # Handle as general conversation
        return self._handle_general_query(query, context)
    
    def _handle_general_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """Handle a general query with conversational AI."""
        
        # Try to get relevant context from RAG
        context_data = self.retrieve_context(query, top_k=5)
        
        # Use web search for current information if needed
        web_results = []
        if context_data.get('count', 0) < 3:
            logger.info("RAG results insufficient, using web search")
            search_result = self.mcp_client.web_search(
                query=query,
                topic_context=query
            )
            if search_result.get("success"):
                web_results = search_result.get("results", [])
        
        # Build prompt
        prompt = f"""User Question: {query}

Relevant Context from Knowledge Base:
{context_data.get('context', 'No specific context found in database')}

Web Search Results (if available):
{self._format_web_results(web_results) if web_results else 'No additional web results'}

Please provide a helpful, comprehensive answer to the user's question. Be conversational, friendly, and informative."""
        
        # Add company context if available
        if context:
            company_name = context.get('basic_info', {}).get('company_name', '')
            if company_name:
                prompt += f"\n\nNote: The user is working with a startup called {company_name}. You can reference this context when relevant, but don't force it if the question is general."
            prompt += f"\n\nCompany Context:\n{json.dumps(context, indent=2)}"
        
        system_prompt = """You are a helpful, friendly AI assistant for startup founders and entrepreneurs. You can help with:

- General questions and conversations
- Startup advice and guidance
- Business strategy and planning
- Technical questions
- Market research and trends
- Any other questions the user might have

Be conversational, friendly, and helpful. You can have natural conversations, answer questions, provide advice, and help users think through problems. 

When appropriate, you can suggest using specialized tools (like generating pitch decks, analyzing competitors, etc.), but you should primarily focus on having a helpful conversation.

If you don't know something, be honest about it. Use web search results when available to provide current information.

Keep responses clear, well-structured, and easy to understand. Use examples when helpful."""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(context)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        # Combine sources
        all_sources = context_data.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'snippet': web_result.get('snippet', ''),
                'similarity': web_result.get('relevance_score', 0),
                'is_web_search': True
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def _format_web_results(self, web_results: List[Dict]) -> str:
        """Format web search results for prompt."""
        if not web_results:
            return ""
        
        formatted = []
        for i, result in enumerate(web_results[:5], 1):  # Limit to top 5
            formatted.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', 'N/A')}\n"
                f"   Snippet: {result.get('snippet', 'No snippet')}"
            )
        
        return "\n\n".join(formatted)

