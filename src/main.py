import discord
from discord.ext import commands, tasks
import asyncio
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import config
from database import database

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
        
        # Initialize systems (will be imported after conversion)
        self.database = database
        # self.role_manager = None
        # self.shop_system = None
        # self.cooldown_manager = None
        # self.giveaway_system = None
        # self.leveling_system = None
        # self.drop_system = None
        
        self.config = config
        
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logging.info("Setting up Wonder Bot...")
        
        # Initialize database
        await self.database.init()
        logging.info("Database initialized")
        
        # Load cogs (will be added as we convert systems)
        # await self.load_extension('cogs.economy')
        # await self.load_extension('cogs.leveling')
        # await self.load_extension('cogs.shop')
        # await self.load_extension('cogs.giveaway')
        
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
        
        # Handle leveling system (will be implemented when leveling system is converted)
        # if hasattr(self, 'leveling_system') and self.leveling_system:
        #     await self.leveling_system.handle_message(message)
        
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
    bot.add_command(balance)
    bot.add_command(daily)
    bot.add_command(work)
    bot.add_command(leaderboard)
    
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