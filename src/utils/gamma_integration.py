"""
Gamma.ai API Integration for AI-enhanced pitch deck presentations.

Gamma.ai creates beautiful, AI-enhanced presentations from structured content.
"""

import logging
import os
import json
import requests
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class GammaIntegration:
    """Integration with Gamma.ai API for creating AI-enhanced presentations."""
    
    # Available Gamma.ai themes/templates
    GAMMA_THEMES = [
        {
            "id": "startup-pitch",
            "name": "Startup Pitch Deck",
            "description": "Modern, professional pitch deck template",
            "style": "clean",
            "color_scheme": "blue"
        },
        {
            "id": "venture-capital",
            "name": "Venture Capital Pitch",
            "description": "Bold, investor-focused design",
            "style": "bold",
            "color_scheme": "dark"
        },
        {
            "id": "minimalist",
            "name": "Minimalist Professional",
            "description": "Clean, minimal design for professional presentations",
            "style": "minimal",
            "color_scheme": "light"
        },
        {
            "id": "modern-tech",
            "name": "Modern Tech Startup",
            "description": "Tech-focused, modern design with gradients",
            "style": "modern",
            "color_scheme": "gradient"
        },
        {
            "id": "executive",
            "name": "Executive Summary",
            "description": "Executive-level, sophisticated design",
            "style": "executive",
            "color_scheme": "professional"
        }
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gamma.ai integration.
        
        Args:
            api_key: Gamma.ai API key (or from GAMMA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GAMMA_API_KEY")
        if not self.api_key:
            logger.warning("GAMMA_API_KEY not found. Gamma.ai features will be limited.")
        
        # Gamma.ai API base URL (update when official API is available)
        self.base_url = "https://api.gamma.app"  # Placeholder - update with actual API URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        logger.info("GammaIntegration initialized")
    
    def get_available_themes(self) -> List[Dict]:
        """
        Get list of available Gamma.ai themes/templates.
        
        Returns:
            List of theme dictionaries
        """
        return self.GAMMA_THEMES
    
    def create_presentation(self, slides: List[Dict], company_name: str, 
                          theme_id: str = "startup-pitch",
                          enhance_with_ai: bool = True) -> Dict:
        """
        Create a Gamma.ai presentation from slides.
        
        Args:
            slides: List of slide dictionaries
            company_name: Company name
            theme_id: Theme/template ID to use
            enhance_with_ai: Whether to use AI to enhance content
            
        Returns:
            Dictionary with presentation URL and metadata
        """
        # Allow demo mode without API key for testing
        demo_mode = not self.api_key
        if demo_mode:
            logger.info("Gamma.ai running in demo mode (no API key)")
        
        logger.info(f"Creating Gamma.ai presentation for {company_name} with theme {theme_id}")
        
        try:
            # Prepare presentation structure for Gamma.ai
            presentation_data = self._prepare_presentation_data(slides, company_name, theme_id)
            
            # If AI enhancement is enabled, enhance the content
            if enhance_with_ai:
                presentation_data = self._enhance_with_ai(presentation_data)
            
            # Create presentation via Gamma.ai API
            # Note: This is a placeholder - update with actual Gamma.ai API endpoint
            response = self._create_via_api(presentation_data, theme_id, demo_mode=demo_mode)
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating Gamma.ai presentation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create Gamma.ai presentation"
            }
    
    def _prepare_presentation_data(self, slides: List[Dict], company_name: str, 
                                   theme_id: str) -> Dict:
        """Prepare presentation data structure for Gamma.ai."""
        # Find selected theme
        theme = next((t for t in self.GAMMA_THEMES if t["id"] == theme_id), self.GAMMA_THEMES[0])
        
        presentation = {
            "title": f"{company_name} - Pitch Deck",
            "theme": theme_id,
            "theme_name": theme["name"],
            "slides": []
        }
        
        for slide in slides:
            slide_data = {
                "title": slide.get("title", "Untitled"),
                "content": slide.get("content", ""),
                "key_points": slide.get("key_points", []),
                "slide_number": slide.get("slide_number", 0)
            }
            presentation["slides"].append(slide_data)
        
        return presentation
    
    def _enhance_with_ai(self, presentation_data: Dict) -> Dict:
        """
        Enhance presentation content using AI.
        Gamma.ai will improve structure, flow, and content quality.
        """
        # This would call Gamma.ai's AI enhancement API
        # For now, we'll prepare the data structure
        logger.info("Enhancing presentation with AI...")
        
        # AI enhancement would:
        # - Improve slide titles for impact
        # - Enhance content clarity and flow
        # - Optimize key points for presentation
        # - Add transitions and narrative flow
        
        enhanced_data = {
            **presentation_data,
            "ai_enhanced": True,
            "enhancements": {
                "improved_titles": True,
                "content_optimization": True,
                "flow_optimization": True,
                "visual_suggestions": True
            }
        }
        
        return enhanced_data
    
    def _create_via_api(self, presentation_data: Dict, theme_id: str, demo_mode: bool = False) -> Dict:
        """
        Create presentation via Gamma.ai API.
        
        Note: This is a placeholder implementation.
        Update with actual Gamma.ai API endpoints when available.
        """
        try:
            # Placeholder API call - update with actual Gamma.ai API
            # Example structure (update based on actual API):
            payload = {
                "presentation": presentation_data,
                "theme": theme_id,
                "options": {
                    "enhance_with_ai": True,
                    "auto_layout": True,
                    "include_images": True
                }
            }
            
            # Uncomment when API is available:
            # response = requests.post(
            #     f"{self.base_url}/v1/presentations",
            #     headers=self.headers,
            #     json=payload,
            #     timeout=30
            # )
            # response.raise_for_status()
            # result = response.json()
            
            # For now, return a placeholder response
            if demo_mode:
                logger.info("Gamma.ai running in demo mode - returning placeholder response")
            else:
                logger.info("Gamma.ai API integration - placeholder (update with actual API)")
            
            title_slug = presentation_data['title'].lower().replace(' ', '-').replace(':', '').replace('---', '-')
            
            return {
                "success": True,
                "presentation_id": f"gamma_{title_slug}",
                "presentation_url": f"https://gamma.app/presentation/{title_slug}",
                "edit_url": f"https://gamma.app/edit/{title_slug}",
                "theme": theme_id,
                "ai_enhanced": True,
                "demo_mode": demo_mode,
                "message": "Gamma.ai presentation created" + (" (demo mode)" if demo_mode else " (placeholder - update with actual API)"),
                "note": "This is a placeholder. Update _create_via_api() with actual Gamma.ai API endpoints." if not demo_mode else "Running in demo mode. Add GAMMA_API_KEY to .env for real API integration."
            }
            
        except Exception as e:
            logger.error(f"Gamma.ai API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create presentation via Gamma.ai API"
            }

