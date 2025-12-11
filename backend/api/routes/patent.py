"""
Patent Agent Routes
"""

from fastapi import APIRouter, HTTPException, Header
from backend.models.schemas import (
    PatentAssessmentRequest, PatentAssessmentResponse,
    FilingStrategyRequest, FilingStrategyResponse, ErrorResponse
)
from backend.services import (
    get_patent_agent, validate_session, get_session, add_activity
)

router = APIRouter()


@router.post("/assess", response_model=PatentAssessmentResponse)
async def assess_patentability(
    request: PatentAssessmentRequest,
    x_session_id: str = Header(...)
):
    """
    Assess patentability of an invention
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_patent_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Patent agent not available")
    
    try:
        # Prepare invention description
        invention = request.invention_description
        if request.novelty:
            invention += f" - Novelty: {request.novelty}"
        
        context = {
            **company_data,
            "invention_description": request.invention_description,
            "novelty": request.novelty
        }
        
        result = agent.assess_patentability(invention, context)
        
        add_activity(
            x_session_id,
            "Patent Assessment",
            "Completed patentability analysis",
            "patent"
        )
        
        return PatentAssessmentResponse(
            success=True,
            assessment=result.get("response", ""),
            patentability_score=result.get("score"),
            sources=result.get("sources")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filing-strategy", response_model=FilingStrategyResponse)
async def get_filing_strategy(
    request: FilingStrategyRequest,
    x_session_id: str = Header(...)
):
    """
    Get patent filing strategy recommendations
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_patent_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Patent agent not available")
    
    try:
        context = {
            **company_data,
            "geographic_interest": request.geographic_interest,
            "budget_range": request.budget_range
        }
        
        result = agent.filing_strategy(context)
        
        add_activity(
            x_session_id,
            "Filing Strategy",
            "Generated patent filing strategy",
            "patent"
        )
        
        return FilingStrategyResponse(
            success=True,
            strategy=result.get("response", ""),
            recommended_jurisdictions=request.geographic_interest,
            estimated_cost=request.budget_range,
            sources=result.get("sources")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_patents(
    query: str,
    x_session_id: str = Header(...)
):
    """
    Search for related patents
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_patent_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Patent agent not available")
    
    try:
        result = agent.search_patents(query, company_data)
        
        add_activity(
            x_session_id,
            "Patent Search",
            f"Searched for: {query[:50]}...",
            "patent"
        )
        
        return {
            "success": True,
            "results": result.get("response", ""),
            "sources": result.get("sources", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


