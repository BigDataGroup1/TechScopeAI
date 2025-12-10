"""
FastAPI server for TechScopeAI backend.
This provides REST API endpoints for the React frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import logging
import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.pitch_agent import PitchAgent
from src.agents.competitive_agent import CompetitiveAgent
from src.agents.marketing_agent import MarketingAgent
from src.agents.policy_agent import PolicyAgent
from src.agents.patent_agent import PatentAgent
from src.agents.team_agent import TeamAgent
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.general_assistant_agent import GeneralAssistantAgent
from src.rag.embedder import Embedder
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TechScopeAI API",
    description="Multi-Agent LLM System for Technical Startups",
    version="1.0.0"
)

# CORS middleware - Get allowed origins from environment or use defaults
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instances (initialized on startup)
pitch_agent = None
competitive_agent = None
marketing_agent = None
policy_agent = None
patent_agent = None
team_agent = None
supervisor_agent = None
coordinator_agent = None
general_assistant_agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    global pitch_agent, competitive_agent, marketing_agent, policy_agent, patent_agent, team_agent
    global supervisor_agent, coordinator_agent, general_assistant_agent
    
    try:
        logger.info("Initializing agents...")
        
        # Check OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not found in environment!")
            logger.warning("Some features may not work without it.")
        
        # Initialize RAG components
        embedder = Embedder(use_openai=False)
        
        # Initialize VectorStore with embedding model (so it knows the dimension)
        # use_local=False means it will use Cloud SQL if CLOUD_SQL_PASSWORD is set
        vector_store = VectorStore(embedding_model=embedder, use_local=False)
        
        # Initialize all agents with shared retriever
        retriever = Retriever(vector_store, embedder)
        
        # Use OpenAI for production (can switch to "gemini" or "auto" for fallback)
        # "auto" will try OpenAI first, then fallback to Gemini on quota errors
        default_ai_provider = "openai"  # Using OpenAI for production deployment
        
        pitch_agent = PitchAgent(retriever, ai_provider=default_ai_provider)
        competitive_agent = CompetitiveAgent(retriever, ai_provider=default_ai_provider)
        marketing_agent = MarketingAgent(retriever, ai_provider=default_ai_provider)
        policy_agent = PolicyAgent(retriever, ai_provider=default_ai_provider)
        patent_agent = PatentAgent(retriever, ai_provider=default_ai_provider)
        team_agent = TeamAgent(retriever, ai_provider=default_ai_provider)
        
        # Initialize supervisor and coordinator agents
        supervisor_agent = SupervisorAgent(retriever, ai_provider=default_ai_provider)
        coordinator_agent = CoordinatorAgent(retriever, ai_provider=default_ai_provider)
        
        # Initialize general assistant agent (for chat)
        general_assistant_agent = GeneralAssistantAgent(retriever, ai_provider=default_ai_provider)
        
        # Register all agents with supervisor
        supervisor_agent.register_agent("pitch", pitch_agent)
        supervisor_agent.register_agent("competitive", competitive_agent)
        supervisor_agent.register_agent("marketing", marketing_agent)
        supervisor_agent.register_agent("policy", policy_agent)
        supervisor_agent.register_agent("patent", patent_agent)
        supervisor_agent.register_agent("team", team_agent)
        supervisor_agent.register_agent("coordinator", coordinator_agent)
        
        logger.info("✅ All agents initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing agents: {e}", exc_info=True)
        raise


# Pydantic models for request/response
class CompanyData(BaseModel):
    """Company data model."""
    company_id: Optional[str] = None
    basic_info: Dict[str, Any]
    problem: Optional[Dict[str, Any]] = None
    solution: Optional[Dict[str, Any]] = None
    market: Optional[Dict[str, Any]] = None
    team: Optional[Dict[str, Any]] = None
    funding: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class PitchGenerateRequest(BaseModel):
    """Request model for pitch generation."""
    company_data: Dict[str, Any]


class PitchEvaluateRequest(BaseModel):
    """Request model for pitch evaluation."""
    pitch_text: str
    company_context: Optional[Dict[str, Any]] = None


class PitchQueryRequest(BaseModel):
    """Request model for pitch query."""
    query: str
    context: Optional[Dict[str, Any]] = None


class GeneralChatRequest(BaseModel):
    """Request model for general chat."""
    query: str
    company_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ElevatorPitchRequest(BaseModel):
    """Request model for elevator pitch."""
    company_data: Dict[str, Any]
    duration_seconds: int = 60


# Company endpoints
@app.post("/api/companies/{company_id}")
async def save_company(company_id: str, company_data: CompanyData):
    """Save company data."""
    try:
        # Convert to dict
        data_dict = company_data.dict()
        data_dict["company_id"] = company_id
        
        # Save to file
        company_path = Path(f"src/data/user_companies/{company_id}.json")
        company_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(company_path, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        logger.info(f"Saved company data: {company_id}")
        return {"status": "success", "company_id": company_id, "message": "Company data saved"}
    except Exception as e:
        logger.error(f"Error saving company: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies/{company_id}")
async def get_company(company_id: str):
    """Get company data."""
    try:
        company_path = Path(f"src/data/user_companies/{company_id}.json")
        if not company_path.exists():
            raise HTTPException(status_code=404, detail="Company not found")
        
        import json
        with open(company_path, 'r') as f:
            data = json.load(f)
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/companies/{company_id}")
async def update_company(company_id: str, company_data: CompanyData):
    """Update company data."""
    try:
        # Same as save
        return await save_company(company_id, company_data)
    except Exception as e:
        logger.error(f"Error updating company: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Pitch Agent endpoints
@app.post("/api/pitch/generate")
async def generate_pitch(request: PitchGenerateRequest):
    """Generate pitch deck from company details."""
    if not pitch_agent:
        raise HTTPException(status_code=503, detail="Pitch agent not initialized")
    
    try:
        # Format company data for pitch agent
        from src.data.load_company_data import format_company_data_for_pitch
        formatted_data = format_company_data_for_pitch(request.company_data)
        
        response = pitch_agent.generate_from_details(formatted_data)
        return response
    except Exception as e:
        logger.error(f"Error generating pitch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/slides")
async def generate_slides(request: PitchGenerateRequest):
    """Generate structured slides (both PowerPoint and Gamma)."""
    if not pitch_agent:
        raise HTTPException(status_code=503, detail="Pitch agent not initialized")
    
    try:
        from src.data.load_company_data import format_company_data_for_pitch
        formatted_data = format_company_data_for_pitch(request.company_data)
        
        # Generate both PowerPoint and Gamma presentations
        response = pitch_agent.generate_slides(formatted_data, gamma_only=False)
        return response
    except Exception as e:
        logger.error(f"Error generating slides: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/gamma")
async def generate_gamma_presentation(request: PitchGenerateRequest):
    """Generate Gamma.ai presentation only."""
    if not pitch_agent:
        raise HTTPException(status_code=503, detail="Pitch agent not initialized")
    
    try:
        from src.data.load_company_data import format_company_data_for_pitch
        formatted_data = format_company_data_for_pitch(request.company_data)
        
        # Generate only Gamma presentation (skip PowerPoint)
        response = pitch_agent.generate_slides(formatted_data, gamma_only=True)
        return response
    except Exception as e:
        logger.error(f"Error generating Gamma presentation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/elevator")
async def generate_elevator_pitch(request: ElevatorPitchRequest):
    """Generate elevator pitch."""
    if not pitch_agent:
        raise HTTPException(status_code=503, detail="Pitch agent not initialized")
    
    try:
        from src.data.load_company_data import format_company_data_for_pitch
        formatted_data = format_company_data_for_pitch(request.company_data)
        
        response = pitch_agent.generate_elevator_pitch(
            formatted_data,
            duration_seconds=request.duration_seconds
        )
        return response
    except Exception as e:
        logger.error(f"Error generating elevator pitch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/evaluate")
async def evaluate_pitch(request: PitchEvaluateRequest):
    """Evaluate a pitch."""
    if not pitch_agent:
        raise HTTPException(status_code=503, detail="Pitch agent not initialized")
    
    try:
        response = pitch_agent.evaluate_pitch(
            request.pitch_text,
            company_context=request.company_context
        )
        return response
    except Exception as e:
        logger.error(f"Error evaluating pitch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pitch/query")
async def query_pitch(request: PitchQueryRequest):
    """Query the pitch agent."""
    if not pitch_agent:
        raise HTTPException(status_code=503, detail="Pitch agent not initialized")
    
    try:
        response = pitch_agent.process_query(
            request.query,
            context=request.context
        )
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Competitive Agent endpoints
@app.post("/api/competitive/analyze")
async def analyze_competitors(request: PitchGenerateRequest):
    """Analyze competitors."""
    if not competitive_agent:
        raise HTTPException(status_code=503, detail="Competitive agent not initialized")
    
    try:
        from src.data.load_company_data import format_company_data_for_pitch
        formatted_data = format_company_data_for_pitch(request.company_data)
        
        response = competitive_agent.analyze_competitors(formatted_data)
        return response
    except Exception as e:
        logger.error(f"Error analyzing competitors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pitch/download/{filename}")
async def download_ppt(filename: str):
    """Download PowerPoint file."""
    try:
        # Security: Only allow .pptx files
        if not filename.endswith('.pptx'):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Remove any path traversal attempts
        filename = os.path.basename(filename)
        
        # Look for file in exports directory (relative to project root)
        # Try both relative and absolute paths
        base_dir = Path(__file__).parent.parent.parent  # Go up to TechScopeAI root
        file_path = base_dir / "exports" / filename
        
        # Also try relative path from current working directory
        if not file_path.exists():
            file_path = Path("exports") / filename
        
        if not file_path.exists():
            logger.error(f"PPT file not found: {filename}. Searched in: {base_dir / 'exports'}, {Path('exports')}")
            raise HTTPException(
                status_code=404, 
                detail=f"File not found: {filename}. Please ensure slides were generated successfully."
            )
        
        logger.info(f"Serving PPT file: {file_path}")
        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/marketing/image/{filename}")
async def serve_marketing_image(filename: str):
    """Serve marketing images generated by Gemini."""
    try:
        # Security: Only allow image files
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Remove any path traversal attempts
        filename = os.path.basename(filename)
        
        # Look for file in gemini_images directory
        base_dir = Path(__file__).parent.parent.parent  # Go up to TechScopeAI root
        file_path = base_dir / "exports" / "gemini_images" / filename
        
        # Also try relative path
        if not file_path.exists():
            file_path = Path("exports") / "gemini_images" / filename
        
        if not file_path.exists():
            logger.error(f"Image file not found: {filename}. Searched in: {base_dir / 'exports' / 'gemini_images'}, {Path('exports') / 'gemini_images'}")
            raise HTTPException(
                status_code=404, 
                detail=f"Image not found: {filename}"
            )
        
        # Determine media type from extension
        ext = filename.lower().split('.')[-1]
        media_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        media_type = media_types.get(ext, 'image/png')
        
        logger.info(f"Serving marketing image: {file_path}")
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Marketing Agent endpoints
@app.post("/api/marketing/instagram")
async def generate_instagram_content(request: PitchGenerateRequest):
    """Generate Instagram marketing content."""
    if not marketing_agent:
        raise HTTPException(status_code=503, detail="Marketing agent not initialized")
    
    try:
        response = marketing_agent.generate_instagram_content(request.company_data)
        return response
    except Exception as e:
        logger.error(f"Error generating Instagram content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/marketing/linkedin")
async def generate_linkedin_content(request: PitchGenerateRequest):
    """Generate LinkedIn marketing content."""
    if not marketing_agent:
        raise HTTPException(status_code=503, detail="Marketing agent not initialized")
    
    try:
        response = marketing_agent.generate_linkedin_content(request.company_data)
        return response
    except Exception as e:
        logger.error(f"Error generating LinkedIn content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/marketing/strategies")
async def suggest_marketing_strategies(request: PitchGenerateRequest):
    """Suggest marketing strategies."""
    if not marketing_agent:
        raise HTTPException(status_code=503, detail="Marketing agent not initialized")
    
    try:
        response = marketing_agent.suggest_marketing_strategies(request.company_data)
        return response
    except Exception as e:
        logger.error(f"Error suggesting marketing strategies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/marketing/query")
async def query_marketing(request: PitchQueryRequest):
    """Query the marketing agent."""
    if not marketing_agent:
        raise HTTPException(status_code=503, detail="Marketing agent not initialized")
    
    try:
        response = marketing_agent.process_query(
            request.query,
            context=request.context
        )
        return response
    except Exception as e:
        logger.error(f"Error processing marketing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/marketing/generate-from-prompt")
async def generate_marketing_from_prompt(request: PitchQueryRequest):
    """Generate marketing content from a user prompt (e.g., 'generate Instagram post with image')."""
    if not marketing_agent:
        raise HTTPException(status_code=503, detail="Marketing agent not initialized")
    
    try:
        # Use company data from context if available
        company_data = request.context if request.context else {}
        
        # Generate marketing content based on the prompt
        response = marketing_agent.generate_from_prompt(
            request.query,
            company_data=company_data
        )
        return response
    except Exception as e:
        logger.error(f"Error generating marketing from prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Policy Agent endpoints
@app.post("/api/policy/privacy")
async def generate_privacy_policy(request: PitchGenerateRequest):
    """Generate privacy policy."""
    if not policy_agent:
        raise HTTPException(status_code=503, detail="Policy agent not initialized")
    
    try:
        response = policy_agent.generate_privacy_policy(request.company_data)
        return response
    except Exception as e:
        logger.error(f"Error generating privacy policy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policy/terms")
async def generate_terms_of_service(request: PitchGenerateRequest):
    """Generate Terms of Service."""
    if not policy_agent:
        raise HTTPException(status_code=503, detail="Policy agent not initialized")
    
    try:
        response = policy_agent.generate_terms_of_service(request.company_data)
        return response
    except Exception as e:
        logger.error(f"Error generating Terms of Service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policy/compliance")
async def check_compliance(request: PitchGenerateRequest):
    """Check compliance requirements."""
    if not policy_agent:
        raise HTTPException(status_code=503, detail="Policy agent not initialized")
    
    try:
        policy_type = request.company_data.get("policy_type")
        response = policy_agent.check_compliance(request.company_data, policy_type=policy_type)
        return response
    except Exception as e:
        logger.error(f"Error checking compliance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policy/hr")
async def generate_hr_policies(request: PitchGenerateRequest):
    """Generate HR policies."""
    if not policy_agent:
        raise HTTPException(status_code=503, detail="Policy agent not initialized")
    
    try:
        response = policy_agent.generate_hr_policies(request.company_data)
        return response
    except Exception as e:
        logger.error(f"Error generating HR policies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policy/query")
async def query_policy(request: PitchQueryRequest):
    """Query the policy agent."""
    if not policy_agent:
        raise HTTPException(status_code=503, detail="Policy agent not initialized")
    
    try:
        response = policy_agent.process_query(
            request.query,
            context=request.context
        )
        return response
    except Exception as e:
        logger.error(f"Error processing policy query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Patent Agent endpoints
@app.post("/api/patent/search")
async def search_patents(request: PitchQueryRequest):
    """Search for patents."""
    if not patent_agent:
        raise HTTPException(status_code=503, detail="Patent agent not initialized")
    
    try:
        company_context = request.context if request.context else {}
        response = patent_agent.search_patents(request.query, company_context=company_context)
        return response
    except Exception as e:
        logger.error(f"Error searching patents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/patent/assess")
async def assess_patentability(request: PitchGenerateRequest):
    """Assess patentability of an invention."""
    if not patent_agent:
        raise HTTPException(status_code=503, detail="Patent agent not initialized")
    
    try:
        invention_description = request.company_data.get("invention_description", "")
        if not invention_description:
            raise HTTPException(status_code=400, detail="invention_description is required")
        
        company_context = request.company_data
        response = patent_agent.assess_patentability(invention_description, company_context=company_context)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing patentability: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/patent/strategy")
async def filing_strategy(request: PitchGenerateRequest):
    """Get patent filing strategy."""
    if not patent_agent:
        raise HTTPException(status_code=503, detail="Patent agent not initialized")
    
    try:
        response = patent_agent.filing_strategy(request.company_data)
        return response
    except Exception as e:
        logger.error(f"Error generating filing strategy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/patent/prior-art")
async def prior_art_search(request: PitchQueryRequest):
    """Conduct prior art search."""
    if not patent_agent:
        raise HTTPException(status_code=503, detail="Patent agent not initialized")
    
    try:
        company_context = request.context if request.context else {}
        response = patent_agent.prior_art_search(request.query, company_context=company_context)
        return response
    except Exception as e:
        logger.error(f"Error conducting prior art search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/patent/query")
async def query_patent(request: PitchQueryRequest):
    """Query the patent agent."""
    if not patent_agent:
        raise HTTPException(status_code=503, detail="Patent agent not initialized")
    
    try:
        response = patent_agent.process_query(
            request.query,
            context=request.context
        )
        return response
    except Exception as e:
        logger.error(f"Error processing patent query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Team Agent endpoints
@app.post("/api/team/analyze")
async def analyze_team_needs(request: PitchGenerateRequest):
    """Analyze team needs and recommend roles."""
    if not team_agent:
        raise HTTPException(status_code=503, detail="Team agent not initialized")
    
    try:
        # Split company_context and team_context if provided separately
        company_context = request.company_data.get("company_context", request.company_data)
        team_context = request.company_data.get("team_context", request.company_data)
        
        response = team_agent.analyze_team_needs(company_context, team_context)
        return response
    except Exception as e:
        logger.error(f"Error analyzing team needs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/team/job-description")
async def generate_job_description(request: PitchGenerateRequest):
    """Generate job description."""
    if not team_agent:
        raise HTTPException(status_code=503, detail="Team agent not initialized")
    
    try:
        role_title = request.company_data.get("role_title")
        if not role_title:
            raise HTTPException(status_code=400, detail="role_title is required")
        
        company_context = request.company_data.get("company_context", request.company_data)
        team_context = request.company_data.get("team_context", request.company_data)
        role_details = request.company_data.get("role_details", {})
        
        response = team_agent.generate_job_description(
            role_title, 
            company_context, 
            team_context, 
            role_details
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating job description: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/team/market-data")
async def get_role_market_data(request: PitchGenerateRequest):
    """Get market data for a role."""
    if not team_agent:
        raise HTTPException(status_code=503, detail="Team agent not initialized")
    
    try:
        role_title = request.company_data.get("role_title")
        location = request.company_data.get("location", "Remote")
        industry = request.company_data.get("industry", "")
        
        if not role_title:
            raise HTTPException(status_code=400, detail="role_title is required")
        
        response = team_agent.get_role_market_data(role_title, location, industry)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/team/query")
async def query_team(request: PitchQueryRequest):
    """Query the team agent."""
    if not team_agent:
        raise HTTPException(status_code=503, detail="Team agent not initialized")
    
    try:
        response = team_agent.process_query(
            request.query,
            context=request.context
        )
        return response
    except Exception as e:
        logger.error(f"Error processing team query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# General Chat endpoint
@app.post("/api/chat")
async def general_chat(request: GeneralChatRequest):
    """
    General-purpose chat endpoint - like ChatGPT!
    Handles general conversations and questions, with smart routing to specialized agents when appropriate.
    """
    if not general_assistant_agent:
        raise HTTPException(status_code=503, detail="General assistant agent not initialized")
    
    try:
        # Prepare context
        query_context = request.context or {}
        if request.company_id:
            query_context["company_id"] = request.company_id
        
        # Store company data in coordinator if provided
        if request.context and coordinator_agent:
            company_id = request.company_id or "default"
            coordinator_agent.store_company_data(company_id, request.context)
        
        # Use general assistant agent with smart routing
        # It will handle general conversations but route to specialized agents when confidence is high
        response = general_assistant_agent.process_query(
            request.query,
            context=query_context,
            use_specialized_agents=True,  # Enable smart routing
            supervisor_agent=supervisor_agent
        )
        
        return response
    except Exception as e:
        logger.error(f"Error processing general chat query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Questionnaire endpoints
@app.get("/api/questionnaire/patent")
async def get_patent_questionnaire():
    """Get patent agent questionnaire."""
    try:
        from src.agents.patent_agent import PatentAgent
        return {"questionnaire": PatentAgent.PATENT_QUESTIONNAIRE}
    except Exception as e:
        logger.error(f"Error getting patent questionnaire: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questionnaire/marketing")
async def get_marketing_questionnaire():
    """Get marketing agent questionnaire."""
    try:
        from src.agents.marketing_agent import MarketingAgent
        return {"questionnaire": MarketingAgent.MARKETING_QUESTIONNAIRE}
    except Exception as e:
        logger.error(f"Error getting marketing questionnaire: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questionnaire/policy")
async def get_policy_questionnaire():
    """Get policy agent questionnaire."""
    try:
        from src.agents.policy_agent import PolicyAgent
        return {"questionnaire": PolicyAgent.POLICY_QUESTIONNAIRE}
    except Exception as e:
        logger.error(f"Error getting policy questionnaire: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questionnaire/team")
async def get_team_questionnaire():
    """Get team agent questionnaire."""
    try:
        from src.agents.team_agent import TeamAgent
        return {"questionnaire": TeamAgent.TEAM_QUESTIONNAIRE}
    except Exception as e:
        logger.error(f"Error getting team questionnaire: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questionnaire/job-description")
async def get_job_description_questionnaire():
    """Get job description questionnaire (role-specific)."""
    try:
        from src.agents.team_agent import TeamAgent
        # Add role_title as first field, then role-specific questions
        questionnaire = [
            {
                "id": "role_title",
                "question": "💼 What job title/role are you hiring for?",
                "type": "text",
                "required": True,
                "placeholder": "e.g., Senior Software Engineer, Product Manager, Marketing Lead..."
            }
        ] + list(TeamAgent.ROLE_SPECIFIC_QUESTIONNAIRE)
        return {"questionnaire": questionnaire}
    except Exception as e:
        logger.error(f"Error getting job description questionnaire: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "pitch_agent": pitch_agent is not None,
        "competitive_agent": competitive_agent is not None,
        "marketing_agent": marketing_agent is not None,
        "policy_agent": policy_agent is not None,
        "patent_agent": patent_agent is not None,
        "team_agent": team_agent is not None,
        "supervisor_agent": supervisor_agent is not None,
        "coordinator_agent": coordinator_agent is not None,
        "general_assistant_agent": general_assistant_agent is not None,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




