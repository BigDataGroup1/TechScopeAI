"""
User Choices Management - Human-in-the-Loop (HITL) choice selection and storage.

This module handles presenting choices to users and storing their selections
for later reporting and analysis.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class UserChoiceManager:
    """Manages user choices for HITL interactions."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize UserChoiceManager.
        
        Args:
            storage_dir: Directory to store choice data. Defaults to data/user_choices.
        """
        if storage_dir is None:
            storage_dir = Path("data/user_choices")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"UserChoiceManager initialized with storage: {self.storage_dir}")
    
    def get_choices_for_action(self, agent_name: str, action: str) -> List[Dict[str, Any]]:
        """
        Get available choices for a specific agent action.
        
        Args:
            agent_name: Name of the agent (e.g., "pitch", "marketing")
            action: Action name (e.g., "generate_slides", "generate_content")
            
        Returns:
            List of choice dictionaries with id, label, description, etc.
        """
        # Define choices for each agent-action combination
        choices_config = {
            "pitch": {
                "generate_slides": [
                    {
                        "id": "normal_ppt",
                        "label": "📊 Normal PowerPoint",
                        "description": "Generate a standard PowerPoint presentation (.pptx file)",
                        "icon": "📊",
                        "value": {"format": "pptx", "gamma": False}
                    },
                    {
                        "id": "gamma_ppt",
                        "label": "🎨 Gamma.ai Presentation",
                        "description": "Generate an interactive Gamma.ai presentation with modern design",
                        "icon": "🎨",
                        "value": {"format": "gamma", "gamma": True}
                    }
                ],
                "generate_pitch": [
                    {
                        "id": "text_only",
                        "label": "📝 Text Only",
                        "description": "Generate pitch text without slides",
                        "icon": "📝",
                        "value": {"format": "text"}
                    },
                    {
                        "id": "with_slides",
                        "label": "📊 With Slides",
                        "description": "Generate pitch text along with slide structure",
                        "icon": "📊",
                        "value": {"format": "slides"}
                    }
                ]
            },
            "marketing": {
                "generate_content": [
                    {
                        "id": "instagram",
                        "label": "📷 Instagram Content",
                        "description": "Generate Instagram posts, stories, and reels",
                        "icon": "📷",
                        "value": {"platform": "instagram"}
                    },
                    {
                        "id": "linkedin",
                        "label": "💼 LinkedIn Content",
                        "description": "Generate LinkedIn posts and articles",
                        "icon": "💼",
                        "value": {"platform": "linkedin"}
                    },
                    {
                        "id": "both",
                        "label": "📱 Both Platforms",
                        "description": "Generate content for both Instagram and LinkedIn",
                        "icon": "📱",
                        "value": {"platform": "both"}
                    }
                ],
                "generate_image": [
                    {
                        "id": "ai_generated",
                        "label": "🤖 AI Generated",
                        "description": "Generate custom AI images",
                        "icon": "🤖",
                        "value": {"image_type": "ai"}
                    },
                    {
                        "id": "stock_images",
                        "label": "🖼️ Stock Images",
                        "description": "Use free stock images",
                        "icon": "🖼️",
                        "value": {"image_type": "stock"}
                    },
                    {
                        "id": "text_only",
                        "label": "📝 Text Only",
                        "description": "No images, just text content",
                        "icon": "📝",
                        "value": {"image_type": "none"}
                    }
                ]
            },
            "team": {
                "generate_job_description": [
                    {
                        "id": "detailed",
                        "label": "📋 Detailed JD",
                        "description": "Comprehensive job description with all sections",
                        "icon": "📋",
                        "value": {"detail_level": "detailed"}
                    },
                    {
                        "id": "concise",
                        "label": "📄 Concise JD",
                        "description": "Brief job description for quick posting",
                        "icon": "📄",
                        "value": {"detail_level": "concise"}
                    }
                ]
            },
            "policy": {
                "generate_policy": [
                    {
                        "id": "privacy_only",
                        "label": "🔒 Privacy Policy",
                        "description": "Generate privacy policy only",
                        "icon": "🔒",
                        "value": {"policy_type": "privacy"}
                    },
                    {
                        "id": "terms_only",
                        "label": "📜 Terms of Service",
                        "description": "Generate terms of service only",
                        "icon": "📜",
                        "value": {"policy_type": "terms"}
                    },
                    {
                        "id": "both",
                        "label": "📚 Both Policies",
                        "description": "Generate both privacy policy and terms of service",
                        "icon": "📚",
                        "value": {"policy_type": "both"}
                    }
                ]
            },
            "patent": {
                "analyze_patentability": [
                    {
                        "id": "quick_analysis",
                        "label": "⚡ Quick Analysis",
                        "description": "Fast preliminary patentability check",
                        "icon": "⚡",
                        "value": {"analysis_depth": "quick"}
                    },
                    {
                        "id": "detailed_analysis",
                        "label": "🔍 Detailed Analysis",
                        "description": "Comprehensive patentability analysis with prior art search",
                        "icon": "🔍",
                        "value": {"analysis_depth": "detailed"}
                    }
                ]
            },
            "competitive": {
                "analyze_competitors": [
                    {
                        "id": "basic",
                        "label": "📊 Basic Analysis",
                        "description": "Basic competitor overview",
                        "icon": "📊",
                        "value": {"analysis_level": "basic"}
                    },
                    {
                        "id": "comprehensive",
                        "label": "🔍 Comprehensive Analysis",
                        "description": "Detailed competitive analysis with market positioning",
                        "icon": "🔍",
                        "value": {"analysis_level": "comprehensive"}
                    }
                ]
            }
        }
        
        # Get choices for this agent-action combination
        agent_choices = choices_config.get(agent_name, {})
        choices = agent_choices.get(action, [])
        
        # If no specific choices found, return default single choice
        if not choices:
            logger.warning(f"No choices configured for {agent_name}.{action}, using default")
            return [{
                "id": "default",
                "label": "✅ Proceed",
                "description": "Continue with default options",
                "icon": "✅",
                "value": {}
            }]
        
        return choices
    
    def save_choice(self, user_id: str, company_id: str, agent_name: str, 
                    action: str, choice_id: str, choice_data: Dict[str, Any],
                    context: Optional[Dict[str, Any]] = None) -> None:
        """
        Save a user choice.
        
        Args:
            user_id: User identifier (can be session_id for anonymous users)
            company_id: Company identifier
            agent_name: Name of the agent
            action: Action name
            choice_id: ID of the selected choice
            choice_data: Full choice data including value
            context: Optional context about when/why choice was made
        """
        choice_record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "company_id": company_id,
            "agent_name": agent_name,
            "action": action,
            "choice_id": choice_id,
            "choice_label": choice_data.get("label", ""),
            "choice_value": choice_data.get("value", {}),
            "context": context or {}
        }
        
        # Load existing choices
        choices_file = self.storage_dir / f"{user_id}_{company_id}.json"
        choices = []
        
        if choices_file.exists():
            try:
                with open(choices_file, 'r') as f:
                    choices = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading existing choices: {e}")
                choices = []
        
        # Append new choice
        choices.append(choice_record)
        
        # Save back to file
        try:
            with open(choices_file, 'w') as f:
                json.dump(choices, f, indent=2)
            logger.info(f"Saved choice: {agent_name}.{action} -> {choice_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving choice: {e}")
    
    def get_user_choices(self, user_id: str, company_id: str, 
                        agent_name: Optional[str] = None,
                        action: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all choices made by a user.
        
        Args:
            user_id: User identifier
            company_id: Company identifier
            agent_name: Optional filter by agent name
            action: Optional filter by action name
            
        Returns:
            List of choice records
        """
        choices_file = self.storage_dir / f"{user_id}_{company_id}.json"
        
        if not choices_file.exists():
            return []
        
        try:
            with open(choices_file, 'r') as f:
                choices = json.load(f)
            
            # Apply filters
            if agent_name:
                choices = [c for c in choices if c.get("agent_name") == agent_name]
            if action:
                choices = [c for c in choices if c.get("action") == action]
            
            return choices
        except Exception as e:
            logger.error(f"Error loading user choices: {e}")
            return []
    
    def get_choice_summary(self, user_id: str, company_id: str) -> Dict[str, Any]:
        """
        Get a summary of all choices made by a user.
        
        Args:
            user_id: User identifier
            company_id: Company identifier
            
        Returns:
            Summary dictionary with counts and breakdowns
        """
        choices = self.get_user_choices(user_id, company_id)
        
        if not choices:
            return {
                "total_choices": 0,
                "by_agent": {},
                "by_action": {},
                "recent_choices": []
            }
        
        # Count by agent
        by_agent = {}
        by_action = {}
        
        for choice in choices:
            agent = choice.get("agent_name", "unknown")
            action = choice.get("action", "unknown")
            
            by_agent[agent] = by_agent.get(agent, 0) + 1
            by_action[action] = by_action.get(action, 0) + 1
        
        return {
            "total_choices": len(choices),
            "by_agent": by_agent,
            "by_action": by_action,
            "recent_choices": choices[-10:]  # Last 10 choices
        }

