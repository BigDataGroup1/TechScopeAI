"""Smart layout engine for content-aware slide layouts (Gamma.ai style)."""

import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class LayoutEngine:
    """Detect slide type and apply appropriate layout."""
    
    # Layout types with detection keywords
    LAYOUT_TYPES = {
        "title": {
            "keywords": ["title", "cover", "intro"],
            "description": "Full-bleed title slide with large text"
        },
        "problem": {
            "keywords": ["problem", "pain", "challenge", "issue"],
            "description": "Large image + text overlay"
        },
        "solution": {
            "keywords": ["solution", "product", "service", "how"],
            "description": "Split screen with visuals"
        },
        "data": {
            "keywords": ["market", "tam", "sam", "som", "size", "metrics", "data"],
            "description": "Chart-focused with minimal text"
        },
        "comparison": {
            "keywords": ["vs", "versus", "compare", "competitor", "competition"],
            "description": "Side-by-side comparison"
        },
        "timeline": {
            "keywords": ["timeline", "roadmap", "milestone", "journey"],
            "description": "Visual timeline layout"
        },
        "team": {
            "keywords": ["team", "founder", "founders", "people"],
            "description": "Photo grid with names"
        },
        "financials": {
            "keywords": ["financial", "revenue", "cost", "budget", "funding"],
            "description": "Table with charts"
        },
        "traction": {
            "keywords": ["traction", "growth", "metrics", "achievement"],
            "description": "Stats-focused with icons"
        },
        "vision": {
            "keywords": ["vision", "future", "goal", "mission"],
            "description": "Large text with background image"
        },
        "default": {
            "keywords": [],
            "description": "Standard two-column layout"
        }
    }
    
    def __init__(self):
        """Initialize layout engine."""
        logger.info("LayoutEngine initialized")
    
    def detect_slide_type(self, slide_title: str, slide_content: str,
                         key_points: List[str]) -> str:
        """
        Detect slide type based on content.
        
        Args:
            slide_title: Slide title
            slide_content: Slide content
            key_points: Key points list
            
        Returns:
            Detected layout type
        """
        text = f"{slide_title} {slide_content} {' '.join(key_points)}".lower()
        
        # Score each layout type
        scores = {}
        for layout_type, config in self.LAYOUT_TYPES.items():
            if layout_type == "default":
                continue
            
            score = 0
            keywords = config["keywords"]
            for keyword in keywords:
                # Title matches are worth more
                if keyword in slide_title.lower():
                    score += 3
                # Content matches
                if keyword in text:
                    score += 1
            
            if score > 0:
                scores[layout_type] = score
        
        # Return highest scoring layout, or default
        if scores:
            best_layout = max(scores.items(), key=lambda x: x[1])[0]
            logger.info(f"Detected layout: {best_layout} (score: {scores[best_layout]})")
            return best_layout
        
        return "default"
    
    def get_layout_config(self, layout_type: str) -> Dict:
        """
        Get configuration for a layout type.
        
        Args:
            layout_type: Layout type name
            
        Returns:
            Layout configuration dictionary
        """
        configs = {
            "title": {
                "has_image": True,
                "image_position": "background",
                "text_position": "center",
                "text_alignment": "center",
                "image_ratio": 1.0,  # Full background
                "text_overlay": True
            },
            "problem": {
                "has_image": True,
                "image_position": "left",
                "image_ratio": 0.5,
                "text_position": "right",
                "text_alignment": "left",
                "text_overlay": False
            },
            "solution": {
                "has_image": True,
                "image_position": "right",
                "image_ratio": 0.5,
                "text_position": "left",
                "text_alignment": "left",
                "text_overlay": False
            },
            "data": {
                "has_image": False,
                "has_chart": True,
                "chart_position": "center",
                "text_position": "top",
                "text_alignment": "center",
                "chart_ratio": 0.7
            },
            "comparison": {
                "has_image": True,
                "image_position": "split",
                "text_position": "split",
                "text_alignment": "center",
                "split_count": 2
            },
            "timeline": {
                "has_image": True,
                "image_position": "horizontal",
                "text_position": "below",
                "text_alignment": "center",
                "layout": "horizontal"
            },
            "team": {
                "has_image": True,
                "image_position": "grid",
                "text_position": "below_image",
                "text_alignment": "center",
                "grid_columns": 3
            },
            "financials": {
                "has_image": False,
                "has_chart": True,
                "has_table": True,
                "chart_position": "right",
                "table_position": "left",
                "text_alignment": "left"
            },
            "traction": {
                "has_image": False,
                "has_icons": True,
                "text_position": "center",
                "text_alignment": "center",
                "stats_layout": "grid"
            },
            "vision": {
                "has_image": True,
                "image_position": "background",
                "text_position": "center",
                "text_alignment": "center",
                "text_overlay": True,
                "image_ratio": 1.0
            },
            "default": {
                "has_image": True,
                "image_position": "right",
                "image_ratio": 0.4,
                "text_position": "left",
                "text_alignment": "left",
                "text_overlay": False
            }
        }
        
        return configs.get(layout_type, configs["default"])
    
    def get_layout_for_slide(self, slide_title: str, slide_content: str,
                            key_points: List[str]) -> Dict:
        """
        Get complete layout configuration for a slide.
        
        Args:
            slide_title: Slide title
            slide_content: Slide content
            key_points: Key points list
            
        Returns:
            Complete layout configuration
        """
        layout_type = self.detect_slide_type(slide_title, slide_content, key_points)
        config = self.get_layout_config(layout_type)
        
        return {
            "layout_type": layout_type,
            "config": config,
            "slide_title": slide_title,
            "slide_content": slide_content,
            "key_points": key_points
        }


