"""Export utilities for pitch decks."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PitchExporter:
    """Export pitch decks to various formats."""
    
    def __init__(self):
        self.output_dir = Path("exports")
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_markdown(self, slides: List[Dict], company_name: str) -> str:
        """Export slides to Markdown format."""
        logger.info(f"Exporting {len(slides)} slides to Markdown")
        
        md_content = f"# Pitch Deck: {company_name}\n\n"
        md_content += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        md_content += "---\n\n"
        
        for slide in slides:
            md_content += f"## Slide {slide.get('slide_number', '?')}: {slide.get('title', 'Untitled')}\n\n"
            
            content = slide.get('content', '')
            if content:
                md_content += f"{content}\n\n"
            
            key_points = slide.get('key_points', [])
            if key_points:
                md_content += "**Key Points:**\n"
                for point in key_points:
                    md_content += f"- {point}\n"
                md_content += "\n"
            
            md_content += "---\n\n"
        
        # Save to file
        filename = f"{company_name.replace(' ', '_')}_pitch_deck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Markdown exported to: {filepath}")
        return str(filepath)
    
    def export_to_pdf(self, slides: List[Dict], company_name: str) -> Optional[str]:
        """Export slides to PDF format."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            logger.info(f"Exporting {len(slides)} slides to PDF")
            
            filename = f"{company_name.replace(' ', '_')}_pitch_deck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = self.output_dir / filename
            
            doc = SimpleDocTemplate(str(filepath), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title style
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#1a1a1a',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Slide title style
            slide_title_style = ParagraphStyle(
                'SlideTitle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor='#2c3e50',
                spaceAfter=12,
                alignment=TA_LEFT
            )
            
            # Content style
            content_style = ParagraphStyle(
                'Content',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                spaceAfter=12,
                alignment=TA_LEFT
            )
            
            # Add title page
            story.append(Paragraph(f"<b>{company_name}</b>", title_style))
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("Pitch Deck", styles['Heading2']))
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
            story.append(PageBreak())
            
            # Add slides
            for slide in slides:
                slide_num = slide.get('slide_number', '?')
                title = slide.get('title', 'Untitled')
                
                story.append(Paragraph(f"Slide {slide_num}: {title}", slide_title_style))
                story.append(Spacer(1, 0.2*inch))
                
                content = slide.get('content', '')
                if content:
                    # Replace newlines with HTML breaks
                    content = content.replace('\n', '<br/>')
                    story.append(Paragraph(content, content_style))
                    story.append(Spacer(1, 0.15*inch))
                
                key_points = slide.get('key_points', [])
                if key_points:
                    story.append(Paragraph("<b>Key Points:</b>", styles['Heading3']))
                    for point in key_points:
                        story.append(Paragraph(f"• {point}", content_style))
                    story.append(Spacer(1, 0.15*inch))
                
                story.append(PageBreak())
            
            doc.build(story)
            logger.info(f"PDF exported to: {filepath}")
            return str(filepath)
            
        except ImportError:
            logger.warning("reportlab not installed. Install with: pip install reportlab")
            return None
    
    def export_to_powerpoint(self, slides: List[Dict], company_name: str, 
                           include_images: bool = True,
                           use_gamma_style: bool = True,
                           template: str = "modern") -> Optional[str]:
        """
        Export slides to PowerPoint format with professional styling.
        
        Args:
            slides: List of slide dictionaries
            company_name: Company name
            include_images: Whether to fetch and include images
            use_gamma_style: Whether to use Gamma.ai-style engine (default: True)
            template: Template name (modern, bold, corporate, startup)
            
        Returns:
            Path to created PowerPoint file
        """
        # Use Gamma-style engine if requested
        if use_gamma_style:
            try:
                from .gamma_ppt_engine import GammaPPTEngine
                logger.info(f"Using Gamma-style PPT engine with template: {template}")
                engine = GammaPPTEngine(template_name=template)
                prs = engine.create_presentation(
                    company_name=company_name,
                    slides=slides,
                    include_images=include_images,
                    include_charts=True
                )
                return engine.save_presentation(prs, company_name, self.output_dir)
            except Exception as e:
                logger.warning(f"Gamma engine failed, falling back to standard: {e}")
                # Fall through to standard implementation
        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt
            from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
            from pptx.dml.color import RGBColor
            from pptx.enum.shapes import MSO_SHAPE
            
            logger.info(f"Exporting {len(slides)} slides to PowerPoint (professional)")
            
            prs = Presentation()
            prs.slide_width = Inches(10)
            prs.slide_height = Inches(7.5)
            
            # Premium color scheme - modern and professional
            primary_color = RGBColor(30, 58, 138)  # Deep blue
            secondary_color = RGBColor(15, 23, 42)  # Navy
            accent_color = RGBColor(59, 130, 246)  # Bright blue
            highlight_color = RGBColor(34, 197, 94)  # Green accent
            text_color = RGBColor(30, 41, 59)  # Slate
            light_bg = RGBColor(248, 250, 252)  # Light gray background
            white = RGBColor(255, 255, 255)
            
            # Initialize image fetcher if needed
            image_fetcher = None
            if include_images:
                try:
                    from .image_fetcher import ImageFetcher
                    image_fetcher = ImageFetcher()
                except Exception as e:
                    logger.warning(f"Image fetcher not available: {e}")
                    include_images = False
            
            # Premium title slide design
            blank_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(blank_layout)
            
            # Full background gradient effect (using solid for now)
            left = Inches(0)
            top = Inches(0)
            width = prs.slide_width
            height = prs.slide_height
            background = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
            background.fill.solid()
            background.fill.fore_color.rgb = secondary_color
            background.line.fill.background()
            
            # Accent bar at top
            accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.3))
            accent_bar.fill.solid()
            accent_bar.fill.fore_color.rgb = accent_color
            accent_bar.line.fill.background()
            
            # Company name - large and bold
            left = Inches(1)
            top = Inches(2.5)
            width = Inches(8)
            height = Inches(1.2)
            title_box = slide.shapes.add_textbox(left, top, width, height)
            title_frame = title_box.text_frame
            title_frame.text = company_name
            title_para = title_frame.paragraphs[0]
            title_para.font.size = Pt(56)
            title_para.font.bold = True
            title_para.font.color.rgb = white
            title_para.alignment = PP_ALIGN.CENTER
            
            # Tagline/subtitle
            top = Inches(4)
            height = Inches(0.6)
            subtitle_box = slide.shapes.add_textbox(left, top, width, height)
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.text = "Pitch Deck"
            subtitle_para = subtitle_frame.paragraphs[0]
            subtitle_para.font.size = Pt(24)
            subtitle_para.font.color.rgb = RGBColor(203, 213, 225)  # Light gray
            subtitle_para.alignment = PP_ALIGN.CENTER
            
            # Date
            top = Inches(5)
            height = Inches(0.4)
            date_box = slide.shapes.add_textbox(left, top, width, height)
            date_frame = date_box.text_frame
            date_frame.text = datetime.now().strftime('%B %Y')
            date_para = date_frame.paragraphs[0]
            date_para.font.size = Pt(16)
            date_para.font.color.rgb = RGBColor(148, 163, 184)  # Medium gray
            date_para.alignment = PP_ALIGN.CENTER
            
            # Premium content slides (no speech/talking points in PPT)
            for slide_data in slides:
                slide = prs.slides.add_slide(blank_layout)
                
                slide_title = slide_data.get('title', 'Untitled')
                slide_content = slide_data.get('content', '')
                key_points = slide_data.get('key_points', [])
                
                # Try to get image - first check if already stored in slide data
                image_path = slide_data.get('image_path')
                
                # If not stored, try to fetch it
                if not image_path and include_images and image_fetcher:
                    try:
                        keywords = image_fetcher.get_slide_keywords(slide_title, slide_content)
                        image_path = image_fetcher.get_image_for_slide(slide_title, slide_content, keywords)
                    except Exception as e:
                        logger.warning(f"Could not fetch image: {e}")
                
                # Verify image exists
                if image_path and not Path(image_path).exists():
                    image_path = None
                
                # Premium header with gradient effect
                left = Inches(0)
                top = Inches(0)
                width = prs.slide_width
                height = Inches(1.2)
                header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
                header.fill.solid()
                header.fill.fore_color.rgb = primary_color
                header.line.fill.background()
                
                # Accent line
                accent_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.15))
                accent_line.fill.solid()
                accent_line.fill.fore_color.rgb = accent_color
                accent_line.line.fill.background()
                
                # Slide number badge (rounded effect with background)
                left_num = Inches(0.3)
                top_num = Inches(0.35)
                width_num = Inches(0.8)
                height_num = Inches(0.5)
                num_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_num, top_num, width_num, height_num)
                num_bg.fill.solid()
                num_bg.fill.fore_color.rgb = white
                num_bg.line.fill.background()
                
                num_box = slide.shapes.add_textbox(left_num, top_num, width_num, height_num)
                num_frame = num_box.text_frame
                num_frame.text = str(slide_data.get('slide_number', '?'))
                num_para = num_frame.paragraphs[0]
                num_para.font.size = Pt(22)
                num_para.font.bold = True
                num_para.font.color.rgb = primary_color
                num_para.alignment = PP_ALIGN.CENTER
                
                # Slide title - larger and bolder
                left_title = Inches(1.3)
                top_title = Inches(0.3)
                width_title = Inches(7.5)
                height_title = Inches(0.6)
                title_box = slide.shapes.add_textbox(left_title, top_title, width_title, height_title)
                title_frame = title_box.text_frame
                title_frame.text = slide_title
                title_para = title_frame.paragraphs[0]
                title_para.font.size = Pt(28)
                title_para.font.bold = True
                title_para.font.color.rgb = white
                
                # Main content area (larger now, no speech/talking points)
                left_content = Inches(0.5)
                top_content = Inches(1.6)
                width_content = Inches(4.8) if image_path else Inches(9)
                height_content = Inches(5.5)  # Increased height since no speech/talking points
                content_box = slide.shapes.add_textbox(left_content, top_content, width_content, height_content)
                content_frame = content_box.text_frame
                content_frame.word_wrap = True
                
                # Add main content with better formatting
                if slide_content:
                    p = content_frame.paragraphs[0]
                    p.text = slide_content
                    p.font.size = Pt(18)  # Slightly larger since more space
                    p.font.color.rgb = text_color
                    p.space_after = Pt(14)
                    p.line_spacing = 1.2
                
                # Add key points as bullets with better styling
                if key_points:
                    for i, point in enumerate(key_points):
                        if i == 0 and not slide_content:
                            p = content_frame.paragraphs[0]
                        else:
                            p = content_frame.add_paragraph()
                        p.text = f"• {point}"
                        p.level = 0
                        p.font.size = Pt(16)  # Slightly larger
                        p.font.color.rgb = text_color
                        p.space_after = Pt(10)
                        p.space_before = Pt(6)
                        p.line_spacing = 1.3
                
                # Add image if available (right side, better positioned)
                if image_path and Path(image_path).exists():
                    try:
                        left_img = Inches(5.5)
                        top_img = Inches(1.6)
                        width_img = Inches(4.2)
                        height_img = Inches(5.7)
                        
                        # Image with border
                        img = slide.shapes.add_picture(image_path, left_img, top_img, width_img, height_img)
                        # Add subtle border effect
                        img_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_img - Inches(0.05), 
                                                          top_img - Inches(0.05), width_img + Inches(0.1), 
                                                          height_img + Inches(0.1))
                        img_line.fill.background()
                        img_line.line.color.rgb = RGBColor(200, 200, 200)
                        img_line.line.width = Pt(1)
                    except Exception as e:
                        logger.warning(f"Could not add image to slide: {e}")
            
            # Save
            filename = f"{company_name.replace(' ', '_')}_pitch_deck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
            filepath = self.output_dir / filename
            
            prs.save(str(filepath))
            logger.info(f"Professional PowerPoint exported to: {filepath}")
            return str(filepath)
            
        except ImportError:
            logger.warning("python-pptx not installed. Install with: pip install python-pptx")
            return None
        except Exception as e:
            logger.error(f"Error creating PowerPoint: {e}")
            return None

