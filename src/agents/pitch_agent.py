"""Pitch Agent - Generates and evaluates startup pitch decks."""

import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

from .base_agent import BaseAgent
from ..rag.retriever import Retriever

logger = logging.getLogger(__name__)


class PitchAgent(BaseAgent):
    """Agent specialized in pitch deck generation and evaluation."""
    
    PITCH_QUESTIONNAIRE = [
        {
            "id": "company_name",
            "question": "🏢 What is your company name?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., TechFlow Solutions Inc."
        },
        {
            "id": "industry",
            "question": "🏭 What industry does your company operate in?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., AI/ML, SaaS, Healthcare, Fintech..."
        },
        {
            "id": "problem",
            "question": "❓ What problem are you solving?",
            "type": "textarea",
            "required": True,
            "placeholder": "Describe the problem your startup addresses..."
        },
        {
            "id": "solution",
            "question": "💡 What is your solution?",
            "type": "textarea",
            "required": True,
            "placeholder": "Describe your product or service solution..."
        },
        {
            "id": "target_market",
            "question": "🎯 Who is your target market?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., Small businesses, Enterprise, Consumers..."
        },
        {
            "id": "current_stage",
            "question": "🚀 What is your current funding stage?",
            "type": "select",
            "options": ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"],
            "required": True
        },
        {
            "id": "traction",
            "question": "📈 What traction do you have? (users, revenue, partnerships, etc.)",
            "type": "textarea",
            "required": False,
            "placeholder": "Describe your key metrics, milestones, or achievements..."
        },
        {
            "id": "funding_goal",
            "question": "💰 What is your funding goal?",
            "type": "text",
            "required": False,
            "placeholder": "e.g., $500K seed round, $2M Series A..."
        },
        {
            "id": "team",
            "question": "👥 Tell us about your team (founders, key members)",
            "type": "textarea",
            "required": False,
            "placeholder": "Brief description of founders and key team members..."
        },
        {
            "id": "competitive_advantage",
            "question": "🏆 What is your competitive advantage?",
            "type": "textarea",
            "required": False,
            "placeholder": "What makes you different from competitors..."
        }
    ]
    
    def __init__(self, retriever: Retriever, model: str = "gpt-4-turbo-preview"):
        """
        Initialize Pitch Agent.
        
        Args:
            retriever: Retriever instance for RAG
            model: LLM model name
        """
        super().__init__("pitch", retriever, model=model)
        logger.info("PitchAgent initialized")
    
    def generate_from_outline(self, outline: Dict, company_context: Optional[Dict] = None) -> Dict:
        """
        Generate pitch deck from user outline.
        
        Args:
            outline: Dictionary with "sections" and "notes"
            company_context: Optional company details
            
        Returns:
            Generated pitch deck with sources
        """
        logger.info("Generating pitch from outline")
        
        # Retrieve relevant examples
        query = outline.get("notes", "") or " ".join(outline.get("sections", []))
        context_data = self.retrieve_context(query, top_k=5)
        
        # Build prompt
        prompt = self._build_generation_prompt(
            outline=outline,
            company_context=company_context,
            examples=context_data.get('documents', []),
            context_text=context_data.get('context', '')
        )
        
        system_prompt = """You are an expert pitch deck advisor with deep knowledge of investor psychology, pitch deck best practices, and startup fundraising. 
Help startup founders create compelling, comprehensive pitch decks.

When generating responses:
- Provide highly detailed, thorough pitch deck content with comprehensive analysis
- Include specific examples, data points, and investor insights
- Explain why each section matters and how it should be structured
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and cover all essential pitch deck elements
You have access to successful pitch examples, templates, and investor insights.
Generate a complete, professional pitch deck based on the provided outline and context.
Make it data-driven, compelling, and tailored to the company."""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_context)
        # Generate response
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        return self.format_response(
            response=response_text,
            sources=context_data.get('sources', [])
        )
    
    def generate_from_details(self, company_details: Dict) -> Dict:
        """
        Generate pitch deck from company details.
        
        Args:
            company_details: Full company information dictionary
            
        Returns:
            Generated pitch deck with sources
        """
        logger.info(f"Generating pitch for company: {company_details.get('company_name', 'Unknown')}")
        
        # Build query from company details
        query_parts = [
            company_details.get('industry', ''),
            company_details.get('problem', ''),
            company_details.get('solution', ''),
            company_details.get('current_stage', '')
        ]
        query = " ".join([p for p in query_parts if p])
        
        # Retrieve similar pitches and templates
        similar_pitches = self.retrieve_context(
            f"{company_details.get('industry', '')} {company_details.get('problem', '')}",
            top_k=5
        )
        
        investor_advice = self.retrieve_context(
            f"{company_details.get('current_stage', '')} funding pitch deck",
            top_k=3
        )
        
        # Build prompt
        prompt = self._build_company_pitch_prompt(
            company_details=company_details,
            similar_pitches=similar_pitches.get('documents', []),
            investor_advice=investor_advice.get('documents', []),
            context_text=similar_pitches.get('context', '')
        )
        
        system_prompt = """You are an expert pitch deck advisor with deep knowledge of pitch deck structure, investor expectations, and startup storytelling. 
Generate comprehensive, complete, personalized pitch decks for startups based on their company details.

When generating responses:
- Provide highly detailed, thorough pitch deck content with comprehensive analysis
- Include specific examples, data points, and strategic recommendations
- Explain why each section matters and how it should be structured
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and cover all essential pitch deck elements
Use successful pitch examples and investor insights
to create a compelling, data-driven pitch deck tailored to their industry and stage."""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_details)
        # Generate response
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        # Combine sources
        all_sources = similar_pitches.get('sources', []) + investor_advice.get('sources', [])
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def evaluate_pitch(self, pitch_text: str, company_context: Optional[Dict] = None) -> Dict:
        """
        Evaluate existing pitch and suggest improvements.
        
        Args:
            pitch_text: User's pitch content
            company_context: Optional company details
            
        Returns:
            Evaluation report with scores, strengths, weaknesses, improvements
        """
        logger.info("Evaluating pitch")
        
        # Analyze structure
        structure = self._analyze_structure(pitch_text)
        
        # Retrieve similar successful pitches
        similar_pitches = self.retrieve_context(
            pitch_text[:500] if len(pitch_text) > 500 else pitch_text,
            top_k=5
        )
        
        # Retrieve best practices
        best_practices = self.retrieve_context(
            "pitch deck best practices common mistakes",
            top_k=5
        )
        
        # Retrieve failure lessons
        failure_lessons = self.retrieve_context(
            "pitch deck mistakes failures what went wrong",
            top_k=3
        )
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            pitch_text=pitch_text,
            structure=structure,
            similar_pitches=similar_pitches.get('documents', []),
            best_practices=best_practices.get('documents', []),
            failure_lessons=failure_lessons.get('documents', []),
            company_context=company_context
        )
        
        system_prompt = """You are an expert pitch deck evaluator with deep knowledge of investor expectations, pitch deck best practices, and fundraising strategies. 
Analyze the provided pitch deck comprehensively and provide detailed evaluation.

When generating responses:
- Provide highly detailed, thorough evaluations with comprehensive analysis
- Include specific feedback, scores, and actionable recommendations
- Explain why each aspect matters and how to improve it
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and cover all essential pitch deck elements

Analyze the provided pitch deck and provide:
1. Overall score (1-10)
2. Strengths
3. Weaknesses
4. Specific improvement suggestions with examples
5. Comparison to successful pitches

Be constructive, actionable, and specific. Reference the examples and best practices provided."""
        
        # Generate evaluation
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        # Combine sources
        all_sources = (
            similar_pitches.get('sources', []) + 
            best_practices.get('sources', []) + 
            failure_lessons.get('sources', [])
        )
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def generate_slides(self, company_details: Dict) -> Dict:
        """
        Generate structured pitch deck slides from company details.
        
        Args:
            company_details: Full company information dictionary
            
        Returns:
            Dictionary with slides array and metadata
        """
        logger.info(f"Generating slides for: {company_details.get('company_name', 'Unknown')}")
        
        # Retrieve similar pitches and templates
        similar_pitches = self.retrieve_context(
            f"{company_details.get('industry', '')} {company_details.get('problem', '')}",
            top_k=5
        )
        
        investor_advice = self.retrieve_context(
            f"{company_details.get('current_stage', '')} funding pitch deck structure slides",
            top_k=3
        )
        
        # Build prompt for slide generation
        prompt = f"""Generate a structured pitch deck with 10-15 slides for this startup:

COMPANY DETAILS:
{json.dumps(company_details, indent=2)}

SUCCESSFUL PITCH EXAMPLES:
{similar_pitches.get('context', '')}

INVESTOR INSIGHTS:
{investor_advice.get('context', '')}

TASK: Create a structured pitch deck with the following slides:
1. Title Slide (Company name, tagline, founder name)
2. Problem (The pain point you're solving)
3. Solution (Your product/service)
4. Market Opportunity (TAM, SAM, SOM)
5. Business Model (How you make money)
6. Traction (Key metrics, customers, growth)
7. Product Demo/Features (What you've built)
8. Competitive Landscape (Competitors and differentiation)
9. Go-to-Market Strategy (How you'll acquire customers)
10. Team (Founders and key team members)
11. Financials/Projections (Revenue, costs, unit economics)
12. The Ask (Funding amount, use of funds, milestones)
13. Vision (Where you're going)

Return ONLY a valid JSON object with this structure:
{{
  "slides": [
    {{
      "slide_number": 1,
      "title": "Slide Title",
      "content": "Main content for this slide (2-4 bullet points or short paragraphs)",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }}
  ],
  "total_slides": 13
}}

IMPORTANT:
- Make each slide concise (50-100 words), data-driven, and compelling
- Include specific numbers and metrics where available
- Focus on clear, impactful content for presentation slides"""
        
        system_prompt = """You are an expert pitch deck creator with deep knowledge of slide design, investor psychology, and startup storytelling. 
Generate comprehensive, structured slides in JSON format.

When generating responses:
- Provide highly detailed, thorough slide content with comprehensive analysis
- Include specific examples, data points, and strategic recommendations
- Explain why each slide matters and how it should be structured
- Structure slides clearly with clear titles, content, and key points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and ensure all essential slides are included

Each slide should be clear, concise, and investor-focused. Use the company details to personalize every slide."""
        
        # Extract company data for personalization
        company_data = self._extract_company_data(company_details)
        # Generate response
        response_text = self.generate_response(prompt, system_prompt=system_prompt, company_data=company_data)
        
        # Parse JSON from response
        try:
            # Extract JSON from response (might have markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            slides_data = json.loads(response_text)
            
            # Combine sources
            all_sources = similar_pitches.get('sources', []) + investor_advice.get('sources', [])
            
            slides_result = {
                "slides": slides_data.get("slides", []),
                "total_slides": slides_data.get("total_slides", len(slides_data.get("slides", []))),
                "company_name": company_details.get('company_name', 'Unknown'),
                "sources": all_sources
            }
            
            # Fetch images for each slide and store in slide data
            try:
                from ..utils.image_fetcher import ImageFetcher
                image_fetcher = ImageFetcher()
                
                logger.info("Fetching images for slides...")
                for slide in slides_result["slides"]:
                    slide_title = slide.get('title', '')
                    slide_content = slide.get('content', '')
                    
                    try:
                        # Get keywords for image search
                        keywords = image_fetcher.get_slide_keywords(slide_title, slide_content)
                        
                        # Fetch image
                        image_path = image_fetcher.get_image_for_slide(slide_title, slide_content, keywords)
                        
                        if image_path and Path(image_path).exists():
                            # Store absolute path for use in PPT and web
                            slide["image_path"] = str(Path(image_path).absolute())
                            logger.info(f"✅ Image fetched for slide: {slide_title}")
                        else:
                            slide["image_path"] = None
                    except Exception as e:
                        logger.warning(f"Could not fetch image for slide {slide.get('title', '')}: {e}")
                        slide["image_path"] = None
            except Exception as e:
                logger.warning(f"Image fetcher not available: {e}")
                # Set image_path to None for all slides
                for slide in slides_result["slides"]:
                    slide["image_path"] = None
            
            # Keep speech and talking_points for UI reference (not in PPT)
            for slide in slides_result["slides"]:
                if "speech" not in slide:
                    slide["speech"] = f"Presenting: {slide.get('title', '')}. {slide.get('content', '')}"
                if "talking_points" not in slide:
                    slide["talking_points"] = slide.get("key_points", [])
            
            # Auto-generate PowerPoint if available
            try:
                from ..utils.exporters import PitchExporter
                exporter = PitchExporter()
                pptx_path = exporter.export_to_powerpoint(
                    slides_result["slides"],
                    slides_result["company_name"],
                    include_images=True
                )
                if pptx_path:
                    slides_result["pptx_path"] = pptx_path
                    logger.info(f"Auto-generated PowerPoint: {pptx_path}")
            except Exception as e:
                logger.warning(f"Could not auto-generate PowerPoint: {e}")
            
            return slides_result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse slides JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            # Fallback: create slides from structure
            return self._create_slides_fallback(company_details, response_text)
    
    def _create_slides_fallback(self, company_details: Dict, response_text: str) -> Dict:
        """Fallback method to create slides if JSON parsing fails."""
        slides = []
        slide_titles = [
            "Title", "Problem", "Solution", "Market Opportunity", "Business Model",
            "Traction", "Product", "Competition", "Go-to-Market", "Team", 
            "Financials", "The Ask", "Vision"
        ]
        
        for i, title in enumerate(slide_titles, 1):
            slides.append({
                "slide_number": i,
                "title": title,
                "content": f"Content for {title} slide based on company details.",
                "key_points": []
            })
        
        return {
            "slides": slides,
            "total_slides": len(slides),
            "company_name": company_details.get('company_name', 'Unknown'),
            "sources": [],
            "note": "Generated fallback slides - original response parsing failed"
        }
    
    def generate_elevator_pitch(self, company_details: Dict, duration_seconds: int = 60) -> Dict:
        """
        Generate an elevator pitch speech (30-60 seconds).
        
        Args:
            company_details: Full company information dictionary
            duration_seconds: Target duration (30, 45, or 60 seconds)
            
        Returns:
            Dictionary with elevator pitch text and metadata
        """
        logger.info(f"Generating {duration_seconds}s elevator pitch for: {company_details.get('company_name', 'Unknown')}")
        
        # Retrieve successful pitch examples
        pitch_examples = self.retrieve_context(
            f"{company_details.get('industry', '')} elevator pitch startup pitch speech",
            top_k=5
        )
        
        # Calculate target word count (average speaking rate: 150 words/minute = 2.5 words/second)
        words_per_second = 2.5
        target_words = int(duration_seconds * words_per_second)
        
        prompt = f"""Create a compelling elevator pitch for this startup:

COMPANY DETAILS:
{json.dumps(company_details, indent=2)}

SUCCESSFUL PITCH EXAMPLES:
{pitch_examples.get('context', '')}

TASK: Write an elevator pitch that:
- Is exactly {duration_seconds} seconds when spoken (approximately {target_words} words)
- Starts with a hook that grabs attention
- Clearly states the problem you're solving
- Explains your solution in simple terms
- Highlights your unique value proposition
- Mentions key traction or metrics (if available)
- Ends with a clear call to action or ask
- Sounds natural and conversational (not robotic)
- Can be delivered confidently in one breath

Return ONLY the elevator pitch text, nothing else. Make it compelling and memorable."""

        system_prompt = """You are an expert at crafting elevator pitches with deep knowledge of storytelling, investor psychology, and persuasive communication. 
Create comprehensive, compelling, natural-sounding pitches that investors remember.

When generating responses:
- Provide highly detailed, thorough elevator pitches with comprehensive analysis
- Include specific examples, hooks, and strategic recommendations
- Explain why each element works and how it drives engagement
- Structure pitches clearly with clear flow and key points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and ensure all essential elements are included

The pitch should flow smoothly and be 
deliverable with confidence."""

        try:
            pitch_text = self.generate_response(prompt, system_prompt=system_prompt)
            
            if not pitch_text or len(pitch_text.strip()) == 0:
                logger.warning("Empty response from LLM for elevator pitch")
                # Fallback pitch
                pitch_text = f"""Hi, I'm {company_details.get('company_name', 'we')}. We solve {company_details.get('problem', 'a critical problem')} by {company_details.get('solution', 'providing an innovative solution')}. Our unique approach {company_details.get('competitive_advantage', 'sets us apart')}. We're looking for {company_details.get('funding_amount', 'support')} to {company_details.get('use_of_funds', 'scale our business')}."""
            
            # Clean up the response (remove quotes if wrapped)
            pitch_text = pitch_text.strip()
            if pitch_text.startswith('"') and pitch_text.endswith('"'):
                pitch_text = pitch_text[1:-1]
            if pitch_text.startswith("'") and pitch_text.endswith("'"):
                pitch_text = pitch_text[1:-1]
            
            # Remove markdown code blocks if present
            if pitch_text.startswith("```"):
                lines = pitch_text.split("\n")
                pitch_text = "\n".join(lines[1:-1]) if len(lines) > 2 else pitch_text
            
            logger.info(f"Generated elevator pitch: {len(pitch_text)} characters")
            
            return {
                "elevator_pitch": pitch_text,
                "duration_seconds": duration_seconds,
                "estimated_words": len(pitch_text.split()),
                "company_name": company_details.get('company_name', 'Unknown'),
                "sources": pitch_examples.get('sources', [])
            }
        except Exception as e:
            logger.error(f"Error generating elevator pitch: {e}", exc_info=True)
            # Return fallback pitch
            fallback_pitch = f"""Hi, I'm {company_details.get('company_name', 'we')}. We solve {company_details.get('problem', 'a critical problem')} by {company_details.get('solution', 'providing an innovative solution')}. Our unique approach {company_details.get('competitive_advantage', 'sets us apart')}. We're looking for {company_details.get('funding_amount', 'support')} to {company_details.get('use_of_funds', 'scale our business')}."""
            return {
                "elevator_pitch": fallback_pitch,
                "duration_seconds": duration_seconds,
                "estimated_words": len(fallback_pitch.split()),
                "company_name": company_details.get('company_name', 'Unknown'),
                "sources": [],
                "error": str(e)
            }
    
    def evaluate_pitch_with_scores(self, pitch_text: str, company_context: Optional[Dict] = None) -> Dict:
        """
        Enhanced evaluation with detailed scoring.
        
        Args:
            pitch_text: User's pitch content
            company_context: Optional company details
            
        Returns:
            Evaluation with detailed scores per section
        """
        logger.info("Evaluating pitch with detailed scores")
        
        # Analyze structure
        structure = self._analyze_structure(pitch_text)
        
        # Retrieve context
        similar_pitches = self.retrieve_context(pitch_text[:500], top_k=5)
        best_practices = self.retrieve_context("pitch deck best practices scoring", top_k=5)
        
        # Build scoring prompt
        prompt = f"""Evaluate this pitch deck and provide detailed scores:

PITCH TEXT:
{pitch_text[:2000]}

STRUCTURE ANALYSIS:
{json.dumps(structure, indent=2)}

BEST PRACTICES:
{best_practices.get('context', '')}

Return ONLY a valid JSON object with this structure:
{{
  "overall_score": 7.5,
  "section_scores": {{
    "problem": {{"score": 8, "max_score": 10, "feedback": "Clear problem statement"}},
    "solution": {{"score": 7, "max_score": 10, "feedback": "Good but needs more detail"}},
    "market": {{"score": 6, "max_score": 10, "feedback": "Market size not quantified"}},
    "traction": {{"score": 8, "max_score": 10, "feedback": "Strong metrics"}},
    "team": {{"score": 7, "max_score": 10, "feedback": "Good backgrounds"}},
    "ask": {{"score": 6, "max_score": 10, "feedback": "Unclear use of funds"}}
  }},
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "improvements": ["Improvement 1", "Improvement 2"]
}}"""
        
        system_prompt = """You are an expert pitch deck evaluator with deep knowledge of investor expectations, pitch deck best practices, and fundraising strategies. 
Provide comprehensive, detailed scores (1-10) for each section with thorough analysis.

When generating responses:
- Provide highly detailed, thorough evaluations with comprehensive analysis
- Include specific feedback, scores, and actionable recommendations
- Explain why each aspect matters and how to improve it
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and cover all essential pitch deck elements

Be specific and constructive in your feedback."""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        # Parse JSON
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            scores_data = json.loads(response_text)
            
            return {
                "evaluation": scores_data,
                "sources": similar_pitches.get('sources', []) + best_practices.get('sources', [])
            }
        except json.JSONDecodeError:
            # Fallback to regular evaluation
            return self.evaluate_pitch(pitch_text, company_context)
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a general pitch-related query.
        
        Args:
            query: User query
            context: Optional context (company details, etc.)
            
        Returns:
            Agent response
        """
        # Retrieve relevant context
        context_data = self.retrieve_context(query, top_k=5)
        
        # Build prompt
        prompt = f"""User Question: {query}

Relevant Context from Pitch Examples and Templates:
{context_data.get('context', 'No relevant context found')}

Please provide helpful advice about pitch decks based on the context above.
If the user asks about their specific company, use the company context provided.
Be specific and reference examples when possible."""
        
        if context:
            prompt += f"\n\nCompany Context:\n{json.dumps(context, indent=2)}"
        
        system_prompt = """You are an expert pitch deck advisor with deep knowledge of pitch decks, investor psychology, and startup fundraising. 
Answer questions comprehensively about pitch decks, provide examples, and give actionable advice.

When generating responses:
- Provide highly detailed, thorough answers with comprehensive explanations
- Include specific examples, case studies, and actionable recommendations
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive, in-depth analysis
- Be comprehensive and cover all relevant aspects of the question
- Provide actionable advice that startups can implement

IMPORTANT - Ask for clarification and more details:
- If the query is vague or unclear, ask specific clarifying questions
- If you need more information to provide a better answer, proactively ask for it
- Request details about: company name, problem, solution, target market, traction, funding needs, team, competitive advantages
- Ask follow-up questions to understand the user's specific pitch needs and investor audience
- Don't assume - ask for clarification when needed
- If information is missing, explicitly ask for it before proceeding"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        return self.format_response(
            response=response_text,
            sources=context_data.get('sources', [])
        )
    
    def _analyze_structure(self, pitch_text: str) -> Dict:
        """Analyze pitch structure."""
        text_lower = pitch_text.lower()
        
        sections = {
            "problem": any(word in text_lower for word in ["problem", "pain", "challenge", "issue"]),
            "solution": any(word in text_lower for word in ["solution", "solve", "product", "service"]),
            "market": any(word in text_lower for word in ["market", "tam", "sam", "som", "opportunity"]),
            "traction": any(word in text_lower for word in ["traction", "revenue", "customers", "mrr", "users"]),
            "team": any(word in text_lower for word in ["team", "founder", "co-founder", "background"]),
            "ask": any(word in text_lower for word in ["ask", "funding", "raise", "investment", "round"])
        }
        
        word_count = len(pitch_text.split())
        
        return {
            "sections_found": [k for k, v in sections.items() if v],
            "sections_missing": [k for k, v in sections.items() if not v],
            "word_count": word_count,
            "has_all_sections": all(sections.values())
        }
    
    def _build_generation_prompt(self, outline: Dict, company_context: Optional[Dict],
                                 examples: List[Dict], context_text: str) -> str:
        """Build prompt for pitch generation from outline."""
        prompt = f"""Generate a complete pitch deck based on the following outline:

OUTLINE:
Sections: {', '.join(outline.get('sections', []))}
Notes: {outline.get('notes', 'No additional notes')}

"""
        
        if company_context:
            prompt += f"COMPANY CONTEXT:\n{json.dumps(company_context, indent=2)}\n\n"
        
        if context_text:
            prompt += f"SUCCESSFUL PITCH EXAMPLES AND TEMPLATES:\n{context_text}\n\n"
        
        prompt += """TASK: Generate a complete pitch deck with all standard sections:
1. Problem
2. Solution
3. Market Opportunity
4. Business Model
5. Traction/Metrics
6. Team
7. Ask/Funding

Make it compelling, data-driven, and professional. Include specific numbers and examples where possible.
Format as structured sections with clear headings."""
        
        return prompt
    
    def _build_company_pitch_prompt(self, company_details: Dict, similar_pitches: List[Dict],
                                   investor_advice: List[Dict], context_text: str) -> str:
        """Build prompt for pitch generation from company details."""
        prompt = f"""Generate a personalized pitch deck for this startup:

COMPANY DETAILS:
{json.dumps(company_details, indent=2)}

"""
        
        if context_text:
            prompt += f"SIMILAR SUCCESSFUL PITCHES AND INVESTOR INSIGHTS:\n{context_text}\n\n"
        
        prompt += """TASK: Create a complete, compelling pitch deck tailored to this company.
Include all standard sections and make it specific to their industry, stage, and unique value proposition.
Use the examples above as inspiration but make it original and personalized."""
        
        return prompt
    
    def _build_evaluation_prompt(self, pitch_text: str, structure: Dict,
                                 similar_pitches: List[Dict], best_practices: List[Dict],
                                 failure_lessons: List[Dict], company_context: Optional[Dict]) -> str:
        """Build prompt for pitch evaluation."""
        prompt = f"""Evaluate this pitch deck:

PITCH TEXT:
{pitch_text[:2000]}...  # Truncate if too long

PITCH STRUCTURE ANALYSIS:
{json.dumps(structure, indent=2)}

"""
        
        if similar_pitches:
            prompt += f"SIMILAR SUCCESSFUL PITCHES (for comparison):\n"
            for i, pitch in enumerate(similar_pitches[:3], 1):
                prompt += f"[{i}] {pitch.get('content', '')[:300]}...\n\n"
        
        if best_practices:
            prompt += f"BEST PRACTICES:\n"
            for i, practice in enumerate(best_practices[:3], 1):
                prompt += f"[{i}] {practice.get('content', '')[:300]}...\n\n"
        
        if failure_lessons:
            prompt += f"COMMON MISTAKES (from failures):\n"
            for lesson in failure_lessons[:2]:
                prompt += f"- {lesson.get('content', '')[:200]}...\n\n"
        
        if company_context:
            prompt += f"COMPANY CONTEXT:\n{json.dumps(company_context, indent=2)}\n\n"
        
        prompt += """TASK: Provide a comprehensive evaluation:
1. Overall score (1-10) with reasoning
2. Strengths (what's working well)
3. Weaknesses (what needs improvement)
4. Specific improvement suggestions with examples
5. Comparison to successful pitches

Be constructive, actionable, and specific. Reference the examples and best practices above."""
        
        return prompt

