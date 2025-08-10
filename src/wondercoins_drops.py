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
    """Manages automatic WonderCoins drops in configured channels with advanced admin features"""
    
    def __init__(self, client):
        self.client = client
        self.drop_channels = {}
        self.channel_settings = {}  # Advanced channel-specific settings
        self.active_drops = {}
        
        # Enhanced rarity configuration
        self.rarity_config = {
            'common': {
                'chance': 70,
                'multiplier': 1.0,
                'emoji': '⚪',
                'base_amount': 150,
                'color': 0x87CEEB
            },
            'rare': {
                'chance': 20,
                'multiplier': 2.5,
                'emoji': '🔵',
                'base_amount': 150,
                'color': 0x9BADBE
            },
            'epic': {
                'chance': 8,
                'multiplier': 4.0,
                'emoji': '🟣',
                'base_amount': 150,
                'color': 0xA89CC8
            },
            'legendary': {
                'chance': 2,
                'multiplier': 8.0,
                'emoji': '🟡',
                'base_amount': 150,
                'color': 0xD8B4DA
            }
        }
        
        # Enhanced collection mechanics
        self.collection_types = [
            {
                'name': 'standard',
                'emoji': '💰',
                'description': 'Standard collection',
                'multiplier': 1.0,
                'chance': 50
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
                'description': 'Lucky grab - 40% chance for 1.8x bonus!',
                'multiplier': 1.0,
                'chance': 15,
                'lucky_chance': 0.4,
                'lucky_multiplier': 1.8
            },
            {
                'name': 'wonder_grab',
                'emoji': '✨',
                'description': 'Wonder grab - Mystical bonus effects!',
                'multiplier': 1.5,
                'chance': 10,
                'special_effects': True
            }
        ]
        
        # Start the drop system
        self.start_drop_system.start()
    
    async def initialize_drop_channels(self):
        """Load drop channels and their settings from database"""
        try:
            async with await database._get_connection() as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM drop_channels') as cursor:
                    channels = await cursor.fetchall()
            
            for channel_row in channels:
                guild_id = channel_row['guild_id']
                channel_id = channel_row['channel_id']
                
                if guild_id not in self.drop_channels:
                    self.drop_channels[guild_id] = []
                
                self.drop_channels[guild_id].append(channel_id)
                
                # Load advanced settings if available
                self.channel_settings[f"{guild_id}_{channel_id}"] = {
                    'custom_rarity_multiplier': 1.0,
                    'custom_amount_multiplier': 1.0,
                    'allowed_rarities': ['common', 'rare', 'epic', 'legendary'],
                    'drop_frequency_modifier': 1.0,
                    'special_events': False
                }
                
        except Exception as e:
            logging.error(f"Error initializing drop channels: {e}")
    
    async def add_drop_channel_advanced(self, guild_id: str, channel_id: str, created_by: str, 
                                      settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a channel with advanced configuration options"""
        try:
            # Check if channel already exists
            async with await database._get_connection() as db:
                async with db.execute(
                    'SELECT id FROM drop_channels WHERE guild_id = ? AND channel_id = ?',
                    (guild_id, channel_id)
                ) as cursor:
                    existing = await cursor.fetchone()
            
            if existing:
                return {"success": False, "message": "Channel is already configured for drops!"}
            
            # Add to database with settings
            settings_json = str(settings) if settings else "{}"
            async with await database._get_connection() as db:
                await db.execute(
                    'INSERT INTO drop_channels (guild_id, channel_id, created_by, settings) VALUES (?, ?, ?, ?)',
                    (guild_id, channel_id, created_by, settings_json)
                )
                await db.commit()
            
            # Update cache
            if guild_id not in self.drop_channels:
                self.drop_channels[guild_id] = []
            self.drop_channels[guild_id].append(channel_id)
            
            # Apply advanced settings
            default_settings = {
                'custom_rarity_multiplier': 1.0,
                'custom_amount_multiplier': 1.0,
                'allowed_rarities': ['common', 'rare', 'epic', 'legendary'],
                'drop_frequency_modifier': 1.0,
                'special_events': False
            }
            
            if settings:
                default_settings.update(settings)
            
            self.channel_settings[f"{guild_id}_{channel_id}"] = default_settings
            
            return {"success": True, "message": "Channel added to drop system with advanced settings!"}
            
        except Exception as e:
            logging.error(f"Error adding drop channel: {e}")
            return {"success": False, "message": "An error occurred while adding the channel."}
    
    async def configure_channel_drops(self, guild_id: str, channel_id: str, 
                                    settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure advanced drop settings for a specific channel"""
        try:
            channel_key = f"{guild_id}_{channel_id}"
            
            # Verify channel exists in drop system
            if guild_id not in self.drop_channels or channel_id not in self.drop_channels[guild_id]:
                return {"success": False, "message": "Channel is not configured for drops!"}
            
            # Update settings
            if channel_key not in self.channel_settings:
                self.channel_settings[channel_key] = {}
            
            self.channel_settings[channel_key].update(settings)
            
            # Save to database
            settings_json = str(self.channel_settings[channel_key])
            async with await database._get_connection() as db:
                await db.execute(
                    'UPDATE drop_channels SET settings = ? WHERE guild_id = ? AND channel_id = ?',
                    (settings_json, guild_id, channel_id)
                )
                await db.commit()
            
            return {"success": True, "message": "Channel drop settings updated successfully!"}
            
        except Exception as e:
            logging.error(f"Error configuring channel drops: {e}")
            return {"success": False, "message": "An error occurred while updating settings."}
    
    async def add_drop_channel(self, guild_id: str, channel_id: str, created_by: str) -> Dict[str, Any]:
        """Legacy method - calls advanced version with default settings"""
        return await self.add_drop_channel_advanced(guild_id, channel_id, created_by)

    async def remove_drop_channel(self, guild_id: str, channel_id: str) -> Dict[str, Any]:
        """Remove a channel from the drop system"""
        try:
            # Remove from database
            async with await database._get_connection() as db:
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
            
            # Remove settings
            channel_key = f"{guild_id}_{channel_id}"
            if channel_key in self.channel_settings:
                del self.channel_settings[channel_key]
            
            return {"success": True, "message": "Channel removed from drop system!"}
            
        except Exception as e:
            logging.error(f"Error removing drop channel: {e}")
            return {"success": False, "message": "An error occurred while removing the channel."}
    
    async def force_drop_in_channel(self, guild_id: str, channel_id: str, 
                                  amount: int = None, rarity: str = None) -> Dict[str, Any]:
        """Force a drop in a specific channel (admin feature)"""
        try:
            guild = self.client.get_guild(int(guild_id))
            channel = guild.get_channel(int(channel_id))
            
            if not channel:
                return {"success": False, "message": "Channel not found!"}
            
            # Override rarity if specified
            if rarity and rarity not in self.rarity_config:
                return {"success": False, "message": "Invalid rarity specified!"}
            
            # Create the drop
            await self.create_drop(guild_id, channel_id, forced_amount=amount, forced_rarity=rarity)
            
            return {"success": True, "message": f"Forced drop created in {channel.name}!"}
            
        except Exception as e:
            logging.error(f"Error forcing drop: {e}")
            return {"success": False, "message": "An error occurred while creating the drop."}
    
    async def get_channel_list(self, guild_id: str) -> List[Dict[str, Any]]:
        """Get list of configured drop channels for a guild"""
        try:
            guild = self.client.get_guild(int(guild_id))
            if not guild:
                return []
            
            channels = []
            if guild_id in self.drop_channels:
                for channel_id in self.drop_channels[guild_id]:
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        channel_key = f"{guild_id}_{channel_id}"
                        settings = self.channel_settings.get(channel_key, {})
                        
                        channels.append({
                            'id': channel_id,
                            'name': channel.name,
                            'mention': f'<#{channel_id}>',
                            'settings': settings
                        })
            
            return channels
            
        except Exception as e:
            logging.error(f"Error getting channel list: {e}")
            return []
    
    @tasks.loop(minutes=20)  # Check every 20 minutes (faster than before)
    async def start_drop_system(self):
        """Enhanced drop system loop with dynamic timing"""
        try:
            # Random timing between 20 minutes to 2 hours
            base_wait = random.randint(20, 120)
            
            # Apply global modifiers based on server activity
            # Could be enhanced to check user activity levels
            wait_minutes = base_wait
            
            await asyncio.sleep(wait_minutes * 60)
            
            # Select random guild and channel for drop
            await self.create_random_drop()
            
        except Exception as e:
            logging.error(f"Error in drop system: {e}")
    
    async def create_random_drop(self):
        """Create a random drop in a configured channel with advanced features"""
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
            
            # Select random channel from guild with frequency modifiers
            channel_ids = self.drop_channels[guild_id]
            
            # Apply frequency modifiers
            weighted_channels = []
            for channel_id in channel_ids:
                channel_key = f"{guild_id}_{channel_id}"
                settings = self.channel_settings.get(channel_key, {})
                modifier = settings.get('drop_frequency_modifier', 1.0)
                
                # Add channel multiple times based on frequency modifier
                weight = max(1, int(modifier * 10))
                weighted_channels.extend([channel_id] * weight)
            
            channel_id = random.choice(weighted_channels) if weighted_channels else random.choice(channel_ids)
            channel = guild.get_channel(int(channel_id))
            
            if not channel:
                return
            
            # Generate drop with channel-specific settings
            await self.create_drop(guild_id, channel_id)
            
        except Exception as e:
            logging.error(f"Error creating random drop: {e}")
    
    async def create_drop(self, guild_id: str, channel_id: str, 
                        forced_amount: int = None, forced_rarity: str = None):
        """Create a WonderCoins drop in a specific channel with advanced features"""
        try:
            guild = self.client.get_guild(int(guild_id))
            channel = guild.get_channel(int(channel_id))
            
            if not channel:
                return
            
            # Get channel-specific settings
            channel_key = f"{guild_id}_{channel_id}"
            settings = self.channel_settings.get(channel_key, {})
            
            # Determine rarity with channel restrictions
            if forced_rarity:
                rarity = forced_rarity
            else:
                allowed_rarities = settings.get('allowed_rarities', ['common', 'rare', 'epic', 'legendary'])
                rarity = self._determine_rarity(allowed_rarities, settings.get('custom_rarity_multiplier', 1.0))
            
            rarity_config = self.rarity_config[rarity]
            
            # Determine collection type
            collection_type = self._determine_collection_type()
            
            # Calculate drop amount with channel modifiers
            if forced_amount:
                amount = forced_amount
            else:
                base_amount = rarity_config['base_amount']
                rarity_multiplier = rarity_config['multiplier']
                channel_multiplier = settings.get('custom_amount_multiplier', 1.0)
                
                amount = int(base_amount * rarity_multiplier * channel_multiplier)
                
                # Add some randomness
                variance = int(amount * 0.2)  # 20% variance
                amount += random.randint(-variance, variance)
                amount = max(50, amount)  # Minimum 50 coins
            
            # Create enhanced drop embed
            embed = self._create_enhanced_drop_embed(amount, rarity, collection_type, settings)
            
            # Send drop message
            message = await channel.send(embed=embed)
            
            # Add reactions for collection
            await message.add_reaction(collection_type['emoji'])
            
            # Store active drop with enhanced data
            self.active_drops[str(message.id)] = {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'amount': amount,
                'rarity': rarity,
                'collection_type': collection_type,
                'collectors': [],
                'created_at': datetime.now(),
                'channel_settings': settings,
                'forced': bool(forced_amount or forced_rarity)
            }
            
            # Log the drop
            await self._log_drop_creation(guild_id, amount, rarity, collection_type['name'])
            
            # Set expiry timer (drops expire after 12 minutes for better collection)
            asyncio.create_task(self._expire_drop(message.id, 720))  # 12 minutes
            
        except Exception as e:
            logging.error(f"Error creating drop: {e}")
    
    def _determine_rarity(self, allowed_rarities: List[str] = None, multiplier: float = 1.0) -> str:
        """Determine the rarity of a drop based on chances and restrictions"""
        if not allowed_rarities:
            allowed_rarities = ['common', 'rare', 'epic', 'legendary']
        
        # Filter rarity config to only allowed rarities
        available_rarities = {k: v for k, v in self.rarity_config.items() if k in allowed_rarities}
        
        # Apply multiplier to rare item chances
        if multiplier != 1.0:
            for rarity_name, config in available_rarities.items():
                if rarity_name != 'common':
                    config = config.copy()
                    config['chance'] = min(50, config['chance'] * multiplier)  # Cap at 50%
        
        rand = random.randint(1, 100)
        cumulative_chance = 0
        
        for rarity, config in available_rarities.items():
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
    
    def _create_enhanced_drop_embed(self, amount: int, rarity: str, collection_type: Dict[str, Any], 
                                  settings: Dict[str, Any]) -> discord.Embed:
        """Create enhanced embed for a WonderCoins drop"""
        rarity_config = self.rarity_config[rarity]
        
        # Use rarity-specific color
        embed_color = rarity_config.get('color', int(config.colors['primary'].replace('#', ''), 16))
        
        embed = discord.Embed(
            title=f"✨ WonderCoins Drop!",
            description=f"**{amount:,}** {config.currency['symbol']} have appeared in a mystical shimmer!",
            color=embed_color
        )
        
        embed.add_field(
            name=f"{rarity_config['emoji']} Rarity",
            value=f"**{rarity.title()}** ✨",
            inline=True
        )
        
        embed.add_field(
            name=f"{collection_type['emoji']} Collection",
            value=collection_type['description'],
            inline=True
        )
        
        # Add special effects info if applicable
        if collection_type.get('special_effects'):
            embed.add_field(
                name="🌟 Special Effects",
                value="Wonder energy enhances this drop!",
                inline=True
            )
        
        embed.add_field(
            name="🔮 How to Collect",
            value=f"React with {collection_type['emoji']} to collect these wonder coins!",
            inline=False
        )
        
        # Add channel-specific info if enhanced
        if settings.get('custom_amount_multiplier', 1.0) > 1.0:
            embed.add_field(
                name="💎 Channel Bonus",
                value=f"This channel has enhanced drops! (+{int((settings['custom_amount_multiplier'] - 1) * 100)}%)",
                inline=False
            )
        
        embed.set_footer(text="Drop expires in 12 minutes • Wonderkind drops are magical!")
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
            async with await database._get_connection() as db:
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
            async with await database._get_connection() as db:
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
            async with await database._get_connection() as db:
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
            async with await database._get_connection() as db:
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
            async with await database._get_connection() as db:
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