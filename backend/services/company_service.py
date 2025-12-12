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
    session_data = {
        "company_id": company_id,
        "company": company,
        "activities": [],
        "created_at": datetime.utcnow().isoformat()
    }
    _sessions[session_id] = session_data
    
    # Save session to file for Cloud Run stateless recovery
    session_file = COMPANIES_PATH / f"session_{session_id}.json"
    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save session file: {e}")
    
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
    Get session by ID.
    For Cloud Run stateless deployments, also check session file if not in memory.
    """
    # Check in-memory first
    if session_id in _sessions:
        return _sessions[session_id]
    
    # Try to recover session from file (for stateless Cloud Run)
    session_file = COMPANIES_PATH / f"session_{session_id}.json"
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                # Restore to memory
                _sessions[session_id] = session_data
                logger.info(f"✅ Restored session from file: {session_id[:8]}...")
                return session_data
        except Exception as e:
            logger.warning(f"Failed to restore session: {e}")
    
    return None


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
    # Use get_session to load from file if needed
    session = get_session(session_id)
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
    
    # Persist session to file for Cloud Run stateless recovery
    session_file = COMPANIES_PATH / f"session_{session_id}.json"
    try:
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to persist session activity: {e}")
    
    return activity


def get_activities(session_id: str, limit: int = 20) -> list:
    """
    Get activities for a session
    """
    # Use get_session to load from file if needed
    session = get_session(session_id)
    if not session:
        return []
    
    return session.get("activities", [])[:limit]


def validate_session(session_id: str) -> bool:
    """
    Check if session is valid (also checks file for Cloud Run stateless recovery)
    """
    if session_id in _sessions:
        return True
    # Try to recover from file
    session = get_session(session_id)
    return session is not None


def delete_session(session_id: str) -> bool:
    """
    Delete/logout session (both in-memory and file)
    """
    deleted = False
    
    # Delete from memory
    if session_id in _sessions:
        del _sessions[session_id]
        deleted = True
    
    # Delete session file for Cloud Run
    session_file = COMPANIES_PATH / f"session_{session_id}.json"
    if session_file.exists():
        try:
            session_file.unlink()
            deleted = True
        except Exception as e:
            logger.warning(f"Failed to delete session file: {e}")
    
    return deleted




