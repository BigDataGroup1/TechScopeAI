"""Competitive Agent - Analyzes competitors and market positioning."""

import logging
import json
from typing import Dict, List, Optional

from .base_agent import BaseAgent
from ..rag.retriever import Retriever

logger = logging.getLogger(__name__)


class CompetitiveAgent(BaseAgent):
    """Agent specialized in competitive analysis and market positioning."""
    
    COMPETITIVE_QUESTIONNAIRE = [
        {
            "id": "company_name",
            "question": "🏢 What is your company name?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., TechFlow Solutions Inc."
        },
        {
            "id": "industry",
            "question": "🏭 What industry does your company operate in?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., AI/ML, SaaS, Healthcare, Fintech..."
        },
        {
            "id": "solution",
            "question": "💡 What is your product or service?",
            "type": "textarea",
            "required": True,
            "placeholder": "Describe your solution..."
        },
        {
            "id": "target_market",
            "question": "🎯 Who is your target market?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., Small businesses, Enterprise, Consumers..."
        },
        {
            "id": "known_competitors",
            "question": "🔍 Do you know who your main competitors are?",
            "type": "select",
            "options": ["Yes, I know them", "Somewhat, but not sure", "No, need help identifying"],
            "required": True
        },
        {
            "id": "competitor_names",
            "question": "📋 If yes, please list your main competitors:",
            "type": "textarea",
            "required": False,
            "depends_on": {"known_competitors": "Yes, I know them"},
            "placeholder": "List competitor names, one per line..."
        },
        {
            "id": "differentiation",
            "question": "🏆 How do you differentiate from competitors?",
            "type": "textarea",
            "required": False,
            "placeholder": "What makes you different or better..."
        },
        {
            "id": "market_position",
            "question": "📍 How would you describe your market position?",
            "type": "select",
            "options": [
                "Market leader",
                "Strong challenger",
                "Niche player",
                "New entrant",
                "Not sure"
            ],
            "required": True
        },
        {
            "id": "competitive_concerns",
            "question": "⚠️ What are your main competitive concerns?",
            "type": "multiselect",
            "options": [
                "Price competition",
                "Feature parity",
                "Market saturation",
                "Large incumbents",
                "New entrants",
                "Customer acquisition",
                "Other"
            ],
            "required": False
        }
    ]
    
    def __init__(self, retriever: Retriever, model: str = "gpt-4-turbo-preview", ai_provider: str = "openai"):
        """
        Initialize Competitive Agent.
        
        Args:
            retriever: Retriever instance for RAG (should use "competitive" category)
            model: LLM model name
            ai_provider: AI provider to use ("openai", "gemini", or "auto")
        """
        super().__init__("competitive", retriever, model=model, ai_provider=ai_provider)
        logger.info("CompetitiveAgent initialized")
    
    def analyze_competitors(self, company_details: Dict, competitors: Optional[List[Dict]] = None) -> Dict:
        """
        Analyze competitors and provide competitive positioning.
        
        Args:
            company_details: Company information
            competitors: Optional list of competitor details
            
        Returns:
            Competitive analysis with positioning recommendations
        """
        logger.info(f"Analyzing competitors for: {company_details.get('company_name', 'Unknown')}")
        
        # Build query
        query = f"{company_details.get('industry', '')} {company_details.get('problem', '')} competitors"
        
        # Retrieve competitive data
        competitive_data = self.retrieve_context(query, top_k=10)
        
        similar_companies = self.retrieve_context(
            f"{company_details.get('industry', '')} {company_details.get('solution', '')}",
            top_k=5
        )
        
        market_insights = self.retrieve_context(
            f"{company_details.get('industry', '')} market trends competition",
            top_k=5
        )
        
        # Build prompt
        prompt = f"""Analyze competitors and provide competitive positioning for this startup:

COMPANY DETAILS:
{json.dumps(company_details, indent=2)}

COMPETITORS PROVIDED:
{json.dumps(competitors, indent=2) if competitors else 'None provided'}

COMPETITIVE DATA FROM DATABASE:
{competitive_data.get('context', '')}

SIMILAR COMPANIES:
{similar_companies.get('context', '')}

MARKET INSIGHTS:
{market_insights.get('context', '')}

TASK: Provide a comprehensive competitive analysis:
1. Direct Competitors (companies solving the same problem)
2. Indirect Competitors (alternative solutions)
3. Competitive Landscape Map (positioning)
4. Your Competitive Advantages
5. Competitive Weaknesses to Address
6. Differentiation Strategy
7. Market Positioning Recommendation

IMPORTANT: If any critical information is missing (company name, industry, solution, target market), ask for clarification before proceeding. 
Be specific and data-driven. Reference the competitive data provided."""
        
        system_prompt = """You are an expert competitive analyst with deep knowledge of market dynamics and competitive positioning. 
Analyze competitors thoroughly and provide highly detailed, actionable positioning recommendations. 

When generating responses:
- Be comprehensive and detailed - provide in-depth analysis, not just surface-level observations
- Include specific examples, data points, and evidence from the competitive data
- Structure your response clearly with sections, bullet points, and actionable recommendations
- If the user asks for more details, provide extensive analysis with market insights, trends, and strategic recommendations
- Use the competitive data to identify market trends, positioning opportunities, and competitive threats
- Provide specific, actionable advice that startups can implement immediately

IMPORTANT - Ask for clarification and more details:
- If critical information is missing (company name, industry, solution, target market), ask for it explicitly
- If the company details are incomplete, ask follow-up questions to get the necessary information
- Request clarification on: known competitors, differentiation points, market position, competitive concerns
- Don't proceed with incomplete information - ask for what you need first"""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_details)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        # Combine sources
        all_sources = (
            competitive_data.get('sources', []) + 
            similar_companies.get('sources', []) + 
            market_insights.get('sources', [])
        )
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def compare_to_competitors(self, company_details: Dict, competitor_name: str) -> Dict:
        """
        Compare your company to a specific competitor.
        
        Args:
            company_details: Your company information
            competitor_name: Name of competitor to compare against
            
        Returns:
            Detailed comparison analysis
        """
        logger.info(f"Comparing to competitor: {competitor_name}")
        
        # Retrieve competitor data
        competitor_data = self.retrieve_context(
            f"{competitor_name} {company_details.get('industry', '')}",
            top_k=5
        )
        
        # Build comparison prompt
        prompt = f"""Compare this startup to a specific competitor:

YOUR COMPANY:
{json.dumps(company_details, indent=2)}

COMPETITOR: {competitor_name}

COMPETITOR DATA:
{competitor_data.get('context', '')}

TASK: Provide a detailed comparison:
1. Feature Comparison (what each offers)
2. Market Position (where each stands)
3. Strengths & Weaknesses (of each)
4. Your Advantages (what you do better)
5. Their Advantages (what they do better)
6. Recommendation (how to position against them)

Be objective and strategic."""
        
        system_prompt = """You are an expert competitive analyst. Provide highly detailed, objective, strategic comparisons between companies. 
Include specific feature comparisons, market positioning analysis, strengths/weaknesses, and actionable recommendations. 
Be comprehensive and thorough in your analysis."""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_details)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        return self.format_response(
            response=response_text,
            sources=competitor_data.get('sources', [])
        )
    
    def identify_competitive_advantages(self, company_details: Dict) -> Dict:
        """
        Identify and highlight competitive advantages.
        
        Args:
            company_details: Company information
            
        Returns:
            Analysis of competitive advantages
        """
        logger.info("Identifying competitive advantages")
        
        # Retrieve competitive context
        competitive_context = self.retrieve_context(
            f"{company_details.get('industry', '')} competitive advantages differentiation",
            top_k=5
        )
        
        prompt = f"""Identify competitive advantages for this startup:

COMPANY DETAILS:
{json.dumps(company_details, indent=2)}

COMPETITIVE CONTEXT:
{competitive_context.get('context', '')}

TASK: Identify and analyze:
1. Unique Value Proposition
2. Competitive Moats (what's defensible)
3. Technology Advantages
4. Market Advantages
5. Team Advantages
6. How to Communicate These Advantages

Be specific and actionable."""
        
        system_prompt = """You are a strategic advisor specializing in competitive analysis. Identify and articulate competitive advantages clearly and comprehensively. 
Provide detailed analysis of each advantage, explain why it matters, and suggest how to leverage it. 
Include market context and strategic recommendations."""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_details)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        return self.format_response(
            response=response_text,
            sources=competitive_context.get('sources', [])
        )
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a general competitive analysis query.
        
        Args:
            query: User query
            context: Optional company context
            
        Returns:
            Agent response
        """
        # Retrieve relevant context
        context_data = self.retrieve_context(query, top_k=5)
        
        # Use web search if RAG doesn't have enough results (especially for news/research queries)
        web_results = []
        if context_data.get('count', 0) < 3:
            logger.info("RAG results insufficient, using web search fallback")
            topic_context = f"{context.get('industry', '')} {context.get('target_market', '')}" if context else query
            search_result = self.mcp_client.web_search(
                query=query,
                topic_context=topic_context
            )
            if search_result.get("success"):
                web_results = search_result.get("results", [])
        
        prompt = f"""User Question: {query}

Relevant Competitive Data:
{context_data.get('context', 'No relevant context found')}

Web Search Results:
{self._format_web_results(web_results) if web_results else 'No additional web results'}

Provide helpful competitive analysis advice based on the context above. If this is a news or research query, prioritize the web search results for current information."""
        
        if context:
            prompt += f"\n\nCompany Context:\n{json.dumps(context, indent=2)}"
        
        system_prompt = """You are an expert competitive analyst. Answer questions about competitors, market positioning, and differentiation strategies with comprehensive detail. 
When users ask questions, provide thorough, well-structured answers with:
- Detailed explanations and analysis
- Specific examples and data points
- Actionable recommendations
- Market context and trends
- Strategic insights

IMPORTANT - Ask for clarification and more details:
- If the query is vague or unclear, ask specific clarifying questions
- If you need more information to provide a better answer, proactively ask for it
- Request details about: company name, industry, target market, known competitors, differentiation points
- Ask follow-up questions to understand the user's specific needs
- Don't assume - ask for clarification when needed

If asked for more details, provide extensive, in-depth analysis. Structure responses clearly with sections and bullet points for readability."""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(context)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        # Combine sources from RAG and web search
        all_sources = context_data.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'snippet': web_result.get('snippet', ''),
                'similarity': web_result.get('relevance_score', 0),
                'is_web_search': True  # Flag to identify web search sources
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
        for i, result in enumerate(web_results[:5], 1):
            formatted.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', '')}\n"
                f"   Snippet: {result.get('snippet', '')[:200]}...\n"
                f"   Relevance: {result.get('relevance_score', 0):.2f}"
            )
        
        return "\n\n".join(formatted)

