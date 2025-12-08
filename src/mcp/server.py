"""MCP Server implementation for TechScopeAI tools."""

import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server that manages and exposes tools for agents.
    
    Tools are registered and can be called by agents via the MCP client.
    """
    
    def __init__(self):
        """Initialize MCP server with empty tool registry."""
        self.tools: Dict[str, 'MCPTool'] = {}
        logger.info("MCP Server initialized")
    
    def register_tool(self, tool: 'MCPTool'):
        """
        Register a tool with the server.
        
        Args:
            tool: MCPTool instance to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, tool_name: str) -> Optional['MCPTool']:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            MCPTool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Tool response dictionary
            
        Raises:
            ValueError: If tool not found
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {self.list_tools()}")
        
        try:
            logger.info(f"Calling tool: {tool_name} with args: {list(kwargs.keys())}")
            result = tool.execute(**kwargs)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }


class MCPTool(ABC):
    """Base class for MCP tools."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize MCP tool.
        
        Args:
            name: Unique tool name
            description: Human-readable description
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Dictionary with tool results
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for tool arguments.
        
        Returns:
            JSON schema dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {}
        }

