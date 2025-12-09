"""Base agent class for all TechScopeAI agents."""

import logging
import os
import json
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

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Try to import PersonalizationAgent (Weaviate Agents - separate from RAG)
# Note: RAG uses PostgreSQL, but agents use Weaviate for personalization
try:
    import weaviate
    try:
        # Correct import path for weaviate-agents v1.1.0+
        from weaviate_agents.personalization import PersonalizationAgent
        PERSONALIZATION_AGENT_AVAILABLE = True
    except (ImportError, AttributeError) as e:
        # Weaviate agents not installed or wrong version - agents will work without personalization
        PERSONALIZATION_AGENT_AVAILABLE = False
except ImportError:
    PERSONALIZATION_AGENT_AVAILABLE = False

from ..rag.retriever import Retriever
from ..mcp.client import MCPClient

logger = logging.getLogger(__name__)

# Log status after logger is defined
if PERSONALIZATION_AGENT_AVAILABLE:
    logger.debug("✅ PersonalizationAgent imported successfully")
else:
    logger.warning("Weaviate Agents PersonalizationAgent not available. Agents will work without personalization features.")


class BaseAgent(ABC):
    """Base class for all TechScopeAI agents."""
    
    def __init__(self, category: str, retriever: Retriever, 
                 model: str = "gpt-4-turbo-preview", temperature: float = 0.7,
                 ai_provider: str = "openai"):
        """
        Initialize base agent.
        
        Args:
            category: Agent category (e.g., "pitch", "competitive")
            retriever: Retriever instance for RAG
            model: LLM model name
            temperature: LLM temperature
            ai_provider: AI provider to use ("openai", "gemini", or "auto")
        """
        self.category = category
        self.retriever = retriever
        self.model = model
        self.temperature = temperature
        self.ai_provider = ai_provider.lower()
        self.original_ai_provider = ai_provider.lower()  # Store original provider for fallback logic
        
        # Initialize LLM client based on provider
        if self.ai_provider in ["gemini", "auto"]:
            # Try Gemini first - reload env vars to ensure latest values
            load_dotenv()  # Reload to ensure .env is loaded
            gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if gemini_key and GEMINI_AVAILABLE:
                try:
                    genai.configure(api_key=gemini_key)
                    # Use appropriate Gemini model
                    if "gemini" in model.lower():
                        self.gemini_model = genai.GenerativeModel(model)
                    else:
                        # Default Gemini model
                        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                    self.client = None  # Use Gemini instead of OpenAI
                    self.use_gemini = True
                    logger.info(f"✅ Using Gemini for {category} agent")
                except Exception as e:
                    logger.warning(f"Could not initialize Gemini: {e}, falling back to OpenAI")
                    self.use_gemini = False
                    self.ai_provider = "openai"
            else:
                if self.ai_provider == "gemini":
                    raise ValueError("GEMINI_API_KEY not found and Gemini was explicitly selected. Add it to .env file")
                logger.warning("GEMINI_API_KEY not found, falling back to OpenAI")
                self.use_gemini = False
                self.ai_provider = "openai"
        
        if not self.use_gemini:
            # Use OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment. Add it to .env file")
            
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package required. Install with: pip install openai")
            
            # If model name is a Gemini model, use OpenAI's default model instead
            if "gemini" in self.model.lower():
                logger.warning(f"Model '{self.model}' is a Gemini model, but Gemini is not available. Using OpenAI default model instead.")
                self.model = "gpt-4-turbo-preview"  # Default OpenAI model
            
            self.client = OpenAI(api_key=api_key)
            self.use_gemini = False
            logger.info(f"✅ Using OpenAI for {category} agent with model: {self.model}")
        
        # Initialize MCP client for tools (web search, image search, etc.)
        self.mcp_client = MCPClient()
        
        # Initialize PersonalizationAgent if available (for Weaviate Cloud)
        self.personalization_agent = None
        if PERSONALIZATION_AGENT_AVAILABLE:
            try:
                weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8081")
                is_local = "localhost" in weaviate_url or "127.0.0.1" in weaviate_url or not weaviate_url.startswith("https://")
                
                if not is_local:
                    # Only use PersonalizationAgent with Weaviate Cloud
                    try:
                        # Connect to Weaviate (reuse retriever's connection if available)
                        if hasattr(retriever, 'query_agent_retriever') and hasattr(retriever.query_agent_retriever, 'client'):
                            weaviate_client = retriever.query_agent_retriever.client
                        else:
                            # Create new connection
                            if weaviate_url.startswith("http://"):
                                url_parts = weaviate_url.replace("http://", "").split(":")
                                host = url_parts[0]
                                port = int(url_parts[1]) if len(url_parts) > 1 else 8081
                                weaviate_client = weaviate.connect_to_custom(
                                    http_host=host, http_port=port, http_secure=False,
                                    grpc_host=host, grpc_port=50051, grpc_secure=False
                                )
                            else:
                                url_parts = weaviate_url.replace("https://", "").split(":")
                                host = url_parts[0]
                                port = int(url_parts[1]) if len(url_parts) > 1 else 443
                                weaviate_client = weaviate.connect_to_custom(
                                    http_host=host, http_port=port, http_secure=True,
                                    grpc_host=host, grpc_port=50051, grpc_secure=True
                                )
                        
                        self.personalization_agent = PersonalizationAgent(client=weaviate_client)
                        logger.info(f"✅ PersonalizationAgent initialized for {category} agent")
                    except Exception as e:
                        logger.warning(f"Could not initialize PersonalizationAgent: {e}, will use company data for personalization")
                else:
                    logger.info(f"PersonalizationAgent requires Weaviate Cloud (local instance detected), will use company data for personalization")
            except Exception as e:
                logger.warning(f"PersonalizationAgent not available: {e}, will use company data for personalization")
        
        logger.info(f"Initialized {category} agent with model {model}")
    
    def retrieve_context(self, query: str, top_k: int = 3, 
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
    
    def _extract_company_data(self, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Extract company data from context dictionary.
        
        Args:
            context: Context dictionary that may contain company data
            
        Returns:
            Company data dictionary or None
        """
        if not context:
            return None
        
        # Check if context itself is company data (has company_name, etc.)
        if isinstance(context, dict) and 'company_name' in context:
            return context
        
        # Check for nested company_data
        if 'company_data' in context:
            return context['company_data']
        
        # Check for common company data keys
        company_keys = ['company_name', 'industry', 'problem', 'solution', 'target_market']
        if any(key in context for key in company_keys):
            return context
        
        return None
    
    def personalize_prompt(self, prompt: str, company_data: Optional[Dict] = None) -> str:
        """
        Personalize prompt with company data for startup-specific responses.
        
        Args:
            prompt: Original prompt
            company_data: Company/startup data dictionary
            
        Returns:
            Personalized prompt with company context
        """
        if not company_data:
            return prompt
        
        # Extract key company information
        company_name = company_data.get('company_name', '')
        industry = company_data.get('industry', '')
        problem = company_data.get('problem', '')
        solution = company_data.get('solution', '')
        target_market = company_data.get('target_market', '')
        current_stage = company_data.get('current_stage', '')
        funding_goal = company_data.get('funding_goal', '')
        traction = company_data.get('traction', '')
        
        # Build personalized context
        personalization_context = []
        
        if company_name:
            personalization_context.append(f"Company: {company_name}")
        if industry:
            personalization_context.append(f"Industry: {industry}")
        if problem:
            personalization_context.append(f"Problem: {problem}")
        if solution:
            personalization_context.append(f"Solution: {solution}")
        if target_market:
            personalization_context.append(f"Target Market: {target_market}")
        if current_stage:
            personalization_context.append(f"Current Stage: {current_stage}")
        if funding_goal:
            personalization_context.append(f"Funding Goal: {funding_goal}")
        if traction:
            personalization_context.append(f"Traction: {traction}")
        
        if personalization_context:
            personalized_header = "=== PERSONALIZED FOR THIS STARTUP ===\n" + "\n".join(personalization_context) + "\n=== END PERSONALIZATION ===\n\n"
            return personalized_header + prompt
        
        return prompt
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, 
                         company_data: Optional[Dict] = None) -> str:
        """
        Generate response using LLM with automatic personalization.
        Supports both OpenAI and Gemini.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            company_data: Optional company data for personalization
            
        Returns:
            LLM response text (personalized to the startup)
        """
        # Personalize the prompt with company data
        personalized_prompt = self.personalize_prompt(prompt, company_data)
        
        # Use Gemini if configured
        if self.use_gemini and hasattr(self, 'gemini_model'):
            try:
                # Enhance system prompt with personalization instructions
                enhanced_system_prompt = system_prompt or ""
                if company_data:
                    company_name = company_data.get('company_name', 'this startup')
                    enhanced_system_prompt += f"\n\nIMPORTANT: All responses must be personalized specifically for {company_name}. Use the company's specific details, industry, problem, solution, and context provided. Make responses relevant and tailored to this startup's unique situation."
                
                # Combine system prompt and user prompt for Gemini
                full_prompt = f"{enhanced_system_prompt}\n\n{personalized_prompt}" if enhanced_system_prompt else personalized_prompt
                
                response = self.gemini_model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": self.temperature,
                    }
                )
                return response.text
            except Exception as e:
                logger.error(f"Error generating response with Gemini: {e}")
                # Fallback to OpenAI if Gemini fails and auto mode
                if self.ai_provider == "auto":
                    logger.info("Falling back to OpenAI...")
                    self.use_gemini = False
                    # If model is Gemini, change to OpenAI model
                    if "gemini" in self.model.lower():
                        logger.warning(f"Changing model from '{self.model}' to OpenAI default")
                        self.model = "gpt-4-turbo-preview"
                    # Initialize OpenAI client if not already done
                    if not hasattr(self, 'client') or self.client is None:
                        api_key = os.getenv("OPENAI_API_KEY")
                        if api_key and OPENAI_AVAILABLE:
                            self.client = OpenAI(api_key=api_key)
                        else:
                            raise ValueError("Cannot fallback to OpenAI: API key not found")
                else:
                    raise
        
        # Use OpenAI
        messages = []
        
        # Enhance system prompt with personalization instructions
        enhanced_system_prompt = system_prompt or ""
        if company_data:
            company_name = company_data.get('company_name', 'this startup')
            enhanced_system_prompt += f"\n\nIMPORTANT: All responses must be personalized specifically for {company_name}. Use the company's specific details, industry, problem, solution, and context provided. Make responses relevant and tailored to this startup's unique situation."
        
        if enhanced_system_prompt:
            messages.append({"role": "system", "content": enhanced_system_prompt})
        
        messages.append({"role": "user", "content": personalized_prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            # Check if it's a quota/rate limit error and we're in auto mode
            # Use original_ai_provider to check, since ai_provider may have been changed to "openai" during init
            is_quota_error = ("429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower() or "insufficient_quota" in error_str.lower())
            
            if (self.original_ai_provider == "auto" or self.ai_provider == "auto") and is_quota_error:
                logger.warning(f"OpenAI quota exceeded or rate limited: {e}")
                logger.info("Attempting to fallback to Gemini...")
                
                # Try to use Gemini as fallback - reload environment variables
                from dotenv import load_dotenv
                load_dotenv()  # Reload to ensure we have latest env vars
                
                gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                logger.info(f"GEMINI_API_KEY found: {'YES' if gemini_key else 'NO'}")
                
                # Try to import Gemini dynamically (in case it's installed but GEMINI_AVAILABLE wasn't set)
                gemini_imported = False
                genai = None
                try:
                    import google.generativeai as genai
                    gemini_imported = True
                    logger.info("[OK] google-generativeai imported successfully")
                except ImportError:
                    logger.warning("[X] google-generativeai not installed. Cannot use Gemini fallback.")
                    logger.info("Install with: pip install google-generativeai")
                
                if gemini_key and gemini_imported:
                    try:
                        genai.configure(api_key=gemini_key)
                        # Use Gemini model
                        if "gemini" in self.model.lower():
                            gemini_model = genai.GenerativeModel(self.model)
                        else:
                            gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                        
                        # Combine system prompt and user prompt for Gemini
                        enhanced_system_prompt = system_prompt or ""
                        if company_data:
                            company_name = company_data.get('company_name', 'this startup')
                            enhanced_system_prompt += f"\n\nIMPORTANT: All responses must be personalized specifically for {company_name}. Use the company's specific details, industry, problem, solution, and context provided. Make responses relevant and tailored to this startup's unique situation."
                        
                        full_prompt = f"{enhanced_system_prompt}\n\n{personalized_prompt}" if enhanced_system_prompt else personalized_prompt
                        
                        logger.info("Using Gemini as fallback for OpenAI quota error")
                        response = gemini_model.generate_content(
                            full_prompt,
                            generation_config={
                                "temperature": self.temperature,
                            }
                        )
                        return response.text
                    except Exception as gemini_error:
                        logger.error(f"Gemini fallback also failed: {gemini_error}")
                        raise e  # Raise original OpenAI error
                else:
                    if not gemini_key:
                        logger.warning("[!] GEMINI_API_KEY not found in environment. Cannot fallback to Gemini.")
                        logger.info("[TIP] Add GEMINI_API_KEY to your .env file to enable automatic fallback.")
                    if not gemini_imported:
                        logger.warning("[!] google-generativeai not installed. Cannot fallback to Gemini.")
                        logger.info("[TIP] Install with: pip install google-generativeai")
                    # Re-raise the original error if fallback can't proceed
                    logger.error(f"Error generating response: {e}")
                    raise
            else:
                # Not a quota error or not in auto mode - just re-raise
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

