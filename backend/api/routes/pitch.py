"""
Pitch Agent Routes
"""

from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from backend.models.schemas import (
    PitchDeckRequest, PitchDeckResponse, SlideData, GammaPresentation,
    ElevatorPitchRequest, ElevatorPitchResponse, ErrorResponse
)
from backend.services import (
    get_pitch_agent, get_company, validate_session,
    get_session, add_activity
)

router = APIRouter()


@router.post("/deck", response_model=PitchDeckResponse)
async def generate_pitch_deck(
    request: PitchDeckRequest,
    x_session_id: str = Header(...)
):
    """
    Generate a complete pitch deck
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Get company data
    session = get_session(x_session_id)
    company_data = session["company"]
    
    # Get agent
    agent = get_pitch_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Pitch agent not available")
    
    try:
        # Add AI provider to company data
        enhanced_data = {
            **company_data,
            "enhance_with_ai": request.enhance_with_ai,
            "ai_provider": request.ai_provider
        }
        
        # Generate slides (pass gamma_only parameter)
        result = agent.generate_slides(enhanced_data, gamma_only=request.gamma_only)
        
        # Add activity
        add_activity(
            x_session_id,
            "Pitch Deck Generated",
            f"Created {result.get('total_slides', 0)} slides",
            "pitch"
        )
        
        # Format response
        slides = [
            SlideData(
                slide_number=s.get("slide_number", i+1),
                title=s.get("title", ""),
                content=s.get("content", ""),
                key_points=s.get("key_points"),
                image_path=s.get("image_path")
            )
            for i, s in enumerate(result.get("slides", []))
        ]
        
        # Parse gamma presentation result if available
        gamma_data = result.get("gamma_presentation")
        gamma_presentation = None
        if gamma_data:
            gamma_presentation = GammaPresentation(
                success=gamma_data.get("success", False),
                presentation_url=gamma_data.get("presentation_url"),
                generation_id=gamma_data.get("generation_id"),
                error=gamma_data.get("error"),
                message=gamma_data.get("message")
            )
        
        return PitchDeckResponse(
            success=True,
            total_slides=result.get("total_slides", len(slides)),
            slides=slides,
            pptx_path=result.get("pptx_path"),
            gamma_presentation=gamma_presentation,
            message="Pitch deck generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/elevator", response_model=ElevatorPitchResponse)
async def generate_elevator_pitch(
    request: ElevatorPitchRequest,
    x_session_id: str = Header(...)
):
    """
    Generate an elevator pitch
    """
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Get company data
    session = get_session(x_session_id)
    company_data = session["company"]
    
    # Get agent
    agent = get_pitch_agent()
    if not agent:
        raise HTTPException(status_code=500, detail="Pitch agent not available")
    
    try:
        result = agent.generate_elevator_pitch(
            company_data,
            duration_seconds=request.duration_seconds
        )
        
        # Add activity
        add_activity(
            x_session_id,
            "Elevator Pitch Generated",
            f"{request.duration_seconds}-second pitch created",
            "pitch"
        )
        
        return ElevatorPitchResponse(
            success=True,
            elevator_pitch=result.get("elevator_pitch", ""),
            duration_seconds=result.get("duration_seconds", request.duration_seconds),
            estimated_words=result.get("estimated_words", 0),
            company_name=company_data["company_name"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_pitch_deck(filename: str, x_session_id: str = Header(...)):
    """
    Download generated pitch deck file
    """
    from fastapi.responses import FileResponse
    from pathlib import Path
    
    if not validate_session(x_session_id):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    file_path = Path("exports") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

