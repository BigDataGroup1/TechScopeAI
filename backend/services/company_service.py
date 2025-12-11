"""
Company Service - Manages company data storage and retrieval
"""

import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Storage path for company data
COMPANIES_PATH = Path(__file__).parent.parent.parent / "src" / "data" / "user_companies"
COMPANIES_PATH.mkdir(parents=True, exist_ok=True)

# In-memory session store (for demo - use Redis/DB in production)
_sessions: Dict[str, Dict[str, Any]] = {}


def create_company(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new company and return session info
    """
    # Generate IDs
    company_id = f"{data['company_name'].lower().replace(' ', '_')[:20]}_{uuid.uuid4().hex[:8]}"
    session_id = uuid.uuid4().hex
    
    # Create company record
    company = {
        "id": company_id,
        "company_name": data["company_name"],
        "industry": data["industry"],
        "problem": data["problem"],
        "solution": data["solution"],
        "target_market": data.get("target_market"),
        "current_stage": data.get("current_stage", "Pre-Seed"),
        "traction": data.get("traction"),
        "funding_goal": data.get("funding_goal"),
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Save to file
    company_file = COMPANIES_PATH / f"{company_id}.json"
    with open(company_file, 'w') as f:
        json.dump(company, f, indent=2)
    
    # Create session
    _sessions[session_id] = {
        "company_id": company_id,
        "company": company,
        "activities": [],
        "created_at": datetime.utcnow().isoformat()
    }
    
    logger.info(f"✅ Created company: {company['company_name']} ({company_id})")
    
    return {
        "session_id": session_id,
        "company": company
    }


def get_company(company_id: str) -> Optional[Dict[str, Any]]:
    """
    Get company by ID
    """
    company_file = COMPANIES_PATH / f"{company_id}.json"
    
    if company_file.exists():
        with open(company_file, 'r') as f:
            return json.load(f)
    
    return None


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get session by ID
    """
    return _sessions.get(session_id)


def get_company_from_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get company data from session
    """
    session = get_session(session_id)
    if session:
        return session.get("company")
    return None


def add_activity(session_id: str, title: str, description: str, activity_type: str) -> Optional[Dict[str, Any]]:
    """
    Add an activity to the session
    """
    session = _sessions.get(session_id)
    if not session:
        return None
    
    activity = {
        "id": uuid.uuid4().hex,
        "title": title,
        "description": description,
        "type": activity_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Insert at beginning (newest first)
    session["activities"].insert(0, activity)
    
    # Keep only last 50 activities
    session["activities"] = session["activities"][:50]
    
    return activity


def get_activities(session_id: str, limit: int = 20) -> list:
    """
    Get activities for a session
    """
    session = _sessions.get(session_id)
    if not session:
        return []
    
    return session.get("activities", [])[:limit]


def validate_session(session_id: str) -> bool:
    """
    Check if session is valid
    """
    return session_id in _sessions


def delete_session(session_id: str) -> bool:
    """
    Delete/logout session
    """
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False




