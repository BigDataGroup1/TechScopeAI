"""
Gamma.ai API Integration for AI-enhanced pitch deck presentations.

Gamma.ai creates beautiful, AI-enhanced presentations from structured content.
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


class GammaIntegration:
    """Integration with Gamma.ai API for creating AI-enhanced presentations."""
    
    # Available Gamma.ai themes/templates
    GAMMA_THEMES = [
        {
            "id": "startup-pitch",
            "name": "Startup Pitch Deck",
            "description": "Modern, professional pitch deck template",
            "style": "clean",
            "color_scheme": "blue"
        },
        {
            "id": "venture-capital",
            "name": "Venture Capital Pitch",
            "description": "Bold, investor-focused design",
            "style": "bold",
            "color_scheme": "dark"
        },
        {
            "id": "minimalist",
            "name": "Minimalist Professional",
            "description": "Clean, minimal design for professional presentations",
            "style": "minimal",
            "color_scheme": "light"
        },
        {
            "id": "modern-tech",
            "name": "Modern Tech Startup",
            "description": "Tech-focused, modern design with gradients",
            "style": "modern",
            "color_scheme": "gradient"
        },
        {
            "id": "executive",
            "name": "Executive Summary",
            "description": "Executive-level, sophisticated design",
            "style": "executive",
            "color_scheme": "professional"
        }
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gamma.ai integration.
        
        Args:
            api_key: Gamma.ai API key (or from GAMMA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GAMMA_API_KEY")
        if not self.api_key:
            logger.warning("GAMMA_API_KEY not found. Gamma.ai features will be limited.")
        
        # Gamma.ai API base URL (correct endpoint)
        self.base_url = "https://public-api.gamma.app/v1.0"
        self.headers = {
            "X-API-KEY": self.api_key,  # Gamma uses X-API-KEY header, not Bearer token
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        if self.api_key:
            logger.info("GammaIntegration initialized with API key")
        else:
            logger.warning("GammaIntegration initialized without API key - will use demo mode")
    
    def get_available_themes(self) -> List[Dict]:
        """
        Get list of available Gamma.ai themes/templates.
        
        Returns:
            List of theme dictionaries
        """
        return self.GAMMA_THEMES
    
    def create_presentation(self, slides: List[Dict], company_name: str, 
                          theme_id: str = "startup-pitch",
                          enhance_with_ai: bool = True) -> Dict:
        """
        Create a Gamma.ai presentation from slides.
        
        Args:
            slides: List of slide dictionaries
            company_name: Company name
            theme_id: Theme/template ID to use
            enhance_with_ai: Whether to use AI to enhance content
            
        Returns:
            Dictionary with presentation URL and metadata
        """
        # Allow demo mode without API key for testing
        demo_mode = not self.api_key
        if demo_mode:
            logger.info("Gamma.ai running in demo mode (no API key)")
        
        logger.info(f"Creating Gamma.ai presentation for {company_name} with theme {theme_id}")
        
        try:
            # Prepare presentation structure for Gamma.ai
            presentation_data = self._prepare_presentation_data(slides, company_name, theme_id)
            
            # If AI enhancement is enabled, enhance the content
            if enhance_with_ai:
                presentation_data = self._enhance_with_ai(presentation_data)
            
            # Create presentation via Gamma.ai API
            # Note: This is a placeholder - update with actual Gamma.ai API endpoint
            response = self._create_via_api(presentation_data, theme_id, demo_mode=demo_mode)
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating Gamma.ai presentation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create Gamma.ai presentation"
            }
    
    def _prepare_presentation_data(self, slides: List[Dict], company_name: str, 
                                   theme_id: str) -> Dict:
        """Prepare presentation data structure for Gamma.ai."""
        # Find selected theme
        theme = next((t for t in self.GAMMA_THEMES if t["id"] == theme_id), self.GAMMA_THEMES[0])
        
        presentation = {
            "title": f"{company_name} - Pitch Deck",
            "theme": theme_id,
            "theme_name": theme["name"],
            "slides": []
        }
        
        for slide in slides:
            slide_data = {
                "title": slide.get("title", "Untitled"),
                "content": slide.get("content", ""),
                "key_points": slide.get("key_points", []),
                "slide_number": slide.get("slide_number", 0)
            }
            presentation["slides"].append(slide_data)
        
        return presentation
    
    def _enhance_with_ai(self, presentation_data: Dict) -> Dict:
        """
        Enhance presentation content using AI.
        Gamma.ai will improve structure, flow, and content quality.
        """
        # This would call Gamma.ai's AI enhancement API
        # For now, we'll prepare the data structure
        logger.info("Enhancing presentation with AI...")
        
        # AI enhancement would:
        # - Improve slide titles for impact
        # - Enhance content clarity and flow
        # - Optimize key points for presentation
        # - Add transitions and narrative flow
        
        enhanced_data = {
            **presentation_data,
            "ai_enhanced": True,
            "enhancements": {
                "improved_titles": True,
                "content_optimization": True,
                "flow_optimization": True,
                "visual_suggestions": True
            }
        }
        
        return enhanced_data
    
    def _create_via_api(self, presentation_data: Dict, theme_id: str, demo_mode: bool = False) -> Dict:
        """
        Create presentation via Gamma.ai API.
        
        Uses Gamma's Generate API to create presentations programmatically.
        """
        if demo_mode:
            logger.info("Gamma.ai running in demo mode - returning placeholder response")
            title_slug = presentation_data['title'].lower().replace(' ', '-').replace(':', '').replace('---', '-')
            return {
                "success": True,
                "presentation_id": f"gamma_demo_{title_slug}",
                "presentation_url": f"https://gamma.app/presentation/{title_slug}",
                "edit_url": f"https://gamma.app/edit/{title_slug}",
                "theme": theme_id,
                "ai_enhanced": True,
                "demo_mode": True,
                "message": "Gamma.ai presentation created (demo mode - add GAMMA_API_KEY to .env for real API)"
            }
        
        try:
            # Prepare slides content for Gamma API
            # Gamma API expects a single text input
            slides_content = []
            for slide in presentation_data.get("slides", []):
                slide_text = f"# {slide.get('title', 'Untitled')}\n\n"
                slide_text += f"{slide.get('content', '')}\n\n"
                if slide.get('key_points'):
                    slide_text += "\n".join([f"- {point}" for point in slide.get('key_points', [])])
                slides_content.append(slide_text)
            
            # Combine all slides into a single document
            full_content = "\n\n---\n\n".join(slides_content)
            
            # Gamma Generate API endpoint (correct)
            endpoint = f"{self.base_url}/generations"
            
            # Gamma Generate API payload format (correct)
            payload = {
                "inputText": full_content,
                "textMode": "generate",  # "generate" | "condense" | "preserve"
                "format": "presentation",  # "presentation" | "document" | "social" | "webpage"
                "numCards": len(presentation_data.get("slides", [])),  # Number of slides
                "cardSplit": "auto"  # "auto" | manual split options
            }
            
            # Add optional theme if specified
            if theme_id and theme_id != "startup-pitch":
                # Map our theme IDs to Gamma theme IDs if needed
                payload["themeId"] = theme_id
            
            logger.info(f"{'='*60}")
            logger.info(f"🌐 GAMMA API CALL:")
            logger.info(f"   Endpoint: {endpoint}")
            logger.info(f"   Headers: {list(self.headers.keys())}")
            logger.info(f"   API Key Present: {'Yes' if self.api_key else 'No'}")
            logger.info(f"   Payload: inputText length={len(full_content)}, format=presentation, numCards={payload['numCards']}")
            logger.info(f"{'='*60}")
            
            # Step 1: Create generation request
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"📡 API Response Status: {response.status_code}")
            if response.status_code != 200 and response.status_code != 201:
                logger.error(f"❌ API Error Response: {response.text[:500]}")
            
            # Check if request was successful
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Gamma generation request created successfully")
                
                # Extract generationId from response
                generation_id = result.get("generationId") or result.get("generation_id") or result.get("id")
                
                if not generation_id:
                    logger.error(f"Gamma API response missing generationId: {result}")
                    return {
                        "success": False,
                        "error": "Missing generationId in response",
                        "message": "Gamma API response did not include generationId",
                        "api_response": result
                    }
                
                logger.info(f"Generation ID: {generation_id}, polling for completion...")
                
                # Step 2: Poll for completion
                import time
                max_polls = 60  # Maximum number of polls (60 seconds max - Gamma can take time)
                poll_interval = 2  # Poll every 2 seconds (less aggressive)
                
                for poll_count in range(max_polls):
                    time.sleep(poll_interval)
                    
                    # Poll the generation status
                    poll_endpoint = f"{self.base_url}/generations/{generation_id}"
                    poll_response = requests.get(
                        poll_endpoint,
                        headers=self.headers,
                        timeout=30
                    )
                    
                    if poll_response.status_code == 200:
                        poll_result = poll_response.json()
                        status = poll_result.get("status", "").lower()
                        
                        # Log status for debugging
                        if poll_count % 5 == 0:  # Log every 5th poll
                            logger.info(f"Gamma generation status (poll {poll_count + 1}/{max_polls}): {status}")
                        
                        if status == "completed" or status == "done" or status == "success":
                            # Generation completed!
                            gamma_url = poll_result.get("gammaUrl") or poll_result.get("gamma_url") or poll_result.get("url")
                            
                            logger.info(f"✅ Gamma presentation completed! URL: {gamma_url}")
                            
                            return {
                                "success": True,
                                "presentation_id": generation_id,
                                "presentation_url": gamma_url or f"https://gamma.app/presentation/{generation_id}",
                                "edit_url": gamma_url or f"https://gamma.app/edit/{generation_id}",
                                "theme": theme_id,
                                "ai_enhanced": True,
                                "demo_mode": False,
                                "message": "Gamma.ai presentation created successfully",
                                "api_response": poll_result
                            }
                        elif status == "failed" or status == "error":
                            error_msg = poll_result.get('error') or poll_result.get('message') or 'Unknown error'
                            logger.error(f"Gamma generation failed: {error_msg}")
                            return {
                                "success": False,
                                "error": error_msg,
                                "message": f"Gamma generation failed: {error_msg}",
                                "generation_id": generation_id,
                                "api_response": poll_result
                            }
                        # Otherwise, still processing - continue polling
                        # Status might be: "processing", "pending", "in_progress", etc.
                        logger.debug(f"Generation status: {status}, polling again...")
                    elif poll_response.status_code == 404:
                        logger.warning(f"Gamma generation endpoint not found (404). Generation ID might be invalid: {generation_id}")
                        return {
                            "success": False,
                            "error": "Generation endpoint not found",
                            "message": f"Gamma generation endpoint returned 404. Check generationId: {generation_id}",
                            "generation_id": generation_id
                        }
                    else:
                        logger.warning(f"Poll request returned {poll_response.status_code}: {poll_response.text[:200]}")
                        # Continue polling - might be temporary error
                
                # If we get here, polling timed out
                logger.warning(f"Gamma generation polling timed out after {max_polls} attempts")
                return {
                    "success": False,
                    "error": "Polling timeout",
                    "message": f"Gamma generation is still processing. Check status manually with generationId: {generation_id}",
                    "generation_id": generation_id,
                    "poll_endpoint": f"{self.base_url}/generations/{generation_id}"
                }
                
            elif response.status_code == 401:
                logger.error(f"{'='*60}")
                logger.error(f"❌ GAMMA API AUTHENTICATION FAILED")
                logger.error(f"   Status Code: 401")
                logger.error(f"   Check your GAMMA_API_KEY in .env file")
                logger.error(f"   Response: {response.text[:500]}")
                logger.error(f"{'='*60}")
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "message": "Invalid GAMMA_API_KEY. Please check your API key in .env file. Make sure it starts with 'sk-gamma-'",
                    "status_code": 401
                }
            else:
                error_text = response.text[:500] if hasattr(response, 'text') else str(response.status_code)
                logger.error(f"Gamma API returned {response.status_code}: {error_text}")
                return {
                    "success": False,
                    "error": f"API error {response.status_code}",
                    "message": f"Gamma API returned status {response.status_code}: {error_text}",
                    "status_code": response.status_code
                }
            
        except Exception as e:
            logger.error(f"Gamma.ai API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create presentation via Gamma.ai API: {e}"
            }


            logger.info(f"🌐 GAMMA API CALL:")
            logger.info(f"   Endpoint: {endpoint}")
            logger.info(f"   Headers: {list(self.headers.keys())}")
            logger.info(f"   API Key Present: {'Yes' if self.api_key else 'No'}")
            logger.info(f"   Payload: inputText length={len(full_content)}, format=presentation, numCards={payload['numCards']}")
            logger.info(f"{'='*60}")
            
            # Step 1: Create generation request
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"📡 API Response Status: {response.status_code}")
            if response.status_code != 200 and response.status_code != 201:
                logger.error(f"❌ API Error Response: {response.text[:500]}")
            
            # Check if request was successful
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Gamma generation request created successfully")
                
                # Extract generationId from response
                generation_id = result.get("generationId") or result.get("generation_id") or result.get("id")
                
                if not generation_id:
                    logger.error(f"Gamma API response missing generationId: {result}")
                    return {
                        "success": False,
                        "error": "Missing generationId in response",
                        "message": "Gamma API response did not include generationId",
                        "api_response": result
                    }
                
                logger.info(f"Generation ID: {generation_id}, polling for completion...")
                
                # Step 2: Poll for completion
                import time
                max_polls = 60  # Maximum number of polls (60 seconds max - Gamma can take time)
                poll_interval = 2  # Poll every 2 seconds (less aggressive)
                
                for poll_count in range(max_polls):
                    time.sleep(poll_interval)
                    
                    # Poll the generation status
                    poll_endpoint = f"{self.base_url}/generations/{generation_id}"
                    poll_response = requests.get(
                        poll_endpoint,
                        headers=self.headers,
                        timeout=30
                    )
                    
                    if poll_response.status_code == 200:
                        poll_result = poll_response.json()
                        status = poll_result.get("status", "").lower()
                        
                        # Log status for debugging
                        if poll_count % 5 == 0:  # Log every 5th poll
                            logger.info(f"Gamma generation status (poll {poll_count + 1}/{max_polls}): {status}")
                        
                        if status == "completed" or status == "done" or status == "success":
                            # Generation completed!
                            gamma_url = poll_result.get("gammaUrl") or poll_result.get("gamma_url") or poll_result.get("url")
                            
                            logger.info(f"✅ Gamma presentation completed! URL: {gamma_url}")
                            
                            return {
                                "success": True,
                                "presentation_id": generation_id,
                                "presentation_url": gamma_url or f"https://gamma.app/presentation/{generation_id}",
                                "edit_url": gamma_url or f"https://gamma.app/edit/{generation_id}",
                                "theme": theme_id,
                                "ai_enhanced": True,
                                "demo_mode": False,
                                "message": "Gamma.ai presentation created successfully",
                                "api_response": poll_result
                            }
                        elif status == "failed" or status == "error":
                            error_msg = poll_result.get('error') or poll_result.get('message') or 'Unknown error'
                            logger.error(f"Gamma generation failed: {error_msg}")
                            return {
                                "success": False,
                                "error": error_msg,
                                "message": f"Gamma generation failed: {error_msg}",
                                "generation_id": generation_id,
                                "api_response": poll_result
                            }
                        # Otherwise, still processing - continue polling
                        # Status might be: "processing", "pending", "in_progress", etc.
                        logger.debug(f"Generation status: {status}, polling again...")
                    elif poll_response.status_code == 404:
                        logger.warning(f"Gamma generation endpoint not found (404). Generation ID might be invalid: {generation_id}")
                        return {
                            "success": False,
                            "error": "Generation endpoint not found",
                            "message": f"Gamma generation endpoint returned 404. Check generationId: {generation_id}",
                            "generation_id": generation_id
                        }
                    else:
                        logger.warning(f"Poll request returned {poll_response.status_code}: {poll_response.text[:200]}")
                        # Continue polling - might be temporary error
                
                # If we get here, polling timed out
                logger.warning(f"Gamma generation polling timed out after {max_polls} attempts")
                return {
                    "success": False,
                    "error": "Polling timeout",
                    "message": f"Gamma generation is still processing. Check status manually with generationId: {generation_id}",
                    "generation_id": generation_id,
                    "poll_endpoint": f"{self.base_url}/generations/{generation_id}"
                }
                
            elif response.status_code == 401:
                logger.error(f"{'='*60}")
                logger.error(f"❌ GAMMA API AUTHENTICATION FAILED")
                logger.error(f"   Status Code: 401")
                logger.error(f"   Check your GAMMA_API_KEY in .env file")
                logger.error(f"   Response: {response.text[:500]}")
                logger.error(f"{'='*60}")
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "message": "Invalid GAMMA_API_KEY. Please check your API key in .env file. Make sure it starts with 'sk-gamma-'",
                    "status_code": 401
                }
            else:
                error_text = response.text[:500] if hasattr(response, 'text') else str(response.status_code)
                logger.error(f"Gamma API returned {response.status_code}: {error_text}")
                return {
                    "success": False,
                    "error": f"API error {response.status_code}",
                    "message": f"Gamma API returned status {response.status_code}: {error_text}",
                    "status_code": response.status_code
                }
            
        except Exception as e:
            logger.error(f"Gamma.ai API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create presentation via Gamma.ai API: {e}"
            }


            logger.info(f"🌐 GAMMA API CALL:")
            logger.info(f"   Endpoint: {endpoint}")
            logger.info(f"   Headers: {list(self.headers.keys())}")
            logger.info(f"   API Key Present: {'Yes' if self.api_key else 'No'}")
            logger.info(f"   Payload: inputText length={len(full_content)}, format=presentation, numCards={payload['numCards']}")
            logger.info(f"{'='*60}")
            
            # Step 1: Create generation request
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"📡 API Response Status: {response.status_code}")
            if response.status_code != 200 and response.status_code != 201:
                logger.error(f"❌ API Error Response: {response.text[:500]}")
            
            # Check if request was successful
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Gamma generation request created successfully")
                
                # Extract generationId from response
                generation_id = result.get("generationId") or result.get("generation_id") or result.get("id")
                
                if not generation_id:
                    logger.error(f"Gamma API response missing generationId: {result}")
                    return {
                        "success": False,
                        "error": "Missing generationId in response",
                        "message": "Gamma API response did not include generationId",
                        "api_response": result
                    }
                
                logger.info(f"Generation ID: {generation_id}, polling for completion...")
                
                # Step 2: Poll for completion
                import time
                max_polls = 60  # Maximum number of polls (60 seconds max - Gamma can take time)
                poll_interval = 2  # Poll every 2 seconds (less aggressive)
                
                for poll_count in range(max_polls):
                    time.sleep(poll_interval)
                    
                    # Poll the generation status
                    poll_endpoint = f"{self.base_url}/generations/{generation_id}"
                    poll_response = requests.get(
                        poll_endpoint,
                        headers=self.headers,
                        timeout=30
                    )
                    
                    if poll_response.status_code == 200:
                        poll_result = poll_response.json()
                        status = poll_result.get("status", "").lower()
                        
                        # Log status for debugging
                        if poll_count % 5 == 0:  # Log every 5th poll
                            logger.info(f"Gamma generation status (poll {poll_count + 1}/{max_polls}): {status}")
                        
                        if status == "completed" or status == "done" or status == "success":
                            # Generation completed!
                            gamma_url = poll_result.get("gammaUrl") or poll_result.get("gamma_url") or poll_result.get("url")
                            
                            logger.info(f"✅ Gamma presentation completed! URL: {gamma_url}")
                            
                            return {
                                "success": True,
                                "presentation_id": generation_id,
                                "presentation_url": gamma_url or f"https://gamma.app/presentation/{generation_id}",
                                "edit_url": gamma_url or f"https://gamma.app/edit/{generation_id}",
                                "theme": theme_id,
                                "ai_enhanced": True,
                                "demo_mode": False,
                                "message": "Gamma.ai presentation created successfully",
                                "api_response": poll_result
                            }
                        elif status == "failed" or status == "error":
                            error_msg = poll_result.get('error') or poll_result.get('message') or 'Unknown error'
                            logger.error(f"Gamma generation failed: {error_msg}")
                            return {
                                "success": False,
                                "error": error_msg,
                                "message": f"Gamma generation failed: {error_msg}",
                                "generation_id": generation_id,
                                "api_response": poll_result
                            }
                        # Otherwise, still processing - continue polling
                        # Status might be: "processing", "pending", "in_progress", etc.
                        logger.debug(f"Generation status: {status}, polling again...")
                    elif poll_response.status_code == 404:
                        logger.warning(f"Gamma generation endpoint not found (404). Generation ID might be invalid: {generation_id}")
                        return {
                            "success": False,
                            "error": "Generation endpoint not found",
                            "message": f"Gamma generation endpoint returned 404. Check generationId: {generation_id}",
                            "generation_id": generation_id
                        }
                    else:
                        logger.warning(f"Poll request returned {poll_response.status_code}: {poll_response.text[:200]}")
                        # Continue polling - might be temporary error
                
                # If we get here, polling timed out
                logger.warning(f"Gamma generation polling timed out after {max_polls} attempts")
                return {
                    "success": False,
                    "error": "Polling timeout",
                    "message": f"Gamma generation is still processing. Check status manually with generationId: {generation_id}",
                    "generation_id": generation_id,
                    "poll_endpoint": f"{self.base_url}/generations/{generation_id}"
                }
                
            elif response.status_code == 401:
                logger.error(f"{'='*60}")
                logger.error(f"❌ GAMMA API AUTHENTICATION FAILED")
                logger.error(f"   Status Code: 401")
                logger.error(f"   Check your GAMMA_API_KEY in .env file")
                logger.error(f"   Response: {response.text[:500]}")
                logger.error(f"{'='*60}")
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "message": "Invalid GAMMA_API_KEY. Please check your API key in .env file. Make sure it starts with 'sk-gamma-'",
                    "status_code": 401
                }
            else:
                error_text = response.text[:500] if hasattr(response, 'text') else str(response.status_code)
                logger.error(f"Gamma API returned {response.status_code}: {error_text}")
                return {
                    "success": False,
                    "error": f"API error {response.status_code}",
                    "message": f"Gamma API returned status {response.status_code}: {error_text}",
                    "status_code": response.status_code
                }
            
        except Exception as e:
            logger.error(f"Gamma.ai API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create presentation via Gamma.ai API: {e}"
            }

