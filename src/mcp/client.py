"""MCP Client for agents to call MCP tools."""

import logging
from typing import Dict, Any, Optional
from .server import MCPServer

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client that provides a simple interface for agents to call tools.
    
    This client wraps the MCP server and provides convenient methods
    for agents to use tools without directly managing the server.
    """
    
    def __init__(self, server: Optional[MCPServer] = None):
        """
        Initialize MCP client.
        
        Args:
            server: Optional MCPServer instance. If None, creates a default server
                    with all standard tools registered.
        """
        if server:
            self.server = server
        else:
            # Create default server with all tools
            self.server = MCPServer()
            self._register_default_tools()
        
        logger.info(f"MCP Client initialized with {len(self.server.list_tools())} tools")
    
    def _register_default_tools(self):
        """Register all default tools with the server."""
        from .tools import (
            WebSearchTool,
            ImageSearchTool,
            PatentSearchTool,
            ContentExtractorTool
        )
        
        self.server.register_tool(WebSearchTool())
        self.server.register_tool(ImageSearchTool())
        self.server.register_tool(PatentSearchTool())
        self.server.register_tool(ContentExtractorTool())
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a tool by name.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Tool response dictionary
        """
        return self.server.call_tool(tool_name, **kwargs)
    
    def web_search(self, query: str, topic_context: Optional[str] = None,
                   max_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Convenience method for web search.
        
        Args:
            query: Search query
            topic_context: Optional context to filter results
            max_results: Maximum number of results
            
        Returns:
            Search results dictionary
        """
        return self.call_tool("web_search", query=query, 
                             topic_context=topic_context, 
                             max_results=max_results)
    
    def image_search(self, query: Optional[str] = None, slide_title: Optional[str] = None,
                    slide_content: Optional[str] = None, keywords: Optional[list] = None) -> Dict[str, Any]:
        """
        Convenience method for image search.
        
        Args:
            query: Search query
            slide_title: Optional slide title
            slide_content: Optional slide content
            keywords: Optional keywords list
            
        Returns:
            Image search results dictionary
        """
        return self.call_tool("image_search", query=query, slide_title=slide_title,
                             slide_content=slide_content, keywords=keywords)
    
    def patent_search(self, query: str, technology_description: Optional[str] = None,
                      company_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Convenience method for patent search.
        
        Args:
            query: Search query
            technology_description: Optional technology description
            company_context: Optional company context
            
        Returns:
            Patent search results dictionary
        """
        return self.call_tool("patent_search", query=query,
                             technology_description=technology_description,
                             company_context=company_context)
    
    def extract_content(self, url: str, max_length: Optional[int] = 5000) -> Dict[str, Any]:
        """
        Convenience method for content extraction.
        
        Args:
            url: URL to extract from
            max_length: Maximum content length
            
        Returns:
            Extracted content dictionary
        """
        return self.call_tool("content_extractor", url=url, max_length=max_length)
    
    def list_tools(self) -> list:
        """List all available tools."""
        return self.server.list_tools()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool schema dictionary or None
        """
        tool = self.server.get_tool(tool_name)
        if tool:
            return tool.get_schema()
        return None


