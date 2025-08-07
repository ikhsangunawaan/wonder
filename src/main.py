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
        
        super().__init__(
            command_prefix=config.prefix,
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
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"❌ Command is on cooldown. Try again in {error.retry_after:.2f} seconds")
            return
        
        logging.error(f"Command error: {error}")
        await ctx.send("❌ An error occurred while executing the command!")
    
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
@app_commands.describe(user='User to check balance for (optional)')
async def balance(ctx: commands.Context, user: discord.Member = None):
    """Check your balance or another user's balance"""
    target_user = user or ctx.author
    
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

@commands.command(name='gamestats')
async def gamestats(ctx: commands.Context, user: discord.Member = None):
    """View gambling statistics"""
    target_user = user or ctx.author
    embed = await ctx.bot.games_system.create_gambling_stats_embed(str(target_user.id), target_user.display_name)
    await ctx.send(embed=embed)

# Shop Commands
@commands.command(name='shop')
async def shop(ctx: commands.Context, category: str = 'all', page: int = 1):
    """View the shop"""
    embed = await ctx.bot.shop_system.get_shop_embed(category, page)
    await ctx.send(embed=embed)

@commands.command(name='buy')
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

@commands.command(name='inventory', aliases=['inv'])
async def inventory(ctx: commands.Context, page: int = 1):
    """View your inventory"""
    embed = await ctx.bot.shop_system.get_inventory_embed(str(ctx.author.id), page)
    await ctx.send(embed=embed)

@commands.command(name='use')
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
@commands.command(name='rank')
async def rank(ctx: commands.Context, user: discord.Member = None):
    """View your or someone's rank"""
    target_user = user or ctx.author
    rank_info = await ctx.bot.leveling_system.get_user_rank(str(target_user.id))
    
    if not rank_info:
        await ctx.send(f"❌ No level data found for {target_user.display_name}")
        return
    
    embed = discord.Embed(
        title=f"📊 Rank - {target_user.display_name}",
        color=int(config.colors['primary'].replace('#', ''), 16)
    )
    
    embed.add_field(
        name="📈 Level",
        value=f"**{rank_info['level']}**",
        inline=True
    )
    
    embed.add_field(
        name="✨ XP",
        value=f"{rank_info['xp']:,}",
        inline=True
    )
    
    if rank_info['xp_needed'] > 0:
        embed.add_field(
            name="🎯 Next Level",
            value=f"{rank_info['xp_needed']:,} XP needed",
            inline=True
        )
    else:
        embed.add_field(
            name="🏆 Max Level",
            value="Level cap reached!",
            inline=True
        )
    
    embed.add_field(
        name="💬 Messages",
        value=f"{rank_info['total_messages']:,}",
        inline=True
    )
    
    embed.set_thumbnail(url=target_user.display_avatar.url)
    
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
@commands.command(name='quickgiveaway', aliases=['qga'])
@commands.has_permissions(manage_guild=True)
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
@app_commands.describe(channel='Channel to add to drop system (optional, defaults to current)')
async def add_drop_channel(ctx: commands.Context, channel: discord.TextChannel = None):
    """Add a channel to the wonder drop system (Admin only)"""
    target_channel = channel or ctx.channel
    
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
@app_commands.describe(channel='Channel to remove from drop system (optional, defaults to current)')
async def remove_drop_channel(ctx: commands.Context, channel: discord.TextChannel = None):
    """Remove a channel from the wonder drop system (Admin only)"""
    target_channel = channel or ctx.channel
    
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

@commands.command(name='configdrops')
@commands.has_permissions(administrator=True)
async def configure_drops(ctx: commands.Context, channel: discord.TextChannel, setting: str = None, value: str = None):
    """Configure advanced drop settings for a channel (Admin only)
    
    Settings:
    - rarity_mult: Multiply rare drop chances (0.5-3.0)
    - amount_mult: Multiply drop amounts (0.5-5.0)
    - frequency: Drop frequency modifier (0.1-10.0)
    - rarities: Allowed rarities (comma separated: common,rare,epic,legendary)
    """
    if not setting:
        # Show current settings
        channels = await ctx.bot.drop_system.get_channel_list(str(ctx.guild.id))
        target_channel = next((ch for ch in channels if ch['id'] == str(channel.id)), None)
        
        embed = discord.Embed(
            title=f"🔮 Drop Settings for #{channel.name}",
            color=int(config.colors['info'].replace('#', ''), 16)
        )
        
        if target_channel:
            settings = target_channel['settings']
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
            str(ctx.guild.id), str(channel.id), new_settings
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

@commands.command(name='dropchannels')
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
    embed = discord.Embed(
        title=f"🌌 {config.branding['name']} - Wonder Help",
        description=f"✨ {config.branding['tagline']} ✨\n*Where Wonder Meets Chrome Dreams*",
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
        name="🎯 Leveling System",
        value="**4-Category Progression:**\n"
              "`w.rank [@user]` - View XP & levels\n"
              "**Gain XP by:** Chatting (Text), Voice time,\n"
              "Special activities (Role), Combined (Overall)",
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
    
    embed.add_field(
        name="🎉 Giveaway System",
        value="**Community Events:**\n"
              "`w.giveaway create` - Advanced giveaway\n"
              "`w.quickgiveaway` - Quick setup\n"
              "`w.giveaway list` - View active\n"
              "`w.giveaway end/reroll` - Manage (Admin)",
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
    
    embed.add_field(
        name="🛡️ Admin Commands",
        value="**Server Management:**\n"
              "`/adddrops` `w.adddrops` - Add drop channel\n"
              "`/removedrops` `w.removedrops` - Remove channel\n"
              "`w.dropchannels` - List channels\n"
              "`w.configdrops` - Configure settings\n"
              "`/forcedrop` `w.forcedrop` - Force drop",
        inline=True
    )
    
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
    
    await ctx.send(embed=embed)

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