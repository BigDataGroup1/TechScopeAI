"""Policy Agent - Helps with legal policies, compliance, and regulatory requirements."""

import logging
import json
from typing import Dict, List, Optional

from .base_agent import BaseAgent
from ..rag.retriever import Retriever
# Web search now via MCP client in BaseAgent

logger = logging.getLogger(__name__)


class PolicyAgent(BaseAgent):
    """Agent specialized in policy generation, compliance, and regulatory guidance."""
    
    POLICY_QUESTIONNAIRE = [
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
            "type": "select",
            "options": [
                "Technology/SaaS",
                "Healthcare/Medical",
                "Finance/Fintech",
                "Education/EdTech",
                "E-commerce/Retail",
                "Social Media/Platform",
                "Gaming/Entertainment",
                "Real Estate/PropTech",
                "Transportation/Mobility",
                "Other"
            ],
            "required": True
        },
        {
            "id": "business_model",
            "question": "💼 What is your primary business model?",
            "type": "select",
            "options": [
                "B2B (Business to Business)",
                "B2C (Business to Consumer)",
                "B2B2C (Business to Business to Consumer)",
                "Marketplace/Platform",
                "SaaS Subscription",
                "E-commerce",
                "Other"
            ],
            "required": True
        },
        {
            "id": "target_markets",
            "question": "🌍 Where do you operate or plan to operate? (Select all that apply)",
            "type": "multiselect",
            "options": [
                "United States",
                "European Union (EU)",
                "United Kingdom",
                "Canada",
                "Australia",
                "Other countries"
            ],
            "required": True
        },
        {
            "id": "data_collected",
            "question": "📊 What types of data do you collect from users? (Select all that apply)",
            "type": "multiselect",
            "options": [
                "Personal information (name, email, phone)",
                "Payment/financial information",
                "Health/medical data",
                "Location data",
                "Biometric data",
                "Children's data (under 18)",
                "User-generated content",
                "Cookies/tracking data",
                "Other sensitive data"
            ],
            "required": True
        },
        {
            "id": "user_types",
            "question": "👥 Who are your primary users?",
            "type": "select",
            "options": [
                "Adults only (18+)",
                "All ages (including children)",
                "Businesses only",
                "Mixed (adults and children)",
                "Other"
            ],
            "required": True
        },
        {
            "id": "third_party_services",
            "question": "🔗 Do you use third-party services that process user data?",
            "type": "select",
            "options": [
                "Yes, multiple services (analytics, payment, cloud, etc.)",
                "Yes, a few services",
                "No third-party services",
                "Not sure"
            ],
            "required": True
        },
        {
            "id": "third_party_details",
            "question": "📋 If yes, please list the main third-party services you use:",
            "type": "textarea",
            "required": False,
            "depends_on": {"third_party_services": ["Yes, multiple services (analytics, payment, cloud, etc.)", "Yes, a few services"]},
            "placeholder": "e.g., Google Analytics, Stripe, AWS, etc."
        },
        {
            "id": "policy_priority",
            "question": "🎯 What policies do you need help with? (Select all that apply)",
            "type": "multiselect",
            "options": [
                "Privacy Policy",
                "Terms of Service",
                "Cookie Policy",
                "Data Protection Policy",
                "Employee Handbook",
                "Acceptable Use Policy",
                "Refund/Return Policy",
                "Security Policy",
                "Other"
            ],
            "required": True
        },
        {
            "id": "compliance_requirements",
            "question": "⚖️ Are there specific compliance requirements you need to meet?",
            "type": "multiselect",
            "options": [
                "GDPR (EU General Data Protection Regulation)",
                "CCPA (California Consumer Privacy Act)",
                "HIPAA (Health Insurance Portability)",
                "PCI DSS (Payment Card Industry)",
                "FERPA (Education records)",
                "COPPA (Children's Online Privacy)",
                "SOC 2",
                "ISO 27001",
                "Not sure yet"
            ],
            "required": True
        },
        {
            "id": "existing_policies",
            "question": "📄 Do you currently have any policies in place?",
            "type": "select",
            "options": [
                "No, starting from scratch",
                "Yes, but need updates",
                "Yes, but need review/compliance check",
                "Yes, need to generate new ones"
            ],
            "required": True
        }
    ]
    
    def __init__(self, retriever: Retriever, model: str = "gpt-4-turbo-preview", ai_provider: str = "openai"):
        """
        Initialize Policy Agent.
        
        Args:
            retriever: Retriever instance for RAG
            model: LLM model name
            ai_provider: AI provider to use ("openai", "gemini", or "auto")
        """
        super().__init__("policy", retriever, model=model, ai_provider=ai_provider)
        logger.info("PolicyAgent initialized")
    
    def generate_privacy_policy(self, company_context: Dict) -> Dict:
        """
        Generate a privacy policy based on company context.
        
        Args:
            company_context: Company details and requirements
            
        Returns:
            Generated privacy policy with sources
        """
        logger.info("Generating privacy policy")
        
        # Retrieve relevant policy templates and guidance
        policy_context = self.retrieve_context(
            f"privacy policy GDPR CCPA {company_context.get('industry', '')} {company_context.get('data_collected', '')}",
            top_k=5
        )
        
        # Web search for latest regulations
        web_results = []
        if policy_context.get('count', 0) < 3:
            topic_context = f"{company_context.get('industry', '')} {company_context.get('target_markets', [])}"
            search_result = self.mcp_client.web_search(
                query=f"privacy policy requirements {company_context.get('industry', '')} {company_context.get('compliance_requirements', [])}",
                topic_context=topic_context
            )
            web_results = []
            if search_result.get("success"):
                web_results = search_result.get("results", [])
        
        prompt = f"""Generate a comprehensive Privacy Policy for this company:

COMPANY DETAILS:
{json.dumps(company_context, indent=2)}

POLICY GUIDANCE FROM DATABASE:
{policy_context.get('context', 'No relevant guidance found')}

WEB SEARCH RESULTS (Latest Regulations):
{self._format_web_results(web_results) if web_results else ''}

TASK: Generate a complete Privacy Policy that includes:
1. Introduction and Company Information
2. Information We Collect (based on data_collected)
3. How We Use Information
4. Data Sharing and Third Parties (mention third_party_services if applicable)
5. User Rights (GDPR, CCPA rights if applicable)
6. Data Security
7. Cookies and Tracking (if applicable)
8. Children's Privacy (if user_types includes children)
9. International Data Transfers (if target_markets includes multiple regions)
10. Contact Information
11. Updates to Policy

Ensure compliance with: {', '.join(company_context.get('compliance_requirements', []))}

IMPORTANT: If critical information is missing (company name, industry, data collected, target markets, user types), ask for clarification before generating the policy.
Be specific, legally sound, and tailored to the company's actual data practices."""
        
        system_prompt = """You are an expert legal policy consultant specializing in privacy policies, GDPR, CCPA, and data protection regulations. 
Generate comprehensive, legally compliant privacy policies for startups.

When generating responses:
- Provide highly detailed, thorough policy documents that cover all required sections
- Include specific legal language appropriate for the company's jurisdiction and data practices
- Explain the purpose and importance of each section
- Structure policies clearly with sections, subsections, and bullet points
- If asked for more details, provide extensive analysis with legal reasoning and examples
- Be comprehensive and ensure all regulatory requirements are met
- Include practical guidance on implementation and compliance"""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_context)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        all_sources = policy_context.get('sources', [])
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
    
    def generate_terms_of_service(self, company_context: Dict) -> Dict:
        """
        Generate Terms of Service based on company context.
        
        Args:
            company_context: Company details and requirements
            
        Returns:
            Generated Terms of Service with sources
        """
        logger.info("Generating Terms of Service")
        
        # Retrieve relevant templates
        tos_context = self.retrieve_context(
            f"terms of service {company_context.get('business_model', '')} {company_context.get('industry', '')}",
            top_k=5
        )
        
        # Web search if needed
        web_results = []
        if tos_context.get('count', 0) < 3:
            topic_context = f"{company_context.get('industry', '')} {company_context.get('business_model', '')}"
            search_result = self.mcp_client.web_search(
                query=f"terms of service template {company_context.get('business_model', '')}",
                topic_context=topic_context
            )
            web_results = []
            if search_result.get("success"):
                web_results = search_result.get("results", [])
        
        prompt = f"""Generate comprehensive Terms of Service for this company:

COMPANY DETAILS:
{json.dumps(company_context, indent=2)}

TEMPLATE GUIDANCE FROM DATABASE:
{tos_context.get('context', 'No relevant guidance found')}

WEB SEARCH RESULTS:
{self._format_web_results(web_results) if web_results else ''}

TASK: Generate complete Terms of Service including:
1. Acceptance of Terms
2. Description of Service
3. User Accounts and Registration
4. User Obligations and Acceptable Use
5. Intellectual Property Rights
6. Payment Terms (if applicable)
7. Limitation of Liability
8. Indemnification
9. Termination
10. Dispute Resolution
11. Governing Law
12. Changes to Terms
13. Contact Information

Tailor to business model: {company_context.get('business_model', '')}
Industry: {company_context.get('industry', '')}

Be legally sound and protect the company while being fair to users."""
        
        system_prompt = """You are an expert legal consultant specializing in Terms of Service agreements. 
Generate comprehensive, legally protective Terms of Service for startups.

When generating responses:
- Provide highly detailed, thorough ToS documents that cover all required sections
- Include specific legal language appropriate for the company's business model and jurisdiction
- Explain the purpose and importance of each section
- Structure documents clearly with sections, subsections, and bullet points
- If asked for more details, provide extensive analysis with legal reasoning and examples
- Be comprehensive and ensure all legal protections are included"""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_context)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        all_sources = tos_context.get('sources', [])
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
    
    def check_compliance(self, company_context: Dict, policy_type: Optional[str] = None) -> Dict:
        """
        Check compliance requirements for the company.
        
        Args:
            company_context: Company details
            policy_type: Optional specific policy type to check
            
        Returns:
            Compliance assessment with recommendations
        """
        logger.info(f"Checking compliance for: {policy_type or 'all policies'}")
        
        # Retrieve compliance guidance
        compliance_context = self.retrieve_context(
            f"compliance {company_context.get('industry', '')} {company_context.get('compliance_requirements', [])}",
            top_k=5
        )
        
        # Web search for latest requirements
        topic_context = f"{company_context.get('industry', '')} {company_context.get('target_markets', [])}"
        search_result = self.mcp_client.web_search(
            query=f"compliance requirements {company_context.get('industry', '')} {company_context.get('compliance_requirements', [])}",
            topic_context=topic_context
        )
        web_results = []
        if search_result.get("success"):
            web_results = search_result.get("results", [])
        
        prompt = f"""Assess compliance requirements for this company:

COMPANY DETAILS:
{json.dumps(company_context, indent=2)}

COMPLIANCE GUIDANCE:
{compliance_context.get('context', 'No relevant guidance found')}

WEB SEARCH RESULTS (Latest Requirements):
{self._format_web_results(web_results) if web_results else ''}

TASK: Provide comprehensive compliance assessment:
1. Required Compliance Frameworks (based on industry, data types, locations)
2. Current Compliance Status (what they likely need)
3. Critical Requirements (must-have policies/processes)
4. Recommended Policies (should-have)
5. Compliance Checklist (action items)
6. Jurisdiction-Specific Requirements (for each target_market)
7. Industry-Specific Requirements (for {company_context.get('industry', '')})
8. Data Protection Requirements (based on data_collected)
9. Timeline Recommendations (when to implement)
10. Resources and Next Steps

Focus on: {policy_type if policy_type else 'All compliance requirements'}"""
        
        system_prompt = """You are an expert compliance consultant with deep knowledge of regulatory and legal compliance requirements. 
Assess regulatory and legal compliance requirements comprehensively for startups across different industries and jurisdictions.

When generating responses:
- Provide highly detailed, thorough compliance assessments
- Include specific regulations, requirements, and deadlines
- Explain the implications of each requirement
- Provide actionable recommendations for achieving compliance
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and cover all relevant compliance requirements"""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_context)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        all_sources = compliance_context.get('sources', [])
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
    
    def generate_hr_policies(self, company_context: Dict) -> Dict:
        """
        Generate HR and employment policies.
        
        Args:
            company_context: Company details
            
        Returns:
            Generated HR policies with sources
        """
        logger.info("Generating HR policies")
        
        # Retrieve HR policy guidance
        hr_context = self.retrieve_context(
            f"employee handbook HR policies {company_context.get('industry', '')}",
            top_k=5
        )
        
        # Web search if needed
        web_results = []
        if hr_context.get('count', 0) < 3:
            search_result = self.mcp_client.web_search(
                query=f"employee handbook template startup {company_context.get('industry', '')}",
                topic_context=company_context.get('industry', '')
            )
            web_results = []
            if search_result.get("success"):
                web_results = search_result.get("results", [])
        
        prompt = f"""Generate HR and employment policies for this company:

COMPANY DETAILS:
{json.dumps(company_context, indent=2)}

HR POLICY GUIDANCE:
{hr_context.get('context', 'No relevant guidance found')}

WEB SEARCH RESULTS:
{self._format_web_results(web_results) if web_results else ''}

TASK: Generate comprehensive HR policies including:
1. Company Culture and Values
2. Employment Policies (hiring, onboarding, termination)
3. Code of Conduct
4. Remote Work Policy (if applicable)
5. Equity/Stock Options Policy
6. Time Off and Leave Policies
7. Performance Review Process
8. Confidentiality and Non-Disclosure
9. Intellectual Property Assignment
10. Anti-Harassment and Discrimination Policies
11. Health and Safety
12. Employee Benefits

Tailor to startup context and industry best practices."""
        
        system_prompt = """You are an expert HR policy consultant specializing in startup-friendly HR policies and employee handbooks. 
Generate comprehensive, startup-friendly HR policies and employee handbooks.

When generating responses:
- Provide highly detailed, thorough HR policy documents
- Include specific policies appropriate for the company's size, stage, and jurisdiction
- Explain the purpose and importance of each policy
- Structure documents clearly with sections, subsections, and bullet points
- If asked for more details, provide extensive analysis with best practices and examples
- Be comprehensive and cover all essential HR policies"""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_context)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        all_sources = hr_context.get('sources', [])
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
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a general policy-related query.
        
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
            topic_context = f"{context.get('industry', '')} {context.get('business_model', '')}" if context else query
            search_result = self.mcp_client.web_search(
                query=query,
                topic_context=topic_context
            )
            web_results = []
            if search_result.get("success"):
                web_results = search_result.get("results", [])
        
        prompt = f"""User Question: {query}

Relevant Policy/Compliance Data:
{context_data.get('context', 'No relevant context found in database')}

Web Search Results:
{self._format_web_results(web_results) if web_results else 'No additional web results'}

Provide helpful policy, compliance, and legal guidance based on the context above."""
        
        if context:
            prompt += f"\n\nCompany Context:\n{json.dumps(context, indent=2)}"
        
        system_prompt = """You are an expert legal and compliance consultant with deep knowledge of policies, regulations, compliance requirements, and legal best practices for startups. 
Answer questions comprehensively about policies, regulations, compliance requirements, and legal best practices.

When generating responses:
- Provide highly detailed, thorough answers with comprehensive explanations
- Include specific examples, case studies, and best practices
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive, in-depth analysis
- Be comprehensive and cover all relevant aspects of the question
- Provide actionable advice that startups can implement

IMPORTANT - Ask for clarification and more details:
- If the query is vague or unclear, ask specific clarifying questions
- If you need more information to provide a better answer, proactively ask for it
- Request details about: company name, industry, business model, target markets, data collected, user types, compliance requirements
- Ask follow-up questions to understand the user's specific needs and legal requirements
- Don't assume - ask for clarification when needed
- If information is missing, explicitly ask for it before proceeding"""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(context)
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
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
        for i, result in enumerate(web_results, 1):
            formatted.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', '')}\n"
                f"   Snippet: {result.get('snippet', '')[:200]}...\n"
                f"   Relevance: {result.get('relevance_score', 0):.2f}"
            )
        
        return "\n\n".join(formatted)

