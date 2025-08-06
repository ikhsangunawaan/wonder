import discord
from discord.ext import tasks
import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from database import database
from config import config

class GiveawaySystem:
    """Manages giveaway creation, entries, and winner selection"""
    
    def __init__(self, client):
        self.client = client
        self.active_giveaways = {}
        self.check_giveaways.start()
    
    async def create_giveaway(self, host_id: str, guild_id: str, channel_id: str, 
                            title: str, description: str, prize: str, 
                            duration_minutes: int, winners_count: int = 1,
                            requirements: Optional[str] = None) -> Dict[str, Any]:
        """Create a new giveaway"""
        try:
            # Validate duration
            max_duration = config.get('giveaways.maxDuration', 10080)  # 7 days default
            if duration_minutes > max_duration:
                return {
                    "success": False,
                    "message": f"Giveaway duration cannot exceed {max_duration} minutes ({max_duration//1440} days)!"
                }
            
            # Validate winners count
            max_winners = config.get('giveaways.maxWinners', 10)
            if winners_count > max_winners:
                return {
                    "success": False,
                    "message": f"Maximum {max_winners} winners allowed!"
                }
            
            # Calculate end time
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            # Create giveaway embed
            embed = self._create_giveaway_embed(title, description, prize, end_time, winners_count, host_id)
            
            # Send giveaway message
            channel = self.client.get_channel(int(channel_id))
            if not channel:
                return {"success": False, "message": "Channel not found!"}
            
            message = await channel.send(embed=embed)
            await message.add_reaction("🎉")
            
            # Save to database
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
                    cursor = await db.execute(
                        """INSERT INTO giveaways 
                           (message_id, channel_id, guild_id, host_id, title, description, 
                            winners_count, end_time, prize, requirements, status)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (str(message.id), channel_id, guild_id, host_id, title, description,
                         winners_count, end_time.isoformat(), prize, requirements, 'active')
                    )
                    await db.commit()
                    giveaway_id = cursor.lastrowid
            
            # Store in memory for tracking
            self.active_giveaways[str(message.id)] = {
                'id': giveaway_id,
                'end_time': end_time,
                'guild_id': guild_id,
                'channel_id': channel_id,
                'message_id': str(message.id)
            }
            
            return {
                "success": True,
                "message": f"Giveaway created successfully! It will end {discord.utils.format_dt(end_time, 'R')}",
                "giveaway_id": giveaway_id,
                "message_id": str(message.id)
            }
            
        except Exception as e:
            logging.error(f"Error creating giveaway: {e}")
            return {"success": False, "message": "An error occurred while creating the giveaway."}
    
    def _create_giveaway_embed(self, title: str, description: str, prize: str, 
                              end_time: datetime, winners_count: int, host_id: str) -> discord.Embed:
        """Create giveaway embed"""
        embed = discord.Embed(
            title=f"🎉 {title}",
            description=description,
            color=int(config.colors['primary'].replace('#', ''), 16)
        )
        
        embed.add_field(
            name="🏆 Prize",
            value=prize,
            inline=True
        )
        
        embed.add_field(
            name="👥 Winners",
            value=f"{winners_count} winner{'s' if winners_count > 1 else ''}",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Ends",
            value=discord.utils.format_dt(end_time, 'R'),
            inline=True
        )
        
        embed.add_field(
            name="📝 How to Enter",
            value="React with 🎉 to enter!",
            inline=False
        )
        
        embed.set_footer(text=f"Hosted by {host_id}")
        embed.timestamp = datetime.now()
        
        return embed
    
    async def handle_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle giveaway entry via reaction"""
        if user.bot:
            return
        
        if str(reaction.emoji) != "🎉":
            return
        
        message_id = str(reaction.message.id)
        
        # Check if this is a giveaway message
        giveaway = await self._get_giveaway_by_message_id(message_id)
        if not giveaway or giveaway['status'] != 'active':
            return
        
        # Check if user meets requirements
        if not await self._check_entry_requirements(user, giveaway):
            try:
                await user.send("❌ You don't meet the requirements to enter this giveaway!")
            except:
                pass  # User has DMs disabled
            return
        
        # Add entry to database
        await self._add_giveaway_entry(giveaway['id'], str(user.id))
    
    async def handle_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        """Handle giveaway entry removal"""
        if user.bot:
            return
        
        if str(reaction.emoji) != "🎉":
            return
        
        message_id = str(reaction.message.id)
        giveaway = await self._get_giveaway_by_message_id(message_id)
        
        if not giveaway:
            return
        
        # Remove entry from database
        await self._remove_giveaway_entry(giveaway['id'], str(user.id))
    
    async def _get_giveaway_by_message_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get giveaway data by message ID"""
        import aiosqlite
        async with aiosqlite.connect(database.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM giveaways WHERE message_id = ?', (message_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
    
    async def _check_entry_requirements(self, user: discord.User, giveaway: Dict[str, Any]) -> bool:
        """Check if user meets giveaway entry requirements"""
        try:
            guild = self.client.get_guild(int(giveaway['guild_id']))
            if not guild:
                return False
            
            member = guild.get_member(user.id)
            if not member:
                return False
            
            # Check account age requirement
            account_age_min = config.get('giveaways.restrictions.accountAgeMin', 7)
            account_age = (datetime.now() - user.created_at).days
            if account_age < account_age_min:
                return False
            
            # Check if user was recently in another giveaway (cooldown)
            winner_cooldown = config.get('giveaways.winnerCooldown', 10080)  # 7 days
            if await self._user_recently_won(str(user.id), winner_cooldown):
                # Premium users can bypass this
                premium_bypass = config.get('giveaways.restrictions.premiumBypass', True)
                if not premium_bypass or not member.premium_since:
                    return False
            
            # Custom requirements (could be role-based, etc.)
            if giveaway.get('requirements'):
                # Parse and check custom requirements
                # Implementation depends on requirement format
                pass
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking entry requirements: {e}")
            return False
    
    async def _user_recently_won(self, user_id: str, cooldown_minutes: int) -> bool:
        """Check if user recently won a giveaway"""
        cutoff_time = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        async with database.db_path as db_path:
            import aiosqlite
            async with aiosqlite.connect(db_path) as db:
                async with db.execute(
                    """SELECT COUNT(*) FROM giveaway_entries ge
                       JOIN giveaways g ON ge.giveaway_id = g.id
                       WHERE ge.user_id = ? AND g.status = 'completed' 
                       AND g.end_time > ?""",
                    (user_id, cutoff_time.isoformat())
                ) as cursor:
                    row = await cursor.fetchone()
                    return row[0] > 0 if row else False
    
    async def _add_giveaway_entry(self, giveaway_id: int, user_id: str):
        """Add user entry to giveaway"""
        try:
            # Calculate entry weight based on user roles
            entries = await self._calculate_entry_weight(user_id, giveaway_id)
            
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        """INSERT OR REPLACE INTO giveaway_entries 
                           (giveaway_id, user_id, entries) VALUES (?, ?, ?)""",
                        (giveaway_id, user_id, entries)
                    )
                    await db.commit()
                    
        except Exception as e:
            logging.error(f"Error adding giveaway entry: {e}")
    
    async def _remove_giveaway_entry(self, giveaway_id: int, user_id: str):
        """Remove user entry from giveaway"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        'DELETE FROM giveaway_entries WHERE giveaway_id = ? AND user_id = ?',
                        (giveaway_id, user_id)
                    )
                    await db.commit()
                    
        except Exception as e:
            logging.error(f"Error removing giveaway entry: {e}")
    
    async def _calculate_entry_weight(self, user_id: str, giveaway_id: int) -> int:
        """Calculate entry weight based on user roles and config"""
        try:
            giveaway = await self._get_giveaway_by_id(giveaway_id)
            if not giveaway:
                return 1
            
            guild = self.client.get_guild(int(giveaway['guild_id']))
            if not guild:
                return 1
            
            member = guild.get_member(int(user_id))
            if not member:
                return 1
            
            # Base entries
            entries = 1
            
            # Role-based multipliers from config
            odds = config.get('giveaways.odds', {})
            
            # Premium members get better odds
            if member.premium_since:
                premium_multiplier = odds.get('premium', 3.0)
                entries = int(entries * premium_multiplier)
            
            # Booster bonus
            if any(role.name.lower() in ['booster', 'server booster'] for role in member.roles):
                booster_multiplier = odds.get('booster', 2.0)
                entries = int(entries * booster_multiplier)
            
            return max(1, entries)
            
        except Exception as e:
            logging.error(f"Error calculating entry weight: {e}")
            return 1
    
    async def _get_giveaway_by_id(self, giveaway_id: int) -> Optional[Dict[str, Any]]:
        """Get giveaway by ID"""
        async with database.db_path as db_path:
            import aiosqlite
            async with aiosqlite.connect(db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM giveaways WHERE id = ?', (giveaway_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
    
    @tasks.loop(minutes=1)
    async def check_giveaways(self):
        """Check for ended giveaways and process them"""
        try:
            now = datetime.now()
            
            # Get all active giveaways that have ended
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute(
                        'SELECT * FROM giveaways WHERE status = ? AND end_time <= ?',
                        ('active', now.isoformat())
                    ) as cursor:
                        ended_giveaways = await cursor.fetchall()
            
            for giveaway_row in ended_giveaways:
                giveaway = dict(giveaway_row)
                await self._end_giveaway(giveaway)
                
        except Exception as e:
            logging.error(f"Error checking giveaways: {e}")
    
    async def _end_giveaway(self, giveaway: Dict[str, Any]):
        """End a giveaway and select winners"""
        try:
            giveaway_id = giveaway['id']
            
            # Get all entries
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute(
                        'SELECT * FROM giveaway_entries WHERE giveaway_id = ?',
                        (giveaway_id,)
                    ) as cursor:
                        entries = await cursor.fetchall()
            
            if not entries:
                # No entries - announce no winners
                await self._announce_no_winners(giveaway)
                await self._mark_giveaway_completed(giveaway_id)
                return
            
            # Select winners
            winners = await self._select_winners(entries, giveaway['winners_count'])
            
            # Announce winners
            await self._announce_winners(giveaway, winners)
            
            # Mark as completed
            await self._mark_giveaway_completed(giveaway_id)
            
            # Remove from active tracking
            message_id = str(giveaway['message_id'])
            if message_id in self.active_giveaways:
                del self.active_giveaways[message_id]
                
        except Exception as e:
            logging.error(f"Error ending giveaway: {e}")
    
    async def _select_winners(self, entries: List[Dict[str, Any]], winners_count: int) -> List[str]:
        """Select winners from giveaway entries using weighted selection"""
        # Create weighted list based on entry counts
        weighted_users = []
        for entry in entries:
            user_id = entry['user_id']
            entry_weight = entry['entries']
            weighted_users.extend([user_id] * entry_weight)
        
        # Select unique winners
        winners = []
        available_users = weighted_users.copy()
        
        for _ in range(min(winners_count, len(set(weighted_users)))):
            if not available_users:
                break
            
            winner = random.choice(available_users)
            winners.append(winner)
            
            # Remove all entries for this user so they can't win multiple times
            available_users = [user for user in available_users if user != winner]
        
        return winners
    
    async def _announce_winners(self, giveaway: Dict[str, Any], winners: List[str]):
        """Announce giveaway winners"""
        try:
            channel = self.client.get_channel(int(giveaway['channel_id']))
            if not channel:
                return
            
            # Get original message
            try:
                message = await channel.fetch_message(int(giveaway['message_id']))
            except:
                message = None
            
            # Create winner announcement
            embed = discord.Embed(
                title="🎉 Giveaway Ended!",
                description=f"**{giveaway['title']}**",
                color=int(config.colors['success'].replace('#', ''), 16)
            )
            
            embed.add_field(
                name="🏆 Prize",
                value=giveaway['prize'],
                inline=True
            )
            
            if winners:
                winner_mentions = [f"<@{winner}>" for winner in winners]
                embed.add_field(
                    name="🎊 Winners",
                    value="\n".join(winner_mentions),
                    inline=False
                )
            else:
                embed.add_field(
                    name="😔 No Winners",
                    value="No valid entries were found.",
                    inline=False
                )
            
            embed.timestamp = datetime.now()
            
            # Send announcement
            await channel.send(embed=embed)
            
            # Update original message if possible
            if message:
                try:
                    updated_embed = message.embeds[0] if message.embeds else None
                    if updated_embed:
                        updated_embed.color = int(config.colors['success'].replace('#', ''), 16)
                        updated_embed.title = f"🎉 {giveaway['title']} (ENDED)"
                        await message.edit(embed=updated_embed)
                except:
                    pass
            
            # Send DM to winners
            for winner_id in winners:
                try:
                    user = await self.client.fetch_user(int(winner_id))
                    if user:
                        dm_embed = discord.Embed(
                            title="🎉 Congratulations!",
                            description=f"You won the giveaway **{giveaway['title']}**!",
                            color=int(config.colors['success'].replace('#', ''), 16)
                        )
                        dm_embed.add_field(name="Prize", value=giveaway['prize'], inline=False)
                        await user.send(embed=dm_embed)
                except:
                    pass  # User has DMs disabled or other error
                    
        except Exception as e:
            logging.error(f"Error announcing winners: {e}")
    
    async def _announce_no_winners(self, giveaway: Dict[str, Any]):
        """Announce that giveaway had no winners"""
        try:
            channel = self.client.get_channel(int(giveaway['channel_id']))
            if not channel:
                return
            
            embed = discord.Embed(
                title="😔 Giveaway Ended - No Winners",
                description=f"**{giveaway['title']}** ended with no entries.",
                color=int(config.colors['warning'].replace('#', ''), 16)
            )
            
            embed.add_field(
                name="🏆 Prize",
                value=giveaway['prize'],
                inline=True
            )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Error announcing no winners: {e}")
    
    async def _mark_giveaway_completed(self, giveaway_id: int):
        """Mark giveaway as completed in database"""
        async with database.db_path as db_path:
            import aiosqlite
            async with aiosqlite.connect(db_path) as db:
                await db.execute(
                    'UPDATE giveaways SET status = ? WHERE id = ?',
                    ('completed', giveaway_id)
                )
                await db.commit()
    
    async def get_active_giveaways(self, guild_id: str) -> List[Dict[str, Any]]:
        """Get all active giveaways for a guild"""
        async with database.db_path as db_path:
            import aiosqlite
            async with aiosqlite.connect(db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM giveaways WHERE guild_id = ? AND status = ? ORDER BY end_time',
                    (guild_id, 'active')
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
    
    async def cancel_giveaway(self, giveaway_id: int, user_id: str) -> Dict[str, Any]:
        """Cancel an active giveaway"""
        try:
            giveaway = await self._get_giveaway_by_id(giveaway_id)
            if not giveaway:
                return {"success": False, "message": "Giveaway not found!"}
            
            if giveaway['status'] != 'active':
                return {"success": False, "message": "Giveaway is not active!"}
            
            # Check permissions (host or admin)
            if giveaway['host_id'] != user_id:
                # Could add admin permission check here
                return {"success": False, "message": "You can only cancel your own giveaways!"}
            
            # Mark as cancelled
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        'UPDATE giveaways SET status = ? WHERE id = ?',
                        ('cancelled', giveaway_id)
                    )
                    await db.commit()
            
            # Announce cancellation
            try:
                channel = self.client.get_channel(int(giveaway['channel_id']))
                if channel:
                    embed = discord.Embed(
                        title="❌ Giveaway Cancelled",
                        description=f"**{giveaway['title']}** has been cancelled by the host.",
                        color=int(config.colors['error'].replace('#', ''), 16)
                    )
                    await channel.send(embed=embed)
            except:
                pass
            
            return {"success": True, "message": "Giveaway cancelled successfully!"}
            
        except Exception as e:
            logging.error(f"Error cancelling giveaway: {e}")
            return {"success": False, "message": "An error occurred while cancelling the giveaway."}

# Global giveaway system instance (will be initialized with bot client)
giveaway_system = None

def init_giveaway_system(client):
    """Initialize the giveaway system with bot client"""
    global giveaway_system
    giveaway_system = GiveawaySystem(client)
    return giveaway_system