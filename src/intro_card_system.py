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
                    title="👋 Someone wants to say hi!",
                    description=f"{interaction.user.display_name} saw your introduction card and wants to connect!",
                    color=0x7C3AED
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
                color=0x7C3AED
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
        super().__init__(title="✨ Create Your Introduction Card" if not existing_card else "✏️ Edit Your Introduction Card")
        self.existing_card = existing_card
        
        # Name field
        self.name_input = discord.ui.TextInput(
            label="Your Name",
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
        
        # Location field
        self.location_input = discord.ui.TextInput(
            label="Location (optional)",
            placeholder="Where are you from?",
            default=existing_card.get('location', '') if existing_card else '',
            max_length=100,
            required=False
        )
        self.add_item(self.location_input)
        
        # Bio field
        self.bio_input = discord.ui.TextInput(
            label="About Me",
            style=discord.TextStyle.paragraph,
            placeholder="Tell us about yourself...",
            default=existing_card.get('bio', '') if existing_card else '',
            max_length=500,
            required=True
        )
        self.add_item(self.bio_input)
        
        # Hobbies field
        self.hobbies_input = discord.ui.TextInput(
            label="Hobbies & Interests",
            style=discord.TextStyle.paragraph,
            placeholder="What do you enjoy doing?",
            default=existing_card.get('hobbies', '') if existing_card else '',
            max_length=300,
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
            
            # Get server theme settings
            server_settings = await database.get_server_settings(str(interaction.guild.id))
            default_color = server_settings.get('intro_card_theme', '#7C3AED') if server_settings else '#7C3AED'
            default_style = server_settings.get('intro_card_style', 'gradient') if server_settings else 'gradient'
            
            # Create card data
            card_data = {
                'user_id': str(interaction.user.id),
                'guild_id': str(interaction.guild.id),
                'name': self.name_input.value.strip(),
                'age': age,
                'location': self.location_input.value.strip() or None,
                'bio': self.bio_input.value.strip(),
                'hobbies': self.hobbies_input.value.strip() or None,
                'favorite_color': default_color,
                'background_style': default_style,
            }
            
            # Save to database
            card_id = await database.save_intro_card(card_data)
            
            if card_id:
                embed = discord.Embed(
                    title="✅ Introduction Card Saved!",
                    description="Your introduction card has been created successfully!",
                    color=0x10B981
                )
                # Create a view with button to add extended info
                class ExtendedInfoView(discord.ui.View):
                    def __init__(self, card_data):
                        super().__init__(timeout=300)
                        self.card_data = card_data
                    
                    @discord.ui.button(label="➕ Add Extended Info", style=discord.ButtonStyle.primary, emoji="✨")
                    async def add_extended_info(self, interaction: discord.Interaction, button: discord.ui.Button):
                        modal = IntroCardAdvancedModal(self.card_data)
                        await interaction.response.send_modal(modal)
                
                view = ExtendedInfoView(card_data)
                embed.add_field(name="Next Steps", value="Use `/intro-view` to see your card\nClick the button below to add more information!\nNote: Card themes are managed by the bot owner.", inline=False)
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            else:
                await interaction.followup.send("❌ There was an error saving your card. Please try again.", ephemeral=True)
                
        except Exception as e:
            logging.error(f"Error handling intro card modal: {e}")
            await interaction.followup.send("❌ An error occurred while saving your card.", ephemeral=True)


class IntroCardAdvancedModal(discord.ui.Modal):
    """Modal for additional introduction card fields"""
    
    def __init__(self, existing_card: Optional[Dict[str, Any]] = None):
        super().__init__(title="✨ Extended Profile Information")
        self.existing_card = existing_card
        
        # Pronouns field
        self.pronouns_input = discord.ui.TextInput(
            label="Pronouns (optional)",
            placeholder="e.g., they/them, she/her, he/him",
            default=existing_card.get('pronouns', '') if existing_card else '',
            max_length=30,
            required=False
        )
        self.add_item(self.pronouns_input)
        
        # Occupation field
        self.occupation_input = discord.ui.TextInput(
            label="Occupation/Role (optional)",
            placeholder="What do you do for work or study?",
            default=existing_card.get('occupation', '') if existing_card else '',
            max_length=100,
            required=False
        )
        self.add_item(self.occupation_input)
        
        # Timezone field
        self.timezone_input = discord.ui.TextInput(
            label="Timezone (optional)",
            placeholder="e.g., EST, UTC+3, PST",
            default=existing_card.get('timezone', '') if existing_card else '',
            max_length=20,
            required=False
        )
        self.add_item(self.timezone_input)
        
        # Social media field
        self.social_input = discord.ui.TextInput(
            label="Social Media/Contact (optional)",
            style=discord.TextStyle.paragraph,
            placeholder="Share your social media handles or ways to connect",
            default=existing_card.get('social_media', '') if existing_card else '',
            max_length=200,
            required=False
        )
        self.add_item(self.social_input)
        
        # Fun fact field
        self.fun_fact_input = discord.ui.TextInput(
            label="Fun Fact (optional)",
            style=discord.TextStyle.paragraph,
            placeholder="Share something interesting or unique about yourself!",
            default=existing_card.get('fun_fact', '') if existing_card else '',
            max_length=200,
            required=False
        )
        self.add_item(self.fun_fact_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Get existing card data or create new
            if self.existing_card:
                card_data = self.existing_card.copy()
            else:
                # This should not happen, but handle gracefully
                card_data = {
                    'user_id': str(interaction.user.id),
                    'guild_id': str(interaction.guild.id),
                }
            
            # Update with new information
            card_data.update({
                'pronouns': self.pronouns_input.value.strip() or None,
                'occupation': self.occupation_input.value.strip() or None,
                'timezone': self.timezone_input.value.strip() or None,
                'social_media': self.social_input.value.strip() or None,
                'fun_fact': self.fun_fact_input.value.strip() or None,
            })
            
            # Save to database
            card_id = await database.save_intro_card(card_data)
            
            if card_id:
                embed = discord.Embed(
                    title="✅ Extended Information Saved!",
                    description="Your additional profile information has been updated successfully!",
                    color=0x10B981
                )
                embed.add_field(name="Next Steps", value="Use `/intro-view` to see your updated card\nCard themes are managed by the bot owner", inline=False)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("❌ There was an error saving your extended information.", ephemeral=True)
                
        except Exception as e:
            logging.error(f"Error handling advanced intro card modal: {e}")
            await interaction.followup.send("❌ An error occurred while saving your extended information.", ephemeral=True)





class IntroCardSystem:
    """Main introduction card system manager"""
    
    def __init__(self, bot):
        self.bot = bot
        
    async def create_card_embed(self, card_data: Dict[str, Any], user: discord.Member) -> discord.Embed:
        """Create an embed for displaying card info"""
        embed = discord.Embed(
            title=f"👋 Meet {card_data.get('name', 'Unknown')}",
            color=int(card_data.get('favorite_color', '#7C3AED').replace('#', ''), 16)
        )
        
        # Basic info
        info_parts = []
        if card_data.get('age'):
            info_parts.append(f"🎂 {card_data['age']} years old")
        if card_data.get('location'):
            info_parts.append(f"📍 {card_data['location']}")
        if card_data.get('pronouns'):
            info_parts.append(f"✨ {card_data['pronouns']}")
        
        if info_parts:
            embed.add_field(name="Basic Info", value="\n".join(info_parts), inline=True)
        
        # About section
        if card_data.get('bio'):
            embed.add_field(name="About Me", value=card_data['bio'], inline=False)
        
        # Hobbies
        if card_data.get('hobbies'):
            embed.add_field(name="Hobbies & Interests", value=card_data['hobbies'], inline=False)
        
        # Additional info
        extra_info = []
        if card_data.get('occupation'):
            extra_info.append(f"💼 {card_data['occupation']}")
        if card_data.get('timezone'):
            extra_info.append(f"🕐 {card_data['timezone']}")
        if card_data.get('social_media'):
            extra_info.append(f"🌐 {card_data['social_media']}")
        
        if extra_info:
            embed.add_field(name="More Info", value="\n".join(extra_info), inline=True)
        
        # Fun fact
        if card_data.get('fun_fact'):
            embed.add_field(name="🎉 Fun Fact", value=card_data['fun_fact'], inline=False)
        
        # Stats
        stats = f"❤️ {card_data.get('likes_count', 0)} likes • 👀 {card_data.get('views_count', 0)} views"
        embed.add_field(name="Stats", value=stats, inline=True)
        
        # Set user avatar
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Footer
        created_time = datetime.fromisoformat(card_data['created_at'])
        embed.set_footer(text=f"Created {created_time.strftime('%B %d, %Y')}")
        
        return embed
    
    async def generate_card_image(self, user: discord.Member, card_data: Dict[str, Any]) -> bytes:
        """Generate the visual card image"""
        try:
            # Record view
            await database.add_card_interaction(card_data['id'], str(user.id), 'view')
            
            # Generate image
            return await canvas_utils.create_introduction_card(user, card_data)
        except Exception as e:
            logging.error(f"Error generating card image: {e}")
            raise
    
    async def validate_card_data(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate card data"""
        # Check required fields
        if not data.get('name', '').strip():
            return False, "Name is required"
        
        if not data.get('bio', '').strip():
            return False, "Bio is required"
        
        # Check lengths
        if len(data.get('name', '')) > 50:
            return False, "Name must be 50 characters or less"
        
        if len(data.get('bio', '')) > 500:
            return False, "Bio must be 500 characters or less"
        
        if data.get('hobbies') and len(data['hobbies']) > 300:
            return False, "Hobbies must be 300 characters or less"
        
        # Validate age
        if data.get('age') and (data['age'] < 13 or data['age'] > 120):
            return False, "Age must be between 13 and 120"
        
        return True, "Valid"


def init_intro_card_system(bot):
    """Initialize the introduction card system"""
    return IntroCardSystem(bot)