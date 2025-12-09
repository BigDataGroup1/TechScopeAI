"""Chat interface for TechScopeAI using Streamlit."""

import streamlit as st
import streamlit.components.v1 as components
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
        
        # Initialize RAG components (PostgreSQL for RAG, Weaviate agents separate)
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        # VectorStore defaults to Cloud SQL (use use_local=True for local PostgreSQL)
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder
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
        
        # Initialize RAG components (PostgreSQL for RAG, Weaviate agents separate)
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        # VectorStore defaults to Cloud SQL (use use_local=True for local PostgreSQL)
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder
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
        
        # Initialize RAG components (PostgreSQL for RAG, Weaviate agents separate)
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        # VectorStore defaults to Cloud SQL (use use_local=True for local PostgreSQL)
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder
        )
        
        # Initialize agent (will use provider from company_data when generating)
        agent = PitchAgent(retriever, ai_provider="auto")  # Default to auto, will use provider from company_data
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
        
        # Initialize RAG components (PostgreSQL for RAG, Weaviate agents separate)
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        # VectorStore defaults to Cloud SQL (use use_local=True for local PostgreSQL)
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder
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
        
        # Initialize RAG components (PostgreSQL for RAG, Weaviate agents separate)
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        # VectorStore defaults to Cloud SQL (use use_local=True for local PostgreSQL)
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder
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
        
        # Initialize RAG components (PostgreSQL for RAG, Weaviate agents separate)
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        # VectorStore defaults to Cloud SQL (use use_local=True for local PostgreSQL)
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder
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
        
        # Initialize RAG components (PostgreSQL for RAG, Weaviate agents separate)
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        # VectorStore defaults to Cloud SQL (use use_local=True for local PostgreSQL)
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder
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
        
        # Initialize RAG components (PostgreSQL for RAG, Weaviate agents separate)
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        # VectorStore defaults to Cloud SQL (use use_local=True for local PostgreSQL)
        vector_store = VectorStore(embedding_model=embedding_model)
        
        retriever = Retriever(
            vector_store=vector_store,
            embedder=embedder
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
        
        # Database Connection Status
        st.markdown("---")
        st.subheader("🔌 Database Status")
        try:
            from src.rag.db_config import get_database_url
            from src.rag.vector_store import VectorStore
            from src.rag.embeddings import EmbeddingModel
            import os
            
            # Check if Cloud SQL password is set (indicates Cloud SQL is default)
            cloud_password = os.getenv("CLOUD_SQL_PASSWORD")
            cloud_host = os.getenv("CLOUD_SQL_HOST", "localhost")
            cloud_port = os.getenv("CLOUD_SQL_PORT", "5433")
            
            # Get database URL to check connection type
            db_url = get_database_url()
            
            # Detect connection type
            is_cloud = (
                cloud_password is not None or  # Cloud SQL password set
                ":5433" in db_url or  # Cloud SQL proxy port
                "/cloudsql/" in db_url or  # Cloud SQL socket path
                "cloudsql" in db_url.lower()
            )
            is_local = ":5432" in db_url and not is_cloud
            
            if is_cloud:
                st.success("✅ **Cloud SQL** (GCP)")
                conn_info = db_url.split('@')[-1] if '@' in db_url else f"{cloud_host}:{cloud_port}"
                st.caption(f"📍 {conn_info}")
                
                # Test connection and show collection counts
                try:
                    embedding_model = EmbeddingModel()
                    test_vs = VectorStore(embedding_model=embedding_model)
                    conn = test_vs._get_connection()
                    test_vs._put_connection(conn)
                    
                    # Get collection counts
                    collections = ['competitors_corpus', 'marketing_corpus', 'ip_policy_corpus', 
                                 'policy_corpus', 'job_roles_corpus', 'pitch_examples_corpus']
                    total_docs = 0
                    collection_counts = {}
                    for coll in collections:
                        try:
                            count = test_vs.get_collection_count(coll)
                            total_docs += count
                            if count > 0:
                                collection_counts[coll.replace('_corpus', '')] = count
                        except:
                            pass
                    
                    if total_docs > 0:
                        st.caption(f"📊 **{total_docs:,}** documents indexed")
                        if collection_counts:
                            coll_list = ", ".join([f"{k}: {v:,}" for k, v in list(collection_counts.items())[:3]])
                            st.caption(f"   ({coll_list})")
                    else:
                        st.caption("⚠️ No documents indexed yet")
                    st.caption("✅ Connection active")
                except Exception as e:
                    st.warning(f"⚠️ Connection test failed")
                    st.caption(f"   {str(e)[:60]}...")
            elif is_local:
                st.warning("⚠️ **Local PostgreSQL**")
                conn_info = db_url.split('@')[-1] if '@' in db_url else "localhost:5432"
                st.caption(f"📍 {conn_info}")
                st.caption("💡 Set CLOUD_SQL_PASSWORD in .env to use Cloud SQL")
            else:
                st.info(f"🔗 **Custom Connection**")
                conn_info = db_url.split('@')[-1] if '@' in db_url else "Custom"
                st.caption(f"📍 {conn_info}")
        except Exception as e:
            st.error(f"❌ Status check failed")
            st.caption(f"   {str(e)[:60]}...")
        
        # Supervisor toggle (for debugging)
        st.markdown("---")
        st.subheader("⚙️ Settings")
        use_supervisor_setting = st.checkbox(
            "Use Supervisor Agent (Smart Routing)", 
            value=st.session_state.get("use_supervisor", True),
            help="Enable intelligent query routing via Supervisor Agent. Disable to use direct routing."
        )
        st.session_state.use_supervisor = use_supervisor_setting
        
        # Gamma and Canva removed - not working
        
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
                        caption = "Generated Instagram Image - Ready to Post!" if message.get('image_generated') else "Generated Marketing Image"
                        st.image(img, caption=caption, width='stretch')
                    except Exception as e:
                        st.warning(f"Could not display image: {e}")
            
            if "sources" in message and message["sources"]:
                # Determine if sources include web search results
                has_web_search = any(source.get('is_web_search', False) for source in message["sources"])
                source_label = "📚 Sources" + (" (Cloud SQL + Web Search)" if has_web_search else " (from Cloud SQL)")
                
                with st.expander(source_label):
                    for i, source in enumerate(message["sources"][:5], 1):  # Show top 5 sources
                        source_name = source.get('source', 'Unknown')
                        source_title = source.get('title', '')
                        snippet = source.get('snippet', '')
                        similarity = source.get('similarity', 0)
                        metadata = source.get('metadata', {})
                        is_web_search = source.get('is_web_search', False)
                        
                        # Display title or source name
                        if source_title:
                            display_title = source_title
                        else:
                            display_title = source_name
                        
                        # Show collection name if available in metadata (for RAG sources)
                        collection_hint = ""
                        if isinstance(metadata, dict) and not is_web_search:
                            if any(coll in source_name.lower() for coll in ['corpus', 'competitor', 'marketing', 'pitch', 'policy', 'job', 'ip']):
                                collection_hint = f" [{source_name}]"
                            elif 'agent' in metadata:
                                collection_hint = f" [{metadata.get('agent', '')}_corpus]"
                        
                        # Display source with clickable link if it's a URL
                        if is_web_search and source_name.startswith('http'):
                            st.markdown(f"**{i}.** [{display_title}]({source_name})")
                        else:
                            st.markdown(f"**{i}.** {display_title}{collection_hint}")
                        
                        # Show snippet if available (for web search results)
                        if snippet and is_web_search:
                            st.markdown(f"   *{snippet[:200]}{'...' if len(snippet) > 200 else ''}*")
                            st.markdown(f"   🔗 [View full article]({source_name})")
                        elif source_name.startswith('http') and not is_web_search:
                            st.markdown(f"   🔗 [View source]({source_name})")
                        
                        # Show similarity and source type
                        if similarity > 0:
                            source_type = "Web Search" if is_web_search else "Cloud SQL"
                            st.caption(f"   Similarity: {similarity:.3f} | {source_type}")
                        else:
                            source_type = "Web Search" if is_web_search else "Cloud SQL Collection"
                            st.caption(f"   {source_type}")
                        
                        if metadata.get('source') and not is_web_search:
                            st.caption(f"   Original source: {metadata.get('source', 'N/A')}")
    
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
                                        has_web_search = any(s.get('is_web_search', False) for s in sources)
                                        source_label = "📚 Sources" + (" (Cloud SQL + Web Search)" if has_web_search else " (from Cloud SQL)")
                                        
                                        with st.expander(source_label):
                                            for i, source in enumerate(sources[:5], 1):
                                                source_name = source.get('source', 'Unknown')
                                                source_title = source.get('title', '')
                                                snippet = source.get('snippet', '')
                                                similarity = source.get('similarity', 0)
                                                metadata = source.get('metadata', {})
                                                is_web_search = source.get('is_web_search', False)
                                                
                                                display_title = source_title if source_title else source_name
                                                
                                                if is_web_search and source_name.startswith('http'):
                                                    st.markdown(f"**{i}.** [{display_title}]({source_name})")
                                                else:
                                                    st.markdown(f"**{i}.** {display_title}")
                                                
                                                if snippet and is_web_search:
                                                    st.markdown(f"   *{snippet[:200]}{'...' if len(snippet) > 200 else ''}*")
                                                    st.markdown(f"   🔗 [View full article]({source_name})")
                                                
                                                if similarity > 0:
                                                    source_type = "Web Search" if is_web_search else "Cloud SQL"
                                                    st.caption(f"   Similarity: {similarity:.3f} | {source_type}")
                                                else:
                                                    source_type = "Web Search" if is_web_search else "Cloud SQL Collection"
                                                    st.caption(f"   {source_type}")
                                    
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": response.get("response", ""),
                                        "sources": sources
                                    })
                                    supervisor_success = True
                                    st.rerun()  # Exit here if supervisor succeeded
                            except Exception as e:
                                logger.error(f"Supervisor execution error: {e}", exc_info=True)
                                # Display error to user
                                error_msg = f"⚠️ Supervisor agent encountered an error. Falling back to direct routing...\n\nError: {str(e)}"
                                st.warning(error_msg)
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
                            response_text = response.get('response', 'No response generated')
                            
                            # Always display response, even if empty
                            if response_text and response_text.strip():
                                st.markdown(response_text)
                            else:
                                st.warning("⚠️ No response generated. Please try rephrasing your question.")
                                response_text = "I couldn't generate a response. Please try asking your question differently or provide more context."
                            
                            # Check if Instagram content has generated image
                            if response.get('image_generated'):
                                if response.get('image_path'):
                                    st.success("✅ Instagram image generated!")
                                    
                                    # Display image
                                    image_path = response.get('image_path')
                                    if image_path and Path(image_path).exists():
                                        try:
                                            from PIL import Image
                                            img = Image.open(image_path)
                                            st.image(img, caption="Generated Instagram Image - Ready to Post!", width='stretch')
                                            
                                            # Download button
                                            with open(image_path, 'rb') as f:
                                                st.download_button(
                                                    "⬇ Download Image for Instagram",
                                                    f,
                                                    file_name=f"instagram_{Path(image_path).name}",
                                                    mime="image/png"
                                                )
                                        except Exception as e:
                                            st.error(f"Could not display image: {e}")
                                            st.info(f"Image path: {image_path}")
                                    else:
                                        st.warning(f"Image file not found at: {response.get('image_path')}")
                                    
                                    # Show image prompt if available
                                    if response.get('image_prompt'):
                                        with st.expander("📝 Image Prompt Used"):
                                            st.code(response.get('image_prompt'))
                                    
                                    # Show image URL if available
                                    if response.get('image_url'):
                                        st.info(f"Image URL: {response.get('image_url')}")
                                else:
                                    st.warning("⚠️ Image generation was attempted but no image path was returned. Check logs for details.")
                            elif response.get('image_generated') is False:
                                st.info("ℹ️ Image generation was not successful. You can still use the text content and manually create an image.")
                            
                            # Show sources
                            if response.get('sources'):
                                sources = response.get('sources', [])
                                has_web_search = any(s.get('is_web_search', False) for s in sources)
                                source_label = "📚 Sources & Citations" + (" (Cloud SQL + Web Search)" if has_web_search else " (from Cloud SQL)")
                                
                                with st.expander(source_label):
                                    for i, source in enumerate(sources[:5], 1):
                                        source_name = source.get('source', 'Unknown')
                                        source_title = source.get('title', '')
                                        snippet = source.get('snippet', '')
                                        similarity = source.get('similarity', 0)
                                        metadata = source.get('metadata', {})
                                        is_web_search = source.get('is_web_search', False)
                                        
                                        display_title = source_title if source_title else source_name
                                        
                                        if is_web_search and source_name.startswith('http'):
                                            st.markdown(f"**{i}.** [{display_title}]({source_name})")
                                        else:
                                            st.markdown(f"**{i}.** {display_title}")
                                        
                                        if snippet and is_web_search:
                                            st.markdown(f"   *{snippet[:200]}{'...' if len(snippet) > 200 else ''}*")
                                            st.markdown(f"   🔗 [View full article]({source_name})")
                                        
                                        if similarity > 0:
                                            source_type = "Web Search" if is_web_search else "Cloud SQL"
                                            st.caption(f"   Similarity: {similarity:.3f} | {source_type}")
                                        else:
                                            source_type = "Web Search" if is_web_search else "Cloud SQL Collection"
                                            st.caption(f"   {source_type}")
                            
                            # Always add to messages, even if response was empty
                            message_content = {
                                "role": "assistant",
                                "content": response_text,  # Use the processed response_text
                                "sources": response.get('sources', [])
                            }
                            
                            # Include image info if available
                            if response.get('image_generated'):
                                message_content['image_generated'] = True
                                message_content['image_path'] = response.get('image_path')
                                message_content['image_url'] = response.get('image_url')
                            
                            st.session_state.messages.append(message_content)
                            st.rerun()
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    logger.error(f"Chat error: {e}", exc_info=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    st.rerun()
    
    # Slides Preview Section
    if st.session_state.slides and len(st.session_state.slides.get('slides', [])) > 0:
        st.markdown("---")
        st.subheader("📊 Pitch Deck Slides")
        
        slides_list = st.session_state.slides['slides']
        total_slides = len(slides_list)
        
        # ============================================
        # 🎯 PRIMARY OUTPUT: POWERPOINT PRESENTATION
        # ============================================
        pptx_path = st.session_state.slides.get('pptx_path')
        
        # Fallback: If no path in session, try to find the most recent PowerPoint file
        if not pptx_path or not Path(pptx_path).exists():
            try:
                exports_dir = Path("exports")
                if exports_dir.exists():
                    pptx_files = sorted(exports_dir.glob("*.pptx"), key=lambda p: p.stat().st_mtime, reverse=True)
                    if pptx_files:
                        # Use most recent PowerPoint file
                        pptx_path = str(pptx_files[0])
                        st.session_state.slides['pptx_path'] = pptx_path
            except Exception:
                pass  # Silently fail
        
        # Always try to generate PowerPoint if slides exist but no PPTX
        # BUT: Skip if we're in Gamma-only mode (pptx_skipped flag)
        is_gamma_only_mode = st.session_state.slides.get('pptx_skipped', False)
        
        if not pptx_path and slides_list and not is_gamma_only_mode:
            print(f"🔄 Auto-generating PowerPoint (not in Gamma-only mode)")
            with st.spinner("🔄 Generating PowerPoint presentation..."):
                try:
                    from src.utils.exporters import PitchExporter
                    exporter = PitchExporter()
                    # Get AI enhancement preference and company data
                    enhance_with_ai = st.session_state.get('enhance_with_ai', True)
                    ai_provider = st.session_state.get('ai_provider', 'auto')  # 🆕 Get AI provider
                    company_data = st.session_state.get('company_data', {})
                    pptx_path = exporter.export_to_powerpoint(
                        slides_list,
                        st.session_state.slides.get('company_name', 'Company'),
                        include_images=True,
                        enhance_with_ai=enhance_with_ai,
                        company_data=company_data,  # 🆕 Pass company data
                        full_rewrite=True,  # 🆕 Enable full AI rewrite
                        ai_provider=ai_provider  # 🆕 Pass AI provider
                    )
                    if pptx_path:
                        st.session_state.slides['pptx_path'] = pptx_path
                        st.success("✅ PowerPoint generated!")
                except Exception as e:
                    st.warning(f"⚠️ Could not auto-generate PowerPoint: {e}")
                    logger.error(f"PowerPoint generation error: {e}", exc_info=True)
        elif is_gamma_only_mode:
            print(f"⏭️ Skipping auto-PowerPoint generation (Gamma-only mode detected)")
            logger.info("Skipping auto-PowerPoint generation - Gamma-only mode")
        
        # Don't show PowerPoint section if we're in Gamma-only mode
        is_gamma_only_mode = st.session_state.slides.get('pptx_skipped', False)
        
        if pptx_path and Path(pptx_path).exists() and not is_gamma_only_mode:
            st.markdown("---")
            st.markdown("## 📊 **YOUR POWERPOINT PRESENTATION**")
            st.markdown("### ✨ AI-Enhanced Professional Pitch Deck")
            
            # Main PowerPoint section
            col_ppt_main1, col_ppt_main2 = st.columns([3, 1])
            with col_ppt_main1:
                st.success(f"✅ **PowerPoint Ready!**")
                st.markdown(f"""
                - **📁 File:** `{Path(pptx_path).name}`
                - **📊 Slides:** {total_slides} professional slides
                - **🎨 Style:** AI-enhanced with modern design
                - **🖼️ Images:** Included (if available)
                """)
                
                # File size
                file_size = Path(pptx_path).stat().st_size / 1024  # KB
                st.caption(f"📦 File size: {file_size:.1f} KB")
            
            with col_ppt_main2:
                with open(pptx_path, 'rb') as f:
                    st.download_button(
                        "⬇️ **DOWNLOAD PPTX**",
                        f.read(),
                        file_name=Path(pptx_path).name,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        help="Download your complete PowerPoint presentation",
                        use_container_width=True,
                        type="primary"
                    )
            
            # Preview PowerPoint slides as images
            st.markdown("---")
            st.markdown("### 👁️ **Preview Your Slides**")
            st.info("💡 **This is your main presentation!** Download the PPTX file above to open in PowerPoint, Google Slides, or any presentation software.")
            
            # Try to show slide previews
            try:
                # Convert PPTX to images for preview (if possible)
                from pptx import Presentation
                from PIL import Image
                import io
                
                prs = Presentation(pptx_path)
                num_slides = len(prs.slides)
                
                st.markdown(f"**📑 Your presentation has {num_slides} slides:**")
                
                # Show slide thumbnails/info
                preview_cols = st.columns(min(3, num_slides))
                for i, slide in enumerate(prs.slides[:min(6, num_slides)]):  # Show first 6 slides
                    col_idx = i % 3
                    with preview_cols[col_idx]:
                        # Get slide title or number
                        slide_title = f"Slide {i+1}"
                        for shape in slide.shapes:
                            if hasattr(shape, "text") and shape.text.strip():
                                slide_title = shape.text.strip()[:30] + ("..." if len(shape.text) > 30 else "")
                                break
                        
                        with st.container():
                            st.markdown(f"""
                            <div style="border: 2px solid #3b82f6; border-radius: 8px; padding: 15px; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); margin-bottom: 10px;">
                                <h4 style="margin: 0; color: #1e40af;">📄 {slide_title}</h4>
                                <p style="margin: 5px 0; color: #64748b; font-size: 0.9em;">Slide {i+1} of {num_slides}</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                if num_slides > 6:
                    st.caption(f"... and {num_slides - 6} more slides. Download the PPTX file to see all slides!")
                    
            except Exception as e:
                # If preview fails, just show info
                st.markdown(f"**✅ Your PowerPoint contains {total_slides} professional slides**")
                st.caption("💡 Download the PPTX file above to view all slides in PowerPoint or Google Slides")
                logger.debug(f"Could not create slide preview: {e}")
            
            st.markdown("---")
        
        # Gamma and Canva removed - not working
        
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
            from src.utils.exporters import PitchExporter
            exporter = PitchExporter()
            col_exp1, col_exp2, col_exp3, col_exp4, col_exp5 = st.columns(5)
            with col_exp1:
                if st.button("📄 Export PDF"):
                    filepath = exporter.export_to_pdf(slides_list, st.session_state.slides.get('company_name', 'Company'))
                    if filepath:
                        with open(filepath, 'rb') as f:
                            st.download_button("⬇ Download PDF", f, file_name=Path(filepath).name, mime="application/pdf")
            with col_exp2:
                if st.button("📊 Export PPTX", help="Generate and download PowerPoint presentation"):
                    with st.spinner("Creating PowerPoint..."):
                        # Get AI enhancement preference (default: True)
                        enhance_with_ai = st.session_state.get('enhance_with_ai', True)
                        ai_provider = st.session_state.get('ai_provider', 'auto')  # 🆕 Get AI provider
                        # Get company data for financial charts and intelligent filtering
                        company_data = st.session_state.get('company_data', {})
                        filepath = exporter.export_to_powerpoint(
                            slides_list, 
                            st.session_state.slides.get('company_name', 'Company'),
                            include_images=True,
                            enhance_with_ai=enhance_with_ai,
                            company_data=company_data,  # 🆕 Pass company data
                            full_rewrite=True,  # 🆕 Enable full AI rewrite
                            ai_provider=ai_provider  # 🆕 Pass AI provider
                        )
                        if filepath:
                            # Update session state with new path
                            st.session_state.slides['pptx_path'] = filepath
                            with open(filepath, 'rb') as f:
                                st.download_button(
                                    "⬇ Download PPTX", 
                                    f.read(), 
                                    file_name=Path(filepath).name, 
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                    help="Download the PowerPoint file"
                                )
                            st.success(f"✅ PowerPoint created: {Path(filepath).name}")
                        else:
                            st.error("❌ Failed to create PowerPoint. Check terminal for errors.")
                            st.info("💡 Make sure python-pptx is installed: `pip install python-pptx`")
            with col_exp3:
                if st.button("📝 Export MD"):
                    filepath = exporter.export_to_markdown(slides_list, st.session_state.slides.get('company_name', 'Company'))
                    if filepath:
                        with open(filepath, 'rb') as f:
                            st.download_button("⬇ Download MD", f, file_name=Path(filepath).name, mime="text/markdown")
            # Gamma and Canva removed
        
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
    
    # Show Gamma result persistently (above Quick Actions)
    if st.session_state.get('gamma_only_result'):
        gamma_result = st.session_state.gamma_only_result
        if gamma_result.get('success') or gamma_result.get('presentation_url'):
            st.markdown("---")
            st.markdown("## 🎨 **Your Gamma.ai Presentation**")
            gamma_url = (gamma_result.get('presentation_url') or 
                       gamma_result.get('gammaUrl') or 
                       gamma_result.get('url') or
                       gamma_result.get('api_response', {}).get('gammaUrl'))
            
            if gamma_url:
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.markdown("### 🌐 **View Presentation**")
                    st.markdown(f"[**🔗 Open in Gamma.ai →**]({gamma_url})")
                    st.text_input("**Copy URL:**", value=gamma_url, key="gamma_view_persistent", disabled=False)
                with col_g2:
                    st.markdown("### ✏️ **Edit Presentation**")
                    edit_url = gamma_result.get('edit_url') or gamma_url
                    st.markdown(f"[**✏️ Edit in Gamma.ai →**]({edit_url})")
                    st.text_input("**Copy URL:**", value=edit_url, key="gamma_edit_persistent", disabled=False)
                
                st.info("""
                **📥 How to Download/Export from Gamma:**
                1. Click the **"Open in Gamma.ai"** link above
                2. In Gamma, click the **Share** button (top-right)
                3. Select **Export** from the dropdown
                4. Choose format: **PPTX**, **PDF**, or **PNG**
                5. The file will download automatically
                """)
    
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
        # Quick test button for Gamma/Canva
        if st.button("🧪 Quick Test (3 slides)", help="Test Gamma.ai and Canva with minimal slides"):
            with st.spinner("Creating test presentation with 3 slides..."):
                # Create minimal test slides
                test_slides_data = {
                    "slides": [
                        {
                            "slide_number": 1,
                            "title": "Test Company",
                            "content": "This is a quick test to verify Gamma.ai and Canva integrations work correctly.",
                            "key_points": ["Test integration", "Verify functionality"]
                        },
                        {
                            "slide_number": 2,
                            "title": "Problem",
                            "content": "Testing the integration system.",
                            "key_points": ["Quick test", "Minimal slides"]
                        },
                        {
                            "slide_number": 3,
                            "title": "Solution",
                            "content": "Integration test successful!",
                            "key_points": ["Working", "Ready"]
                        }
                    ],
                    "total_slides": 3,
                    "company_name": "Test Company"
                }
                
                # Gamma and Canva removed
                
                # Generate PowerPoint for test slides too
                try:
                    from src.utils.exporters import PitchExporter
                    exporter = PitchExporter()
                    pptx_path = exporter.export_to_powerpoint(
                        test_slides_data["slides"],
                        "Test Company",
                        include_images=False  # Skip images for quick test
                    )
                    if pptx_path:
                        test_slides_data["pptx_path"] = pptx_path
                        st.success("✅ PowerPoint also generated for test slides!")
                except Exception as e:
                    st.warning(f"⚠️ PowerPoint generation failed: {e}")
                
                # Store test results
                st.session_state.slides = test_slides_data
                st.session_state.current_slide = 0
                st.rerun()
        
        # AI Enhancement Toggle
        col_ai1, col_ai2 = st.columns([2, 1])
        with col_ai1:
            enhance_with_ai = st.checkbox(
                "🤖 Enhance with AI (improves slide content quality)", 
                value=True,
                help="Uses AI to enhance slide titles, content, and key points for better investor appeal"
            )
        with col_ai2:
            # AI Provider Selection (Gemini or OpenAI)
            ai_provider = st.selectbox(
                "AI Provider",
                options=["Auto (Gemini → OpenAI)", "Gemini", "OpenAI"],
                index=0,
                help="Choose AI provider. Auto tries Gemini first, then OpenAI"
            )
        
        # Store in session state so it persists across reruns
        st.session_state['enhance_with_ai'] = enhance_with_ai
        st.session_state['ai_provider'] = ai_provider
        
        # 🆕 QUESTIONNAIRE FOR MISSING IMPORTANT DATA
        if st.session_state.company_data:
            missing_data = []
            company_data = st.session_state.company_data
            
            # Check for critical missing data
            if not company_data.get('company_name'):
                missing_data.append(('company_name', 'Company Name', 'text'))
            if not company_data.get('problem'):
                missing_data.append(('problem', 'Problem Statement', 'textarea'))
            if not company_data.get('solution'):
                missing_data.append(('solution', 'Solution Description', 'textarea'))
            if not company_data.get('target_market'):
                missing_data.append(('target_market', 'Target Market', 'text'))
            
            # Check for important financial data if company is operating
            company_stage = company_data.get('company_stage', '').lower()
            if 'operating' in company_stage or 'established' in company_stage:
                if not company_data.get('annual_revenue'):
                    missing_data.append(('annual_revenue', 'Annual Revenue', 'text'))
                if not company_data.get('customer_count'):
                    missing_data.append(('customer_count', 'Number of Customers/Users', 'text'))
                if not company_data.get('growth_rate'):
                    missing_data.append(('growth_rate', 'Growth Rate', 'text'))
            
            # If missing critical data, show questionnaire
            if missing_data:
                st.warning("⚠️ **Missing Important Data** - Please fill these to create a better pitch deck:")
                with st.expander("📝 Fill Missing Information", expanded=True):
                    for field_id, field_label, field_type in missing_data:
                        if field_type == 'textarea':
                            value = st.text_area(
                                f"**{field_label}**",
                                value=company_data.get(field_id, ''),
                                key=f"missing_{field_id}",
                                help=f"This information is important for your pitch deck"
                            )
                        else:
                            value = st.text_input(
                                f"**{field_label}**",
                                value=company_data.get(field_id, ''),
                                key=f"missing_{field_id}",
                                help=f"This information is important for your pitch deck"
                            )
                        if value:
                            st.session_state.company_data[field_id] = value
                    
                    if st.button("✅ Save & Continue", key="save_missing_data"):
                        st.success("✅ Data saved! You can now generate slides.")
                        st.rerun()
        
        if st.button("🎯 Generate Slides"):
            if st.session_state.company_data:
                # Show info about AI provider
                if enhance_with_ai:
                    if ai_provider == "Gemini":
                        st.info("🤖 Using **Gemini** for AI enhancement. If quota is exceeded, will automatically fallback to OpenAI.")
                    elif ai_provider == "OpenAI":
                        st.info("🤖 Using **ChatGPT (OpenAI)** for AI enhancement.")
                    else:
                        st.info("🤖 Using **Auto mode**: Will try Gemini first, then automatically fallback to OpenAI if needed.")
                
                with st.spinner("Generating slides and PowerPoint..."):
                    # Include AI provider in company data
                    company_data_with_themes = {
                        **st.session_state.company_data,
                        "enhance_with_ai": enhance_with_ai,  # Pass AI enhancement preference
                        "ai_provider": ai_provider  # 🆕 Pass AI provider preference
                    }
                    slides_data = agent.generate_slides(company_data_with_themes)
                    st.session_state.slides = slides_data
                    st.session_state.current_slide = 0
                    
                    success_msg = f"✅ Generated {slides_data.get('total_slides', 0)} slides!"
                    
                    # Check what was generated
                    if slides_data.get('pptx_path'):
                        st.success(success_msg)
                    
                    # Show PowerPoint status and download
                    if slides_data.get('pptx_path'):
                        pptx_path = Path(slides_data['pptx_path'])
                        if pptx_path.exists():
                            st.markdown("---")
                            st.success("📊 **PowerPoint Generated Successfully!**")
                            with open(pptx_path, 'rb') as f:
                                st.download_button(
                                    "⬇️ Download PowerPoint Presentation",
                                    f.read(),
                                    file_name=pptx_path.name,
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                    help="Download the complete PowerPoint with all slides",
                                    use_container_width=True
                                )
        
        # Separate Gamma button
        if st.button("🚀 Generate Slides Using Gamma", help="Generate slides and create Gamma.ai presentation with PPT download"):
            if st.session_state.company_data:
                # Show info about AI provider
                if enhance_with_ai:
                    if ai_provider == "Gemini":
                        st.info("🤖 Using **Gemini** for AI enhancement. If quota is exceeded, will automatically fallback to OpenAI.")
                    elif ai_provider == "OpenAI":
                        st.info("🤖 Using **ChatGPT (OpenAI)** for AI enhancement.")
                    else:
                        st.info("🤖 Using **Auto mode**: Will try Gemini first, then automatically fallback to OpenAI if needed.")
                
                # Print to console immediately
                print(f"\n{'='*80}")
                print("🚀 GAMMA BUTTON CLICKED - Starting Gamma-only generation")
                print(f"{'='*80}\n")
                
                with st.spinner("🚀 Generating slides and creating Gamma.ai presentation (Gamma-only mode)..."):
                    # Include AI provider in company data
                    company_data_with_themes = {
                        **st.session_state.company_data,
                        "enhance_with_ai": enhance_with_ai,
                        "ai_provider": ai_provider,
                        "gamma_theme": st.session_state.get("gamma_theme", "startup-pitch")
                    }
                    
                    print(f"📋 Company data prepared: {company_data_with_themes.get('company_name', 'Unknown')}")
                    print(f"🔧 Calling generate_slides with gamma_only=True")
                    
                    # Generate slides with gamma_only=True to skip PowerPoint generation
                    slides_data = agent.generate_slides(company_data_with_themes, gamma_only=True)
                    
                    print(f"✅ generate_slides returned. Keys: {list(slides_data.keys())}")
                    print(f"📊 pptx_path in result: {slides_data.get('pptx_path', 'NOT SET')}")
                    print(f"🎨 gamma_presentation in result: {'YES' if 'gamma_presentation' in slides_data else 'NO'}")
                    print(f"⏭️ pptx_skipped flag: {slides_data.get('pptx_skipped', 'NOT SET')}")
                    
                    # Check Gamma presentation status
                    if 'gamma_presentation' in slides_data:
                        gamma_result = slides_data['gamma_presentation']
                        print(f"\n{'='*80}")
                        print(f"🎨 GAMMA PRESENTATION RESULT:")
                        print(f"   Success: {gamma_result.get('success', 'NOT SET')}")
                        if gamma_result.get('success'):
                            print(f"   ✅ Presentation URL: {gamma_result.get('presentation_url', 'NOT SET')}")
                            print(f"   ✅ Edit URL: {gamma_result.get('edit_url', 'NOT SET')}")
                            print(f"   ✅ Generation ID: {gamma_result.get('generation_id', 'NOT SET')}")
                        else:
                            print(f"   ❌ Error: {gamma_result.get('error', 'NOT SET')}")
                            print(f"   ❌ Message: {gamma_result.get('message', 'NOT SET')}")
                            if gamma_result.get('generation_id'):
                                print(f"   ⚠️ Generation ID: {gamma_result.get('generation_id')} (may still be processing)")
                        print(f"{'='*80}\n")
                    
                    # Ensure pptx_skipped flag is set
                    if slides_data.get('pptx_skipped') is None:
                        slides_data['pptx_skipped'] = True
                        print(f"✅ Set pptx_skipped=True explicitly")
                    
                    st.session_state.slides = slides_data
                    st.session_state.current_slide = 0
                    
                    print(f"🔍 Session state slides keys: {list(st.session_state.slides.keys())}")
                    print(f"🔍 Session state pptx_skipped: {st.session_state.slides.get('pptx_skipped', 'NOT SET')}")
                    
                    success_msg = f"✅ Generated {slides_data.get('total_slides', 0)} slides!"
                    st.success(success_msg)
                    
                    # Show Gamma presentation status - this is the main focus
                    st.markdown("---")
                    
                    # Check if gamma_presentation exists in response
                    if 'gamma_presentation' not in slides_data:
                        st.error("❌ **CRITICAL ERROR: Gamma presentation was not generated!**")
                        st.error("The `gamma_presentation` key is missing from the response.")
                        st.info("💡 Check the terminal/logs for detailed error messages.")
                        st.code("Expected key: 'gamma_presentation' in slides_data", language="python")
                    else:
                        gamma = slides_data.get('gamma_presentation', {})
                        gamma_success = gamma.get('success', False)
                        
                        # Try multiple possible URL fields (including nested api_response)
                        gamma_url = (gamma.get('presentation_url') or 
                                    gamma.get('gammaUrl') or 
                                    gamma.get('url') or
                                    gamma.get('api_response', {}).get('gammaUrl') or
                                    gamma.get('api_response', {}).get('gamma_url') or
                                    gamma.get('api_response', {}).get('url') or
                                    None)
                        edit_url = gamma.get('edit_url') or gamma_url
                        generation_id = gamma.get('generation_id') or gamma.get('id') or gamma.get('presentation_id')
                        
                        # Debug: Print what we got
                        print(f"\n{'='*80}")
                        print(f"🔍 UI DEBUG: Gamma presentation data:")
                        print(f"   Keys: {list(gamma.keys())}")
                        print(f"   Success: {gamma.get('success', 'NOT SET')}")
                        print(f"   presentation_url: {gamma.get('presentation_url', 'NOT SET')}")
                        print(f"   gammaUrl: {gamma.get('gammaUrl', 'NOT SET')}")
                        print(f"   url: {gamma.get('url', 'NOT SET')}")
                        print(f"   edit_url: {gamma.get('edit_url', 'NOT SET')}")
                        if gamma.get('api_response'):
                            print(f"   api_response keys: {list(gamma.get('api_response', {}).keys())}")
                            print(f"   api_response.gammaUrl: {gamma.get('api_response', {}).get('gammaUrl', 'NOT SET')}")
                            print(f"   api_response.url: {gamma.get('api_response', {}).get('url', 'NOT SET')}")
                        print(f"   Extracted gamma_url: {gamma_url}")
                        print(f"{'='*80}\n")
                        
                        # Always show status first
                        if gamma_success:
                            st.success("🎨 **Gamma.ai Presentation Created Successfully!**")
                        else:
                            st.warning("⚠️ **Gamma.ai Presentation Status**")
                            if gamma.get('error'):
                                st.error(f"**Error:** {gamma.get('error')}")
                            if gamma.get('message'):
                                st.info(f"💡 {gamma.get('message')}")
                        
                        # Always show URLs if available - FORCE DISPLAY
                        print(f"🔍 UI: About to check URL. gamma_url={gamma_url}, type={type(gamma_url)}")
                        print(f"🔍 UI: URL check result: {bool(gamma_url and gamma_url != '#' and gamma_url != 'NOT SET' and gamma_url)}")
                        
                        # Force display - show URL regardless
                        st.markdown("---")
                        st.markdown("## 🎨 **Gamma.ai Presentation**")
                        
                        if gamma_url and isinstance(gamma_url, str) and len(gamma_url) > 10:
                            # URL exists and is valid
                            st.success(f"✅ **Presentation Created!**")
                            
                            col_gamma1, col_gamma2 = st.columns(2)
                            with col_gamma1:
                                st.markdown("### 🌐 **View Presentation**")
                                st.markdown(f"[**🔗 Open in Gamma.ai →**]({gamma_url})")
                                st.caption("Click the link above to view")
                                st.text_input("**Copy URL:**", value=gamma_url, key="gamma_view_url", disabled=True)
                            
                            with col_gamma2:
                                st.markdown("### ✏️ **Edit Presentation**")
                                if edit_url and edit_url != gamma_url:
                                    st.markdown(f"[**✏️ Edit in Gamma.ai →**]({edit_url})")
                                    st.caption("Click the link above to edit")
                                    st.text_input("**Copy URL:**", value=edit_url, key="gamma_edit_url", disabled=True)
                                else:
                                    st.info("Same URL for viewing and editing")
                                    st.text_input("**Copy URL:**", value=gamma_url, key="gamma_edit_url_dup", disabled=True)
                            
                            # Show generation ID if available
                            if generation_id and generation_id != 'NOT SET':
                                st.caption(f"**Generation ID:** {generation_id}")
                        else:
                            # No valid URL - show debug info
                            st.error("⚠️ **URL extraction failed**")
                            st.warning(f"Extracted URL: {repr(gamma_url)}")
                            st.info("💡 Check terminal logs - URL should be there")
                            with st.expander("🔍 View Full Gamma Response (Debug)"):
                                st.json(gamma)
                            if generation_id:
                                st.caption(f"**Generation ID:** {generation_id}")
                            if gamma.get('poll_endpoint'):
                                st.caption(f"**Poll Endpoint:** {gamma.get('poll_endpoint')}")
                        
                        # Export instructions
                        st.markdown("---")
                        st.info("""
                        **📥 How to Download/Export from Gamma:**
                        1. Click the **"Open in Gamma.ai"** link above
                        2. In Gamma, click the **Share** button (top-right)
                        3. Select **Export** from the dropdown
                        4. Choose format: **PPTX**, **PDF**, or **PNG**
                        5. The file will download automatically
                        """)
                        
                        # Also offer to generate a regular PPTX from the same slides
                        st.markdown("---")
                        st.markdown("### 📊 **Alternative: Download Regular PowerPoint**")
                        st.caption("Generate a standard PPTX file from the same slides (not Gamma-styled)")
                        if st.button("📥 Generate & Download PPTX", key="gamma_pptx_download"):
                            with st.spinner("Generating PowerPoint from slides..."):
                                try:
                                    from src.utils.exporters import PitchExporter
                                    exporter = PitchExporter()
                                    enhance_with_ai = st.session_state.get('enhance_with_ai', True)
                                    ai_provider = st.session_state.get('ai_provider', 'auto')
                                    company_data = st.session_state.get('company_data', {})
                                    
                                    pptx_path = exporter.export_to_powerpoint(
                                        slides_data.get("slides", []),
                                        slides_data.get("company_name", "Company"),
                                        include_images=True,
                                        enhance_with_ai=enhance_with_ai,
                                        company_data=company_data,
                                        full_rewrite=True,
                                        ai_provider=ai_provider
                                    )
                                    
                                    if pptx_path and Path(pptx_path).exists():
                                        with open(pptx_path, 'rb') as f:
                                            st.download_button(
                                                "⬇️ Download PowerPoint (PPTX)",
                                                f.read(),
                                                file_name=Path(pptx_path).name,
                                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                                use_container_width=True
                                            )
                                        st.success("✅ PowerPoint generated! Click download button above.")
                                    else:
                                        st.error("❌ Failed to generate PowerPoint")
                                except Exception as e:
                                    st.error(f"❌ Error generating PowerPoint: {e}")
                        
                        # Show generation details
                        with st.expander("🔍 View Full Generation Details"):
                            st.json(gamma)
                    
                    # Don't show PowerPoint options in Gamma-only mode
                    # Check if PPT was generated despite gamma_only=True (shouldn't happen)
                    if slides_data.get('pptx_path'):
                        st.error("⚠️ **ERROR: PowerPoint was generated despite Gamma-only mode!**")
                        st.error(f"This should not happen. PPT path: {slides_data.get('pptx_path')}")
                        st.info("💡 Check terminal logs for debugging info.")
                    elif slides_data.get('pptx_skipped'):
                        st.success("✅ PowerPoint generation correctly skipped (Gamma-only mode)")
                    else:
                        st.info("ℹ️ **Note:** This is Gamma-only mode. PowerPoint generation was skipped. Use the regular 'Generate Slides' button if you need PowerPoint.")
                    
                    # Store Gamma result in session state for persistent display
                    if 'gamma_only_result' not in st.session_state:
                        st.session_state.gamma_only_result = None
                    st.session_state.gamma_only_result = slides_data.get('gamma_presentation')
                    
                    # Don't rerun here - let the Gamma display stay visible
                    # The Gamma display is already shown above, no need to rerun
                    # st.rerun()  # REMOVED - was clearing Gamma display
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

