"""Brand customization system for PowerPoint presentations."""

import logging
from pathlib import Path
from typing import Dict, Optional
from pptx.dml.color import RGBColor

logger = logging.getLogger(__name__)


class BrandManager:
    """Manage brand customization (logo, colors, fonts)."""
    
    def __init__(self, logo_path: Optional[str] = None,
                 primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None,
                 font_family: Optional[str] = None):
        """
        Initialize brand manager.
        
        Args:
            logo_path: Path to company logo image
            primary_color: Primary brand color (hex or RGB)
            secondary_color: Secondary brand color (hex or RGB)
            font_family: Brand font family name
        """
        self.logo_path = logo_path
        self.primary_color = self._parse_color(primary_color) if primary_color else None
        self.secondary_color = self._parse_color(secondary_color) if secondary_color else None
        self.font_family = font_family
        
        if logo_path and Path(logo_path).exists():
            logger.info(f"Brand logo loaded: {logo_path}")
        else:
            logger.info("No brand logo provided")
        
        logger.info("BrandManager initialized")
    
    def _parse_color(self, color_str: str) -> RGBColor:
        """
        Parse color from string (hex or RGB).
        
        Args:
            color_str: Color string (e.g., "#1e40af" or "rgb(30, 64, 175)")
            
        Returns:
            RGBColor object
        """
        try:
            # Hex color
            if color_str.startswith("#"):
                hex_color = color_str.lstrip("#")
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return RGBColor(r, g, b)
            
            # RGB string
            elif color_str.startswith("rgb"):
                # Extract numbers
                import re
                numbers = re.findall(r'\d+', color_str)
                if len(numbers) >= 3:
                    return RGBColor(int(numbers[0]), int(numbers[1]), int(numbers[2]))
            
            # Comma-separated RGB
            elif "," in color_str:
                parts = color_str.split(",")
                if len(parts) >= 3:
                    return RGBColor(int(parts[0]), int(parts[1]), int(parts[2]))
        except Exception as e:
            logger.warning(f"Could not parse color {color_str}: {e}")
        
        # Default: blue
        return RGBColor(30, 58, 138)
    
    def get_brand_colors(self, default_colors: Dict[str, RGBColor]) -> Dict[str, RGBColor]:
        """
        Get brand colors, falling back to defaults.
        
        Args:
            default_colors: Default color scheme
            
        Returns:
            Brand color scheme
        """
        colors = default_colors.copy()
        
        if self.primary_color:
            colors["primary"] = self.primary_color
            # Generate accent from primary
            colors["accent"] = self._lighten_color(self.primary_color)
        
        if self.secondary_color:
            colors["secondary"] = self.secondary_color
        
        return colors
    
    def _lighten_color(self, color: RGBColor, factor: float = 1.3) -> RGBColor:
        """Lighten a color."""
        return RGBColor(
            min(255, int(color.r * factor)),
            min(255, int(color.g * factor)),
            min(255, int(color.b * factor))
        )
    
    def add_logo_to_slide(self, slide, position: str = "top-right",
                         size: float = 1.0) -> bool:
        """
        Add logo to slide.
        
        Args:
            slide: PowerPoint slide object
            position: Logo position (top-left, top-right, bottom-left, bottom-right)
            size: Logo size in inches
            
        Returns:
            True if logo added successfully
        """
        if not self.logo_path or not Path(self.logo_path).exists():
            return False
        
        try:
            from pptx.util import Inches
            
            slide_width = slide.slide_width
            slide_height = slide.slide_height
            
            # Calculate position
            if position == "top-right":
                left = slide_width - Inches(size + 0.2)
                top = Inches(0.2)
            elif position == "top-left":
                left = Inches(0.2)
                top = Inches(0.2)
            elif position == "bottom-right":
                left = slide_width - Inches(size + 0.2)
                top = slide_height - Inches(size + 0.2)
            elif position == "bottom-left":
                left = Inches(0.2)
                top = slide_height - Inches(size + 0.2)
            else:
                left = slide_width - Inches(size + 0.2)
                top = Inches(0.2)
            
            slide.shapes.add_picture(
                self.logo_path,
                left, top,
                width=Inches(size),
                height=Inches(size * 0.5)  # Maintain aspect ratio
            )
            
            logger.info(f"Logo added to slide at {position}")
            return True
            
        except Exception as e:
            logger.warning(f"Could not add logo: {e}")
            return False
    
    def get_brand_fonts(self, default_fonts: Dict[str, str]) -> Dict[str, str]:
        """
        Get brand fonts, falling back to defaults.
        
        Args:
            default_fonts: Default font configuration
            
        Returns:
            Brand font configuration
        """
        fonts = default_fonts.copy()
        
        if self.font_family:
            fonts["heading"] = self.font_family
            fonts["body"] = self.font_family
        
        return fonts


