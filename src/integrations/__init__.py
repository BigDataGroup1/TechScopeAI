"""Real-time data integrations for TechScopeAI."""

from .product_hunt import ProductHuntAPI
from .hackernews import HackerNewsAPI
from .real_data_layer import RealDataLayer

__all__ = [
    "ProductHuntAPI",
    "HackerNewsAPI",
    "RealDataLayer"
]


