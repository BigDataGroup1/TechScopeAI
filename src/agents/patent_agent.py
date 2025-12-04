"""Patent Agent - Helps with patent research, filing, and IP strategy."""

import logging
import json
from typing import Dict, List, Optional

from .base_agent import BaseAgent
from ..rag.retriever import Retriever
from ..utils.web_search import WebSearcher

logger = logging.getLogger(__name__)


class PatentAgent(BaseAgent):
    """Agent specialized in patent research, filing guidance, and IP strategy."""
    
    PATENT_QUESTIONNAIRE = [
        {
            "id": "invention_description",
            "question": "🔬 What is your invention or technology? Please describe it in detail.",
            "type": "textarea",
            "required": True,
            "placeholder": "Describe your invention, how it works, and what problem it solves..."
        },
        {
            "id": "industry",
            "question": "🏭 What industry or field does your invention belong to?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., AI/ML, Biotechnology, Software, Hardware..."
        },
        {
            "id": "novelty",
            "question": "💡 What makes your invention new or different from existing solutions?",
            "type": "textarea",
            "required": True,
            "placeholder": "Explain the unique aspects, improvements, or innovations..."
        },
        {
            "id": "prior_art_awareness",
            "question": "🔍 Are you aware of any existing patents, products, or publications similar to your invention?",
            "type": "select",
            "options": ["Yes, I know of some", "No, not aware of any", "Not sure"],
            "required": True
        },
        {
            "id": "prior_art_details",
            "question": "📋 If yes, please list any known similar patents, products, or publications:",
            "type": "textarea",
            "required": False,
            "depends_on": {"prior_art_awareness": "Yes, I know of some"},
            "placeholder": "List patents, products, or publications you're aware of..."
        },
        {
            "id": "development_stage",
            "question": "🚀 What stage is your invention at?",
            "type": "select",
            "options": ["Concept/Idea", "Prototype", "Working Product", "In Market"],
            "required": True
        },
        {
            "id": "public_disclosure",
            "question": "📢 Have you publicly disclosed this invention (published, presented, sold)?",
            "type": "select",
            "options": ["No public disclosure", "Published in paper/article", "Presented at conference", "Product already on market", "Other"],
            "required": True
        },
        {
            "id": "disclosure_date",
            "question": "📅 If disclosed, when was it first disclosed? (YYYY-MM-DD)",
            "type": "text",
            "required": False,
            "depends_on": {"public_disclosure": ["Published in paper/article", "Presented at conference", "Product already on market", "Other"]},
            "placeholder": "YYYY-MM-DD or leave blank if not disclosed"
        },
        {
            "id": "filing_priority",
            "question": "⏰ How urgent is filing a patent?",
            "type": "select",
            "options": ["Very urgent (within 1 month)", "Moderate (1-3 months)", "Not urgent (3+ months)", "Just exploring"],
            "required": True
        },
        {
            "id": "geographic_interest",
            "question": "🌍 Where do you want patent protection?",
            "type": "multiselect",
            "options": ["United States (USPTO)", "Europe (EPO)", "International (PCT)", "Other countries"],
            "required": True
        },
        {
            "id": "budget_range",
            "question": "💰 What is your budget range for patent filing?",
            "type": "select",
            "options": ["Under $5,000", "$5,000 - $15,000", "$15,000 - $50,000", "$50,000+", "Not sure yet"],
            "required": True
        }
    ]
    
    def __init__(self, retriever: Retriever, model: str = "gpt-4-turbo-preview"):
        """
        Initialize Patent Agent.
        
        Args:
            retriever: Retriever instance for RAG
            model: LLM model name
        """
        super().__init__("patent", retriever, model=model)
        self.web_searcher = WebSearcher(max_results=5)
        logger.info("PatentAgent initialized")
    
    def search_patents(self, query: str, company_context: Optional[Dict] = None) -> Dict:
        """
        Search for existing patents related to a technology or idea.
        
        Args:
            query: Technology or idea to search for
            company_context: Optional company details for context
            
        Returns:
            Patent search results with analysis
        """
        logger.info(f"Searching patents for: {query}")
        
        # Try RAG first
        patent_data = self.retrieve_context(
            f"patent {query} intellectual property",
            top_k=5
        )
        
        # If RAG doesn't have enough results, use web search
        web_results = []
        if patent_data.get('count', 0) < 3:
            logger.info("RAG results insufficient, using web search fallback")
            topic_context = f"{company_context.get('industry', '')} {company_context.get('solution', '')}" if company_context else query
            web_results = self.web_searcher.search(
                f"patent {query} intellectual property",
                topic_context=topic_context
            )
        
        # Build prompt
        prompt = f"""Search for existing patents related to this technology/idea:

TECHNOLOGY/IDEA: {query}

COMPANY CONTEXT:
{json.dumps(company_context, indent=2) if company_context else 'None provided'}

PATENT DATA FROM DATABASE:
{patent_data.get('context', 'No relevant patent data found in database')}

WEB SEARCH RESULTS:
{self._format_web_results(web_results) if web_results else 'No additional web results'}

TASK: Provide a comprehensive patent search analysis:
1. Existing Patents Found (list key patents if found)
2. Patent Landscape (what's already patented in this space)
3. Patentability Assessment (is this idea patentable?)
4. Potential Patent Conflicts (existing patents that might conflict)
5. Recommendations (next steps for patent research/filing)
6. Key Patent Databases to Check (USPTO, EPO, WIPO, etc.)

IMPORTANT: If the technology/idea description is vague or incomplete, ask for more details about: what the invention does, how it works, what problem it solves, what makes it unique.
Be specific and cite sources when available."""
        
        system_prompt = """You are an expert patent research specialist with deep knowledge of patent databases, prior art search, and IP landscape analysis. 
Help startups understand the patent landscape for their technology and provide comprehensive, actionable guidance on patent research and filing strategies.

When generating responses:
- Provide highly detailed, thorough analysis of patent search results
- Include specific patent numbers, dates, and key findings
- Explain the implications of each finding
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with strategic recommendations
- Be comprehensive and cover all relevant aspects of the patent landscape"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        # Combine sources
        all_sources = patent_data.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'similarity': web_result.get('relevance_score', 0)
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def assess_patentability(self, invention_description: str, 
                           company_context: Optional[Dict] = None) -> Dict:
        """
        Assess whether an invention is patentable.
        
        Args:
            invention_description: Description of the invention
            company_context: Optional company details
            
        Returns:
            Patentability assessment
        """
        logger.info("Assessing patentability")
        
        # Retrieve relevant patent information
        patent_context = self.retrieve_context(
            f"patentability requirements novelty non-obviousness {invention_description}",
            top_k=5
        )
        
        # Web search if needed
        web_results = []
        if patent_context.get('count', 0) < 3:
            topic_context = f"{company_context.get('industry', '')} {invention_description}" if company_context else invention_description
            web_results = self.web_searcher.search(
                f"patentability requirements {invention_description}",
                topic_context=topic_context
            )
        
        prompt = f"""Assess the patentability of this invention:

INVENTION DESCRIPTION:
{invention_description}

COMPANY CONTEXT:
{json.dumps(company_context, indent=2) if company_context else 'None provided'}

PATENT LAW CONTEXT:
{patent_context.get('context', 'No relevant context found')}

WEB SEARCH RESULTS:
{self._format_web_results(web_results) if web_results else ''}

TASK: Provide a comprehensive patentability assessment:
1. Novelty Analysis (is this new?)
2. Non-Obviousness Analysis (is this inventive enough?)
3. Utility Analysis (does it have practical use?)
4. Prior Art Assessment (what similar inventions exist?)
5. Patentability Conclusion (likely patentable? why/why not?)
6. Recommendations (what to do next - file provisional? conduct prior art search?)

IMPORTANT: If the invention description is incomplete or unclear, ask for more details about: how the invention works, what makes it unique, what problem it solves, technical specifications, development stage.

Be thorough and cite legal requirements when relevant."""
        
        system_prompt = """You are an expert patent attorney with deep knowledge of patent law, USPTO requirements, and patentability assessment. 
Assess inventions comprehensively for patentability based on patent law requirements: novelty, non-obviousness, and utility.

When generating responses:
- Provide highly detailed, thorough patentability assessments
- Explain each requirement (novelty, non-obviousness, utility) in detail
- Include specific analysis of strengths and weaknesses
- Provide actionable recommendations for improving patentability
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with legal reasoning and examples
- Be comprehensive and cover all relevant aspects of patentability"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = patent_context.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'similarity': web_result.get('relevance_score', 0)
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def filing_strategy(self, company_context: Dict) -> Dict:
        """
        Provide patent filing strategy recommendations.
        
        Args:
            company_context: Company details including technology/inventions
            
        Returns:
            Filing strategy recommendations
        """
        logger.info("Generating patent filing strategy")
        
        # Retrieve relevant guidance
        strategy_context = self.retrieve_context(
            f"patent filing strategy provisional utility patent {company_context.get('industry', '')}",
            top_k=5
        )
        
        # Web search if needed
        web_results = []
        if strategy_context.get('count', 0) < 3:
            topic_context = f"{company_context.get('industry', '')} {company_context.get('solution', '')}"
            web_results = self.web_searcher.search(
                f"startup patent filing strategy {company_context.get('industry', '')}",
                topic_context=topic_context
            )
        
        prompt = f"""Provide patent filing strategy for this startup:

COMPANY DETAILS:
{json.dumps(company_context, indent=2)}

STRATEGY GUIDANCE FROM DATABASE:
{strategy_context.get('context', 'No relevant guidance found')}

WEB SEARCH RESULTS:
{self._format_web_results(web_results) if web_results else ''}

TASK: Provide a comprehensive patent filing strategy:
1. What to Patent (which aspects of the technology)
2. Filing Timeline (when to file - provisional vs. utility)
3. Geographic Strategy (US, international, PCT)
4. Budget Considerations (costs and prioritization)
5. Provisional vs. Utility Patents (recommendations)
6. Patent Portfolio Strategy (building a portfolio)
7. Next Steps (immediate actions)

Be practical and consider startup constraints."""
        
        system_prompt = """You are an expert patent strategy consultant with deep knowledge of IP law, patent filing processes, and startup IP strategy. 
Help startups develop comprehensive, practical patent filing strategies that balance protection with budget constraints.

When generating responses:
- Provide highly detailed, thorough analysis and recommendations
- Include specific timelines, costs, and strategic considerations
- Explain the reasoning behind each recommendation
- Structure responses clearly with sections, bullet points, and actionable next steps
- If asked for more details, provide extensive analysis with examples, case studies, and strategic insights
- Be comprehensive and cover all relevant aspects of patent strategy"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = strategy_context.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'similarity': web_result.get('relevance_score', 0)
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def prior_art_search(self, technology_description: str, 
                        company_context: Optional[Dict] = None) -> Dict:
        """
        Conduct a prior art search for a technology.
        
        Args:
            technology_description: Description of technology to search
            company_context: Optional company details
            
        Returns:
            Prior art search results
        """
        logger.info("Conducting prior art search")
        
        # Retrieve relevant information
        prior_art_context = self.retrieve_context(
            f"prior art {technology_description} existing patents",
            top_k=5
        )
        
        # Always use web search for prior art (patent databases)
        topic_context = f"{company_context.get('industry', '')} {technology_description}" if company_context else technology_description
        web_results = self.web_searcher.search(
            f"patent {technology_description} prior art USPTO",
            topic_context=topic_context,
            max_results=10
        )
        
        prompt = f"""Conduct a prior art search for this technology:

TECHNOLOGY DESCRIPTION:
{technology_description}

COMPANY CONTEXT:
{json.dumps(company_context, indent=2) if company_context else 'None provided'}

DATABASE CONTEXT:
{prior_art_context.get('context', 'No relevant context found')}

WEB SEARCH RESULTS (Patent Databases):
{self._format_web_results(web_results) if web_results else 'No results found'}

TASK: Provide a comprehensive prior art analysis:
1. Key Prior Art Found (list relevant patents/publications)
2. Similar Technologies (what exists that's similar)
3. Differences from Prior Art (how this differs)
4. Patent Database Recommendations (where to search further)
5. Search Strategy (how to conduct thorough prior art search)
6. Risk Assessment (likelihood of patent conflicts)

Be thorough and cite specific patents/publications when found."""
        
        system_prompt = """You are an expert patent researcher specializing in prior art searches and patent analysis. 
Conduct thorough prior art searches and identify existing patents and publications that might affect patentability.

When generating responses:
- Provide highly detailed, comprehensive prior art search results
- Include specific patent numbers, publication details, and relevance analysis
- Explain how each prior art reference relates to the invention
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with strategic recommendations
- Be comprehensive and cover all relevant prior art"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = prior_art_context.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'similarity': web_result.get('relevance_score', 0)
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a general patent-related query.
        
        Args:
            query: User query
            context: Optional company context
            
        Returns:
            Agent response
        """
        # Try RAG first
        context_data = self.retrieve_context(query, top_k=5)
        
        # Use web search if RAG doesn't have enough results
        web_results = []
        if context_data.get('count', 0) < 3:
            logger.info("RAG results insufficient, using web search fallback")
            topic_context = f"{context.get('industry', '')} {context.get('solution', '')}" if context else query
            web_results = self.web_searcher.search(
                query,
                topic_context=topic_context
            )
        
        prompt = f"""User Question: {query}

Relevant Patent/IP Data:
{context_data.get('context', 'No relevant context found in database')}

Web Search Results:
{self._format_web_results(web_results) if web_results else 'No additional web results'}

Provide helpful patent and intellectual property advice based on the context above."""
        
        if context:
            prompt += f"\n\nCompany Context:\n{json.dumps(context, indent=2)}"
        
        system_prompt = """You are an expert patent and intellectual property consultant with deep knowledge of patents, patentability, filing strategies, prior art, and IP protection for startups. 
Answer questions comprehensively about patents, patentability, filing strategies, prior art, and IP protection.

When generating responses:
- Provide highly detailed, thorough answers with comprehensive explanations
- Include specific examples, case studies, and strategic recommendations
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive, in-depth analysis
- Be comprehensive and cover all relevant aspects of the question
- Provide actionable advice that startups can implement

IMPORTANT - Ask for clarification and more details:
- If the query is vague or unclear, ask specific clarifying questions
- If you need more information to provide a better answer, proactively ask for it
- Request details about: invention description, industry, development stage, prior art awareness, geographic interest, budget
- Ask follow-up questions to understand the user's specific needs and goals
- Don't assume - ask for clarification when needed
- If information is missing, explicitly ask for it before proceeding"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = context_data.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'similarity': web_result.get('relevance_score', 0)
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
        for i, result in enumerate(web_results, 1):
            formatted.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', '')}\n"
                f"   Snippet: {result.get('snippet', '')[:200]}...\n"
                f"   Relevance: {result.get('relevance_score', 0):.2f}"
            )
        
        return "\n\n".join(formatted)

