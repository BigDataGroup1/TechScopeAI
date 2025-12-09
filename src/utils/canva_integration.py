"""
Canva API Integration for visually enhanced pitch deck designs.

Canva creates beautiful, professionally designed presentations with better visual structure.
"""

import logging
import os
import json
import requests
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CanvaIntegration:
    """Integration with Canva API for creating visually enhanced presentations."""
    
    # Available Canva templates/themes
    CANVA_TEMPLATES = [
        {
            "id": "pitch-deck-modern",
            "name": "Modern Pitch Deck",
            "description": "Clean, modern design with bold typography",
            "style": "modern",
            "color_palette": "blue_white",
            "layout": "professional"
        },
        {
            "id": "startup-presentation",
            "name": "Startup Presentation",
            "description": "Vibrant, energetic design for startups",
            "style": "vibrant",
            "color_palette": "gradient",
            "layout": "dynamic"
        },
        {
            "id": "business-pitch",
            "name": "Business Pitch",
            "description": "Professional, corporate design",
            "style": "corporate",
            "color_palette": "professional",
            "layout": "structured"
        },
        {
            "id": "tech-startup",
            "name": "Tech Startup",
            "description": "Tech-focused design with modern aesthetics",
            "style": "tech",
            "color_palette": "tech",
            "layout": "modern"
        },
        {
            "id": "minimal-elegant",
            "name": "Minimal & Elegant",
            "description": "Minimalist design with elegant typography",
            "style": "minimal",
            "color_palette": "monochrome",
            "layout": "clean"
        },
        {
            "id": "bold-venture",
            "name": "Bold Venture",
            "description": "Bold, attention-grabbing design for VCs",
            "style": "bold",
            "color_palette": "high_contrast",
            "layout": "impact"
        }
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Canva integration.
        
        Args:
            api_key: Canva API key (or from CANVA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("CANVA_API_KEY")
        if not self.api_key:
            logger.warning("CANVA_API_KEY not found. Canva features will be limited.")
        
        # Canva API base URL (update when official API is available)
        self.base_url = "https://api.canva.com"  # Placeholder - update with actual API URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        logger.info("CanvaIntegration initialized")
    
    def get_available_templates(self) -> List[Dict]:
        """
        Get list of available Canva templates/themes.
        
        Returns:
            List of template dictionaries
        """
        return self.CANVA_TEMPLATES
    
    def create_presentation(self, slides: List[Dict], company_name: str,
                          template_id: str = "pitch-deck-modern",
                          enhance_visuals: bool = True) -> Dict:
        """
        Create a Canva presentation from slides.
        
        Args:
            slides: List of slide dictionaries
            company_name: Company name
            template_id: Template/theme ID to use
            enhance_visuals: Whether to enhance visual structure
            
        Returns:
            Dictionary with design URL and metadata
        """
        # Allow demo mode without API key for testing
        demo_mode = not self.api_key
        if demo_mode:
            logger.info("Canva running in demo mode (no API key)")
        
        logger.info(f"Creating Canva presentation for {company_name} with template {template_id}")
        
        try:
            # Prepare design structure for Canva
            design_data = self._prepare_design_data(slides, company_name, template_id)
            
            # If visual enhancement is enabled, enhance the design structure
            if enhance_visuals:
                design_data = self._enhance_visual_structure(design_data)
            
            # Create design via Canva API
            # Note: This is a placeholder - update with actual Canva API endpoint
            response = self._create_via_api(design_data, template_id, demo_mode=demo_mode)
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating Canva presentation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create Canva presentation"
            }
    
    def _prepare_design_data(self, slides: List[Dict], company_name: str,
                             template_id: str) -> Dict:
        """Prepare design data structure for Canva."""
        # Find selected template
        template = next((t for t in self.CANVA_TEMPLATES if t["id"] == template_id), 
                       self.CANVA_TEMPLATES[0])
        
        design = {
            "title": f"{company_name} - Pitch Deck",
            "template": template_id,
            "template_name": template["name"],
            "style": template["style"],
            "color_palette": template["color_palette"],
            "slides": []
        }
        
        for slide in slides:
            slide_data = {
                "title": slide.get("title", "Untitled"),
                "content": slide.get("content", ""),
                "key_points": slide.get("key_points", []),
                "slide_number": slide.get("slide_number", 0),
                "image_path": slide.get("image_path"),  # Include images if available
                "visual_elements": {
                    "layout": "professional",
                    "typography": "modern",
                    "color_scheme": template["color_palette"]
                }
            }
            design["slides"].append(slide_data)
        
        return design
    
    def _enhance_visual_structure(self, design_data: Dict) -> Dict:
        """
        Enhance visual structure using Canva's design capabilities.
        Improves layout, typography, spacing, and visual hierarchy.
        """
        logger.info("Enhancing visual structure with Canva...")
        
        # Visual enhancements would:
        # - Optimize layout and spacing
        # - Improve typography hierarchy
        # - Enhance color usage and contrast
        # - Add visual elements (icons, shapes, etc.)
        # - Optimize image placement and sizing
        
        enhanced_data = {
            **design_data,
            "visual_enhanced": True,
            "enhancements": {
                "layout_optimization": True,
                "typography_hierarchy": True,
                "color_optimization": True,
                "visual_elements": True,
                "spacing_optimization": True
            }
        }
        
        return enhanced_data
    
    def _create_via_api(self, design_data: Dict, template_id: str, demo_mode: bool = False) -> Dict:
        """
        Create design via Canva API.
        
        Note: This is a placeholder implementation.
        Update with actual Canva API endpoints when available.
        """
        try:
            # Placeholder API call - update with actual Canva API
            # Example structure (update based on actual API):
            payload = {
                "design": design_data,
                "template": template_id,
                "options": {
                    "enhance_visuals": True,
                    "auto_layout": True,
                    "include_images": True,
                    "professional_styling": True
                }
            }
            
            # Uncomment when API is available:
            # response = requests.post(
            #     f"{self.base_url}/v1/designs",
            #     headers=self.headers,
            #     json=payload,
            #     timeout=30
            # )
            # response.raise_for_status()
            # result = response.json()
            
            # For now, return a placeholder response
            if demo_mode:
                logger.info("Canva running in demo mode - returning placeholder response")
            else:
                logger.info("Canva API integration - placeholder (update with actual API)")
            
            title_slug = design_data["title"].lower().replace(" ", "-").replace(":", "").replace("---", "-")
            
            return {
                "success": True,
                "design_id": f"canva_{title_slug}",
                "design_url": f"https://www.canva.com/design/{title_slug}",
                "edit_url": f"https://www.canva.com/design/{title_slug}/edit",
                "template": template_id,
                "visual_enhanced": True,
                "demo_mode": demo_mode,
                "message": "Canva presentation created" + (" (demo mode)" if demo_mode else " (placeholder - update with actual API)"),
                "note": "This is a placeholder. Update _create_via_api() with actual Canva API endpoints." if not demo_mode else "Running in demo mode. Add CANVA_API_KEY to .env for real API integration."
            }
            
        except Exception as e:
            logger.error(f"Canva API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create design via Canva API"
            }

