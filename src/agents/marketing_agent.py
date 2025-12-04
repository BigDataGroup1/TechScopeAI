"""Marketing Agent - Generates social media content, images, and marketing strategies."""

import logging
import json
import os
import requests
from typing import Dict, List, Optional
from pathlib import Path

from .base_agent import BaseAgent
from ..rag.retriever import Retriever
from ..utils.web_search import WebSearcher

logger = logging.getLogger(__name__)


class MarketingAgent(BaseAgent):
    """Agent specialized in marketing content generation for Instagram and LinkedIn."""
    
    MARKETING_QUESTIONNAIRE = [
        {
            "id": "product_description",
            "question": "📦 Describe your product or service in detail",
            "type": "textarea",
            "required": True,
            "placeholder": "What does your product/service do? What problem does it solve?"
        },
        {
            "id": "company_name",
            "question": "🏢 What is your company name?",
            "type": "text",
            "required": True,
            "placeholder": "e.g., TechFlow Solutions"
        },
        {
            "id": "platform",
            "question": "📱 Which platform(s) do you want content for?",
            "type": "multiselect",
            "options": ["Instagram", "LinkedIn", "Both"],
            "required": True
        },
        {
            "id": "content_style",
            "question": "🎨 What content style do you prefer?",
            "type": "select",
            "options": ["Quirky/Fun", "Professional", "Trendy/Modern", "Mix of styles"],
            "required": True
        },
        {
            "id": "content_type",
            "question": "📝 What type of content do you need?",
            "type": "multiselect",
            "options": [
                "Single Post",
                "Carousel Post (multiple slides)",
                "Story",
                "Reel/LinkedIn Video Script",
                "Content Series (multiple posts)"
            ],
            "required": True
        },
        {
            "id": "target_audience",
            "question": "🎯 Who is your target audience?",
            "type": "textarea",
            "required": True,
            "placeholder": "e.g., Small business owners, Tech professionals, Gen Z consumers..."
        },
        {
            "id": "campaign_goal",
            "question": "🎯 What's your main campaign goal?",
            "type": "select",
            "options": [
                "Brand awareness",
                "Lead generation",
                "Product launch",
                "Engagement/growth",
                "Sales/conversions",
                "Thought leadership"
            ],
            "required": True
        },
        {
            "id": "generate_image",
            "question": "🖼️ Do you want AI-generated images?",
            "type": "select",
            "options": [
                "Yes, generate custom AI images",
                "No, just create text content",
                "Use stock images (free)"
            ],
            "required": True
        },
        {
            "id": "image_style_description",
            "question": "🎨 Describe the image style you want (if generating images):",
            "type": "textarea",
            "required": False,
            "depends_on": {"generate_image": "Yes, generate custom AI images"},
            "placeholder": "e.g., Modern tech workspace, colorful abstract, minimalist design..."
        },
        {
            "id": "trend_check",
            "question": "📈 Should we check and incorporate latest marketing trends?",
            "type": "select",
            "options": ["Yes, include latest trends", "No, just create standard content"],
            "required": True
        },
        {
            "id": "hashtag_preference",
            "question": "🏷️ How many hashtags do you want?",
            "type": "select",
            "options": [
                "5-10 hashtags (recommended)",
                "10-20 hashtags",
                "20-30 hashtags",
                "No hashtags"
            ],
            "required": True
        },
        {
            "id": "content_count",
            "question": "📊 How many content pieces do you want?",
            "type": "select",
            "options": ["1 post", "3 posts", "5 posts", "10 posts (content series)"],
            "required": True
        }
    ]
    
    def __init__(self, retriever: Retriever, model: str = "gpt-4-turbo-preview"):
        """
        Initialize Marketing Agent.
        
        Args:
            retriever: Retriever instance for RAG
            model: LLM model name
        """
        super().__init__("marketing", retriever, model=model)
        self.web_searcher = WebSearcher(max_results=5)
        self.image_cache_dir = Path("exports/marketing_images")
        self.image_cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("MarketingAgent initialized")
    
    def generate_instagram_content(self, marketing_context: Dict) -> Dict:
        """
        Generate Instagram content with captions, hashtags, and image prompts.
        
        Args:
            marketing_context: Marketing requirements and preferences
            
        Returns:
            Generated Instagram content with sources
        """
        logger.info("Generating Instagram content")
        
        # Check trends if requested
        trends_context = ""
        if marketing_context.get('trend_check') == "Yes, include latest trends":
            trends = self._check_marketing_trends("Instagram marketing trends 2025")
            trends_context = f"\n\nLATEST INSTAGRAM TRENDS:\n{trends}"
        
        # Retrieve marketing examples
        marketing_data = self.retrieve_context(
            f"Instagram marketing content {marketing_context.get('content_style', '')} {marketing_context.get('campaign_goal', '')}",
            top_k=5
        )
        
        # Web search for best practices if needed
        web_results = []
        if marketing_data.get('count', 0) < 3:
            topic_context = f"{marketing_context.get('platform', '')} {marketing_context.get('content_style', '')}"
            web_results = self.web_searcher.search(
                f"Instagram marketing best practices {marketing_context.get('campaign_goal', '')}",
                topic_context=topic_context
            )
        
        content_count = int(marketing_context.get('content_count', '1 post').split()[0])
        
        prompt = f"""Generate Instagram content for this company:

COMPANY DETAILS:
{json.dumps(marketing_context, indent=2)}

MARKETING EXAMPLES FROM DATABASE:
{marketing_data.get('context', 'No relevant examples found')}

WEB SEARCH RESULTS:
{self._format_web_results(web_results) if web_results else ''}
{trends_context}

TASK: Generate {content_count} Instagram post(s) with:
1. Engaging Caption (optimized for Instagram, emoji usage based on style)
2. Relevant Hashtags ({marketing_context.get('hashtag_preference', '5-10 hashtags')})
3. Image Description/Prompt (for AI image generation)
4. Posting Recommendations (best time, engagement tips)

Style: {marketing_context.get('content_style', 'Professional')}
Goal: {marketing_context.get('campaign_goal', 'Brand awareness')}
Target Audience: {marketing_context.get('target_audience', '')}

IMPORTANT: If critical information is missing (product description, target audience, campaign goals), ask for clarification before generating content.

Format each post clearly with:
- Caption (with line breaks for readability)
- Hashtags (separated)
- Image Description
- Engagement Tips"""
        
        system_prompt = """You are an expert Instagram marketing strategist with deep knowledge of social media marketing, content creation, and engagement strategies. 
Create comprehensive, engaging, viral-worthy Instagram content that drives engagement and conversions. Use appropriate emojis, hashtags, and formatting for Instagram's algorithm.

When generating responses:
- Provide highly detailed, thorough content with multiple post ideas and strategies
- Include specific captions, hashtags, posting schedules, and engagement tactics
- Explain why each element works and how it drives results
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and cover all aspects of Instagram marketing"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = marketing_data.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'similarity': web_result.get('relevance_score', 0)
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def generate_linkedin_content(self, marketing_context: Dict) -> Dict:
        """
        Generate LinkedIn content optimized for professional networking.
        
        Args:
            marketing_context: Marketing requirements and preferences
            
        Returns:
            Generated LinkedIn content with sources
        """
        logger.info("Generating LinkedIn content")
        
        # Check trends if requested
        trends_context = ""
        if marketing_context.get('trend_check') == "Yes, include latest trends":
            trends = self._check_marketing_trends("LinkedIn marketing trends 2025")
            trends_context = f"\n\nLATEST LINKEDIN TRENDS:\n{trends}"
        
        # Retrieve LinkedIn examples
        linkedin_data = self.retrieve_context(
            f"LinkedIn marketing content professional {marketing_context.get('campaign_goal', '')}",
            top_k=5
        )
        
        # Web search if needed
        web_results = []
        if linkedin_data.get('count', 0) < 3:
            web_results = self.web_searcher.search(
                f"LinkedIn marketing best practices {marketing_context.get('campaign_goal', '')}",
                topic_context=marketing_context.get('content_style', '')
            )
        
        content_count = int(marketing_context.get('content_count', '1 post').split()[0])
        
        prompt = f"""Generate LinkedIn content for this company:

COMPANY DETAILS:
{json.dumps(marketing_context, indent=2)}

LINKEDIN EXAMPLES FROM DATABASE:
{linkedin_data.get('context', 'No relevant examples found')}

WEB SEARCH RESULTS:
{self._format_web_results(web_results) if web_results else ''}
{trends_context}

TASK: Generate {content_count} LinkedIn post(s) with:
1. Professional Post Text (LinkedIn-optimized, engaging but professional)
2. Relevant Hashtags (3-5 professional hashtags)
3. Image Description (if needed)
4. Engagement Strategy (how to boost engagement)
5. Call-to-Action (CTA)

Style: {marketing_context.get('content_style', 'Professional')}
Goal: {marketing_context.get('campaign_goal', 'Thought leadership')}
Target Audience: {marketing_context.get('target_audience', '')}

Format each post with:
- Post Text (professional, value-driven)
- Hashtags
- Image Description
- Engagement Tips
- CTA"""
        
        system_prompt = """You are an expert LinkedIn marketing consultant with deep knowledge of B2B marketing, thought leadership, and professional content creation. 
Create comprehensive, professional, value-driven LinkedIn content that establishes thought leadership and drives B2B engagement.

When generating responses:
- Provide highly detailed, thorough content with multiple post ideas and strategies
- Include specific post text, engagement tactics, and thought leadership strategies
- Explain why each element works and how it drives B2B results
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with examples and best practices
- Be comprehensive and cover all aspects of LinkedIn marketing"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = linkedin_data.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'similarity': web_result.get('relevance_score', 0)
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )
    
    def generate_marketing_image(self, product_description: str, style: str, 
                                 image_style_description: Optional[str] = None) -> Dict:
        """
        Generate marketing image using DALL-E 3.
        
        Args:
            product_description: Description of product/service
            style: Content style (quirky, professional, trendy)
            image_style_description: Optional additional style description
            
        Returns:
            Dictionary with image URL and path
        """
        logger.info(f"Generating marketing image with style: {style}")
        
        # Build image prompt based on style
        style_prompts = {
            "Quirky/Fun": "quirky, fun, playful, colorful, eye-catching, social media friendly",
            "Professional": "professional, clean, modern, business-focused, high-quality",
            "Trendy/Modern": "trendy, modern, sleek, contemporary, Instagram-worthy, viral potential",
            "Mix of styles": "balanced, engaging, modern, professional yet approachable"
        }
        
        style_prompt = style_prompts.get(style, "professional, modern, engaging")
        
        # Combine prompts
        if image_style_description:
            full_prompt = f"{image_style_description}, {style_prompt}, marketing image for: {product_description}, high quality, social media ready, 1024x1024"
        else:
            full_prompt = f"{style_prompt} marketing image for: {product_description}, high quality, social media ready, 1024x1024"
        
        try:
            # Generate image using DALL-E 3
            # Note: DALL-E 3 doesn't support 'n' parameter - it always generates 1 image
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1024",
                quality="standard"
            )
            
            image_url = response.data[0].url
            
            # Download and save image
            image_path = self._download_image(image_url, product_description)
            
            return {
                "success": True,
                "image_url": image_url,
                "image_path": str(image_path),
                "prompt_used": full_prompt
            }
            
        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Could not generate image. Try using stock images instead."
            }
    
    def suggest_marketing_strategies(self, marketing_context: Dict) -> Dict:
        """
        Suggest innovative marketing strategies.
        
        Args:
            marketing_context: Marketing requirements
            
        Returns:
            Marketing strategy suggestions
        """
        logger.info("Generating marketing strategies")
        
        # Check latest marketing trends
        trends = self._check_marketing_trends(
            f"{marketing_context.get('platform', '')} marketing strategies 2025"
        )
        
        # Retrieve strategy examples
        strategy_data = self.retrieve_context(
            f"marketing strategies {marketing_context.get('campaign_goal', '')} {marketing_context.get('industry', '')}",
            top_k=5
        )
        
        prompt = f"""Suggest innovative marketing strategies for this company:

COMPANY DETAILS:
{json.dumps(marketing_context, indent=2)}

STRATEGY EXAMPLES FROM DATABASE:
{strategy_data.get('context', 'No relevant examples found')}

LATEST MARKETING TRENDS:
{trends}

TASK: Provide innovative marketing strategies including:
1. Content Strategy (what to post, when, how often)
2. Engagement Tactics (how to boost engagement)
3. Growth Hacks (creative ways to grow followers)
4. Campaign Ideas (specific campaign concepts)
5. Cross-Platform Strategy (if multiple platforms)
6. Influencer/Collaboration Ideas
7. User-Generated Content Ideas
8. Trend Integration (how to leverage current trends)
9. Analytics & Measurement (what to track)
10. Budget-Friendly Tactics

Be creative, specific, and actionable. Focus on {marketing_context.get('campaign_goal', 'brand awareness')}."""
        
        system_prompt = """You are an expert creative marketing strategist with deep knowledge of digital marketing, growth hacking, and startup marketing. 
Suggest comprehensive, innovative, actionable marketing strategies that drive real results for startups.

When generating responses:
- Provide highly detailed, thorough marketing strategies with comprehensive analysis
- Include specific tactics, timelines, budgets, and expected results
- Explain why each strategy works and how to implement it
- Structure responses clearly with sections and bullet points
- If asked for more details, provide extensive analysis with examples, case studies, and best practices
- Be comprehensive and cover all aspects of marketing strategy"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        return self.format_response(
            response=response_text,
            sources=strategy_data.get('sources', [])
        )
    
    def _check_marketing_trends(self, query: str) -> str:
        """
        Check latest marketing trends via web search.
        
        Args:
            query: Search query for trends
            
        Returns:
            Formatted trends information
        """
        logger.info(f"Checking marketing trends: {query}")
        
        web_results = self.web_searcher.search(
            query,
            topic_context="marketing trends social media",
            max_results=8
        )
        
        if not web_results:
            return "No recent trends found. Using general best practices."
        
        trends_text = "Latest Marketing Trends:\n"
        for i, result in enumerate(web_results, 1):
            trends_text += f"\n[{i}] {result.get('title', '')}\n"
            trends_text += f"   {result.get('snippet', '')[:200]}...\n"
            trends_text += f"   Source: {result.get('url', '')}\n"
        
        return trends_text
    
    def _download_image(self, image_url: str, description: str) -> Path:
        """
        Download image from URL and save to cache.
        
        Args:
            image_url: URL of the image
            description: Description for filename
            
        Returns:
            Path to saved image
        """
        try:
            import hashlib
            import time
            
            # Create filename from description
            filename_hash = hashlib.md5(description.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            filename = f"marketing_{filename_hash}_{timestamp}.png"
            filepath = self.image_cache_dir / filename
            
            # Download image
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded marketing image: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            raise
    
    def _format_web_results(self, web_results: List[Dict]) -> str:
        """Format web search results for prompt."""
        if not web_results:
            return ""
        
        formatted = []
        for i, result in enumerate(web_results, 1):
            formatted.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', '')}\n"
                f"   Snippet: {result.get('snippet', '')[:200]}...\n"
                f"   Relevance: {result.get('relevance_score', 0):.2f}"
            )
        
        return "\n\n".join(formatted)
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a general marketing-related query.
        
        Args:
            query: User query
            context: Optional marketing context
            
        Returns:
            Agent response
        """
        # Try RAG first
        context_data = self.retrieve_context(query, top_k=5)
        
        # Use web search if RAG doesn't have enough results
        web_results = []
        if context_data.get('count', 0) < 3:
            logger.info("RAG results insufficient, using web search fallback")
            topic_context = f"{context.get('platform', '')} {context.get('content_style', '')}" if context else query
            web_results = self.web_searcher.search(
                query,
                topic_context=topic_context
            )
        
        prompt = f"""User Question: {query}

Relevant Marketing Data:
{context_data.get('context', 'No relevant context found in database')}

Web Search Results:
{self._format_web_results(web_results) if web_results else 'No additional web results'}

Provide helpful marketing advice and content suggestions based on the context above."""
        
        if context:
            prompt += f"\n\nMarketing Context:\n{json.dumps(context, indent=2)}"
        
        system_prompt = """You are an expert marketing consultant specializing in social media marketing, content creation, and digital marketing strategies for startups. 
Answer questions comprehensively about marketing, content creation, and digital marketing strategies.

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
- Request details about: product/service description, target audience, platform (Instagram/LinkedIn), content style, campaign goals, budget, brand voice
- Ask follow-up questions to understand the user's specific marketing needs and objectives
- Don't assume - ask for clarification when needed
- If information is missing, explicitly ask for it before proceeding"""
        
        response_text = self.generate_response(prompt, system_prompt=system_prompt)
        
        all_sources = context_data.get('sources', [])
        for web_result in web_results:
            all_sources.append({
                'source': web_result.get('url', 'Web Search'),
                'title': web_result.get('title', ''),
                'similarity': web_result.get('relevance_score', 0)
            })
        
        return self.format_response(
            response=response_text,
            sources=all_sources
        )

