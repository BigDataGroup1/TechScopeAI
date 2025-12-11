"""
Team Agent Routes
"""

from fastapi import APIRouter, HTTPException, Header
from backend.models.schemas import (
    TeamAnalysisRequest, TeamAnalysisResponse,
    JobDescriptionRequest, JobDescriptionResponse, ErrorResponse
)
from backend.services import (
    get_team_agent, validate_session, get_session, add_activity
)

router = APIRouter()


@router.post("/analyze", response_model=TeamAnalysisResponse)
async def analyze_team_needs(
    request: TeamAnalysisRequest,
    x_session_id: str = Header(...)
):
    """
    Analyze team needs and get hiring recommendations
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_team_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Team agent not available")
    
    try:
        context = {
            **company_data,
            "current_team": request.current_team,
            "challenges": request.challenges
        }
        
        result = agent.analyze_team_needs(
            company_context=context,
            team_context=context
        )
        
        add_activity(
            x_session_id,
            "Team Analysis",
            "Completed hiring recommendations",
            "team"
        )
        
        return TeamAnalysisResponse(
            success=True,
            analysis=result.get("response", ""),
            recommended_roles=result.get("recommended_roles"),
            sources=result.get("sources")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/job-description", response_model=JobDescriptionResponse)
async def generate_job_description(
    request: JobDescriptionRequest,
    x_session_id: str = Header(...)
):
    """
    Generate a job description for a role
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_team_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Team agent not available")
    
    try:
        context = {
            **company_data,
            "role_title": request.role_title,
            "role_type": request.role_type,
            "experience_level": request.experience_level,
            "responsibilities": request.responsibilities,
            "required_skills": request.required_skills
        }
        
        result = agent.generate_job_description(context)
        
        add_activity(
            x_session_id,
            "Job Description",
            f"Generated JD for {request.role_title}",
            "team"
        )
        
        return JobDescriptionResponse(
            success=True,
            job_description=result.get("response", ""),
            role_title=request.role_title,
            sources=result.get("sources")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


