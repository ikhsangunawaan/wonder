import discord
from discord.ext import commands
import asyncio
import logging
import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
import json

from database import database
from config import config

class ProgressiveLevelingSystem:
    """Enhanced leveling system with progressive XP and configurable roles every 5 levels up to level 100"""
    
    def __init__(self, client):
        self.client = client
        self.voice_sessions = {}  # Track active voice sessions
        self.xp_cooldowns = {}  # Text XP cooldowns
        
        # XP Configuration
        self.xp_config = {
            'text': {
                'base': 15,
                'bonus': 10,
                'cooldown': 60000,  # 1 minute cooldown
                'maxPerMessage': 35
            },
            'voice': {
                'base': 10,
                'bonus': 5,
                'minDuration': 60000  # 1 minute minimum
            }
        }
        
        # Progressive XP formula for levels 1-100
        self.max_level = 100
        self.role_interval = 5  # Role every 5 levels
        
    def calculate_xp_needed(self, level: int) -> int:
        """Calculate XP needed to reach a specific level with progressive scaling"""
        if level <= 1:
            return 0
        
        # Progressive formula: Base XP increases significantly with level
        # Level 1-10: 100 * level^1.2
        # Level 11-30: 150 * level^1.3  
        # Level 31-60: 200 * level^1.4
        # Level 61-100: 300 * level^1.5
        
        if level <= 10:
            base_xp = 100
            exponent = 1.2
        elif level <= 30:
            base_xp = 150
            exponent = 1.3
        elif level <= 60:
            base_xp = 200
            exponent = 1.4
        else:
            base_xp = 300
            exponent = 1.5
            
        return math.floor(base_xp * math.pow(level, exponent))
    
    def calculate_total_xp_for_level(self, target_level: int) -> int:
        """Calculate total XP needed to reach a specific level"""
        total_xp = 0
        for level in range(2, target_level + 1):
            total_xp += self.calculate_xp_needed(level)
        return total_xp
    
    def calculate_level_from_xp(self, total_xp: int) -> Tuple[int, int, int]:
        """Calculate current level, current level XP, and XP needed for next level"""
        if total_xp <= 0:
            return 1, 0, self.calculate_xp_needed(2)
        
        current_level = 1
        xp_accumulated = 0
        
        for level in range(2, self.max_level + 1):
            xp_needed = self.calculate_xp_needed(level)
            if xp_accumulated + xp_needed > total_xp:
                break
            xp_accumulated += xp_needed
            current_level = level
        
        if current_level >= self.max_level:
            return self.max_level, total_xp - xp_accumulated, 0
        
        current_level_xp = total_xp - xp_accumulated
        next_level_xp_needed = self.calculate_xp_needed(current_level + 1) - current_level_xp
        
        return current_level, current_level_xp, next_level_xp_needed
    
    def get_role_levels(self) -> List[int]:
        """Get all levels that should have roles (every 5 levels)"""
        return [level for level in range(self.role_interval, self.max_level + 1, self.role_interval)]
    
    def is_role_level(self, level: int) -> bool:
        """Check if a level should have a role"""
        return level > 0 and level % self.role_interval == 0 and level <= self.max_level
    
    async def get_level_role_config(self, guild_id: str, level: int) -> Optional[Dict[str, Any]]:
        """Get role configuration for a specific level"""
        try:
            # Get server settings
            server_settings = await database.get_server_settings(guild_id)
            if not server_settings:
                return None
            
            level_roles = server_settings.get('level_roles', {})
            return level_roles.get(str(level))
            
        except Exception as e:
            logging.error(f"Error getting level role config: {e}")
            return None
    
    async def set_level_role_config(self, guild_id: str, level: int, role_id: str, role_name: str, description: str = None) -> bool:
        """Set role configuration for a specific level"""
        try:
            if not self.is_role_level(level):
                return False
            
            # Get or create server settings
            server_settings = await database.get_server_settings(guild_id)
            if not server_settings:
                server_settings = {
                    'guild_id': guild_id,
                    'level_roles': {},
                    'leveling_enabled': True
                }
            
            # Update level roles configuration
            if 'level_roles' not in server_settings:
                server_settings['level_roles'] = {}
            
            server_settings['level_roles'][str(level)] = {
                'role_id': role_id,
                'role_name': role_name,
                'description': description or f"Level {level} Role",
                'created_at': datetime.now().isoformat()
            }
            
            # Save to database
            await database.save_server_settings(server_settings)
            return True
            
        except Exception as e:
            logging.error(f"Error setting level role config: {e}")
            return False
    
    async def remove_level_role_config(self, guild_id: str, level: int) -> bool:
        """Remove role configuration for a specific level"""
        try:
            server_settings = await database.get_server_settings(guild_id)
            if not server_settings or 'level_roles' not in server_settings:
                return False
            
            if str(level) in server_settings['level_roles']:
                del server_settings['level_roles'][str(level)]
                await database.save_server_settings(server_settings)
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error removing level role config: {e}")
            return False
    
    async def get_all_configured_roles(self, guild_id: str) -> Dict[int, Dict[str, Any]]:
        """Get all configured level roles for a guild"""
        try:
            server_settings = await database.get_server_settings(guild_id)
            if not server_settings or 'level_roles' not in server_settings:
                return {}
            
            # Convert string keys back to integers
            configured_roles = {}
            for level_str, role_data in server_settings['level_roles'].items():
                try:
                    level = int(level_str)
                    configured_roles[level] = role_data
                except ValueError:
                    continue
            
            return configured_roles
            
        except Exception as e:
            logging.error(f"Error getting configured roles: {e}")
            return {}
    
    async def handle_message_xp(self, message: discord.Message) -> Optional[Dict[str, Any]]:
        """Handle XP gain from text messages"""
        try:
            user_id = str(message.author.id)
            guild_id = str(message.guild.id)
            
            # Check cooldown
            current_time = datetime.now()
            cooldown_key = f"{user_id}_{guild_id}_text"
            
            if cooldown_key in self.xp_cooldowns:
                time_diff = (current_time - self.xp_cooldowns[cooldown_key]).total_seconds() * 1000
                if time_diff < self.xp_config['text']['cooldown']:
                    return None
            
            # Update cooldown
            self.xp_cooldowns[cooldown_key] = current_time
            
            # Calculate XP gain
            base_xp = self.xp_config['text']['base']
            bonus_xp = random.randint(0, self.xp_config['text']['bonus'])
            total_xp_gain = base_xp + bonus_xp
            
            # Apply multipliers based on user roles
            multiplier = await self.get_user_multiplier(message.author)
            total_xp_gain = math.floor(total_xp_gain * multiplier)
            
            # Get current user data
            user_data = await database.get_user(user_id)
            if not user_data:
                await database.create_user(user_id, message.author.name)
                user_data = await database.get_user(user_id)
            
            # Get current level data
            level_data = await database.get_user_level(user_id)
            if not level_data:
                # Create initial level data
                current_xp = 0
                current_level = 1
            else:
                current_xp = level_data.get('total_xp', 0)
                current_level, _, _ = self.calculate_level_from_xp(current_xp)
            
            # Add XP
            new_total_xp = current_xp + total_xp_gain
            new_level, current_level_xp, next_level_xp = self.calculate_level_from_xp(new_total_xp)
            
            # Update database
            xp_gain, level_up = await database.update_user_xp(user_id, total_xp_gain)
            
            # Check for role rewards
            role_reward = None
            if new_level > current_level and self.is_role_level(new_level):
                role_config = await self.get_level_role_config(guild_id, new_level)
                if role_config:
                    role_reward = {
                        'level': new_level,
                        'role_id': role_config['role_id'],
                        'role_name': role_config['role_name'],
                        'description': role_config.get('description', f"Level {new_level} Role")
                    }
            
            return {
                'xp_gained': total_xp_gain,
                'total_xp': new_total_xp,
                'old_level': current_level,
                'new_level': new_level,
                'current_level_xp': current_level_xp,
                'next_level_xp_needed': next_level_xp,
                'level_up': new_level > current_level,
                'role_reward': role_reward,
                'multiplier': multiplier
            }
            
        except Exception as e:
            logging.error(f"Error handling message XP: {e}")
            return None
    
    async def get_user_multiplier(self, user: discord.Member) -> float:
        """Get XP multiplier based on user roles"""
        multiplier = 1.0
        
        # Check for premium/booster roles
        for role in user.roles:
            if role.name.lower() in ['premium', 'vip']:
                multiplier += 0.5  # 50% bonus
            elif role.name.lower() in ['booster', 'nitro booster']:
                multiplier += 0.25  # 25% bonus
        
        return multiplier
    
    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get detailed user level progress"""
        try:
            level_data = await database.get_user_level(user_id)
            if not level_data:
                return {
                    'level': 1,
                    'total_xp': 0,
                    'current_level_xp': 0,
                    'next_level_xp_needed': self.calculate_xp_needed(2),
                    'progress_percentage': 0.0,
                    'next_role_level': 5,
                    'levels_to_next_role': 4
                }
            
            total_xp = level_data.get('total_xp', 0)
            current_level, current_level_xp, next_level_xp = self.calculate_level_from_xp(total_xp)
            
            # Calculate progress percentage
            if current_level >= self.max_level:
                progress_percentage = 100.0
            else:
                xp_needed_for_current = self.calculate_xp_needed(current_level + 1)
                progress_percentage = (current_level_xp / xp_needed_for_current) * 100
            
            # Find next role level
            next_role_level = None
            for role_level in self.get_role_levels():
                if role_level > current_level:
                    next_role_level = role_level
                    break
            
            levels_to_next_role = next_role_level - current_level if next_role_level else 0
            
            return {
                'level': current_level,
                'total_xp': total_xp,
                'current_level_xp': current_level_xp,
                'next_level_xp_needed': next_level_xp,
                'progress_percentage': progress_percentage,
                'next_role_level': next_role_level,
                'levels_to_next_role': levels_to_next_role,
                'max_level_reached': current_level >= self.max_level
            }
            
        except Exception as e:
            logging.error(f"Error getting user progress: {e}")
            return {}

# Global instance
progressive_leveling = None

def init_progressive_leveling(client):
    """Initialize the progressive leveling system"""
    global progressive_leveling
    progressive_leveling = ProgressiveLevelingSystem(client)
    return progressive_leveling