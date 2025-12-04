"""Team Agent - Helps with team building, role recommendations, and job descriptions."""

import logging
import json
from typing import Dict, List, Optional

from .base_agent import BaseAgent
from ..rag.retriever import Retriever
from ..utils.web_search import WebSearcher

logger = logging.getLogger(__name__)


class TeamAgent(BaseAgent):
    """Agent specialized in team building, role recommendations, and job description generation."""
    
    TEAM_QUESTIONNAIRE = [
        {
            "id": "current_team_size",
            "question": "👥 How many people are currently on your team?",
            "type": "select",
            "options": ["Just founders", "2-5 people", "6-10 people", "11-20 people", "20+ people"],
            "required": True
        },
        {
            "id": "existing_roles",
            "question": "👔 What roles do you currently have? (Select all that apply)",
            "type": "multiselect",
            "options": [
                "CEO/Founder",
                "CTO/Technical Lead",
                "CMO/Marketing Lead",
                "CFO/Finance",
                "Sales Lead",
                "Product Manager",
                "Engineers/Developers",
                "Designers",
                "Operations",
                "Customer Success",
                "Other"
            ],
            "required": True
        },
        {
            "id": "team_gaps",
            "question": "⚠️ What are your biggest team gaps or needs?",
            "type": "multiselect",
            "options": [
                "Technical/Engineering",
                "Product Management",
                "Marketing/Growth",
                "Sales/Business Development",
                "Design/UX",
                "Operations",
                "Finance/Accounting",
                "Customer Success/Support",
                "Data Science/Analytics",
                "DevOps/Infrastructure",
                "Other"
            ],
            "required": True
        },
        {
            "id": "hiring_priority",
            "question": "🎯 What's your hiring priority?",
            "type": "select",
            "options": [
                "Urgent - Need to hire ASAP",
                "High priority - Next 1-3 months",
                "Moderate - Next 3-6 months",
                "Planning - Just exploring options"
            ],
            "required": True
        },
        {
            "id": "budget_range",
            "question": "💰 What's your budget range for hiring?",
            "type": "select",
            "options": [
                "Under $50K",
                "$50K - $100K",
                "$100K - $150K",
                "$150K - $200K",
                "$200K+",
                "Equity-heavy (lower cash)",
                "Not sure yet"
            ],
            "required": True
        },
        {
            "id": "work_location",
            "question": "🌍 Work location preference?",
            "type": "select",
            "options": ["Remote", "On-site", "Hybrid", "Flexible"],
            "required": True
        },
        {
            "id": "company_stage",
            "question": "🚀 What stage is your company at?",
            "type": "select",
            "options": ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"],
            "required": True
        }
    ]
    
    ROLE_SPECIFIC_QUESTIONNAIRE = [
        {
            "id": "experience_level",
            "question": "📊 What experience level are you looking for?",
            "type": "select",
            "options": [
                "Junior (0-2 years)",
                "Mid-level (2-5 years)",
                "Senior (5-10 years)",
                "Lead/Principal (10+ years)",
                "Flexible"
            ],
            "required": True
        },
        {
            "id": "must_have_skills",
            "question": "✅ Must-have skills (comma-separated or list):",
            "type": "textarea",
            "required": True,
            "placeholder": "e.g., Python, React, AWS, 3+ years experience, etc."
        },
        {
            "id": "nice_to_have_skills",
            "question": "⭐ Nice-to-have skills (optional):",
            "type": "textarea",
            "required": False,
            "placeholder": "e.g., Machine Learning, Docker, etc."
        },
        {
            "id": "employment_type",
            "question": "💼 Employment type?",
            "type": "select",
            "options": ["Full-time", "Part-time", "Contract", "Internship", "Flexible"],
            "required": True
        },
        {
            "id": "equity_offering",
            "question": "📈 Will you offer equity?",
            "type": "select",
            "options": ["Yes, equity included", "No equity", "Negotiable"],
            "required": True
        },
        {
            "id": "start_date",
            "question": "📅 When do you need them to start?",
            "type": "select",
            "options": ["ASAP", "Within 1 month", "1-3 months", "3-6 months", "Flexible"],
            "required": True
        },
        {
            "id": "additional_requirements",
            "question": "📝 Any additional requirements or preferences?",
            "type": "textarea",
            "required": False,
            "placeholder": "e.g., Must have startup experience, Industry-specific knowledge, etc."
        }
    ]
    
    def __init__(self, retriever: Retriever, model: str = "gpt-4-turbo-preview"):
        """
        Initialize Team Agent.
        
        Args:
            retriever: Retriever instance for RAG
            model: LLM model name
        """
        super().__init__("team", retriever, model=model)
        self.web_searcher = WebSearcher(max_results=5)
        logger.info("TeamAgent initialized")
    
    def analyze_team_needs(self, company_context: Dict, team_context: Dict) -> Dict:
        """
        Analyze team needs and recommend roles based on company and team information.
        
        Args:
            company_context: Company details (product, problem, solution, industry, stage)
            team_context: Team information (current team, gaps, budget)
            
        Returns:
            Role recommendations with salary ranges and skillsets
        """
        logger.info("Analyzing team needs and recommending roles")
        
        # Combine contexts
        full_context = {**company_context, **team_context}
        
        # Retrieve team building examples
        team_data = self.retrieve_context(
            f"team building startup roles {full_context.get('industry', '')} {full_context.get('company_stage', '')}",
            top_k=5
        )
        
        # Web search for role market data
        topic_context = f"{full_context.get('industry', '')} {full_context.get('team_gaps', [])}"
        web_results = self.web_searcher.search(
            f"startup roles {full_context.get('industry', '')} {full_context.get('company_stage', '')} salary",
            topic_context=topic_context,
            max_results=8
        )
        
        prompt = f"""Analyze team needs and recommend job roles for this startup:

COMPANY CONTEXT:
- Company: {full_context.get('company_name', 'Startup')}
- Industry: {full_context.get('industry', 'N/A')}
- Stage: {full_context.get('company_stage', 'N/A')}
- Product/Solution: {full_context.get('solution', 'N/A')}
- Problem: {full_context.get('problem', 'N/A')}

CURRENT TEAM:
- Team Size: {full_context.get('current_team_size', 'N/A')}
- Existing Roles: {', '.join(full_context.get('existing_roles', []))}
- Team Gaps: {', '.join(full_context.get('team_gaps', []))}
- Hiring Priority: {full_context.get('hiring_priority', 'N/A')}
- Budget: {full_context.get('budget_range', 'N/A')}
- Location: {full_context.get('work_location', 'N/A')}

TEAM BUILDING EXAMPLES:
{team_data.get('context', 'No relevant examples found')}

MARKET DATA (Salary & Trends):
{self._format_web_results(web_results) if web_results else 'No market data found'}

TASK: Recommend 3-5 job roles that this startup needs. For each role, provide:

1. ROLE TITLE (specific, e.g., "Senior Full-Stack Engineer" not just "Engineer")
2. WHY THIS ROLE IS NEEDED (based on product, gaps, stage)
3. TYPICAL SALARY RANGE (based on location, stage, budget - use market data)
4. REQUIRED SKILLSET (key skills needed)
5. EXPERIENCE LEVEL (Junior/Mid/Senior)
6. PRIORITY (High/Medium/Low based on hiring priority)

Format as a numbered list with clear sections for each role.
Be specific and actionable. Consider the company stage and budget constraints."""
        
        system_prompt = """You are a startup hiring expert and organizational consultant. Analyze team needs 
and recommend specific, actionable job roles with realistic salary ranges and skillsets based on company stage, 
budget, and industry standards."""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = team_data.get('sources', [])
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
    
    def get_role_market_data(self, role_title: str, location: str, industry: str) -> Dict:
        """
        Get market data for a specific role (salary, skillset trends).
        
        Args:
            role_title: Job title
            location: Work location (Remote/On-site/etc.)
            industry: Industry sector
            
        Returns:
            Market data including salary range and skillset trends
        """
        logger.info(f"Getting market data for role: {role_title}")
        
        # Web search for salary and skillset data
        salary_query = f"{role_title} salary {location} {industry} 2025"
        skills_query = f"{role_title} skills requirements {industry}"
        
        salary_results = self.web_searcher.search(salary_query, topic_context=role_title, max_results=5)
        skills_results = self.web_searcher.search(skills_query, topic_context=role_title, max_results=5)
        
        prompt = f"""Get market data for this job role:

ROLE: {role_title}
LOCATION: {location}
INDUSTRY: {industry}

SALARY DATA:
{self._format_web_results(salary_results) if salary_results else 'No salary data found'}

SKILLSET DATA:
{self._format_web_results(skills_results) if skills_results else 'No skillset data found'}

TASK: Extract and summarize:
1. Salary Range (min-max, percentiles if available)
2. Key Skills Required (most common/important)
3. Experience Level Expectations
4. Market Demand (high/medium/low)
5. Location Impact (if remote vs on-site affects salary)

Be specific with numbers and data points."""
        
        system_prompt = "You are a compensation and hiring market research expert. Extract and summarize salary and skillset data from search results."
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = []
        for result in salary_results + skills_results:
            all_sources.append({
                'source': result.get('url', 'Web Search'),
                'title': result.get('title', ''),
                'similarity': result.get('relevance_score', 0)
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def generate_job_description(self, role_title: str, company_context: Dict, 
                                 team_context: Dict, role_details: Dict) -> Dict:
        """
        Generate comprehensive job description for a role.
        
        Args:
            role_title: Job title
            company_context: Company information
            team_context: Team information
            role_details: Role-specific details (skills, experience, etc.)
            
        Returns:
            Complete job description
        """
        logger.info(f"Generating job description for: {role_title}")
        
        # Get market data for the role
        market_data = self.get_role_market_data(
            role_title,
            team_context.get('work_location', 'Remote'),
            company_context.get('industry', '')
        )
        
        # Retrieve JD examples
        jd_data = self.retrieve_context(
            f"job description {role_title} {company_context.get('industry', '')}",
            top_k=5
        )
        
        # Web search for JD best practices
        web_results = []
        if jd_data.get('count', 0) < 3:
            web_results = self.web_searcher.search(
                f"job description template {role_title} startup",
                topic_context=role_title
            )
        
        # Combine all context
        full_context = {**company_context, **team_context, **role_details}
        
        prompt = f"""Generate a comprehensive, professional job description for this role:

ROLE: {role_title}

COMPANY INFORMATION:
- Company Name: {full_context.get('company_name', 'Our Startup')}
- Industry: {full_context.get('industry', 'Technology')}
- Stage: {full_context.get('company_stage', 'Seed')}
- Product/Solution: {full_context.get('solution', 'N/A')}
- Problem We Solve: {full_context.get('problem', 'N/A')}

ROLE DETAILS:
- Experience Level: {full_context.get('experience_level', 'Mid-level')}
- Must-Have Skills: {full_context.get('must_have_skills', 'N/A')}
- Nice-to-Have Skills: {full_context.get('nice_to_have_skills', 'N/A')}
- Employment Type: {full_context.get('employment_type', 'Full-time')}
- Equity: {full_context.get('equity_offering', 'Negotiable')}
- Start Date: {full_context.get('start_date', 'Flexible')}
- Location: {full_context.get('work_location', 'Remote')}
- Additional Requirements: {full_context.get('additional_requirements', 'None')}

MARKET DATA:
{market_data.get('response', 'No market data available')}

JD EXAMPLES:
{jd_data.get('context', 'No relevant examples found')}

WEB SEARCH RESULTS:
{self._format_web_results(web_results) if web_results else ''}

TASK: Generate a complete, professional job description with these sections:

1. JOB TITLE (clear and specific)
2. COMPANY OVERVIEW (brief, compelling - 2-3 sentences)
3. ABOUT THE ROLE (what they'll do, why it matters)
4. KEY RESPONSIBILITIES (5-8 bullet points, specific and actionable)
5. REQUIRED QUALIFICATIONS (must-haves, based on must_have_skills)
6. PREFERRED QUALIFICATIONS (nice-to-haves)
7. WHAT WE OFFER (salary range, equity, benefits, culture)
8. LOCATION & WORK ARRANGEMENT
9. HOW TO APPLY (clear application instructions)

Make it:
- Professional yet engaging
- Specific and detailed
- Attractive to candidates
- Honest about requirements
- Startup-appropriate (mention equity, growth opportunity, impact)

Include salary range from market data if available."""
        
        system_prompt = """You are an expert in writing compelling, professional job descriptions for startups. 
Create job descriptions that attract top talent while being honest and specific about requirements."""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = market_data.get('sources', []) + jd_data.get('sources', [])
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
        Process a general team/hiring-related query.
        
        Args:
            query: User query
            context: Optional company/team context
            
        Returns:
            Agent response
        """
        # Try RAG first
        context_data = self.retrieve_context(query, top_k=5)
        
        # Use web search if RAG doesn't have enough results
        web_results = []
        if context_data.get('count', 0) < 3:
            logger.info("RAG results insufficient, using web search fallback")
            topic_context = f"{context.get('industry', '')} {context.get('company_stage', '')}" if context else query
            web_results = self.web_searcher.search(
                query,
                topic_context=topic_context
            )
        
        prompt = f"""User Question: {query}

Relevant Team/Hiring Data:
{context_data.get('context', 'No relevant context found in database')}

Web Search Results:
{self._format_web_results(web_results) if web_results else 'No additional web results'}

Provide helpful team building and hiring advice based on the context above."""
        
        if context:
            prompt += f"\n\nCompany/Team Context:\n{json.dumps(context, indent=2)}"
        
        system_prompt = """You are a team building and hiring expert. Answer questions about team structure, 
role recommendations, job descriptions, hiring best practices, and startup team building."""
        
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

