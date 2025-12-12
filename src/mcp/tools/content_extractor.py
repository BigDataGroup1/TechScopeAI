"""Content extraction tool for MCP server."""

import logging
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from ..server import MCPTool

logger = logging.getLogger(__name__)

try:
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests/beautifulsoup4 not available for content extraction")


class ContentExtractorTool(MCPTool):
    """Tool for extracting content from web pages."""
    
    def __init__(self):
        """Initialize content extractor tool."""
        super().__init__(
            name="content_extractor",
            description="Extract main text content from a webpage URL. Removes scripts, styles, and formatting."
        )
    
    def execute(self, url: str, max_length: Optional[int] = 5000) -> Dict[str, Any]:
        """
        Execute content extraction.
        
        Args:
            url: URL to extract content from
            max_length: Maximum length of extracted content (default: 5000)
            
        Returns:
            Dictionary with extracted content
        """
        if not REQUESTS_AVAILABLE:
            return {
                "success": False,
                "error": "requests/beautifulsoup4 not available",
                "content": None
            }
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit length
            if max_length and len(text) > max_length:
                text = text[:max_length] + "..."
            
            return {
                "success": True,
                "content": text,
                "url": url,
                "length": len(text)
            }
            
        except Exception as e:
            logger.warning(f"Could not extract content from {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "content": None
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for tool arguments."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to extract content from"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum length of extracted content",
                        "default": 5000
                    }
                },
                "required": ["url"]
            }
        }


