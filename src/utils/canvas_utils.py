from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
import io
import asyncio
import aiohttp
from typing import Dict, Any, List, Tuple, Optional
import logging
import math

class CanvasUtils:
    """Canvas utility for creating introduction cards and other images"""
    
    def __init__(self):
        self.width = 800
        self.height = 600
        
        # Try to load default fonts
        self.fonts = self._load_fonts()
    
    def _load_fonts(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """Load system fonts"""
        fonts = {}
        try:
            # Try to load common system fonts
            fonts['regular'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            fonts['bold'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            fonts['large'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            fonts['medium'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except (OSError, IOError):
            # Fallback to default font
            logging.warning("Could not load system fonts, using default")
            fonts['regular'] = ImageFont.load_default()
            fonts['bold'] = ImageFont.load_default()
            fonts['large'] = ImageFont.load_default()
            fonts['medium'] = ImageFont.load_default()
        
        return fonts
    
    async def create_introduction_card(self, user, card_data: Dict[str, Any]) -> bytes:
        """Create an introduction card image"""
        try:
            # Create base image
            img = Image.new('RGB', (self.width, self.height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Create gradient background
            gradient = self._create_gradient_background(card_data.get('favorite_color', '#7C3AED'))
            img.paste(gradient, (0, 0))
            
            # Add subtle pattern overlay
            pattern_overlay = self._create_pattern_overlay()
            img.paste(pattern_overlay, (0, 0), pattern_overlay)
            
            # Main content background
            content_x, content_y = 50, 50
            content_width = self.width - 100
            content_height = self.height - 100
            
            # Create rounded rectangle for content background
            content_bg = Image.new('RGBA', (content_width, content_height), color=(255, 255, 255, 240))
            content_bg = self._add_rounded_corners(content_bg, 20)
            
            # Add shadow effect
            shadow = content_bg.filter(ImageFilter.GaussianBlur(radius=5))
            img.paste(shadow, (content_x + 5, content_y + 10), shadow)
            img.paste(content_bg, (content_x, content_y), content_bg)
            
            # Get user avatar
            avatar = await self._get_user_avatar(user)
            
            # Draw avatar
            avatar_size = 120
            avatar_x, avatar_y = content_x + 40, content_y + 40
            
            if avatar:
                # Create circular mask for avatar
                mask = Image.new('L', (avatar_size, avatar_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
                
                # Resize and apply mask
                avatar = avatar.resize((avatar_size, avatar_size))
                avatar.putalpha(mask)
                img.paste(avatar, (avatar_x, avatar_y), avatar)
            else:
                # Fallback: draw colored circle with initials
                draw.ellipse(
                    (avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size),
                    fill=card_data.get('favorite_color', '#7C3AED')
                )
                
                # Draw initials
                initials = ''.join([n[0] for n in card_data.get('name', 'U').split()]).upper()
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36) if self.fonts else ImageFont.load_default()
                bbox = draw.textbbox((0, 0), initials, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = avatar_x + (avatar_size - text_width) // 2
                text_y = avatar_y + (avatar_size - text_height) // 2
                draw.text((text_x, text_y), initials, fill='white', font=font)
            
            # Draw text content
            text_x = avatar_x + avatar_size + 30
            text_start_y = avatar_y + 20
            current_y = text_start_y
            
            # Name
            name_font = self.fonts.get('large', ImageFont.load_default())
            draw.text((text_x, current_y), card_data.get('name', 'Unknown'), fill='#1F2937', font=name_font)
            current_y += 40
            
            # Age and Location
            info_font = self.fonts.get('regular', ImageFont.load_default())
            age_location = f"{card_data.get('age', 'Unknown')} years old • {card_data.get('location', 'Unknown')}"
            draw.text((text_x, current_y), age_location, fill='#6B7280', font=info_font)
            current_y += 40
            
            # Bio section
            current_y = content_y + 200
            section_font = self.fonts.get('medium', ImageFont.load_default())
            draw.text((content_x + 40, current_y), 'About Me:', fill='#1F2937', font=section_font)
            current_y += 35
            
            # Bio text with word wrapping
            bio_font = self.fonts.get('regular', ImageFont.load_default())
            bio_lines = self._wrap_text(draw, card_data.get('bio', ''), content_width - 80, bio_font)
            for line in bio_lines:
                draw.text((content_x + 40, current_y), line, fill='#374151', font=bio_font)
                current_y += 25
            
            # Hobbies section
            current_y += 20
            draw.text((content_x + 40, current_y), 'Hobbies & Interests:', fill='#1F2937', font=section_font)
            current_y += 35
            
            hobbies_lines = self._wrap_text(draw, card_data.get('hobbies', ''), content_width - 80, bio_font)
            for line in hobbies_lines:
                draw.text((content_x + 40, current_y), line, fill='#374151', font=bio_font)
                current_y += 25
            
            # Add decorative elements
            self._add_decorations(draw, card_data.get('favorite_color', '#7C3AED'))
            
            # Wonder bot branding
            brand_font = self.fonts.get('regular', ImageFont.load_default())
            brand_text = 'Generated by Wonder Bot'
            bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
            brand_width = bbox[2] - bbox[0]
            draw.text((self.width - brand_width - 20, self.height - 30), brand_text, fill='#9CA3AF', font=brand_font)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            logging.error(f"Error creating introduction card: {e}")
            # Return a simple error image
            return self._create_error_image()
    
    async def _get_user_avatar(self, user) -> Optional[Image.Image]:
        """Download and return user avatar"""
        try:
            avatar_url = user.display_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as response:
                    if response.status == 200:
                        avatar_data = await response.read()
                        return Image.open(io.BytesIO(avatar_data)).convert('RGBA')
        except Exception as e:
            logging.warning(f"Could not load user avatar: {e}")
        return None
    
    def _create_gradient_background(self, color: str) -> Image.Image:
        """Create a gradient background"""
        # Create gradient from color to darker version
        base_color = self._hex_to_rgb(color)
        dark_color = self._darken_color(color, 0.3)
        dark_rgb = self._hex_to_rgb(dark_color)
        
        gradient = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(gradient)
        
        # Create vertical gradient
        for y in range(self.height):
            ratio = y / self.height
            r = int(base_color[0] * (1 - ratio) + dark_rgb[0] * ratio)
            g = int(base_color[1] * (1 - ratio) + dark_rgb[1] * ratio)
            b = int(base_color[2] * (1 - ratio) + dark_rgb[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return gradient
    
    def _create_pattern_overlay(self) -> Image.Image:
        """Create a subtle pattern overlay"""
        pattern = Image.new('RGBA', (self.width, self.height), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(pattern)
        
        pattern_size = 20
        for x in range(0, self.width, pattern_size):
            for y in range(0, self.height, pattern_size):
                draw.rectangle((x, y, x + 2, y + 2), fill=(255, 255, 255, 25))
        
        return pattern
    
    def _add_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """Add rounded corners to an image"""
        # Create a mask with rounded corners
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + img.size, radius=radius, fill=255)
        
        # Apply the mask
        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(img, (0, 0))
        result.putalpha(mask)
        
        return result
    
    def _wrap_text(self, draw: ImageDraw.Draw, text: str, max_width: int, font: ImageFont.FreeTypeFont) -> List[str]:
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = words[0] if words else ""
        
        for word in words[1:]:
            test_line = current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _add_decorations(self, draw: ImageDraw.Draw, color: str):
        """Add decorative circles to the image"""
        color_with_alpha = self._hex_to_rgb(color) + (32,)  # 20% opacity
        
        # Add decorative circles
        draw.ellipse((self.width - 130, 70, self.width - 70, 130), fill=color_with_alpha)
        draw.ellipse((self.width - 70, self.height - 120, self.width - 30, self.height - 80), fill=color_with_alpha)
        draw.ellipse((75, self.height - 105, 125, self.height - 55), fill=color_with_alpha)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _darken_color(self, hex_color: str, percent: float) -> str:
        """Darken a hex color by the specified percentage"""
        rgb = self._hex_to_rgb(hex_color)
        darkened = tuple(max(0, int(c * (1 - percent))) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    def _create_error_image(self) -> bytes:
        """Create a simple error image"""
        img = Image.new('RGB', (400, 200), color='#FF6B6B')
        draw = ImageDraw.Draw(img)
        
        font = self.fonts.get('medium', ImageFont.load_default())
        text = "Error creating image"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (400 - text_width) // 2
        y = (200 - text_height) // 2
        draw.text((x, y), text, fill='white', font=font)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

# Global canvas utils instance
canvas_utils = CanvasUtils()