import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, Any, Optional, List
import asyncio
import io
from datetime import datetime
import logging

from database import database
from utils.canvas_utils import canvas_utils


class IntroCardView(discord.ui.View):
    """Interactive view for introduction cards with buttons"""
    
    def __init__(self, card_data: Dict[str, Any], user_id: str):
        super().__init__(timeout=None)  # Persistent view
        self.card_data = card_data
        self.user_id = user_id
        
    @discord.ui.button(label='❤️ Like', style=discord.ButtonStyle.secondary, custom_id='like_card')
    async def like_card(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Like/unlike an introduction card"""
        try:
            # Check if user already liked this card
            interactions = await database.get_card_interactions(self.card_data['id'], 'like')
            user_liked = any(i['user_id'] == str(interaction.user.id) for i in interactions)
            
            if user_liked:
                # Remove like
                await database.remove_card_interaction(self.card_data['id'], str(interaction.user.id), 'like')
                button.label = '🤍 Like'
                await interaction.response.edit_message(view=self)
                await interaction.followup.send("❤️ Removed like from this card!", ephemeral=True)
            else:
                # Add like
                await database.add_card_interaction(self.card_data['id'], str(interaction.user.id), 'like')
                button.label = '❤️ Liked'
                await interaction.response.edit_message(view=self)
                await interaction.followup.send("❤️ Liked this card!", ephemeral=True)
                
        except Exception as e:
            logging.error(f"Error handling card like: {e}")
            await interaction.response.send_message("❌ An error occurred while processing your like.", ephemeral=True)
    
    @discord.ui.button(label='👋 Say Hi', style=discord.ButtonStyle.primary, custom_id='say_hi')
    async def say_hi(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Send a greeting to the card owner"""
        if str(interaction.user.id) == self.card_data['user_id']:
            await interaction.response.send_message("❌ You can't greet yourself!", ephemeral=True)
            return
            
        try:
            user = interaction.guild.get_member(int(self.card_data['user_id']))
            if user:
                embed = discord.Embed(
                    title="🌟 Someone wants to connect!",
                    description=f"{interaction.user.display_name} saw your Wonder member card and wants to connect!",
                    color=0x9F7AEA
                )
                embed.add_field(name="Message", value="Feel free to reach out and make a new friend! 🤝", inline=False)
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                
                try:
                    await user.send(embed=embed)
                    await interaction.response.send_message("✅ Greeting sent! They'll receive a DM notification.", ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message(
                        f"✅ I couldn't send a DM, but you can greet {user.mention} directly in the server!",
                        ephemeral=True
                    )
            else:
                await interaction.response.send_message("❌ User not found in this server.", ephemeral=True)
                
        except Exception as e:
            logging.error(f"Error sending greeting: {e}")
            await interaction.response.send_message("❌ An error occurred while sending the greeting.", ephemeral=True)
    
    @discord.ui.button(label='📊 Stats', style=discord.ButtonStyle.secondary, custom_id='card_stats')
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View card statistics"""
        try:
            likes = await database.get_card_interactions(self.card_data['id'], 'like')
            views = self.card_data.get('views_count', 0)
            
            embed = discord.Embed(
                title="📊 Card Statistics",
                color=0x9F7AEA
            )
            embed.add_field(name="❤️ Likes", value=str(len(likes)), inline=True)
            embed.add_field(name="👀 Views", value=str(views), inline=True)
            embed.add_field(name="📅 Created", value=f"<t:{int(datetime.fromisoformat(self.card_data['created_at']).timestamp())}:R>", inline=True)
            
            if likes:
                recent_likes = likes[:5]  # Show last 5 likes
                like_users = []
                for like in recent_likes:
                    user = interaction.guild.get_member(int(like['user_id']))
                    if user:
                        like_users.append(user.display_name)
                
                if like_users:
                    embed.add_field(name="Recent Likes", value="\n".join(like_users), inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Error viewing card stats: {e}")
            await interaction.response.send_message("❌ An error occurred while fetching stats.", ephemeral=True)


class IntroCardModal(discord.ui.Modal):
    """Modal for creating/editing introduction cards"""
    
    def __init__(self, existing_card: Optional[Dict[str, Any]] = None):
        super().__init__(title="🌟 Create Your Wonder Member Card" if not existing_card else "✏️ Edit Your Wonder Member Card")
        self.existing_card = existing_card
        
        # Nickname field
        self.name_input = discord.ui.TextInput(
            label="Nickname",
            placeholder="What should people call you?",
            default=existing_card.get('name', '') if existing_card else '',
            max_length=50,
            required=True
        )
        self.add_item(self.name_input)
        
        # Age field
        self.age_input = discord.ui.TextInput(
            label="Age (optional)",
            placeholder="How old are you?",
            default=str(existing_card.get('age', '')) if existing_card and existing_card.get('age') else '',
            max_length=3,
            required=False
        )
        self.add_item(self.age_input)
        
        # Gender field
        self.gender_input = discord.ui.TextInput(
            label="Gender (optional)",
            placeholder="Your gender identity",
            default=existing_card.get('gender', '') if existing_card else '',
            max_length=50,
            required=False
        )
        self.add_item(self.gender_input)
        
        # City field
        self.location_input = discord.ui.TextInput(
            label="City (optional)",
            placeholder="Which city are you from?",
            default=existing_card.get('location', '') if existing_card else '',
            max_length=100,
            required=False
        )
        self.add_item(self.location_input)
        
        # Hobby field (single line to match reference design)
        self.hobbies_input = discord.ui.TextInput(
            label="Hobby",
            placeholder="Your main hobby or interest",
            default=existing_card.get('hobbies', '') if existing_card else '',
            max_length=100,
            required=False
        )
        self.add_item(self.hobbies_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Validate age input
            age = None
            if self.age_input.value.strip():
                try:
                    age = int(self.age_input.value.strip())
                    if age < 13 or age > 120:
                        await interaction.followup.send("❌ Please enter a valid age between 13 and 120.", ephemeral=True)
                        return
                except ValueError:
                    await interaction.followup.send("❌ Please enter a valid number for age.", ephemeral=True)
                    return
            
            # Create card data for Wonder member card
            card_data = {
                'user_id': str(interaction.user.id),
                'guild_id': str(interaction.guild.id),
                'name': self.name_input.value.strip(),
                'age': age,
                'gender': self.gender_input.value.strip() or None,
                'location': self.location_input.value.strip() or None,
                'hobbies': self.hobbies_input.value.strip() or None,
                'favorite_color': '#9F7AEA',  # Purple theme for Y2K aesthetic
                'background_style': 'y2k_holographic',  # Y2K holographic style
            }
            
            # Save to database
            card_id = await database.save_intro_card(card_data)
            
            if card_id:
                embed = discord.Embed(
                    title="✅ Wonder Member Card Saved!",
                    description="Your Wonder member card has been created successfully! ✨",
                    color=0x9F7AEA
                )
                embed.add_field(name="Next Steps", value="Use `/intro-view` to see your card\nUse `/intro-edit` to modify your information", inline=False)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("❌ There was an error saving your card. Please try again.", ephemeral=True)
                
        except Exception as e:
            logging.error(f"Error handling intro card modal: {e}")
            await interaction.followup.send("❌ An error occurred while saving your card.", ephemeral=True)








class IntroCardSystem:
    """Main introduction card system manager"""
    
    def __init__(self, bot):
        self.bot = bot
        
    async def create_card_embed(self, card_data: Dict[str, Any], user: discord.Member) -> discord.Embed:
        """Create an embed for displaying card info"""
        embed = discord.Embed(
            title=f"🌟 {card_data.get('name', 'Unknown')}'s Wonder Member Card",
            color=int(card_data.get('favorite_color', '#9F7AEA').replace('#', ''), 16)
        )
        
        # Basic info
        info_parts = []
        if card_data.get('age'):
            info_parts.append(f"🎂 {card_data['age']} years old")
        if card_data.get('gender'):
            info_parts.append(f"⚧️ {card_data['gender']}")
        if card_data.get('location'):
            info_parts.append(f"🏙️ {card_data['location']}")
        
        if info_parts:
            embed.add_field(name="🎮 User Info", value="\n".join(info_parts), inline=True)
        
        # Hobby
        if card_data.get('hobbies'):
            embed.add_field(name="🎯 Hobby", value=card_data['hobbies'], inline=True)
        
        # Stats
        stats = f"❤️ {card_data.get('likes_count', 0)} likes • 👀 {card_data.get('views_count', 0)} views"
        embed.add_field(name="📊 Stats", value=stats, inline=False)
        
        # Set user avatar
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Footer
        created_time = datetime.fromisoformat(card_data['created_at'])
        embed.set_footer(text=f"Connected since {created_time.strftime('%B %d, %Y')} • Wonder ✨")
        
        return embed
    
    async def generate_card_image(self, user: discord.Member, card_data: Dict[str, Any]) -> bytes:
        """Generate the visual card image"""
        try:
            # Record view only if it's a real card (has ID)
            if card_data.get('id'):
                await database.add_card_interaction(card_data['id'], str(user.id), 'view')
            
            # Generate Wonder member card
            return await canvas_utils.create_y2k_identity_card(user, card_data)
        except Exception as e:
            logging.error(f"Error generating card image: {e}")
            raise
    
    async def validate_card_data(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate card data"""
        # Check required fields
        if not data.get('name', '').strip():
            return False, "Nickname is required"
        
        # Check lengths
        if len(data.get('name', '')) > 50:
            return False, "Nickname must be 50 characters or less"
        
        if data.get('gender') and len(data['gender']) > 50:
            return False, "Gender must be 50 characters or less"
        
        if data.get('location') and len(data['location']) > 100:
            return False, "City must be 100 characters or less"
        
        if data.get('hobbies') and len(data['hobbies']) > 100:
            return False, "Hobby must be 100 characters or less"
        
        # Validate age
        if data.get('age') and (data['age'] < 13 or data['age'] > 120):
            return False, "Age must be between 13 and 120"
        
        return True, "Valid"


def init_intro_card_system(bot):
    """Initialize the introduction card system"""
    return IntroCardSystem(bot)