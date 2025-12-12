"""Gemini-powered image generation for pitch deck slides."""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
import base64
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system env vars

logger = logging.getLogger(__name__)


class GeminiImageGenerator:
    """Generate custom images for slides using Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini image generator.
        
        Args:
            api_key: Google Gemini API key (or from GEMINI_API_KEY or GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY or GOOGLE_API_KEY not found. Gemini image generation will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                # Use gemini-2.0-flash for image generation prompts
                try:
                    self.model = genai.GenerativeModel('gemini-2.0-flash')
                    logger.info("Gemini image generator initialized")
                except Exception as e:
                    logger.error(f"Could not initialize Gemini model: {e}")
                    self.enabled = False
            except ImportError:
                logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.enabled = False
        
        # Create output directory for generated images
        self.output_dir = Path("exports/gemini_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_image_for_slide(self, slide: Dict, company_name: str, 
                                 company_data: Optional[Dict] = None) -> Optional[str]:
        """
        Generate a FULL SLIDE IMAGE using Gemini's image generation API.
        This creates one complete slide image (like the screenshot you showed) that can be stitched into PPT.
        
        Args:
            slide: Slide dictionary with title, content, key_points
            company_name: Company name for personalization
            company_data: Optional company data for context
            
        Returns:
            Path to generated full slide image file, or None if generation failed
        """
        if not self.enabled:
            logger.warning("Gemini image generation disabled")
            return None
        
        try:
            slide_title = slide.get('title', '')
            slide_content = slide.get('content', '')
            key_points = slide.get('key_points', [])
            slide_number = slide.get('slide_number', 0)
            
            # Build comprehensive prompt for FULL SLIDE image generation
            full_slide_prompt = self._build_full_slide_prompt(
                slide_title, slide_content, key_points, company_name, company_data, slide_number
            )
            
            # Try Gemini's image generation API
            image_path = self._generate_with_gemini_image_api(full_slide_prompt, slide_number)
            if image_path:
                logger.info(f"✅ Generated FULL SLIDE IMAGE with Gemini for: {slide_title}")
                return image_path
            
            # Fallback: Try Imagen API
            image_path = self._generate_with_imagen(full_slide_prompt, slide_number)
            if image_path:
                logger.info(f"✅ Generated image with Imagen for slide: {slide_title}")
                return image_path
            
            # Save prompt for reference
            prompt_file = self.output_dir / f"slide_{slide_number}_prompt_{int(time.time())}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(f"Slide {slide_number}: {slide_title}\n\n")
                f.write(f"Full Slide Prompt:\n{full_slide_prompt}\n\n")
                f.write(f"Original Content:\n{slide_content}\n")
            
            logger.warning(f"⚠️ Image generation API not available. Prompt saved to {prompt_file}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating image for slide {slide.get('title', 'unknown')}: {e}", exc_info=True)
            return None
    
    def _generate_with_gemini_image_api(self, prompt: str, slide_number: int) -> Optional[str]:
        """
        Use Gemini's image generation API to generate actual images.
        Supports both google.generativeai and google.genai SDKs.
        """
        try:
            # Try new google.genai SDK first (recommended for image generation)
            try:
                from google import genai
                from google.genai.types import GenerateContentConfig, Modality
                from PIL import Image
                from io import BytesIO
                
                client = genai.Client(api_key=self.api_key)
                
                # Try different image generation models
                image_models_to_try = [
                    'gemini-2.5-flash-image',
                    'gemini-2.5-flash-image-preview',
                    'gemini-3-pro-image-preview',
                    'gemini-2.0-flash-exp-image-generation',
                ]
                
                for model_name in image_models_to_try:
                    try:
                        logger.info(f"🎨 Trying to generate image with {model_name} for slide {slide_number}...")
                        
                        # Generate image with proper config
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=GenerateContentConfig(
                                response_modalities=[Modality.IMAGE],
                                temperature=0.7,
                            )
                        )
                        
                        # Extract image data from response - check multiple formats
                        image_data = None
                        
                        if response.parts and len(response.parts) > 0:
                            for part in response.parts:
                                # Check for inline_data (base64) - most common format
                                if hasattr(part, 'inline_data') and part.inline_data:
                                    if hasattr(part.inline_data, 'data') and part.inline_data.data:
                                        try:
                                            image_data = base64.b64decode(part.inline_data.data)
                                            if len(image_data) > 1000:  # Valid image should be > 1KB
                                                logger.debug(f"Found image in inline_data, size: {len(image_data)} bytes")
                                                break
                                            else:
                                                logger.warning(f"Image data too small: {len(image_data)} bytes")
                                        except Exception as e:
                                            logger.debug(f"Error decoding inline_data: {e}")
                                # Check for direct data
                                elif hasattr(part, 'data') and part.data:
                                    data = part.data
                                    if isinstance(data, bytes) and len(data) > 1000:
                                        image_data = data
                                        logger.debug(f"Found image in data, size: {len(image_data)} bytes")
                                        break
                                    elif isinstance(data, str):
                                        # Might be base64 encoded
                                        try:
                                            decoded = base64.b64decode(data)
                                            if len(decoded) > 1000:
                                                image_data = decoded
                                                logger.debug(f"Decoded base64 image, size: {len(image_data)} bytes")
                                                break
                                        except:
                                            pass
                        
                        # Save image if found and valid
                        if image_data and len(image_data) > 1000:  # Minimum 1KB for valid image
                            image_path = self.output_dir / f"slide_{slide_number}_gemini_{int(time.time())}.png"
                            
                            # Write image data
                            with open(image_path, 'wb') as f:
                                f.write(image_data)
                            
                            # Verify it's a valid image
                            try:
                                img = Image.open(image_path)
                                img.verify()  # Verify it's a valid image
                                # Reopen for saving (verify closes the file)
                                img = Image.open(image_path)
                                img.save(image_path)  # Re-save to ensure proper format
                                logger.info(f"✅ Generated valid slide image with {model_name}: {image_path} ({len(image_data)} bytes)")
                                return str(image_path)
                            except Exception as e:
                                logger.warning(f"⚠️ Saved data is not a valid image: {e}, size: {len(image_data)} bytes")
                                # Delete invalid file
                                try:
                                    image_path.unlink()
                                except:
                                    pass
                        else:
                            if image_data:
                                logger.warning(f"⚠️ Image data too small ({len(image_data)} bytes) - likely not an image")
                            else:
                                logger.debug(f"Response from {model_name} did not contain image data")
                            
                            # Log response structure for debugging
                            if hasattr(response, 'text'):
                                logger.debug(f"Response text (first 500 chars): {response.text[:500]}")
                            if hasattr(response, 'parts'):
                                logger.debug(f"Response has {len(response.parts)} parts")
                                for i, part in enumerate(response.parts):
                                    attrs = [attr for attr in dir(part) if not attr.startswith('_')]
                                    logger.debug(f"Part {i} attributes: {attrs[:10]}")
                        
                    except Exception as e:
                        error_str = str(e)
                        if "not found" in error_str.lower() or "not available" in error_str.lower():
                            logger.debug(f"Model {model_name} not available, trying next...")
                            continue
                        elif "quota" in error_str.lower() or "429" in error_str:
                            logger.warning(f"⚠️ Quota exceeded for {model_name}")
                            return None
                        else:
                            logger.debug(f"Error with {model_name}: {e}")
                            continue
                
                logger.warning("⚠️ None of the image generation models worked")
                return None
                
            except ImportError:
                logger.debug("google.genai SDK not available, trying google.generativeai...")
                # Fallback to google.generativeai
                import google.generativeai as genai_old
                
                # Try with old SDK
                image_models_to_try = [
                    'gemini-2.5-flash-image',
                    'gemini-2.5-flash-image-preview',
                    'gemini-3-pro-image-preview',
                    'gemini-2.0-flash-exp-image-generation',
                ]
                
                for model_name in image_models_to_try:
                    try:
                        image_model = genai_old.GenerativeModel(model_name)
                        logger.info(f"🎨 Generating with {model_name} (old SDK) for slide {slide_number}...")
                        
                        # Try different response format configurations
                        try:
                            response = image_model.generate_content(
                                prompt,
                                generation_config=genai_old.types.GenerationConfig(
                                    response_modalities=["IMAGE"],
                                    temperature=0.7,
                                )
                            )
                        except Exception:
                            # Try without explicit config
                            response = image_model.generate_content(prompt)
                        
                        # Extract image from response (check multiple possible formats)
                        # Debug: log response structure
                        logger.debug(f"Response type: {type(response)}")
                        logger.debug(f"Response has candidates: {hasattr(response, 'candidates')}")
                        
                        # Try multiple response formats
                        image_data = None
                        
                        # Format 1: response.candidates[0].content.parts
                        if hasattr(response, 'candidates') and response.candidates:
                            candidate = response.candidates[0]
                            if hasattr(candidate, 'content') and candidate.content:
                                if hasattr(candidate.content, 'parts'):
                                    for part in candidate.content.parts:
                                        # Check inline_data
                                        if hasattr(part, 'inline_data') and part.inline_data:
                                            if hasattr(part.inline_data, 'data'):
                                                image_data = base64.b64decode(part.inline_data.data)
                                                break
                                        # Check for direct data
                                        elif hasattr(part, 'data') and part.data:
                                            image_data = part.data
                                            break
                        
                        # Format 2: response.parts (new SDK format)
                        if not image_data and hasattr(response, 'parts') and response.parts:
                            for part in response.parts:
                                if hasattr(part, 'data') and part.data:
                                    image_data = part.data
                                    break
                                elif hasattr(part, 'inline_data') and part.inline_data:
                                    if hasattr(part.inline_data, 'data'):
                                        image_data = base64.b64decode(part.inline_data.data)
                                        break
                        
                        # Format 3: Direct response data
                        if not image_data and hasattr(response, 'data') and response.data:
                            image_data = response.data
                        
                        # Save image if found
                        if image_data:
                            image_path = self.output_dir / f"slide_{slide_number}_gemini_{int(time.time())}.png"
                            with open(image_path, 'wb') as f:
                                if isinstance(image_data, str):
                                    # If it's base64 string, decode it
                                    image_data = base64.b64decode(image_data)
                                f.write(image_data)
                            
                            logger.info(f"✅ Generated image with {model_name}: {image_path}")
                            return str(image_path)
                        
                        # Log response for debugging
                        logger.debug(f"Response structure: {dir(response)}")
                        if hasattr(response, 'text'):
                            logger.debug(f"Response text (first 200 chars): {response.text[:200]}")
                        
                        logger.debug(f"Response from {model_name} did not contain image data")
                        
                    except Exception as e:
                        error_str = str(e)
                        if "not found" in error_str.lower():
                            continue
                        elif "quota" in error_str.lower() or "429" in error_str:
                            logger.warning(f"⚠️ Quota exceeded")
                            return None
                        else:
                            logger.debug(f"Error with {model_name}: {e}")
                            continue
                
                logger.warning("⚠️ Could not generate image with any model")
                return None
                
        except Exception as e:
            logger.error(f"Error in Gemini image generation: {e}", exc_info=True)
            return None
    
    def _build_full_slide_prompt(self, title: str, content: str, key_points: List[str],
                                company_name: str, company_data: Optional[Dict], slide_number: int) -> str:
        """Build a comprehensive prompt for generating a FULL SLIDE IMAGE."""
        
        industry = company_data.get('industry', '') if company_data else ''
        
        prompt = f"""Create a complete professional pitch deck slide image for {company_name}.

Slide {slide_number}: {title}

Content:
{content}

Key Points:
{chr(10).join(f"- {point}" for point in key_points) if key_points else "None"}

Industry: {industry}

Design a complete slide image with:
- Professional business presentation layout (16:9 landscape)
- Slide title at the top
- Content sections with text
- Visual elements (charts, icons, diagrams if relevant)
- Modern, clean design suitable for investors
- Professional color scheme (blues, whites, accent colors)
- All text readable and well-formatted
- High quality, presentation-ready image

The image should be a complete, ready-to-use slide that can be inserted into a PowerPoint presentation."""
        
        return prompt
    
    def _build_image_prompt(self, title: str, content: str, key_points: List[str],
                           company_name: str, company_data: Optional[Dict] = None) -> str:
        """Build a detailed image prompt from slide information."""
        
        # Extract industry/theme from company data
        industry = company_data.get('industry', '') if company_data else ''
        
        # Build comprehensive prompt
        prompt_parts = [
            f"Professional pitch deck illustration for {company_name}",
            f"Slide topic: {title}",
        ]
        
        if industry:
            prompt_parts.append(f"Industry: {industry}")
        
        if content:
            # Extract key concepts from content
            prompt_parts.append(f"Context: {content[:100]}...")
        
        if key_points:
            prompt_parts.append(f"Key themes: {', '.join(key_points[:3])}")
        
        prompt_parts.extend([
            "Style: Modern, professional, business presentation",
            "Mood: Confident, innovative, forward-thinking",
            "Color scheme: Professional blue and white with accent colors",
            "Format: Landscape, suitable for slide background"
        ])
        
        return ". ".join(prompt_parts)
    
    def _generate_with_imagen(self, prompt: str, slide_number: int) -> Optional[str]:
        """
        Try to generate image using Google Imagen API or Vertex AI.
        
        Args:
            prompt: Image generation prompt
            slide_number: Slide number for filename
            
        Returns:
            Path to generated image, or None if not available
        """
        try:
            # Try Vertex AI Imagen API
            try:
                import vertexai
                from vertexai.preview import vision_models
                
                # Check if Vertex AI is configured
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
                location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
                
                if project_id:
                    vertexai.init(project=project_id, location=location)
                    imagen_model = vision_models.ImageGenerationModel.from_pretrained("imagegeneration@006")
                    
                    # Generate image
                    response = imagen_model.generate_images(
                        prompt=prompt,
                        number_of_images=1,
                        aspect_ratio="16:9",  # Landscape for slides
                        safety_filter_level="block_some",
                        person_generation="allow_all"
                    )
                    
                    if response.images:
                        image_path = self.output_dir / f"slide_{slide_number}_imagen_{int(time.time())}.png"
                        response.images[0].save(str(image_path))
                        logger.info(f"✅ Generated image with Vertex AI Imagen: {image_path}")
                        return str(image_path)
            except ImportError:
                logger.debug("Vertex AI not available - install with: pip install google-cloud-aiplatform")
            except Exception as e:
                logger.debug(f"Vertex AI Imagen not available: {e}")
            
            # Try Google AI Studio Imagen (if available via API)
            # Note: This might require different setup
            
            return None
        except Exception as e:
            logger.debug(f"Imagen API not available: {e}")
            return None
    
    def _extract_keywords_from_prompt(self, prompt: str) -> List[str]:
        """Extract search keywords from an image prompt."""
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", 
                     "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
                     "will", "would", "should", "could", "may", "might", "must", "can", "professional", "business",
                     "style", "mood", "color", "scheme", "format", "suitable", "for", "slide", "background"}
        
        words = prompt.lower().replace(",", " ").replace(".", " ").split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return top 5 keywords
        return keywords[:5]
    
    def generate_images_for_slides(self, slides: List[Dict], company_name: str,
                                    company_data: Optional[Dict] = None) -> Dict[int, Optional[str]]:
        """
        Generate FULL SLIDE IMAGES for all slides in batch.
        Each image is a complete slide that can be stitched into PPT.
        
        Args:
            slides: List of slide dictionaries
            company_name: Company name
            company_data: Optional company data
            
        Returns:
            Dictionary mapping slide_number to image path (or None if failed)
        """
        if not self.enabled:
            logger.warning("Gemini image generation disabled")
            return {slide.get('slide_number', i): None for i, slide in enumerate(slides)}
        
        logger.info(f"🎨 Generating FULL SLIDE IMAGES for {len(slides)} slides using Gemini...")
        logger.info("💡 Each image will be a complete slide that can be stitched into PPT")
        
        results = {}
        for slide in slides:
            slide_num = slide.get('slide_number', slides.index(slide) + 1)
            try:
                image_path = self.generate_image_for_slide(slide, company_name, company_data)
                results[slide_num] = image_path
                if image_path:
                    logger.info(f"✅ Generated FULL SLIDE IMAGE for slide {slide_num}: {slide.get('title', 'Unknown')}")
                else:
                    logger.warning(f"⚠️ Could not generate image for slide {slide_num} (description saved)")
            except Exception as e:
                logger.error(f"Error generating image for slide {slide_num}: {e}")
                results[slide_num] = None
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        generated_count = len([p for p in results.values() if p])
        logger.info(f"✅ Generated {generated_count} out of {len(slides)} full slide images")
        
        if generated_count > 0:
            logger.info("💡 Ready to stitch images into PowerPoint!")
        
        return results

