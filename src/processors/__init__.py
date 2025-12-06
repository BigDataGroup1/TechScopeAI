"""Data processors for TechScope AI agents."""

from .base_processor import BaseProcessor
from .competitive_processor import CompetitiveProcessor
from .marketing_processor import MarketingProcessor
from .ip_legal_processor import IPLegalProcessor
from .policy_processor import PolicyProcessor
from .team_processor import TeamProcessor
from .pitch_processor import PitchProcessor

__all__ = [
    "BaseProcessor",
    "CompetitiveProcessor",
    "MarketingProcessor",
    "IPLegalProcessor",
    "PolicyProcessor",
    "TeamProcessor",
    "PitchProcessor",
]

