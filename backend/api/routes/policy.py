"""
Policy Agent Routes
"""

from fastapi import APIRouter, HTTPException, Header
from backend.models.schemas import (
    PolicyRequest, PolicyResponse, ErrorResponse
)
from backend.services import (
    get_policy_agent, validate_session, get_session, add_activity
)

router = APIRouter()


@router.post("/generate", response_model=PolicyResponse)
async def generate_policy(
    request: PolicyRequest,
    x_session_id: str = Header(...)
):
    """
    Generate legal policies (Privacy Policy, Terms of Service)
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_policy_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Policy agent not available")
    
    try:
        context = {
            **company_data,
            "additional_requirements": request.additional_requirements
        }
        
        # Normalize policy type (UI may send lowercase ids)
        pt_raw = request.policy_type or ""
        pt = pt_raw.lower().strip()

        # Generate based on policy type
        if pt in ("privacy policy", "privacy"):
            result = agent.generate_privacy_policy(context)
        elif pt in ("terms of service", "terms"):
            result = agent.generate_terms_of_service(context)
        elif pt in ("both", "privacy+terms"):
            pp_result = agent.generate_privacy_policy(context)
            tos_result = agent.generate_terms_of_service(context)
            result = {
                "response": f"# Privacy Policy\n\n{pp_result.get('response', '')}\n\n---\n\n# Terms of Service\n\n{tos_result.get('response', '')}",
                "sources": (pp_result.get("sources", []) or []) + (tos_result.get("sources", []) or [])
            }
        else:
            # For unsupported types (e.g., cookies/refund/HR), provide a generic policy doc via process_query
            query = f"Generate a comprehensive {pt_raw or 'policy'} for this company with additional requirements: {request.additional_requirements or 'N/A'}"
            result = agent.process_query(query, context)
        
        add_activity(
            x_session_id,
            pt_raw or "Policy",
            "Generated policy document",
            "policy"
        )
        
        return PolicyResponse(
            success=True,
            policy_type=pt_raw or "Policy",
            content=result.get("response", ""),
            sources=result.get("sources")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance")
async def check_compliance(
    x_session_id: str = Header(...)
):
    """
    Check compliance requirements for the company
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_policy_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Policy agent not available")
    
    try:
        result = agent.check_compliance(company_data)
        
        add_activity(
            x_session_id,
            "Compliance Check",
            "Analyzed compliance requirements",
            "policy"
        )
        
        return {
            "success": True,
            "compliance_report": result.get("response", ""),
            "sources": result.get("sources", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




