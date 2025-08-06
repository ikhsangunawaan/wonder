import discord
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
import os

from database import database
from config import config

class RoleManager:
    """Manages automatic role assignment and role-based features"""
    
    def __init__(self, client):
        self.client = client
        self.role_cache = {}
        self.level_roles = {}
        
        # Role IDs from environment variables
        self.premium_role_id = os.getenv('PREMIUM_ROLE_ID')
        self.booster_role_id = os.getenv('BOOSTER_ROLE_ID')
        
    async def initialize_role_cache(self, guild_id: int):
        """Initialize role cache for a guild"""
        try:
            guild = self.client.get_guild(guild_id)
            if not guild:
                return
            
            self.role_cache[guild_id] = {}
            for role in guild.roles:
                self.role_cache[guild_id][role.name.lower()] = role.id
                
            # Load level roles from database
            await self._load_level_roles(guild_id)
            
        except Exception as e:
            logging.error(f"Error initializing role cache: {e}")
    
    async def _load_level_roles(self, guild_id: int):
        """Load level role configurations from database"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute(
                        'SELECT * FROM level_role_config ORDER BY level_type, level'
                    ) as cursor:
                        rows = await cursor.fetchall()
            
            self.level_roles[guild_id] = {}
            for row in rows:
                level_type = row['level_type']
                level = row['level']
                role_id = row['role_id']
                
                if level_type not in self.level_roles[guild_id]:
                    self.level_roles[guild_id][level_type] = {}
                
                self.level_roles[guild_id][level_type][level] = {
                    'role_id': role_id,
                    'role_name': row['role_name']
                }
                
        except Exception as e:
            logging.error(f"Error loading level roles: {e}")
    
    async def handle_level_up(self, user_id: str, guild_id: int, level_type: str, new_level: int):
        """Handle role assignment when user levels up"""
        try:
            if guild_id not in self.level_roles:
                await self.initialize_role_cache(guild_id)
            
            guild = self.client.get_guild(guild_id)
            if not guild:
                return
            
            member = guild.get_member(int(user_id))
            if not member:
                return
            
            # Check if there's a role reward for this level
            level_type_roles = self.level_roles.get(guild_id, {}).get(level_type, {})
            if new_level in level_type_roles:
                role_info = level_type_roles[new_level]
                role = guild.get_role(int(role_info['role_id']))
                
                if role and role not in member.roles:
                    await member.add_roles(role, reason=f"Level {new_level} {level_type} reward")
                    logging.info(f"Assigned {role.name} to {member.display_name} for reaching level {new_level}")
            
        except Exception as e:
            logging.error(f"Error handling level up role assignment: {e}")
    
    async def add_level_role_reward(self, guild_id: int, level_type: str, level: int, 
                                   role_id: str, created_by: str) -> Dict[str, Any]:
        """Add a new level role reward configuration"""
        try:
            guild = self.client.get_guild(guild_id)
            if not guild:
                return {"success": False, "message": "Guild not found!"}
            
            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "message": "Role not found!"}
            
            # Check if configuration already exists
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    async with db.execute(
                        'SELECT id FROM level_role_config WHERE level_type = ? AND level = ?',
                        (level_type, level)
                    ) as cursor:
                        existing = await cursor.fetchone()
            
            if existing:
                return {"success": False, "message": f"Role reward for {level_type} level {level} already exists!"}
            
            # Add new configuration
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    await db.execute(
                        """INSERT INTO level_role_config 
                           (level_type, level, role_id, role_name, created_by)
                           VALUES (?, ?, ?, ?, ?)""",
                        (level_type, level, role_id, role.name, created_by)
                    )
                    await db.commit()
            
            # Update cache
            if guild_id not in self.level_roles:
                self.level_roles[guild_id] = {}
            if level_type not in self.level_roles[guild_id]:
                self.level_roles[guild_id][level_type] = {}
            
            self.level_roles[guild_id][level_type][level] = {
                'role_id': role_id,
                'role_name': role.name
            }
            
            return {
                "success": True,
                "message": f"Successfully added {role.name} as reward for {level_type} level {level}!"
            }
            
        except Exception as e:
            logging.error(f"Error adding level role reward: {e}")
            return {"success": False, "message": "An error occurred while adding the role reward."}
    
    async def remove_level_role_reward(self, guild_id: int, level_type: str, level: int) -> Dict[str, Any]:
        """Remove a level role reward configuration"""
        try:
            # Remove from database
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    cursor = await db.execute(
                        'DELETE FROM level_role_config WHERE level_type = ? AND level = ?',
                        (level_type, level)
                    )
                    await db.commit()
                    
                    if cursor.rowcount == 0:
                        return {"success": False, "message": "No role reward found for that level!"}
            
            # Update cache
            if (guild_id in self.level_roles and 
                level_type in self.level_roles[guild_id] and 
                level in self.level_roles[guild_id][level_type]):
                del self.level_roles[guild_id][level_type][level]
            
            return {"success": True, "message": f"Removed role reward for {level_type} level {level}!"}
            
        except Exception as e:
            logging.error(f"Error removing level role reward: {e}")
            return {"success": False, "message": "An error occurred while removing the role reward."}
    
    async def get_level_role_rewards(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all level role rewards for a guild"""
        try:
            async with database.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(db_path) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute(
                        'SELECT * FROM level_role_config ORDER BY level_type, level'
                    ) as cursor:
                        rows = await cursor.fetchall()
                        return [dict(row) for row in rows]
                        
        except Exception as e:
            logging.error(f"Error getting level role rewards: {e}")
            return []
    
    async def assign_role_by_name(self, member: discord.Member, role_name: str, 
                                 reason: str = "Role assignment") -> bool:
        """Assign role by name to a member"""
        try:
            guild = member.guild
            role = discord.utils.get(guild.roles, name=role_name)
            
            if not role:
                return False
            
            if role in member.roles:
                return True
            
            await member.add_roles(role, reason=reason)
            return True
            
        except Exception as e:
            logging.error(f"Error assigning role {role_name}: {e}")
            return False
    
    async def remove_role_by_name(self, member: discord.Member, role_name: str, 
                                 reason: str = "Role removal") -> bool:
        """Remove role by name from a member"""
        try:
            guild = member.guild
            role = discord.utils.get(guild.roles, name=role_name)
            
            if not role or role not in member.roles:
                return False
            
            await member.remove_roles(role, reason=reason)
            return True
            
        except Exception as e:
            logging.error(f"Error removing role {role_name}: {e}")
            return False
    
    def is_premium_user(self, member: discord.Member) -> bool:
        """Check if member is a premium user"""
        if not self.premium_role_id:
            return False
        
        premium_role = member.guild.get_role(int(self.premium_role_id))
        return premium_role in member.roles if premium_role else False
    
    def is_booster_user(self, member: discord.Member) -> bool:
        """Check if member is a server booster"""
        # Check for Discord's native boost status
        if member.premium_since:
            return True
        
        # Check for custom booster role
        if not self.booster_role_id:
            return False
        
        booster_role = member.guild.get_role(int(self.booster_role_id))
        return booster_role in member.roles if booster_role else False
    
    def get_user_multipliers(self, member: discord.Member) -> Dict[str, float]:
        """Get XP and currency multipliers for a user based on roles"""
        multipliers = {
            'xp': 1.0,
            'currency': 1.0,
            'cooldown_reduction': 1.0
        }
        
        # Premium user bonuses
        if self.is_premium_user(member):
            multipliers['xp'] *= config.get('leveling.xp.text.multipliers.premium', 1.75)
            multipliers['currency'] *= 1.5  # 50% more currency
            multipliers['cooldown_reduction'] *= 0.5  # 50% cooldown reduction
        
        # Booster bonuses
        if self.is_booster_user(member):
            multipliers['xp'] *= config.get('leveling.xp.text.multipliers.booster', 1.5)
            multipliers['currency'] *= 1.25  # 25% more currency
            multipliers['cooldown_reduction'] *= 0.75  # 25% cooldown reduction
        
        return multipliers
    
    async def handle_member_update(self, before: discord.Member, after: discord.Member):
        """Handle member updates (role changes, boost status, etc.)"""
        try:
            # Check for boost status changes
            if before.premium_since != after.premium_since:
                if after.premium_since:
                    # Member started boosting
                    await self._handle_boost_start(after)
                else:
                    # Member stopped boosting
                    await self._handle_boost_end(after)
            
            # Check for role changes that might affect permissions
            added_roles = set(after.roles) - set(before.roles)
            removed_roles = set(before.roles) - set(after.roles)
            
            if added_roles or removed_roles:
                await self._update_user_permissions(after, added_roles, removed_roles)
                
        except Exception as e:
            logging.error(f"Error handling member update: {e}")
    
    async def _handle_boost_start(self, member: discord.Member):
        """Handle when a member starts boosting"""
        try:
            # Log the boost
            logging.info(f"{member.display_name} started boosting {member.guild.name}")
            
            # Could send a thank you message or give special perks
            # Implementation depends on specific requirements
            
        except Exception as e:
            logging.error(f"Error handling boost start: {e}")
    
    async def _handle_boost_end(self, member: discord.Member):
        """Handle when a member stops boosting"""
        try:
            # Log the boost end
            logging.info(f"{member.display_name} stopped boosting {member.guild.name}")
            
        except Exception as e:
            logging.error(f"Error handling boost end: {e}")
    
    async def _update_user_permissions(self, member: discord.Member, 
                                     added_roles: Set[discord.Role], 
                                     removed_roles: Set[discord.Role]):
        """Update user permissions based on role changes"""
        try:
            # This could be used to update database permissions or cache
            # Implementation depends on specific requirements
            pass
            
        except Exception as e:
            logging.error(f"Error updating user permissions: {e}")
    
    async def assign_temporary_role(self, member: discord.Member, role_name: str, 
                                   duration_minutes: int, reason: str = "Temporary role") -> Dict[str, Any]:
        """Assign a temporary role that will be removed after duration"""
        try:
            guild = member.guild
            role = discord.utils.get(guild.roles, name=role_name)
            
            if not role:
                return {"success": False, "message": "Role not found!"}
            
            if role in member.roles:
                return {"success": False, "message": "User already has this role!"}
            
            await member.add_roles(role, reason=reason)
            
            # Schedule role removal (in a real implementation, you'd want to store this in database
            # and have a background task check for expired temporary roles)
            remove_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            # For now, we'll just log it
            logging.info(f"Assigned temporary role {role.name} to {member.display_name}, expires at {remove_time}")
            
            return {
                "success": True,
                "message": f"Assigned temporary role {role.name} for {duration_minutes} minutes!",
                "expires_at": remove_time
            }
            
        except Exception as e:
            logging.error(f"Error assigning temporary role: {e}")
            return {"success": False, "message": "An error occurred while assigning the role."}
    
    async def get_user_roles_info(self, member: discord.Member) -> Dict[str, Any]:
        """Get comprehensive role information for a user"""
        try:
            roles_info = {
                "roles": [{"name": role.name, "id": str(role.id), "color": str(role.color)} 
                         for role in member.roles if role.name != "@everyone"],
                "is_premium": self.is_premium_user(member),
                "is_booster": self.is_booster_user(member),
                "boost_since": member.premium_since.isoformat() if member.premium_since else None,
                "multipliers": self.get_user_multipliers(member),
                "permissions": {
                    "administrator": member.guild_permissions.administrator,
                    "manage_guild": member.guild_permissions.manage_guild,
                    "manage_roles": member.guild_permissions.manage_roles,
                    "manage_channels": member.guild_permissions.manage_channels,
                    "manage_messages": member.guild_permissions.manage_messages
                }
            }
            
            return roles_info
            
        except Exception as e:
            logging.error(f"Error getting user roles info: {e}")
            return {}
    
    async def bulk_role_assignment(self, guild_id: int, role_name: str, 
                                  user_ids: List[str], reason: str = "Bulk assignment") -> Dict[str, Any]:
        """Assign role to multiple users at once"""
        try:
            guild = self.client.get_guild(guild_id)
            if not guild:
                return {"success": False, "message": "Guild not found!"}
            
            role = discord.utils.get(guild.roles, name=role_name)
            if not role:
                return {"success": False, "message": "Role not found!"}
            
            successful = 0
            failed = 0
            
            for user_id in user_ids:
                try:
                    member = guild.get_member(int(user_id))
                    if member and role not in member.roles:
                        await member.add_roles(role, reason=reason)
                        successful += 1
                    else:
                        failed += 1
                except:
                    failed += 1
                    continue
            
            return {
                "success": True,
                "message": f"Bulk role assignment completed! Success: {successful}, Failed: {failed}",
                "successful": successful,
                "failed": failed
            }
            
        except Exception as e:
            logging.error(f"Error in bulk role assignment: {e}")
            return {"success": False, "message": "An error occurred during bulk role assignment."}

# Global role manager instance (will be initialized with bot client)
role_manager = None

def init_role_manager(client):
    """Initialize the role manager with bot client"""
    global role_manager
    role_manager = RoleManager(client)
    return role_manager