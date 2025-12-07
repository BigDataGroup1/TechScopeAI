"""Gamma.ai API integration for presentation generation."""

import logging
import requests
import json
import os
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class GammaAPI:
    """Gamma.ai API client for generating presentations."""
    
    BASE_URL = "https://public-api.gamma.app/v1.0"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gamma.ai API client.
        
        Args:
            api_key: Gamma.ai API key (from .env or passed directly)
        """
        self.api_key = api_key or os.getenv("GAMMA_API_KEY")
        if not self.api_key:
            logger.warning("Gamma.ai API key not found. Set GAMMA_API_KEY in .env")
        
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        logger.info("GammaAPI initialized")
    
    def generate_presentation(self, company_data: Dict, output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate presentation using Gamma.ai API.
        
        Args:
            company_data: Company information dictionary
            output_path: Optional output path for downloaded PPT
            
        Returns:
            Path to downloaded PowerPoint file or None
        """
        if not self.api_key:
            logger.error("Gamma.ai API key not set. Cannot generate presentation.")
            return None
        
        try:
            # Prepare prompt/content for Gamma.ai
            prompt = self._format_company_data_for_gamma(company_data)
            
            # Gamma.ai Generate API endpoint
            url = f"{self.BASE_URL}/generate"
            
            # Request payload
            payload = {
                "prompt": prompt,
                "format": "pptx",  # PowerPoint format
                "theme": "professional",  # Can be: professional, modern, creative, etc.
                "slides": 12  # Number of slides
            }
            
            logger.info("Sending request to Gamma.ai API...")
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Gamma.ai returns a URL or file data
                if "url" in result:
                    # Download the presentation
                    ppt_url = result["url"]
                    return self._download_presentation(ppt_url, output_path, company_data)
                elif "file" in result:
                    # Save file data directly
                    return self._save_file_data(result["file"], output_path, company_data)
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return None
            else:
                logger.error(f"Gamma.ai API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating Gamma.ai presentation: {e}")
            return None
    
    def _format_company_data_for_gamma(self, company_data: Dict) -> str:
        """Format company data as prompt for Gamma.ai."""
        prompt = f"""Create a professional pitch deck presentation for:

Company: {company_data.get('company_name', 'Unknown')}
Industry: {company_data.get('industry', 'N/A')}
Problem: {company_data.get('problem', 'N/A')}
Solution: {company_data.get('solution', 'N/A')}
Target Market: {company_data.get('target_market', 'N/A')}
Market Size: {company_data.get('market_size', 'N/A')}
Traction: {company_data.get('traction', 'N/A')}
Funding Goal: {company_data.get('funding_goal', 'N/A')}
Team: {company_data.get('founders', 'N/A')}

Create a compelling pitch deck with professional slides covering:
1. Title slide
2. Problem
3. Solution
4. Market opportunity
5. Business model
6. Traction
7. Competitive advantage
8. Team
9. Financials
10. The Ask
11. Vision
"""
        return prompt
    
    def _download_presentation(self, url: str, output_path: Optional[str], company_data: Dict) -> str:
        """Download presentation from URL."""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            if not output_path:
                output_dir = Path("comparisons/gamma_ai")
                output_dir.mkdir(parents=True, exist_ok=True)
                company_name = company_data.get('company_name', 'Company').replace(' ', '_')
                output_path = output_dir / f"{company_name}_gamma_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Gamma.ai presentation downloaded: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error downloading Gamma.ai presentation: {e}")
            return None
    
    def _save_file_data(self, file_data: bytes, output_path: Optional[str], company_data: Dict) -> str:
        """Save file data directly."""
        try:
            if not output_path:
                output_dir = Path("comparisons/gamma_ai")
                output_dir.mkdir(parents=True, exist_ok=True)
                company_name = company_data.get('company_name', 'Company').replace(' ', '_')
                output_path = output_dir / f"{company_name}_gamma_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
            
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Gamma.ai presentation saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving Gamma.ai presentation: {e}")
            return None

