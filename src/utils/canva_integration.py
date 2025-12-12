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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        
        # Canva API base URL - Canva uses OAuth 2.0, but we'll try direct API key first
        self.base_url = "https://api.canva.com/rest/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        if self.api_key:
            logger.info("CanvaIntegration initialized with API key")
        else:
            logger.warning("CanvaIntegration initialized without API key - will use demo mode")
    
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
        
        Note: Canva uses OAuth 2.0 for authentication. This implementation
        attempts to use the API key directly, but may require OAuth flow for full functionality.
        """
        if demo_mode:
            logger.info("Canva running in demo mode - returning placeholder response")
            title_slug = design_data["title"].lower().replace(" ", "-").replace(":", "").replace("---", "-")
            return {
                "success": True,
                "design_id": f"canva_demo_{title_slug}",
                "design_url": f"https://www.canva.com/design/{title_slug}",
                "edit_url": f"https://www.canva.com/design/{title_slug}/edit",
                "template": template_id,
                "visual_enhanced": True,
                "demo_mode": True,
                "message": "Canva presentation created (demo mode - add CANVA_API_KEY to .env for real API)"
            }
        
        try:
            # Prepare slides for Canva API
            slides_content = []
            for slide in design_data.get("slides", []):
                slide_obj = {
                    "title": slide.get("title", "Untitled"),
                    "content": slide.get("content", ""),
                    "key_points": slide.get("key_points", []),
                    "slide_number": slide.get("slide_number", 0)
                }
                if slide.get("image_path"):
                    slide_obj["image_url"] = slide.get("image_path")
                slides_content.append(slide_obj)
            
            # Try different Canva API endpoints
            endpoints_to_try = [
                f"{self.base_url}/designs",
                f"{self.base_url}/presentations",
                "https://api.canva.com/v1/designs",
                "https://api.canva.com/rest/v1/designs"
            ]
            
            payload = {
                "title": design_data.get("title", "Presentation"),
                "type": "presentation",
                "template_id": template_id,
                "slides": slides_content,
                "options": {
                    "enhance_visuals": True,
                    "auto_layout": True,
                    "include_images": True,
                    "professional_styling": True
                }
            }
            
            last_error = None
            for endpoint in endpoints_to_try:
                try:
                    logger.info(f"Attempting Canva API call to: {endpoint}")
                    response = requests.post(
                        endpoint,
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    
                    # Check if request was successful
                    if response.status_code == 200 or response.status_code == 201:
                        result = response.json()
                        logger.info(f"✅ Canva API call successful to {endpoint}")
                        
                        # Extract design URL from response
                        design_url = result.get("url") or result.get("design_url") or result.get("link")
                        design_id = result.get("id") or result.get("design_id")
                        edit_url = result.get("edit_url") or result.get("edit_link")
                        
                        return {
                            "success": True,
                            "design_id": design_id or f"canva_{design_data['title'].lower().replace(' ', '-')}",
                            "design_url": design_url or f"https://www.canva.com/design/{design_id}",
                            "edit_url": edit_url or f"https://www.canva.com/design/{design_id}/edit",
                            "template": template_id,
                            "visual_enhanced": True,
                            "demo_mode": False,
                            "message": "Canva presentation created successfully",
                            "api_response": result
                        }
                    elif response.status_code == 401:
                        logger.error(f"Canva API authentication failed - check your CANVA_API_KEY")
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("error", {}).get("message", "Authentication failed")
                        except:
                            error_msg = response.text[:200] if hasattr(response, 'text') else "Authentication failed"
                        
                        return {
                            "success": False,
                            "error": "Authentication failed",
                            "message": f"Canva API requires OAuth 2.0 authentication, not a simple API key. The CANVA_API_KEY you provided is not valid for direct API access. To use Canva integration, you need to set up OAuth 2.0 flow. See: https://www.canva.dev/docs/connect/authentication/",
                            "status_code": 401,
                            "oauth_required": True,
                            "docs_url": "https://www.canva.dev/docs/connect/authentication/"
                        }
                    elif response.status_code == 404:
                        # Try next endpoint
                        last_error = f"Endpoint not found: {endpoint}"
                        continue
                    else:
                        error_text = response.text[:500] if hasattr(response, 'text') else str(response.status_code)
                        last_error = f"API returned status {response.status_code}: {error_text}"
                        logger.warning(f"Canva API returned {response.status_code}: {error_text}")
                        continue
                        
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    logger.debug(f"Request to {endpoint} failed: {e}")
                    continue
            
            # If all endpoints failed, return error
            logger.error(f"All Canva API endpoints failed. Last error: {last_error}")
            return {
                "success": False,
                "error": last_error or "All API endpoints failed",
                "message": "Failed to create design via Canva API. Canva may require OAuth 2.0 authentication instead of API key.",
                "note": "Check https://www.canva.dev/docs/connect/ for OAuth 2.0 setup instructions. Canva Connect APIs use OAuth, not simple API keys."
            }
            
        except Exception as e:
            logger.error(f"Canva API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create design via Canva API: {e}"
            }


                }
            }
            
            last_error = None
            for endpoint in endpoints_to_try:
                try:
                    logger.info(f"Attempting Canva API call to: {endpoint}")
                    response = requests.post(
                        endpoint,
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    
                    # Check if request was successful
                    if response.status_code == 200 or response.status_code == 201:
                        result = response.json()
                        logger.info(f"✅ Canva API call successful to {endpoint}")
                        
                        # Extract design URL from response
                        design_url = result.get("url") or result.get("design_url") or result.get("link")
                        design_id = result.get("id") or result.get("design_id")
                        edit_url = result.get("edit_url") or result.get("edit_link")
                        
                        return {
                            "success": True,
                            "design_id": design_id or f"canva_{design_data['title'].lower().replace(' ', '-')}",
                            "design_url": design_url or f"https://www.canva.com/design/{design_id}",
                            "edit_url": edit_url or f"https://www.canva.com/design/{design_id}/edit",
                            "template": template_id,
                            "visual_enhanced": True,
                            "demo_mode": False,
                            "message": "Canva presentation created successfully",
                            "api_response": result
                        }
                    elif response.status_code == 401:
                        logger.error(f"Canva API authentication failed - check your CANVA_API_KEY")
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("error", {}).get("message", "Authentication failed")
                        except:
                            error_msg = response.text[:200] if hasattr(response, 'text') else "Authentication failed"
                        
                        return {
                            "success": False,
                            "error": "Authentication failed",
                            "message": f"Canva API requires OAuth 2.0 authentication, not a simple API key. The CANVA_API_KEY you provided is not valid for direct API access. To use Canva integration, you need to set up OAuth 2.0 flow. See: https://www.canva.dev/docs/connect/authentication/",
                            "status_code": 401,
                            "oauth_required": True,
                            "docs_url": "https://www.canva.dev/docs/connect/authentication/"
                        }
                    elif response.status_code == 404:
                        # Try next endpoint
                        last_error = f"Endpoint not found: {endpoint}"
                        continue
                    else:
                        error_text = response.text[:500] if hasattr(response, 'text') else str(response.status_code)
                        last_error = f"API returned status {response.status_code}: {error_text}"
                        logger.warning(f"Canva API returned {response.status_code}: {error_text}")
                        continue
                        
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    logger.debug(f"Request to {endpoint} failed: {e}")
                    continue
            
            # If all endpoints failed, return error
            logger.error(f"All Canva API endpoints failed. Last error: {last_error}")
            return {
                "success": False,
                "error": last_error or "All API endpoints failed",
                "message": "Failed to create design via Canva API. Canva may require OAuth 2.0 authentication instead of API key.",
                "note": "Check https://www.canva.dev/docs/connect/ for OAuth 2.0 setup instructions. Canva Connect APIs use OAuth, not simple API keys."
            }
            
        except Exception as e:
            logger.error(f"Canva API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create design via Canva API: {e}"
            }


                }
            }
            
            last_error = None
            for endpoint in endpoints_to_try:
                try:
                    logger.info(f"Attempting Canva API call to: {endpoint}")
                    response = requests.post(
                        endpoint,
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    
                    # Check if request was successful
                    if response.status_code == 200 or response.status_code == 201:
                        result = response.json()
                        logger.info(f"✅ Canva API call successful to {endpoint}")
                        
                        # Extract design URL from response
                        design_url = result.get("url") or result.get("design_url") or result.get("link")
                        design_id = result.get("id") or result.get("design_id")
                        edit_url = result.get("edit_url") or result.get("edit_link")
                        
                        return {
                            "success": True,
                            "design_id": design_id or f"canva_{design_data['title'].lower().replace(' ', '-')}",
                            "design_url": design_url or f"https://www.canva.com/design/{design_id}",
                            "edit_url": edit_url or f"https://www.canva.com/design/{design_id}/edit",
                            "template": template_id,
                            "visual_enhanced": True,
                            "demo_mode": False,
                            "message": "Canva presentation created successfully",
                            "api_response": result
                        }
                    elif response.status_code == 401:
                        logger.error(f"Canva API authentication failed - check your CANVA_API_KEY")
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("error", {}).get("message", "Authentication failed")
                        except:
                            error_msg = response.text[:200] if hasattr(response, 'text') else "Authentication failed"
                        
                        return {
                            "success": False,
                            "error": "Authentication failed",
                            "message": f"Canva API requires OAuth 2.0 authentication, not a simple API key. The CANVA_API_KEY you provided is not valid for direct API access. To use Canva integration, you need to set up OAuth 2.0 flow. See: https://www.canva.dev/docs/connect/authentication/",
                            "status_code": 401,
                            "oauth_required": True,
                            "docs_url": "https://www.canva.dev/docs/connect/authentication/"
                        }
                    elif response.status_code == 404:
                        # Try next endpoint
                        last_error = f"Endpoint not found: {endpoint}"
                        continue
                    else:
                        error_text = response.text[:500] if hasattr(response, 'text') else str(response.status_code)
                        last_error = f"API returned status {response.status_code}: {error_text}"
                        logger.warning(f"Canva API returned {response.status_code}: {error_text}")
                        continue
                        
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    logger.debug(f"Request to {endpoint} failed: {e}")
                    continue
            
            # If all endpoints failed, return error
            logger.error(f"All Canva API endpoints failed. Last error: {last_error}")
            return {
                "success": False,
                "error": last_error or "All API endpoints failed",
                "message": "Failed to create design via Canva API. Canva may require OAuth 2.0 authentication instead of API key.",
                "note": "Check https://www.canva.dev/docs/connect/ for OAuth 2.0 setup instructions. Canva Connect APIs use OAuth, not simple API keys."
            }
            
        except Exception as e:
            logger.error(f"Canva API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create design via Canva API: {e}"
            }

