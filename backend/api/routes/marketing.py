"""
Marketing Agent Routes
"""

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
from pathlib import Path
from backend.models.schemas import (
    MarketingContentRequest, MarketingContentResponse, ErrorResponse
)
from backend.services import (
    get_marketing_agent, validate_session, get_session, add_activity
)

router = APIRouter()


@router.post("/content", response_model=MarketingContentResponse)
async def generate_marketing_content(
    request: MarketingContentRequest,
    x_session_id: str = Header(...)
):
    """
    Generate marketing content for social media
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Get company data
    session = get_session(x_session_id)
    company_data = session["company"]
    
    # Get agent
    agent = get_marketing_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Marketing agent not available")
    
    try:
        # Prepare context
        context = {
            **company_data,
            "platform": request.platform,
            "content_type": request.content_type,
            "product_description": request.description,
            "generate_image": "Yes, generate custom AI images" if request.generate_image else "No",
            "image_provider": request.image_provider
        }
        
        # Generate content based on platform
        if request.platform.lower() == "instagram":
            result = agent.generate_instagram_content(context)
        elif request.platform.lower() == "linkedin":
            result = agent.generate_linkedin_content(context)
        else:
            result = agent.suggest_marketing_strategies(context)
        
        # Add activity
        add_activity(
            x_session_id,
            f"{request.platform} Content",
            f"Generated {request.content_type} content",
            "marketing"
        )
        
        return MarketingContentResponse(
            success=True,
            content=result.get("response", ""),
            platform=request.platform,
            hashtags=result.get("hashtags"),
            image_path=result.get("image_path"),
            image_url=result.get("image_url"),
            sources=result.get("sources")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image")
async def get_marketing_image(path: str, x_session_id: str = Header(...)):
    """
    Serve generated marketing images stored in exports/.
    Accepts a relative path like 'exports/gemini_images/abc.png'.
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        # Normalize path to prevent directory traversal
        rel_path = path.lstrip("/\\")
        file_path = Path(rel_path)
        # Resolve to absolute path
        abs_path = (Path.cwd() / file_path).resolve()
        exports_dir = (Path.cwd() / "exports").resolve()
        if exports_dir not in abs_path.parents and abs_path != exports_dir:
            raise HTTPException(status_code=400, detail="Invalid path")
        if not abs_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=str(abs_path),
            filename=abs_path.name,
            media_type="image/png"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies")
async def get_marketing_strategies(
    x_session_id: str = Header(...)
):
    """
    Get marketing strategy recommendations
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session = get_session(x_session_id)
    company_data = session["company"]
    
    agent = get_marketing_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Marketing agent not available")
    
    try:
        result = agent.suggest_marketing_strategies(company_data)
        
        add_activity(
            x_session_id,
            "Marketing Strategies",
            "Generated strategy recommendations",
            "marketing"
        )
        
        return {
            "success": True,
            "strategies": result.get("response", ""),
            "sources": result.get("sources", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




