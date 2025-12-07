"""Content enhancement for compelling, data-driven pitch deck content."""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ContentEnhancer:
    """Enhance content with hooks, storytelling, and data extraction."""
    
    def __init__(self):
        """Initialize content enhancer."""
        logger.info("ContentEnhancer initialized")
    
    def generate_hook(self, slide_title: str, slide_content: str,
                     company_name: str) -> str:
        """
        Generate compelling hook/opening for a slide.
        
        Args:
            slide_title: Slide title
            slide_content: Slide content
            company_name: Company name
            
        Returns:
            Compelling hook sentence
        """
        hooks = {
            "problem": [
                f"Every day, {company_name} sees the same problem:",
                f"The pain is real. {company_name} discovered that",
                f"Here's what keeps {company_name} up at night:",
                f"{company_name} found that the biggest challenge is:"
            ],
            "solution": [
                f"{company_name} has the answer:",
                f"That's why {company_name} built:",
                f"{company_name} solves this with:",
                f"Introducing {company_name}'s solution:"
            ],
            "traction": [
                f"{company_name} is already proving it works:",
                f"The numbers speak for themselves:",
                f"{company_name} has achieved:",
                f"Here's what {company_name} has accomplished:"
            ],
            "market": [
                f"The opportunity is massive:",
                f"{company_name} is entering a market worth:",
                f"This is a ${0}B opportunity because:",
                f"The market is ready for {company_name}:"
            ]
        }
        
        # Detect slide type
        text_lower = slide_title.lower()
        slide_type = "default"
        
        if any(word in text_lower for word in ["problem", "pain", "challenge"]):
            slide_type = "problem"
        elif any(word in text_lower for word in ["solution", "product", "how"]):
            slide_type = "solution"
        elif any(word in text_lower for word in ["traction", "growth", "metrics"]):
            slide_type = "traction"
        elif any(word in text_lower for word in ["market", "opportunity", "tam"]):
            slide_type = "market"
        
        # Get appropriate hook
        hook_list = hooks.get(slide_type, hooks["problem"])
        import random
        hook_template = random.choice(hook_list)
        
        # Extract key metric if available
        numbers = self.extract_numbers(slide_content)
        if numbers and slide_type == "market":
            hook_template = hook_template.replace("${0}B", f"${numbers[0]:.1f}B")
        
        return hook_template
    
    def extract_numbers(self, text: str) -> List[float]:
        """
        Extract all numbers from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of extracted numbers
        """
        # Pattern to match numbers (including with K, M, B suffixes)
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*([KMkm]|million|billion)?',
            r'(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*([KMkm])',
            r'(\d+(?:\.\d+)?)'
        ]
        
        numbers = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.group(1))
                    # Handle suffixes
                    suffix = match.group(2) if len(match.groups()) > 1 else None
                    if suffix:
                        suffix_lower = suffix.lower()
                        if suffix_lower in ['k', 'thousand']:
                            value *= 1000
                        elif suffix_lower in ['m', 'million']:
                            value *= 1000000
                        elif suffix_lower in ['b', 'billion']:
                            value *= 1000000000
                    numbers.append(value)
                except (ValueError, IndexError):
                    continue
        
        return numbers
    
    def extract_metrics(self, text: str) -> Dict[str, float]:
        """
        Extract key metrics from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of metric names and values
        """
        metrics = {}
        
        # Common metric patterns
        patterns = {
            'revenue': r'(?:revenue|mrr|arr)[:\s]*\$?(\d+(?:\.\d+)?)\s*([KMkm]|million)?',
            'users': r'(\d+(?:\.\d+)?)\s*(?:users|customers|subscribers)',
            'growth': r'(\d+(?:\.\d+)?)\s*%?\s*(?:growth|increase|yoy)',
            'market_size': r'(?:tam|market)[:\s]*\$?(\d+(?:\.\d+)?)\s*([KMkm]|billion)?',
            'conversion': r'(\d+(?:\.\d+)?)\s*%?\s*(?:conversion|ctr|cvr)'
        }
        
        for metric_name, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.group(1))
                    if len(match.groups()) > 1 and match.group(2):
                        suffix = match.group(2).lower()
                        if suffix in ['k', 'thousand']:
                            value *= 1000
                        elif suffix in ['m', 'million']:
                            value *= 1000000
                        elif suffix in ['b', 'billion']:
                            value *= 1000000000
                    metrics[metric_name] = value
                    break  # Take first match
                except (ValueError, IndexError):
                    continue
        
        return metrics
    
    def enhance_with_storytelling(self, slide_content: str, slide_title: str) -> str:
        """
        Enhance content with storytelling elements.
        
        Args:
            slide_content: Original content
            slide_title: Slide title
            
        Returns:
            Enhanced content with storytelling
        """
        # Add emotional appeal
        if "problem" in slide_title.lower():
            # Add impact statement
            if "cost" in slide_content.lower() or "waste" in slide_content.lower():
                enhanced = f"💸 The cost is staggering. " + slide_content
            elif "time" in slide_content.lower():
                enhanced = f"⏰ Time is being wasted. " + slide_content
            else:
                enhanced = f"🚨 The problem is real. " + slide_content
        else:
            enhanced = slide_content
        
        return enhanced
    
    def create_compelling_stat(self, metric_name: str, value: float,
                              context: str = "") -> str:
        """
        Create a compelling statistic statement.
        
        Args:
            metric_name: Name of metric
            value: Metric value
            context: Additional context
            
        Returns:
            Compelling stat statement
        """
        # Format value
        if value >= 1000000000:
            formatted = f"${value/1000000000:.1f}B"
        elif value >= 1000000:
            formatted = f"${value/1000000:.1f}M"
        elif value >= 1000:
            formatted = f"${value/1000:.1f}K"
        else:
            formatted = f"${value:.0f}"
        
        statements = [
            f"{formatted} in {metric_name}",
            f"Reached {formatted} {metric_name}",
            f"{formatted} {metric_name} and growing",
            f"Already at {formatted} {metric_name}"
        ]
        
        import random
        return random.choice(statements) + (f" - {context}" if context else "")
    
    def add_transition(self, current_slide: Dict, next_slide: Dict) -> str:
        """
        Generate transition sentence between slides.
        
        Args:
            current_slide: Current slide data
            next_slide: Next slide data
            
        Returns:
            Transition sentence
        """
        current_type = self._detect_slide_type(current_slide.get('title', ''))
        next_type = self._detect_slide_type(next_slide.get('title', ''))
        
        transitions = {
            ("problem", "solution"): "But there's a solution:",
            ("solution", "market"): "And the market opportunity is huge:",
            ("market", "traction"): "We're already proving it works:",
            ("traction", "team"): "With the right team to execute:",
            ("team", "financials"): "Here's how we'll scale:",
            ("financials", "ask"): "We're raising to accelerate:"
        }
        
        transition = transitions.get((current_type, next_type), "Next:")
        return transition
    
    def _detect_slide_type(self, title: str) -> str:
        """Detect slide type from title."""
        title_lower = title.lower()
        if any(word in title_lower for word in ["problem", "pain", "challenge"]):
            return "problem"
        elif any(word in title_lower for word in ["solution", "product"]):
            return "solution"
        elif any(word in title_lower for word in ["market", "opportunity"]):
            return "market"
        elif any(word in title_lower for word in ["traction", "growth"]):
            return "traction"
        elif any(word in title_lower for word in ["team", "founder"]):
            return "team"
        elif any(word in title_lower for word in ["financial", "revenue"]):
            return "financials"
        elif any(word in title_lower for word in ["ask", "funding"]):
            return "ask"
        return "default"
    
    def enhance_key_points(self, key_points: List[str]) -> List[str]:
        """
        Enhance key points with better formatting and impact.
        
        Args:
            key_points: List of key points
            
        Returns:
            Enhanced key points
        """
        enhanced = []
        for point in key_points:
            # Add emphasis to numbers
            point_enhanced = re.sub(
                r'(\d+(?:\.\d+)?)',
                r'**\1**',
                point
            )
            # Ensure it starts with action verb or strong statement
            if not point_enhanced[0].isupper():
                point_enhanced = point_enhanced.capitalize()
            enhanced.append(point_enhanced)
        
        return enhanced


