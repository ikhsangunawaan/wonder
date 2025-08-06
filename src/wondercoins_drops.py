import discord
from discord.ext import tasks
import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from database import database
from config import config

class WonderCoinsDropSystem:
    """Manages automatic WonderCoins drops in configured channels"""
    
    def __init__(self, client):
        self.client = client
        self.drop_channels = {}
        self.active_drops = {}
        self.rarity_config = {
            'common': {
                'chance': 84,
                'multiplier': 1.0,
                'emoji': '⚪',
                'base_amount': 150
            },
            'rare': {
                'chance': 10,
                'multiplier': 3.0,
                'emoji': '🔵',
                'base_amount': 150
            },
            'epic': {
                'chance': 5,
                'multiplier': 5.0,
                'emoji': '🟣',
                'base_amount': 150
            },
            'legendary': {
                'chance': 1,
                'multiplier': 10.0,
                'emoji': '🟡',
                'base_amount': 150
            }
        }
        
        # Collection mechanics
        self.collection_types = [
            {
                'name': 'standard',
                'emoji': '💰',
                'description': 'Standard collection',
                'multiplier': 1.0,
                'chance': 60
            },
            {
                'name': 'quick_grab',
                'emoji': '⚡',
                'description': 'Quick grab - 2x coins for first 3 collectors!',
                'multiplier': 2.0,
                'chance': 25,
                'max_collectors': 3
            },
            {
                'name': 'lucky_grab',
                'emoji': '🍀',
                'description': 'Lucky grab - 30% chance for 1.5x bonus!',
                'multiplier': 1.0,  # Base, bonus applied randomly
                'chance': 15,
                'lucky_chance': 0.3,
                'lucky_multiplier': 1.5
            }
        ]
        
        # Start the drop system
        self.start_drop_system.start()
    
    async def initialize_drop_channels(self):
        """Load drop channels from database"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute('SELECT * FROM drop_channels') as cursor:
                        channels = await cursor.fetchall()
            
            for channel_row in channels:
                guild_id = channel_row['guild_id']
                channel_id = channel_row['channel_id']
                
                if guild_id not in self.drop_channels:
                    self.drop_channels[guild_id] = []
                
                self.drop_channels[guild_id].append(channel_id)
                
        except Exception as e:
            logging.error(f"Error initializing drop channels: {e}")
    
    async def add_drop_channel(self, guild_id: str, channel_id: str, created_by: str) -> Dict[str, Any]:
        """Add a channel to the drop system"""
        try:
            # Check if channel already exists
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    async with db.execute(
                        'SELECT id FROM drop_channels WHERE guild_id = ? AND channel_id = ?',
                        (guild_id, channel_id)
                    ) as cursor:
                        existing = await cursor.fetchone()
            
            if existing:
                return {"success": False, "message": "Channel is already configured for drops!"}
            
            # Add to database
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        'INSERT INTO drop_channels (guild_id, channel_id, created_by) VALUES (?, ?, ?)',
                        (guild_id, channel_id, created_by)
                    )
                    await db.commit()
            
            # Update cache
            if guild_id not in self.drop_channels:
                self.drop_channels[guild_id] = []
            self.drop_channels[guild_id].append(channel_id)
            
            return {"success": True, "message": "Channel added to drop system!"}
            
        except Exception as e:
            logging.error(f"Error adding drop channel: {e}")
            return {"success": False, "message": "An error occurred while adding the channel."}
    
    async def remove_drop_channel(self, guild_id: str, channel_id: str) -> Dict[str, Any]:
        """Remove a channel from the drop system"""
        try:
            # Remove from database
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    cursor = await db.execute(
                        'DELETE FROM drop_channels WHERE guild_id = ? AND channel_id = ?',
                        (guild_id, channel_id)
                    )
                    await db.commit()
                    
                    if cursor.rowcount == 0:
                        return {"success": False, "message": "Channel is not configured for drops!"}
            
            # Update cache
            if guild_id in self.drop_channels and channel_id in self.drop_channels[guild_id]:
                self.drop_channels[guild_id].remove(channel_id)
            
            return {"success": True, "message": "Channel removed from drop system!"}
            
        except Exception as e:
            logging.error(f"Error removing drop channel: {e}")
            return {"success": False, "message": "An error occurred while removing the channel."}
    
    @tasks.loop(minutes=30)  # Check every 30 minutes
    async def start_drop_system(self):
        """Main drop system loop"""
        try:
            # Random timing between 30 minutes to 3 hours
            wait_minutes = random.randint(30, 180)
            await asyncio.sleep(wait_minutes * 60)
            
            # Select random guild and channel for drop
            await self.create_random_drop()
            
        except Exception as e:
            logging.error(f"Error in drop system: {e}")
    
    async def create_random_drop(self):
        """Create a random drop in a configured channel"""
        try:
            if not self.drop_channels:
                await self.initialize_drop_channels()
            
            if not self.drop_channels:
                return
            
            # Select random guild
            guild_id = random.choice(list(self.drop_channels.keys()))
            guild = self.client.get_guild(int(guild_id))
            
            if not guild:
                return
            
            # Select random channel from guild
            channel_ids = self.drop_channels[guild_id]
            channel_id = random.choice(channel_ids)
            channel = guild.get_channel(int(channel_id))
            
            if not channel:
                return
            
            # Generate drop
            await self.create_drop(guild_id, channel_id)
            
        except Exception as e:
            logging.error(f"Error creating random drop: {e}")
    
    async def create_drop(self, guild_id: str, channel_id: str):
        """Create a WonderCoins drop in a specific channel"""
        try:
            guild = self.client.get_guild(int(guild_id))
            channel = guild.get_channel(int(channel_id))
            
            if not channel:
                return
            
            # Determine rarity
            rarity = self._determine_rarity()
            rarity_config = self.rarity_config[rarity]
            
            # Determine collection type
            collection_type = self._determine_collection_type()
            
            # Calculate drop amount
            base_amount = rarity_config['base_amount']
            rarity_multiplier = rarity_config['multiplier']
            amount = int(base_amount * rarity_multiplier)
            
            # Add some randomness
            amount += random.randint(-25, 25)
            amount = max(50, amount)  # Minimum 50 coins
            
            # Create drop embed
            embed = self._create_drop_embed(amount, rarity, collection_type)
            
            # Send drop message
            message = await channel.send(embed=embed)
            
            # Add reactions for collection
            await message.add_reaction(collection_type['emoji'])
            
            # Store active drop
            self.active_drops[str(message.id)] = {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'amount': amount,
                'rarity': rarity,
                'collection_type': collection_type,
                'collectors': [],
                'created_at': datetime.now()
            }
            
            # Log the drop
            await self._log_drop_creation(guild_id, amount, rarity, collection_type['name'])
            
            # Set expiry timer (drops expire after 10 minutes)
            asyncio.create_task(self._expire_drop(message.id, 600))  # 10 minutes
            
        except Exception as e:
            logging.error(f"Error creating drop: {e}")
    
    def _determine_rarity(self) -> str:
        """Determine the rarity of a drop based on chances"""
        rand = random.randint(1, 100)
        
        cumulative_chance = 0
        for rarity, config in self.rarity_config.items():
            cumulative_chance += config['chance']
            if rand <= cumulative_chance:
                return rarity
        
        return 'common'  # Fallback
    
    def _determine_collection_type(self) -> Dict[str, Any]:
        """Determine the collection type for a drop"""
        rand = random.randint(1, 100)
        
        cumulative_chance = 0
        for collection in self.collection_types:
            cumulative_chance += collection['chance']
            if rand <= cumulative_chance:
                return collection
        
        return self.collection_types[0]  # Fallback to standard
    
    def _create_drop_embed(self, amount: int, rarity: str, collection_type: Dict[str, Any]) -> discord.Embed:
        """Create embed for a WonderCoins drop"""
        rarity_config = self.rarity_config[rarity]
        
        embed = discord.Embed(
            title=f"💰 WonderCoins Drop!",
            description=f"**{amount:,}** {config.currency['symbol']} have appeared!",
            color=int(config.colors['primary'].replace('#', ''), 16)
        )
        
        embed.add_field(
            name=f"{rarity_config['emoji']} Rarity",
            value=rarity.title(),
            inline=True
        )
        
        embed.add_field(
            name=f"{collection_type['emoji']} Collection",
            value=collection_type['description'],
            inline=True
        )
        
        embed.add_field(
            name="📝 How to Collect",
            value=f"React with {collection_type['emoji']} to collect!",
            inline=False
        )
        
        embed.set_footer(text="Drop expires in 10 minutes")
        embed.timestamp = datetime.now()
        
        return embed
    
    async def handle_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle reactions to drop messages"""
        if user.bot:
            return
        
        message_id = str(reaction.message.id)
        if message_id not in self.active_drops:
            return
        
        drop_data = self.active_drops[message_id]
        collection_type = drop_data['collection_type']
        
        # Check if reaction matches collection type
        if str(reaction.emoji) != collection_type['emoji']:
            return
        
        # Check if user already collected
        if user.id in [collector['user_id'] for collector in drop_data['collectors']]:
            return
        
        # Calculate collection amount
        base_amount = drop_data['amount']
        final_amount = await self._calculate_collection_amount(user, drop_data)
        
        # Add to user balance
        await database.create_user(str(user.id), user.name)
        await database.update_balance(str(user.id), final_amount)
        await database.add_transaction(str(user.id), 'wondercoins_drop', final_amount, 
                                      f'Drop collection: {drop_data["rarity"]} {collection_type["name"]}')
        
        # Record collection
        collection_info = {
            'user_id': user.id,
            'amount': final_amount,
            'collected_at': datetime.now()
        }
        drop_data['collectors'].append(collection_info)
        
        # Log the collection
        await self._log_drop_collection(drop_data['guild_id'], str(user.id), final_amount, 
                                       drop_data['rarity'], collection_type['name'])
        
        # Update user drop stats
        await self._update_user_drop_stats(str(user.id), final_amount, drop_data['rarity'])
        
        # Send collection confirmation
        try:
            await user.send(f"🎉 You collected **{final_amount:,}** {config.currency['symbol']} from a {drop_data['rarity']} drop!")
        except:
            pass  # User has DMs disabled
        
        # Check if drop should end (for quick grab)
        if (collection_type['name'] == 'quick_grab' and 
            len(drop_data['collectors']) >= collection_type.get('max_collectors', 3)):
            await self._end_drop(message_id)
    
    async def _calculate_collection_amount(self, user: discord.User, drop_data: Dict[str, Any]) -> int:
        """Calculate the amount a user gets from collecting a drop"""
        base_amount = drop_data['amount']
        collection_type = drop_data['collection_type']
        multiplier = 1.0
        
        # Apply collection type multiplier
        if collection_type['name'] == 'quick_grab':
            # Check if user is in first 3 collectors
            if len(drop_data['collectors']) < collection_type.get('max_collectors', 3):
                multiplier = collection_type['multiplier']
        
        elif collection_type['name'] == 'lucky_grab':
            # Random chance for bonus
            if random.random() < collection_type.get('lucky_chance', 0.3):
                multiplier = collection_type['lucky_multiplier']
        
        else:  # standard
            multiplier = collection_type['multiplier']
        
        # Apply role-based multipliers
        try:
            guild = self.client.get_guild(int(drop_data['guild_id']))
            if guild:
                member = guild.get_member(user.id)
                if member:
                    # Premium members get bonus
                    if member.premium_since:
                        multiplier *= 1.5  # 50% bonus for boosters
                    
                    # Could add other role-based bonuses here
        except:
            pass
        
        final_amount = int(base_amount * multiplier)
        return max(1, final_amount)  # Minimum 1 coin
    
    async def _log_drop_creation(self, guild_id: str, amount: int, rarity: str, collection_type: str):
        """Log drop creation to database"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        """INSERT INTO drop_stats 
                           (guild_id, user_id, amount, rarity, collection_type)
                           VALUES (?, ?, ?, ?, ?)""",
                        (guild_id, 'SYSTEM', amount, rarity, f'created_{collection_type}')
                    )
                    await db.commit()
        except Exception as e:
            logging.error(f"Error logging drop creation: {e}")
    
    async def _log_drop_collection(self, guild_id: str, user_id: str, amount: int, rarity: str, collection_type: str):
        """Log drop collection to database"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        """INSERT INTO drop_stats 
                           (guild_id, user_id, amount, rarity, collection_type)
                           VALUES (?, ?, ?, ?, ?)""",
                        (guild_id, user_id, amount, rarity, collection_type)
                    )
                    await db.commit()
        except Exception as e:
            logging.error(f"Error logging drop collection: {e}")
    
    async def _update_user_drop_stats(self, user_id: str, amount: int, rarity: str):
        """Update user's drop statistics"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    # Check if user stats exist
                    async with db.execute(
                        'SELECT * FROM user_drop_stats WHERE user_id = ?', (user_id,)
                    ) as cursor:
                        existing = await cursor.fetchone()
                    
                    if existing:
                        # Update existing stats
                        await db.execute(
                            """UPDATE user_drop_stats SET 
                               total_collected = total_collected + ?,
                               total_drops = total_drops + 1,
                               {}_drops = {}_drops + 1,
                               last_drop = CURRENT_TIMESTAMP,
                               best_drop = MAX(best_drop, ?)
                               WHERE user_id = ?""".format(rarity, rarity),
                            (amount, amount, user_id)
                        )
                    else:
                        # Create new stats record
                        await db.execute(
                            """INSERT INTO user_drop_stats 
                               (user_id, total_collected, total_drops, {}_drops, last_drop, best_drop)
                               VALUES (?, ?, 1, 1, CURRENT_TIMESTAMP, ?)""".format(rarity),
                            (user_id, amount, amount)
                        )
                    
                    await db.commit()
                    
        except Exception as e:
            logging.error(f"Error updating user drop stats: {e}")
    
    async def _expire_drop(self, message_id: int, delay_seconds: int):
        """Expire a drop after a delay"""
        await asyncio.sleep(delay_seconds)
        await self._end_drop(str(message_id))
    
    async def _end_drop(self, message_id: str):
        """End a drop and clean up"""
        if message_id in self.active_drops:
            drop_data = self.active_drops[message_id]
            
            # Update drop message to show it ended
            try:
                guild = self.client.get_guild(int(drop_data['guild_id']))
                if guild:
                    channel = guild.get_channel(int(drop_data['channel_id']))
                    if channel:
                        message = await channel.fetch_message(int(message_id))
                        
                        # Update embed to show ended
                        embed = message.embeds[0] if message.embeds else None
                        if embed:
                            embed.title = "💰 WonderCoins Drop (ENDED)"
                            embed.color = discord.Color.gray()
                            embed.set_footer(text=f"Drop ended • {len(drop_data['collectors'])} collectors")
                            await message.edit(embed=embed)
            except:
                pass
            
            # Remove from active drops
            del self.active_drops[message_id]
    
    async def get_drop_stats(self, guild_id: str) -> Dict[str, Any]:
        """Get drop statistics for a guild"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    db.row_factory = aiosqlite.Row
                    
                    # Get total drops created
                    async with db.execute(
                        """SELECT COUNT(*) as total_drops, SUM(amount) as total_amount
                           FROM drop_stats WHERE guild_id = ? AND user_id = 'SYSTEM'""",
                        (guild_id,)
                    ) as cursor:
                        drop_stats = await cursor.fetchone()
                    
                    # Get collection stats
                    async with db.execute(
                        """SELECT COUNT(*) as total_collections, SUM(amount) as total_collected
                           FROM drop_stats WHERE guild_id = ? AND user_id != 'SYSTEM'""",
                        (guild_id,)
                    ) as cursor:
                        collection_stats = await cursor.fetchone()
                    
                    # Get rarity breakdown
                    async with db.execute(
                        """SELECT rarity, COUNT(*) as count FROM drop_stats 
                           WHERE guild_id = ? AND user_id = 'SYSTEM' 
                           GROUP BY rarity""",
                        (guild_id,)
                    ) as cursor:
                        rarity_stats = await cursor.fetchall()
            
            return {
                'total_drops': drop_stats['total_drops'] or 0,
                'total_drop_amount': drop_stats['total_amount'] or 0,
                'total_collections': collection_stats['total_collections'] or 0,
                'total_collected': collection_stats['total_collected'] or 0,
                'rarity_breakdown': {row['rarity']: row['count'] for row in rarity_stats}
            }
            
        except Exception as e:
            logging.error(f"Error getting drop stats: {e}")
            return {}
    
    async def get_user_drop_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get drop statistics for a user"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute(
                        'SELECT * FROM user_drop_stats WHERE user_id = ?', (user_id,)
                    ) as cursor:
                        stats = await cursor.fetchone()
                        return dict(stats) if stats else None
                        
        except Exception as e:
            logging.error(f"Error getting user drop stats: {e}")
            return None

# Global drop system instance (will be initialized with bot client)
wondercoins_drops = None

def init_wondercoins_drops(client):
    """Initialize the WonderCoins drop system with bot client"""
    global wondercoins_drops
    wondercoins_drops = WonderCoinsDropSystem(client)
    return wondercoins_drops