"""Canva API integration for presentation generation."""

import logging
import requests
import json
from typing import Dict, Optional
from pathlib import Path
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class CanvaAPI:
    """Canva API client for generating presentations."""
    
    BASE_URL = "https://api.canva.com/rest/v1"
    
    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        """
        Initialize Canva API client.
        
        Args:
            api_key: Canva API key (from .env)
            access_token: Canva OAuth access token (from .env)
        """
        self.api_key = api_key or os.getenv("CANVA_API_KEY")
        self.access_token = access_token or os.getenv("CANVA_ACCESS_TOKEN")
        
        if not self.api_key and not self.access_token:
            logger.warning("Canva API credentials not found. Set CANVA_API_KEY or CANVA_ACCESS_TOKEN in .env")
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}" if self.access_token else f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if (self.access_token or self.api_key) else {}
        
        logger.info("CanvaAPI initialized")
    
    def generate_presentation(self, company_data: Dict, template_id: Optional[str] = None,
                            output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate presentation using Canva API.
        
        Args:
            company_data: Company information dictionary
            template_id: Optional Canva template ID
            output_path: Optional output path for downloaded PPT
            
        Returns:
            Path to downloaded PowerPoint file or None
        """
        if not self.access_token and not self.api_key:
            logger.error("Canva API credentials not set. Cannot generate presentation.")
            return None
        
        try:
            # Canva API: Create design from template
            # Note: Canva API workflow may require:
            # 1. Create design from template
            # 2. Update design with content
            # 3. Export as PowerPoint
            
            # Step 1: Create design
            design_id = self._create_design(template_id)
            if not design_id:
                return None
            
            # Step 2: Update design with content
            self._update_design_content(design_id, company_data)
            
            # Step 3: Export as PowerPoint
            return self._export_presentation(design_id, output_path, company_data)
            
        except Exception as e:
            logger.error(f"Error generating Canva presentation: {e}")
            return None
    
    def _create_design(self, template_id: Optional[str] = None) -> Optional[str]:
        """Create a new design from template."""
        try:
            url = f"{self.BASE_URL}/designs"
            
            payload = {
                "type": "presentation",
                "width": 1920,
                "height": 1080
            }
            
            if template_id:
                payload["template_id"] = template_id
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                design_id = result.get("id") or result.get("design_id")
                logger.info(f"Canva design created: {design_id}")
                return design_id
            else:
                logger.error(f"Canva API error creating design: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Canva design: {e}")
            return None
    
    def _update_design_content(self, design_id: str, company_data: Dict):
        """Update design with company content."""
        try:
            # Canva API: Update design elements
            # This is a simplified version - actual implementation depends on Canva API structure
            url = f"{self.BASE_URL}/designs/{design_id}/elements"
            
            # Format content for Canva
            content = self._format_company_data_for_canva(company_data)
            
            # Update design (simplified - actual API may differ)
            payload = {
                "elements": content
            }
            
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code in [200, 204]:
                logger.info(f"Canva design content updated")
            else:
                logger.warning(f"Canva API warning updating content: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Error updating Canva design content: {e}")
            # Continue even if update fails
    
    def _format_company_data_for_canva(self, company_data: Dict) -> list:
        """Format company data for Canva API."""
        # Simplified structure - actual Canva API structure may differ
        elements = [
            {"type": "text", "content": company_data.get('company_name', 'Company')},
            {"type": "text", "content": company_data.get('problem', 'Problem')},
            {"type": "text", "content": company_data.get('solution', 'Solution')},
            {"type": "text", "content": company_data.get('traction', 'Traction')},
        ]
        return elements
    
    def _export_presentation(self, design_id: str, output_path: Optional[str], company_data: Dict) -> Optional[str]:
        """Export design as PowerPoint."""
        try:
            url = f"{self.BASE_URL}/designs/{design_id}/exports"
            
            payload = {
                "format": "pptx",
                "quality": "high"
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            
            if response.status_code in [200, 202]:
                result = response.json()
                
                # Check if export is ready or needs polling
                if "url" in result:
                    # Download immediately
                    return self._download_presentation(result["url"], output_path, company_data)
                elif "export_id" in result:
                    # Poll for export completion
                    return self._poll_export(result["export_id"], output_path, company_data)
                else:
                    logger.error(f"Unexpected export response: {result}")
                    return None
            else:
                logger.error(f"Canva API error exporting: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error exporting Canva presentation: {e}")
            return None
    
    def _poll_export(self, export_id: str, output_path: Optional[str], company_data: Dict) -> Optional[str]:
        """Poll for export completion."""
        import time
        
        url = f"{self.BASE_URL}/exports/{export_id}"
        
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("status") == "completed":
                        if "url" in result:
                            return self._download_presentation(result["url"], output_path, company_data)
                    elif result.get("status") == "failed":
                        logger.error("Canva export failed")
                        return None
                    else:
                        # Still processing
                        time.sleep(2)
                        continue
                        
            except Exception as e:
                logger.warning(f"Error polling export: {e}")
                time.sleep(2)
        
        logger.error("Canva export timeout")
        return None
    
    def _download_presentation(self, url: str, output_path: Optional[str], company_data: Dict) -> str:
        """Download presentation from URL."""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            if not output_path:
                output_dir = Path("comparisons/canva")
                output_dir.mkdir(parents=True, exist_ok=True)
                company_name = company_data.get('company_name', 'Company').replace(' ', '_')
                output_path = output_dir / f"{company_name}_canva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Canva presentation downloaded: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error downloading Canva presentation: {e}")
            return None


