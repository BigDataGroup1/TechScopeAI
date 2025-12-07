"""Multi-agent system for TechScopeAI."""

from .base_agent import BaseAgent
from .pitch_agent import PitchAgent
from .competitive_agent import CompetitiveAgent
from .patent_agent import PatentAgent
from .policy_agent import PolicyAgent
from .marketing_agent import MarketingAgent
from .team_agent import TeamAgent
from .coordinator_agent import CoordinatorAgent
from .supervisor_agent import SupervisorAgent

__all__ = [
    "BaseAgent", 
    "PitchAgent", 
    "CompetitiveAgent", 
    "PatentAgent", 
    "PolicyAgent", 
    "MarketingAgent", 
    "TeamAgent",
    "CoordinatorAgent",
    "SupervisorAgent"
]

