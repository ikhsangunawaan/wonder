import discord
from discord.ext import tasks, commands
import asyncio
import logging
import random
import json
import aiosqlite
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from database import database
from config import config

class AdvancedGiveawaySystem:
    """Advanced Giveaway System with comprehensive features"""
    
    def __init__(self, client):
        self.client = client
        self.active_giveaways = {}
        self.check_giveaways.start()
    
    async def create_giveaway(self, 
                            ctx: commands.Context,
                            prize: str,
                            duration: str,
                            winners: int = 1,
                            channel: discord.TextChannel = None,
                            required_roles: List[discord.Role] = None,
                            forbidden_roles: List[discord.Role] = None,
                            winner_role: discord.Role = None,
                            min_messages: int = 0,
                            min_account_age: int = 0,
                            bypass_roles: List[discord.Role] = None,
                            description: str = None) -> Dict[str, Any]:
        """Create an advanced giveaway with comprehensive options"""
        try:
            # Parse duration
            duration_minutes = self._parse_duration(duration)
            if duration_minutes is None:
                return {
                    "success": False,
                    "message": "❌ Invalid duration format! Use formats like: 1h, 30m, 2d, 1w"
                }
            
            # Validate duration limits
            max_duration = config.get('giveaways.maxDuration', 10080)  # 7 days default
            if duration_minutes > max_duration:
                return {
                    "success": False,
                    "message": f"❌ Giveaway duration cannot exceed {max_duration} minutes ({max_duration//1440} days)!"
                }
            
            # Validate winners count
            max_winners = config.get('giveaways.maxWinners', 10)
            if winners > max_winners:
                return {
                    "success": False,
                    "message": f"❌ Maximum {max_winners} winners allowed!"
                }
            
            if winners < 1:
                return {
                    "success": False,
                    "message": "❌ Must have at least 1 winner!"
                }
            
            # Use current channel if none specified
            if channel is None:
                channel = ctx.channel
            
            # Check permissions
            if not channel.permissions_for(ctx.guild.me).send_messages:
                return {
                    "success": False,
                    "message": f"❌ I don't have permission to send messages in {channel.mention}!"
                }
            
            # Calculate end time
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            # Prepare role data for storage
            required_roles_data = [str(role.id) for role in required_roles] if required_roles else []
            forbidden_roles_data = [str(role.id) for role in forbidden_roles] if forbidden_roles else []
            bypass_roles_data = [str(role.id) for role in bypass_roles] if bypass_roles else []
            
            # Create giveaway embed
            embed = self._create_giveaway_embed(
                prize, description or f"React with 🎉 to enter!",
                end_time, winners, ctx.author,
                required_roles, forbidden_roles, min_messages, min_account_age
            )
            
            # Send giveaway message
            message = await channel.send(embed=embed)
            await message.add_reaction("🎉")
            
            # Save to database
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
                cursor = await db.execute(
                    """INSERT INTO giveaways 
                       (message_id, channel_id, guild_id, host_id, title, description, 
                        winners_count, end_time, prize, required_roles, forbidden_roles,
                        winner_role_id, min_messages, min_account_age_days, bypass_roles, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (str(message.id), str(channel.id), str(ctx.guild.id), str(ctx.author.id),
                     f"🎉 {prize}", description or f"React with 🎉 to enter!",
                     winners, end_time.isoformat(), prize,
                     json.dumps(required_roles_data), json.dumps(forbidden_roles_data),
                     str(winner_role.id) if winner_role else None,
                     min_messages, min_account_age, json.dumps(bypass_roles_data), 'active')
                )
                await db.commit()
                giveaway_id = cursor.lastrowid
            
            # Store in memory for tracking
            self.active_giveaways[str(message.id)] = {
                'id': giveaway_id,
                'end_time': end_time,
                'guild_id': str(ctx.guild.id),
                'channel_id': str(channel.id),
                'message_id': str(message.id)
            }
            
            return {
                "success": True,
                "message": f"🎉 **Giveaway Created Successfully!**\n\n"
                          f"**Prize:** {prize}\n"
                          f"**Winners:** {winners}\n"
                          f"**Channel:** {channel.mention}\n"
                          f"**Ends:** {discord.utils.format_dt(end_time, 'R')}\n"
                          f"**Giveaway ID:** `{giveaway_id}`",
                "giveaway_id": giveaway_id,
                "message_id": str(message.id)
            }
            
        except Exception as e:
            logging.error(f"Error creating giveaway: {e}")
            return {"success": False, "message": "❌ An error occurred while creating the giveaway."}
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string into minutes"""
        duration_str = duration_str.lower().strip()
        
        # Duration mapping
        multipliers = {
            's': 1/60,    # seconds to minutes
            'm': 1,       # minutes
            'h': 60,      # hours to minutes
            'd': 1440,    # days to minutes
            'w': 10080    # weeks to minutes
        }
        
        # Extract number and unit
        import re
        match = re.match(r'^(\d+)([smhdw])$', duration_str)
        if not match:
            return None
        
        amount, unit = match.groups()
        return int(amount) * multipliers[unit]
    
    def _create_giveaway_embed(self, prize: str, description: str, end_time: datetime,
                              winners_count: int, host: discord.Member,
                              required_roles: List[discord.Role] = None,
                              forbidden_roles: List[discord.Role] = None,
                              min_messages: int = 0,
                              min_account_age: int = 0) -> discord.Embed:
        """Create advanced giveaway embed"""
        embed = discord.Embed(
            title=f"🎉 {prize}",
            description=description,
            color=int(config.colors['primary'].replace('#', ''), 16)
        )
        
        embed.add_field(
            name="🏆 Prize",
            value=f"```{prize}```",
            inline=True
        )
        
        embed.add_field(
            name="👥 Winners",
            value=f"```{winners_count} winner{'s' if winners_count > 1 else ''}```",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Ends",
            value=f"{discord.utils.format_dt(end_time, 'R')}\n{discord.utils.format_dt(end_time, 'F')}",
            inline=True
        )
        
        # Requirements section
        requirements = []
        if min_account_age > 0:
            requirements.append(f"📅 Account age: {min_account_age} days")
        if min_messages > 0:
            requirements.append(f"💬 Messages sent: {min_messages}")
        if required_roles:
            role_mentions = [role.mention for role in required_roles[:3]]
            if len(required_roles) > 3:
                role_mentions.append(f"and {len(required_roles) - 3} more...")
            requirements.append(f"✅ Required roles: {', '.join(role_mentions)}")
        if forbidden_roles:
            role_mentions = [role.mention for role in forbidden_roles[:3]]
            if len(forbidden_roles) > 3:
                role_mentions.append(f"and {len(forbidden_roles) - 3} more...")
            requirements.append(f"❌ Cannot have roles: {', '.join(role_mentions)}")
        
        if requirements:
            embed.add_field(
                name="📋 Requirements",
                value="\n".join(requirements),
                inline=False
            )
        
        embed.add_field(
            name="📝 How to Enter",
            value="React with 🎉 to enter the giveaway!",
            inline=False
        )
        
        embed.set_footer(
            text=f"Hosted by {host.display_name}",
            icon_url=host.display_avatar.url
        )
        embed.timestamp = datetime.now()
        
        return embed
    
    async def end_giveaway(self, giveaway_id: int, user_id: str) -> Dict[str, Any]:
        """Manually end a giveaway"""
        try:
            giveaway = await self._get_giveaway_by_id(giveaway_id)
            if not giveaway:
                return {"success": False, "message": "❌ Giveaway not found!"}
            
            if giveaway['status'] != 'active':
                return {"success": False, "message": "❌ This giveaway is not active!"}
            
            # Check permissions (host or admin)
            guild = self.client.get_guild(int(giveaway['guild_id']))
            member = guild.get_member(int(user_id)) if guild else None
            
            if not member:
                return {"success": False, "message": "❌ You're not in this server!"}
            
            is_host = giveaway['host_id'] == user_id
            is_admin = member.guild_permissions.administrator
            is_manage_guild = member.guild_permissions.manage_guild
            
            if not (is_host or is_admin or is_manage_guild):
                return {"success": False, "message": "❌ You can only end your own giveaways or need admin permissions!"}
            
            # End the giveaway
            await self._end_giveaway(giveaway, manual=True)
            
            return {"success": True, "message": f"✅ Giveaway **{giveaway['prize']}** has been ended manually!"}
            
        except Exception as e:
            logging.error(f"Error ending giveaway: {e}")
            return {"success": False, "message": "❌ An error occurred while ending the giveaway."}
    
    async def reroll_giveaway(self, giveaway_id: int, user_id: str, 
                             new_winner_count: Optional[int] = None) -> Dict[str, Any]:
        """Reroll winners for a completed giveaway"""
        try:
            giveaway = await self._get_giveaway_by_id(giveaway_id)
            if not giveaway:
                return {"success": False, "message": "❌ Giveaway not found!"}
            
            if giveaway['status'] != 'completed':
                return {"success": False, "message": "❌ Can only reroll completed giveaways!"}
            
            # Check permissions
            guild = self.client.get_guild(int(giveaway['guild_id']))
            member = guild.get_member(int(user_id)) if guild else None
            
            if not member:
                return {"success": False, "message": "❌ You're not in this server!"}
            
            is_host = giveaway['host_id'] == user_id
            is_admin = member.guild_permissions.administrator
            is_manage_guild = member.guild_permissions.manage_guild
            
            if not (is_host or is_admin or is_manage_guild):
                return {"success": False, "message": "❌ You can only reroll your own giveaways or need admin permissions!"}
            
            # Get all entries
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM giveaway_entries WHERE giveaway_id = ?',
                    (giveaway_id,)
                ) as cursor:
                    entries = await cursor.fetchall()
            
            if not entries:
                return {"success": False, "message": "❌ No entries found for this giveaway!"}
            
            # Use new winner count or original
            winners_count = new_winner_count if new_winner_count is not None else giveaway['winners_count']
            max_winners = config.get('giveaways.maxWinners', 10)
            
            if winners_count > max_winners:
                return {"success": False, "message": f"❌ Maximum {max_winners} winners allowed!"}
            
            # Get previous winners to exclude them
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT user_id FROM giveaway_winners WHERE giveaway_id = ?',
                    (giveaway_id,)
                ) as cursor:
                    previous_winners = [row['user_id'] for row in await cursor.fetchall()]
            
            # Select new winners (excluding previous ones)
            available_entries = [entry for entry in entries if entry['user_id'] not in previous_winners]
            
            if not available_entries:
                return {"success": False, "message": "❌ No new participants available for reroll!"}
            
            new_winners = await self._select_winners(available_entries, winners_count)
            
            if not new_winners:
                return {"success": False, "message": "❌ Could not select new winners!"}
            
            # Store new winners
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
                for i, winner_id in enumerate(new_winners):
                    await db.execute(
                        """INSERT INTO giveaway_winners 
                           (giveaway_id, user_id, winner_position, is_reroll) 
                           VALUES (?, ?, ?, ?)""",
                        (giveaway_id, winner_id, i + 1, True)
                    )
                
                # Update reroll count
                await db.execute(
                    'UPDATE giveaways SET reroll_count = reroll_count + 1 WHERE id = ?',
                    (giveaway_id,)
                )
                await db.commit()
            
            # Announce reroll
            await self._announce_reroll(giveaway, new_winners)
            
            return {
                "success": True,
                "message": f"🎲 **Giveaway Rerolled!**\n\n"
                          f"**New Winners:** {len(new_winners)}\n"
                          f"**Prize:** {giveaway['prize']}"
            }
            
        except Exception as e:
            logging.error(f"Error rerolling giveaway: {e}")
            return {"success": False, "message": "❌ An error occurred while rerolling the giveaway."}
    
    async def list_giveaways(self, guild_id: str, show_all: bool = False) -> Dict[str, Any]:
        """List giveaways for a guild"""
        try:
            status_filter = None if show_all else 'active'
            
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
                db.row_factory = aiosqlite.Row
                query = 'SELECT * FROM giveaways WHERE guild_id = ?'
                params = [guild_id]
                
                if status_filter:
                    query += ' AND status = ?'
                    params.append(status_filter)
                
                query += ' ORDER BY created_at DESC LIMIT 10'
                
                async with db.execute(query, params) as cursor:
                    giveaways = await cursor.fetchall()
            
            if not giveaways:
                status_text = "active" if status_filter else "any"
                return {
                    "success": False,
                    "message": f"❌ No {status_text} giveaways found for this server!"
                }
            
            # Format giveaway list
            embed = discord.Embed(
                title="🎉 Giveaway List",
                color=int(config.colors['primary'].replace('#', ''), 16)
            )
            
            for giveaway in giveaways:
                status_emoji = {
                    'active': '🟢',
                    'completed': '✅',
                    'cancelled': '❌'
                }.get(giveaway['status'], '❓')
                
                end_time = datetime.fromisoformat(giveaway['end_time'])
                
                field_value = (
                    f"**Prize:** {giveaway['prize']}\n"
                    f"**Winners:** {giveaway['winners_count']}\n"
                    f"**Status:** {status_emoji} {giveaway['status'].title()}\n"
                    f"**Ends:** {discord.utils.format_dt(end_time, 'R')}\n"
                    f"**Channel:** <#{giveaway['channel_id']}>"
                )
                
                if giveaway['reroll_count'] > 0:
                    field_value += f"\n**Rerolls:** {giveaway['reroll_count']}"
                
                embed.add_field(
                    name=f"🎁 Giveaway #{giveaway['id']}",
                    value=field_value,
                    inline=True
                )
            
            embed.set_footer(text=f"Showing {len(giveaways)} giveaway(s)")
            
            return {
                "success": True,
                "embed": embed
            }
            
        except Exception as e:
            logging.error(f"Error listing giveaways: {e}")
            return {"success": False, "message": "❌ An error occurred while listing giveaways."}

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
        check_result = await self._check_entry_requirements(user, giveaway)
        if not check_result['allowed']:
            try:
                embed = discord.Embed(
                    title="❌ Entry Denied",
                    description=check_result['reason'],
                    color=int(config.colors['error'].replace('#', ''), 16)
                )
                await user.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            # Remove the reaction
            try:
                await reaction.remove(user)
            except:
                pass
            return
        
        # Add entry to database
        await self._add_giveaway_entry(giveaway['id'], str(user.id))
        
        # Send confirmation DM
        try:
            embed = discord.Embed(
                title="✅ Successfully Entered!",
                description=f"You've entered the giveaway for **{giveaway['prize']}**!",
                color=int(config.colors['success'].replace('#', ''), 16)
            )
            embed.add_field(
                name="🎁 Prize",
                value=giveaway['prize'],
                inline=True
            )
            embed.add_field(
                name="⏰ Ends",
                value=discord.utils.format_dt(datetime.fromisoformat(giveaway['end_time']), 'R'),
                inline=True
            )
            await user.send(embed=embed)
        except:
            pass
    
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
    
    async def _get_giveaway_by_id(self, giveaway_id: int) -> Optional[Dict[str, Any]]:
        """Get giveaway by ID"""
        import aiosqlite
        async with aiosqlite.connect(database.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM giveaways WHERE id = ?', (giveaway_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def _check_entry_requirements(self, user: discord.User, giveaway: Dict[str, Any]) -> Dict[str, Any]:
        """Check if user meets all giveaway entry requirements"""
        try:
            guild = self.client.get_guild(int(giveaway['guild_id']))
            if not guild:
                return {"allowed": False, "reason": "Server not found!"}
            
            member = guild.get_member(user.id)
            if not member:
                return {"allowed": False, "reason": "You must be a member of this server!"}
            
            # Check bypass roles first
            if giveaway.get('bypass_roles'):
                bypass_role_ids = json.loads(giveaway['bypass_roles'])
                if any(str(role.id) in bypass_role_ids for role in member.roles):
                    return {"allowed": True, "reason": "Bypass role detected"}
            
            # Check account age requirement
            if giveaway.get('min_account_age_days', 0) > 0:
                account_age = (datetime.now() - user.created_at).days
                if account_age < giveaway['min_account_age_days']:
                    return {
                        "allowed": False,
                        "reason": f"Your account must be at least {giveaway['min_account_age_days']} days old! "
                                f"(Currently {account_age} days)"
                    }
            
            # Check message requirement
            if giveaway.get('min_messages', 0) > 0:
                # This would require a message tracking system
                # For now, we'll skip this check
                pass
            
            # Check required roles
            if giveaway.get('required_roles'):
                required_role_ids = json.loads(giveaway['required_roles'])
                member_role_ids = [str(role.id) for role in member.roles]
                
                if not any(role_id in member_role_ids for role_id in required_role_ids):
                    role_names = []
                    for role_id in required_role_ids:
                        role = guild.get_role(int(role_id))
                        if role:
                            role_names.append(role.name)
                    
                    return {
                        "allowed": False,
                        "reason": f"You need one of these roles: {', '.join(role_names)}"
                    }
            
            # Check forbidden roles
            if giveaway.get('forbidden_roles'):
                forbidden_role_ids = json.loads(giveaway['forbidden_roles'])
                member_role_ids = [str(role.id) for role in member.roles]
                
                forbidden_roles_found = []
                for role_id in forbidden_role_ids:
                    if role_id in member_role_ids:
                        role = guild.get_role(int(role_id))
                        if role:
                            forbidden_roles_found.append(role.name)
                
                if forbidden_roles_found:
                    return {
                        "allowed": False,
                        "reason": f"You cannot have these roles: {', '.join(forbidden_roles_found)}"
                    }
            
            # Check winner cooldown
            winner_cooldown = config.get('giveaways.winnerCooldown', 10080)  # 7 days
            if await self._user_recently_won(str(user.id), winner_cooldown):
                # Premium users can bypass this
                premium_bypass = config.get('giveaways.restrictions.premiumBypass', True)
                if not premium_bypass or not member.premium_since:
                    return {
                        "allowed": False,
                        "reason": f"You've won a giveaway recently! Please wait before entering another."
                    }
            
            return {"allowed": True, "reason": "All requirements met"}
            
        except Exception as e:
            logging.error(f"Error checking entry requirements: {e}")
            return {"allowed": False, "reason": "Error checking requirements"}
    
    async def _user_recently_won(self, user_id: str, cooldown_minutes: int) -> bool:
        """Check if user recently won a giveaway"""
        cutoff_time = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        import aiosqlite
        async with aiosqlite.connect(database.db_path) as db:
            async with db.execute(
                """SELECT COUNT(*) FROM giveaway_winners gw
                   JOIN giveaways g ON gw.giveaway_id = g.id
                   WHERE gw.user_id = ? AND g.ended_at > ?""",
                (user_id, cutoff_time.isoformat())
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] > 0 if row else False
    
    async def _add_giveaway_entry(self, giveaway_id: int, user_id: str):
        """Add user entry to giveaway"""
        try:
            # Calculate entry weight based on user roles
            entries = await self._calculate_entry_weight(user_id, giveaway_id)
            
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
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
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
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
    
    @tasks.loop(minutes=1)
    async def check_giveaways(self):
        """Check for ended giveaways and process them"""
        try:
            now = datetime.now()
            
            # Get all active giveaways that have ended
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
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
    
    async def _end_giveaway(self, giveaway: Dict[str, Any], manual: bool = False):
        """End a giveaway and select winners"""
        try:
            giveaway_id = giveaway['id']
            
            # Get all entries
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    'SELECT * FROM giveaway_entries WHERE giveaway_id = ?',
                    (giveaway_id,)
                ) as cursor:
                    entries = await cursor.fetchall()
            
            if not entries:
                # No entries - announce no winners
                await self._announce_no_winners(giveaway, manual)
                await self._mark_giveaway_completed(giveaway_id)
                return
            
            # Select winners
            winners = await self._select_winners(entries, giveaway['winners_count'])
            
            # Store winners in database
            import aiosqlite
            async with aiosqlite.connect(database.db_path) as db:
                for i, winner_id in enumerate(winners):
                    await db.execute(
                        """INSERT INTO giveaway_winners 
                           (giveaway_id, user_id, winner_position) 
                           VALUES (?, ?, ?)""",
                        (giveaway_id, winner_id, i + 1)
                    )
                await db.commit()
            
            # Assign winner role if specified
            if giveaway.get('winner_role_id'):
                await self._assign_winner_roles(giveaway, winners)
            
            # Announce winners
            await self._announce_winners(giveaway, winners, manual)
            
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
    
    async def _assign_winner_roles(self, giveaway: Dict[str, Any], winners: List[str]):
        """Assign winner role to winners"""
        try:
            guild = self.client.get_guild(int(giveaway['guild_id']))
            if not guild:
                return
            
            winner_role = guild.get_role(int(giveaway['winner_role_id']))
            if not winner_role:
                return
            
            for winner_id in winners:
                try:
                    member = guild.get_member(int(winner_id))
                    if member and winner_role not in member.roles:
                        await member.add_roles(winner_role, reason=f"Won giveaway: {giveaway['prize']}")
                except Exception as e:
                    logging.error(f"Error assigning winner role to {winner_id}: {e}")
                    
        except Exception as e:
            logging.error(f"Error assigning winner roles: {e}")
    
    async def _announce_winners(self, giveaway: Dict[str, Any], winners: List[str], manual: bool = False):
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
                description=f"**{giveaway['prize']}**",
                color=int(config.colors['success'].replace('#', ''), 16)
            )
            
            embed.add_field(
                name="🏆 Prize",
                value=f"```{giveaway['prize']}```",
                inline=True
            )
            
            if winners:
                winner_mentions = [f"<@{winner}>" for winner in winners]
                embed.add_field(
                    name="🎊 Winners",
                    value="\n".join(winner_mentions),
                    inline=False
                )
                
                embed.add_field(
                    name="🎁 Congratulations!",
                    value=f"You have won **{giveaway['prize']}**!\nPlease contact the host for your prize.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="😔 No Winners",
                    value="No valid entries were found.",
                    inline=False
                )
            
            if manual:
                embed.add_field(
                    name="ℹ️ Note",
                    value="This giveaway was ended manually by an administrator.",
                    inline=False
                )
            
            embed.timestamp = datetime.now()
            embed.set_footer(text=f"Giveaway ID: {giveaway['id']}")
            
            # Send announcement
            content = " ".join([f"<@{winner}>" for winner in winners]) if winners else None
            await channel.send(content=content, embed=embed)
            
            # Update original message if possible
            if message:
                try:
                    updated_embed = message.embeds[0] if message.embeds else None
                    if updated_embed:
                        updated_embed.color = int(config.colors['success'].replace('#', ''), 16)
                        updated_embed.title = f"🎉 {giveaway['prize']} (ENDED)"
                        updated_embed.add_field(
                            name="🏆 Winners",
                            value="\n".join([f"<@{winner}>" for winner in winners]) if winners else "No winners",
                            inline=False
                        )
                        await message.edit(embed=updated_embed)
                except Exception as e:
                    logging.error(f"Error updating original message: {e}")
            
            # Send DM to winners
            for winner_id in winners:
                try:
                    user = await self.client.fetch_user(int(winner_id))
                    if user:
                        dm_embed = discord.Embed(
                            title="🎉 Congratulations!",
                            description=f"You won the giveaway for **{giveaway['prize']}**!",
                            color=int(config.colors['success'].replace('#', ''), 16)
                        )
                        dm_embed.add_field(name="🏆 Prize", value=giveaway['prize'], inline=False)
                        dm_embed.add_field(
                            name="📬 Next Steps",
                            value="Please contact the giveaway host to claim your prize!",
                            inline=False
                        )
                        await user.send(embed=dm_embed)
                except Exception as e:
                    logging.error(f"Error sending DM to winner {winner_id}: {e}")
                    
        except Exception as e:
            logging.error(f"Error announcing winners: {e}")
    
    async def _announce_reroll(self, giveaway: Dict[str, Any], new_winners: List[str]):
        """Announce giveaway reroll"""
        try:
            channel = self.client.get_channel(int(giveaway['channel_id']))
            if not channel:
                return
            
            embed = discord.Embed(
                title="🎲 Giveaway Rerolled!",
                description=f"**{giveaway['prize']}**",
                color=int(config.colors['primary'].replace('#', ''), 16)
            )
            
            embed.add_field(
                name="🏆 Prize",
                value=f"```{giveaway['prize']}```",
                inline=True
            )
            
            if new_winners:
                winner_mentions = [f"<@{winner}>" for winner in new_winners]
                embed.add_field(
                    name="🎊 New Winners",
                    value="\n".join(winner_mentions),
                    inline=False
                )
                
                embed.add_field(
                    name="🎁 Congratulations!",
                    value=f"You are the new winner{'s' if len(new_winners) > 1 else ''} of **{giveaway['prize']}**!",
                    inline=False
                )
            
            embed.timestamp = datetime.now()
            embed.set_footer(text=f"Giveaway ID: {giveaway['id']} | Reroll")
            
            # Send announcement
            content = " ".join([f"<@{winner}>" for winner in new_winners]) if new_winners else None
            await channel.send(content=content, embed=embed)
            
            # Assign winner role if specified
            if giveaway.get('winner_role_id'):
                await self._assign_winner_roles(giveaway, new_winners)
            
            # Send DM to new winners
            for winner_id in new_winners:
                try:
                    user = await self.client.fetch_user(int(winner_id))
                    if user:
                        dm_embed = discord.Embed(
                            title="🎲 You're a Reroll Winner!",
                            description=f"You won the rerolled giveaway for **{giveaway['prize']}**!",
                            color=int(config.colors['success'].replace('#', ''), 16)
                        )
                        dm_embed.add_field(name="🏆 Prize", value=giveaway['prize'], inline=False)
                        await user.send(embed=dm_embed)
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"Error announcing reroll: {e}")
    
    async def _announce_no_winners(self, giveaway: Dict[str, Any], manual: bool = False):
        """Announce that giveaway had no winners"""
        try:
            channel = self.client.get_channel(int(giveaway['channel_id']))
            if not channel:
                return
            
            embed = discord.Embed(
                title="😔 Giveaway Ended - No Winners",
                description=f"**{giveaway['prize']}** ended with no entries.",
                color=int(config.colors['warning'].replace('#', ''), 16)
            )
            
            embed.add_field(
                name="🏆 Prize",
                value=f"```{giveaway['prize']}```",
                inline=True
            )
            
            if manual:
                embed.add_field(
                    name="ℹ️ Note",
                    value="This giveaway was ended manually by an administrator.",
                    inline=False
                )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Error announcing no winners: {e}")
    
    async def _mark_giveaway_completed(self, giveaway_id: int):
        """Mark giveaway as completed in database"""
        import aiosqlite
        async with aiosqlite.connect(database.db_path) as db:
            await db.execute(
                'UPDATE giveaways SET status = ?, ended_at = ? WHERE id = ?',
                ('completed', datetime.now().isoformat(), giveaway_id)
            )
            await db.commit()

# Global giveaway system instance (will be initialized with bot client)
giveaway_system = None

def init_giveaway_system(client):
    """Initialize the advanced giveaway system with bot client"""
    global giveaway_system
    giveaway_system = AdvancedGiveawaySystem(client)
    return giveaway_system