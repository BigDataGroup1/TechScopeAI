"""Supervisor Agent - Orchestrates all agents and routes queries."""

import logging
from typing import Dict, List, Optional, Tuple

from .base_agent import BaseAgent
from ..rag.retriever import Retriever

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Agent that supervises and coordinates all other agents."""
    
    # Agent registry with keywords for routing
    AGENT_REGISTRY = {
        "pitch": {
            "keywords": ["pitch", "deck", "presentation", "elevator", "pitch deck", "pitch presentation", "raise capital", "funding deck", "investor pitch"],
            "description": "Generates pitch decks and elevator pitches for your startup"
        },
        "competitive": {
            "keywords": ["competitor", "competitive", "market analysis", "competition", "rival", "startup news", "funding rounds", "acquisitions", "market trends"],
            "description": "Analyzes competitors, market positioning, and startup industry news"
        },
        "marketing": {
            "keywords": ["marketing", "instagram", "linkedin", "social media", "content", "campaign", "post", "hashtag"],
            "description": "Creates marketing content for social media"
        },
        "patent": {
            "keywords": ["patent", "patentability", "ip", "intellectual property", "prior art", "filing", "uspto"],
            "description": "Helps with patent research and filing"
        },
        "policy": {
            "keywords": ["policy", "privacy", "terms", "tos", "compliance", "gdpr", "legal", "regulations"],
            "description": "Generates legal policies and compliance documents"
        },
        "team": {
            "keywords": ["team", "hiring", "job", "recruit", "role", "position", "employee", "jd", "job description"],
            "description": "Helps with team building and job descriptions"
        },
        "coordinator": {
            "keywords": ["what have we", "what did we", "summary", "overview", "what was generated"],
            "description": "Provides summaries and context"
        }
    }
    
    def __init__(self, retriever: Retriever, model: str = "gpt-4-turbo-preview", ai_provider: str = "openai"):
        """
        Initialize Supervisor Agent.
        
        Args:
            retriever: Retriever instance for RAG
            model: LLM model name
        """
        super().__init__("supervisor", retriever, model=model, ai_provider=ai_provider)
        self.agents = {}  # Will be populated with agent instances
        logger.info("SupervisorAgent initialized")
    
    def register_agent(self, agent_name: str, agent_instance: BaseAgent) -> None:
        """
        Register an agent instance.
        
        Args:
            agent_name: Name of the agent
            agent_instance: Agent instance
        """
        self.agents[agent_name] = agent_instance
        logger.info(f"Registered agent: {agent_name}")
    
    def route_query(self, query: str, context: Optional[Dict] = None) -> Tuple[str, float]:
        """
        Route a query to the appropriate agent(s).
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Tuple of (agent_name, confidence_score)
        """
        logger.info(f"Routing query: {query[:50]}...")
        
        query_lower = query.lower()
        
        # Check for news/research queries that should go to competitive agent
        news_indicators = ["news", "recent", "latest", "happened", "this week", "this month", "today", "current", "what are", "find me", "search for"]
        is_news_query = any(indicator in query_lower for indicator in news_indicators)
        
        # Check for pitch-specific queries
        pitch_indicators = ["generate", "create", "make", "build", "my pitch", "my deck", "for my", "help me"]
        is_pitch_query = any(indicator in query_lower for indicator in pitch_indicators)
        
        # Calculate scores for each agent
        agent_scores = {}
        for agent_name, agent_info in self.AGENT_REGISTRY.items():
            score = 0.0
            keywords = agent_info["keywords"]
            
            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            score = matches / len(keywords) if keywords else 0.0
            
            # Boost score for exact matches
            for keyword in keywords:
                if keyword in query_lower:
                    score += 0.1
            
            # Special handling for news queries
            if is_news_query and agent_name == "competitive":
                score += 0.5  # Boost competitive agent for news queries
            elif is_news_query and agent_name == "pitch":
                score -= 0.3  # Reduce pitch agent score for news queries
            
            # Special handling for pitch generation queries
            if is_pitch_query and agent_name == "pitch":
                score += 0.4  # Boost pitch agent for generation queries
            
            agent_scores[agent_name] = score
        
        # Use LLM for better routing if scores are close or ambiguous
        if max(agent_scores.values()) < 0.3 or (is_news_query and agent_scores.get("pitch", 0) > agent_scores.get("competitive", 0)):
            # Fallback to LLM routing for ambiguous cases
            return self._llm_route_query(query, context)
        
        # Get best match
        best_agent = max(agent_scores.items(), key=lambda x: x[1])
        
        if best_agent[1] > 0:
            logger.info(f"Routed to {best_agent[0]} with confidence {best_agent[1]:.2f}")
            return best_agent
        else:
            # Default to pitch agent
            logger.info("No clear match, defaulting to pitch agent")
            return ("pitch", 0.5)
    
    def _llm_route_query(self, query: str, context: Optional[Dict] = None) -> Tuple[str, float]:
        """Use LLM to route query when keyword matching is unclear."""
        agent_descriptions = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.AGENT_REGISTRY.items()
        ])
        
        prompt = f"""Route this query to the most appropriate agent:

Query: {query}

Available Agents:
{agent_descriptions}

Routing Guidelines:
- "pitch" agent: For generating, creating, or improving YOUR OWN pitch deck
- "competitive" agent: For news, research, market analysis, or information about OTHER startups/companies
- "marketing" agent: For creating marketing content, social media posts
- "patent" agent: For patent research, IP questions
- "policy" agent: For legal policies, compliance
- "team" agent: For hiring, job descriptions, team building

Examples:
- "Generate a pitch deck" → pitch
- "What startup funding rounds happened?" → competitive (news/research)
- "Find recent acquisitions" → competitive (news/research)
- "Create Instagram content" → marketing
- "Search for patents" → patent

Return only the agent name (one word) that should handle this query."""
        
        system_prompt = "You are a query router. Select the most appropriate agent for the query. Distinguish between queries about the user's own startup (pitch agent) vs. news/research about other companies (competitive agent)."
        
        try:
            response = self.generate_response(prompt, system_prompt=system_prompt)
            agent_name = response.strip().lower().split()[0]  # Get first word
            
            if agent_name in self.AGENT_REGISTRY:
                return (agent_name, 0.7)
            else:
                return ("pitch", 0.5)  # Default
        except Exception as e:
            logger.error(f"Error in LLM routing: {e}")
            return ("pitch", 0.5)
    
    def execute_with_agent(self, query: str, agent_name: str, 
                          context: Optional[Dict] = None) -> Dict:
        """
        Execute a query with a specific agent.
        
        Args:
            query: User query
            agent_name: Name of agent to use
            context: Optional context
            
        Returns:
            Agent response
        """
        if agent_name not in self.agents:
            return {
                "response": f"Agent '{agent_name}' is not available.",
                "sources": [],
                "error": f"Agent not registered: {agent_name}"
            }
        
        agent = self.agents[agent_name]
        
        try:
            response = agent.process_query(query, context)
            return response
        except Exception as e:
            logger.error(f"Error executing with {agent_name}: {e}")
            return {
                "response": f"Error processing query with {agent_name}: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def coordinate_multi_agent_task(self, task_description: str, 
                                    context: Optional[Dict] = None) -> Dict:
        """
        Coordinate a task that requires multiple agents.
        
        Args:
            task_description: Description of the task
            context: Optional context
            
        Returns:
            Combined results from multiple agents
        """
        logger.info(f"Coordinating multi-agent task: {task_description}")
        
        # Use LLM to break down task
        prompt = f"""Break down this task into steps that can be handled by different agents:

Task: {task_description}

Available Agents:
{chr(10).join([f"- {name}: {info['description']}" for name, info in self.AGENT_REGISTRY.items()])}

Return a JSON list of steps, each with:
- "agent": agent name
- "action": what the agent should do
- "order": step order (1, 2, 3...)

Example:
[
  {{"agent": "pitch", "action": "Generate pitch deck", "order": 1}},
  {{"agent": "marketing", "action": "Create marketing content", "order": 2}}
]"""
        
        system_prompt = "You are a task coordinator. Break down complex tasks into agent-specific steps."
        
        try:
            response_text = self.generate_response(prompt, system_prompt=system_prompt)
            
            # Parse JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            import json
            steps = json.loads(response_text)
            
            # Execute steps in order
            results = []
            for step in sorted(steps, key=lambda x: x.get("order", 0)):
                agent_name = step.get("agent")
                action = step.get("action")
                
                if agent_name in self.agents:
                    logger.info(f"Executing step {step.get('order')}: {agent_name} - {action}")
                    result = self.execute_with_agent(action, agent_name, context)
                    results.append({
                        "step": step.get("order"),
                        "agent": agent_name,
                        "action": action,
                        "result": result
                    })
            
            return {
                "response": f"Completed multi-agent task with {len(results)} steps.",
                "steps": results,
                "sources": []
            }
        except Exception as e:
            logger.error(f"Error coordinating multi-agent task: {e}")
            return {
                "response": f"Error coordinating task: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def get_agent_status(self, agent_name: str) -> Dict:
        """
        Get status of an agent.
        
        Args:
            agent_name: Name of agent
            
        Returns:
            Agent status information
        """
        if agent_name in self.agents:
            return {
                "available": True,
                "registered": True,
                "description": self.AGENT_REGISTRY.get(agent_name, {}).get("description", "")
            }
        elif agent_name in self.AGENT_REGISTRY:
            return {
                "available": False,
                "registered": False,
                "description": self.AGENT_REGISTRY[agent_name]["description"]
            }
        else:
            return {
                "available": False,
                "registered": False,
                "description": "Unknown agent"
            }
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a query by routing to appropriate agent.
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Agent response
        """
        # Route query
        agent_name, confidence = self.route_query(query, context)
        
        # Execute with routed agent
        response = self.execute_with_agent(query, agent_name, context)
        
        # Add routing info
        response["routed_to"] = agent_name
        response["routing_confidence"] = confidence
        
        return response

