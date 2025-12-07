"""Enhanced image handling with overlays, filters, and smart cropping."""

import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import os

logger = logging.getLogger(__name__)


class ImageEnhancer:
    """Enhance images for professional presentations."""
    
    def __init__(self):
        """Initialize image enhancer."""
        self.cache_dir = Path("exports/enhanced_images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("ImageEnhancer initialized")
    
    def add_text_overlay(self, image_path: str, text: str,
                         position: str = "bottom",
                         output_path: Optional[str] = None) -> Optional[str]:
        """
        Add text overlay to image.
        
        Args:
            image_path: Path to image
            text: Text to overlay
            position: Position (top, center, bottom)
            output_path: Optional output path
            
        Returns:
            Path to enhanced image
        """
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Create semi-transparent background for text
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Calculate text position
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except:
                font = ImageFont.load_default()
            
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position
            if position == "bottom":
                y = img.height - text_height - 40
            elif position == "top":
                y = 20
            else:  # center
                y = (img.height - text_height) // 2
            
            x = (img.width - text_width) // 2
            
            # Draw background
            padding = 20
            overlay_draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(0, 0, 0, 180)  # Semi-transparent black
            )
            
            # Composite overlay
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Draw text
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
            
            # Save
            if not output_path:
                output_path = self.cache_dir / f"overlay_{Path(image_path).stem}.jpg"
            
            img.save(output_path, quality=95)
            logger.info(f"Added text overlay: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error adding text overlay: {e}")
            return None
    
    def apply_filter(self, image_path: str, filter_type: str = "blur",
                    output_path: Optional[str] = None) -> Optional[str]:
        """
        Apply filter to image.
        
        Args:
            image_path: Path to image
            filter_type: Filter type (blur, sharpen, brightness, contrast)
            output_path: Optional output path
            
        Returns:
            Path to filtered image
        """
        try:
            img = Image.open(image_path)
            
            if filter_type == "blur":
                img = img.filter(ImageFilter.GaussianBlur(radius=2))
            elif filter_type == "sharpen":
                img = img.filter(ImageFilter.SHARPEN)
            elif filter_type == "brightness":
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.2)
            elif filter_type == "contrast":
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.3)
            
            if not output_path:
                output_path = self.cache_dir / f"filtered_{filter_type}_{Path(image_path).stem}.jpg"
            
            img.save(output_path, quality=95)
            logger.info(f"Applied {filter_type} filter: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error applying filter: {e}")
            return None
    
    def smart_crop(self, image_path: str, aspect_ratio: Tuple[float, float] = (16, 9),
                   output_path: Optional[str] = None) -> Optional[str]:
        """
        Smart crop image to aspect ratio (centers on important content).
        
        Args:
            image_path: Path to image
            aspect_ratio: Target aspect ratio (width, height)
            output_path: Optional output path
            
        Returns:
            Path to cropped image
        """
        try:
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # Calculate target size
            target_ratio = aspect_ratio[0] / aspect_ratio[1]
            current_ratio = img_width / img_height
            
            if current_ratio > target_ratio:
                # Image is wider, crop width
                new_width = int(img_height * target_ratio)
                left = (img_width - new_width) // 2
                crop_box = (left, 0, left + new_width, img_height)
            else:
                # Image is taller, crop height
                new_height = int(img_width / target_ratio)
                top = (img_height - new_height) // 2
                crop_box = (0, top, img_width, top + new_height)
            
            img_cropped = img.crop(crop_box)
            
            if not output_path:
                output_path = self.cache_dir / f"cropped_{Path(image_path).stem}.jpg"
            
            img_cropped.save(output_path, quality=95)
            logger.info(f"Smart cropped image: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error smart cropping: {e}")
            return None
    
    def create_image_mask(self, image_path: str, mask_type: str = "rounded",
                         output_path: Optional[str] = None) -> Optional[str]:
        """
        Create image with mask (rounded corners, circle, etc.).
        
        Args:
            image_path: Path to image
            mask_type: Mask type (rounded, circle)
            output_path: Optional output path
            
        Returns:
            Path to masked image
        """
        try:
            img = Image.open(image_path).convert('RGBA')
            size = min(img.width, img.height)
            
            # Create mask
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            
            if mask_type == "circle":
                draw.ellipse([0, 0, size, size], fill=255)
            else:  # rounded
                radius = size // 10
                draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=255)
            
            # Resize mask to image size
            mask = mask.resize(img.size, Image.LANCZOS)
            
            # Apply mask
            output = Image.new('RGBA', img.size, (255, 255, 255, 0))
            output.paste(img, (0, 0))
            output.putalpha(mask)
            
            if not output_path:
                output_path = self.cache_dir / f"masked_{mask_type}_{Path(image_path).stem}.png"
            
            output.save(output_path)
            logger.info(f"Created {mask_type} mask: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating mask: {e}")
            return None


