"""Template manager for multiple PowerPoint design templates (Gamma.ai style)."""

import logging
from typing import Dict, Optional
from pptx.dml.color import RGBColor

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manage multiple design templates for PowerPoint."""
    
    TEMPLATES = {
        "modern": {
            "name": "Modern",
            "description": "Clean, minimal, lots of white space",
            "colors": {
                "primary": RGBColor(30, 58, 138),      # Deep blue
                "secondary": RGBColor(15, 23, 42),     # Navy
                "accent": RGBColor(59, 130, 246),      # Bright blue
                "highlight": RGBColor(34, 197, 94),    # Green
                "text": RGBColor(30, 41, 59),          # Slate
                "background": RGBColor(248, 250, 252), # Light gray
                "white": RGBColor(255, 255, 255)
            },
            "fonts": {
                "heading": "Inter",
                "body": "Inter",
                "size_heading": 32,
                "size_body": 18
            },
            "style": "minimal"
        },
        "bold": {
            "name": "Bold",
            "description": "Vibrant colors, strong typography",
            "colors": {
                "primary": RGBColor(124, 58, 237),      # Purple
                "secondary": RGBColor(79, 70, 229),     # Indigo
                "accent": RGBColor(168, 85, 247),       # Light purple
                "highlight": RGBColor(236, 72, 153),    # Pink
                "text": RGBColor(17, 24, 39),           # Dark gray
                "background": RGBColor(255, 255, 255),  # White
                "white": RGBColor(255, 255, 255)
            },
            "fonts": {
                "heading": "Poppins",
                "body": "Poppins",
                "size_heading": 36,
                "size_body": 20
            },
            "style": "bold"
        },
        "corporate": {
            "name": "Corporate",
            "description": "Professional, conservative",
            "colors": {
                "primary": RGBColor(15, 23, 42),       # Navy
                "secondary": RGBColor(30, 41, 59),      # Slate
                "accent": RGBColor(100, 116, 139),      # Gray
                "highlight": RGBColor(14, 165, 233),    # Sky blue
                "text": RGBColor(30, 41, 59),          # Slate
                "background": RGBColor(255, 255, 255),  # White
                "white": RGBColor(255, 255, 255)
            },
            "fonts": {
                "heading": "Roboto",
                "body": "Roboto",
                "size_heading": 30,
                "size_body": 16
            },
            "style": "professional"
        },
        "startup": {
            "name": "Startup",
            "description": "Energetic, modern, tech-focused",
            "colors": {
                "primary": RGBColor(59, 130, 246),      # Blue
                "secondary": RGBColor(37, 99, 235),     # Dark blue
                "accent": RGBColor(34, 197, 94),        # Green
                "highlight": RGBColor(251, 146, 60),    # Orange
                "text": RGBColor(17, 24, 39),           # Dark gray
                "background": RGBColor(249, 250, 251),   # Light gray
                "white": RGBColor(255, 255, 255)
            },
            "fonts": {
                "heading": "Inter",
                "body": "Inter",
                "size_heading": 34,
                "size_body": 18
            },
            "style": "energetic"
        }
    }
    
    def __init__(self, template_name: str = "modern"):
        """
        Initialize template manager.
        
        Args:
            template_name: Name of template to use
        """
        self.template_name = template_name
        self.template = self.TEMPLATES.get(template_name, self.TEMPLATES["modern"])
        logger.info(f"TemplateManager initialized with template: {template_name}")
    
    def get_template(self, template_name: Optional[str] = None) -> Dict:
        """
        Get template configuration.
        
        Args:
            template_name: Optional template name (uses current if None)
            
        Returns:
            Template configuration dictionary
        """
        if template_name:
            return self.TEMPLATES.get(template_name, self.TEMPLATES["modern"])
        return self.template
    
    def get_colors(self) -> Dict[str, RGBColor]:
        """Get color scheme for current template."""
        return self.template["colors"]
    
    def get_fonts(self) -> Dict[str, str]:
        """Get font configuration for current template."""
        return self.template["fonts"]
    
    def list_templates(self) -> Dict[str, Dict]:
        """List all available templates."""
        return {name: {
            "name": config["name"],
            "description": config["description"]
        } for name, config in self.TEMPLATES.items()}
    
    def set_template(self, template_name: str):
        """
        Set active template.
        
        Args:
            template_name: Name of template to use
        """
        if template_name in self.TEMPLATES:
            self.template_name = template_name
            self.template = self.TEMPLATES[template_name]
            logger.info(f"Switched to template: {template_name}")
        else:
            logger.warning(f"Template '{template_name}' not found, using 'modern'")
            self.template_name = "modern"
            self.template = self.TEMPLATES["modern"]


