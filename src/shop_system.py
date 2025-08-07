import discord
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import random

from database import database
from config import config
from cooldown_manager import cooldown_manager

class ShopSystem:
    """Manages the shop system with items, purchasing, and inventory"""
    
    def __init__(self):
        self.shop_items = self._load_shop_items()
        self.categories = config.get('shop.categories', ['consumables', 'collectibles', 'profile', 'special'])
        
    def _load_shop_items(self) -> Dict[str, Dict[str, Any]]:
        """Load shop items configuration"""
        return {
            # Consumables
            'daily_double': {
                'name': 'Daily Double',
                'description': 'Double your next daily reward',
                'price': 1000,
                'category': 'consumables',
                'emoji': '⚡',
                'effect_type': 'daily_double',
                'uses': 1,
                'rarity': 'common'
            },
            'work_energy': {
                'name': 'Work Energy',
                'description': 'Skip work cooldown for 3 uses',
                'price': 800,
                'category': 'consumables',
                'emoji': '🔋',
                'effect_type': 'work_cooldown_reset',
                'uses': 3,
                'rarity': 'common'
            },
            'exp_boost': {
                'name': 'XP Boost',
                'description': '50% more XP for 1 hour',
                'price': 1500,
                'category': 'consumables',
                'emoji': '🚀',
                'effect_type': 'exp_boost',
                'duration_minutes': 60,
                'uses': 10,
                'rarity': 'rare'
            },
            'gambling_luck': {
                'name': 'Gambling Luck',
                'description': 'Better odds in games for 5 uses',
                'price': 2000,
                'category': 'consumables',
                'emoji': '🍀',
                'effect_type': 'gambling_luck',
                'uses': 5,
                'rarity': 'rare'
            },
            
            # Collectibles
            'golden_coin': {
                'name': 'Golden Coin',
                'description': 'A rare collectible golden coin',
                'price': 5000,
                'category': 'collectibles',
                'emoji': '🪙',
                'rarity': 'epic'
            },
            'crystal_gem': {
                'name': 'Crystal Gem',
                'description': 'A beautiful crystal gem',
                'price': 10000,
                'category': 'collectibles',
                'emoji': '💎',
                'rarity': 'legendary'
            },
            'wonder_crown': {
                'name': 'Wonder Crown',
                'description': 'Symbol of ultimate wonder',
                'price': 50000,
                'category': 'collectibles',
                'emoji': '👑',
                'rarity': 'mythic'
            },
            
            # Profile Items
            'custom_background': {
                'name': 'Custom Background',
                'description': 'Customize your profile background',
                'price': 2500,
                'category': 'profile',
                'emoji': '🎨',
                'rarity': 'rare'
            },
            'special_title': {
                'name': 'Special Title',
                'description': 'Unlock special titles for your profile',
                'price': 3000,
                'category': 'profile',
                'emoji': '🏷️',
                'rarity': 'rare'
            },
            
            # Special Items
            'mystery_box': {
                'name': 'Mystery Box',
                'description': 'Contains random rewards',
                'price': 1000,
                'category': 'special',
                'emoji': '📦',
                'rarity': 'common'
            },
            'premium_pass': {
                'name': 'Premium Pass',
                'description': '7 days of premium benefits',
                'price': 15000,
                'category': 'special',
                'emoji': '🎫',
                'rarity': 'legendary'
            }
        }
    
    def get_all_items(self) -> Dict[str, Dict[str, Any]]:
        """Get all shop items"""
        return self.shop_items
    
    async def get_shop_embed(self, category: str = 'all', page: int = 1) -> discord.Embed:
        """Create shop display embed"""
        items_per_page = 5
        
        # Filter items by category
        if category == 'all':
            filtered_items = self.shop_items
        else:
            filtered_items = {k: v for k, v in self.shop_items.items() if v['category'] == category}
        
        # Pagination
        total_items = len(filtered_items)
        total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = list(filtered_items.items())[start_idx:end_idx]
        
        # Create embed
        embed = discord.Embed(
            title=f"🏪 Wonder Shop - {category.title()}",
            description="Purchase items with your WonderCoins!",
            color=int(config.colors['primary'].replace('#', ''), 16)
        )
        
        if not page_items:
            embed.add_field(
                name="No items found",
                value="This category is empty or doesn't exist.",
                inline=False
            )
        else:
            for item_id, item in page_items:
                rarity_colors = {
                    'common': '⚪',
                    'rare': '🔵', 
                    'epic': '🟣',
                    'legendary': '🟡',
                    'mythic': '🔴'
                }
                
                rarity_indicator = rarity_colors.get(item.get('rarity', 'common'), '⚪')
                
                embed.add_field(
                    name=f"{item['emoji']} {item['name']} {rarity_indicator}",
                    value=f"{item['description']}\n**Price:** {item['price']:,} {config.currency['symbol']}\n**ID:** `{item_id}`",
                    inline=True
                )
        
        embed.set_footer(text=f"Page {page}/{total_pages} • Use w.buy <item_id> to purchase")
        
        return embed
    
    async def purchase_item(self, user_id: str, item_id: str, quantity: int = 1) -> Dict[str, Any]:
        """Purchase an item from the shop"""
        try:
            # Check if item exists
            if item_id not in self.shop_items:
                return {"success": False, "message": "Item not found in shop!"}
            
            item = self.shop_items[item_id]
            total_cost = item['price'] * quantity
            
            # Get user data
            user_data = await database.get_user(user_id)
            if not user_data:
                await database.create_user(user_id, "Unknown")
                user_data = await database.get_user(user_id)
            
            # Check balance
            if user_data['balance'] < total_cost:
                return {
                    "success": False, 
                    "message": f"Insufficient funds! You need {total_cost:,} {config.currency['symbol']} but only have {user_data['balance']:,}."
                }
            
            # Check stock (if applicable)
            if item.get('limited_stock'):
                # Implementation for limited stock items
                pass
            
            # Process purchase
            await database.update_balance(user_id, -total_cost)
            await database.add_transaction(user_id, 'shop_purchase', -total_cost, f"Purchased {quantity}x {item['name']}")
            
            # Add item to inventory
            await database.add_item_to_inventory(user_id, item_id, quantity)
            
            # Apply effects for consumables
            if item['category'] == 'consumables' and item.get('effect_type'):
                await self._apply_item_effect(user_id, item)
            
            return {
                "success": True,
                "message": f"Successfully purchased {quantity}x {item['emoji']} {item['name']} for {total_cost:,} {config.currency['symbol']}!",
                "item": item,
                "quantity": quantity,
                "total_cost": total_cost
            }
            
        except Exception as e:
            logging.error(f"Error purchasing item: {e}")
            return {"success": False, "message": "An error occurred during purchase."}
    
    async def use_item(self, user_id: str, item_id: str) -> Dict[str, Any]:
        """Use an item from inventory"""
        try:
            # Check cooldown
            cooldown_check = await cooldown_manager.check_cooldown(user_id, 'use_item')
            if cooldown_check['on_cooldown']:
                return {
                    "success": False,
                    "message": cooldown_manager.create_cooldown_message('use_item', cooldown_check['time_left'])
                }
            
            # Check if user has the item
            inventory = await database.get_user_inventory(user_id)
            user_item = next((item for item in inventory if item['item_id'] == item_id), None)
            
            if not user_item or user_item['quantity'] <= 0:
                return {"success": False, "message": "You don't have this item!"}
            
            # Get item details
            if item_id not in self.shop_items:
                return {"success": False, "message": "Item not found!"}
            
            item = self.shop_items[item_id]
            
            # Use the item
            result = await self._use_specific_item(user_id, item_id, item)
            
            if result['success']:
                # Set cooldown
                await cooldown_manager.set_cooldown(user_id, 'use_item')
                
                # Remove one item from inventory
                await self._remove_item_from_inventory(user_id, item_id, 1)
            
            return result
            
        except Exception as e:
            logging.error(f"Error using item: {e}")
            return {"success": False, "message": "An error occurred while using the item."}
    
    async def _use_specific_item(self, user_id: str, item_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle usage of specific item types"""
        if item['category'] == 'consumables':
            return await self._use_consumable(user_id, item)
        elif item_id == 'mystery_box':
            return await self._open_mystery_box(user_id)
        else:
            return {"success": False, "message": "This item cannot be used!"}
    
    async def _use_consumable(self, user_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Use a consumable item"""
        effect_type = item.get('effect_type')
        
        if not effect_type:
            return {"success": False, "message": "This item has no effect!"}
        
        # Apply the effect
        await self._apply_item_effect(user_id, item)
        
        return {
            "success": True,
            "message": f"Used {item['emoji']} {item['name']}! {item['description']}"
        }
    
    async def _apply_item_effect(self, user_id: str, item: Dict[str, Any]) -> None:
        """Apply effect from consumable item"""
        effect_type = item.get('effect_type')
        
        if not effect_type:
            return
        
        # Calculate expiry time
        expires_at = None
        if item.get('duration_minutes'):
            expires_at = datetime.now() + timedelta(minutes=item['duration_minutes'])
        
        # Add effect to database
        import aiosqlite
        async with aiosqlite.connect(database.db_path) as db:
                await db.execute(
                    """INSERT INTO active_effects 
                       (user_id, effect_type, duration_minutes, uses_remaining, expires_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, effect_type, item.get('duration_minutes'), 
                     item.get('uses'), expires_at.isoformat() if expires_at else None)
                )
                await db.commit()
    
    async def _open_mystery_box(self, user_id: str) -> Dict[str, Any]:
        """Open a mystery box and give random rewards"""
        rewards = [
            {"type": "currency", "amount": 500, "chance": 40},
            {"type": "currency", "amount": 1000, "chance": 25},
            {"type": "currency", "amount": 2000, "chance": 15},
            {"type": "currency", "amount": 5000, "chance": 10},
            {"type": "item", "item_id": "daily_double", "chance": 5},
            {"type": "item", "item_id": "work_energy", "chance": 3},
            {"type": "item", "item_id": "exp_boost", "chance": 2}
        ]
        
        # Weighted random selection
        total_chance = sum(reward['chance'] for reward in rewards)
        rand = random.randint(1, total_chance)
        
        current_chance = 0
        selected_reward = None
        
        for reward in rewards:
            current_chance += reward['chance']
            if rand <= current_chance:
                selected_reward = reward
                break
        
        if not selected_reward:
            selected_reward = rewards[0]  # Fallback
        
        # Apply reward
        if selected_reward['type'] == 'currency':
            amount = selected_reward['amount']
            await database.update_balance(user_id, amount)
            await database.add_transaction(user_id, 'mystery_box', amount, "Mystery box reward")
            
            return {
                "success": True,
                "message": f"🎉 Mystery box opened! You received {amount:,} {config.currency['symbol']}!"
            }
        
        elif selected_reward['type'] == 'item':
            item_id = selected_reward['item_id']
            await database.add_item_to_inventory(user_id, item_id, 1)
            item = self.shop_items[item_id]
            
            return {
                "success": True,
                "message": f"🎉 Mystery box opened! You received {item['emoji']} {item['name']}!"
            }
    
    async def _remove_item_from_inventory(self, user_id: str, item_id: str, quantity: int) -> None:
        """Remove item from user inventory"""
        import aiosqlite
        async with aiosqlite.connect(database.db_path) as db:
                # Get current quantity
                async with db.execute(
                    'SELECT quantity FROM user_inventory WHERE user_id = ? AND item_id = ?',
                    (user_id, item_id)
                ) as cursor:
                    row = await cursor.fetchone()
                
                if row and row[0] > quantity:
                    # Reduce quantity
                    await db.execute(
                        'UPDATE user_inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?',
                        (quantity, user_id, item_id)
                    )
                else:
                    # Remove completely
                    await db.execute(
                        'DELETE FROM user_inventory WHERE user_id = ? AND item_id = ?',
                        (user_id, item_id)
                    )
                
                await db.commit()
    
    async def get_inventory_embed(self, user_id: str, page: int = 1) -> discord.Embed:
        """Get user inventory as embed"""
        items_per_page = 10
        inventory = await database.get_user_inventory(user_id)
        
        if not inventory:
            embed = discord.Embed(
                title="📦 Your Inventory",
                description="Your inventory is empty! Visit the shop to buy items.",
                color=int(config.colors['info'].replace('#', ''), 16)
            )
            return embed
        
        # Pagination
        total_items = len(inventory)
        total_pages = (total_items - 1) // items_per_page + 1
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = inventory[start_idx:end_idx]
        
        embed = discord.Embed(
            title="📦 Your Inventory",
            color=int(config.colors['primary'].replace('#', ''), 16)
        )
        
        inventory_text = ""
        for item_data in page_items:
            item_id = item_data['item_id']
            quantity = item_data['quantity']
            
            if item_id in self.shop_items:
                item = self.shop_items[item_id]
                inventory_text += f"{item['emoji']} **{item['name']}** x{quantity}\n"
            else:
                inventory_text += f"❓ **Unknown Item** ({item_id}) x{quantity}\n"
        
        embed.description = inventory_text or "Your inventory is empty!"
        embed.set_footer(text=f"Page {page}/{total_pages} • Use w.use <item_id> to use items")
        
        return embed

# Global shop system instance
shop_system = ShopSystem()