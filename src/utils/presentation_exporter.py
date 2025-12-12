"""
Export presentations for Gamma.ai and Canva import.

Creates downloadable files that can be imported into Gamma.ai and Canva.
Also creates beautiful HTML presentations with Gamma.ai and Canva styling.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PresentationExporter:
    """Export presentations in formats compatible with Gamma.ai and Canva."""
    
    def __init__(self):
        self.output_dir = Path("exports")
        self.output_dir.mkdir(exist_ok=True)
    
    def export_for_gamma(self, slides: List[Dict], company_name: str, theme: str = "startup-pitch") -> str:
        """
        Export slides in Gamma.ai compatible format.
        
        Creates a JSON file that can be imported into Gamma.ai or used with their API.
        """
        logger.info(f"Exporting {len(slides)} slides for Gamma.ai")
        
        # Format slides for Gamma.ai
        gamma_slides = []
        for slide in slides:
            gamma_slide = {
                "title": slide.get("title", "Untitled"),
                "content": slide.get("content", ""),
                "key_points": slide.get("key_points", []),
                "slide_number": slide.get("slide_number", 0)
            }
            gamma_slides.append(gamma_slide)
        
        gamma_data = {
            "presentation": {
                "title": f"{company_name} - Pitch Deck",
                "theme": theme,
                "created_at": datetime.now().isoformat(),
                "slides": gamma_slides
            },
            "metadata": {
                "company_name": company_name,
                "total_slides": len(slides),
                "export_format": "gamma_ai",
                "version": "1.0",
                "instructions": "Import this JSON into Gamma.ai to create an AI-enhanced presentation"
            }
        }
        
        # Save to file
        filename = f"{company_name.replace(' ', '_')}_gamma_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(gamma_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Gamma.ai export saved to: {filepath}")
        return str(filepath)
    
    def export_for_canva(self, slides: List[Dict], company_name: str, template: str = "pitch-deck-modern") -> str:
        """
        Export slides in Canva compatible format.
        
        Creates a JSON file that can be imported into Canva or used with their API.
        """
        logger.info(f"Exporting {len(slides)} slides for Canva")
        
        # Format slides for Canva
        canva_slides = []
        for slide in slides:
            canva_slide = {
                "title": slide.get("title", "Untitled"),
                "content": slide.get("content", ""),
                "key_points": slide.get("key_points", []),
                "slide_number": slide.get("slide_number", 0),
                "image_path": slide.get("image_path")  # Include image paths if available
            }
            canva_slides.append(canva_slide)
        
        canva_data = {
            "design": {
                "title": f"{company_name} - Pitch Deck",
                "template": template,
                "created_at": datetime.now().isoformat(),
                "slides": canva_slides
            },
            "metadata": {
                "company_name": company_name,
                "total_slides": len(slides),
                "export_format": "canva",
                "version": "1.0",
                "instructions": "Import this JSON into Canva to create a visually enhanced presentation"
            }
        }
        
        # Save to file
        filename = f"{company_name.replace(' ', '_')}_canva_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(canva_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Canva export saved to: {filepath}")
        return str(filepath)
    
    def export_html_preview(self, slides: List[Dict], company_name: str, presentation_type: str = "gamma") -> str:
        """
        Create a beautiful HTML preview of the presentation with Gamma.ai or Canva styling.
        
        This creates a local HTML file that can be viewed in a browser.
        """
        logger.info(f"Creating HTML preview for {presentation_type}")
        
        # Fix: Uppercase the presentation type once for use in format strings
        presentation_type_upper = presentation_type.upper()
        
        # Define theme colors based on presentation type
        if presentation_type.lower() == "gamma":
            primary_color = "#667eea"
            secondary_color = "#764ba2"
            accent_color = "#f093fb"
            gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            title_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        else:  # canva
            primary_color = "#00c4cc"
            secondary_color = "#00a8cc"
            accent_color = "#00d4ff"
            gradient = "linear-gradient(135deg, #00c4cc 0%, #00a8cc 100%)"
            title_gradient = "linear-gradient(135deg, #00c4cc 0%, #00a8cc 100%)"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - {presentation_type_upper} Presentation Preview</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: {gradient};
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}
        .header h1 {{
            background: {title_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 18px;
            margin-top: 10px;
        }}
        .header .meta {{
            color: #999;
            font-size: 14px;
            margin-top: 15px;
        }}
        .slide {{
            background: white;
            padding: 50px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }}
        .slide::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: {gradient};
        }}
        .slide-number {{
            color: #999;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .slide-title {{
            font-size: 36px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 25px;
            line-height: 1.2;
            background: {title_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .slide-content {{
            font-size: 20px;
            line-height: 1.8;
            color: #333;
            margin-bottom: 30px;
        }}
        .key-points {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 12px;
            margin-top: 30px;
            border-left: 4px solid {primary_color};
        }}
        .key-points h3 {{
            color: #1a1a1a;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: 600;
        }}
        .key-points ul {{
            list-style: none;
            padding-left: 0;
        }}
        .key-points li {{
            padding: 12px 0;
            padding-left: 35px;
            position: relative;
            font-size: 18px;
            line-height: 1.6;
            color: #333;
        }}
        .key-points li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: {primary_color};
            font-weight: bold;
            font-size: 24px;
            width: 28px;
            height: 28px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 50px;
            padding: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        .footer p {{
            font-size: 16px;
            line-height: 1.6;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .footer {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{company_name}</h1>
            <p class="subtitle">Pitch Deck Preview</p>
            <p class="meta">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} • {presentation_type_upper} Style</p>
        </div>
"""
        
        for slide in slides:
            html_content += f"""
        <div class="slide">
            <div class="slide-number">Slide {slide.get('slide_number', '?')} of {len(slides)}</div>
            <div class="slide-title">{slide.get('title', 'Untitled')}</div>
            <div class="slide-content">{slide.get('content', '').replace(chr(10), '<br>')}</div>
"""
            if slide.get('key_points'):
                html_content += """
            <div class="key-points">
                <h3>Key Points</h3>
                <ul>
"""
                for point in slide.get('key_points', []):
                    html_content += f"                    <li>{point}</li>\n"
                html_content += """
                </ul>
            </div>
"""
            html_content += """
        </div>
"""
        
        html_content += """
    </div>
    <div class="footer">
        <p><strong>Your Presentation - {presentation_type_upper} Style</strong></p>
        <p style="margin-top: 15px; font-size: 14px; opacity: 0.9;">You can print this page or save it as PDF for offline viewing.</p>
    </div>
</body>
</html>
""".format(presentation_type_upper=presentation_type_upper)
        
        # Save to file
        filename = f"{company_name.replace(' ', '_')}_{presentation_type}_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML preview saved to: {filepath}")
        return str(filepath)
