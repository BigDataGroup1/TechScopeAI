"""
Test Data for All Agent Endpoints
Use this file to test all agent functionalities with fake data
"""

# ============================================================================
# PITCH AGENT TEST DATA
# ============================================================================

PITCH_COMPANY_DATA = {
    "company_name": "AIFlow Solutions Inc.",
    "industry": "AI/ML SaaS",
    "problem": "Small businesses struggle to automate their workflows efficiently. Manual processes waste 40% of employee time, leading to decreased productivity and increased operational costs.",
    "solution": "AIFlow is an AI-powered workflow automation platform that uses natural language processing to understand business processes and automatically create custom automation workflows. Our platform integrates with 200+ business tools and requires no coding knowledge.",
    "target_market": "Small to medium businesses (10-500 employees) in professional services, retail, and healthcare",
    "current_stage": "Seed",
    "company_stage": "Operating with customers",
    "traction": "• 150 paying customers\n• $45K MRR (Monthly Recurring Revenue)\n• 25% month-over-month growth\n• 4.8/5 average customer satisfaction\n• Partnerships with 3 major CRM platforms",
    "funding_goal": "$2M Seed Round",
    "team": "• CEO: Sarah Chen (ex-Google, 10 years product experience)\n• CTO: Michael Rodriguez (ex-AWS, built 3 successful SaaS products)\n• CMO: Emily Watson (scaled 2 startups from 0 to $10M ARR)",
    "competitive_advantage": "• Only AI-powered workflow automation that requires zero coding\n• 3x faster implementation than competitors\n• Proprietary NLP engine trained on 1M+ workflows\n• Self-learning system that improves over time",
    "annual_revenue": "$540K ARR",
    "customer_count": "150 customers",
    "growth_rate": "25% MoM",
    "market_size": "$15B workflow automation market",
    "business_model": "SaaS subscription: $99-$499/month per company",
    "use_of_funds": "• 40% Product development (AI engine improvements)\n• 30% Sales and marketing (customer acquisition)\n• 20% Team expansion (hiring 5 engineers)\n• 10% Operations and infrastructure"
}

PITCH_OUTLINE = {
    "title": "AIFlow Solutions - Seed Round Pitch",
    "slides": [
        {"title": "Problem", "content": "Small businesses waste 40% of time on manual processes"},
        {"title": "Solution", "content": "AI-powered workflow automation platform"},
        {"title": "Market", "content": "$15B market opportunity"},
        {"title": "Traction", "content": "150 customers, $45K MRR, 25% MoM growth"},
        {"title": "Team", "content": "Experienced founders from Google, AWS"},
        {"title": "Ask", "content": "$2M Seed Round"}
    ]
}

PITCH_TEXT_FOR_EVALUATION = """
AIFlow Solutions is revolutionizing workflow automation for small businesses. 
We solve the critical problem of manual process inefficiency that costs businesses 
40% of their productive time. Our AI-powered platform enables businesses to automate 
workflows using natural language - no coding required.

With 150 paying customers and $45K MRR, we're experiencing 25% month-over-month growth. 
We're seeking $2M in seed funding to accelerate product development, expand our sales 
team, and capture our share of the $15B workflow automation market.

Our team brings deep expertise from Google, AWS, and successful SaaS startups. 
We have proprietary NLP technology and partnerships with major CRM platforms.
"""

# ============================================================================
# MARKETING AGENT TEST DATA
# ============================================================================

MARKETING_CONTEXT = {
    "company_name": "AIFlow Solutions",
    "product_description": "AI-powered workflow automation platform that helps small businesses automate their processes using natural language. No coding required. Integrates with 200+ business tools.",
    "target_audience": "Small to medium business owners (10-500 employees), operations managers, and business process consultants in professional services, retail, and healthcare industries",
    "platform": "Both",  # Instagram, LinkedIn, or Both
    "content_style": "Professional",
    "content_type": ["Single Post", "Carousel Post (multiple slides)"],
    "campaign_goal": "Lead generation",
    "generate_image": "Yes, generate custom AI images",
    "image_style_description": "Modern tech workspace with AI visualization, clean and professional, blue and white color scheme",
    "trend_check": "Yes, include latest trends",
    "hashtag_preference": "Industry-specific + trending",
    "call_to_action": "Sign up for free trial",
    "key_benefits": [
        "Save 40% of employee time",
        "No coding required",
        "200+ integrations",
        "25% month-over-month growth"
    ],
    "industry": "SaaS",
    "company_stage": "Seed stage startup"
}

# ============================================================================
# PATENT AGENT TEST DATA
# ============================================================================

PATENT_INVENTION_CONTEXT = {
    "invention_description": "A natural language processing system that automatically generates workflow automation scripts by analyzing business process descriptions. The system uses a proprietary neural network architecture trained on over 1 million workflow patterns to understand user intent and create executable automation workflows without requiring any programming knowledge.",
    "industry": "AI/ML Software",
    "novelty": "Unlike existing workflow automation tools that require users to manually configure workflows using visual builders or code, our invention uses advanced NLP to understand natural language descriptions and automatically generate optimized workflows. Our proprietary neural network architecture specifically trained on workflow patterns enables understanding of complex business logic and multi-step processes.",
    "prior_art_awareness": "Yes, I know of some",
    "prior_art_details": "Zapier (visual workflow builder), Microsoft Power Automate (low-code platform), IFTTT (simple automation). None use NLP to automatically generate workflows from natural language.",
    "development_stage": "Working Product",
    "public_disclosure": "Product already on market",
    "disclosure_date": "2024-01-15",
    "filing_priority": "Moderate (1-3 months)",
    "geographic_interest": ["United States (USPTO)", "Europe (EPO)"],
    "budget_range": "$15,000 - $50,000"
}

PATENT_SEARCH_QUERY = "natural language workflow automation AI"

# ============================================================================
# TEAM AGENT TEST DATA
# ============================================================================

TEAM_COMPANY_CONTEXT = {
    "company_name": "AIFlow Solutions",
    "industry": "AI/ML SaaS",
    "company_stage": "Seed",
    "current_team_size": "6-10 people",
    "existing_roles": ["CEO/Founder", "CTO/Technical Lead", "CMO/Marketing Lead", "Engineers/Developers"],
    "team_gaps": ["Product Management", "Sales/Business Development", "Customer Success/Support"],
    "hiring_priority": "High priority - Next 1-3 months",
    "budget_range": "$100K - $150K",
    "work_location": "Remote",
    "solution": "AI-powered workflow automation platform",
    "target_market": "Small to medium businesses",
    "annual_revenue": "$540K ARR",
    "customer_count": "150 customers"
}

TEAM_ROLE_CONTEXT = {
    "role_title": "Senior Product Manager",
    "experience_level": "Senior (5-10 years)",
    "must_have_skills": "Product management, SaaS experience, AI/ML product experience, 5+ years PM experience, B2B SaaS background",
    "nice_to_have_skills": "Workflow automation knowledge, startup experience, technical background",
    "employment_type": "Full-time",
    "equity_offering": "Yes, equity included",
    "start_date": "Within 1 month",
    "location": "Remote",
    "reporting_to": "CEO",
    "team_size": "Will manage 2-3 engineers initially"
}

# ============================================================================
# POLICY AGENT TEST DATA
# ============================================================================

POLICY_COMPANY_CONTEXT = {
    "company_name": "AIFlow Solutions Inc.",
    "industry": "Technology/SaaS",
    "business_model": "SaaS Subscription",
    "target_markets": ["United States", "European Union (EU)", "Canada"],
    "data_collected": [
        "Personal information (name, email, phone)",
        "Payment/financial information",
        "Location data",
        "User-generated content",
        "Cookies/tracking data"
    ],
    "user_types": "Businesses only",
    "third_party_services": "Yes, multiple services (analytics, payment, cloud, etc.)",
    "third_party_details": "Stripe (payments), Google Analytics (analytics), AWS (cloud hosting), Intercom (customer support)",
    "refund_policy": "30-day money-back guarantee",
    "age_restriction": "18+",
    "data_retention": "As long as account is active, then 90 days after deletion",
    "contact_email": "privacy@aiflow.com",
    "website_url": "https://www.aiflow.com",
    "company_address": "123 Tech Street, San Francisco, CA 94105, USA"
}

# ============================================================================
# COMPETITIVE AGENT TEST DATA
# ============================================================================

COMPETITIVE_COMPANY_CONTEXT = {
    "company_name": "AIFlow Solutions",
    "industry": "AI/ML SaaS - Workflow Automation",
    "solution": "AI-powered workflow automation platform using natural language processing. No coding required. Integrates with 200+ business tools.",
    "target_market": "Small to medium businesses (10-500 employees) in professional services, retail, and healthcare",
    "known_competitors": "Yes, I know them",
    "competitor_names": "Zapier\nMicrosoft Power Automate\nIFTTT\nMake (formerly Integromat)",
    "differentiation": "• Only platform using NLP to auto-generate workflows from natural language\n• No coding or visual builder required\n• Proprietary AI trained on 1M+ workflows\n• 3x faster implementation than competitors",
    "market_position": "New entrant",
    "competitive_concerns": ["Price competition", "Large incumbents", "Customer acquisition"],
    "current_stage": "Seed",
    "traction": "150 customers, $45K MRR, 25% MoM growth",
    "pricing": "$99-$499/month per company",
    "key_features": [
        "Natural language workflow creation",
        "200+ integrations",
        "AI-powered optimization",
        "Self-learning system"
    ]
}

COMPETITOR_COMPARISON = {
    "competitor_name": "Zapier",
    "company_details": COMPETITIVE_COMPANY_CONTEXT
}

# ============================================================================
# TEST QUERIES FOR PROCESS_QUERY ENDPOINTS
# ============================================================================

TEST_QUERIES = {
    "pitch": [
        "What are common pitch deck mistakes?",
        "How should I structure my pitch deck for seed funding?",
        "What metrics do investors care about most?",
        "How long should my pitch deck be?",
        "What's the best way to present traction?"
    ],
    "marketing": [
        "What are the best marketing strategies for SaaS startups?",
        "How do I create engaging Instagram content for B2B?",
        "What LinkedIn content performs best for lead generation?",
        "What are current marketing trends in 2024?",
        "How do I create viral social media content?"
    ],
    "patent": [
        "What makes an invention patentable?",
        "How do I search for prior art?",
        "What's the difference between provisional and utility patents?",
        "How long does patent filing take?",
        "What are the costs of filing a patent?"
    ],
    "team": [
        "What roles should I hire first for a SaaS startup?",
        "How do I write a good job description?",
        "What's the market salary for a product manager?",
        "Should I hire remote or on-site employees?",
        "How do I structure equity compensation?"
    ],
    "policy": [
        "What should be included in a privacy policy?",
        "Do I need GDPR compliance?",
        "What's the difference between privacy policy and terms of service?",
        "How do I make my policies compliant?",
        "What data protection laws apply to my business?"
    ],
    "competitive": [
        "How do I analyze my competitors?",
        "What's the best way to differentiate from competitors?",
        "How do I create a competitive matrix?",
        "What are common competitive analysis frameworks?",
        "How do I identify my competitive advantages?"
    ]
}

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
USAGE EXAMPLES:

# PITCH AGENT
from src.agents.pitch_agent import PitchAgent
from src.rag.retriever import Retriever
from test_agent_endpoints import PITCH_COMPANY_DATA, PITCH_OUTLINE, PITCH_TEXT_FOR_EVALUATION

agent = PitchAgent(retriever)

# Test all endpoints:
agent.generate_from_details(PITCH_COMPANY_DATA)
agent.generate_from_outline(PITCH_OUTLINE, PITCH_COMPANY_DATA)
agent.generate_slides(PITCH_COMPANY_DATA)
agent.generate_slides(PITCH_COMPANY_DATA, gamma_only=True)
agent.generate_elevator_pitch(PITCH_COMPANY_DATA, duration_seconds=60)
agent.evaluate_pitch(PITCH_TEXT_FOR_EVALUATION, PITCH_COMPANY_DATA)
agent.evaluate_pitch_with_scores(PITCH_TEXT_FOR_EVALUATION, PITCH_COMPANY_DATA)
agent.process_query("What are common pitch deck mistakes?", PITCH_COMPANY_DATA)

# MARKETING AGENT
from src.agents.marketing_agent import MarketingAgent
from test_agent_endpoints import MARKETING_CONTEXT

agent = MarketingAgent(retriever)

agent.generate_instagram_content(MARKETING_CONTEXT)
agent.generate_linkedin_content(MARKETING_CONTEXT)
agent.generate_marketing_image("AI-powered workflow automation platform", "Professional")
agent.suggest_marketing_strategies(MARKETING_CONTEXT)
agent.process_query("What are best marketing strategies for SaaS?", MARKETING_CONTEXT)

# PATENT AGENT
from src.agents.patent_agent import PatentAgent
from test_agent_endpoints import PATENT_INVENTION_CONTEXT, PATENT_SEARCH_QUERY

agent = PatentAgent(retriever)

agent.search_patents(PATENT_SEARCH_QUERY, PATENT_INVENTION_CONTEXT)
agent.assess_patentability(PATENT_INVENTION_CONTEXT["invention_description"], PATENT_INVENTION_CONTEXT)
agent.filing_strategy(PATENT_INVENTION_CONTEXT)
agent.prior_art_search(PATENT_INVENTION_CONTEXT["invention_description"], PATENT_INVENTION_CONTEXT)
agent.process_query("What makes an invention patentable?", PATENT_INVENTION_CONTEXT)

# TEAM AGENT
from src.agents.team_agent import TeamAgent
from test_agent_endpoints import TEAM_COMPANY_CONTEXT, TEAM_ROLE_CONTEXT

agent = TeamAgent(retriever)

agent.analyze_team_needs(TEAM_COMPANY_CONTEXT, {})
agent.get_role_market_data("Senior Product Manager", "San Francisco, CA", "SaaS")
agent.generate_job_description("Senior Product Manager", TEAM_COMPANY_CONTEXT, TEAM_ROLE_CONTEXT)
agent.process_query("What roles should I hire first?", TEAM_COMPANY_CONTEXT)

# POLICY AGENT
from src.agents.policy_agent import PolicyAgent
from test_agent_endpoints import POLICY_COMPANY_CONTEXT

agent = PolicyAgent(retriever)

agent.generate_privacy_policy(POLICY_COMPANY_CONTEXT)
agent.generate_terms_of_service(POLICY_COMPANY_CONTEXT)
agent.check_compliance(POLICY_COMPANY_CONTEXT, "privacy")
agent.generate_hr_policies(POLICY_COMPANY_CONTEXT)
agent.process_query("What should be in a privacy policy?", POLICY_COMPANY_CONTEXT)

# COMPETITIVE AGENT
from src.agents.competitive_agent import CompetitiveAgent
from test_agent_endpoints import COMPETITIVE_COMPANY_CONTEXT, COMPETITOR_COMPARISON

agent = CompetitiveAgent(retriever)

agent.analyze_competitors(COMPETITIVE_COMPANY_CONTEXT)
agent.compare_to_competitors(COMPETITIVE_COMPANY_CONTEXT, "Zapier")
agent.identify_competitive_advantages(COMPETITIVE_COMPANY_CONTEXT)
agent.process_query("How do I analyze competitors?", COMPETITIVE_COMPANY_CONTEXT)
"""


