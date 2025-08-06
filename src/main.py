import discord
from discord.ext import commands, tasks
import asyncio
import os
import logging
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

# Economy Commands
@commands.command(name='balance', aliases=['bal'])
async def balance(ctx: commands.Context):
    """Check your balance"""
    user_data = await ctx.bot.database.get_user(str(ctx.author.id))
    if not user_data:
        await ctx.bot.database.create_user(str(ctx.author.id), ctx.author.name)
        user_data = await ctx.bot.database.get_user(str(ctx.author.id))
    
    balance = user_data['balance'] if user_data else 0
    
    embed = discord.Embed(
        title=f"{config.currency['symbol']} Balance",
        description=f"**{ctx.author.mention}** has **{balance:,}** {config.currency['name']}",
        color=int(config.colors['primary'].replace('#', ''), 16)
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

@commands.command(name='daily')
async def daily(ctx: commands.Context):
    """Claim your daily reward"""
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
            await ctx.send(f"❌ You can claim your daily reward in {hours}h {minutes}m")
            return
    
    # Give daily reward
    daily_amount = config.currency['dailyAmount']
    
    # Check for booster bonus (will be implemented when role system is converted)
    # if ctx.author.premium_since:  # Boost bonus
    #     daily_amount += config.booster['dailyBonus']
    
    await ctx.bot.database.update_balance(str(ctx.author.id), daily_amount)
    await ctx.bot.database.update_daily_claim(str(ctx.author.id))
    await ctx.bot.database.add_transaction(str(ctx.author.id), 'daily', daily_amount, 'Daily reward')
    
    embed = discord.Embed(
        title=f"{config.currency['symbol']} Daily Reward",
        description=f"You claimed **{daily_amount:,}** {config.currency['name']}!",
        color=int(config.colors['success'].replace('#', ''), 16)
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

@commands.command(name='work')
async def work(ctx: commands.Context):
    """Work to earn coins"""
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
            await ctx.send(f"❌ You can work again in {minutes}m {seconds}s")
            return
    
    # Generate work reward
    base_amount = config.currency['workAmount']
    work_amount = random.randint(base_amount - 10, base_amount + 20)
    
    # Work job options
    jobs = [
        "coding", "designing", "streaming", "moderating", "helping others",
        "creating content", "building bots", "managing servers", "tutoring"
    ]
    job = random.choice(jobs)
    
    await ctx.bot.database.update_balance(str(ctx.author.id), work_amount)
    await ctx.bot.database.update_work_claim(str(ctx.author.id))
    await ctx.bot.database.add_transaction(str(ctx.author.id), 'work', work_amount, f'Work: {job}')
    
    embed = discord.Embed(
        title=f"💼 Work Complete",
        description=f"You worked as **{job}** and earned **{work_amount:,}** {config.currency['name']}!",
        color=int(config.colors['success'].replace('#', ''), 16)
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

@commands.command(name='leaderboard', aliases=['lb', 'top'])
async def leaderboard(ctx: commands.Context):
    """View the leaderboard"""
    top_users = await ctx.bot.database.get_top_users(10)
    
    if not top_users:
        await ctx.send("❌ No users found on the leaderboard!")
        return
    
    embed = discord.Embed(
        title=f"{config.theme['emojis']['crown']} {config.currency['name']} Leaderboard",
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
    embed.set_footer(text=f"Total users: {len(top_users)}")
    
    await ctx.send(embed=embed)

# Game Commands with Animations
@commands.command(name='coinflip', aliases=['cf'])
async def coinflip(ctx: commands.Context, bet_amount: int, choice: str):
    """Play animated coinflip game"""
    result = await ctx.bot.games_system.coinflip(str(ctx.author.id), bet_amount, choice, ctx)
    
    if not result['success']:
        await ctx.send(result['message'])
        return
    
    # Animation message is already updated in the game method
    # No need to send another message if animation was shown

@commands.command(name='dice')
async def dice(ctx: commands.Context, bet_amount: int, target: int):
    """Play animated dice game"""
    result = await ctx.bot.games_system.dice(str(ctx.author.id), bet_amount, target, ctx)
    
    if not result['success']:
        await ctx.send(result['message'])
        return
    
    # Animation message is already updated in the game method
    # No need to send another message if animation was shown

@commands.command(name='slots')
async def slots(ctx: commands.Context, bet_amount: int):
    """Play animated slots game"""
    result = await ctx.bot.games_system.slots(str(ctx.author.id), bet_amount, ctx)
    
    if not result['success']:
        await ctx.send(result['message'])
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

@commands.command(name='adddrops')
@commands.has_permissions(manage_guild=True)
async def add_drop_channel(ctx: commands.Context, channel: discord.TextChannel = None):
    """Add a channel to the drop system (Admin only)"""
    target_channel = channel or ctx.channel
    
    result = await ctx.bot.drop_system.add_drop_channel(
        str(ctx.guild.id), str(target_channel.id), str(ctx.author.id)
    )
    
    embed = discord.Embed(
        title="💰 Drop Channel Configuration",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    
    await ctx.send(embed=embed)

@commands.command(name='removedrops')
@commands.has_permissions(manage_guild=True)
async def remove_drop_channel(ctx: commands.Context, channel: discord.TextChannel = None):
    """Remove a channel from the drop system (Admin only)"""
    target_channel = channel or ctx.channel
    
    result = await ctx.bot.drop_system.remove_drop_channel(
        str(ctx.guild.id), str(target_channel.id)
    )
    
    embed = discord.Embed(
        title="💰 Drop Channel Configuration",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
    
    await ctx.send(embed=embed)

@commands.command(name='forcedrop')
@commands.has_permissions(administrator=True)
async def force_drop(ctx: commands.Context, amount: int = None, rarity: str = None):
    """Force a WonderCoins drop in current channel (Admin only)"""
    result = await ctx.bot.drop_system.force_drop_in_channel(
        str(ctx.guild.id), str(ctx.channel.id), amount, rarity
    )
    
    embed = discord.Embed(
        title="✨ Force Drop",
        description=result['message'],
        color=int(config.colors['success' if result['success'] else 'error'].replace('#', ''), 16)
    )
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

# Help Command
@commands.command(name='help')
async def help_command(ctx: commands.Context):
    """Show help information"""
    embed = discord.Embed(
        title=f"🤖 {config.branding['name']} - Help",
        description=config.branding['tagline'],
        color=int(config.colors['primary'].replace('#', ''), 16)
    )
    
    embed.add_field(
        name="💰 Economy Commands",
        value="`w.balance` - Check balance\n"
              "`w.daily` - Daily reward\n"
              "`w.work` - Work for coins\n"
              "`w.leaderboard` - Top earners",
        inline=True
    )
    
    embed.add_field(
        name="🎮 Games",
        value="`w.coinflip <amount> <h/t>` - Coinflip\n"
              "`w.dice <amount> <1-6>` - Dice roll\n"
              "`w.slots <amount>` - Slot machine\n"
              "`w.gamestats` - Gambling stats",
        inline=True
    )
    
    embed.add_field(
        name="🛒 Shop & Items",
        value="`w.shop [category]` - View shop\n"
              "`w.buy <item>` - Purchase item\n"
              "`w.inventory` - View items\n"
              "`w.use <item>` - Use item",
        inline=True
    )
    
    embed.add_field(
        name="📊 Leveling",
        value="`w.rank [@user]` - View rank\n"
              "Gain XP by chatting and being in voice!",
        inline=True
    )
    
    embed.add_field(
        name="🎉 Giveaway Commands",
        value="`w.giveaway` - Advanced giveaway system\n"
              "`w.giveaway create` - Create giveaway\n"
              "`w.giveaway list` - List giveaways\n"
              "`w.quickgiveaway` - Quick giveaway",
        inline=True
    )
    
    embed.add_field(
        name="🛡️ Admin Commands",
        value="`w.giveaway end` - End giveaway\n"
              "`w.giveaway reroll` - Reroll winners\n"
              "`w.adddrops` - Add drop channel\n"
              "`w.removedrops` - Remove drop channel\n"
              "`w.dropchannels` - List drop channels\n"
              "`w.configdrops` - Configure channel drops\n"
              "`w.forcedrop` - Force wonder drop",
        inline=True
    )
    
    embed.add_field(
        name="✨ WonderCoins Drops",
        value="Mystical wonder drops appear randomly!\n"
              "React quickly to collect them!\n"
              "🌟 Enhanced with wonder energy! 🌟",
        inline=True
    )
    
    embed.set_footer(text=f"Bot Version: {config.branding['version']}")
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