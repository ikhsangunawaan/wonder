import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import os
import logging
import io
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import config
from database import database
from shop_system import shop_system
from giveaway_system import init_giveaway_system
from role_manager import init_role_manager
from games_system import games_system
from wondercoins_drops import init_wondercoins_drops
from leveling_system import init_leveling_system
from cooldown_manager import cooldown_manager
from intro_card_system import init_intro_card_system, IntroCardModal, IntroCardView
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

class WonderBot(commands.Bot):
    """Wonder Discord Bot - Python Version"""
    
    def __init__(self):
        # Configure bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        intents.voice_states = True
        
        # Support multiple prefixes
        def get_prefix(bot, message):
            return ['w.', '/']
        
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        # Initialize systems
        self.database = database
        self.shop_system = shop_system
        self.cooldown_manager = cooldown_manager
        self.games_system = games_system
        self.config = config
        
        # These will be initialized in setup_hook
        self.role_manager = None
        self.giveaway_system = None
        self.leveling_system = None
        self.drop_system = None
        self.intro_card_system = None
        
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logging.info("Setting up Wonder Bot...")
        
        # Initialize database
        await self.database.init()
        logging.info("Database initialized")
        
        # Initialize systems that need the client
        self.role_manager = init_role_manager(self)
        self.giveaway_system = init_giveaway_system(self)
        self.leveling_system = init_leveling_system(self)
        self.drop_system = init_wondercoins_drops(self)
        self.intro_card_system = init_intro_card_system(self)
        
        # Add intro card slash commands to tree
        self.tree.add_command(intro_create)
        self.tree.add_command(intro_edit)
        self.tree.add_command(intro_view)
        self.tree.add_command(intro_privacy)
        self.tree.add_command(intro_background)
        self.tree.add_command(intro_delete)
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logging.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logging.error(f"Failed to sync slash commands: {e}")
        
        logging.info("All systems initialized")
        
        # Sync commands
        try:
            synced = await self.tree.sync()
            logging.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logging.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logging.info(f'{self.user} has connected to Discord!')
        logging.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{config.branding['name']} | {config.prefix}help"
        )
        await self.change_presence(activity=activity)
        
        # Start background tasks (will be uncommented as systems are converted)
        # self.check_giveaways.start()
        # self.update_roles.start()
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        if message.author.bot:
            return
            
        # Create user in database if not exists
        try:
            await self.database.create_user(str(message.author.id), message.author.name)
        except Exception as e:
            logging.error(f"Error creating user: {e}")
        
        # Handle leveling system
        if hasattr(self, 'leveling_system') and self.leveling_system:
            await self.leveling_system.handle_message(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def on_member_join(self, member: discord.Member):
        """Handle member join events"""
        # Create user in database
        try:
            await self.database.create_user(str(member.id), member.name)
        except Exception as e:
            logging.error(f"Error creating user on join: {e}")
        
        # Handle welcome messages (will be implemented)
        # await self.handle_welcome(member)
    
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle command errors with detailed information"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        command_name = ctx.command.name if ctx.command else "unknown"
        
        if isinstance(error, commands.MissingRequiredArgument):
            additional_info = f"Missing parameter: `{error.param.name}`"
            await send_command_error(ctx, "missing_argument", command_name, additional_info)
            return
        
        if isinstance(error, commands.BadArgument):
            additional_info = f"Please check your input format and try again."
            await send_command_error(ctx, "bad_argument", command_name, additional_info)
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            cooldown_time = f"{error.retry_after:.1f} seconds" if error.retry_after < 60 else f"{error.retry_after/60:.1f} minutes"
            additional_info = f"Try again in {cooldown_time}"
            await send_command_error(ctx, "cooldown", command_name, additional_info)
            return
        
        if isinstance(error, commands.MissingPermissions):
            required_perms = ", ".join(error.missing_permissions)
            additional_info = f"Required permissions: {required_perms}"
            await send_command_error(ctx, "permission", command_name, additional_info)
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            additional_info = f"Bot is missing permissions: {missing_perms}"
            await send_command_error(ctx, "bot_permission", command_name, additional_info)
            return
        
        if isinstance(error, commands.NoPrivateMessage):
            additional_info = "This command can only be used in servers, not in DMs."
            await send_command_error(ctx, "no_dm", command_name, additional_info)
            return
        
        if isinstance(error, commands.ChannelNotFound):
            additional_info = "The specified channel could not be found."
            await send_command_error(ctx, "channel_not_found", command_name, additional_info)
            return
        
        if isinstance(error, commands.MemberNotFound):
            additional_info = "The specified user could not be found."
            await send_command_error(ctx, "member_not_found", command_name, additional_info)
            return
        
        if isinstance(error, commands.RoleNotFound):
            additional_info = "The specified role could not be found."
            await send_command_error(ctx, "role_not_found", command_name, additional_info)
            return
        
        # Log unexpected errors
        logging.error(f"Command error in {command_name}: {error}")
        additional_info = f"Unexpected error occurred. Please try again or contact support."
        await send_command_error(ctx, "unexpected", command_name, additional_info)
    
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle reaction additions"""
        if user.bot:
            return
            
        # Handle giveaway reactions
        if hasattr(self, 'giveaway_system') and self.giveaway_system:
            await self.giveaway_system.handle_reaction_add(reaction, user)
        
        # Handle drop reactions
        if hasattr(self, 'drop_system') and self.drop_system:
            await self.drop_system.handle_reaction_add(reaction, user)
    
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        """Handle reaction removals"""
        if user.bot:
            return
            
        # Handle giveaway reaction removals
        if hasattr(self, 'giveaway_system') and self.giveaway_system:
            await self.giveaway_system.handle_reaction_remove(reaction, user)
    
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Handle member updates"""
        if hasattr(self, 'role_manager') and self.role_manager:
            await self.role_manager.handle_member_update(before, after)
    
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice state updates for leveling"""
        if hasattr(self, 'leveling_system') and self.leveling_system:
            await self.leveling_system.handle_voice_update(member, before, after)

# Economy Commands (Hybrid: both prefix and slash)
@commands.hybrid_command(name='balance', aliases=['bal'])
@app_commands.describe(user='User to check balance for (mention, ID, or username - optional)')
async def balance(ctx: commands.Context, user: str = None):
    """Check your balance or another user's balance"""
    if user:
        target_user = parse_user_mention_or_id(user, ctx.guild)
        if not target_user:
            await send_command_error(ctx, "member_not_found", "balance", f"User '{user}' not found. Use mention, ID, or username.")
            return
    else:
        target_user = ctx.author
    
    user_data = await ctx.bot.database.get_user(str(target_user.id))
    if not user_data:
        await ctx.bot.database.create_user(str(target_user.id), target_user.name)
        user_data = await ctx.bot.database.get_user(str(target_user.id))
    
    balance = user_data['balance'] if user_data else 0
    
    # Check if user has premium role for special styling
    role_status = "✨ Wonder Dreamer"
    role_color = config.colors['primary']
    
    if any(role.name.lower() in ['premium', 'vip'] for role in target_user.roles):
        role_status = "🌟 Premium Dreamer"
        role_color = config.colors['royal']
    elif target_user.premium_since:
        role_status = "💫 Server Booster"
        role_color = config.colors['luxury']
    
    embed = discord.Embed(
        title=f"💰 Wonder Balance",
        description=f"**{target_user.display_name}** - *{role_status}*\n\n"
                   f"**{config.currency['symbol']} {balance:,}** {config.currency['name']}",
        color=int(role_color.replace('#', ''), 16)
    )
    embed.set_thumbnail(url=target_user.display_avatar.url)
    embed.add_field(
        name="🔮 Wonder Stats",
        value=f"Total Earned: **{user_data.get('total_earned', 0):,}** {config.currency['symbol']}\n"
              f"Member Since: {target_user.joined_at.strftime('%B %d, %Y') if target_user.joined_at else 'Unknown'}",
        inline=False
    )
    embed.set_footer(text="Wonder Bot • Where Wonder Meets Chrome Dreams", 
                    icon_url="https://cdn.discordapp.com/emojis/✨.png")
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='daily')
async def daily(ctx: commands.Context):
    """Claim your daily wonder reward"""
    from datetime import datetime, timedelta
    
    user_data = await ctx.bot.database.get_user(str(ctx.author.id))
    if not user_data:
        await ctx.bot.database.create_user(str(ctx.author.id), ctx.author.name)
        user_data = await ctx.bot.database.get_user(str(ctx.author.id))
    
    # Check cooldown
    now = datetime.now()
    last_claim = user_data.get('daily_last_claimed')
    
    if last_claim:
        last_claim_dt = datetime.fromisoformat(last_claim)
        if now - last_claim_dt < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last_claim_dt)
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            embed = discord.Embed(
                title="🌙 Daily Wonder Cooldown",
                description=f"✨ Your daily wonder energy is recharging...\n\n"
                           f"⏰ Available in: **{hours}h {minutes}m**\n"
                           f"💰 Next reward: **{config.currency['dailyAmount']:,}** {config.currency['symbol']}",
                color=int(config.colors['warning'].replace('#', ''), 16)
            )
            embed.set_author(name=f"{ctx.author.display_name}'s Daily Wonder", 
                           icon_url=ctx.author.display_avatar.url)
            embed.add_field(
                name="💫 Tip",
                value="Daily rewards reset every 24 hours and include bonus rewards for Boosters and Premium members!",
                inline=False
            )
            embed.set_footer(text="Wonder Bot • Where Wonder Meets Chrome Dreams")
            await ctx.send(embed=embed)
            return
    
    # Calculate daily reward with bonuses
    base_amount = config.currency['dailyAmount']
    daily_amount = base_amount
    bonus_text = ""
    
    # Check for premium role bonus
    if any(role.name.lower() in ['premium', 'vip'] for role in ctx.author.roles):
        daily_amount = int(base_amount * config.multipliers['premium']['daily'])
        bonus_text = "🌟 Premium bonus applied!"
    elif ctx.author.premium_since:  # Boost bonus
        daily_amount = int(base_amount * config.multipliers['booster']['daily'])
        bonus_text = "💫 Server Booster bonus applied!"
    
    await ctx.bot.database.update_balance(str(ctx.author.id), daily_amount)
    await ctx.bot.database.update_daily_claim(str(ctx.author.id))
    await ctx.bot.database.add_transaction(str(ctx.author.id), 'daily', daily_amount, f'Daily reward{" with bonus" if bonus_text else ""}')
    
    # Get updated balance for display
    updated_user = await ctx.bot.database.get_user(str(ctx.author.id))
    new_balance = updated_user['balance']
    
    embed = discord.Embed(
        title=f"✨ Daily Wonder Claimed!",
        description=f"🎉 **+{daily_amount:,}** {config.currency['symbol']} {config.currency['name']}\n\n"
                   f"💰 **New Balance:** {new_balance:,} {config.currency['symbol']}\n"
                   f"{bonus_text}",
        color=int(config.colors['success'].replace('#', ''), 16)
    )
    embed.set_author(name=f"{ctx.author.display_name}'s Daily Wonder", 
                    icon_url=ctx.author.display_avatar.url)
    
    if bonus_text:
        bonus_amount = daily_amount - base_amount
        embed.add_field(
            name="🎁 Bonus Breakdown",
            value=f"Base: **{base_amount:,}** {config.currency['symbol']}\n"
                  f"Bonus: **+{bonus_amount:,}** {config.currency['symbol']}\n"
                  f"Total: **{daily_amount:,}** {config.currency['symbol']}",
            inline=True
        )
    
    embed.add_field(
        name="⏰ Next Claim",
        value="Available in 24 hours",
        inline=True
    )
    embed.set_footer(text="Wonder Bot • Where Wonder Meets Chrome Dreams")
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='work')
async def work(ctx: commands.Context):
    """Work in the wonder kingdom to earn coins"""
    from datetime import datetime, timedelta
    import random
    
    user_data = await ctx.bot.database.get_user(str(ctx.author.id))
    if not user_data:
        await ctx.bot.database.create_user(str(ctx.author.id), ctx.author.name)
        user_data = await ctx.bot.database.get_user(str(ctx.author.id))
    
    # Check cooldown
    now = datetime.now()
    last_work = user_data.get('work_last_used')
    
    if last_work:
        last_work_dt = datetime.fromisoformat(last_work)
        if now - last_work_dt < timedelta(minutes=config.cooldowns['work']):
            remaining = timedelta(minutes=config.cooldowns['work']) - (now - last_work_dt)
            minutes, seconds = divmod(remaining.seconds, 60)
            
            embed = discord.Embed(
                title="⏰ Work Cooldown",
                description=f"You can work again in **{minutes}m {seconds}s**",
                color=int(config.colors['warning'].replace('#', ''), 16)
            )
            embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
            await ctx.send(embed=embed)
            return
    
    # Generate work reward
    base_amount = config.currency['workAmount']
    work_amount = random.randint(base_amount - 10, base_amount + 20)
    
    # Check for booster bonus
    if ctx.author.premium_since:  # Boost bonus
        work_amount += config.booster['workBonus']
    
    # Wonder work job options
    jobs = [
        "wonder coding", "mystical designing", "dream streaming", "kingdom moderating", 
        "helping fellow dreamers", "creating wonder content", "building mystical bots", 
        "managing dream servers", "tutoring wonder magic", "chrome development"
    ]
    job = random.choice(jobs)
    
    await ctx.bot.database.update_balance(str(ctx.author.id), work_amount)
    await ctx.bot.database.update_work_claim(str(ctx.author.id))
    await ctx.bot.database.add_transaction(str(ctx.author.id), 'work', work_amount, f'Work: {job}')
    
    embed = discord.Embed(
        title=f"✨ Wonder Work Complete",
        description=f"You worked on **{job}** and earned **{work_amount:,}** {config.currency['name']}!",
        color=int(config.colors['success'].replace('#', ''), 16)
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='leaderboard', aliases=['lb', 'top'])
async def leaderboard(ctx: commands.Context):
    """View the wonder leaderboard"""
    top_users = await ctx.bot.database.get_top_users(10)
    
    if not top_users:
        embed = discord.Embed(
            title="🌙 Empty Leaderboard",
            description="No users found on the leaderboard yet!",
            color=int(config.colors['warning'].replace('#', ''), 16)
        )
        embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"🌌 {config.currency['name']} Wonder Leaderboard",
        color=int(config.colors['primary'].replace('#', ''), 16)
    )
    
    description = ""
    for i, user_data in enumerate(top_users, 1):
        try:
            user = ctx.bot.get_user(int(user_data['user_id']))
            username = user.display_name if user else user_data['username']
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            description += f"{medal} **{username}** - {user_data['balance']:,} {config.currency['symbol']}\n"
        except:
            continue
    
    embed.description = description
    embed.set_footer(text=f"Total dreamers: {len(top_users)} • Wonderkind • Where Wonder Meets Chrome Dreams")
    
    await ctx.send(embed=embed)

# Game Commands with Animations (Hybrid: both prefix and slash)
@commands.hybrid_command(name='coinflip', aliases=['cf'])
@app_commands.describe(
    bet_amount='Amount of WonderCoins to bet',
    choice='Choose heads or tails (h/t)'
)
async def coinflip(ctx: commands.Context, bet_amount: int, choice: str):
    """Play animated wonder coinflip game"""
    # Validate bet amount
    min_bet = config.games['coinflip']['minBet']
    max_bet = config.games['coinflip']['maxBet']
    
    if bet_amount < min_bet or bet_amount > max_bet:
        await send_command_error(
            ctx, "bad_argument", "coinflip", 
            f"Bet amount must be between {min_bet} and {max_bet} WonderCoins."
        )
        return
    
    # Validate choice
    if choice.lower() not in ['h', 'heads', 't', 'tails']:
        await send_command_error(
            ctx, "bad_argument", "coinflip", 
            f"Choice must be 'h', 'heads', 't', or 'tails'."
        )
        return
    
    result = await ctx.bot.games_system.coinflip(str(ctx.author.id), bet_amount, choice, ctx)
    
    if not result['success']:
        error_embed = discord.Embed(
            title="🌙 Coinflip Error",
            description=result['message'],
            color=int(config.colors['error'].replace('#', ''), 16)
        )
        error_embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
        await ctx.send(embed=error_embed)
        return
    
    # Animation message is already updated in the game method
    # No need to send another message if animation was shown

@commands.hybrid_command(name='dice')
@app_commands.describe(
    bet_amount='Amount of WonderCoins to bet',
    target='Target number to roll (1-6)'
)
async def dice(ctx: commands.Context, bet_amount: int, target: int):
    """Play animated wonder dice game"""
    # Validate bet amount
    min_bet = config.games['dice']['minBet']
    max_bet = config.games['dice']['maxBet']
    
    if bet_amount < min_bet or bet_amount > max_bet:
        await send_command_error(
            ctx, "bad_argument", "dice", 
            f"Bet amount must be between {min_bet} and {max_bet} WonderCoins."
        )
        return
    
    # Validate target number
    if target < 1 or target > 6:
        await send_command_error(
            ctx, "bad_argument", "dice", 
            f"Target number must be between 1 and 6."
        )
        return
    
    result = await ctx.bot.games_system.dice(str(ctx.author.id), bet_amount, target, ctx)
    
    if not result['success']:
        error_embed = discord.Embed(
            title="🌙 Dice Error",
            description=result['message'],
            color=int(config.colors['error'].replace('#', ''), 16)
        )
        error_embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
        await ctx.send(embed=error_embed)
        return
    
    # Animation message is already updated in the game method
    # No need to send another message if animation was shown

@commands.hybrid_command(name='slots')
@app_commands.describe(bet_amount='Amount of WonderCoins to bet')
async def slots(ctx: commands.Context, bet_amount: int):
    """Play animated wonder slot machine"""
    # Validate bet amount
    min_bet = config.games['slots']['minBet']
    max_bet = config.games['slots']['maxBet']
    
    if bet_amount < min_bet or bet_amount > max_bet:
        await send_command_error(
            ctx, "bad_argument", "slots", 
            f"Bet amount must be between {min_bet} and {max_bet} WonderCoins."
        )
        return
    
    result = await ctx.bot.games_system.slots(str(ctx.author.id), bet_amount, ctx)
    
    if not result['success']:
        error_embed = discord.Embed(
            title="🌙 Slots Error",
            description=result['message'],
            color=int(config.colors['error'].replace('#', ''), 16)
        )
        error_embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
        await ctx.send(embed=error_embed)
        return
    
    # Animation message is already updated in the game method
    # No need to send another message if animation was shown

@commands.hybrid_command(name='gamestats')
@app_commands.describe(user='User to check gambling stats for (mention, ID, or username - optional)')
async def gamestats(ctx: commands.Context, user: str = None):
    """View gambling statistics"""
    if user:
        target_user = parse_user_mention_or_id(user, ctx.guild)
        if not target_user:
            await send_command_error(ctx, "member_not_found", "gamestats", f"User '{user}' not found. Use mention, ID, or username.")
            return
    else:
        target_user = ctx.author
    embed = await ctx.bot.games_system.create_gambling_stats_embed(str(target_user.id), target_user.display_name)
    await ctx.send(embed=embed)

# Shop Commands
@commands.hybrid_command(name='shop')
@app_commands.describe(category='Shop category to view', page='Page number')
async def shop(ctx: commands.Context, category: str = 'all', page: int = 1):
    """View the shop"""
    embed = await ctx.bot.shop_system.get_shop_embed(category, page)
    await ctx.send(embed=embed)

@commands.hybrid_command(name='buy')
@app_commands.describe(item_id='ID of the item to buy', quantity='Number of items to buy')
async def buy(ctx: commands.Context, item_id: str, quantity: int = 1):
    """Buy an item from the shop"""
    result = await ctx.bot.shop_system.purchase_item(str(ctx.author.id), item_id, quantity)
    
    embed = discord.Embed(
        title="🛒 Purchase Result",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    
    if result['success']:
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='inventory', aliases=['inv'])
@app_commands.describe(page='Page number of inventory to view')
async def inventory(ctx: commands.Context, page: int = 1):
    """View your inventory"""
    embed = await ctx.bot.shop_system.get_inventory_embed(str(ctx.author.id), page)
    await ctx.send(embed=embed)

@commands.hybrid_command(name='use')
@app_commands.describe(item_id='ID of the item to use')
async def use_item(ctx: commands.Context, item_id: str):
    """Use an item from inventory"""
    result = await ctx.bot.shop_system.use_item(str(ctx.author.id), item_id)
    
    embed = discord.Embed(
        title="📦 Item Usage",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    
    await ctx.send(embed=embed)

# Leveling Commands
@commands.hybrid_command(name='rank')
@app_commands.describe(user='User to check rank for (mention, ID, or username - optional)')
async def rank(ctx: commands.Context, user: str = None):
    """View comprehensive rank information across all categories"""
    if user:
        target_user = parse_user_mention_or_id(user, ctx.guild)
        if not target_user:
            await send_command_error(ctx, "member_not_found", "rank", f"User '{user}' not found. Use mention, ID, or username.")
            return
    else:
        target_user = ctx.author
    rank_info = await ctx.bot.leveling_system.get_user_rank(str(target_user.id))
    
    if not rank_info:
        await ctx.send(f"❌ No level data found for {target_user.display_name}")
        return
    
    embed = discord.Embed(
        title=f"🌟 Comprehensive Rank - {target_user.display_name}",
        description="*Multi-Category Leveling System*",
        color=int(config.colors['primary'].replace('#', ''), 16)
    )
    
    # Add category information
    categories = {
        'text': {'emoji': '💬', 'name': 'Text Chat'},
        'voice': {'emoji': '🎤', 'name': 'Voice Activity'},
        'role': {'emoji': '🎭', 'name': 'Community Role'},
        'overall': {'emoji': '⭐', 'name': 'Overall Progress'}
    }
    
    for category, info in categories.items():
        level_data = rank_info['levels'].get(category, {})
        current_role = rank_info['roles_earned'].get(category)
        next_role = rank_info['next_roles'].get(category)
        
        level = level_data.get('level', 0)
        xp = level_data.get('xp', 0)
        xp_needed = level_data.get('xp_needed', 0)
        
        # Build field value
        field_value = f"**Level {level}** • {xp:,} XP"
        
        if current_role:
            field_value += f"\n🏆 **{current_role['name']}**"
            if current_role['perks']:
                field_value += f"\n🎁 {', '.join(current_role['perks'][:2])}"
        
        if next_role and xp_needed > 0:
            field_value += f"\n\n🎯 Next: **{next_role['name']}** ({next_role['levels_needed']} levels)"
        elif level >= 50:
            field_value += f"\n\n🏆 **MAX LEVEL REACHED!**"
        
        embed.add_field(
            name=f"{info['emoji']} {info['name']}",
            value=field_value,
            inline=True
        )
    
    # Add prestige information if eligible
    prestige_info = rank_info.get('prestige_info', {})
    if prestige_info.get('eligible'):
        embed.add_field(
            name="⭐ Prestige Eligible",
            value="🌟 **You can prestige!**\nAll categories at level 50\nUnlock exclusive benefits",
            inline=False
        )
    
    # Add statistics
    stats_value = f"💬 **Messages:** {rank_info['total_messages']:,}\n"
    if rank_info.get('total_voice_time'):
        hours = rank_info['total_voice_time'] // 3600
        stats_value += f"🎤 **Voice Time:** {hours:,} hours\n"
    
    prestige_level = rank_info.get('prestige_level', 0)
    if prestige_level > 0:
        stats_value += f"⭐ **Prestige Level:** {prestige_level}"
    
    embed.add_field(
        name="📊 Statistics",
        value=stats_value,
        inline=False
    )
    
    embed.set_thumbnail(url=target_user.display_avatar.url)
    embed.set_footer(text="Wonder Leveling System • Progress across all activities")
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='roles')
@app_commands.describe(category='Category to view roles for (text/voice/role/overall)')
async def level_roles(ctx: commands.Context, category: str = None):
    """View all available level roles and their requirements"""
    level_roles_config = config.get('leveling.levelRoles', {})
    
    if not level_roles_config:
        await ctx.send("❌ Level roles system is not configured.")
        return
    
    embed = discord.Embed(
        title="🏆 Wonder Level Roles System",
        description="*Earn roles and perks as you level up in different categories*",
        color=int(config.colors['primary'].replace('#', ''), 16)
    )
    
    # If specific category requested
    if category and category.lower() in level_roles_config:
        cat_name = category.lower()
        category_roles = level_roles_config[cat_name]
        
        category_names = {
            'text': '💬 Text Chat Roles',
            'voice': '🎤 Voice Activity Roles', 
            'role': '🎭 Community Role Roles',
            'overall': '⭐ Overall Progress Roles'
        }
        
        embed.title = f"🏆 {category_names.get(cat_name, f'{cat_name.title()} Roles')}"
        
        for level in sorted([int(x) for x in category_roles.keys()]):
            role_info = category_roles[str(level)]
            
            field_value = f"**Color:** {role_info['color']}\n"
            field_value += f"**Perks:** {', '.join(role_info['perks'])}"
            
            embed.add_field(
                name=f"Level {level} - {role_info['name']}",
                value=field_value,
                inline=False
            )
    
    else:
        # Show overview of all categories
        category_info = {
            'text': {'emoji': '💬', 'name': 'Text Chat', 'desc': 'Earned through messaging'},
            'voice': {'emoji': '🎤', 'name': 'Voice Activity', 'desc': 'Earned through voice participation'},
            'role': {'emoji': '🎭', 'name': 'Community Role', 'desc': 'Earned through community activities'},
            'overall': {'emoji': '⭐', 'name': 'Overall Progress', 'desc': 'Combined progress across all categories'}
        }
        
        for cat_key, cat_data in category_info.items():
            if cat_key in level_roles_config:
                roles = level_roles_config[cat_key]
                role_count = len(roles)
                max_level = max([int(x) for x in roles.keys()]) if roles else 0
                
                field_value = f"{cat_data['desc']}\n"
                field_value += f"**{role_count} roles** available (Level 5-{max_level})\n"
                field_value += f"Use `/roles {cat_key}` for details"
                
                embed.add_field(
                    name=f"{cat_data['emoji']} {cat_data['name']}",
                    value=field_value,
                    inline=True
                )
    
    # Add prestige information
    prestige_config = config.get('leveling.prestigeSystem', {})
    if prestige_config.get('enabled'):
        prestige_levels = prestige_config.get('levels', {})
        prestige_value = f"Unlock after reaching Level 50 in all categories\n"
        prestige_value += f"**{len(prestige_levels)} Prestige Levels** available\n"
        prestige_value += f"Permanent bonuses and exclusive perks"
        
        embed.add_field(
            name="⭐ Prestige System",
            value=prestige_value,
            inline=False
        )
    
    embed.set_footer(text="Use /rank to see your current progress • /roles <category> for detailed role info")
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='prestige')
async def prestige_info(ctx: commands.Context):
    """View prestige system information and requirements"""
    prestige_config = config.get('leveling.prestigeSystem', {})
    
    if not prestige_config.get('enabled'):
        await ctx.send("❌ Prestige system is not enabled.")
        return
    
    embed = discord.Embed(
        title="⭐ Wonder Prestige System",
        description="*Ultimate achievement for dedicated community members*",
        color=int('#FFD700'.replace('#', ''), 16)
    )
    
    # Requirements
    requirements = prestige_config.get('requirements', {})
    req_value = ""
    if requirements.get('allCategoriesLevel50'):
        req_value += "🏆 **Level 50** in all categories (Text, Voice, Role, Overall)\n"
    if requirements.get('minimumActivity'):
        req_value += f"📊 **{requirements['minimumActivity']}** minimum activity points\n"
    if requirements.get('communityContribution'):
        req_value += f"🤝 **{requirements['communityContribution']}** community contribution points\n"
    
    embed.add_field(
        name="📋 Requirements",
        value=req_value,
        inline=False
    )
    
    # Prestige levels
    levels = prestige_config.get('levels', {})
    for level in sorted([int(x) for x in levels.keys()]):
        level_info = levels[str(level)]
        bonus_percent = int(level_info['bonus'] * 100)
        
        embed.add_field(
            name=f"⭐ {level_info['name']}",
            value=f"**{bonus_percent}% XP Bonus** for all activities\nExclusive perks and recognition",
            inline=True
        )
    
    # Benefits
    rewards = prestige_config.get('rewards', {})
    benefits_value = ""
    if rewards.get('prestigeRoles'):
        benefits_value += "🏆 Exclusive prestige roles with unique colors\n"
    if rewards.get('specialPerks'):
        benefits_value += "🎁 Special server perks and privileges\n"
    if rewards.get('permanentBonuses'):
        benefits_value += "⚡ Permanent XP bonuses that stack\n"
    
    embed.add_field(
        name="🎁 Benefits",
        value=benefits_value,
        inline=False
    )
    
    embed.set_footer(text="Use /rank to check your prestige eligibility")
    
    await ctx.send(embed=embed)

# =============================================================================
# ADMIN LEVELING MANAGEMENT COMMANDS
# =============================================================================

@commands.hybrid_command(name='toggle-category')
@commands.has_permissions(administrator=True)
@app_commands.describe(category='Category to toggle (text/voice/role/overall)', enabled='Enable or disable the category')
async def toggle_category(ctx: commands.Context, category: str, enabled: bool):
    """Enable or disable a leveling category (Admin only)"""
    valid_categories = ['text', 'voice', 'role', 'overall']
    
    if category.lower() not in valid_categories:
        await send_command_error(ctx, "bad_argument", "toggle-category", f"Category must be one of: {', '.join(valid_categories)}")
        return
    
    category = category.lower()
    
    # Get current server settings
    server_settings = await database.get_server_settings(str(ctx.guild.id))
    if not server_settings:
        server_settings = {'guild_id': str(ctx.guild.id)}
    
    # Update category setting
    if 'leveling_categories' not in server_settings:
        server_settings['leveling_categories'] = {
            'text': True,
            'voice': True,
            'role': True,
            'overall': True
        }
    
    server_settings['leveling_categories'][category] = enabled
    success = await database.save_server_settings(server_settings)
    
    if success:
        status = "enabled" if enabled else "disabled"
        embed = discord.Embed(
            title=f"⚙️ Category {status.title()}",
            description=f"**{category.title()}** leveling category has been **{status}**.",
            color=int(config.colors['success' if enabled else 'warning'].replace('#', ''), 16)
        )
        
        if enabled:
            embed.add_field(
                name="✅ Category Active",
                value=f"Users will now earn XP in the **{category}** category.",
                inline=False
            )
        else:
            embed.add_field(
                name="⏸️ Category Paused",
                value=f"Users will no longer earn XP in the **{category}** category.\nExisting progress is preserved.",
                inline=False
            )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to update category setting. Please try again.",
            color=int(config.colors['error'].replace('#', ''), 16)
        )
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='set-user-xp')
@commands.has_permissions(administrator=True)
@app_commands.describe(user='User to modify (mention, ID, or username)', category='XP category (text/voice/role/overall)', amount='XP amount to set')
async def set_user_xp(ctx: commands.Context, user: str, category: str, amount: int):
    """Set user's XP in a specific category (Admin only)"""
    valid_categories = ['text', 'voice', 'role', 'overall']
    
    if category.lower() not in valid_categories:
        await send_command_error(ctx, "bad_argument", "set-user-xp", f"Category must be one of: {', '.join(valid_categories)}")
        return
    
    target_user = parse_user_mention_or_id(user, ctx.guild)
    if not target_user:
        await send_command_error(ctx, "member_not_found", "set-user-xp", f"User '{user}' not found. Use mention, ID, or username.")
        return
    
    if amount < 0:
        await send_command_error(ctx, "bad_argument", "set-user-xp", "XP amount cannot be negative.")
        return
    
    category = category.lower()
    
    # Set user XP
    user_data = await database.get_user(str(target_user.id))
    if not user_data:
        user_data = {'user_id': str(target_user.id)}
    
    old_xp = user_data.get(f'{category}_xp', 0)
    user_data[f'{category}_xp'] = amount
    
    # Calculate new level
    from leveling_system import LevelingSystem
    level_system = LevelingSystem(None)
    new_level = level_system.level_formula['calculateLevel'](amount)
    old_level = level_system.level_formula['calculateLevel'](old_xp)
    
    success = await database.save_user(user_data)
    
    if success:
        embed = discord.Embed(
            title="⚙️ User XP Updated",
            description=f"**{target_user.display_name}**'s {category} XP has been set.",
            color=int(config.colors['success'].replace('#', ''), 16)
        )
        
        embed.add_field(
            name="📊 Changes",
            value=f"**Category:** {category.title()}\n"
                  f"**Old XP:** {old_xp:,}\n"
                  f"**New XP:** {amount:,}\n"
                  f"**Old Level:** {old_level}\n"
                  f"**New Level:** {new_level}",
            inline=True
        )
        
        if new_level != old_level:
            embed.add_field(
                name="🎉 Level Change",
                value=f"Level changed from **{old_level}** to **{new_level}**",
                inline=True
            )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to update user XP. Please try again.",
            color=int(config.colors['error'].replace('#', ''), 16)
        )
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='add-user-xp')
@commands.has_permissions(administrator=True)
@app_commands.describe(user='User to modify (mention, ID, or username)', category='XP category (text/voice/role/overall)', amount='XP amount to add')
async def add_user_xp(ctx: commands.Context, user: str, category: str, amount: int):
    """Add XP to user in a specific category (Admin only)"""
    valid_categories = ['text', 'voice', 'role', 'overall']
    
    if category.lower() not in valid_categories:
        await send_command_error(ctx, "bad_argument", "add-user-xp", f"Category must be one of: {', '.join(valid_categories)}")
        return
    
    target_user = parse_user_mention_or_id(user, ctx.guild)
    if not target_user:
        await send_command_error(ctx, "member_not_found", "add-user-xp", f"User '{user}' not found. Use mention, ID, or username.")
        return
    
    category = category.lower()
    
    # Add user XP
    user_data = await database.get_user(str(target_user.id))
    if not user_data:
        user_data = {'user_id': str(target_user.id)}
    
    old_xp = user_data.get(f'{category}_xp', 0)
    new_xp = max(0, old_xp + amount)  # Ensure XP doesn't go negative
    user_data[f'{category}_xp'] = new_xp
    
    # Calculate levels
    from leveling_system import LevelingSystem
    level_system = LevelingSystem(None)
    new_level = level_system.level_formula['calculateLevel'](new_xp)
    old_level = level_system.level_formula['calculateLevel'](old_xp)
    
    success = await database.save_user(user_data)
    
    if success:
        embed = discord.Embed(
            title="⚙️ User XP Modified",
            description=f"**{target_user.display_name}**'s {category} XP has been modified.",
            color=int(config.colors['success'].replace('#', ''), 16)
        )
        
        embed.add_field(
            name="📊 Changes",
            value=f"**Category:** {category.title()}\n"
                  f"**XP Change:** {amount:+,}\n"
                  f"**Old XP:** {old_xp:,}\n"
                  f"**New XP:** {new_xp:,}\n"
                  f"**Level:** {old_level} → {new_level}",
            inline=True
        )
        
        if new_level != old_level:
            level_change = "increased" if new_level > old_level else "decreased"
            embed.add_field(
                name=f"🎉 Level {level_change.title()}",
                value=f"Level {level_change} by **{abs(new_level - old_level)}**",
                inline=True
            )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to modify user XP. Please try again.",
            color=int(config.colors['error'].replace('#', ''), 16)
        )
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='reset-user-xp')
@commands.has_permissions(administrator=True)
@app_commands.describe(user='User to reset (mention, ID, or username)', category='XP category to reset (text/voice/role/overall/all)')
async def reset_user_xp(ctx: commands.Context, user: str, category: str = 'all'):
    """Reset user's XP in specific category or all categories (Admin only)"""
    valid_categories = ['text', 'voice', 'role', 'overall', 'all']
    
    if category.lower() not in valid_categories:
        await send_command_error(ctx, "bad_argument", "reset-user-xp", f"Category must be one of: {', '.join(valid_categories)}")
        return
    
    target_user = parse_user_mention_or_id(user, ctx.guild)
    if not target_user:
        await send_command_error(ctx, "member_not_found", "reset-user-xp", f"User '{user}' not found. Use mention, ID, or username.")
        return
    
    category = category.lower()
    
    # Confirmation for reset
    class ConfirmResetView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            
        @discord.ui.button(label="✅ Confirm Reset", style=discord.ButtonStyle.danger)
        async def confirm_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
            user_data = await database.get_user(str(target_user.id))
            if not user_data:
                user_data = {'user_id': str(target_user.id)}
            
            reset_categories = ['text', 'voice', 'role', 'overall'] if category == 'all' else [category]
            
            for cat in reset_categories:
                user_data[f'{cat}_xp'] = 0
            
            success = await database.save_user(user_data)
            
            if success:
                embed = discord.Embed(
                    title="✅ XP Reset Complete",
                    description=f"**{target_user.display_name}**'s XP has been reset.",
                    color=int(config.colors['success'].replace('#', ''), 16)
                )
                
                if category == 'all':
                    embed.add_field(
                        name="🔄 Reset Categories",
                        value="All categories (Text, Voice, Role, Overall) reset to 0 XP",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🔄 Reset Category",
                        value=f"**{category.title()}** category reset to 0 XP",
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Failed to reset user XP. Please try again.",
                    color=int(config.colors['error'].replace('#', ''), 16)
                )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        async def cancel_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = discord.Embed(
                title="❌ Reset Cancelled",
                description="XP reset has been cancelled.",
                color=int(config.colors['warning'].replace('#', ''), 16)
            )
            await interaction.response.edit_message(embed=embed, view=None)
    
    embed = discord.Embed(
        title="⚠️ Confirm XP Reset",
        description=f"Are you sure you want to reset **{target_user.display_name}**'s XP?",
        color=int(config.colors['warning'].replace('#', ''), 16)
    )
    
    if category == 'all':
        embed.add_field(
            name="🔄 Reset Scope",
            value="**ALL CATEGORIES** will be reset to 0 XP\n(Text, Voice, Role, Overall)",
            inline=False
        )
    else:
        embed.add_field(
            name="🔄 Reset Scope",
            value=f"**{category.title()}** category will be reset to 0 XP",
            inline=False
        )
    
    embed.add_field(
        name="⚠️ Warning",
        value="This action cannot be undone!",
        inline=False
    )
    
    view = ConfirmResetView()
    await ctx.send(embed=embed, view=view)

@commands.hybrid_command(name='set-user-currency')
@commands.has_permissions(administrator=True)
@app_commands.describe(user='User to modify (mention, ID, or username)', amount='Currency amount to set')
async def set_user_currency(ctx: commands.Context, user: str, amount: int):
    """Set user's currency balance (Admin only)"""
    target_user = parse_user_mention_or_id(user, ctx.guild)
    if not target_user:
        await send_command_error(ctx, "member_not_found", "set-user-currency", f"User '{user}' not found. Use mention, ID, or username.")
        return
    
    if amount < 0:
        await send_command_error(ctx, "bad_argument", "set-user-currency", "Currency amount cannot be negative.")
        return
    
    # Set user currency
    user_data = await database.get_user(str(target_user.id))
    if not user_data:
        user_data = {'user_id': str(target_user.id)}
    
    old_balance = user_data.get('balance', 0)
    user_data['balance'] = amount
    
    success = await database.save_user(user_data)
    
    if success:
        embed = discord.Embed(
            title="💰 Currency Updated",
            description=f"**{target_user.display_name}**'s balance has been set.",
            color=int(config.colors['success'].replace('#', ''), 16)
        )
        
        embed.add_field(
            name="💸 Changes",
            value=f"**Old Balance:** {old_balance:,} {config.currency['symbol']}\n"
                  f"**New Balance:** {amount:,} {config.currency['symbol']}\n"
                  f"**Difference:** {amount - old_balance:+,} {config.currency['symbol']}",
            inline=True
        )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to update user currency. Please try again.",
            color=int(config.colors['error'].replace('#', ''), 16)
        )
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='add-user-currency')
@commands.has_permissions(administrator=True)
@app_commands.describe(user='User to modify (mention, ID, or username)', amount='Currency amount to add (use negative to subtract)')
async def add_user_currency(ctx: commands.Context, user: str, amount: int):
    """Add currency to user's balance (Admin only)"""
    target_user = parse_user_mention_or_id(user, ctx.guild)
    if not target_user:
        await send_command_error(ctx, "member_not_found", "add-user-currency", f"User '{user}' not found. Use mention, ID, or username.")
        return
    
    # Add user currency
    user_data = await database.get_user(str(target_user.id))
    if not user_data:
        user_data = {'user_id': str(target_user.id)}
    
    old_balance = user_data.get('balance', 0)
    new_balance = max(0, old_balance + amount)  # Ensure balance doesn't go negative
    user_data['balance'] = new_balance
    
    success = await database.save_user(user_data)
    
    if success:
        embed = discord.Embed(
            title="💰 Currency Modified",
            description=f"**{target_user.display_name}**'s balance has been modified.",
            color=int(config.colors['success'].replace('#', ''), 16)
        )
        
        embed.add_field(
            name="💸 Changes",
            value=f"**Change:** {amount:+,} {config.currency['symbol']}\n"
                  f"**Old Balance:** {old_balance:,} {config.currency['symbol']}\n"
                  f"**New Balance:** {new_balance:,} {config.currency['symbol']}",
            inline=True
        )
        
        if amount > 0:
            embed.add_field(
                name="💰 Added",
                value=f"Added {amount:,} {config.currency['symbol']}",
                inline=True
            )
        elif amount < 0:
            embed.add_field(
                name="💸 Deducted",
                value=f"Deducted {abs(amount):,} {config.currency['symbol']}",
                inline=True
            )
    else:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to modify user currency. Please try again.",
            color=int(config.colors['error'].replace('#', ''), 16)
        )
    
    await ctx.send(embed=embed)

# =============================================================================
# ADVANCED GIVEAWAY COMMANDS
# =============================================================================

def parse_role_mentions(role_str: str, guild: discord.Guild) -> List[discord.Role]:
    """Parse role mentions or names from string"""
    if not role_str:
        return []
    
    roles = []
    role_parts = role_str.split(',')
    
    for part in role_parts:
        part = part.strip()
        if not part:
            continue
            
        # Try role mention first
        if part.startswith('<@&') and part.endswith('>'):
            role_id = part[3:-1]
            role = guild.get_role(int(role_id))
            if role:
                roles.append(role)
        else:
            # Try role name
            role = discord.utils.get(guild.roles, name=part)
            if role:
                roles.append(role)
    
    return roles

@commands.group(name='giveaway', aliases=['ga'], invoke_without_command=True)
@commands.has_permissions(manage_guild=True)
async def giveaway_group(ctx: commands.Context):
    """Advanced giveaway system - Use subcommands for specific actions"""
    embed = discord.Embed(
        title="🎉 Advanced Giveaway System",
        description="Use the following subcommands to manage giveaways:",
        color=int(config.colors['primary'].replace('#', ''), 16)
    )
    
    embed.add_field(
        name="📝 Create Giveaway",
        value="`w.giveaway create <prize> <duration> [options]`\n"
              "Create a new giveaway with advanced options",
        inline=False
    )
    
    embed.add_field(
        name="⏹️ End Giveaway",
        value="`w.giveaway end <giveaway_id>`\n"
              "Manually end an active giveaway",
        inline=False
    )
    
    embed.add_field(
        name="🎲 Reroll Winners",
        value="`w.giveaway reroll <giveaway_id> [new_winner_count]`\n"
              "Reroll winners for a completed giveaway",
        inline=False
    )
    
    embed.add_field(
        name="📋 List Giveaways",
        value="`w.giveaway list [all]`\n"
              "List active (or all) giveaways in this server",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Advanced Options",
        value="**--channel** `#channel` - Set channel\n"
              "**--winners** `number` - Number of winners (default: 1)\n"
              "**--required-roles** `@role1,@role2` - Required roles\n"
              "**--forbidden-roles** `@role1,@role2` - Forbidden roles\n"
              "**--winner-role** `@role` - Role given to winners\n"
              "**--min-messages** `number` - Minimum messages required\n"
              "**--min-age** `days` - Minimum account age in days\n"
              "**--bypass-roles** `@role1,@role2` - Roles that bypass requirements",
        inline=False
    )
    
    embed.add_field(
        name="⏰ Duration Format",
        value="`1m` = 1 minute | `1h` = 1 hour | `1d` = 1 day | `1w` = 1 week",
        inline=False
    )
    
    await ctx.send(embed=embed)

@giveaway_group.command(name='create', aliases=['c'])
@commands.has_permissions(manage_guild=True)
async def giveaway_create(ctx: commands.Context, prize: str, duration: str, *args):
    """Create an advanced giveaway with comprehensive options
    
    Examples:
    w.giveaway create "Discord Nitro" 1d --winners 2 --channel #giveaways
    w.giveaway create "Steam Game" 12h --required-roles @Members --min-age 7
    w.giveaway create "Special Prize" 3d --winner-role @Winner --bypass-roles @VIP
    """
    
    # Parse arguments
    channel = ctx.channel
    winners = 1
    required_roles = []
    forbidden_roles = []
    winner_role = None
    min_messages = 0
    min_account_age = 0
    bypass_roles = []
    description = None
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == '--channel' and i + 1 < len(args):
            try:
                channel_id = args[i + 1].replace('<#', '').replace('>', '')
                channel = ctx.guild.get_channel(int(channel_id))
                if not channel:
                    raise ValueError("Channel not found")
            except:
                return await ctx.send("❌ Invalid channel specified!")
            i += 2
        
        elif arg == '--winners' and i + 1 < len(args):
            try:
                winners = int(args[i + 1])
                if winners < 1:
                    raise ValueError("Winners must be at least 1")
            except:
                return await ctx.send("❌ Invalid number of winners specified!")
            i += 2
        
        elif arg == '--required-roles' and i + 1 < len(args):
            required_roles = parse_role_mentions(args[i + 1], ctx.guild)
            i += 2
        
        elif arg == '--forbidden-roles' and i + 1 < len(args):
            forbidden_roles = parse_role_mentions(args[i + 1], ctx.guild)
            i += 2
        
        elif arg == '--winner-role' and i + 1 < len(args):
            try:
                role_str = args[i + 1].replace('<@&', '').replace('>', '')
                winner_role = ctx.guild.get_role(int(role_str))
                if not winner_role:
                    winner_role = discord.utils.get(ctx.guild.roles, name=args[i + 1])
            except:
                return await ctx.send("❌ Invalid winner role specified!")
            i += 2
        
        elif arg == '--min-messages' and i + 1 < len(args):
            try:
                min_messages = int(args[i + 1])
                if min_messages < 0:
                    raise ValueError("Min messages cannot be negative")
            except:
                return await ctx.send("❌ Invalid minimum messages specified!")
            i += 2
        
        elif arg == '--min-age' and i + 1 < len(args):
            try:
                min_account_age = int(args[i + 1])
                if min_account_age < 0:
                    raise ValueError("Min age cannot be negative")
            except:
                return await ctx.send("❌ Invalid minimum account age specified!")
            i += 2
        
        elif arg == '--bypass-roles' and i + 1 < len(args):
            bypass_roles = parse_role_mentions(args[i + 1], ctx.guild)
            i += 2
        
        elif arg == '--description' and i + 1 < len(args):
            description = args[i + 1]
            i += 2
        
        else:
            i += 1
    
    # Create the giveaway
    result = await ctx.bot.giveaway_system.create_giveaway(
        ctx=ctx,
        prize=prize,
        duration=duration,
        winners=winners,
        channel=channel,
        required_roles=required_roles,
        forbidden_roles=forbidden_roles,
        winner_role=winner_role,
        min_messages=min_messages,
        min_account_age=min_account_age,
        bypass_roles=bypass_roles,
        description=description
    )
    
    # Send result
    embed = discord.Embed(
        title="🎉 Giveaway Creation",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    
    await ctx.send(embed=embed)

@giveaway_group.command(name='end', aliases=['stop'])
@commands.has_permissions(manage_guild=True)
async def giveaway_end(ctx: commands.Context, giveaway_id: int):
    """Manually end an active giveaway
    
    Example: w.giveaway end 123
    """
    
    result = await ctx.bot.giveaway_system.end_giveaway(giveaway_id, str(ctx.author.id))
    
    embed = discord.Embed(
        title="⏹️ End Giveaway",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    
    await ctx.send(embed=embed)

@giveaway_group.command(name='reroll', aliases=['r'])
@commands.has_permissions(manage_guild=True)
async def giveaway_reroll(ctx: commands.Context, giveaway_id: int, new_winner_count: Optional[int] = None):
    """Reroll winners for a completed giveaway
    
    Examples:
    w.giveaway reroll 123 - Reroll with same number of winners
    w.giveaway reroll 123 3 - Reroll with 3 new winners
    """
    
    result = await ctx.bot.giveaway_system.reroll_giveaway(
        giveaway_id, str(ctx.author.id), new_winner_count
    )
    
    embed = discord.Embed(
        title="🎲 Reroll Giveaway",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    
    await ctx.send(embed=embed)

@giveaway_group.command(name='list', aliases=['l'])
@commands.has_permissions(manage_guild=True)
async def giveaway_list(ctx: commands.Context, show_all: Optional[str] = None):
    """List giveaways in this server
    
    Examples:
    w.giveaway list - Show active giveaways
    w.giveaway list all - Show all giveaways
    """
    
    show_all_bool = show_all and show_all.lower() == 'all'
    result = await ctx.bot.giveaway_system.list_giveaways(str(ctx.guild.id), show_all_bool)
    
    if result['success']:
        await ctx.send(embed=result['embed'])
    else:
        embed = discord.Embed(
            title="📋 Giveaway List",
            description=result['message'],
            color=int(config.colors['error'].replace('#', ''), 16)
        )
        await ctx.send(embed=embed)

# Quick giveaway command for simple giveaways
@commands.hybrid_command(name='quickgiveaway', aliases=['qga'])
@commands.has_permissions(manage_guild=True)
@app_commands.describe(duration='Duration of the giveaway (e.g., 1h, 30m)', winners='Number of winners', prize='Prize description')
async def quick_giveaway(ctx: commands.Context, duration: str, winners: int, *, prize: str):
    """Create a simple giveaway quickly
    
    Example: w.quickgiveaway 1h 1 Discord Nitro
    """
    
    result = await ctx.bot.giveaway_system.create_giveaway(
        ctx=ctx,
        prize=prize,
        duration=duration,
        winners=winners
    )
    
    embed = discord.Embed(
        title="🎉 Quick Giveaway Created",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    
    await ctx.send(embed=embed)

# Admin Commands (Hybrid: both prefix and slash)
@commands.hybrid_command(name='adddrops')
@commands.has_permissions(manage_guild=True)
@app_commands.describe(channel='Channel to add to drop system (mention, ID, or name - optional, defaults to current)')
async def add_drop_channel(ctx: commands.Context, channel: str = None):
    """Add a channel to the wonder drop system (Admin only)"""
    if channel:
        target_channel = parse_channel_mention_or_id(channel, ctx.guild)
        if not target_channel:
            await send_command_error(ctx, "channel_not_found", "adddrops", f"Channel '{channel}' not found. Use mention, ID, or name.")
            return
    else:
        target_channel = ctx.channel
    
    result = await ctx.bot.drop_system.add_drop_channel(
        str(ctx.guild.id), str(target_channel.id), str(ctx.author.id)
    )
    
    embed = discord.Embed(
        title="✨ Wonder Drop Channel Configuration",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    embed.add_field(name="Channel", value=target_channel.mention, inline=True)
    embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='removedrops')
@commands.has_permissions(manage_guild=True)
@app_commands.describe(channel='Channel to remove from drop system (mention, ID, or name - optional, defaults to current)')
async def remove_drop_channel(ctx: commands.Context, channel: str = None):
    """Remove a channel from the wonder drop system (Admin only)"""
    if channel:
        target_channel = parse_channel_mention_or_id(channel, ctx.guild)
        if not target_channel:
            await send_command_error(ctx, "channel_not_found", "removedrops", f"Channel '{channel}' not found. Use mention, ID, or name.")
            return
    else:
        target_channel = ctx.channel
    
    result = await ctx.bot.drop_system.remove_drop_channel(
        str(ctx.guild.id), str(target_channel.id)
    )
    
    embed = discord.Embed(
        title="✨ Wonder Drop Channel Configuration",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    embed.add_field(name="Channel", value=target_channel.mention, inline=True)
    embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='forcedrop')
@commands.has_permissions(administrator=True)
@app_commands.describe(
    amount='Custom amount of WonderCoins (optional)',
    rarity='Custom rarity: common, rare, epic, legendary (optional)'
)
async def force_drop(ctx: commands.Context, amount: int = None, rarity: str = None):
    """Force a wonder drop in current channel (Admin only)"""
    result = await ctx.bot.drop_system.force_drop_in_channel(
        str(ctx.guild.id), str(ctx.channel.id), amount, rarity
    )
    
    embed = discord.Embed(
        title="🌟 Force Wonder Drop",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    if amount:
        embed.add_field(name="Custom Amount", value=f"{amount:,} {config.currency['symbol']}", inline=True)
    if rarity:
        embed.add_field(name="Custom Rarity", value=rarity.title(), inline=True)
    embed.set_footer(text="Wonderkind • Where Wonder Meets Chrome Dreams")
    await ctx.send(embed=embed)

@commands.hybrid_command(name='configdrops')
@commands.has_permissions(administrator=True)
@app_commands.describe(channel='Channel to configure (mention, ID, or name)', setting='Setting to change (rarity_mult, amount_mult, frequency, rarities)', value='New value for the setting')
async def configure_drops(ctx: commands.Context, channel: str, setting: str = None, value: str = None):
    """Configure advanced drop settings for a channel (Admin only)
    
    Settings:
    - rarity_mult: Multiply rare drop chances (0.5-3.0)
    - amount_mult: Multiply drop amounts (0.5-5.0)
    - frequency: Drop frequency modifier (0.1-10.0)
    - rarities: Allowed rarities (comma separated: common,rare,epic,legendary)
    """
    target_channel = parse_channel_mention_or_id(channel, ctx.guild)
    if not target_channel:
        await send_command_error(ctx, "channel_not_found", "configdrops", f"Channel '{channel}' not found. Use mention, ID, or name.")
        return
    
    if not setting:
        # Show current settings
        channels = await ctx.bot.drop_system.get_channel_list(str(ctx.guild.id))
        channel_config = next((ch for ch in channels if ch['id'] == str(target_channel.id)), None)
        
        embed = discord.Embed(
            title=f"🔮 Drop Settings for #{target_channel.name}",
            color=int(config.colors['info'].replace('#', ''), 16)
        )
        
        if channel_config:
            settings = channel_config['settings']
            embed.add_field(name="🎲 Rarity Multiplier", value=f"{settings.get('custom_rarity_multiplier', 1.0):.1f}x", inline=True)
            embed.add_field(name="💰 Amount Multiplier", value=f"{settings.get('custom_amount_multiplier', 1.0):.1f}x", inline=True)
            embed.add_field(name="⏰ Frequency Modifier", value=f"{settings.get('drop_frequency_modifier', 1.0):.1f}x", inline=True)
            embed.add_field(name="✨ Allowed Rarities", value=", ".join(settings.get('allowed_rarities', ['common', 'rare', 'epic', 'legendary'])), inline=False)
        else:
            embed.description = "Channel is not configured for drops!"
        
        await ctx.send(embed=embed)
        return
    
    # Update setting
    try:
        new_settings = {}
        
        if setting == "rarity_mult":
            val = float(value)
            if 0.5 <= val <= 3.0:
                new_settings['custom_rarity_multiplier'] = val
            else:
                raise ValueError("Rarity multiplier must be between 0.5 and 3.0")
        
        elif setting == "amount_mult":
            val = float(value)
            if 0.5 <= val <= 5.0:
                new_settings['custom_amount_multiplier'] = val
            else:
                raise ValueError("Amount multiplier must be between 0.5 and 5.0")
        
        elif setting == "frequency":
            val = float(value)
            if 0.1 <= val <= 10.0:
                new_settings['drop_frequency_modifier'] = val
            else:
                raise ValueError("Frequency modifier must be between 0.1 and 10.0")
        
        elif setting == "rarities":
            valid_rarities = ['common', 'rare', 'epic', 'legendary']
            rarities = [r.strip().lower() for r in value.split(',')]
            if all(r in valid_rarities for r in rarities) and rarities:
                new_settings['allowed_rarities'] = rarities
            else:
                raise ValueError("Invalid rarities. Use: common,rare,epic,legendary")
        
        else:
            raise ValueError("Invalid setting. Use: rarity_mult, amount_mult, frequency, rarities")
        
        result = await ctx.bot.drop_system.configure_channel_drops(
            str(ctx.guild.id), str(target_channel.id), new_settings
        )
        
        embed = discord.Embed(
            title="⚙️ Drop Configuration",
            description=result['message'],
            color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
        )
        
    except ValueError as e:
        embed = discord.Embed(
            title="❌ Configuration Error",
            description=str(e),
            color=int(config.colors['error'].replace('#', ''), 16)
        )
    
    await ctx.send(embed=embed)

@commands.hybrid_command(name='dropchannels')
@commands.has_permissions(manage_guild=True)
async def list_drop_channels(ctx: commands.Context):
    """List all configured drop channels (Admin only)"""
    channels = await ctx.bot.drop_system.get_channel_list(str(ctx.guild.id))
    
    embed = discord.Embed(
        title="🌌 Wonderkind Drop Channels",
        color=int(config.colors['info'].replace('#', ''), 16)
    )
    
    if not channels:
        embed.description = "No drop channels configured! Use `w.adddrops #channel` to add one."
    else:
        embed.description = f"**{len(channels)}** channels configured for mystical drops:\n"
        
        for channel in channels:
            settings = channel['settings']
            mult_info = []
            
            if settings.get('custom_rarity_multiplier', 1.0) != 1.0:
                mult_info.append(f"Rarity: {settings['custom_rarity_multiplier']:.1f}x")
            
            if settings.get('custom_amount_multiplier', 1.0) != 1.0:
                mult_info.append(f"Amount: {settings['custom_amount_multiplier']:.1f}x")
            
            if settings.get('drop_frequency_modifier', 1.0) != 1.0:
                mult_info.append(f"Frequency: {settings['drop_frequency_modifier']:.1f}x")
            
            extras = f" ({', '.join(mult_info)})" if mult_info else ""
            embed.description += f"\n🔮 {channel['mention']}{extras}"
    
    await ctx.send(embed=embed)

# Introduction Card Commands (Slash only)
@app_commands.command(name='intro-create', description='Create your introduction card')
async def intro_create(interaction: discord.Interaction):
    """Create an introduction card"""
    try:
        # Check if user already has a card
        existing_card = await database.get_intro_card(str(interaction.user.id))
        
        if existing_card:
            embed = discord.Embed(
                title="❌ Card Already Exists",
                description="You already have an introduction card! Use `/intro-edit` to modify it or `/intro-view` to see it.",
                color=0xF59E0B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Show modal for card creation
        modal = IntroCardModal()
        await interaction.response.send_modal(modal)
        
    except Exception as e:
        logging.error(f"Error creating intro card: {e}")
        await interaction.response.send_message("❌ An error occurred while creating your card.", ephemeral=True)

@app_commands.command(name='intro-edit', description='Edit your introduction card')
async def intro_edit(interaction: discord.Interaction):
    """Edit an existing introduction card"""
    try:
        # Get existing card
        existing_card = await database.get_intro_card(str(interaction.user.id))
        
        if not existing_card:
            embed = discord.Embed(
                title="❌ No Card Found",
                description="You don't have an introduction card yet! Use `/intro-create` to make one.",
                color=0xF59E0B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Show modal for card editing
        modal = IntroCardModal(existing_card)
        await interaction.response.send_modal(modal)
        
    except Exception as e:
        logging.error(f"Error editing intro card: {e}")
        await interaction.response.send_message("❌ An error occurred while editing your card.", ephemeral=True)

@app_commands.command(name='intro-view', description='View an introduction card')
@app_commands.describe(user='The user whose card you want to view (optional - defaults to yourself)')
async def intro_view(interaction: discord.Interaction, user: discord.Member = None):
    """View an introduction card"""
    try:
        target_user = user or interaction.user
        
        # Get card data
        card_data = await database.get_intro_card(str(target_user.id))
        
        if not card_data:
            if target_user == interaction.user:
                embed = discord.Embed(
                    title="❌ No Card Found",
                    description="You don't have an introduction card yet! Use `/intro-create` to make one.",
                    color=0xF59E0B
                )
            else:
                embed = discord.Embed(
                    title="❌ No Card Found",
                    description=f"{target_user.display_name} doesn't have an introduction card yet.",
                    color=0xF59E0B
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if card is public or if user is viewing their own card
        if not card_data.get('is_public', True) and target_user != interaction.user:
            embed = discord.Embed(
                title="🔒 Private Card",
                description=f"{target_user.display_name}'s introduction card is set to private.",
                color=0xF59E0B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Generate card image
        try:
            card_image = await interaction.client.intro_card_system.generate_card_image(target_user, card_data)
            
            # Create embed with card info
            embed = await interaction.client.intro_card_system.create_card_embed(card_data, target_user)
            
            # Create interactive view
            view = IntroCardView(card_data, str(interaction.user.id))
            
            # Send card with image and interactive buttons
            file = discord.File(io.BytesIO(card_image), filename=f"intro_card_{target_user.id}.png")
            embed.set_image(url=f"attachment://intro_card_{target_user.id}.png")
            
            await interaction.followup.send(embed=embed, file=file, view=view)
            
        except Exception as e:
            logging.error(f"Error generating card image: {e}")
            # Fallback to text-only embed
            embed = await interaction.client.intro_card_system.create_card_embed(card_data, target_user)
            view = IntroCardView(card_data, str(interaction.user.id))
            await interaction.followup.send(embed=embed, view=view)
        
    except Exception as e:
        logging.error(f"Error viewing intro card: {e}")
        await interaction.response.send_message("❌ An error occurred while viewing the card.", ephemeral=True)





@app_commands.command(name='intro-privacy', description='Toggle your introduction card privacy')
async def intro_privacy(interaction: discord.Interaction):
    """Toggle introduction card privacy"""
    try:
        # Get existing card
        card_data = await database.get_intro_card(str(interaction.user.id))
        
        if not card_data:
            embed = discord.Embed(
                title="❌ No Card Found",
                description="You don't have an introduction card yet! Use `/intro-create` to make one.",
                color=0xF59E0B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Toggle privacy
        current_privacy = card_data.get('is_public', True)
        new_privacy = not current_privacy
        
        card_data['is_public'] = new_privacy
        await database.save_intro_card(card_data)
        
        privacy_status = "Public" if new_privacy else "Private"
        privacy_emoji = "🌐" if new_privacy else "🔒"
        
        embed = discord.Embed(
            title=f"{privacy_emoji} Privacy Updated",
            description=f"Your introduction card is now **{privacy_status}**.",
            color=0x10B981 if new_privacy else 0xF59E0B
        )
        
        if new_privacy:
            embed.add_field(name="Public Card", value="✅ Other members can view your card\n✅ Appears in server gallery\n✅ Can receive likes and interactions", inline=False)
        else:
            embed.add_field(name="Private Card", value="🔒 Only you can view your card\n🔒 Hidden from server gallery\n🔒 No public interactions", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logging.error(f"Error toggling intro card privacy: {e}")
        await interaction.response.send_message("❌ An error occurred while updating privacy settings.", ephemeral=True)

@app_commands.command(name='intro-background', description='🔒 Bot Owner: Set custom background image for introduction cards')
@app_commands.describe(image='Upload a background image (JPG/PNG)')
async def intro_background(interaction: discord.Interaction, image: discord.Attachment = None):
    """Bot owner only: Set custom background image for introduction cards"""
    try:
        # Check if user is bot owner
        app_info = await interaction.client.application_info()
        if interaction.user.id != app_info.owner.id:
            embed = discord.Embed(
                title="🔒 Owner Only Command",
                description="This command can only be used by the bot owner.",
                color=0xF59E0B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Get current server settings
        server_settings = await database.get_server_settings(str(interaction.guild.id))
        if not server_settings:
            server_settings = {
                'guild_id': str(interaction.guild.id),
                'intro_card_theme': '#7C3AED',
                'intro_card_style': 'gradient'
            }
        
        if image is None:
            # Show current background and options to remove
            class BackgroundManagementView(discord.ui.View):
                def __init__(self, settings):
                    super().__init__(timeout=300)
                    self.settings = settings
                
                @discord.ui.button(label="🗑️ Remove Custom Background", style=discord.ButtonStyle.danger)
                async def remove_background(self, interaction: discord.Interaction, button: discord.ui.Button):
                    """Remove custom background"""
                    self.settings['intro_card_background_url'] = None
                    await database.save_server_settings(self.settings)
                    
                    embed = discord.Embed(
                        title="✅ Background Removed",
                        description="Custom background has been removed. Cards will now use the default gradient background.",
                        color=0x10B981
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
            
            current_bg = server_settings.get('intro_card_background_url')
            embed = discord.Embed(
                title="🖼️ Introduction Card Background Management",
                description="Manage the background image for introduction cards in this server.",
                color=0x7C3AED
            )
            
            if current_bg:
                embed.add_field(
                    name="Current Background", 
                    value="✅ Custom background image is set", 
                    inline=False
                )
                embed.set_image(url=current_bg)
                view = BackgroundManagementView(server_settings)
            else:
                embed.add_field(
                    name="Current Background", 
                    value="🌈 Default gradient background", 
                    inline=False
                )
                view = None
            
            embed.add_field(
                name="How to Set Background",
                value="Use `/intro-background` with an image attachment to set a custom background.\n"
                      "Supported formats: JPG, PNG\n"
                      "Recommended size: 800x600 pixels",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            return
        
        # Validate image
        if not image.content_type or not image.content_type.startswith('image/'):
            embed = discord.Embed(
                title="❌ Invalid File Type",
                description="Please upload a valid image file (JPG or PNG).",
                color=0xF59E0B
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Check file size (max 8MB)
        if image.size > 8 * 1024 * 1024:
            embed = discord.Embed(
                title="❌ File Too Large",
                description="Image must be smaller than 8MB.",
                color=0xF59E0B
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Save the image URL to server settings
        server_settings['intro_card_background_url'] = image.url
        success = await database.save_server_settings(server_settings)
        
        if success:
            embed = discord.Embed(
                title="✅ Background Updated Successfully",
                description="The custom background image has been set for introduction cards.",
                color=0x10B981
            )
            embed.add_field(
                name="New Background Preview",
                value="All new and updated introduction cards will use this background.",
                inline=False
            )
            embed.set_image(url=image.url)
            
            # Add button to test the background
            class TestView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                
                @discord.ui.button(label="🎨 Preview on Sample Card", style=discord.ButtonStyle.primary)
                async def preview_background(self, interaction: discord.Interaction, button: discord.ui.Button):
                    """Generate a sample card with the new background"""
                    await interaction.response.defer(ephemeral=True)
                    
                    try:
                        # Create sample card data
                        sample_data = {
                            'name': 'Sample User',
                            'age': 25,
                            'location': 'Wonderland',
                            'bio': 'This is a sample introduction card to preview the new background!',
                            'hobbies': 'Testing, Previewing, and Being Awesome',
                            'favorite_color': '#7C3AED',
                            'background_style': 'gradient'
                        }
                        
                        # Generate preview card
                        card_image = await interaction.client.intro_card_system.generate_card_image(
                            interaction.user, sample_data
                        )
                        
                        file = discord.File(io.BytesIO(card_image), filename="background_preview.png")
                        embed = discord.Embed(
                            title="🎨 Background Preview",
                            description="Here's how the new background looks on an introduction card:",
                            color=0x7C3AED
                        )
                        embed.set_image(url="attachment://background_preview.png")
                        
                        await interaction.followup.send(embed=embed, file=file, ephemeral=True)
                        
                    except Exception as e:
                        logging.error(f"Error generating background preview: {e}")
                        await interaction.followup.send("❌ Error generating preview. The background is still saved successfully.", ephemeral=True)
            
            view = TestView()
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="There was an error saving the background image. Please try again.",
                color=0xEF4444
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logging.error(f"Error setting intro background: {e}")
        await interaction.followup.send("❌ An error occurred while setting the background.", ephemeral=True)

@app_commands.command(name='intro-delete', description='Delete your introduction card')
async def intro_delete(interaction: discord.Interaction):
    """Delete introduction card"""
    try:
        # Get existing card
        card_data = await database.get_intro_card(str(interaction.user.id))
        
        if not card_data:
            embed = discord.Embed(
                title="❌ No Card Found",
                description="You don't have an introduction card to delete.",
                color=0xF59E0B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Confirmation view
        class ConfirmDeleteView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                
            @discord.ui.button(label="✅ Yes, Delete", style=discord.ButtonStyle.danger)
            async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
                success = await database.delete_intro_card(str(interaction.user.id))
                if success:
                    embed = discord.Embed(
                        title="✅ Card Deleted",
                        description="Your introduction card has been successfully deleted.",
                        color=0x10B981
                    )
                else:
                    embed = discord.Embed(
                        title="❌ Error",
                        description="There was an error deleting your card. Please try again.",
                        color=0xEF4444
                    )
                await interaction.response.edit_message(embed=embed, view=None)
                
            @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
            async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
                embed = discord.Embed(
                    title="❌ Cancelled",
                    description="Card deletion cancelled.",
                    color=0x6B7280
                )
                await interaction.response.edit_message(embed=embed, view=None)
        
        embed = discord.Embed(
            title="⚠️ Confirm Deletion",
            description="Are you sure you want to delete your introduction card?\n**This action cannot be undone!**",
            color=0xF59E0B
        )
        view = ConfirmDeleteView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    except Exception as e:
        logging.error(f"Error deleting intro card: {e}")
        await interaction.response.send_message("❌ An error occurred while deleting your card.", ephemeral=True)

# Help Command (Hybrid)
@commands.hybrid_command(name='help')
async def help_command(ctx: commands.Context):
    """Show comprehensive wonderkind help information"""
    embed = await get_help_embed_for_user(ctx.author, ctx.bot)
    await ctx.send(embed=embed)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def is_admin(user: discord.Member) -> bool:
    """Check if user has admin permissions"""
    return user.guild_permissions.administrator or user.guild_permissions.manage_guild

def is_owner(user: discord.Member, bot: commands.Bot) -> bool:
    """Check if user is bot owner"""
    return user.id == bot.owner_id

def parse_user_mention_or_id(user_input: str, guild: discord.Guild) -> discord.Member:
    """Parse user from mention, ID, or username"""
    if not user_input:
        return None
    
    # Try mention format <@!123> or <@123>
    if user_input.startswith('<@') and user_input.endswith('>'):
        user_id = user_input.replace('<@!', '').replace('<@', '').replace('>', '')
        try:
            return guild.get_member(int(user_id))
        except ValueError:
            return None
    
    # Try direct ID
    try:
        user_id = int(user_input)
        return guild.get_member(user_id)
    except ValueError:
        pass
    
    # Try username/display name
    member = discord.utils.get(guild.members, name=user_input)
    if not member:
        member = discord.utils.get(guild.members, display_name=user_input)
    
    return member

def parse_role_mention_or_id(role_input: str, guild: discord.Guild) -> discord.Role:
    """Parse role from mention, ID, or name"""
    if not role_input:
        return None
    
    # Try mention format <@&123>
    if role_input.startswith('<@&') and role_input.endswith('>'):
        role_id = role_input.replace('<@&', '').replace('>', '')
        try:
            return guild.get_role(int(role_id))
        except ValueError:
            return None
    
    # Try direct ID
    try:
        role_id = int(role_input)
        return guild.get_role(role_id)
    except ValueError:
        pass
    
    # Try role name
    return discord.utils.get(guild.roles, name=role_input)

def parse_channel_mention_or_id(channel_input: str, guild: discord.Guild) -> discord.TextChannel:
    """Parse channel from mention, ID, or name"""
    if not channel_input:
        return None
    
    # Try mention format <#123>
    if channel_input.startswith('<#') and channel_input.endswith('>'):
        channel_id = channel_input.replace('<#', '').replace('>', '')
        try:
            return guild.get_channel(int(channel_id))
        except ValueError:
            return None
    
    # Try direct ID
    try:
        channel_id = int(channel_input)
        return guild.get_channel(channel_id)
    except ValueError:
        pass
    
    # Try channel name
    return discord.utils.get(guild.text_channels, name=channel_input)

def get_command_help(command_name: str) -> str:
    """Get detailed help information for a specific command"""
    command_info = {
        'balance': {
            'usage': '`w.balance [@user]` or `/balance [user]`',
            'description': 'Check your balance or another user\'s balance',
            'parameters': '• `user` (optional): User to check balance for'
        },
        'daily': {
            'usage': '`w.daily` or `/daily`',
            'description': 'Claim your daily WonderCoins reward',
            'parameters': '• No parameters required'
        },
        'work': {
            'usage': '`w.work` or `/work`',
            'description': 'Work to earn WonderCoins (1 hour cooldown)',
            'parameters': '• No parameters required'
        },
        'shop': {
            'usage': '`w.shop [category] [page]` or `/shop [category] [page]`',
            'description': 'Browse the shop items',
            'parameters': '• `category` (optional): Shop category to view (default: all)\n• `page` (optional): Page number (default: 1)'
        },
        'buy': {
            'usage': '`w.buy <item_id> [quantity]` or `/buy <item_id> [quantity]`',
            'description': 'Purchase an item from the shop',
            'parameters': '• `item_id` (required): ID of the item to buy\n• `quantity` (optional): Number of items to buy (default: 1)'
        },
        'inventory': {
            'usage': '`w.inventory [page]` or `/inventory [page]`',
            'description': 'View your inventory',
            'parameters': '• `page` (optional): Page number to view (default: 1)'
        },
        'use': {
            'usage': '`w.use <item_id>` or `/use <item_id>`',
            'description': 'Use an item from your inventory',
            'parameters': '• `item_id` (required): ID of the item to use'
        },
        'rank': {
            'usage': '`w.rank [@user]` or `/rank [user]`',
            'description': 'View your or someone\'s rank and XP',
            'parameters': '• `user` (optional): User to check rank for'
        },
        'coinflip': {
            'usage': '`w.coinflip <amount> <choice>` or `/coinflip <amount> <choice>`',
            'description': 'Flip a coin and bet WonderCoins',
            'parameters': '• `amount` (required): Amount to bet (10-1000 coins)\n• `choice` (required): h/heads or t/tails'
        },
        'dice': {
            'usage': '`w.dice <amount> <target>` or `/dice <amount> <target>`',
            'description': 'Roll dice and bet WonderCoins',
            'parameters': '• `amount` (required): Amount to bet (10-500 coins)\n• `target` (required): Target number (1-6)'
        },
        'slots': {
            'usage': '`w.slots <amount>` or `/slots <amount>`',
            'description': 'Play slot machine with WonderCoins',
            'parameters': '• `amount` (required): Amount to bet (20-200 coins)'
        },
        'gamestats': {
            'usage': '`w.gamestats [@user]` or `/gamestats [user]`',
            'description': 'View gambling statistics',
            'parameters': '• `user` (optional): User to check stats for'
        },
        'quickgiveaway': {
            'usage': '`w.quickgiveaway <duration> <winners> <prize>` or `/quickgiveaway <duration> <winners> <prize>`',
            'description': 'Create a quick giveaway (Admin only)',
            'parameters': '• `duration` (required): Duration (e.g., 1h, 30m, 2d)\n• `winners` (required): Number of winners\n• `prize` (required): Prize description'
        },
        'adddrops': {
            'usage': '`w.adddrops [#channel]` or `/adddrops [channel]`',
            'description': 'Add a channel to the drop system (Admin only)',
            'parameters': '• `channel` (optional): Channel to add (defaults to current)'
        },
        'removedrops': {
            'usage': '`w.removedrops [#channel]` or `/removedrops [channel]`',
            'description': 'Remove a channel from the drop system (Admin only)',
            'parameters': '• `channel` (optional): Channel to remove (defaults to current)'
        },
        'forcedrop': {
            'usage': '`w.forcedrop [#channel]` or `/forcedrop [channel]`',
            'description': 'Force a WonderCoins drop (Admin only)',
            'parameters': '• `channel` (optional): Channel to drop in (defaults to current)'
        },
        'configdrops': {
            'usage': '`w.configdrops <#channel> [setting] [value]` or `/configdrops <channel> [setting] [value]`',
            'description': 'Configure drop settings for a channel (Admin only)',
            'parameters': '• `channel` (required): Channel to configure\n• `setting` (optional): rarity_mult, amount_mult, frequency, rarities\n• `value` (optional): New value for the setting'
        },
        'dropchannels': {
            'usage': '`w.dropchannels` or `/dropchannels`',
            'description': 'List all configured drop channels (Admin only)',
            'parameters': '• No parameters required'
        },
        'roles': {
            'usage': '`w.roles [category]` or `/roles [category]`',
            'description': 'View level roles and requirements for each category',
            'parameters': '• `category` (optional): text, voice, role, or overall'
        },
        'prestige': {
            'usage': '`w.prestige` or `/prestige`',
            'description': 'View prestige system information and requirements',
            'parameters': '• No parameters required'
        },
        'toggle-category': {
            'usage': '`w.toggle-category <category> <enabled>` or `/toggle-category <category> <enabled>`',
            'description': 'Enable or disable a leveling category (Admin only)',
            'parameters': '• `category` (required): text, voice, role, or overall\n• `enabled` (required): true or false'
        },
        'set-user-xp': {
            'usage': '`w.set-user-xp <user> <category> <amount>` or `/set-user-xp <user> <category> <amount>`',
            'description': 'Set user\'s XP in a specific category (Admin only)',
            'parameters': '• `user` (required): User mention, ID, or username\n• `category` (required): text, voice, role, or overall\n• `amount` (required): XP amount to set'
        },
        'add-user-xp': {
            'usage': '`w.add-user-xp <user> <category> <amount>` or `/add-user-xp <user> <category> <amount>`',
            'description': 'Add XP to user in a specific category (Admin only)',
            'parameters': '• `user` (required): User mention, ID, or username\n• `category` (required): text, voice, role, or overall\n• `amount` (required): XP amount to add (can be negative)'
        },
        'reset-user-xp': {
            'usage': '`w.reset-user-xp <user> [category]` or `/reset-user-xp <user> [category]`',
            'description': 'Reset user\'s XP in specific category or all categories (Admin only)',
            'parameters': '• `user` (required): User mention, ID, or username\n• `category` (optional): text, voice, role, overall, or all (default: all)'
        },
        'set-user-currency': {
            'usage': '`w.set-user-currency <user> <amount>` or `/set-user-currency <user> <amount>`',
            'description': 'Set user\'s currency balance (Admin only)',
            'parameters': '• `user` (required): User mention, ID, or username\n• `amount` (required): Currency amount to set'
        },
        'add-user-currency': {
            'usage': '`w.add-user-currency <user> <amount>` or `/add-user-currency <user> <amount>`',
            'description': 'Add currency to user\'s balance (Admin only)',
            'parameters': '• `user` (required): User mention, ID, or username\n• `amount` (required): Currency amount to add (can be negative)'
        },
        'help': {
            'usage': '`w.help` or `/help`',
            'description': 'Show this help information',
            'parameters': '• No parameters required'
        }
    }
    
    return command_info.get(command_name, {
        'usage': f'`w.{command_name}` or `/{command_name}`',
        'description': 'Command information not available',
        'parameters': '• Check command documentation'
    })

async def send_command_error(ctx: commands.Context, error_type: str, command_name: str, additional_info: str = ""):
    """Send a detailed error message for command failures"""
    cmd_info = get_command_help(command_name)
    
    embed = discord.Embed(
        title="❌ Command Error",
        color=int(config.colors['error'].replace('#', ''), 16)
    )
    
    if error_type == "missing_argument":
        embed.description = f"**Missing required argument for `{command_name}` command**"
    elif error_type == "bad_argument":
        embed.description = f"**Invalid argument provided for `{command_name}` command**"
    elif error_type == "cooldown":
        embed.description = f"**Command `{command_name}` is on cooldown**"
    elif error_type == "permission":
        embed.description = f"**You don't have permission to use `{command_name}` command**"
    elif error_type == "bot_permission":
        embed.description = f"**Bot missing permissions for `{command_name}` command**"
    elif error_type == "no_dm":
        embed.description = f"**Command `{command_name}` cannot be used in DMs**"
    elif error_type == "channel_not_found":
        embed.description = f"**Channel not found for `{command_name}` command**"
    elif error_type == "member_not_found":
        embed.description = f"**User not found for `{command_name}` command**"
    elif error_type == "role_not_found":
        embed.description = f"**Role not found for `{command_name}` command**"
    elif error_type == "unexpected":
        embed.description = f"**Unexpected error in `{command_name}` command**"
    else:
        embed.description = f"**Error executing `{command_name}` command**"
    
    if additional_info:
        embed.description += f"\n{additional_info}"
    
    embed.add_field(
        name="📝 Usage",
        value=cmd_info['usage'],
        inline=False
    )
    
    embed.add_field(
        name="📋 Description", 
        value=cmd_info['description'],
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Parameters",
        value=cmd_info['parameters'],
        inline=False
    )
    
    embed.set_footer(text="💡 Use /help for a complete list of commands")
    
    await ctx.send(embed=embed)

async def get_help_embed_for_user(user: discord.Member, bot: commands.Bot) -> discord.Embed:
    """Get appropriate help embed based on user permissions"""
    is_user_admin = is_admin(user)
    is_user_owner = is_owner(user, bot)
    
    embed = discord.Embed(
        title=f"🌌 {config.branding['name']} - Wonder Help",
        description=f"*Where Wonder Meets Chrome Dreams*",
        color=int(config.colors['primary'].replace('#', ''), 16)
    )
    
    embed.add_field(
        name="💰 Wonder Economy",
        value="**Balance & Rewards:**\n"
              "`/balance` `w.balance` - Check WonderCoins\n"
              "`/daily` `w.daily` - Daily reward (24h cooldown)\n"
              "`/work` `w.work` - Work for coins (1h cooldown)\n"
              "`/leaderboard` `w.leaderboard` - Top dreamers",
        inline=True
    )
    
    embed.add_field(
        name="🎮 Wonder Games",
        value="**Animated Gaming:**\n"
              "`/coinflip` `w.coinflip` - Coin flip betting\n"
              "`/dice` `w.dice` - Dice roll betting\n"
              "`/slots` `w.slots` - Slot machine\n"
              "`w.gamestats` - View gambling stats",
        inline=True
    )
    
    embed.add_field(
        name="🏪 Shop & Inventory",
        value="**Items & Trading:**\n"
              "`w.shop [category]` - Browse shop\n"
              "`w.buy <item> [quantity]` - Purchase items\n"
              "`w.inventory` - View your items\n"
              "`w.use <item>` - Use consumables",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Comprehensive Leveling System",
        value="**4-Category Progression with Roles:**\n"
              "`w.rank [@user]` - View comprehensive rank\n"
              "`w.roles [category]` - View level roles & perks\n"
              "`w.prestige` - View prestige system info\n"
              "**Categories:** Text, Voice, Community, Overall",
        inline=True
    )
    
    embed.add_field(
        name="🎨 Introduction Cards",
        value="**Personal Profiles:**\n"
              "`/intro-create` - Create your card\n"
              "`/intro-view [@user]` - View cards\n"
              "`/intro-edit` - Edit your info\n"
              "`/intro-privacy` - Toggle privacy\n"
              "`/intro-delete` - Delete your card",
        inline=True
    )
    
    giveaway_commands = "**Community Events:**\n" \
                       "`w.giveaway create` - Advanced giveaway\n" \
                       "`w.giveaway list` - View active\n"
    
    if is_user_admin:
        giveaway_commands += "`w.quickgiveaway` - Quick setup (Admin)\n" \
                           "`w.giveaway end/reroll` - Manage (Admin)"
    
    embed.add_field(
        name="🎉 Giveaway System",
        value=giveaway_commands,
        inline=True
    )
    
    embed.add_field(
        name="🪙 WonderCoins Drops",
        value="**Automatic Drop System:**\n"
              "• **Random drops** every 30min-3h\n"
              "• **4 rarities:** Common, Rare, Epic, Legendary\n"
              "• **3 collection types:** Standard, Quick, Lucky\n"
              "• **Role bonuses:** Boosters +25%, Premium +50%",
        inline=True
    )
    
    # Add admin commands only for admins
    if is_user_admin:
        embed.add_field(
            name="🛡️ Admin Drop Commands",
            value="**Drop System Management:**\n"
                  "`/adddrops` `w.adddrops` - Add drop channel\n"
                  "`/removedrops` `w.removedrops` - Remove channel\n"
                  "`w.dropchannels` - List channels\n"
                  "`w.configdrops` - Configure settings\n"
                  "`/forcedrop` `w.forcedrop` - Force drop",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Admin Leveling Commands",
            value="**Leveling System Management:**\n"
                  "`w.toggle-category` - Enable/disable categories\n"
                  "`w.set-user-xp` - Set user XP\n"
                  "`w.add-user-xp` - Add/remove user XP\n"
                  "`w.reset-user-xp` - Reset user XP\n"
                  "`w.set-user-currency` - Set user balance\n"
                  "`w.add-user-currency` - Add/remove currency",
            inline=True
        )
    
    # Add owner commands only for owner
    if is_user_owner:
        embed.add_field(
            name="🔒 Owner Commands",
            value="**Bot Owner Only:**\n"
                  "`/intro-background` - Custom card backgrounds\n"
                  "Upload images to customize server cards",
            inline=True
        )
    
    embed.add_field(
        name="✨ Command Support",
        value="🌟 **Hybrid Commands:** Use either `/command` (slash) or `w.command` (prefix)\n"
              "🔮 **Slash Benefits:** Autocomplete, parameter help, mobile-friendly\n"
              "💫 **Prefix Benefits:** Quick typing, familiar Discord experience",
        inline=False
    )
    
    embed.add_field(
        name="🎁 Role Benefits",
        value="**Server Boosters:** 1.5x XP, +50% daily/work, +25% drops\n"
              "**Premium Members:** 1.75x XP, +100% daily/work, +50% drops\n"
              "**Weighted Giveaways:** Premium 3x, Boosters 2x, Regular 1x odds",
        inline=False
    )
    
    embed.set_footer(text=f"Wonder Bot v{config.branding['version']} • Where Wonder Meets Chrome Dreams • Use /help for this menu")
    embed.timestamp = datetime.now()
    
    return embed

async def main():
    """Main function to run the bot"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logging.error("DISCORD_TOKEN not found in environment variables!")
        return
    
    # Create and run bot
    bot = WonderBot()
    
    # Add commands to bot
    # Economy commands
    bot.add_command(balance)
    bot.add_command(daily)
    bot.add_command(work)
    bot.add_command(leaderboard)
    
    # Game commands
    bot.add_command(coinflip)
    bot.add_command(dice)
    bot.add_command(slots)
    bot.add_command(gamestats)
    
    # Shop commands
    bot.add_command(shop)
    bot.add_command(buy)
    bot.add_command(inventory)
    bot.add_command(use_item)
    
    # Leveling commands
    bot.add_command(rank)
    bot.add_command(level_roles)
    bot.add_command(prestige_info)
    
    # Admin leveling management commands
    bot.add_command(toggle_category)
    bot.add_command(set_user_xp)
    bot.add_command(add_user_xp)
    bot.add_command(reset_user_xp)
    bot.add_command(set_user_currency)
    bot.add_command(add_user_currency)
    
    # Admin commands
    bot.add_command(giveaway_group)
    bot.add_command(quick_giveaway)
    bot.add_command(add_drop_channel)
    bot.add_command(remove_drop_channel)
    bot.add_command(force_drop)
    
    # Help command
    bot.add_command(help_command)
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logging.info("Bot shutdown requested")
    except Exception as e:
        logging.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())