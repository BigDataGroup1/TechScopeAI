"""Modern Dashboard Interface for TechScopeAI using Streamlit."""

import streamlit as st
import streamlit.components.v1 as components
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import sys
import uuid

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
from src.utils.user_choices import UserChoiceManager
from src.utils.pitch_question_analyzer import PitchQuestionAnalyzer

logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="TechScopeAI - AI Startup Toolkit",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# MODERN CSS STYLING
# ============================================
def inject_custom_css():
    """Inject modern CSS styling for the dashboard."""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --dark-bg: #1a1d29;
        --darker-bg: #12141c;
        --card-bg: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-light: #e2e8f0;
        --border-color: #e2e8f0;
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    }
    
    /* Global Styles */
    .stApp {
        background: #f8fafc;
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Login Page Styles */
    .login-container {
        max-width: 480px;
        margin: 60px auto;
        padding: 48px;
        background: white;
        border-radius: 24px;
        box-shadow: var(--shadow-lg);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .login-title {
        font-family: 'Outfit', sans-serif;
        font-size: 32px;
        font-weight: 700;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
    }
    
    .login-subtitle {
        color: var(--text-secondary);
        font-size: 16px;
    }
    
    /* Dashboard Header */
    .welcome-text {
        font-family: 'Outfit', sans-serif;
        font-size: 32px;
        font-weight: 600;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
        margin-top: 28px;
    }
    
    .section-bar {
        width: 40px;
        height: 4px;
        background: var(--primary-gradient);
        border-radius: 2px;
        margin-right: 12px;
    }
    
    .section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 20px;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Activity Panel - Dark Theme */
    .activity-panel-dark {
        background: linear-gradient(180deg, #1e2330 0%, #171923 100%);
        border-radius: 16px;
        padding: 24px;
        min-height: 400px;
    }
    
    .activity-header-dark {
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid #2d3748;
    }
    
    .activity-title-dark {
        font-family: 'Outfit', sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: #f7fafc;
        margin-bottom: 4px;
    }
    
    .activity-subtitle-dark {
        color: #a0aec0;
        font-size: 13px;
    }
    
    .activity-item-dark {
        padding: 14px 16px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 3px solid #667eea;
        transition: background 0.2s ease;
    }
    
    .activity-item-dark:hover {
        background: rgba(255, 255, 255, 0.08);
    }
    
    .activity-item-title-dark {
        font-weight: 500;
        color: #f7fafc;
        font-size: 14px;
        margin-bottom: 4px;
    }
    
    .activity-item-desc-dark {
        color: #a0aec0;
        font-size: 12px;
        margin-bottom: 4px;
    }
    
    .activity-item-time-dark {
        font-size: 11px;
        color: #718096;
    }
    
    .activity-empty-dark {
        text-align: center;
        padding: 50px 20px;
    }
    
    .activity-empty-text {
        color: #718096;
        font-size: 14px;
    }
    
    .activity-empty-subtext {
        color: #4a5568;
        font-size: 12px;
        margin-top: 8px;
    }
    
    /* Floating Chat Button */
    .chat-fab {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: var(--primary-gradient);
        color: white;
        padding: 16px 24px;
        border-radius: 50px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        display: flex;
        align-items: center;
        gap: 10px;
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .chat-fab:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
    }
    
    /* Chat Panel */
    .chat-panel {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 400px;
        max-height: 500px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        z-index: 999;
        overflow: hidden;
    }
    
    .chat-panel-header {
        background: var(--primary-gradient);
        color: white;
        padding: 20px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-panel-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 18px;
    }
    
    .chat-panel-body {
        padding: 20px;
        max-height: 350px;
        overflow-y: auto;
    }
    
    .chat-panel-footer {
        padding: 16px;
        border-top: 1px solid var(--border-color);
        display: flex;
        gap: 12px;
    }
    
    /* Sign Out Button */
    .signout-btn {
        background: var(--dark-bg);
        color: white;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        border: none;
        transition: all 0.3s ease;
    }
    
    .signout-btn:hover {
        background: #1e293b;
    }
    
    /* Modal/Dialog Styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 998;
    }
    
    .modal-content {
        background: white;
        border-radius: 24px;
        max-width: 800px;
        max-height: 90vh;
        margin: 40px auto;
        overflow: hidden;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
    }
    
    .modal-header {
        padding: 24px;
        border-bottom: 1px solid var(--border-color);
    }
    
    .modal-body {
        padding: 24px;
        overflow-y: auto;
        max-height: calc(90vh - 180px);
    }
    
    /* Form Styling - LARGER INPUTS */
    .stTextInput > div > div > input {
        border-radius: 14px !important;
        border: 2px solid var(--border-color) !important;
        padding: 18px 20px !important;
        font-size: 16px !important;
        min-height: 56px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 14px !important;
        border: 2px solid var(--border-color) !important;
        padding: 18px 20px !important;
        font-size: 16px !important;
        min-height: 120px !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 14px !important;
    }
    
    .stSelectbox > div > div > div {
        padding: 14px 16px !important;
        min-height: 56px !important;
        font-size: 16px !important;
    }
    
    /* Button Styling - LARGER COLORFUL BUTTONS */
    .stButton > button {
        border-radius: 12px !important;
        padding: 20px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        min-height: 70px !important;
        transition: all 0.25s ease !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Primary buttons - Purple gradient */
    .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Secondary buttons - Clean white */
    .stButton > button[kind="secondary"], .stButton > button[data-testid="baseButton-secondary"] {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        color: #334155 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: #667eea !important;
        background: #f8fafc !important;
    }
    
    /* Agent Card Buttons - Colorful variants */
    div[data-testid="column"]:nth-child(1) .stButton > button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: white !important;
    }
    
    div[data-testid="column"]:nth-child(2) .stButton > button {
        background: linear-gradient(135deg, #ec4899 0%, #db2777 100%) !important;
        color: white !important;
    }
    
    /* Database Status Badge */
    .db-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
    }
    
    .db-status-postgres {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
    }
    
    .db-status-weaviate {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: var(--primary-gradient) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8fafc !important;
        border-radius: 12px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Generated Content Cards */
    .generated-content {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid var(--border-color);
    }
    
    .generated-content-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--border-color);
    }
    
    /* Hide sidebar completely when collapsed */
    [data-testid="stSidebar"][aria-expanded="false"] {
        display: none;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================
# DATABASE STATUS CHECK
# ============================================
def get_database_status():
    """
    Check which database backend is being used.
    Returns: dict with 'type' ('weaviate' or 'postgresql'), 'status', 'details'
    """
    use_weaviate = os.getenv("USE_WEAVIATE_QUERY_AGENT", "false").lower() in ("true", "1", "yes")
    weaviate_url = os.getenv("WEAVIATE_URL", "")
    
    if use_weaviate and weaviate_url:
        # Check Weaviate connection
        try:
            # Try to import and check
            from weaviate_agents.query import QueryAgent
            import weaviate
            return {
                'type': 'weaviate',
                'status': 'active',
                'details': f"Weaviate QueryAgent",
                'url': weaviate_url[:30] + "..." if len(weaviate_url) > 30 else weaviate_url
            }
        except ImportError:
            return {
                'type': 'weaviate',
                'status': 'unavailable',
                'details': "Weaviate configured but not installed",
                'url': weaviate_url
            }
    else:
        # Using PostgreSQL
        cloud_password = os.getenv("CLOUD_SQL_PASSWORD")
        cloud_port = os.getenv("CLOUD_SQL_PORT", "5432")
        
        if cloud_password:
            return {
                'type': 'postgresql',
                'status': 'cloud',
                'details': f"Cloud SQL (port {cloud_port})",
                'url': f"localhost:{cloud_port}"
            }
        else:
            return {
                'type': 'postgresql',
                'status': 'local',
                'details': f"Local PostgreSQL (port {cloud_port})",
                'url': f"localhost:{cloud_port}"
            }


def render_database_status():
    """Render the database status badge in the UI."""
    status = get_database_status()
    
    if status['type'] == 'weaviate':
        icon = "🔮"
        label = "Weaviate QueryAgent"
        css_class = "db-status-weaviate"
    else:
        icon = "🐘"
        if status['status'] == 'cloud':
            label = "Cloud SQL (PostgreSQL)"
        else:
            label = "PostgreSQL RAG"
        css_class = "db-status-postgres"
    
    st.markdown(f"""
    <div class="db-status-badge {css_class}">
        <span>{icon}</span>
        <span>{label}</span>
    </div>
    """, unsafe_allow_html=True)
    
    return status


# ============================================
# AGENT LOADING FUNCTIONS (Cached)
# ============================================
@st.cache_resource
def load_coordinator_agent():
    """Load and cache CoordinatorAgent."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = CoordinatorAgent(retriever)
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_supervisor_agent():
    """Load and cache SupervisorAgent with all agents registered."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        
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
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = PitchAgent(retriever, ai_provider="auto")
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource(ttl=3600)
def load_competitive_agent():
    """Load and cache CompetitiveAgent."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = CompetitiveAgent(retriever, model="gpt-4-turbo-preview", ai_provider="auto")
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_patent_agent():
    """Load and cache PatentAgent."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = PatentAgent(retriever, model="gpt-4-turbo-preview", ai_provider="auto")
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_policy_agent():
    """Load and cache PolicyAgent."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = PolicyAgent(retriever, model="gpt-4-turbo-preview", ai_provider="auto")
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_marketing_agent():
    """Load and cache MarketingAgent."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = MarketingAgent(retriever, model="gpt-4-turbo-preview", ai_provider="auto")
        return agent, None
    except Exception as e:
        return None, str(e)


@st.cache_resource
def load_team_agent():
    """Load and cache TeamAgent."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, "OPENAI_API_KEY not found in environment. Add it to .env file"
        
        embedder = Embedder(use_openai=False)
        embedding_model = embedder.get_embedding_model()
        vector_store = VectorStore(embedding_model=embedding_model)
        retriever = Retriever(vector_store=vector_store, embedder=embedder)
        agent = TeamAgent(retriever, model="gpt-4-turbo-preview", ai_provider="auto")
        return agent, None
    except Exception as e:
        return None, str(e)


# ============================================
# DATA FUNCTIONS
# ============================================
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


def get_policy_questionnaire():
    """Get policy questionnaire questions."""
    from src.agents.policy_agent import PolicyAgent
    return PolicyAgent.POLICY_QUESTIONNAIRE


def get_team_questionnaire():
    """Get team building questionnaire questions."""
    from src.agents.team_agent import TeamAgent
    return TeamAgent.TEAM_QUESTIONNAIRE


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


# ============================================
# INITIALIZE SESSION STATE
# ============================================
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'authenticated': False,
        'user_id': str(uuid.uuid4()),
        'company_id': None,
        'company_data': None,
        'messages': [],
        'activities': [],
        'slides': None,
        'current_slide': 0,
        'elevator_pitch': None,
        'use_supervisor': True,
        'pending_action': None,
        'pending_action_data': None,
        'chat_open': False,
        'current_view': 'dashboard',
        'active_feature': None,
        'questionnaire_active': None,
        'questionnaire_answers': {},
        'questionnaire_index': 0,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_activity(title: str, description: str, icon: str = "📄"):
    """Add an activity to the activity log."""
    activity = {
        'id': str(uuid.uuid4()),
        'title': title,
        'description': description,
        'icon': icon,
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.activities.insert(0, activity)
    # Keep only last 20 activities
    st.session_state.activities = st.session_state.activities[:20]


# ============================================
# LOGIN PAGE
# ============================================
def render_login_page():
    """Render the login/signup page with company details form."""
    
    # Get database status
    db_status = get_database_status()
    db_icon = "🔮" if db_status['type'] == 'weaviate' else "🐘"
    db_label = "Weaviate" if db_status['type'] == 'weaviate' else "PostgreSQL"
    
    st.markdown(f"""
    <div style="max-width: 520px; margin: 40px auto; padding: 0 20px;">
        <div style="text-align: center; margin-bottom: 40px;">
            <h1 style="font-family: 'Outfit', sans-serif; font-size: 42px; font-weight: 700; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                margin-bottom: 12px;">TechScopeAI</h1>
            <p style="color: #64748b; font-size: 18px;">Your AI-powered startup toolkit</p>
            <div style="margin-top: 16px; display: inline-flex; align-items: center; gap: 8px; 
                 padding: 8px 16px; background: {'#10b98120' if db_status['type'] == 'weaviate' else '#3b82f620'}; 
                 border-radius: 20px; font-size: 13px; color: {'#059669' if db_status['type'] == 'weaviate' else '#1d4ed8'};">
                <span>Connected to {db_label} - {db_status.get('details', '')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📋 Tell us about your startup")
        st.markdown("Fill in your company details to get started with personalized AI assistance.")
        
        st.markdown("---")
        
        # Company details form
        company_name = st.text_input("Company Name *", placeholder="e.g., TechStartup Inc.")
        industry = st.text_input("Industry *", placeholder="e.g., FinTech, HealthTech, SaaS")
        
        problem = st.text_area(
            "Problem You're Solving *", 
            placeholder="Describe the problem your startup is addressing...",
            height=100
        )
        
        solution = st.text_area(
            "Your Solution *", 
            placeholder="Describe your product/service solution...",
            height=100
        )
        
        target_market = st.text_input(
            "Target Market", 
            placeholder="e.g., Small businesses, Enterprise, Consumers"
        )
        
        stage = st.selectbox(
            "Current Stage",
            ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"]
        )
        
        traction = st.text_area(
            "Traction (Optional)", 
            placeholder="Revenue, users, partnerships, etc.",
            height=80
        )
        
        funding_goal = st.text_input(
            "Funding Goal (Optional)", 
            placeholder="e.g., $500K, $2M"
        )
        
        st.markdown("---")
        
        # Submit button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Get Started", type="primary", use_container_width=True):
                # Validate required fields
                if not company_name or not industry or not problem or not solution:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    # Create company data
                    company_data = {
                        'company_name': company_name,
                        'industry': industry,
                        'problem': problem,
                        'solution': solution,
                        'target_market': target_market,
                        'current_stage': stage,
                        'traction': traction,
                        'funding_goal': funding_goal
                    }
                    
                    # Generate company ID
                    company_id = company_name.lower().replace(' ', '_').replace('.', '')[:20] + '_' + str(uuid.uuid4())[:8]
                    
                    # Save company data
                    save_company_data(company_id, company_data)
                    
                    # Update session state
                    st.session_state.authenticated = True
                    st.session_state.company_id = company_id
                    st.session_state.company_data = company_data
                    
                    # Add activity
                    add_activity(
                        "Welcome!",
                        f"Started session for {company_name}",
                        "👋"
                    )
                    
                    st.rerun()
        
        # Load test data option
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px;'>Or try with sample data</p>", unsafe_allow_html=True)
        
        col_test1, col_test2, col_test3 = st.columns([1, 2, 1])
        with col_test2:
            if st.button("📋 Load Demo Company", use_container_width=True):
                test_data = load_test_company_data()
                if test_data:
                    formatted = format_company_data_for_pitch(test_data)
                    company_id = "demo_" + str(uuid.uuid4())[:8]
                    save_company_data(company_id, formatted)
                    
                    st.session_state.authenticated = True
                    st.session_state.company_id = company_id
                    st.session_state.company_data = formatted
                    
                    add_activity(
                        "Welcome!",
                        f"Started demo session for {formatted.get('company_name', 'Demo Company')}",
                        "👋"
                    )
                    
                    st.rerun()
                else:
                    st.error("Demo data not available")


# ============================================
# FEATURE CARD COMPONENT
# ============================================
def render_feature_card(icon: str, icon_class: str, title: str, description: str, feature_key: str):
    """Render a clickable feature card."""
    # Use button for interaction
    if st.button(
        f"{icon} {title}",
        key=f"btn_{feature_key}",
        use_container_width=True,
        help=description
    ):
        st.session_state.active_feature = feature_key
        st.rerun()
    
    st.caption(description)


# ============================================
# ACTIVITY PANEL
# ============================================
def render_activity_panel():
    """Render the activity report panel with dark theme."""
    
    # Build activity items HTML
    if not st.session_state.activities:
        activities_html = """
        <div class="activity-empty-dark">
            <p class="activity-empty-text">No activities yet</p>
            <p class="activity-empty-subtext">Your selections and generated content will appear here</p>
        </div>
        """
    else:
        items_html = ""
        for activity in st.session_state.activities[:15]:  # Show more items
            timestamp = datetime.fromisoformat(activity['timestamp'])
            time_str = timestamp.strftime("%I:%M %p")
            
            items_html += f"""
            <div class="activity-item-dark">
                <div class="activity-item-title-dark">{activity['title']}</div>
                <div class="activity-item-desc-dark">{activity['description']}</div>
                <div class="activity-item-time-dark">{time_str}</div>
            </div>
            """
        activities_html = items_html
    
    # Render the full panel
    st.markdown(f"""
    <div class="activity-panel-dark">
        <div class="activity-header-dark">
            <div class="activity-title-dark">Activity Report</div>
            <div class="activity-subtitle-dark">Track your selections</div>
        </div>
        <div style="max-height: 500px; overflow-y: auto;">
            {activities_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# DASHBOARD PAGE
# ============================================
def render_dashboard():
    """Render the main dashboard with feature cards."""
    company_name = st.session_state.company_data.get('company_name', 'User')
    
    # Header
    col_header, col_status, col_signout = st.columns([3, 1.5, 0.8])
    
    with col_header:
        st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <span style="font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 600;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Welcome back, {company_name}!
            </span>
        </div>
        <p style="color: #64748b; font-size: 16px; margin: 0;">Your AI-powered startup toolkit is ready.</p>
        """, unsafe_allow_html=True)
    
    with col_status:
        # Show database status
        db_status = render_database_status()
        st.caption(f"📍 {db_status.get('details', 'Unknown')}")
    
    with col_signout:
        if st.button("Sign Out", key="signout_btn"):
            # Clear session
            st.session_state.authenticated = False
            st.session_state.company_data = None
            st.session_state.company_id = None
            st.session_state.activities = []
            st.rerun()
    
    st.markdown("---")
    
    # Main layout: Features (left) | Activity (right)
    col_features, col_activity = st.columns([2.5, 1])
    
    with col_features:
        # =====================================
        # PITCH & PRESENTATION SECTION
        # =====================================
        st.markdown("""
        <div class="section-header">
            <div class="section-bar" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);"></div>
            <span class="section-title">Pitch & Presentation</span>
        </div>
        """, unsafe_allow_html=True)
        
        pitch_col1, pitch_col2 = st.columns(2)
        
        with pitch_col1:
            st.markdown("""
            <style>
            div[data-testid="stVerticalBlock"]:has(> div > div > button[key="pitch_deck"]) button {
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            if st.button("Generate Pitch Deck", key="pitch_deck", use_container_width=True):
                st.session_state.active_feature = "pitch_deck"
                add_activity("Pitch Deck", "Started generating pitch deck", "")
            st.caption("Create a complete pitch deck (PowerPoint + Gamma).")
        
        with pitch_col2:
            if st.button("Elevator Pitch", key="elevator_pitch", use_container_width=True):
                st.session_state.active_feature = "elevator_pitch"
                add_activity("Elevator Pitch", "Started generating elevator pitch", "")
            st.caption("Generate a 60-second elevator pitch.")
        
        # =====================================
        # MARKET INTELLIGENCE SECTION
        # =====================================
        st.markdown("""
        <div class="section-header">
            <div class="section-bar" style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);"></div>
            <span class="section-title">Market Intelligence</span>
        </div>
        """, unsafe_allow_html=True)
        
        market_col1, market_col2, market_col3 = st.columns(3)
        
        with market_col1:
            if st.button("Analyze Competitors", key="competitors", use_container_width=True):
                st.session_state.active_feature = "competitors"
                add_activity("Competitors", "Started competitive analysis", "")
            st.caption("Get competitive intelligence and market insights.")
        
        with market_col2:
            if st.button("Marketing Strategies", key="marketing", use_container_width=True):
                st.session_state.active_feature = "marketing"
                add_activity("Marketing", "Started marketing content generation", "")
            st.caption("Generate content from your prompt.")
        
        with market_col3:
            if st.button("Policy & Compliance", key="policy", use_container_width=True):
                st.session_state.active_feature = "policy"
                add_activity("Policy", "Started policy generation", "")
            st.caption("Generate privacy policy or terms of service.")
        
        # =====================================
        # PATENT & IP SECTION
        # =====================================
        st.markdown("""
        <div class="section-header">
            <div class="section-bar" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);"></div>
            <span class="section-title">Patent & IP</span>
        </div>
        """, unsafe_allow_html=True)
        
        patent_col1, patent_col2 = st.columns(2)
        
        with patent_col1:
            if st.button("Assess Patentability", key="patentability", use_container_width=True):
                st.session_state.active_feature = "patentability"
                add_activity("Patent", "Started patentability assessment", "")
            st.caption("Describe your invention to assess patentability.")
        
        with patent_col2:
            if st.button("Filing Strategy", key="filing_strategy", use_container_width=True):
                st.session_state.active_feature = "filing_strategy"
                add_activity("Filing", "Started filing strategy analysis", "")
            st.caption("Get patent filing strategy.")
        
        # =====================================
        # TEAM SECTION
        # =====================================
        st.markdown("""
        <div class="section-header">
            <div class="section-bar" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);"></div>
            <span class="section-title">Team</span>
        </div>
        """, unsafe_allow_html=True)
        
        team_col1, team_col2 = st.columns(2)
        
        with team_col1:
            if st.button("Team Analysis", key="team_analysis", use_container_width=True):
                st.session_state.active_feature = "team_analysis"
                add_activity("Team", "Started team analysis", "")
            st.caption("Describe your team needs and get recommendations.")
        
        with team_col2:
            if st.button("Job Description", key="job_description", use_container_width=True):
                st.session_state.active_feature = "job_description"
                add_activity("Job Description", "Started JD generation", "")
            st.caption("Describe the role you want to hire for.")
    
    with col_activity:
        render_activity_panel()
    
    # =====================================
    # FLOATING CHAT BUTTON
    # =====================================
    render_chat_button()


# ============================================
# CHAT ASSISTANT
# ============================================
def render_chat_button():
    """Render the floating chat button and panel."""
    # Create a container for the chat interface at the bottom
    st.markdown("---")
    
    # Chat toggle
    if st.button("Ask me anything", key="chat_toggle", use_container_width=True):
        st.session_state.chat_open = not st.session_state.chat_open
    
    if st.session_state.chat_open:
        render_chat_panel()


def render_chat_panel():
    """Render the AI assistant chat panel."""
    st.markdown("### AI Assistant")
    st.caption("Ask about pitch decks, marketing, patents, and more")
    
    # Display chat messages
    for message in st.session_state.messages[-10:]:  # Show last 10 messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Process with supervisor agent
        with st.spinner("Thinking..."):
            try:
                supervisor, error = load_supervisor_agent()
                if error:
                    response_text = f"Error: {error}"
                else:
                    query_context = st.session_state.company_data or {}
                    response = supervisor.process_query(prompt, query_context)
                    response_text = response.get("response", "I couldn't process that request.")
                    
                    # Add activity
                    add_activity(
                        "AI Chat",
                        f"Asked: {prompt[:50]}...",
                        "💬"
                    )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}"
                })
        
        st.rerun()


# ============================================
# FEATURE VIEWS
# ============================================
def render_feature_view():
    """Render the active feature view."""
    feature = st.session_state.active_feature
    
    if not feature:
        return
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.active_feature = None
        st.rerun()
    
    st.markdown("---")
    
    # Route to appropriate feature handler
    if feature == "pitch_deck":
        render_pitch_deck_feature()
    elif feature == "elevator_pitch":
        render_elevator_pitch_feature()
    elif feature == "competitors":
        render_competitors_feature()
    elif feature == "marketing":
        render_marketing_feature()
    elif feature == "policy":
        render_policy_feature()
    elif feature == "patentability":
        render_patent_feature()
    elif feature == "filing_strategy":
        render_filing_strategy_feature()
    elif feature == "team_analysis":
        render_team_feature()
    elif feature == "job_description":
        render_job_description_feature()


def render_pitch_deck_feature():
    """Render pitch deck generation feature."""
    st.markdown("## Generate Pitch Deck")
    st.markdown("Create a professional pitch deck based on your company information.")
    
    company_data = st.session_state.company_data
    
    # Show company summary
    with st.expander("📋 Your Company Information", expanded=False):
        st.json(company_data)
    
    # Options
    col1, col2 = st.columns(2)
    with col1:
        enhance_with_ai = st.checkbox("🤖 Enhance with AI", value=True, 
                                       help="Use AI to improve slide content")
    with col2:
        ai_provider = st.selectbox(
            "AI Provider",
            ["Auto (Gemini → OpenAI)", "Gemini", "OpenAI"],
            help="Choose AI provider for enhancement"
        )
    
    st.markdown("---")
    
    if st.button("🚀 Generate Pitch Deck", type="primary", use_container_width=True):
        pitch_agent, error = load_pitch_agent()
        
        if error:
            st.error(f"Error loading agent: {error}")
            return
        
        with st.spinner("Generating your pitch deck... This may take a minute."):
            try:
                # Map provider selection
                provider_map = {
                    "Auto (Gemini → OpenAI)": "auto",
                    "Gemini": "gemini",
                    "OpenAI": "openai"
                }
                
                enhanced_data = {
                    **company_data,
                    "enhance_with_ai": enhance_with_ai,
                    "ai_provider": provider_map.get(ai_provider, "auto")
                }
                
                slides_data = pitch_agent.generate_slides(enhanced_data)
                st.session_state.slides = slides_data
                st.session_state.current_slide = 0
                
                add_activity(
                    "Pitch Deck Generated",
                    f"Created {slides_data.get('total_slides', 0)} slides",
                    "📊"
                )
                
                st.success(f"✅ Generated {slides_data.get('total_slides', 0)} slides!")
                
            except Exception as e:
                st.error(f"Error generating pitch deck: {str(e)}")
                logger.error(f"Pitch deck error: {e}", exc_info=True)
    
    # Display slides if available
    if st.session_state.slides:
        render_slides_preview()


def render_slides_preview():
    """Render the slides preview section."""
    slides_data = st.session_state.slides
    slides_list = slides_data.get('slides', [])
    total_slides = len(slides_list)
    
    if total_slides == 0:
        return
    
    st.markdown("---")
    st.markdown("### 📊 Your Pitch Deck")
    
    # Download PowerPoint
    pptx_path = slides_data.get('pptx_path')
    if pptx_path and Path(pptx_path).exists():
        with open(pptx_path, 'rb') as f:
            st.download_button(
                "⬇️ Download PowerPoint",
                f.read(),
                file_name=Path(pptx_path).name,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )
    
    # Slide navigation
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("◀ Previous", disabled=st.session_state.current_slide == 0):
            st.session_state.current_slide -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"**Slide {st.session_state.current_slide + 1} of {total_slides}**")
    
    with col3:
        if st.button("Next ▶", disabled=st.session_state.current_slide >= total_slides - 1):
            st.session_state.current_slide += 1
            st.rerun()
    
    # Display current slide
    if 0 <= st.session_state.current_slide < total_slides:
        slide = slides_list[st.session_state.current_slide]
        
        st.markdown(f"### {slide.get('title', 'Untitled')}")
        st.markdown(slide.get('content', ''))
        
        if slide.get('key_points'):
            st.markdown("**Key Points:**")
            for point in slide['key_points']:
                st.markdown(f"• {point}")


def render_elevator_pitch_feature():
    """Render elevator pitch generation feature."""
    st.markdown("## Generate Elevator Pitch")
    st.markdown("Create a compelling 60-second elevator pitch for your startup.")
    
    duration = st.slider("Pitch Duration (seconds)", 30, 120, 60)
    
    if st.button("🎤 Generate Pitch", type="primary", use_container_width=True):
        pitch_agent, error = load_pitch_agent()
        
        if error:
            st.error(f"Error: {error}")
            return
        
        with st.spinner("Crafting your elevator pitch..."):
            try:
                result = pitch_agent.generate_elevator_pitch(
                    st.session_state.company_data,
                    duration_seconds=duration
                )
                
                if result and result.get('elevator_pitch'):
                    st.session_state.elevator_pitch = result
                    
                    add_activity(
                        "Elevator Pitch Generated",
                        f"{duration}-second pitch created",
                        "🎤"
                    )
                    
                    st.success("✅ Elevator pitch generated!")
                else:
                    st.error("Failed to generate pitch")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display elevator pitch if available
    if st.session_state.elevator_pitch:
        pitch_data = st.session_state.elevator_pitch
        
        st.markdown("---")
        st.markdown("### Your Elevator Pitch")
        
        st.info(pitch_data.get('elevator_pitch', ''))
        
        st.download_button(
            "💾 Download as Text",
            pitch_data.get('elevator_pitch', ''),
            file_name=f"{st.session_state.company_data.get('company_name', 'company')}_elevator_pitch.txt",
            mime="text/plain"
        )


def render_competitors_feature():
    """Render competitive analysis feature."""
    st.markdown("## Competitive Analysis")
    st.markdown("Get deep insights into your competitive landscape.")
    
    # Optional additional input
    specific_competitors = st.text_area(
        "Known Competitors (Optional)",
        placeholder="List any specific competitors you'd like analyzed, one per line",
        height=100
    )
    
    if st.button("🔍 Analyze Competition", type="primary", use_container_width=True):
        competitive_agent, error = load_competitive_agent()
        
        if error:
            st.error(f"Error: {error}")
            return
        
        with st.spinner("Analyzing competitive landscape..."):
            try:
                competitors = [c.strip() for c in specific_competitors.split('\n') if c.strip()] if specific_competitors else None
                
                response = competitive_agent.analyze_competitors(
                    company_details=st.session_state.company_data,
                    competitors=competitors
                )
                
                add_activity(
                    "Competitive Analysis",
                    "Completed market analysis",
                    "📊"
                )
                
                st.markdown("### Analysis Results")
                st.markdown(response.get('response', 'No response'))
                
                # Show sources
                if response.get('sources'):
                    with st.expander("📚 Sources"):
                        for source in response['sources'][:5]:
                            st.markdown(f"• {source.get('source', 'Unknown')}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


def render_marketing_feature():
    """Render marketing content generation feature."""
    st.markdown("## Marketing Content")
    st.markdown("Generate engaging marketing content for your startup.")
    
    platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Both"])
    
    content_type = st.selectbox(
        "Content Type",
        ["Product Launch", "Feature Announcement", "Company Update", "Educational", "Promotional"]
    )
    
    description = st.text_area(
        "What's this post about?",
        placeholder="Describe what you want to promote or announce...",
        height=100
    )
    
    generate_image = st.checkbox("🎨 Generate AI Image", value=True)
    
    if generate_image:
        image_provider = st.selectbox("Image Provider", ["DALL-E 3 (OpenAI)", "Gemini Image (Google)"])
    
    if st.button("📱 Generate Content", type="primary", use_container_width=True):
        if not description:
            st.warning("Please describe your post")
            return
        
        marketing_agent, error = load_marketing_agent()
        
        if error:
            st.error(f"Error: {error}")
            return
        
        with st.spinner("Creating marketing content..."):
            try:
                context = {
                    **st.session_state.company_data,
                    'platform': platform,
                    'content_type': content_type,
                    'product_description': description,
                    'generate_image': 'Yes, generate custom AI images' if generate_image else 'No',
                    'image_provider': 'dalle' if generate_image and 'DALL-E' in image_provider else 'gemini'
                }
                
                if 'Instagram' in platform:
                    response = marketing_agent.generate_instagram_content(context)
                else:
                    response = marketing_agent.generate_linkedin_content(context)
                
                add_activity(
                    f"{platform} Content",
                    f"Generated {content_type} content",
                    "📱"
                )
                
                st.markdown("### Generated Content")
                st.markdown(response.get('response', 'No content generated'))
                
                # Show image if generated
                if response.get('image_path') and Path(response['image_path']).exists():
                    st.image(response['image_path'], caption="Generated Image")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


def render_policy_feature():
    """Render policy generation feature."""
    st.markdown("## Policy & Compliance")
    st.markdown("Generate legal policies for your startup.")
    
    policy_type = st.selectbox(
        "Policy Type",
        ["Privacy Policy", "Terms of Service", "Both"]
    )
    
    additional_info = st.text_area(
        "Additional Requirements (Optional)",
        placeholder="Any specific requirements or focus areas...",
        height=100
    )
    
    if st.button("📋 Generate Policy", type="primary", use_container_width=True):
        policy_agent, error = load_policy_agent()
        
        if error:
            st.error(f"Error: {error}")
            return
        
        with st.spinner("Generating policy document..."):
            try:
                context = {
                    **st.session_state.company_data,
                    'additional_requirements': additional_info
                }
                
                responses = []
                
                if policy_type in ["Privacy Policy", "Both"]:
                    pp_response = policy_agent.generate_privacy_policy(context)
                    responses.append(("Privacy Policy", pp_response))
                
                if policy_type in ["Terms of Service", "Both"]:
                    tos_response = policy_agent.generate_terms_of_service(context)
                    responses.append(("Terms of Service", tos_response))
                
                add_activity(
                    policy_type,
                    "Generated policy document",
                    "🔒"
                )
                
                for name, resp in responses:
                    st.markdown(f"### {name}")
                    st.markdown(resp.get('response', 'No content generated'))
                    st.markdown("---")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


def render_patent_feature():
    """Render patent assessment feature."""
    st.markdown("## Patentability Assessment")
    st.markdown("Assess the patentability of your invention.")
    
    invention_description = st.text_area(
        "Describe Your Invention *",
        placeholder="Provide a detailed description of your invention...",
        height=150
    )
    
    novelty = st.text_area(
        "What's Novel About It?",
        placeholder="What makes your invention unique compared to existing solutions?",
        height=100
    )
    
    if st.button("🔬 Assess Patentability", type="primary", use_container_width=True):
        if not invention_description:
            st.warning("Please describe your invention")
            return
        
        patent_agent, error = load_patent_agent()
        
        if error:
            st.error(f"Error: {error}")
            return
        
        with st.spinner("Analyzing patentability..."):
            try:
                context = {
                    **st.session_state.company_data,
                    'invention_description': invention_description,
                    'novelty': novelty
                }
                
                response = patent_agent.assess_patentability(
                    f"{invention_description} - {novelty}",
                    context
                )
                
                add_activity(
                    "Patent Assessment",
                    "Completed patentability analysis",
                    "⚖️"
                )
                
                st.markdown("### Assessment Results")
                st.markdown(response.get('response', 'No assessment generated'))
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


def render_filing_strategy_feature():
    """Render patent filing strategy feature."""
    st.markdown("## Filing Strategy")
    st.markdown("Get recommendations for your patent filing strategy.")
    
    geographic_interest = st.multiselect(
        "Target Geographies",
        ["United States", "European Union", "China", "Japan", "South Korea", "India", "Other"],
        default=["United States"]
    )
    
    budget_range = st.selectbox(
        "Budget Range",
        ["$5K - $15K", "$15K - $30K", "$30K - $50K", "$50K+"]
    )
    
    if st.button("📄 Generate Strategy", type="primary", use_container_width=True):
        patent_agent, error = load_patent_agent()
        
        if error:
            st.error(f"Error: {error}")
            return
        
        with st.spinner("Developing filing strategy..."):
            try:
                context = {
                    **st.session_state.company_data,
                    'geographic_interest': geographic_interest,
                    'budget_range': budget_range
                }
                
                response = patent_agent.filing_strategy(context)
                
                add_activity(
                    "Filing Strategy",
                    "Generated patent filing strategy",
                    "📄"
                )
                
                st.markdown("### Filing Strategy")
                st.markdown(response.get('response', 'No strategy generated'))
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


def render_team_feature():
    """Render team analysis feature."""
    st.markdown("## Team Analysis")
    st.markdown("Analyze your team needs and get hiring recommendations.")
    
    current_team = st.text_area(
        "Current Team (Optional)",
        placeholder="Describe your current team members and their roles...",
        height=100
    )
    
    challenges = st.text_area(
        "Current Challenges",
        placeholder="What challenges are you facing that require new hires?",
        height=100
    )
    
    if st.button("👥 Analyze Team", type="primary", use_container_width=True):
        team_agent, error = load_team_agent()
        
        if error:
            st.error(f"Error: {error}")
            return
        
        with st.spinner("Analyzing team needs..."):
            try:
                context = {
                    **st.session_state.company_data,
                    'current_team': current_team,
                    'challenges': challenges
                }
                
                response = team_agent.analyze_team_needs(
                    company_context=context,
                    team_context=context
                )
                
                add_activity(
                    "Team Analysis",
                    "Completed hiring recommendations",
                    "👥"
                )
                
                st.markdown("### Team Recommendations")
                st.markdown(response.get('response', 'No recommendations generated'))
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


def render_job_description_feature():
    """Render job description generation feature."""
    st.markdown("## Job Description Generator")
    st.markdown("Generate professional job descriptions for your open positions.")
    
    role_title = st.text_input("Role Title *", placeholder="e.g., Senior Software Engineer")
    
    role_type = st.selectbox(
        "Role Type",
        ["Full-time", "Part-time", "Contract", "Internship"]
    )
    
    experience_level = st.selectbox(
        "Experience Level",
        ["Entry Level", "Mid Level", "Senior", "Lead", "Executive"]
    )
    
    key_responsibilities = st.text_area(
        "Key Responsibilities",
        placeholder="Main responsibilities for this role...",
        height=100
    )
    
    required_skills = st.text_area(
        "Required Skills",
        placeholder="Technical and soft skills required...",
        height=80
    )
    
    if st.button("💼 Generate Job Description", type="primary", use_container_width=True):
        if not role_title:
            st.warning("Please enter a role title")
            return
        
        team_agent, error = load_team_agent()
        
        if error:
            st.error(f"Error: {error}")
            return
        
        with st.spinner("Generating job description..."):
            try:
                context = {
                    **st.session_state.company_data,
                    'role_title': role_title,
                    'role_type': role_type,
                    'experience_level': experience_level,
                    'responsibilities': key_responsibilities,
                    'required_skills': required_skills
                }
                
                response = team_agent.generate_job_description(context)
                
                add_activity(
                    "Job Description",
                    f"Generated JD for {role_title}",
                    "💼"
                )
                
                st.markdown("### Job Description")
                st.markdown(response.get('response', 'No JD generated'))
                
                # Download button
                st.download_button(
                    "💾 Download JD",
                    response.get('response', ''),
                    file_name=f"{role_title.replace(' ', '_')}_JD.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application entry point."""
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Route based on authentication state
    if not st.session_state.authenticated:
        render_login_page()
    else:
        # Check if a feature is active
        if st.session_state.active_feature:
            render_feature_view()
        else:
            render_dashboard()


if __name__ == "__main__":
    main()
