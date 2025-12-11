"""FastAPI application for TechScopeAI backend API."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from functools import lru_cache
import sys

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment variables
from dotenv import load_dotenv

# Try to load .env from multiple locations
# 1. Current directory (worktree)
# 2. Parent project directory (original location)
env_paths = [
    Path(__file__).parent.parent.parent / ".env",  # Worktree root
    Path("/Users/akshtalati/Desktop/FinalProject/TechScopeAI/.env"),  # Original project
]

# Debug: print all paths being checked
print("Checking for .env file in:")
for env_path in env_paths:
    print(f"  - {env_path} (exists: {env_path.exists()})")

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        result = load_dotenv(env_path, override=True)
        print(f"✓ Loaded .env from {env_path} (result: {result})")
        env_loaded = True
        break

if not env_loaded:
    # Fallback to default behavior (current directory)
    result = load_dotenv()
    print(f"⚠ No .env file found in expected locations, using default load_dotenv() (result: {result})")

# Debug: Check if OPENAI_API_KEY is loaded
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✓ OPENAI_API_KEY is set (length: {len(api_key)})")
else:
    print("✗ OPENAI_API_KEY is NOT set after loading .env")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional as Opt

# Import agents and utilities
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

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TechScopeAI API",
    description="Backend API for TechScopeAI multi-agent system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent cache
_agent_cache = {}


def init_rag_components():
    """Initialize RAG components."""
    embedder = Embedder(use_openai=False)
    embedding_model = embedder.get_embedding_model()
    vector_store = VectorStore(embedding_model=embedding_model)
    retriever = Retriever(vector_store=vector_store, embedder=embedder)
    return retriever


def _check_api_key():
    """Check if OPENAI_API_KEY is set."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not found in environment. Please set it in your .env file or as an environment variable."
        )
    return api_key


@lru_cache(maxsize=1)
def get_pitch_agent():
    """Get or create PitchAgent."""
    if "pitch" not in _agent_cache:
        _check_api_key()
        retriever = init_rag_components()
        _agent_cache["pitch"] = PitchAgent(retriever, ai_provider="auto")
    return _agent_cache["pitch"]


@lru_cache(maxsize=1)
def get_competitive_agent():
    """Get or create CompetitiveAgent."""
    if "competitive" not in _agent_cache:
        _check_api_key()
        retriever = init_rag_components()
        _agent_cache["competitive"] = CompetitiveAgent(
            retriever, model="gpt-4-turbo-preview", ai_provider="auto"
        )
    return _agent_cache["competitive"]


@lru_cache(maxsize=1)
def get_patent_agent():
    """Get or create PatentAgent."""
    if "patent" not in _agent_cache:
        _check_api_key()
        retriever = init_rag_components()
        _agent_cache["patent"] = PatentAgent(
            retriever, model="gpt-4-turbo-preview", ai_provider="auto"
        )
    return _agent_cache["patent"]


@lru_cache(maxsize=1)
def get_policy_agent():
    """Get or create PolicyAgent."""
    if "policy" not in _agent_cache:
        _check_api_key()
        retriever = init_rag_components()
        _agent_cache["policy"] = PolicyAgent(
            retriever, model="gpt-4-turbo-preview", ai_provider="auto"
        )
    return _agent_cache["policy"]


@lru_cache(maxsize=1)
def get_marketing_agent():
    """Get or create MarketingAgent."""
    if "marketing" not in _agent_cache:
        _check_api_key()
        retriever = init_rag_components()
        _agent_cache["marketing"] = MarketingAgent(
            retriever, model="gpt-4-turbo-preview", ai_provider="auto"
        )
    return _agent_cache["marketing"]


@lru_cache(maxsize=1)
def get_team_agent():
    """Get or create TeamAgent."""
    if "team" not in _agent_cache:
        _check_api_key()
        retriever = init_rag_components()
        _agent_cache["team"] = TeamAgent(
            retriever, model="gpt-4-turbo-preview", ai_provider="auto"
        )
    return _agent_cache["team"]


@lru_cache(maxsize=1)
def get_coordinator_agent():
    """Get or create CoordinatorAgent."""
    if "coordinator" not in _agent_cache:
        _check_api_key()
        retriever = init_rag_components()
        _agent_cache["coordinator"] = CoordinatorAgent(retriever)
    return _agent_cache["coordinator"]


@lru_cache(maxsize=1)
def get_supervisor_agent():
    """Get or create SupervisorAgent with all agents registered."""
    if "supervisor" not in _agent_cache:
        _check_api_key()
        retriever = init_rag_components()
        supervisor = SupervisorAgent(retriever)
        
        # Register all agents
        try:
            supervisor.register_agent("pitch", get_pitch_agent())
            supervisor.register_agent("competitive", get_competitive_agent())
            supervisor.register_agent("patent", get_patent_agent())
            supervisor.register_agent("policy", get_policy_agent())
            supervisor.register_agent("marketing", get_marketing_agent())
            supervisor.register_agent("team", get_team_agent())
            supervisor.register_agent("coordinator", get_coordinator_agent())
        except Exception as e:
            logger.error(f"Error registering agents: {e}")
        
        _agent_cache["supervisor"] = supervisor
    return _agent_cache["supervisor"]


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


# Pydantic models
class CompanyDataRequest(BaseModel):
    company_id: str
    data: Dict[str, Any]


class QueryRequest(BaseModel):
    query: str
    company_id: Opt[str] = None
    context: Opt[Dict[str, Any]] = None


class GenerateSlidesRequest(BaseModel):
    company_id: str
    gamma_only: Opt[bool] = False


class EvaluatePitchRequest(BaseModel):
    pitch_content: str
    company_id: Opt[str] = None


class GenerateFromOutlineRequest(BaseModel):
    outline: str
    company_id: str


class AnalyzeCompetitorsRequest(BaseModel):
    company_id: str
    competitors: Opt[List[str]] = None


class SearchPatentsRequest(BaseModel):
    query: str
    company_id: Opt[str] = None


class GenerateMarketingImageRequest(BaseModel):
    product_description: str
    style: Opt[str] = "Professional"
    company_id: Opt[str] = None


class GenerateContentRequest(BaseModel):
    content_type: str  # "instagram", "linkedin", "privacy_policy", "terms_of_service", "hr_policies"
    company_id: Opt[str] = None
    context: Opt[Dict[str, Any]] = None


class AnalyzeTeamNeedsRequest(BaseModel):
    company_id: str
    team_context: Opt[Dict[str, Any]] = None


# Health check
@app.get("/")
async def root():
    return {"message": "TechScopeAI API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Company data endpoints
@app.get("/api/company/{company_id}")
async def get_company_data(company_id: str):
    """Get company data by ID."""
    data = load_company_data_file(company_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Company data not found")
    return {"company_id": company_id, "data": data}


@app.post("/api/company")
async def save_company_data_endpoint(request: CompanyDataRequest):
    """Save company data."""
    try:
        save_company_data(request.company_id, request.data)
        return {"message": "Company data saved successfully", "company_id": request.company_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Questionnaire endpoints
@app.get("/api/questionnaires/patent")
async def get_patent_questionnaire():
    """Get patent questionnaire."""
    from src.agents.patent_agent import PatentAgent
    return {"questionnaire": PatentAgent.PATENT_QUESTIONNAIRE}


@app.get("/api/questionnaires/marketing")
async def get_marketing_questionnaire():
    """Get marketing questionnaire."""
    from src.agents.marketing_agent import MarketingAgent
    return {"questionnaire": MarketingAgent.MARKETING_QUESTIONNAIRE}


@app.get("/api/questionnaires/policy")
async def get_policy_questionnaire():
    """Get policy questionnaire."""
    from src.agents.policy_agent import PolicyAgent
    return {"questionnaire": PolicyAgent.POLICY_QUESTIONNAIRE}


@app.get("/api/questionnaires/team")
async def get_team_questionnaire():
    """Get team questionnaire."""
    from src.agents.team_agent import TeamAgent
    return {"questionnaire": TeamAgent.TEAM_QUESTIONNAIRE}


@app.get("/api/questionnaires/role-specific")
async def get_role_specific_questionnaire():
    """Get role-specific questionnaire."""
    from src.agents.team_agent import TeamAgent
    return {"questionnaire": TeamAgent.ROLE_SPECIFIC_QUESTIONNAIRE}


# Pitch Agent endpoints
@app.post("/api/pitch/generate-slides")
async def generate_slides(request: GenerateSlidesRequest):
    """Generate pitch deck slides."""
    try:
        agent = get_pitch_agent()
        company_data = load_company_data_file(request.company_id)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company data not found")
        
        slides_data = agent.generate_slides(company_data, gamma_only=request.gamma_only)
        return {"slides": slides_data, "company_id": request.company_id}
    except Exception as e:
        logger.error(f"Error generating slides: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/evaluate")
async def evaluate_pitch(request: EvaluatePitchRequest):
    """Evaluate a pitch."""
    try:
        agent = get_pitch_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.evaluate_pitch(request.pitch_content, company_data)
        return {"evaluation": response}
    except Exception as e:
        logger.error(f"Error evaluating pitch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/evaluate-with-scores")
async def evaluate_pitch_with_scores(request: EvaluatePitchRequest):
    """Evaluate a pitch with detailed scores."""
    try:
        agent = get_pitch_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.evaluate_pitch_with_scores(request.pitch_content, company_data)
        return {"evaluation": response}
    except Exception as e:
        logger.error(f"Error evaluating pitch with scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/generate-from-outline")
async def generate_from_outline(request: GenerateFromOutlineRequest):
    """Generate pitch from outline."""
    try:
        agent = get_pitch_agent()
        company_data = load_company_data_file(request.company_id)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company data not found")
        
        response = agent.generate_from_outline(request.outline, company_data)
        return {"content": response, "company_id": request.company_id}
    except Exception as e:
        logger.error(f"Error generating from outline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/generate-from-details")
async def generate_from_details(company_id: str):
    """Generate pitch from company details."""
    try:
        agent = get_pitch_agent()
        company_data = load_company_data_file(company_id)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company data not found")
        
        response = agent.generate_from_details(company_data)
        return {"content": response, "company_id": company_id}
    except Exception as e:
        logger.error(f"Error generating from details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/elevator-pitch")
async def generate_elevator_pitch(company_id: str):
    """Generate elevator pitch."""
    try:
        agent = get_pitch_agent()
        company_data = load_company_data_file(company_id)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company data not found")
        
        response = agent.generate_elevator_pitch(company_data)
        return {"elevator_pitch": response, "company_id": company_id}
    except Exception as e:
        logger.error(f"Error generating elevator pitch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/query")
async def pitch_query(request: QueryRequest):
    """Process a query with pitch agent."""
    try:
        agent = get_pitch_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.process_query(request.query, company_data or request.context or {})
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing pitch query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Competitive Agent endpoints
@app.post("/api/competitive/analyze")
async def analyze_competitors(request: AnalyzeCompetitorsRequest):
    """Analyze competitors."""
    try:
        agent = get_competitive_agent()
        company_data = load_company_data_file(request.company_id)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company data not found")
        
        response = agent.analyze_competitors(company_data, request.competitors)
        return {"analysis": response, "company_id": request.company_id}
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/competitive/query")
async def competitive_query(request: QueryRequest):
    """Process a query with competitive agent."""
    try:
        agent = get_competitive_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.process_query(request.query, company_data or request.context or {})
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing competitive query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Patent Agent endpoints
@app.post("/api/patent/search")
async def search_patents(request: SearchPatentsRequest):
    """Search for patents."""
    try:
        agent = get_patent_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.search_patents(request.query, company_data)
        return {"patents": response}
    except Exception as e:
        logger.error(f"Error searching patents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/patent/query")
async def patent_query(request: QueryRequest):
    """Process a query with patent agent."""
    try:
        agent = get_patent_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.process_query(request.query, company_data or request.context or {})
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing patent query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Policy Agent endpoints
@app.post("/api/policy/generate")
async def generate_policy(request: GenerateContentRequest):
    """Generate policy documents."""
    try:
        agent = get_policy_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        context = company_data or request.context or {}
        
        if request.content_type == "privacy_policy":
            response = agent.generate_privacy_policy(context)
        elif request.content_type == "terms_of_service":
            response = agent.generate_terms_of_service(context)
        elif request.content_type == "hr_policies":
            response = agent.generate_hr_policies(context)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown content type: {request.content_type}")
        
        return {"content": response, "type": request.content_type}
    except Exception as e:
        logger.error(f"Error generating policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policy/query")
async def policy_query(request: QueryRequest):
    """Process a query with policy agent."""
    try:
        agent = get_policy_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.process_query(request.query, company_data or request.context or {})
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing policy query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Marketing Agent endpoints
@app.post("/api/marketing/generate-image")
async def generate_marketing_image(request: GenerateMarketingImageRequest):
    """Generate marketing image."""
    try:
        agent = get_marketing_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.generate_marketing_image(request.product_description, request.style, company_data)
        return {"image": response}
    except Exception as e:
        logger.error(f"Error generating marketing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/marketing/generate-content")
async def generate_marketing_content(request: GenerateContentRequest):
    """Generate marketing content."""
    try:
        agent = get_marketing_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        context = company_data or request.context or {}
        
        if request.content_type == "instagram":
            response = agent.generate_instagram_content(context)
        elif request.content_type == "linkedin":
            response = agent.generate_linkedin_content(context)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown content type: {request.content_type}")
        
        return {"content": response, "type": request.content_type}
    except Exception as e:
        logger.error(f"Error generating marketing content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/marketing/query")
async def marketing_query(request: QueryRequest):
    """Process a query with marketing agent."""
    try:
        agent = get_marketing_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.process_query(request.query, company_data or request.context or {})
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing marketing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Team Agent endpoints
@app.post("/api/team/analyze-needs")
async def analyze_team_needs(request: AnalyzeTeamNeedsRequest):
    """Analyze team needs."""
    try:
        agent = get_team_agent()
        company_data = load_company_data_file(request.company_id)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company data not found")
        
        team_context = request.team_context or {}
        response = agent.analyze_team_needs(company_data, team_context)
        return {"analysis": response, "company_id": request.company_id}
    except Exception as e:
        logger.error(f"Error analyzing team needs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/team/query")
async def team_query(request: QueryRequest):
    """Process a query with team agent."""
    try:
        agent = get_team_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        response = agent.process_query(request.query, company_data or request.context or {})
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing team query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Coordinator Agent endpoints
@app.post("/api/coordinator/store-company-data")
async def coordinator_store_company_data(request: CompanyDataRequest):
    """Store company data via coordinator."""
    try:
        agent = get_coordinator_agent()
        agent.store_company_data(request.company_id, request.data)
        return {"message": "Company data stored successfully", "company_id": request.company_id}
    except Exception as e:
        logger.error(f"Error storing company data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/coordinator/get-context")
async def coordinator_get_context(company_id: str, agent_name: str):
    """Get context for an agent from coordinator."""
    try:
        agent = get_coordinator_agent()
        context = agent.get_context_for_agent(company_id, agent_name)
        return {"context": context, "company_id": company_id, "agent_name": agent_name}
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/coordinator/store-generated-content")
async def coordinator_store_generated_content(company_id: str, agent_name: str, content: str):
    """Store generated content via coordinator."""
    try:
        agent = get_coordinator_agent()
        agent.store_generated_content(company_id, agent_name, content)
        return {"message": "Content stored successfully", "company_id": company_id, "agent_name": agent_name}
    except Exception as e:
        logger.error(f"Error storing generated content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Supervisor Agent endpoints
@app.post("/api/supervisor/query")
async def supervisor_query(request: QueryRequest):
    """Process a query with supervisor agent (routes to appropriate agent)."""
    try:
        supervisor = get_supervisor_agent()
        company_data = load_company_data_file(request.company_id) if request.company_id else None
        query_context = company_data or request.context or {}
        response = supervisor.process_query(request.query, query_context)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing supervisor query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

