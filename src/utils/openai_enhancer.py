"""OpenAI-powered slide content enhancement."""

import logging
import os
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class OpenAISlideEnhancer:
    """Enhance slide content using OpenAI GPT-4."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI enhancer.
        
        Args:
            api_key: OpenAI API key (or from OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Slide enhancement will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI enhancer initialized")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
    
    def enhance_slide(self, slide: Dict, company_name: str, slide_number: int) -> Dict:
        """
        Enhance a single slide's content using OpenAI.
        
        Args:
            slide: Slide dictionary with title, content, key_points
            company_name: Company name for context
            slide_number: Slide number
            
        Returns:
            Enhanced slide dictionary
        """
        if not self.enabled:
            return slide  # Return original if enhancement disabled
        
        try:
            title = slide.get("title", "")
            content = slide.get("content", "")
            key_points = slide.get("key_points", [])
            
            # Build prompt for OpenAI
            prompt = f"""You are a professional pitch deck consultant. Enhance this slide for a startup pitch deck.

Company: {company_name}
Slide {slide_number}: {title}

Current Content:
{content}

Key Points:
{chr(10).join(f"- {point}" for point in key_points) if key_points else "None"}

Please enhance this slide by:
1. Making the title more compelling and impactful (keep it concise, max 10 words)
2. Improving the content to be more persuasive and investor-focused
3. Refining key points to be more specific and impactful (3-5 bullet points max)
4. Ensuring professional, confident tone suitable for investors

Return ONLY a JSON object with this exact structure:
{{
    "title": "enhanced title",
    "content": "enhanced content (2-3 sentences, concise)",
    "key_points": ["point 1", "point 2", "point 3"]
}}

Do not include any other text, only the JSON object."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for cost efficiency, change to "gpt-4" for better quality
                messages=[
                    {"role": "system", "content": "You are an expert pitch deck consultant. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON (handle markdown code blocks if present)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            enhanced = json.loads(response_text)
            
            # Merge with original (preserve other fields)
            enhanced_slide = {
                **slide,
                "title": enhanced.get("title", title),
                "content": enhanced.get("content", content),
                "key_points": enhanced.get("key_points", key_points),
                "ai_enhanced": True
            }
            
            logger.info(f"Enhanced slide {slide_number}: {title}")
            return enhanced_slide
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse OpenAI response for slide {slide_number}: {e}")
            return slide
        except Exception as e:
            logger.error(f"Error enhancing slide {slide_number}: {e}", exc_info=True)
            return slide  # Return original on error
    
    def enhance_slides_batch(self, slides: List[Dict], company_name: str, 
                            enhance_all: bool = True) -> List[Dict]:
        """
        Enhance multiple slides.
        
        Args:
            slides: List of slide dictionaries
            company_name: Company name
            enhance_all: If True, enhance all slides. If False, enhance key slides only
            
        Returns:
            List of enhanced slides
        """
        if not self.enabled:
            logger.info("OpenAI enhancement disabled, returning original slides")
            return slides
        
        # Key slides to always enhance (if not enhancing all)
        key_slide_indices = [0, 1, 2, 3, 4] if not enhance_all else None
        
        enhanced_slides = []
        for i, slide in enumerate(slides):
            if enhance_all or (key_slide_indices and i in key_slide_indices):
                enhanced = self.enhance_slide(slide, company_name, i + 1)
                enhanced_slides.append(enhanced)
            else:
                enhanced_slides.append(slide)
        
        enhanced_count = len([s for s in enhanced_slides if s.get('ai_enhanced')])
        logger.info(f"Enhanced {enhanced_count} out of {len(slides)} slides with OpenAI")
        return enhanced_slides
    
    def rewrite_full_pitch_deck(self, slides: List[Dict], company_name: str, 
                                 company_data: Optional[Dict] = None) -> List[Dict]:
        """
        Full rewrite of entire pitch deck using ChatGPT for investor-focused, compelling content.
        This is a second pass that makes the entire deck more polished and investor-ready.
        
        Args:
            slides: List of slide dictionaries
            company_name: Company name
            company_data: Optional company financial/investor data
            
        Returns:
            Fully rewritten slides
        """
        if not self.enabled:
            logger.info("OpenAI rewrite disabled, returning original slides")
            return slides
        
        try:
            # Prepare company context for investor focus
            financial_context = ""
            if company_data:
                if company_data.get('annual_revenue'):
                    financial_context += f"Annual Revenue: {company_data.get('annual_revenue')}\n"
                if company_data.get('ebitda'):
                    financial_context += f"EBITDA: {company_data.get('ebitda')}\n"
                if company_data.get('current_valuation'):
                    financial_context += f"Current Valuation: {company_data.get('current_valuation')}\n"
                if company_data.get('equity_offering'):
                    financial_context += f"Equity Offering: {company_data.get('equity_offering')}\n"
                if company_data.get('growth_rate'):
                    financial_context += f"Growth Rate: {company_data.get('growth_rate')}\n"
            
            # Build comprehensive prompt for full rewrite
            prompt = f"""You are an expert pitch deck consultant working with top VCs and investors. 
Rewrite this entire pitch deck to be investor-focused, compelling, and professionally written.

Company: {company_name}

Financial Context:
{financial_context if financial_context else "Early stage - no financial data yet"}

Current Pitch Deck ({len(slides)} slides):
{json.dumps(slides, indent=2)}

TASK: Rewrite the ENTIRE pitch deck with:
1. Investor-focused language (emphasize returns, market opportunity, traction)
2. Compelling, concise content (each slide should be powerful and memorable)
3. Professional tone suitable for VCs and angel investors
4. Clear value propositions and differentiation
5. Strong calls to action
6. If financial data is weak/negative, either omit it or frame it positively (e.g., "investing in growth" instead of "losing money")
7. Include shareholding/equity info if provided
8. Emphasize valuation and growth potential
9. Make every word count - be concise but impactful

Return ONLY a valid JSON object with this exact structure:
{{
  "slides": [
    {{
      "slide_number": 1,
      "title": "Rewritten compelling title",
      "content": "Rewritten compelling content (2-3 sentences max)",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }}
  ]
}}

IMPORTANT:
- Keep the same number of slides
- Maintain slide_number order
- Be investor-focused throughout
- If data is weak, either omit it or reframe positively
- Make it compelling and professional"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Can change to "gpt-4" for better quality
                messages=[
                    {"role": "system", "content": "You are an expert pitch deck consultant. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=3000
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            rewritten_data = json.loads(response_text)
            rewritten_slides = rewritten_data.get("slides", slides)
            
            # Preserve original metadata (image_path, etc.)
            for i, rewritten_slide in enumerate(rewritten_slides):
                if i < len(slides):
                    rewritten_slide["image_path"] = slides[i].get("image_path")
                    rewritten_slide["ai_rewritten"] = True
            
            logger.info(f"✅ Full pitch deck rewritten with ChatGPT ({len(rewritten_slides)} slides)")
            return rewritten_slides
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse ChatGPT rewrite response: {e}")
            return slides
        except Exception as e:
            logger.error(f"Error rewriting pitch deck: {e}", exc_info=True)
            return slides

