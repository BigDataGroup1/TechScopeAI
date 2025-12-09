"""Google Gemini-powered slide content enhancement."""

import logging
import os
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GeminiSlideEnhancer:
    """Enhance slide content using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini enhancer.
        
        Args:
            api_key: Google Gemini API key (or from GEMINI_API_KEY or GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY or GOOGLE_API_KEY not found. Gemini enhancement will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                # Use gemini-2.0-flash (latest, fastest) or gemini-2.5-pro (best quality)
                try:
                    self.model = genai.GenerativeModel('gemini-2.0-flash')
                    logger.info("Gemini enhancer initialized with gemini-2.0-flash")
                except Exception:
                    # Fallback to gemini-2.5-pro if flash not available
                    try:
                        self.model = genai.GenerativeModel('gemini-2.5-pro')
                        logger.info("Gemini enhancer initialized with gemini-2.5-pro")
                    except Exception:
                        # Last fallback to gemini-1.5-flash
                        try:
                            self.model = genai.GenerativeModel('gemini-1.5-flash')
                            logger.info("Gemini enhancer initialized with gemini-1.5-flash")
                        except Exception as e:
                            logger.error(f"Could not initialize Gemini model: {e}")
                            self.enabled = False
            except ImportError:
                logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.enabled = False
    
    def enhance_slide(self, slide: Dict, company_name: str, slide_number: int) -> Dict:
        """
        Enhance a single slide's content using Gemini.
        
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
            
            # Build prompt for Gemini
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

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
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
                "ai_enhanced": True,
                "enhanced_by": "gemini"
            }
            
            logger.info(f"Enhanced slide {slide_number}: {title}")
            return enhanced_slide
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini response for slide {slide_number}: {e}")
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
            logger.info("Gemini enhancement disabled, returning original slides")
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
        logger.info(f"Enhanced {enhanced_count} out of {len(slides)} slides with Gemini")
        return enhanced_slides
    
    def rewrite_full_pitch_deck(self, slides: List[Dict], company_name: str, 
                                 company_data: Optional[Dict] = None) -> List[Dict]:
        """
        Full rewrite of entire pitch deck using Gemini for investor-focused, compelling content.
        This is a second pass that makes the entire deck more polished and investor-ready.
        
        Args:
            slides: List of slide dictionaries
            company_name: Company name
            company_data: Optional company financial/investor data
            
        Returns:
            Fully rewritten slides
        """
        if not self.enabled:
            logger.info("Gemini rewrite disabled, returning original slides")
            return slides
        
        try:
            # Build COMPREHENSIVE company context with ALL details for personalization
            company_context = f"""
COMPANY PROFILE:
- Name: {company_name}
- Industry: {company_data.get('industry', 'Not specified')}
- Stage: {company_data.get('current_stage', 'Not specified')}
- Location: {company_data.get('location', 'Not specified')}
- Founded: {company_data.get('founded_year', 'Not specified')}
- Website: {company_data.get('website', 'Not specified')}

PROBLEM & SOLUTION:
- Problem: {company_data.get('problem', 'Not specified')}
- Solution: {company_data.get('solution', 'Not specified')}
- Unique Value Proposition: {company_data.get('unique_value_prop', company_data.get('value_proposition', 'Not specified'))}
- Target Market: {company_data.get('target_market', 'Not specified')}
- Customer Segment: {company_data.get('customer_segment', 'Not specified')}

BUSINESS MODEL:
- Revenue Model: {company_data.get('revenue_model', 'Not specified')}
- Pricing Strategy: {company_data.get('pricing', 'Not specified')}
- Key Partnerships: {company_data.get('partnerships', 'Not specified')}
- Distribution Channels: {company_data.get('distribution', 'Not specified')}

TRACTION & METRICS:
- Annual Revenue: {company_data.get('annual_revenue', 'Not specified')}
- Monthly Recurring Revenue (MRR): {company_data.get('mrr', 'Not specified')}
- Customer Count: {company_data.get('customer_count', 'Not specified')}
- Growth Rate: {company_data.get('growth_rate', 'Not specified')}
- Key Metrics: {company_data.get('key_metrics', 'Not specified')}
- EBITDA: {company_data.get('ebitda', 'Not specified')}

FINANCIAL & INVESTMENT:
- Current Valuation: {company_data.get('valuation', company_data.get('current_valuation', 'Not specified'))}
- Equity Offering: {company_data.get('equity_offering', 'Not specified')}
- Funding Amount Needed: {company_data.get('funding_amount', company_data.get('funding_goal', 'Not specified'))}
- Use of Funds: {company_data.get('use_of_funds', 'Not specified')}
- Projected Revenue: {company_data.get('projected_revenue', 'Not specified')}

COMPETITIVE LANDSCAPE:
- Main Competitors: {company_data.get('competitors', 'Not specified')}
- Competitive Advantage: {company_data.get('competitive_advantage', company_data.get('differentiation', 'Not specified'))}
- Market Position: {company_data.get('market_position', 'Not specified')}

TEAM:
- Founders: {company_data.get('founders', company_data.get('team', 'Not specified'))}
- Key Team Members: {company_data.get('key_team_members', 'Not specified')}
- Advisory Board: {company_data.get('advisors', 'Not specified')}

GO-TO-MARKET:
- Marketing Strategy: {company_data.get('marketing_strategy', 'Not specified')}
- Sales Strategy: {company_data.get('sales_strategy', 'Not specified')}
- Customer Acquisition: {company_data.get('customer_acquisition', 'Not specified')}

VISION & ROADMAP:
- Vision: {company_data.get('vision', company_data.get('long_term_vision', 'Not specified'))}
- Milestones: {company_data.get('milestones', 'Not specified')}
- Roadmap: {company_data.get('roadmap', 'Not specified')}
"""

            # Build HIGHLY PERSONALIZED prompt for full rewrite
            prompt = f"""You are an elite pitch deck consultant who has worked with top VCs (Sequoia, a16z, Y Combinator) and helped raise billions in funding.

Your task: Rewrite this ENTIRE pitch deck to be HIGHLY PERSONALIZED, compelling, and investor-ready for THIS SPECIFIC COMPANY.

COMPANY DETAILS (USE THESE TO MAKE IT PERSONALIZED - NOT GENERIC):
{company_context}

CURRENT PITCH DECK ({len(slides)} slides):
{json.dumps(slides, indent=2)}

CRITICAL REQUIREMENTS FOR PERSONALIZATION:
1. **USE SPECIFIC COMPANY DETAILS**: Reference the actual company name, industry, problem, solution, and metrics throughout. DO NOT use generic phrases like "our company" or "the startup" - use "{company_name}" specifically.

2. **INDUSTRY-SPECIFIC LANGUAGE**: Use terminology and examples relevant to {company_data.get('industry', 'their industry')}. Show deep understanding of their market.

3. **PROBLEM-SOLUTION FIT**: Clearly articulate how {company_data.get('solution', 'their solution')} solves {company_data.get('problem', 'the specific problem')} for {company_data.get('target_market', 'their target market')}.

4. **REAL METRICS & DATA**: Include actual numbers from the company data:
   - Revenue: {company_data.get('annual_revenue', 'if available')}
   - Customers: {company_data.get('customer_count', 'if available')}
   - Growth: {company_data.get('growth_rate', 'if available')}
   - Valuation: {company_data.get('valuation', 'if available')}

5. **UNIQUE VALUE PROPS**: Highlight what makes {company_name} unique: {company_data.get('unique_value_prop', company_data.get('competitive_advantage', 'their unique advantages'))}

6. **COMPETITIVE POSITIONING**: Reference their actual competitors ({company_data.get('competitors', 'if provided')}) and show clear differentiation.

7. **TEAM CREDIBILITY**: Mention specific founders/team members if provided: {company_data.get('founders', company_data.get('team', 'if available'))}

8. **INVESTOR-FOCUSED**: Every slide should answer "Why should I invest in {company_name} specifically?" - not just any startup.

9. **STORYTELLING**: Create a narrative arc that's unique to {company_name}'s journey, not a generic startup story.

10. **AVOID GENERIC PHRASES**: Replace phrases like:
    - "We are a leading company" → "{company_name} is revolutionizing {company_data.get('industry', 'the industry')} by..."
    - "Our solution" → "{company_data.get('solution', 'Their specific solution')}"
    - "The market" → "{company_data.get('target_market', 'Their specific target market')}"

Return ONLY a valid JSON object with this exact structure:
{{
  "slides": [
    {{
      "slide_number": 1,
      "title": "Highly personalized, company-specific title",
      "content": "Personalized content referencing {company_name} and their specific details (2-3 sentences max)",
      "key_points": ["Company-specific point 1", "Company-specific point 2", "Company-specific point 3"]
    }}
  ]
}}

IMPORTANT:
- Keep the same number of slides
- Maintain slide_number order
- EVERY slide must reference {company_name} or their specific details
- NO generic startup language - everything must be personalized
- Use actual company data, metrics, and details throughout
- Make it compelling, professional, and SPECIFIC to this company"""

            # Try to generate content (with error handling for quota)
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()
            except Exception as e:
                error_str = str(e)
                # Check if it's a quota/rate limit error
                if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                    logger.error("❌ Gemini quota exceeded. The system will automatically fallback to OpenAI or continue without enhancement.")
                    raise  # Re-raise to trigger fallback in exporter
                else:
                    raise  # Re-raise other errors
            
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
                    rewritten_slide["enhanced_by"] = "gemini"
            
            logger.info(f"✅ Full pitch deck rewritten with Gemini ({len(rewritten_slides)} slides)")
            return rewritten_slides
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini rewrite response: {e}")
            return slides
        except Exception as e:
            logger.error(f"Error rewriting pitch deck: {e}", exc_info=True)
            return slides

