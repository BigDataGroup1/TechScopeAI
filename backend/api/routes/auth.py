"""
Authentication & Company Registration Routes
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from backend.models.schemas import (
    CompanyCreate, CompanyResponse, SessionResponse, 
    ActivityList, Activity, ErrorResponse
)
from backend.services import (
    create_company, get_company, get_session,
    get_activities, validate_session, delete_session, add_activity
)
from datetime import datetime

router = APIRouter()


@router.post("/register", response_model=SessionResponse)
async def register_company(company: CompanyCreate):
    """
    Register a new company and create a session
    """
    try:
        result = create_company(company.model_dump())
        
        return SessionResponse(
            session_id=result["session_id"],
            company=CompanyResponse(
                id=result["company"]["id"],
                company_name=result["company"]["company_name"],
                industry=result["company"]["industry"],
                problem=result["company"]["problem"],
                solution=result["company"]["solution"],
                target_market=result["company"].get("target_market"),
                current_stage=result["company"]["current_stage"],
                traction=result["company"].get("traction"),
                funding_goal=result["company"].get("funding_goal"),
                created_at=datetime.fromisoformat(result["company"]["created_at"])
            ),
            message="Company registered successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session", response_model=SessionResponse)
async def get_current_session(x_session_id: str = Header(...)):
    """
    Get current session info
    """
    session = get_session(x_session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    company = session["company"]
    return SessionResponse(
        session_id=x_session_id,
        company=CompanyResponse(
            id=company["id"],
            company_name=company["company_name"],
            industry=company["industry"],
            problem=company["problem"],
            solution=company["solution"],
            target_market=company.get("target_market"),
            current_stage=company["current_stage"],
            traction=company.get("traction"),
            funding_goal=company.get("funding_goal"),
            created_at=datetime.fromisoformat(company["created_at"])
        ),
        message="Session valid"
    )


@router.post("/logout")
async def logout(x_session_id: str = Header(...)):
    """
    Logout and delete session
    """
    if delete_session(x_session_id):
        return {"success": True, "message": "Logged out successfully"}
    raise HTTPException(status_code=401, detail="Invalid session")


@router.get("/activities", response_model=ActivityList)
async def get_session_activities(
    x_session_id: str = Header(...),
    limit: int = 20
):
    """
    Get activities for current session
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    activities = get_activities(x_session_id, limit)
    
    return ActivityList(
        activities=[
            Activity(
                id=a["id"],
                title=a["title"],
                description=a["description"],
                timestamp=datetime.fromisoformat(a["timestamp"]),
                type=a["type"]
            )
            for a in activities
        ],
        total=len(activities)
    )


