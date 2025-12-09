"""MCP (Model Context Protocol) Server for TechScopeAI.

Provides tools for agents to access external services like web search,
image search, patent search, and content extraction.
"""

from .server import MCPServer
from .client import MCPClient

__all__ = ['MCPServer', 'MCPClient']


