"""
AI Chat Assistant Routes
"""

from fastapi import APIRouter, HTTPException, Header
from backend.models.schemas import (
    ChatRequest, ChatResponse, ChatMessage, ErrorResponse
)
from backend.services import (
    get_supervisor_agent, validate_session, get_session, add_activity
)

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    x_session_id: str = Header(...)
):
    """
    Send a message to the AI assistant
    The supervisor agent will route to the appropriate specialized agent
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    # Get supervisor agent
    supervisor = get_supervisor_agent()
    if not supervisor:
        raise HTTPException(status_code=500, detail="AI assistant not available")
    
    try:
        # Process query through supervisor
        result = supervisor.process_query(request.message, company_data)
        
        # Add activity
        add_activity(
            x_session_id,
            "AI Chat",
            f"Asked: {request.message[:50]}...",
            "chat"
        )
        
        return ChatResponse(
            success=True,
            response=result.get("response", "I couldn't process that request."),
            routed_to=result.get("routed_to"),
            sources=result.get("sources")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_specific_agent(
    agent_name: str,
    query: str,
    x_session_id: str = Header(...)
):
    """
    Query a specific agent directly
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    # Get the specific agent
    from backend.services import (
        get_pitch_agent, get_marketing_agent, get_patent_agent,
        get_policy_agent, get_team_agent, get_competitive_agent
    )
    
    agents = {
        "pitch": get_pitch_agent,
        "marketing": get_marketing_agent,
        "patent": get_patent_agent,
        "policy": get_policy_agent,
        "team": get_team_agent,
        "competitive": get_competitive_agent
    }
    
    if agent_name not in agents:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {agent_name}")
    
    agent = agents[agent_name]()
    if not agent:
        raise HTTPException(status_code=500, detail=f"{agent_name} agent not available")
    
    try:
        result = agent.process_query(query, company_data)
        
        add_activity(
            x_session_id,
            f"{agent_name.title()} Query",
            f"Asked: {query[:50]}...",
            agent_name
        )
        
        return {
            "success": True,
            "agent": agent_name,
            "response": result.get("response", ""),
            "sources": result.get("sources", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




