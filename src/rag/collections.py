"""
Collection definitions for ChromaDB.

Each agent has a corresponding collection that stores its RAG corpus.
"""

from typing import Dict, Optional
from enum import Enum


class AgentType(str, Enum):
    """Agent types in the system."""
    COMPETITIVE = "competitive"
    MARKETING = "marketing"
    IP_LEGAL = "ip_legal"
    POLICY = "policy"
    TEAM = "team"
    PITCH = "pitch"


class CollectionConfig:
    """Configuration for a ChromaDB collection."""
    
    def __init__(
        self,
        name: str,
        agent_type: AgentType,
        description: str,
        processed_data_path: str
    ):
        self.name = name
        self.agent_type = agent_type
        self.description = description
        self.processed_data_path = processed_data_path


# Collection mappings: collection_name -> CollectionConfig
COLLECTIONS: Dict[str, CollectionConfig] = {
    "competitors_corpus": CollectionConfig(
        name="competitors_corpus",
        agent_type=AgentType.COMPETITIVE,
        description="Competitive analysis data: startups, funding, sectors, positioning",
        processed_data_path="data/processed/competitive/competitive_data.jsonl"
    ),
    "marketing_corpus": CollectionConfig(
        name="marketing_corpus",
        agent_type=AgentType.MARKETING,
        description="Marketing and ad copy data: taglines, ad creatives, positioning examples",
        processed_data_path="data/processed/marketing/marketing_data.jsonl"
    ),
    "ip_policy_corpus": CollectionConfig(
        name="ip_policy_corpus",
        agent_type=AgentType.IP_LEGAL,
        description="IP/Legal data: privacy Q&A, patent guides, OSS policies",
        processed_data_path="data/processed/ip_legal/ip_legal_data.jsonl"
    ),
    "policy_corpus": CollectionConfig(
        name="policy_corpus",
        agent_type=AgentType.POLICY,
        description="Policy drafting data: privacy policies, terms of service examples",
        processed_data_path="data/processed/policy/policy_data.jsonl"
    ),
    "job_roles_corpus": CollectionConfig(
        name="job_roles_corpus",
        agent_type=AgentType.TEAM,
        description="Team composition data: job descriptions, skills, role requirements",
        processed_data_path="data/processed/team/team_data.jsonl"
    ),
    "pitch_examples_corpus": CollectionConfig(
        name="pitch_examples_corpus",
        agent_type=AgentType.PITCH,
        description="Pitch examples: one-line pitches, pitch deck templates, success stories",
        processed_data_path="data/processed/pitch/pitch_data.jsonl"
    ),
}


def get_collection_name(agent_type: AgentType) -> Optional[str]:
    """Get the collection name for an agent type."""
    for collection_name, config in COLLECTIONS.items():
        if config.agent_type == agent_type:
            return collection_name
    return None


def get_collection_config(collection_name: str) -> Optional[CollectionConfig]:
    """Get the collection config by name."""
    return COLLECTIONS.get(collection_name)


def get_all_collections() -> Dict[str, CollectionConfig]:
    """Get all collection configurations."""
    return COLLECTIONS.copy()





