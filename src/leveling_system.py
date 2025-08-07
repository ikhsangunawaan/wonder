import discord
import asyncio
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
import random

from database import database
from config import config

class LevelingSystem:
    """Manages user leveling and XP system"""
    
    def __init__(self, client):
        self.client = client
        self.voice_sessions = {}  # Track active voice sessions
        self.xp_cooldowns = {}  # Text XP cooldowns
        
        # XP Configuration from config or defaults
        self.xp_config = {
            'text': {
                'base': config.get('leveling.xp.text.base', 15),
                'bonus': config.get('leveling.xp.text.bonus', 5),
                'cooldown': config.get('leveling.xp.text.cooldown', 60000),  # milliseconds
                'maxPerMessage': config.get('leveling.xp.text.maxPerMessage', 25),
                'multipliers': config.get('leveling.xp.text.multipliers', {})
            },
            'voice': {
                'base': config.get('leveling.xp.voice.base', 10),
                'bonus': config.get('leveling.xp.voice.bonus', 5),
                'minDuration': config.get('leveling.xp.voice.minDuration', 60000),
                'multipliers': config.get('leveling.xp.voice.multipliers', {})
            },
            'role': {
                'dailyLogin': config.get('leveling.xp.role.dailyLogin', 50),
                'messageStreak': config.get('leveling.xp.role.messageStreak', 25),
                'voiceStreak': config.get('leveling.xp.role.voiceStreak', 30),
                'helpingOthers': config.get('leveling.xp.role.helpingOthers', 100),
                'eventParticipation': config.get('leveling.xp.role.eventParticipation', 200),
                'multipliers': config.get('leveling.xp.role.multipliers', {})
            }
        }
        
        # Level calculation formula: XP needed = 100 * level^1.5, capped at level 50
        self.level_formula = {
            'calculateXPNeeded': lambda level: math.floor(100 * math.pow(level, 1.5)),
            'calculateLevel': lambda xp: min(math.floor(math.pow(xp / 100, 1 / 1.5)), 50),
            'maxLevel': config.get('leveling.maxLevel', 50)
        }
        
        # Comprehensive role system
        self.level_roles = config.get('leveling.levelRoles', {})
        self.prestige_system = config.get('leveling.prestigeSystem', {})
        
        # Level rewards configuration
        self.level_rewards = {
            'text': {
                5: {'type': 'currency', 'amount': 500, 'message': 'Chatty Beginner Bonus!'},
                10: {'type': 'currency', 'amount': 1000, 'message': 'Active Chatter Reward!'},
                20: {'type': 'currency', 'amount': 2000, 'message': 'Text Master Bonus!'},
                25: {'type': 'title', 'title': 'Text Master', 'message': 'You can now use the Text Master title!'},
                30: {'type': 'currency', 'amount': 5000, 'message': 'Legendary Chatter Reward!'},
                35: {'type': 'currency', 'amount': 7500, 'message': 'Text Elite Bonus!'},
                40: {'type': 'currency', 'amount': 10000, 'message': 'Text Supreme Reward!'},
                45: {'type': 'currency', 'amount': 15000, 'message': 'Text Grandmaster Bonus!'},
                50: {'type': 'currency', 'amount': 25000, 'message': 'MAX LEVEL ACHIEVED! Text Legend!'}
            },
            'voice': {
                5: {'type': 'currency', 'amount': 750, 'message': 'Voice Newbie Bonus!'},
                10: {'type': 'currency', 'amount': 1500, 'message': 'Social Speaker Reward!'},
                20: {'type': 'currency', 'amount': 3000, 'message': 'Voice Champion Bonus!'},
                25: {'type': 'title', 'title': 'Voice Champion', 'message': 'You can now use the Voice Champion title!'},
                30: {'type': 'currency', 'amount': 7500, 'message': 'Voice Legend Reward!'},
                35: {'type': 'currency', 'amount': 10000, 'message': 'Voice Elite Bonus!'},
                40: {'type': 'currency', 'amount': 15000, 'message': 'Voice Supreme Reward!'},
                45: {'type': 'currency', 'amount': 20000, 'message': 'Voice Grandmaster Bonus!'},
                50: {'type': 'currency', 'amount': 35000, 'message': 'MAX LEVEL ACHIEVED! Voice Legend!'}
            },
            'overall': {
                10: {'type': 'currency', 'amount': 2000, 'message': 'Rising Star Bonus!'},
                30: {'type': 'currency', 'amount': 10000, 'message': 'Server Veteran Reward!'},
                35: {'type': 'currency', 'amount': 15000, 'message': 'Elite Member Bonus!'},
                40: {'type': 'currency', 'amount': 25000, 'message': 'Supreme Member Reward!'},
                45: {'type': 'title', 'title': 'Server Grandmaster', 'message': 'You can now use the Server Grandmaster title!'},
                50: {'type': 'currency', 'amount': 100000, 'message': 'MAX LEVEL ACHIEVED! ULTIMATE LEGEND STATUS!'}
            }
        }
    
    def get_xp_for_level(self, level: int) -> int:
        """Calculate XP needed for a specific level"""
        return self.level_formula['calculateXPNeeded'](level)
    
    def get_level_from_xp(self, xp: int) -> int:
        """Calculate level from XP"""
        return self.level_formula['calculateLevel'](xp) + 1  # +1 because we start at level 1
    
    async def handle_message(self, message: discord.Message) -> Optional[Dict[str, Any]]:
        """Handle message XP gain"""
        if message.author.bot:
            return None
        
        user_id = str(message.author.id)
        
        # Check cooldown
        cooldown_key = f"{user_id}_text"
        now = datetime.now()
        cooldown_time = self.xp_config['text']['cooldown'] / 1000  # Convert to seconds
        
        if cooldown_key in self.xp_cooldowns:
            if (now - self.xp_cooldowns[cooldown_key]).total_seconds() < cooldown_time:
                return None
        
        self.xp_cooldowns[cooldown_key] = now
        
        # Calculate XP gain
        base_xp = self.xp_config['text']['base']
        bonus_xp = random.randint(0, self.xp_config['text']['bonus'])
        xp_gain = min(base_xp + bonus_xp, self.xp_config['text']['maxPerMessage'])
        
        # Apply multipliers
        multiplier = self.get_xp_multiplier(message.author)
        xp_gain = math.floor(xp_gain * multiplier)
        
        # Update XP in database
        await database.create_user(user_id, message.author.name)
        new_level, leveled_up = await database.update_user_xp(user_id, xp_gain)
        
        # Check for level up
        if leveled_up:
            await self.handle_level_up(user_id, 'text', new_level - 1, new_level, message.channel)
        
        return {'xp_gain': xp_gain, 'new_level': leveled_up}
    
    async def handle_voice_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice state updates for XP"""
        user_id = str(member.id)
        
        # User joined voice
        if before.channel is None and after.channel is not None:
            self.voice_sessions[user_id] = {
                'start_time': datetime.now(),
                'channel': after.channel,
                'muted': after.self_mute or after.mute
            }
        
        # User left voice
        elif before.channel is not None and after.channel is None:
            if user_id in self.voice_sessions:
                session = self.voice_sessions.pop(user_id)
                duration = datetime.now() - session['start_time']
                minutes = duration.total_seconds() / 60
                
                # Only give XP if they were there long enough
                min_duration = self.xp_config['voice']['minDuration'] / (1000 * 60)  # Convert to minutes
                if minutes >= min_duration:
                    await self.add_voice_xp(user_id, minutes, member)
        
        # User switched channels
        elif before.channel != after.channel and user_id in self.voice_sessions:
            self.voice_sessions[user_id]['channel'] = after.channel
    
    async def add_voice_xp(self, user_id: str, minutes: float, member: discord.Member) -> Dict[str, Any]:
        """Add voice XP to user"""
        # Calculate base XP
        xp_gain = math.floor(self.xp_config['voice']['base'] * minutes)
        
        # Check if user was in voice with others (bonus)
        if user_id in self.voice_sessions:
            channel = self.voice_sessions[user_id]['channel']
            if len(channel.members) > 1:  # Others were present
                xp_gain += math.floor(self.xp_config['voice']['bonus'] * minutes)
        
        # Apply multipliers
        multiplier = self.get_xp_multiplier(member)
        xp_gain = math.floor(xp_gain * multiplier)
        
        # Update XP in database
        await database.create_user(user_id, member.name)
        new_level, leveled_up = await database.update_user_xp(user_id, xp_gain)
        
        # Check for level up
        if leveled_up:
            await self.handle_level_up(user_id, 'voice', new_level - 1, new_level)
        
        return {'xp_gain': xp_gain, 'new_level': leveled_up}
    
    async def add_role_xp(self, user_id: str, activity_type: str, amount: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Add role-based XP for achievements"""
        xp_mappings = {
            'daily_login': self.xp_config['role']['dailyLogin'],
            'message_streak': self.xp_config['role']['messageStreak'],
            'voice_streak': self.xp_config['role']['voiceStreak'],
            'helping_others': self.xp_config['role']['helpingOthers'],
            'event_participation': self.xp_config['role']['eventParticipation'],
            'custom': amount or 0
        }
        
        if activity_type not in xp_mappings:
            return None
        
        xp_gain = xp_mappings[activity_type]
        
        # Apply multipliers (would need member object)
        # For now, just use base amount
        
        # Update XP in database
        new_level, leveled_up = await database.update_user_xp(user_id, xp_gain)
        
        # Check for level up
        if leveled_up:
            await self.handle_level_up(user_id, 'role', new_level - 1, new_level)
        
        return {'xp_gain': xp_gain, 'new_level': leveled_up}
    
    def get_xp_multiplier(self, member: discord.Member) -> float:
        """Get XP multiplier based on user roles"""
        multiplier = 1.0
        
        # TODO: Implement role checking when role system is converted
        # For now, check premium_since for boost bonus
        if member.premium_since:
            multiplier += 0.5  # 50% bonus for boosters
        
        return multiplier
    
    async def handle_level_up(self, user_id: str, level_type: str, old_level: int, new_level: int, channel: Optional[discord.TextChannel] = None):
        """Handle level up and rewards"""
        # Cap the new level at max level
        capped_level = min(new_level, self.level_formula['maxLevel'])
        
        # Check for hardcoded rewards (currency and titles)
        rewards = self.level_rewards.get(level_type, {})
        if capped_level in rewards:
            reward = rewards[capped_level]
            await self.grant_reward(user_id, level_type, capped_level, reward)
        
        # TODO: Check for configurable role rewards from database
        
        # Send level up message
        if channel:
            await self.send_level_up_message(channel, user_id, level_type, capped_level)
    
    async def grant_reward(self, user_id: str, level_type: str, level: int, reward: Dict[str, Any]):
        """Grant level rewards"""
        try:
            if reward['type'] == 'currency':
                await database.update_balance(user_id, reward['amount'])
                await database.add_transaction(user_id, 'level_reward', reward['amount'], 
                                             f"Level {level} {level_type} reward")
            
            elif reward['type'] == 'role':
                # TODO: Implement role granting when role system is converted
                pass
            
            elif reward['type'] == 'title':
                # TODO: Implement title system
                pass
            
        except Exception as error:
            logging.error(f"Error granting reward for {user_id}: {error}")
    
    async def send_level_up_message(self, channel: discord.TextChannel, user_id: str, level_type: str, new_level: int):
        """Send level up message"""
        try:
            user = await self.client.fetch_user(int(user_id))
            is_max_level = new_level >= self.level_formula['maxLevel']
            
            # Get colors from config
            embed_color = int(config.colors['primary'].replace('#', ''), 16)
            if is_max_level:
                embed_color = int(config.colors['kingdom'].replace('#', ''), 16)
            
            # Level type icons
            icons = {
                'text': '💬',
                'voice': '🎤',
                'role': '👑',
                'overall': '⭐'
            }
            
            icon = icons.get(level_type, '📈')
            
            # Create embed
            embed = discord.Embed(
                title=f"{icon} Level Up!",
                description=f"**{user.mention}** reached **Level {new_level}** in **{level_type.title()}**!",
                color=embed_color
            )
            
            if is_max_level:
                embed.add_field(
                    name="🏆 MAX LEVEL ACHIEVED!",
                    value="You have reached the maximum level!",
                    inline=False
                )
            
            # Add reward info if available
            rewards = self.level_rewards.get(level_type, {})
            if new_level in rewards:
                reward = rewards[new_level]
                embed.add_field(
                    name="🎁 Reward",
                    value=reward['message'],
                    inline=False
                )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.timestamp = datetime.now()
            
            await channel.send(embed=embed)
            
        except Exception as error:
            logging.error(f"Error sending level up message: {error}")
    
    async def get_user_rank(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive user rank information across all categories"""
        try:
            user_data = await database.get_user(user_id)
            if not user_data:
                return None
            
            levels = {}
            roles_earned = {}
            next_roles = {}
            
            # Get information for each category
            for category in ['text', 'voice', 'role', 'overall']:
                xp = user_data.get(f'{category}_xp', 0)
                level = self.level_formula['calculateLevel'](xp)
                
                # Calculate XP needed for next level
                if level >= self.level_formula['maxLevel']:
                    xp_needed = 0
                    xp_for_next = 0
                else:
                    xp_for_next = self.get_xp_for_level(level + 1)
                    xp_needed = xp_for_next - xp
                
                levels[category] = {
                    'level': level,
                    'xp': xp,
                    'xp_needed': xp_needed,
                    'xp_for_next': xp_for_next
                }
                
                # Get current and next roles
                roles_earned[category] = self._get_current_role(category, level)
                next_roles[category] = self._get_next_role(category, level)
            
            # Check prestige eligibility
            prestige_info = self._check_prestige_eligibility(levels)
            
            return {
                'levels': levels,
                'roles_earned': roles_earned,
                'next_roles': next_roles,
                'prestige_info': prestige_info,
                'total_messages': user_data.get('total_messages', 0),
                'total_voice_time': user_data.get('total_voice_time', 0),
                'prestige_level': user_data.get('prestige_level', 0)
            }
            
        except Exception as error:
            logging.error(f"Error getting user rank: {error}")
            return None
    
    def _get_current_role(self, category: str, level: int) -> Optional[Dict[str, Any]]:
        """Get the current role for a category and level"""
        if category not in self.level_roles:
            return None
        
        category_roles = self.level_roles[category]
        current_role = None
        
        for role_level in sorted([int(x) for x in category_roles.keys()]):
            if level >= role_level:
                current_role = {
                    'level': role_level,
                    'name': category_roles[str(role_level)]['name'],
                    'color': category_roles[str(role_level)]['color'],
                    'perks': category_roles[str(role_level)]['perks']
                }
            else:
                break
        
        return current_role
    
    def _get_next_role(self, category: str, level: int) -> Optional[Dict[str, Any]]:
        """Get the next role to achieve for a category"""
        if category not in self.level_roles:
            return None
        
        category_roles = self.level_roles[category]
        
        for role_level in sorted([int(x) for x in category_roles.keys()]):
            if level < role_level:
                return {
                    'level': role_level,
                    'name': category_roles[str(role_level)]['name'],
                    'color': category_roles[str(role_level)]['color'],
                    'perks': category_roles[str(role_level)]['perks'],
                    'levels_needed': role_level - level
                }
        
        return None
    
    def _check_prestige_eligibility(self, levels: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check if user is eligible for prestige"""
        if not self.prestige_system.get('enabled'):
            return {'eligible': False}
        
        requirements = self.prestige_system.get('requirements', {})
        
        # Check if all categories are at level 50
        all_max_level = all(levels[cat]['level'] >= 50 for cat in ['text', 'voice', 'role', 'overall'])
        
        return {
            'eligible': all_max_level,
            'requirements_met': {
                'all_categories_level_50': all_max_level,
                'minimum_activity': True,  # Would need to implement activity tracking
                'community_contribution': True  # Would need to implement contribution tracking
            },
            'next_prestige_level': 1  # Would need to get from user data
        }

# Global leveling system instance (will be initialized with bot client)
leveling_system = None

def init_leveling_system(client):
    """Initialize the leveling system with bot client"""
    global leveling_system
    leveling_system = LevelingSystem(client)
    return leveling_system