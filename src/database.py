import aiosqlite
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

class Database:
    """Async SQLite database manager for Wonder Discord Bot"""
    
    def __init__(self, db_path: str = "../wonder.db"):
        self.db_path = Path(__file__).parent / db_path
        self.db_path.parent.mkdir(exist_ok=True)
        
    async def init(self):
        """Initialize database and create all tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table for economy system
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    balance INTEGER DEFAULT 0,
                    daily_last_claimed TEXT,
                    work_last_used TEXT,
                    total_earned INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Introduction cards table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS introduction_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    name TEXT,
                    age INTEGER,
                    location TEXT,
                    hobbies TEXT,
                    favorite_color TEXT,
                    bio TEXT,
                    image_url TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Server settings table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS server_settings (
                    guild_id TEXT PRIMARY KEY,
                    welcome_channel TEXT,
                    introduction_channel TEXT,
                    welcome_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Transaction history
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    type TEXT,
                    amount INTEGER,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User inventory table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    item_id TEXT,
                    quantity INTEGER DEFAULT 1,
                    acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Active effects table for consumables
            await db.execute("""
                CREATE TABLE IF NOT EXISTS active_effects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    effect_type TEXT,
                    duration_minutes INTEGER,
                    uses_remaining INTEGER DEFAULT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME
                )
            """)

            # Cooldowns table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cooldowns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    command_type TEXT,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, command_type)
                )
            """)

            # User profiles table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    background_id TEXT,
                    accent_color TEXT,
                    title TEXT,
                    badge TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Giveaways table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS giveaways (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    channel_id TEXT,
                    guild_id TEXT,
                    host_id TEXT,
                    title TEXT,
                    description TEXT,
                    winners_count INTEGER,
                    end_time DATETIME,
                    prize TEXT,
                    requirements TEXT,
                    required_roles TEXT,
                    forbidden_roles TEXT,
                    winner_role_id TEXT,
                    min_messages INTEGER DEFAULT 0,
                    min_account_age_days INTEGER DEFAULT 0,
                    bypass_roles TEXT,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ended_at DATETIME,
                    reroll_count INTEGER DEFAULT 0
                )
            """)

            # Giveaway entries table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS giveaway_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    giveaway_id INTEGER,
                    user_id TEXT,
                    entries INTEGER DEFAULT 1,
                    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(giveaway_id) REFERENCES giveaways(id),
                    UNIQUE(giveaway_id, user_id)
                )
            """)

            # Giveaway winners table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS giveaway_winners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    giveaway_id INTEGER,
                    user_id TEXT,
                    winner_position INTEGER,
                    selected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_reroll BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY(giveaway_id) REFERENCES giveaways(id)
                )
            """)

            # Leveling system tables
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_levels (
                    user_id TEXT PRIMARY KEY,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    total_messages INTEGER DEFAULT 0,
                    last_xp_gain DATETIME,
                    voice_time INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 0,
                    last_daily DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Level role rewards configuration table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS level_role_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level_type TEXT,
                    level INTEGER,
                    role_id TEXT,
                    role_name TEXT,
                    created_by TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(level_type, level)
                )
            """)

            # WonderCoins drop channels table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS drop_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT,
                    channel_id TEXT,
                    created_by TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, channel_id)
                )
            """)

            # WonderCoins drop statistics table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS drop_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT,
                    user_id TEXT,
                    amount INTEGER,
                    rarity TEXT,
                    collection_type TEXT,
                    drop_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User drop statistics summary table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_drop_stats (
                    user_id TEXT PRIMARY KEY,
                    total_collected INTEGER DEFAULT 0,
                    total_drops INTEGER DEFAULT 0,
                    common_drops INTEGER DEFAULT 0,
                    rare_drops INTEGER DEFAULT 0,
                    epic_drops INTEGER DEFAULT 0,
                    legendary_drops INTEGER DEFAULT 0,
                    last_drop DATETIME,
                    best_drop INTEGER DEFAULT 0
                )
            """)

            await db.commit()

    # User economy methods
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from database"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_user(self, user_id: str, username: str) -> int:
        """Create a new user in the database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
                (user_id, username)
            )
            await db.commit()
            return cursor.lastrowid

    async def update_balance(self, user_id: str, amount: int) -> int:
        """Update user balance by adding the specified amount"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'UPDATE users SET balance = balance + ?, total_earned = total_earned + ? WHERE user_id = ?',
                (amount, max(0, amount), user_id)
            )
            await db.commit()
            return cursor.rowcount

    async def set_balance(self, user_id: str, amount: int) -> int:
        """Set user balance to the specified amount"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'UPDATE users SET balance = ? WHERE user_id = ?',
                (amount, user_id)
            )
            await db.commit()
            return cursor.rowcount

    async def update_daily_claim(self, user_id: str) -> int:
        """Update the daily claim timestamp for a user"""
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'UPDATE users SET daily_last_claimed = ? WHERE user_id = ?',
                (now, user_id)
            )
            await db.commit()
            return cursor.rowcount

    async def update_work_claim(self, user_id: str) -> int:
        """Update the work claim timestamp for a user"""
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'UPDATE users SET work_last_used = ? WHERE user_id = ?',
                (now, user_id)
            )
            await db.commit()
            return cursor.rowcount

    # Introduction card methods
    async def save_intro_card(self, data: Dict[str, Any]) -> int:
        """Save introduction card data"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR REPLACE INTO introduction_cards 
                   (user_id, name, age, location, hobbies, favorite_color, bio) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data['user_id'], data['name'], data['age'], data['location'], 
                 data['hobbies'], data['favorite_color'], data['bio'])
            )
            await db.commit()
            return cursor.lastrowid

    async def get_intro_card(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get introduction card for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM introduction_cards WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    # Transaction methods
    async def add_transaction(self, user_id: str, transaction_type: str, amount: int, description: str) -> int:
        """Add a transaction record"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
                (user_id, transaction_type, amount, description)
            )
            await db.commit()
            return cursor.lastrowid

    # Server settings methods
    async def get_server_settings(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get server settings"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM server_settings WHERE guild_id = ?', (guild_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_server_settings(self, guild_id: str, settings: Dict[str, Any]) -> int:
        """Update server settings"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR REPLACE INTO server_settings 
                   (guild_id, welcome_channel, introduction_channel, welcome_message) 
                   VALUES (?, ?, ?, ?)""",
                (guild_id, settings.get('welcome_channel'), 
                 settings.get('introduction_channel'), settings.get('welcome_message'))
            )
            await db.commit()
            return cursor.lastrowid

    # Leaderboard methods
    async def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by balance"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM users ORDER BY balance DESC LIMIT ?', (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # Inventory methods
    async def add_item_to_inventory(self, user_id: str, item_id: str, quantity: int = 1) -> int:
        """Add item to user inventory"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if item already exists
            async with db.execute(
                'SELECT quantity FROM user_inventory WHERE user_id = ? AND item_id = ?',
                (user_id, item_id)
            ) as cursor:
                existing = await cursor.fetchone()
            
            if existing:
                cursor = await db.execute(
                    'UPDATE user_inventory SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?',
                    (quantity, user_id, item_id)
                )
            else:
                cursor = await db.execute(
                    'INSERT INTO user_inventory (user_id, item_id, quantity) VALUES (?, ?, ?)',
                    (user_id, item_id, quantity)
                )
            
            await db.commit()
            return cursor.rowcount

    async def get_user_inventory(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's inventory"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM user_inventory WHERE user_id = ? ORDER BY acquired_at DESC',
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # Leveling system methods
    async def get_user_level(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user level data"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM user_levels WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_user_xp(self, user_id: str, xp_gain: int) -> Tuple[int, bool]:
        """Update user XP and return new level and whether they leveled up"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get current data
            async with db.execute(
                'SELECT xp, level FROM user_levels WHERE user_id = ?', (user_id,)
            ) as cursor:
                current = await cursor.fetchone()
            
            if not current:
                # Create new user level record
                await db.execute(
                    'INSERT INTO user_levels (user_id, xp, level) VALUES (?, ?, ?)',
                    (user_id, xp_gain, 1)
                )
                await db.commit()
                return 1, False
            
            current_xp, current_level = current
            new_xp = current_xp + xp_gain
            new_level = self._calculate_level(new_xp)
            leveled_up = new_level > current_level
            
            await db.execute(
                'UPDATE user_levels SET xp = ?, level = ?, last_xp_gain = CURRENT_TIMESTAMP WHERE user_id = ?',
                (new_xp, new_level, user_id)
            )
            await db.commit()
            
            return new_level, leveled_up

    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP"""
        # Simple level calculation: level = sqrt(xp / 100)
        import math
        return max(1, int(math.sqrt(xp / 100)) + 1)

    # Cooldown methods
    async def set_cooldown(self, user_id: str, command_type: str) -> None:
        """Set cooldown for a user and command type"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO cooldowns (user_id, command_type, last_used) VALUES (?, ?, CURRENT_TIMESTAMP)',
                (user_id, command_type)
            )
            await db.commit()

    async def get_cooldown(self, user_id: str, command_type: str) -> Optional[datetime]:
        """Get cooldown timestamp for a user and command type"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT last_used FROM cooldowns WHERE user_id = ? AND command_type = ?',
                (user_id, command_type)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return datetime.fromisoformat(row[0])
                return None

    async def close(self):
        """Close database connection (for cleanup)"""
        pass  # aiosqlite handles connections automatically

# Global database instance
database = Database()