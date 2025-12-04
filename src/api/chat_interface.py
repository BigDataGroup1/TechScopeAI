"""Chat interface for TechScopeAI using Streamlit."""

import streamlit as st
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional
import sys

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.pitch_agent import PitchAgent
from src.agents.competitive_agent import CompetitiveAgent
from src.agents.patent_agent import PatentAgent
from src.agents.policy_agent import PolicyAgent
from src.agents.marketing_agent import MarketingAgent
from src.agents.team_agent import TeamAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.team_agent import TeamAgent
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.data.load_company_data import load_test_company_data, format_company_data_for_pitch, load_company_data
from src.utils.exporters import PitchExporter

logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="TechScopeAI - Pitch Agent",
    page_icon="🚀",
    layout="wide"
)


@st.cache_resource
def load_coordinator_agent():
    """Load and cache CoordinatorAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        from src.rag.weaviate_store import WeaviateStore
        vector_store = WeaviateStore(category="competitive", dimension=dimension)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=True,
            collection_names=["TechScopeAI_Competitive"]
        )
        
        agent = CoordinatorAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_supervisor_agent():
    """Load and cache SupervisorAgent with all agents registered."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        from src.rag.weaviate_store import WeaviateStore
        vector_store = WeaviateStore(category="competitive", dimension=dimension)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=True,
            collection_names=["TechScopeAI_Competitive"]
        )
        
        # Create supervisor
        supervisor = SupervisorAgent(retriever)
        
        # Register all agents
        pitch_agent, _ = load_pitch_agent()
        if pitch_agent:
            supervisor.register_agent("pitch", pitch_agent)
        
        competitive_agent, _ = load_competitive_agent()
        if competitive_agent:
            supervisor.register_agent("competitive", competitive_agent)
        
        patent_agent, _ = load_patent_agent()
        if patent_agent:
            supervisor.register_agent("patent", patent_agent)
        
        policy_agent, _ = load_policy_agent()
        if policy_agent:
            supervisor.register_agent("policy", policy_agent)
        
        marketing_agent, _ = load_marketing_agent()
        if marketing_agent:
            supervisor.register_agent("marketing", marketing_agent)
        
        team_agent, _ = load_team_agent()
        if team_agent:
            supervisor.register_agent("team", team_agent)
        
        coordinator_agent, _ = load_coordinator_agent()
        if coordinator_agent:
            supervisor.register_agent("coordinator", coordinator_agent)
        
        return supervisor, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_pitch_agent():
    """Load and cache PitchAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components
        # Note: QueryAgent requires Weaviate Cloud, so for local instances we use manual RAG
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        from src.rag.weaviate_store import WeaviateStore
        vector_store = WeaviateStore(category="pitch", dimension=dimension)
        
        # Try QueryAgent first (will fallback to manual if local)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=True,  # Will auto-detect local and fallback
            collection_names=["TechScopeAI_Pitch"]
        )
        
        # Initialize agent
        agent = PitchAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_competitive_agent():
    """Load and cache CompetitiveAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components for competitive analysis
        # Note: QueryAgent requires Weaviate Cloud, so for local instances we use manual RAG
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        from src.rag.weaviate_store import WeaviateStore
        vector_store = WeaviateStore(category="competitive", dimension=dimension)
        
        # Try QueryAgent first (will fallback to manual if local)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=True,  # Will auto-detect local and fallback
            collection_names=["TechScopeAI_Competitive"]
        )
        
        # Initialize agent
        agent = CompetitiveAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_patent_agent():
    """Load and cache PatentAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components for patent/IP
        # Note: QueryAgent requires Weaviate Cloud, so for local instances we use manual RAG
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        from src.rag.weaviate_store import WeaviateStore
        vector_store = WeaviateStore(category="competitive", dimension=dimension)  # Use competitive for now, can create patent category later
        
        # Try QueryAgent first (will fallback to manual if local)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=True,  # Will auto-detect local and fallback
            collection_names=["TechScopeAI_Competitive"]  # Can create TechScopeAI_Patent later
        )
        
        # Initialize agent (has built-in web search fallback)
        agent = PatentAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_policy_agent():
    """Load and cache PolicyAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components for policy/compliance
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        from src.rag.weaviate_store import WeaviateStore
        vector_store = WeaviateStore(category="competitive", dimension=dimension)  # Use competitive for now
        
        # Try QueryAgent first (will fallback to manual if local)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=True,  # Will auto-detect local and fallback
            collection_names=["TechScopeAI_Competitive"]
        )
        
        # Initialize agent (has built-in web search fallback)
        agent = PolicyAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_marketing_agent():
    """Load and cache MarketingAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components for marketing
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        from src.rag.weaviate_store import WeaviateStore
        vector_store = WeaviateStore(category="competitive", dimension=dimension)  # Use competitive for now
        
        # Try QueryAgent first (will fallback to manual if local)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=True,  # Will auto-detect local and fallback
            collection_names=["TechScopeAI_Competitive"]
        )
        
        # Initialize agent (has built-in web search fallback and image generation)
        agent = MarketingAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_team_agent():
    """Load and cache TeamAgent."""
    try:
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        # Initialize RAG components for team/hiring
        embedder = Embedder(use_openai=False)
        dimension = embedder.get_embedding_dimension()
        from src.rag.weaviate_store import WeaviateStore
        vector_store = WeaviateStore(category="competitive", dimension=dimension)  # Use competitive for now
        
        # Try QueryAgent first (will fallback to manual if local)
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder,
            use_query_agent=True,  # Will auto-detect local and fallback
            collection_names=["TechScopeAI_Competitive"]
        )
        
        # Initialize agent (has built-in web search fallback)
        agent = TeamAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


def load_company_data_file(company_id: str) -> Optional[Dict]:
    """Load company data from file."""
    company_path = Path(f"src/data/user_companies/{company_id}.json")
    if company_path.exists():
        with open(company_path, 'r') as f:
            return json.load(f)
    return None


def save_company_data(company_id: str, data: Dict):
    """Save company data to file."""
    company_path = Path(f"src/data/user_companies/{company_id}.json")
    company_path.parent.mkdir(parents=True, exist_ok=True)
    with open(company_path, 'w') as f:
        json.dump(data, f, indent=2)


def get_patent_questionnaire():
    """Get patent questionnaire questions."""
    from src.agents.patent_agent import PatentAgent
    return PatentAgent.PATENT_QUESTIONNAIRE


def get_marketing_questionnaire():
    """Get marketing content questionnaire questions."""
    from src.agents.marketing_agent import MarketingAgent
    return MarketingAgent.MARKETING_QUESTIONNAIRE


def get_team_questionnaire():
    """Get team building questionnaire questions."""
    from src.agents.team_agent import TeamAgent
    return TeamAgent.TEAM_QUESTIONNAIRE


def get_role_specific_questionnaire():
    """Get role-specific questionnaire questions."""
    from src.agents.team_agent import TeamAgent
    return TeamAgent.ROLE_SPECIFIC_QUESTIONNAIRE


def should_show_question(question, answers):
    """Check if a question should be shown based on dependencies."""
    if "depends_on" not in question:
        return True
    
    depends = question["depends_on"]
    for key, value in depends.items():
        if key not in answers:
            return False
        answer = answers[key]
        if isinstance(value, list):
            if answer not in value:
                return False
        else:
            if answer != value:
                return False
    return True


def main():
    """Main chat interface."""
    st.title("🚀 TechScopeAI - Pitch Agent")
    st.markdown("**Your AI-powered pitch deck advisor**")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'company_data' not in st.session_state:
        st.session_state.company_data = None
    if 'company_id' not in st.session_state:
        st.session_state.company_id = None
    if 'slides' not in st.session_state:
        st.session_state.slides = None
    if 'current_slide' not in st.session_state:
        st.session_state.current_slide = 0
    if 'elevator_pitch' not in st.session_state:
        st.session_state.elevator_pitch = None
    if 'use_supervisor' not in st.session_state:
        st.session_state.use_supervisor = True  # Enable supervisor by default
    
    # Load agent
    agent, error = load_pitch_agent()
    
    if error:
        st.error(f"❌ Error loading agent: {error}")
        st.info("💡 Make sure you've:")
        st.info("1. Processed the pitch data (run: python scripts/processing/process_pitch_data.py)")
        st.info("2. Built the RAG index (run: python scripts/processing/build_rag_index.py)")
        st.info("3. Set OPENAI_API_KEY in .env file")
        return
    
    # Sidebar for company details
    with st.sidebar:
        st.header("📋 Company Details")
        
        # Supervisor toggle (for debugging)
        st.markdown("---")
        st.subheader("⚙️ Settings")
        use_supervisor_setting = st.checkbox(
            "Use Supervisor Agent (Smart Routing)", 
            value=st.session_state.get("use_supervisor", True),
            help="Enable intelligent query routing via Supervisor Agent. Disable to use direct routing."
        )
        st.session_state.use_supervisor = use_supervisor_setting
        
        # Company ID input
        company_id = st.text_input("Company ID", value=st.session_state.company_id or "default")
        st.session_state.company_id = company_id
        
        # Load test data option
        if st.button("📋 Load Test Company Data"):
            test_data = load_test_company_data()
            if test_data:
                formatted = format_company_data_for_pitch(test_data)
                st.session_state.company_data = formatted
                st.success(f"✅ Loaded test data for: {formatted.get('company_name', 'Unknown')}")
            else:
                st.error("Test company data not found!")
        
        # Load existing company data
        if st.button("📂 Load Saved Company Data"):
            data = load_company_data_file(company_id)
            if data:
                formatted = format_company_data_for_pitch(data)
                st.session_state.company_data = formatted
                st.success("✅ Company data loaded!")
            else:
                st.warning("No company data found. Fill in the form below or load test data.")
        
        # Company details form
        st.subheader("Enter Company Details")
        
        company_name = st.text_input("Company Name", value=st.session_state.company_data.get('company_name', '') if st.session_state.company_data else '')
        industry = st.text_input("Industry", value=st.session_state.company_data.get('industry', '') if st.session_state.company_data else '')
        problem = st.text_area("Problem", value=st.session_state.company_data.get('problem', '') if st.session_state.company_data else '', height=100)
        solution = st.text_area("Solution", value=st.session_state.company_data.get('solution', '') if st.session_state.company_data else '', height=100)
        market = st.text_input("Target Market", value=st.session_state.company_data.get('target_market', '') if st.session_state.company_data else '')
        stage = st.selectbox("Current Stage", ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"], 
                           index=0 if not st.session_state.company_data else 
                           ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"].index(st.session_state.company_data.get('current_stage', 'Pre-Seed')) if st.session_state.company_data.get('current_stage') in ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"] else 0)
        traction = st.text_area("Traction", value=st.session_state.company_data.get('traction', '') if st.session_state.company_data else '', height=80)
        funding_goal = st.text_input("Funding Goal", value=st.session_state.company_data.get('funding_goal', '') if st.session_state.company_data else '')
        
        if st.button("💾 Save Company Data"):
            company_data = {
                'company_name': company_name,
                'industry': industry,
                'problem': problem,
                'solution': solution,
                'target_market': market,
                'current_stage': stage,
                'traction': traction,
                'funding_goal': funding_goal
            }
            save_company_data(company_id, company_data)
            st.session_state.company_data = company_data
            st.success("✅ Company data saved!")
    
    # Main chat area
    st.header("💬 Chat with Pitch Agent")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display image if available
            if "image_path" in message and message["image_path"]:
                image_path = message["image_path"]
                if Path(image_path).exists():
                    try:
                        from PIL import Image
                        img = Image.open(image_path)
                        st.image(img, caption="Generated Marketing Image", width='stretch')
                    except Exception as e:
                        st.warning(f"Could not display image: {e}")
            
            if "sources" in message and message["sources"]:
                with st.expander("📚 Sources"):
                    for source in message["sources"][:3]:  # Show top 3 sources
                        st.text(f"• {source.get('source', 'Unknown')} (similarity: {source.get('similarity', 0):.2f})")
    
    # Chat input
    if prompt := st.chat_input("Ask about pitch decks, patents, competitors, or generate a pitch..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Use Supervisor Agent for routing (if enabled)
                    use_supervisor = st.session_state.get("use_supervisor", True)
                    
                    # Try supervisor first if enabled
                    supervisor_success = False
                    if use_supervisor:
                        # Load supervisor and coordinator
                        supervisor, supervisor_error = load_supervisor_agent()
                        coordinator, coordinator_error = load_coordinator_agent()
                        
                        if supervisor_error or coordinator_error:
                            logger.warning(f"Supervisor/Coordinator not available: {supervisor_error or coordinator_error}")
                            use_supervisor = False
                        else:
                            try:
                                # Get company ID
                                company_id = st.session_state.get("company_id", "default")
                                
                                # Store company data in coordinator
                                if st.session_state.company_data:
                                    coordinator.store_company_data(company_id, st.session_state.company_data)
                                
                                # Get context from coordinator
                                context_from_coordinator = coordinator.get_context_for_agent(
                                    company_id, 
                                    "supervisor",
                                    prompt
                                )
                                
                                # Add coordinator context to query context
                                query_context = {
                                    **(st.session_state.company_data or {}),
                                    "coordinator_context": context_from_coordinator.get("summary", ""),
                                    "company_id": company_id
                                }
                                
                                # Route and execute via supervisor
                                response = supervisor.process_query(prompt, query_context)
                                
                                # Check for errors
                                if response.get("error"):
                                    logger.warning(f"Supervisor agent error: {response.get('error')}")
                                    use_supervisor = False
                                elif not response.get("response") or response.get("response") == "No response":
                                    logger.warning("No response from supervisor agent")
                                    use_supervisor = False
                                else:
                                    # Success - store and display
                                    routed_to = response.get("routed_to", "unknown")
                                    coordinator.store_generated_content(
                                        company_id,
                                        routed_to,
                                        "response",
                                        response
                                    )
                                    
                                    # Display response
                                    st.markdown(response.get("response", "No response"))
                                    
                                    # Show routing info
                                    if response.get("routed_to"):
                                        st.caption(f"🤖 Routed to: {response['routed_to']} agent (confidence: {response.get('routing_confidence', 0):.2f})")
                                    
                                    # Show sources
                                    sources = response.get("sources", [])
                                    if sources:
                                        with st.expander("📚 Sources"):
                                            for source in sources[:5]:
                                                st.markdown(f"- {source.get('source', 'Unknown')}")
                                    
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": response.get("response", ""),
                                        "sources": sources
                                    })
                                    supervisor_success = True
                                    st.rerun()  # Exit here if supervisor succeeded
                            except Exception as e:
                                logger.error(f"Supervisor execution error: {e}", exc_info=True)
                                use_supervisor = False
                    
                    # Fallback to direct routing if supervisor didn't succeed
                    if not supervisor_success:
                        # Fallback to direct routing (original logic)
                        # Determine mode based on prompt
                        prompt_lower = prompt.lower()
                        
                        # Check if it's a team-related query
                        team_keywords = ["team", "hiring", "job", "recruit", "role", "position", "employee",
                                        "job description", "jd", "salary", "skillset", "candidate", "hire"]
                        is_team_query = any(keyword in prompt_lower for keyword in team_keywords)
                        
                        # Check if it's a marketing-related query
                        marketing_keywords = ["marketing", "instagram", "linkedin", "social media", "content", 
                                             "post", "hashtag", "campaign", "ad", "promotion", "viral",
                                             "engagement", "follower", "trend", "marketing strategy"]
                        is_marketing_query = any(keyword in prompt_lower for keyword in marketing_keywords)
                        
                        # Check if it's a patent-related query
                        patent_keywords = ["patent", "patentability", "prior art", "ip", "intellectual property", 
                                          "filing", "uspto", "patent search", "patent strategy"]
                        is_patent_query = any(keyword in prompt_lower for keyword in patent_keywords)
                        
                        # Check if it's a policy-related query
                        policy_keywords = ["policy", "privacy policy", "terms of service", "tos", "compliance", 
                                          "gdpr", "ccpa", "hipaa", "legal", "regulations", "employee handbook",
                                          "cookie policy", "data protection", "refund policy"]
                        is_policy_query = any(keyword in prompt_lower for keyword in policy_keywords)
                        
                        if is_team_query:
                            # Route to Team Agent
                            team_agent, team_error = load_team_agent()
                            if team_error:
                                st.error(f"Team Agent Error: {team_error}")
                                response = {"response": f"Error: {team_error}", "sources": []}
                            else:
                                if "job description" in prompt_lower or "jd" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    # Would need role details - suggest using questionnaire
                                    response = {"response": "Please use the '👥 Team & Hiring' button to generate a comprehensive job description with all details.", "sources": []}
                                elif "recommend" in prompt_lower or "role" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    team_context = {}  # Would need team info
                                    response = team_agent.analyze_team_needs(context, team_context)
                                else:
                                    response = team_agent.process_query(prompt, st.session_state.company_data)
                        
                        elif is_marketing_query:
                            # Route to Marketing Agent
                            marketing_agent, marketing_error = load_marketing_agent()
                            if marketing_error:
                                st.error(f"Marketing Agent Error: {marketing_error}")
                                response = {"response": f"Error: {marketing_error}", "sources": []}
                            else:
                                if "instagram" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    response = marketing_agent.generate_instagram_content(context)
                                elif "linkedin" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    response = marketing_agent.generate_linkedin_content(context)
                                elif "image" in prompt_lower or "generate image" in prompt_lower:
                                    product_desc = prompt if not st.session_state.company_data else st.session_state.company_data.get('solution', prompt)
                                    response = marketing_agent.generate_marketing_image(product_desc, "Professional")
                                elif "strategy" in prompt_lower or "strategies" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    response = marketing_agent.suggest_marketing_strategies(context)
                                else:
                                    response = marketing_agent.process_query(prompt, st.session_state.company_data)
                        
                        elif is_policy_query:
                            # Route to Policy Agent
                            policy_agent, policy_error = load_policy_agent()
                            if policy_error:
                                st.error(f"Policy Agent Error: {policy_error}")
                                response = {"response": f"Error: {policy_error}", "sources": []}
                            else:
                                if "privacy policy" in prompt_lower or "privacy" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    response = policy_agent.generate_privacy_policy(context)
                                elif "terms of service" in prompt_lower or "tos" in prompt_lower or "terms" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    response = policy_agent.generate_terms_of_service(context)
                                elif "compliance" in prompt_lower or "gdpr" in prompt_lower or "ccpa" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    response = policy_agent.check_compliance(context)
                                elif "hr" in prompt_lower or "employee" in prompt_lower or "handbook" in prompt_lower:
                                    context = st.session_state.company_data or {}
                                    response = policy_agent.generate_hr_policies(context)
                                else:
                                    response = policy_agent.process_query(prompt, st.session_state.company_data)
                        
                        elif is_patent_query:
                            # Route to Patent Agent
                            patent_agent, patent_error = load_patent_agent()
                            if patent_error:
                                st.error(f"Patent Agent Error: {patent_error}")
                                response = {"response": f"Error: {patent_error}", "sources": []}
                            else:
                                if "patentability" in prompt_lower or "assess" in prompt_lower:
                                    invention = prompt if not st.session_state.company_data else f"{st.session_state.company_data.get('solution', prompt)}"
                                    response = patent_agent.assess_patentability(invention, st.session_state.company_data)
                                elif "prior art" in prompt_lower or "search" in prompt_lower:
                                    query = prompt.replace("patent", "").replace("search", "").strip()
                                    response = patent_agent.search_patents(query, st.session_state.company_data)
                                elif "filing" in prompt_lower or "strategy" in prompt_lower:
                                    if st.session_state.company_data:
                                        response = patent_agent.filing_strategy(st.session_state.company_data)
                                    else:
                                        response = patent_agent.process_query(prompt, st.session_state.company_data)
                                else:
                                    response = patent_agent.process_query(prompt, st.session_state.company_data)
                        
                        elif "evaluate" in prompt_lower or "review" in prompt_lower or "improve" in prompt_lower:
                            # Extract pitch text (assume it's after "evaluate:" or similar)
                            pitch_text = prompt
                            if ":" in prompt:
                                pitch_text = prompt.split(":", 1)[1].strip()
                            
                            response = agent.evaluate_pitch(
                                pitch_text=pitch_text,
                                company_context=st.session_state.company_data
                            )
                        elif "outline" in prompt_lower or "generate from outline" in prompt_lower:
                            # Extract outline (simplified - in real app, use structured input)
                            outline = {
                                "sections": ["Problem", "Solution", "Market", "Traction", "Team", "Ask"],
                                "notes": prompt
                            }
                            response = agent.generate_from_outline(
                                outline=outline,
                                company_context=st.session_state.company_data
                            )
                        elif "generate" in prompt_lower and st.session_state.company_data:
                            # Generate from company details
                            response = agent.generate_from_details(st.session_state.company_data)
                        else:
                            # General query - try pitch agent first
                            response = agent.process_query(
                                query=prompt,
                                context=st.session_state.company_data
                            )
                        
                        # Check if this is an image generation response
                        if response.get('success') is not None and 'image_path' in response:
                            # Handle image generation result
                            if response.get('success'):
                                st.success("✅ Image generated successfully!")
                                
                                # Display image
                                image_path = response.get('image_path')
                                if image_path and Path(image_path).exists():
                                    try:
                                        from PIL import Image
                                        img = Image.open(image_path)
                                        st.image(img, caption="Generated Marketing Image", width='stretch')
                                        
                                        # Download button
                                        with open(image_path, 'rb') as f:
                                            st.download_button(
                                                "⬇ Download Image",
                                                f,
                                                file_name=Path(image_path).name,
                                                mime="image/png"
                                            )
                                    except Exception as e:
                                        st.error(f"Could not display image: {e}")
                                
                                # Show image URL if available
                                if response.get('image_url'):
                                    st.markdown(f"**Image URL:** {response.get('image_url')}")
                                
                                # Show prompt used
                                if response.get('prompt_used'):
                                    with st.expander("📝 Prompt Used"):
                                        st.code(response.get('prompt_used'))
                                
                                # Add to messages
                                msg_content = f"✅ Generated marketing image successfully!\n\n"
                                if response.get('image_url'):
                                    msg_content += f"Image URL: {response.get('image_url')}\n"
                                if response.get('image_path'):
                                    msg_content += f"Saved to: {response.get('image_path')}"
                                
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": msg_content,
                                    "image_path": response.get('image_path'),
                                    "image_url": response.get('image_url')
                                })
                            else:
                                # Image generation failed
                                error_msg = f"❌ Image generation failed: {response.get('error', 'Unknown error')}"
                                if response.get('message'):
                                    error_msg += f"\n{response.get('message')}"
                                st.error(error_msg)
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": error_msg
                                })
                        else:
                            # Regular text response
                            st.markdown(response.get('response', 'No response generated'))
                            
                            # Show sources
                            if response.get('sources'):
                                with st.expander("📚 Sources & Citations"):
                                    for source in response['sources'][:5]:
                                        st.text(f"• {source.get('source', 'Unknown')} (similarity: {source.get('similarity', 0):.2f})")
                            
                            # Add to messages
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response.get('response', ''),
                                "sources": response.get('sources', [])
                            })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Slides Preview Section
    if st.session_state.slides and len(st.session_state.slides.get('slides', [])) > 0:
        st.markdown("---")
        st.subheader("📊 Pitch Deck Slides")
        
        slides_list = st.session_state.slides['slides']
        total_slides = len(slides_list)
        
        # Slide navigation
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 2, 1, 2])
        with col_nav1:
            if st.button("◀ Previous", disabled=st.session_state.current_slide == 0):
                st.session_state.current_slide = max(0, st.session_state.current_slide - 1)
                st.rerun()
        with col_nav2:
            st.write(f"**Slide {st.session_state.current_slide + 1} of {total_slides}**")
        with col_nav3:
            if st.button("Next ▶", disabled=st.session_state.current_slide >= total_slides - 1):
                st.session_state.current_slide = min(total_slides - 1, st.session_state.current_slide + 1)
                st.rerun()
        with col_nav4:
            # Export buttons
            exporter = PitchExporter()
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            with col_exp1:
                if st.button("📄 Export PDF"):
                    filepath = exporter.export_to_pdf(slides_list, st.session_state.slides.get('company_name', 'Company'))
                    if filepath:
                        with open(filepath, 'rb') as f:
                            st.download_button("⬇ Download PDF", f, file_name=Path(filepath).name, mime="application/pdf")
            with col_exp2:
                if st.button("📊 Export PPTX (with images)"):
                    filepath = exporter.export_to_powerpoint(
                        slides_list, 
                        st.session_state.slides.get('company_name', 'Company'),
                        include_images=True
                    )
                    if filepath:
                        with open(filepath, 'rb') as f:
                            st.download_button("⬇ Download PPTX", f, file_name=Path(filepath).name, mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
            with col_exp3:
                if st.button("📝 Export MD"):
                    filepath = exporter.export_to_markdown(slides_list, st.session_state.slides.get('company_name', 'Company'))
                    if filepath:
                        with open(filepath, 'rb') as f:
                            st.download_button("⬇ Download MD", f, file_name=Path(filepath).name, mime="text/markdown")
        
        # Display current slide
        if 0 <= st.session_state.current_slide < total_slides:
            slide = slides_list[st.session_state.current_slide]
            st.markdown("---")
            with st.container():
                # Create two columns: content on left, image on right
                col_content, col_image = st.columns([2, 1])
                
                with col_content:
                    st.markdown(f"### 📊 Slide {slide.get('slide_number', '?')}: {slide.get('title', 'Untitled')}")
                    
                    # Main content
                    if slide.get('content'):
                        st.markdown("**Content:**")
                        st.markdown(slide.get('content', ''))
                    
                    if slide.get('key_points'):
                        st.markdown("**Key Points:**")
                        for point in slide['key_points']:
                            st.markdown(f"- {point}")
                
                with col_image:
                    # Display image if available
                    image_path = slide.get('image_path')
                    if image_path and Path(image_path).exists():
                        try:
                            from PIL import Image
                            img = Image.open(image_path)
                            st.image(img, caption=slide.get('title', 'Slide Image'), width='stretch')
                        except Exception as e:
                            st.warning(f"Could not display image: {e}")
                    else:
                        st.info("🖼️ No image available for this slide")
                
                # Speech section (in expander - not in PPT)
                if slide.get('speech'):
                    with st.expander("💬 Speech Script (Not in PPT - for reference only)"):
                        st.info(slide.get('speech', ''))
                
                # Talking points section (in expander - not in PPT)
                if slide.get('talking_points'):
                    with st.expander("🎯 Talking Points (Not in PPT - for reference only)"):
                        for point in slide.get('talking_points', []):
                            st.markdown(f"→ **{point}**")
        
        # Slide thumbnails
        st.markdown("---")
        st.subheader("📑 All Slides")
        cols = st.columns(min(5, total_slides))
        for idx, slide in enumerate(slides_list):
            col_idx = idx % 5
            with cols[col_idx]:
                if st.button(f"Slide {idx + 1}\n{slide.get('title', '')[:20]}...", key=f"slide_btn_{idx}"):
                    st.session_state.current_slide = idx
                    st.rerun()
    
    # Elevator Pitch Section (independent of slides)
    if st.session_state.get('elevator_pitch'):
        st.markdown("---")
        st.subheader("🎤 Elevator Pitch")
        
        pitch_data = st.session_state.elevator_pitch
        col_pitch1, col_pitch2 = st.columns([3, 1])
        
        with col_pitch1:
            st.markdown(f"**Duration:** {pitch_data.get('duration_seconds', 60)} seconds")
            st.markdown(f"**Words:** ~{pitch_data.get('estimated_words', 0)} words")
            
            # Display pitch in a nice box
            st.markdown("### Your Elevator Pitch:")
            st.info(pitch_data.get('elevator_pitch', ''))
            
            # Also show in code block for easy copying
            st.markdown("### Copy Text:")
            st.code(pitch_data.get('elevator_pitch', ''), language=None)
        
        with col_pitch2:
            # Copy button info
            st.markdown("### Export")
            pitch_text = pitch_data.get('elevator_pitch', '')
            st.download_button(
                "💾 Download as TXT",
                pitch_text,
                file_name=f"{pitch_data.get('company_name', 'Company')}_ElevatorPitch.txt",
                mime="text/plain"
            )
            st.caption("💡 Tip: Click the code block above and copy to clipboard")
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Generate Pitch"):
            if st.session_state.company_data:
                with st.spinner("Generating pitch..."):
                    response = agent.generate_from_details(st.session_state.company_data)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response['response'],
                        "sources": response.get('sources', [])
                    })
                    st.rerun()
            else:
                st.warning("Please enter company details first!")
    
    with col2:
        if st.button("🎯 Generate Slides"):
            if st.session_state.company_data:
                with st.spinner("Generating slides and creating professional PowerPoint..."):
                    slides_data = agent.generate_slides(st.session_state.company_data)
                    st.session_state.slides = slides_data
                    st.session_state.current_slide = 0
                    
                    success_msg = f"✅ Generated {slides_data.get('total_slides', 0)} slides!"
                    if slides_data.get('pptx_path'):
                        success_msg += f"\n📊 Professional PowerPoint created!"
                        st.success(success_msg)
                        # Auto-download option
                        pptx_path = Path(slides_data['pptx_path'])
                        if pptx_path.exists():
                            with open(pptx_path, 'rb') as f:
                                st.download_button(
                                    "⬇ Download PowerPoint",
                                    f,
                                    file_name=pptx_path.name,
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                                )
                    else:
                        st.success(success_msg)
                    st.rerun()
            else:
                st.warning("Please enter company details first!")
    
    with col3:
        if st.button("🎤 Generate Elevator Pitch"):
            if st.session_state.company_data:
                with st.spinner("Crafting your elevator pitch..."):
                    try:
                        # Generate 60-second elevator pitch
                        pitch_result = agent.generate_elevator_pitch(
                            st.session_state.company_data,
                            duration_seconds=60
                        )
                        if pitch_result and pitch_result.get('elevator_pitch'):
                            st.session_state.elevator_pitch = pitch_result
                            st.success("✅ Elevator pitch generated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to generate elevator pitch. Please try again.")
                            logger.error(f"Elevator pitch generation returned empty result: {pitch_result}")
                    except Exception as e:
                        error_msg = f"Error generating elevator pitch: {str(e)}"
                        st.error(error_msg)
                        logger.error(f"Elevator pitch generation error: {e}", exc_info=True)
            else:
                st.warning("Please enter company details first!")
    
    with col4:
        if st.button("📊 Evaluate Pitch"):
            st.info("Paste your pitch in chat: 'evaluate: [your pitch]'")
    
    # Competitive Agent button
    col_comp = st.columns(1)[0]
    with col_comp:
        if st.button("🔍 Competitive Analysis"):
            if "competitive_questionnaire_active" not in st.session_state:
                st.session_state.competitive_questionnaire_active = False
            if "competitive_answers" not in st.session_state:
                st.session_state.competitive_answers = {}
            if "competitive_question_index" not in st.session_state:
                st.session_state.competitive_question_index = 0
            
            st.session_state.competitive_questionnaire_active = True
            st.session_state.competitive_question_index = 0
            st.session_state.competitive_answers = {}
            st.rerun()
    
    # Team, Marketing, Policy & Patent Agent buttons
    col_team, col_mkt, col_pol, col_pat = st.columns(4)
    
    with col_team:
        if st.button("👥 Team & Hiring"):
            if "team_questionnaire_active" not in st.session_state:
                st.session_state.team_questionnaire_active = False
            if "team_answers" not in st.session_state:
                st.session_state.team_answers = {}
            if "team_question_index" not in st.session_state:
                st.session_state.team_question_index = 0
            if "team_phase" not in st.session_state:
                st.session_state.team_phase = "analysis"  # "analysis" or "jd_generation"
            if "selected_role" not in st.session_state:
                st.session_state.selected_role = None
            
            st.session_state.team_questionnaire_active = True
            st.session_state.team_question_index = 0
            st.session_state.team_answers = {}
            st.session_state.team_phase = "analysis"
            st.session_state.selected_role = None
            st.rerun()
    
    with col_mkt:
        if st.button("📱 Marketing Content"):
            if "marketing_questionnaire_active" not in st.session_state:
                st.session_state.marketing_questionnaire_active = False
            if "marketing_answers" not in st.session_state:
                st.session_state.marketing_answers = {}
            if "marketing_question_index" not in st.session_state:
                st.session_state.marketing_question_index = 0
            
            st.session_state.marketing_questionnaire_active = True
            st.session_state.marketing_question_index = 0
            st.session_state.marketing_answers = {}
            st.rerun()
    
    with col_pol:
        if st.button("📋 Policy & Compliance"):
            if "policy_questionnaire_active" not in st.session_state:
                st.session_state.policy_questionnaire_active = False
            if "policy_answers" not in st.session_state:
                st.session_state.policy_answers = {}
            if "policy_question_index" not in st.session_state:
                st.session_state.policy_question_index = 0
            
            st.session_state.policy_questionnaire_active = True
            st.session_state.policy_question_index = 0
            st.session_state.policy_answers = {}
            st.rerun()
    
    with col_pat:
        if st.button("🔬 Patent Analysis"):
            if "patent_questionnaire_active" not in st.session_state:
                st.session_state.patent_questionnaire_active = False
            if "patent_answers" not in st.session_state:
                st.session_state.patent_answers = {}
            if "patent_question_index" not in st.session_state:
                st.session_state.patent_question_index = 0
            
            st.session_state.patent_questionnaire_active = True
            st.session_state.patent_question_index = 0
            st.session_state.patent_answers = {}
            st.rerun()
    
    # Patent Questionnaire Flow
    if "patent_questionnaire_active" not in st.session_state:
        st.session_state.patent_questionnaire_active = False
    if "patent_answers" not in st.session_state:
        st.session_state.patent_answers = {}
    if "patent_question_index" not in st.session_state:
        st.session_state.patent_question_index = 0
    
    if st.session_state.patent_questionnaire_active:
        st.markdown("---")
        st.subheader("🔬 Patent Analysis Questionnaire")
        
        questionnaire = get_patent_questionnaire()
        
        # Filter questions based on dependencies
        visible_questions = [q for q in questionnaire if should_show_question(q, st.session_state.patent_answers)]
        
        if st.session_state.patent_question_index < len(visible_questions):
            current_question = visible_questions[st.session_state.patent_question_index]
            
            st.progress((st.session_state.patent_question_index + 1) / len(visible_questions))
            st.caption(f"Question {st.session_state.patent_question_index + 1} of {len(visible_questions)}")
            
            st.markdown(f"### {current_question['question']}")
            
            answer_key = f"patent_q_{current_question['id']}"
            answer = None
            
            # Render input based on type
            if current_question['type'] == 'textarea':
                answer = st.text_area(
                    "Your answer:",
                    value=st.session_state.patent_answers.get(current_question['id'], ''),
                    height=150,
                    key=answer_key,
                    placeholder=current_question.get('placeholder', '')
                )
            elif current_question['type'] == 'text':
                answer = st.text_input(
                    "Your answer:",
                    value=st.session_state.patent_answers.get(current_question['id'], ''),
                    key=answer_key,
                    placeholder=current_question.get('placeholder', '')
                )
            elif current_question['type'] == 'select':
                current_value = st.session_state.patent_answers.get(current_question['id'])
                default_index = 0
                if current_value and current_value in current_question['options']:
                    default_index = current_question['options'].index(current_value)
                
                answer = st.selectbox(
                    "Select an option:",
                    options=current_question['options'],
                    index=default_index,
                    key=answer_key
                )
            elif current_question['type'] == 'multiselect':
                answer = st.multiselect(
                    "Select all that apply:",
                    options=current_question['options'],
                    default=st.session_state.patent_answers.get(current_question['id'], []),
                    key=answer_key
                )
            
            # Store answer
            if answer:
                if current_question['type'] == 'multiselect':
                    st.session_state.patent_answers[current_question['id']] = answer
                else:
                    st.session_state.patent_answers[current_question['id']] = answer
            
            # Navigation buttons
            col_prev, col_next, col_cancel = st.columns([1, 3, 1])
            
            with col_prev:
                if st.button("◀ Previous", disabled=st.session_state.patent_question_index == 0, key=f"prev_{answer_key}"):
                    st.session_state.patent_question_index -= 1
                    st.rerun()
            
            with col_next:
                is_disabled = False
                if current_question.get('required'):
                    if current_question['type'] == 'multiselect':
                        is_disabled = not answer or len(answer) == 0
                    else:
                        is_disabled = not answer or (isinstance(answer, str) and len(answer.strip()) == 0)
                
                if st.button("Next ▶", disabled=is_disabled, key=f"next_{answer_key}"):
                    if is_disabled:
                        st.warning("Please answer this question to continue.")
                    else:
                        st.session_state.patent_question_index += 1
                        st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancel", key=f"cancel_{answer_key}"):
                    st.session_state.patent_questionnaire_active = False
                    st.session_state.patent_answers = {}
                    st.session_state.patent_question_index = 0
                    st.rerun()
        
        else:
            # All questions answered - show summary and analyze
            st.success("✅ All questions answered!")
            
            st.subheader("📋 Your Answers Summary")
            for q in visible_questions:
                if q['id'] in st.session_state.patent_answers:
                    st.markdown(f"**{q['question']}**")
                    answer = st.session_state.patent_answers[q['id']]
                    if isinstance(answer, list):
                        st.markdown(f"  → {', '.join(answer)}")
                    else:
                        st.markdown(f"  → {answer}")
                    st.markdown("---")
            
            col_analyze, col_restart = st.columns([3, 1])
            
            with col_analyze:
                if st.button("🔬 Analyze Patent", type="primary"):
                    patent_agent, patent_error = load_patent_agent()
                    if patent_error:
                        st.error(f"Error: {patent_error}")
                    else:
                        with st.spinner("Analyzing your invention and generating comprehensive patent analysis..."):
                            # Prepare context from answers
                            invention_context = {
                                'invention_description': st.session_state.patent_answers.get('invention_description', ''),
                                'industry': st.session_state.patent_answers.get('industry', ''),
                                'novelty': st.session_state.patent_answers.get('novelty', ''),
                                'development_stage': st.session_state.patent_answers.get('development_stage', ''),
                                'prior_art_awareness': st.session_state.patent_answers.get('prior_art_awareness', ''),
                                'prior_art_details': st.session_state.patent_answers.get('prior_art_details', ''),
                                'public_disclosure': st.session_state.patent_answers.get('public_disclosure', ''),
                                'disclosure_date': st.session_state.patent_answers.get('disclosure_date', ''),
                                'filing_priority': st.session_state.patent_answers.get('filing_priority', ''),
                                'geographic_interest': st.session_state.patent_answers.get('geographic_interest', []),
                                'budget_range': st.session_state.patent_answers.get('budget_range', '')
                            }
                            
                            # Perform comprehensive analysis
                            invention_desc = f"{invention_context['invention_description']} - {invention_context['novelty']}"
                            
                            # 1. Assess patentability
                            patentability_response = patent_agent.assess_patentability(
                                invention_desc, 
                                invention_context
                            )
                            
                            # 2. Search patents
                            search_query = f"{invention_context['invention_description']} {invention_context['industry']}"
                            search_response = patent_agent.search_patents(
                                search_query,
                                invention_context
                            )
                            
                            # 3. Filing strategy
                            filing_response = patent_agent.filing_strategy(invention_context)
                            
                            # Combine all analyses
                            combined_response = f"""# 🔬 Comprehensive Patent Analysis

## 📋 Patentability Assessment
{patentability_response['response']}

---

## 🔍 Patent Search Results
{search_response['response']}

---

## 📄 Filing Strategy
{filing_response['response']}
"""
                            
                            # Combine sources
                            all_sources = (
                                patentability_response.get('sources', []) +
                                search_response.get('sources', []) +
                                filing_response.get('sources', [])
                            )
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": combined_response,
                                "sources": all_sources
                            })
                            
                            # Reset questionnaire
                            st.session_state.patent_questionnaire_active = False
                            st.session_state.patent_answers = {}
                            st.session_state.patent_question_index = 0
                            st.rerun()
            
            with col_restart:
                if st.button("🔄 Restart"):
                    st.session_state.patent_questionnaire_active = False
                    st.session_state.patent_answers = {}
                    st.session_state.patent_question_index = 0
                    st.rerun()
    
    # Additional actions
    col5, col6 = st.columns(2)
    with col5:
        if st.button("💡 Pitch Tips"):
            response = agent.process_query("What are common pitch deck mistakes and best practices?")
            st.session_state.messages.append({
                "role": "assistant",
                "content": response['response'],
                "sources": response.get('sources', [])
            })
            st.rerun()
    
    with col6:
        if st.button("📈 Enhanced Scoring"):
            if st.session_state.messages:
                # Get last pitch from messages
                last_pitch = None
                for msg in reversed(st.session_state.messages):
                    if msg.get("role") == "assistant" and len(msg.get("content", "")) > 100:
                        last_pitch = msg.get("content", "")
                        break
                
                if last_pitch:
                    with st.spinner("Scoring pitch..."):
                        response = agent.evaluate_pitch_with_scores(
                            last_pitch,
                            st.session_state.company_data
                        )
                        eval_data = response.get('evaluation', {})
                        
                        # Display scores
                        st.subheader("📊 Pitch Scores")
                        overall = eval_data.get('overall_score', 0)
                        st.metric("Overall Score", f"{overall}/10")
                        
                        section_scores = eval_data.get('section_scores', {})
                        for section, score_data in section_scores.items():
                            if isinstance(score_data, dict):
                                score = score_data.get('score', 0)
                                st.progress(score / 10)
                                st.caption(f"{section.title()}: {score}/10 - {score_data.get('feedback', '')}")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"## Enhanced Scoring\n\n{json.dumps(eval_data, indent=2)}",
                            "sources": response.get('sources', [])
                        })
                        st.rerun()
                else:
                    st.info("Generate a pitch first to score it!")


if __name__ == "__main__":
    main()

