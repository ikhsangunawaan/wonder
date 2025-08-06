import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging

from database import database
from config import config

class CooldownManager:
    """Manages command cooldowns and active effects"""
    
    def __init__(self):
        # Get cooldowns from config
        self.cooldowns = config.cooldowns.copy()
        
        # Convert to minutes if needed (some might be in seconds)
        # Ensure all are in minutes for consistency
        if 'daily' not in self.cooldowns:
            self.cooldowns['daily'] = 24 * 60  # 24 hours
        if 'work' not in self.cooldowns:
            self.cooldowns['work'] = 60  # 1 hour
        if 'use_item' not in self.cooldowns:
            self.cooldowns['use_item'] = 1  # 1 minute
    
    async def check_cooldown(self, user_id: str, command_type: str) -> Dict[str, Any]:
        """Check if user is on cooldown for a command"""
        try:
            # Check for work energy effect that removes work cooldown
            if command_type == 'work':
                has_work_energy = await self.has_active_effect(user_id, 'work_cooldown_reset')
                if has_work_energy:
                    return {"on_cooldown": False, "time_left": 0}
            
            cooldown_time = self.cooldowns.get(command_type)
            if not cooldown_time:
                return {"on_cooldown": False, "time_left": 0}
            
            # Get last used timestamp
            last_used = await database.get_cooldown(user_id, command_type)
            if not last_used:
                return {"on_cooldown": False, "time_left": 0}
            
            # Calculate time difference
            now = datetime.now()
            time_diff = now - last_used
            minutes_passed = time_diff.total_seconds() / 60
            
            if minutes_passed >= cooldown_time:
                return {"on_cooldown": False, "time_left": 0}
            
            time_left = int(cooldown_time - minutes_passed)
            return {"on_cooldown": True, "time_left": time_left}
            
        except Exception as error:
            logging.error(f'Error checking cooldown: {error}')
            return {"on_cooldown": False, "time_left": 0}
    
    async def set_cooldown(self, user_id: str, command_type: str) -> None:
        """Set cooldown for a command"""
        try:
            await database.set_cooldown(user_id, command_type)
        except Exception as error:
            logging.error(f'Error setting cooldown: {error}')
    
    def format_time_left(self, minutes: int) -> str:
        """Format time remaining for display"""
        if minutes >= 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours}h"
            return f"{hours}h {remaining_minutes}m"
        return f"{minutes}m"
    
    def create_cooldown_message(self, command_type: str, time_left: int) -> str:
        """Create cooldown error message"""
        time_formatted = self.format_time_left(time_left)
        messages = {
            'daily': f"⏰ You can claim your daily reward in **{time_formatted}**!",
            'work': f"⏰ You can work again in **{time_formatted}**! Use ⚡ Work Energy to skip this cooldown.",
            'coinflip': f"🪙 Coin flip is on cooldown for **{time_formatted}**. Take a break!",
            'dice': f"🎲 Dice game is on cooldown for **{time_formatted}**. Try again soon!",
            'slots': f"🎰 Slot machine is on cooldown for **{time_formatted}**. Patience pays off!",
            'mystery_box': f"📦 You can open another mystery box in **{time_formatted}**!",
            'use_item': f"⏱️ You can use another item in **{time_formatted}**!"
        }
        
        return messages.get(command_type, f"⏰ Command is on cooldown for **{time_formatted}**!")
    
    async def can_bypass_cooldown(self, user_id: str, command_type: str, member) -> bool:
        """Check if user can bypass cooldown with premium perks"""
        try:
            # Premium members get reduced game cooldowns
            if command_type in ['coinflip', 'dice', 'slots']:
                # Check for premium role (will be implemented when role system is converted)
                # For now, return False
                # TODO: Implement premium role checking
                return False
            
            return False
        except Exception as error:
            logging.error(f'Error checking cooldown bypass: {error}')
            return False
    
    async def get_user_cooldowns(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all active cooldowns for a user"""
        try:
            cooldowns = {}
            for command_type in self.cooldowns.keys():
                cooldown_data = await self.check_cooldown(user_id, command_type)
                if cooldown_data['on_cooldown']:
                    cooldowns[command_type] = {
                        'time_left': cooldown_data['time_left'],
                        'formatted': self.format_time_left(cooldown_data['time_left'])
                    }
            return cooldowns
        except Exception as error:
            logging.error(f'Error getting user cooldowns: {error}')
            return {}
    
    async def has_active_effect(self, user_id: str, effect_type: str) -> bool:
        """Check if user has an active effect"""
        try:
            # This would check the active_effects table
            # For now, return False as effects system needs to be implemented
            # TODO: Implement active effects checking
            return False
        except Exception as error:
            logging.error(f'Error checking active effect: {error}')
            return False
    
    async def apply_gambling_luck(self, user_id: str) -> bool:
        """Apply gambling luck effect"""
        try:
            has_luck = await self.has_active_effect(user_id, 'gambling_luck')
            if has_luck:
                # Use one charge of the luck effect
                await self.use_effect(user_id, 'gambling_luck')
                return True
            return False
        except Exception as error:
            logging.error(f'Error applying gambling luck: {error}')
            return False
    
    async def has_experience_boost(self, user_id: str) -> bool:
        """Check if user has experience boost"""
        try:
            has_boost = await self.has_active_effect(user_id, 'exp_boost')
            if has_boost:
                await self.use_effect(user_id, 'exp_boost')
                return True
            return False
        except Exception as error:
            logging.error(f'Error checking experience boost: {error}')
            return False
    
    async def has_daily_double(self, user_id: str) -> bool:
        """Check if user has daily double effect"""
        try:
            has_double = await self.has_active_effect(user_id, 'daily_double')
            if has_double:
                # Remove the effect after use (it's single use)
                await self.remove_effect(user_id, 'daily_double')
                return True
            return False
        except Exception as error:
            logging.error(f'Error checking daily double: {error}')
            return False
    
    async def use_effect(self, user_id: str, effect_type: str) -> None:
        """Use an active effect (decrement uses or remove if expired)"""
        # TODO: Implement effect usage
        pass
    
    async def remove_effect(self, user_id: str, effect_type: str) -> None:
        """Remove an active effect"""
        # TODO: Implement effect removal
        pass
    
    async def cleanup_expired_effects(self) -> None:
        """Clean up expired effects (run periodically)"""
        try:
            # TODO: Implement expired effects cleanup
            logging.info('🧹 Cleaned up expired effects')
        except Exception as error:
            logging.error(f'Error cleaning up expired effects: {error}')
    
    def get_cooldown_reduction(self, command_type: str, member) -> float:
        """Get cooldown reduction for premium users"""
        if not member:
            return 1.0
        
        # TODO: Implement premium/booster role checking
        # For now, return no reduction
        return 1.0
    
    async def get_actual_cooldown(self, user_id: str, command_type: str, member) -> int:
        """Calculate actual cooldown time with reductions"""
        try:
            base_cooldown = self.cooldowns.get(command_type, 0)
            if not base_cooldown:
                return 0
            
            reduction = self.get_cooldown_reduction(command_type, member)
            actual_cooldown = int(base_cooldown * reduction)
            
            return actual_cooldown
        except Exception as error:
            logging.error(f'Error calculating actual cooldown: {error}')
            return self.cooldowns.get(command_type, 0)

# Global cooldown manager instance
cooldown_manager = CooldownManager()