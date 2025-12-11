"""
Competitive Agent Routes
"""

from fastapi import APIRouter, HTTPException, Header
from backend.models.schemas import (
    CompetitiveAnalysisRequest, CompetitiveAnalysisResponse, ErrorResponse
)
from backend.services import (
    get_competitive_agent, validate_session, get_session, add_activity
)

router = APIRouter()


@router.post("/analyze", response_model=CompetitiveAnalysisResponse)
async def analyze_competitors(
    request: CompetitiveAnalysisRequest,
    x_session_id: str = Header(...)
):
    """
    Perform competitive analysis
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_competitive_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Competitive agent not available")
    
    try:
        result = agent.analyze_competitors(
            company_details=company_data,
            competitors=request.specific_competitors
        )
        
        add_activity(
            x_session_id,
            "Competitive Analysis",
            "Completed market analysis",
            "competitive"
        )
        
        return CompetitiveAnalysisResponse(
            success=True,
            analysis=result.get("response", ""),
            competitors_found=request.specific_competitors,
            sources=result.get("sources")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-overview")
async def get_market_overview(
    x_session_id: str = Header(...)
):
    """
    Get market overview for the company's industry
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_competitive_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Competitive agent not available")
    
    try:
        query = f"What is the market overview and trends for {company_data['industry']} industry?"
        result = agent.process_query(query, company_data)
        
        add_activity(
            x_session_id,
            "Market Overview",
            f"Analyzed {company_data['industry']} market",
            "competitive"
        )
        
        return {
            "success": True,
            "overview": result.get("response", ""),
            "industry": company_data["industry"],
            "sources": result.get("sources", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


