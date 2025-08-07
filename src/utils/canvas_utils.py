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
            from database import database
            
            # Create base image
            img = Image.new('RGB', (self.width, self.height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Check if custom background is set
            guild_id = card_data.get('guild_id')
            custom_bg_url = None
            
            if guild_id:
                server_settings = await database.get_server_settings(guild_id)
                if server_settings:
                    custom_bg_url = server_settings.get('intro_card_background_url')
            
            # Use custom background if available, otherwise use gradient
            if custom_bg_url:
                try:
                    background = await self._create_custom_background(custom_bg_url)
                    img.paste(background, (0, 0))
                except Exception as e:
                    logging.warning(f"Failed to load custom background, using default: {e}")
                    # Fallback to gradient
                    background = self._create_gradient_background('#7C3AED')
                    img.paste(background, (0, 0))
                    # Add pattern overlay for gradient
                    pattern_overlay = self._create_pattern_overlay()
                    img.paste(pattern_overlay, (0, 0), pattern_overlay)
            else:
                # Create gradient background (default)
                background = self._create_gradient_background('#7C3AED')
                img.paste(background, (0, 0))
                # Add pattern overlay for gradient
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
            name_text = card_data.get('name', 'Unknown')
            draw.text((text_x, current_y), name_text, fill='#1F2937', font=name_font)
            current_y += 40
            
            # Age and Location
            info_font = self.fonts.get('regular', ImageFont.load_default())
            info_parts = []
            if card_data.get('age'):
                info_parts.append(f"{card_data['age']} years old")
            if card_data.get('location'):
                info_parts.append(card_data['location'])
            
            if info_parts:
                age_location = " • ".join(info_parts)
                draw.text((text_x, current_y), age_location, fill='#6B7280', font=info_font)
                current_y += 25
            
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
            
            if card_data.get('hobbies'):
                hobbies_lines = self._wrap_text(draw, card_data['hobbies'], content_width - 80, bio_font)
                for line in hobbies_lines:
                    draw.text((content_x + 40, current_y), line, fill='#374151', font=bio_font)
                    current_y += 25
            
            # Add decorative elements
            self._add_decorations(draw, '#7C3AED')
            
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
    
    def _create_solid_background(self, color: str) -> Image.Image:
        """Create a solid color background"""
        base_color = self._hex_to_rgb(color)
        return Image.new('RGB', (self.width, self.height), base_color)
    
    def _create_pattern_background(self, color: str) -> Image.Image:
        """Create a geometric pattern background"""
        base_color = self._hex_to_rgb(color)
        dark_color = self._darken_color(color, 0.2)
        dark_rgb = self._hex_to_rgb(dark_color)
        
        pattern = Image.new('RGB', (self.width, self.height), base_color)
        draw = ImageDraw.Draw(pattern)
        
        # Create geometric pattern
        pattern_size = 40
        for x in range(0, self.width, pattern_size):
            for y in range(0, self.height, pattern_size):
                # Alternate between shapes
                if (x // pattern_size + y // pattern_size) % 2 == 0:
                    # Diamond shape
                    points = [
                        (x + pattern_size // 2, y),
                        (x + pattern_size, y + pattern_size // 2),
                        (x + pattern_size // 2, y + pattern_size),
                        (x, y + pattern_size // 2)
                    ]
                    draw.polygon(points, fill=dark_rgb)
                else:
                    # Circle
                    margin = pattern_size // 4
                    draw.ellipse(
                        (x + margin, y + margin, x + pattern_size - margin, y + pattern_size - margin),
                        fill=dark_rgb
                    )
        
        return pattern
    
    async def _create_custom_background(self, image_url: str) -> Image.Image:
        """Create background from custom image URL"""
        try:
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Open and process image
                        bg_image = Image.open(io.BytesIO(image_data)).convert('RGBA')
                        
                        # Resize to fit card dimensions while maintaining aspect ratio
                        bg_image = self._resize_background_image(bg_image)
                        
                        # Create final background
                        background = Image.new('RGB', (self.width, self.height), color='white')
                        
                        # Center the background image
                        bg_width, bg_height = bg_image.size
                        x = (self.width - bg_width) // 2
                        y = (self.height - bg_height) // 2
                        
                        # Paste background image
                        if bg_image.mode == 'RGBA':
                            background.paste(bg_image, (x, y), bg_image)
                        else:
                            background.paste(bg_image, (x, y))
                        
                        # Add slight overlay to ensure text readability
                        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 30))
                        background.paste(overlay, (0, 0), overlay)
                        
                        return background
                    else:
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            logging.error(f"Error loading custom background: {e}")
            raise
    
    def _resize_background_image(self, image: Image.Image) -> Image.Image:
        """Resize background image to fit card dimensions"""
        original_width, original_height = image.size
        target_width, target_height = self.width, self.height
        
        # Calculate scaling factor to cover the entire card
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = max(scale_x, scale_y)  # Use max to ensure full coverage
        
        # Calculate new dimensions
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Resize image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # If image is larger than target, crop from center
        if new_width > target_width or new_height > target_height:
            left = (new_width - target_width) // 2
            top = (new_height - target_height) // 2
            right = left + target_width
            bottom = top + target_height
            resized_image = resized_image.crop((left, top, right, bottom))
        
        return resized_image
    
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