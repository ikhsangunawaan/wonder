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
    
    async def create_member_identity_card(self, user, card_data: Dict[str, Any]) -> bytes:
        """Create a Member Identity Card similar to the reference design"""
        try:
            from database import database
            
            # Card dimensions - wider format like the reference
            card_width = 850
            card_height = 500
            
            # Create base image with orange gradient background
            img = Image.new('RGB', (card_width, card_height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Create orange gradient background (orange to darker orange)
            self._create_orange_gradient_background(img, draw, card_width, card_height)
            
            # Add dotted pattern overlay
            self._add_dotted_pattern(img, draw, card_width, card_height)
            
            # Main card content area (white rounded rectangle)
            card_margin = 30
            card_content_x = card_margin
            card_content_y = card_margin + 60  # Leave space for title
            card_content_width = card_width - (card_margin * 2)
            card_content_height = card_height - card_content_y - card_margin - 60  # Leave space for footer
            
            # Create rounded rectangle for main content
            content_bg = Image.new('RGBA', (card_content_width, card_content_height), color=(255, 255, 255, 250))
            content_bg = self._add_rounded_corners(content_bg, 15)
            
            # Add subtle shadow
            shadow = content_bg.filter(ImageFilter.GaussianBlur(radius=3))
            img.paste(shadow, (card_content_x + 2, card_content_y + 3), shadow)
            img.paste(content_bg, (card_content_x, card_content_y), content_bg)
            
            # Title "Member Identity Card"
            title_font = self._get_font('title', 36)
            title_text = "Member Identity Card"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (card_width - title_width) // 2
            title_y = 20
            
            # Add title with shadow effect
            draw.text((title_x + 2, title_y + 2), title_text, fill=(0, 0, 0, 100), font=title_font)
            draw.text((title_x, title_y), title_text, fill='white', font=title_font)
            
            # Avatar section
            avatar_size = 140
            avatar_x = card_content_x + 30
            avatar_y = card_content_y + 30
            
            # Get and draw user avatar
            avatar = await self._get_user_avatar(user)
            if avatar:
                # Create rounded rectangle mask for avatar
                avatar_bg = Image.new('RGBA', (avatar_size + 10, avatar_size + 10), (255, 255, 255, 255))
                avatar_bg = self._add_rounded_corners(avatar_bg, 10)
                img.paste(avatar_bg, (avatar_x - 5, avatar_y - 5), avatar_bg)
                
                # Resize and crop avatar to square
                avatar = avatar.resize((avatar_size, avatar_size))
                avatar_mask = Image.new('L', (avatar_size, avatar_size), 0)
                avatar_mask_draw = ImageDraw.Draw(avatar_mask)
                avatar_mask_draw.rounded_rectangle((0, 0, avatar_size, avatar_size), radius=8, fill=255)
                avatar.putalpha(avatar_mask)
                img.paste(avatar, (avatar_x, avatar_y), avatar)
            else:
                # Fallback: draw rounded rectangle with initials
                draw.rounded_rectangle(
                    (avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size),
                    radius=10,
                    fill='#E5E7EB'
                )
                
                # Draw initials
                initials = ''.join([n[0] for n in card_data.get('name', 'U').split()]).upper()
                initials_font = self._get_font('bold', 48)
                initials_bbox = draw.textbbox((0, 0), initials, font=initials_font)
                initials_width = initials_bbox[2] - initials_bbox[0]
                initials_height = initials_bbox[3] - initials_bbox[1]
                initials_x = avatar_x + (avatar_size - initials_width) // 2
                initials_y = avatar_y + (avatar_size - initials_height) // 2
                draw.text((initials_x, initials_y), initials, fill='#6B7280', font=initials_font)
            
            # Information fields section
            info_start_x = avatar_x + avatar_size + 40
            info_start_y = avatar_y + 10
            field_height = 35
            
            # Define fields with their values
            fields = [
                ("Nickname", card_data.get('name', 'N/A')),
                ("Age", f"{card_data.get('age', 'N/A')}" + (" (fck.)" if card_data.get('age') else "")),
                ("Gender", card_data.get('gender', 'N/A')),
                ("City", card_data.get('location', 'N/A')),
                ("Hobby", card_data.get('hobbies', 'N/A'))
            ]
            
            # Draw information fields
            self._draw_info_fields(draw, fields, info_start_x, info_start_y, field_height)
            
            # Footer branding
            footer_y = card_height - 45
            brand_font = self._get_font('bold', 24)
            brand_text = "MenggokiI Cafe"
            draw.text((card_margin + 20, footer_y), brand_text, fill='white', font=brand_font)
            
            # ID and barcode section
            id_number = f"{user.id % 1000000000000000:015d}"  # Generate a 15-digit ID from user ID
            self._draw_id_section(draw, id_number, card_width, footer_y)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            logging.error(f"Error creating member identity card: {e}")
            return self._create_error_image()
    
    def _create_orange_gradient_background(self, img: Image.Image, draw: ImageDraw.Draw, width: int, height: int):
        """Create orange gradient background like the reference"""
        # Orange gradient colors
        top_color = (255, 140, 60)     # Light orange
        bottom_color = (255, 100, 20)  # Darker orange
        
        # Create vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _add_dotted_pattern(self, img: Image.Image, draw: ImageDraw.Draw, width: int, height: int):
        """Add dotted pattern overlay like the reference"""
        pattern_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        pattern_draw = ImageDraw.Draw(pattern_overlay)
        
        dot_spacing = 20
        dot_size = 2
        
        for x in range(0, width, dot_spacing):
            for y in range(0, height, dot_spacing):
                pattern_draw.ellipse(
                    (x, y, x + dot_size, y + dot_size),
                    fill=(255, 255, 255, 80)
                )
        
        img.paste(pattern_overlay, (0, 0), pattern_overlay)
    
    def _get_font(self, style: str, size: int) -> ImageFont.FreeTypeFont:
        """Get font with specific style and size"""
        try:
            if style == 'title':
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            elif style == 'bold':
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            elif style == 'regular':
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
            else:
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()
    
    def _draw_info_fields(self, draw: ImageDraw.Draw, fields: List[tuple], start_x: int, start_y: int, field_height: int):
        """Draw information fields with labels and values"""
        label_font = self._get_font('bold', 18)
        value_font = self._get_font('regular', 18)
        
        current_y = start_y
        
        for label, value in fields:
            # Draw label
            draw.text((start_x, current_y), label, fill='#1F2937', font=label_font)
            
            # Draw field background (rounded rectangle)
            field_bg_x = start_x + 120
            field_bg_y = current_y - 3
            field_bg_width = 300
            field_bg_height = 25
            
            draw.rounded_rectangle(
                (field_bg_x, field_bg_y, field_bg_x + field_bg_width, field_bg_y + field_bg_height),
                radius=5,
                fill='#F3F4F6',
                outline='#D1D5DB',
                width=1
            )
            
            # Draw value text
            draw.text((field_bg_x + 10, current_y), str(value), fill='#374151', font=value_font)
            
            current_y += field_height
    
    def _draw_id_section(self, draw: ImageDraw.Draw, id_number: str, card_width: int, footer_y: int):
        """Draw ID number and barcode representation"""
        id_font = self._get_font('regular', 16)
        
        # Draw ID number
        id_text = f"ID: {id_number}"
        id_bbox = draw.textbbox((0, 0), id_text, font=id_font)
        id_width = id_bbox[2] - id_bbox[0]
        id_x = card_width - id_width - 30
        draw.text((id_x, footer_y + 5), id_text, fill='white', font=id_font)
        
        # Draw simple barcode representation
        barcode_x = id_x
        barcode_y = footer_y - 15
        barcode_width = id_width
        
        # Simple barcode pattern
        bar_width = 2
        for i in range(0, barcode_width, bar_width * 2):
            if i % 4 == 0:  # Alternate pattern
                draw.rectangle(
                    (barcode_x + i, barcode_y, barcode_x + i + bar_width, barcode_y + 10),
                    fill='white'
                )

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

    async def create_y2k_identity_card(self, user, card_data: Dict[str, Any]) -> bytes:
        """Create a Y2K aesthetic identity card with chrome effects and purple theme"""
        try:
            from database import database
            
            # Card dimensions
            card_width = 850
            card_height = 500
            
            # Create base image
            img = Image.new('RGB', (card_width, card_height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Create Y2K holographic background
            self._create_y2k_holographic_background(img, draw, card_width, card_height)
            
            # Add chrome grid pattern overlay
            self._add_chrome_grid_pattern(img, draw, card_width, card_height)
            
            # Main card content area (with chrome border)
            card_margin = 25
            border_width = 3
            card_content_x = card_margin + border_width
            card_content_y = card_margin + 70  # Space for title
            card_content_width = card_width - (card_margin + border_width) * 2
            card_content_height = card_height - card_content_y - card_margin - 70  # Space for footer
            
            # Create chrome border effect
            self._create_chrome_border(draw, card_margin, card_content_y - 5, 
                                     card_width - card_margin * 2, card_content_height + 10)
            
            # Create glass-like content background
            content_bg = Image.new('RGBA', (card_content_width, card_content_height), color=(40, 20, 80, 200))
            content_bg = self._add_rounded_corners(content_bg, 12)
            
            # Add holographic overlay to content area
            holo_overlay = self._create_holographic_overlay(card_content_width, card_content_height)
            content_bg.paste(holo_overlay, (0, 0), holo_overlay)
            
            # Apply content background
            img.paste(content_bg, (card_content_x, card_content_y), content_bg)
            
            # Title with Y2K chrome effect
            title_font = self._get_font('title', 40)
            title_text = "◊ IDENTITY CARD ◊"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (card_width - title_width) // 2
            title_y = 15
            
            # Chrome text effect for title
            self._draw_chrome_text(draw, title_x, title_y, title_text, title_font, size='large')
            
            # Avatar section with chrome frame
            avatar_size = 130
            avatar_x = card_content_x + 25
            avatar_y = card_content_y + 25
            
            # Chrome frame for avatar
            self._draw_chrome_frame(draw, avatar_x - 5, avatar_y - 5, avatar_size + 10, avatar_size + 10)
            
            # Get and draw user avatar
            avatar = await self._get_user_avatar(user)
            if avatar:
                # Create hexagonal mask for Y2K aesthetic
                avatar_mask = self._create_hexagonal_mask(avatar_size, avatar_size)
                avatar = avatar.resize((avatar_size, avatar_size))
                avatar.putalpha(avatar_mask)
                img.paste(avatar, (avatar_x, avatar_y), avatar)
            else:
                # Fallback: hexagonal shape with chrome effect
                self._draw_hexagonal_avatar(draw, avatar_x, avatar_y, avatar_size, card_data.get('name', 'U'))
            
            # Information fields with Y2K styling
            info_start_x = avatar_x + avatar_size + 35
            info_start_y = avatar_y + 15
            field_height = 32
            
            # Define fields with Y2K formatting
            fields = [
                ("NICKNAME", card_data.get('name', 'N/A').upper()),
                ("AGE", f"{card_data.get('age', 'N/A')}" + (" YRS" if card_data.get('age') else "")),
                ("GENDER", card_data.get('gender', 'N/A').upper()),
                ("LOCATION", card_data.get('location', 'N/A').upper()),
                ("INTEREST", card_data.get('hobbies', 'N/A'))
            ]
            
            # Draw information fields with Y2K styling
            self._draw_y2k_info_fields(draw, fields, info_start_x, info_start_y, field_height)
            
            # Footer with Wonder branding and Y2K elements
            footer_y = card_height - 50
            
            # Wonder logo with chrome effect
            brand_font = self._get_font('bold', 32)
            brand_text = "W O N D E R"
            brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
            brand_x = card_margin + 25
            self._draw_chrome_text(draw, brand_x, footer_y, brand_text, brand_font, size='medium')
            
            # Y2K decorative elements
            self._add_y2k_decorations(draw, card_width, card_height)
            
            # Holographic ID section
            id_number = f"{user.id % 1000000000000000:015d}"
            self._draw_y2k_id_section(draw, id_number, card_width, footer_y)
            
            # Final holographic overlay
            final_holo = self._create_subtle_holographic_overlay(card_width, card_height)
            img.paste(final_holo, (0, 0), final_holo)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            logging.error(f"Error creating Y2K identity card: {e}")
            return self._create_error_image()
    
    def _create_y2k_holographic_background(self, img: Image.Image, draw: ImageDraw.Draw, width: int, height: int):
        """Create Y2K holographic gradient background"""
        # Y2K purple/pink gradient with chrome accents
        colors = [
            (120, 50, 200),   # Deep purple
            (180, 70, 255),   # Bright purple
            (220, 120, 255),  # Light purple
            (255, 150, 220),  # Pink
            (150, 100, 255),  # Blue-purple
            (100, 60, 180)    # Dark purple
        ]
        
        # Create complex gradient
        for y in range(height):
            for x in range(width):
                # Create wave-like color transitions
                wave1 = math.sin(x * 0.01) * 0.3
                wave2 = math.cos(y * 0.015) * 0.3
                combined_wave = (wave1 + wave2 + 1) / 2
                
                # Select color based on position and waves
                color_index = int(combined_wave * (len(colors) - 1))
                color_index = max(0, min(color_index, len(colors) - 1))
                
                # Add some variation
                base_color = colors[color_index]
                variation = int(math.sin(x * 0.02 + y * 0.02) * 15)
                
                r = max(0, min(255, base_color[0] + variation))
                g = max(0, min(255, base_color[1] + variation))
                b = max(0, min(255, base_color[2] + variation))
                
                # Set pixel (for performance, we'll use lines instead)
                if x == 0:  # Only draw vertical lines for performance
                    draw.line([(x, y), (x, y)], fill=(r, g, b))
        
        # Simplified approach for better performance
        for y in range(height):
            ratio1 = y / height
            ratio2 = math.sin(y * 0.02) * 0.3 + 0.5
            
            # Blend between purple tones
            r = int(120 + (180 - 120) * ratio1 + 30 * ratio2)
            g = int(50 + (120 - 50) * ratio1 + 20 * ratio2)
            b = int(200 + (255 - 200) * ratio1 + 15 * ratio2)
            
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _add_chrome_grid_pattern(self, img: Image.Image, draw: ImageDraw.Draw, width: int, height: int):
        """Add chrome grid pattern overlay"""
        grid_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        grid_draw = ImageDraw.Draw(grid_overlay)
        
        grid_size = 40
        line_width = 1
        
        # Draw grid lines with chrome effect
        for x in range(0, width, grid_size):
            grid_draw.line([(x, 0), (x, height)], fill=(200, 200, 255, 30), width=line_width)
        
        for y in range(0, height, grid_size):
            grid_draw.line([(0, y), (width, y)], fill=(200, 200, 255, 30), width=line_width)
        
        img.paste(grid_overlay, (0, 0), grid_overlay)
    
    def _create_chrome_border(self, draw: ImageDraw.Draw, x: int, y: int, width: int, height: int):
        """Create chrome border effect"""
        border_colors = [
            (255, 255, 255, 180),  # Bright highlight
            (200, 200, 255, 150),  # Chrome
            (150, 150, 200, 120),  # Medium
            (100, 100, 150, 100),  # Shadow
        ]
        
        for i, color in enumerate(border_colors):
            border_width = len(border_colors) - i
            draw.rounded_rectangle(
                (x - i, y - i, x + width + i, y + height + i),
                radius=15 + i,
                outline=color[:3],
                width=border_width
            )
    
    def _create_holographic_overlay(self, width: int, height: int) -> Image.Image:
        """Create holographic rainbow overlay"""
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Create rainbow stripes
        stripe_height = 3
        colors = [
            (255, 100, 255, 40),  # Magenta
            (100, 200, 255, 40),  # Cyan
            (255, 255, 100, 40),  # Yellow
            (100, 255, 100, 40),  # Green
        ]
        
        for y in range(0, height, stripe_height * len(colors)):
            for i, color in enumerate(colors):
                stripe_y = y + i * stripe_height
                if stripe_y < height:
                    overlay_draw.rectangle(
                        (0, stripe_y, width, stripe_y + stripe_height),
                        fill=color
                    )
        
        return overlay
    
    def _draw_chrome_text(self, draw: ImageDraw.Draw, x: int, y: int, text: str, font: ImageFont.FreeTypeFont, size: str = 'medium'):
        """Draw text with chrome effect"""
        offsets = [(2, 2), (1, 1), (0, 0)] if size == 'large' else [(1, 1), (0, 0)]
        colors = [(0, 0, 0, 100), (100, 100, 150, 200), (255, 255, 255, 255)]
        
        for i, (offset_x, offset_y) in enumerate(offsets):
            color = colors[min(i, len(colors) - 1)]
            draw.text((x + offset_x, y + offset_y), text, fill=color[:3], font=font)
    
    def _create_hexagonal_mask(self, width: int, height: int) -> Image.Image:
        """Create hexagonal mask for Y2K aesthetic"""
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 5
        
        # Calculate hexagon points
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        
        mask_draw.polygon(points, fill=255)
        return mask
    
    def _draw_hexagonal_avatar(self, draw: ImageDraw.Draw, x: int, y: int, size: int, name: str):
        """Draw hexagonal avatar fallback"""
        center_x, center_y = x + size // 2, y + size // 2
        radius = size // 2 - 5
        
        # Calculate hexagon points
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        
        # Draw hexagon with gradient
        draw.polygon(points, fill=(150, 100, 255))
        
        # Draw initials
        initials = ''.join([n[0] for n in name.split()]).upper()
        initials_font = self._get_font('bold', 36)
        bbox = draw.textbbox((0, 0), initials, font=initials_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2
        draw.text((text_x, text_y), initials, fill='white', font=initials_font)
    
    def _draw_chrome_frame(self, draw: ImageDraw.Draw, x: int, y: int, width: int, height: int):
        """Draw chrome frame around element"""
        colors = [(255, 255, 255), (200, 200, 255), (150, 150, 200)]
        
        for i, color in enumerate(colors):
            draw.rounded_rectangle(
                (x - i, y - i, x + width + i, y + height + i),
                radius=8 + i,
                outline=color,
                width=2
            )
    
    def _draw_y2k_info_fields(self, draw: ImageDraw.Draw, fields: list, start_x: int, start_y: int, field_height: int):
        """Draw information fields with Y2K styling"""
        label_font = self._get_font('bold', 14)
        value_font = self._get_font('regular', 16)
        
        current_y = start_y
        
        for label, value in fields:
            # Draw label with chrome effect
            draw.text((start_x, current_y), label, fill=(200, 200, 255), font=label_font)
            
            # Draw field background with holographic effect
            field_bg_x = start_x + 100
            field_bg_y = current_y - 2
            field_bg_width = 280
            field_bg_height = 22
            
            # Holographic field background
            colors = [(80, 40, 120, 180), (120, 80, 160, 180), (160, 120, 200, 180)]
            for i, color in enumerate(colors):
                draw.rounded_rectangle(
                    (field_bg_x - i, field_bg_y - i, field_bg_x + field_bg_width + i, field_bg_y + field_bg_height + i),
                    radius=8,
                    fill=color
                )
            
            # Draw value text with slight glow effect
            draw.text((field_bg_x + 8, current_y), str(value), fill=(255, 255, 255), font=value_font)
            
            current_y += field_height
    
    def _add_y2k_decorations(self, draw: ImageDraw.Draw, width: int, height: int):
        """Add Y2K decorative elements"""
        # Floating geometric shapes
        shapes = [
            {'type': 'circle', 'pos': (width - 120, 80), 'size': 20, 'color': (255, 200, 255, 100)},
            {'type': 'triangle', 'pos': (width - 80, 200), 'size': 15, 'color': (200, 255, 255, 100)},
            {'type': 'diamond', 'pos': (80, height - 100), 'size': 18, 'color': (255, 255, 200, 100)},
            {'type': 'star', 'pos': (width - 150, height - 80), 'size': 12, 'color': (255, 150, 255, 100)},
        ]
        
        for shape in shapes:
            x, y = shape['pos']
            size = shape['size']
            color = shape['color'][:3]  # Remove alpha for now
            
            if shape['type'] == 'circle':
                draw.ellipse((x, y, x + size, y + size), fill=color)
            elif shape['type'] == 'diamond':
                points = [(x + size//2, y), (x + size, y + size//2), (x + size//2, y + size), (x, y + size//2)]
                draw.polygon(points, fill=color)
    
    def _draw_y2k_id_section(self, draw: ImageDraw.Draw, id_number: str, card_width: int, footer_y: int):
        """Draw ID section with Y2K styling"""
        id_font = self._get_font('regular', 14)
        
        # Draw ID with chrome effect
        id_text = f"ID: {id_number[:8]}•••"
        id_bbox = draw.textbbox((0, 0), id_text, font=id_font)
        id_width = id_bbox[2] - id_bbox[0]
        id_x = card_width - id_width - 40
        
        # Chrome text effect for ID
        self._draw_chrome_text(draw, id_x, footer_y + 10, id_text, id_font)
        
        # Holographic barcode
        barcode_x = id_x
        barcode_y = footer_y - 10
        colors = [(255, 100, 255), (100, 255, 255), (255, 255, 100)]
        
        for i in range(0, 60, 3):
            color = colors[i % len(colors)]
            if i % 6 == 0:  # Vary bar pattern
                draw.rectangle(
                    (barcode_x + i, barcode_y, barcode_x + i + 2, barcode_y + 12),
                    fill=color
                )
    
    def _create_subtle_holographic_overlay(self, width: int, height: int) -> Image.Image:
        """Create subtle final holographic overlay"""
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Add subtle rainbow gradients in corners
        gradient_size = 100
        
        # Top-left corner
        for i in range(gradient_size):
            alpha = int(30 * (1 - i / gradient_size))
            color = (255, 200, 255, alpha)
            overlay_draw.ellipse((0, 0, i*2, i*2), fill=color)
        
        # Bottom-right corner  
        for i in range(gradient_size):
            alpha = int(30 * (1 - i / gradient_size))
            color = (200, 255, 255, alpha)
            start_x = width - i*2
            start_y = height - i*2
            overlay_draw.ellipse((start_x, start_y, width, height), fill=color)
        
        return overlay

# Global canvas utils instance
canvas_utils = CanvasUtils()