"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# COMPANY & AUTH SCHEMAS
# ============================================

class CompanyCreate(BaseModel):
    """Schema for creating/registering a company"""
    company_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    problem: str = Field(..., min_length=10)
    solution: str = Field(..., min_length=10)
    target_market: Optional[str] = None
    current_stage: str = Field(default="Pre-Seed")
    traction: Optional[str] = None
    funding_goal: Optional[str] = None


class CompanyResponse(BaseModel):
    """Schema for company response"""
    id: str
    company_name: str
    industry: str
    problem: str
    solution: str
    target_market: Optional[str]
    current_stage: str
    traction: Optional[str]
    funding_goal: Optional[str]
    created_at: datetime


class SessionResponse(BaseModel):
    """Schema for session/auth response"""
    session_id: str
    company: CompanyResponse
    message: str


# ============================================
# ACTIVITY SCHEMAS
# ============================================

class Activity(BaseModel):
    """Schema for activity items"""
    id: str
    title: str
    description: str
    timestamp: datetime
    type: str  # pitch, marketing, patent, etc.


class ActivityList(BaseModel):
    """Schema for list of activities"""
    activities: List[Activity]
    total: int


# ============================================
# PITCH AGENT SCHEMAS
# ============================================

class PitchDeckRequest(BaseModel):
    """Request schema for pitch deck generation"""
    company_id: str
    enhance_with_ai: bool = True
    ai_provider: str = "auto"  # auto, openai, gemini
    gamma_only: bool = False  # If True, only generate Gamma presentation (skip PPTX)


class SlideData(BaseModel):
    """Schema for a single slide"""
    slide_number: int
    title: str
    content: str
    key_points: Optional[List[str]] = None
    image_path: Optional[str] = None


class GammaPresentation(BaseModel):
    """Schema for Gamma.ai presentation result"""
    success: bool
    presentation_url: Optional[str] = None
    generation_id: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None

class PitchDeckResponse(BaseModel):
    """Response schema for pitch deck"""
    success: bool
    total_slides: int
    slides: List[SlideData]
    pptx_path: Optional[str] = None
    gamma_presentation: Optional[GammaPresentation] = None
    message: Optional[str] = None


class ElevatorPitchRequest(BaseModel):
    """Request schema for elevator pitch"""
    company_id: str
    duration_seconds: int = 60


class ElevatorPitchResponse(BaseModel):
    """Response schema for elevator pitch"""
    success: bool
    elevator_pitch: str
    duration_seconds: int
    estimated_words: int
    company_name: str


# ============================================
# MARKETING AGENT SCHEMAS
# ============================================

class MarketingContentRequest(BaseModel):
    """Request schema for marketing content"""
    company_id: str
    platform: str = "Instagram"  # Instagram, LinkedIn, Both
    content_type: str = "Product Launch"
    description: str
    generate_image: bool = True
    image_provider: str = "dalle"  # dalle, gemini


class MarketingContentResponse(BaseModel):
    """Response schema for marketing content"""
    success: bool
    content: str
    platform: str
    hashtags: Optional[List[str]] = None
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None


# ============================================
# PATENT AGENT SCHEMAS
# ============================================

class PatentAssessmentRequest(BaseModel):
    """Request schema for patent assessment"""
    company_id: str
    invention_description: str
    novelty: Optional[str] = None


class PatentAssessmentResponse(BaseModel):
    """Response schema for patent assessment"""
    success: bool
    assessment: str
    patentability_score: Optional[float] = None
    sources: Optional[List[Dict[str, Any]]] = None


class FilingStrategyRequest(BaseModel):
    """Request schema for filing strategy"""
    company_id: str
    geographic_interest: List[str] = ["United States"]
    budget_range: str = "$15K - $30K"


class FilingStrategyResponse(BaseModel):
    """Response schema for filing strategy"""
    success: bool
    strategy: str
    recommended_jurisdictions: Optional[List[str]] = None
    estimated_cost: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None


# ============================================
# POLICY AGENT SCHEMAS
# ============================================

class PolicyRequest(BaseModel):
    """Request schema for policy generation"""
    company_id: str
    policy_type: str = "Privacy Policy"  # Privacy Policy, Terms of Service, Both
    additional_requirements: Optional[str] = None


class PolicyResponse(BaseModel):
    """Response schema for policy generation"""
    success: bool
    policy_type: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None


# ============================================
# TEAM AGENT SCHEMAS
# ============================================

class TeamAnalysisRequest(BaseModel):
    """Request schema for team analysis"""
    company_id: str
    current_team: Optional[str] = None
    challenges: Optional[str] = None


class TeamAnalysisResponse(BaseModel):
    """Response schema for team analysis"""
    success: bool
    analysis: str
    recommended_roles: Optional[List[str]] = None
    sources: Optional[List[Dict[str, Any]]] = None


class JobDescriptionRequest(BaseModel):
    """Request schema for job description"""
    company_id: str
    role_title: str
    role_type: str = "Full-time"
    experience_level: str = "Mid Level"
    responsibilities: Optional[str] = None
    required_skills: Optional[str] = None


class JobDescriptionResponse(BaseModel):
    """Response schema for job description"""
    success: bool
    job_description: str
    role_title: str
    sources: Optional[List[Dict[str, Any]]] = None


# ============================================
# COMPETITIVE AGENT SCHEMAS
# ============================================

class CompetitiveAnalysisRequest(BaseModel):
    """Request schema for competitive analysis"""
    company_id: str
    specific_competitors: Optional[List[str]] = None


class CompetitiveAnalysisResponse(BaseModel):
    """Response schema for competitive analysis"""
    success: bool
    analysis: str
    competitors_found: Optional[List[str]] = None
    sources: Optional[List[Dict[str, Any]]] = None


# ============================================
# CHAT AGENT SCHEMAS
# ============================================

class ChatMessage(BaseModel):
    """Schema for a chat message"""
    role: str  # user, assistant
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request schema for chat"""
    company_id: str
    message: str
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    """Response schema for chat"""
    success: bool
    response: str
    routed_to: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None


# ============================================
# GENERIC RESPONSE
# ============================================

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    success: bool = False
    error: str
    detail: Optional[str] = None

