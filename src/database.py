import aiosqlite
import aiomysql
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from config import config
from mysql_database import MySQLDatabase

class Database:
    """Async database manager for Wonder Discord Bot (supports SQLite and MySQL)"""
    
    def __init__(self, db_path: str = "../wonder.db"):
        # Check if MySQL is configured
        self.db_config = config.get('database', {})
        self.use_mysql = self.db_config.get('type') == 'mysql'
        
        if self.use_mysql:
            # Use MySQL adapter
            self.mysql_db = MySQLDatabase()
        else:
            # SQLite configuration (fallback)
            self.db_path = Path(__file__).parent / db_path
            self.db_path.parent.mkdir(exist_ok=True)
    
    async def _get_connection(self):
        """Get database connection (MySQL pool or SQLite)"""
        if self.use_mysql:
            return await self.mysql_db._get_connection()
        else:
            return aiosqlite.connect(self.db_path)
        
    async def init(self):
        """Initialize database and create all tables"""
        if self.use_mysql:
            await self.mysql_db.init()
            return
            
        async with await self._get_connection() as db:
            # Users table for economy system
            users_sql = f"""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    username {self._get_sql_syntax('text')},
                    balance {self._get_sql_syntax('integer')} DEFAULT 0,
                    daily_last_claimed {self._get_sql_syntax('text')},
                    work_last_used {self._get_sql_syntax('text')},
                    total_earned {self._get_sql_syntax('integer')} DEFAULT 0,
                    created_at {self._get_sql_syntax('datetime')} DEFAULT {self._get_sql_syntax('current_timestamp')}
                )
            """
            await db.execute(users_sql)

            # Introduction cards table
            intro_cards_sql = f"""
                CREATE TABLE IF NOT EXISTS introduction_cards (
                    id {self._get_sql_syntax('integer')} {self._get_sql_syntax('primary_key')},
                    user_id VARCHAR(255) UNIQUE,
                    guild_id VARCHAR(255),
                    name {self._get_sql_syntax('text')},
                    age {self._get_sql_syntax('integer')},
                    location {self._get_sql_syntax('text')},
                    hobbies {self._get_sql_syntax('text')},
                    favorite_color VARCHAR(255) DEFAULT '#7C3AED',
                    bio {self._get_sql_syntax('text')},
                    social_media {self._get_sql_syntax('text')},
                    occupation {self._get_sql_syntax('text')},
                    pronouns {self._get_sql_syntax('text')},
                    timezone {self._get_sql_syntax('text')},
                    fun_fact {self._get_sql_syntax('text')},
                    card_template VARCHAR(255) DEFAULT 'default',
                    background_style VARCHAR(255) DEFAULT 'gradient',
                    is_public {self._get_sql_syntax('boolean')} DEFAULT TRUE,
                    is_approved {self._get_sql_syntax('boolean')} DEFAULT TRUE,
                    likes_count {self._get_sql_syntax('integer')} DEFAULT 0,
                    views_count {self._get_sql_syntax('integer')} DEFAULT 0,
                    image_url {self._get_sql_syntax('text')},
                    created_at {self._get_sql_syntax('datetime')} DEFAULT {self._get_sql_syntax('current_timestamp')},
                    updated_at {self._get_sql_syntax('datetime')} DEFAULT {self._get_sql_syntax('current_timestamp')}
                )
            """
            await db.execute(intro_cards_sql)

            # Introduction card interactions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS intro_card_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER,
                    user_id TEXT,
                    interaction_type TEXT, -- 'like', 'view', 'comment'
                    comment_text TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (card_id) REFERENCES introduction_cards (id),
                    UNIQUE (card_id, user_id, interaction_type)
                )
            """)

            # Server settings table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS server_settings (
                    guild_id TEXT PRIMARY KEY,
                    welcome_channel TEXT,
                    introduction_channel TEXT,
                    welcome_message TEXT,
                    intro_card_theme TEXT DEFAULT '#7C3AED',
                    intro_card_style TEXT DEFAULT 'gradient',
                    intro_card_background_url TEXT,
                    category_text_enabled BOOLEAN DEFAULT TRUE,
                    category_voice_enabled BOOLEAN DEFAULT TRUE,
                    category_role_enabled BOOLEAN DEFAULT TRUE,
                    category_overall_enabled BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add category columns to existing tables if they don't exist
            try:
                await db.execute("ALTER TABLE server_settings ADD COLUMN category_text_enabled BOOLEAN DEFAULT TRUE")
            except:
                pass
            try:
                await db.execute("ALTER TABLE server_settings ADD COLUMN category_voice_enabled BOOLEAN DEFAULT TRUE")
            except:
                pass
            try:
                await db.execute("ALTER TABLE server_settings ADD COLUMN category_role_enabled BOOLEAN DEFAULT TRUE")
            except:
                pass
            try:
                await db.execute("ALTER TABLE server_settings ADD COLUMN category_overall_enabled BOOLEAN DEFAULT TRUE")
            except:
                pass

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
                    settings TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, channel_id)
                )
            """)
            
            # Add settings column to existing drop_channels if it doesn't exist
            try:
                await db.execute("ALTER TABLE drop_channels ADD COLUMN settings TEXT DEFAULT '{}'")
            except:
                pass  # Column already exists

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
        if self.use_mysql:
            return await self.mysql_db.get_user(user_id)
            
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_user(self, user_id: str, username: str) -> int:
        """Create a new user in the database"""
        if self.use_mysql:
            return await self.mysql_db.create_user(user_id, username)
            
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
            # Check if card exists
            existing = await self.get_intro_card(data['user_id'])
            
            if existing:
                # Update existing card
                cursor = await db.execute(
                    """UPDATE introduction_cards SET 
                       name=?, age=?, location=?, hobbies=?, favorite_color=?, bio=?,
                       social_media=?, occupation=?, pronouns=?, timezone=?, fun_fact=?,
                       card_template=?, background_style=?, is_public=?, updated_at=CURRENT_TIMESTAMP
                       WHERE user_id=?""",
                    (data.get('name'), data.get('age'), data.get('location'), 
                     data.get('hobbies'), data.get('favorite_color', '#7C3AED'), data.get('bio'),
                     data.get('social_media'), data.get('occupation'), data.get('pronouns'),
                     data.get('timezone'), data.get('fun_fact'), data.get('card_template', 'default'),
                     data.get('background_style', 'gradient'), data.get('is_public', True),
                     data['user_id'])
                )
                await db.commit()
                return existing['id']
            else:
                # Insert new card
                cursor = await db.execute(
                    """INSERT INTO introduction_cards 
                       (user_id, guild_id, name, age, location, hobbies, favorite_color, bio,
                        social_media, occupation, pronouns, timezone, fun_fact, card_template,
                        background_style, is_public) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (data['user_id'], data.get('guild_id'), data.get('name'), data.get('age'), 
                     data.get('location'), data.get('hobbies'), data.get('favorite_color', '#7C3AED'), 
                     data.get('bio'), data.get('social_media'), data.get('occupation'), 
                     data.get('pronouns'), data.get('timezone'), data.get('fun_fact'),
                     data.get('card_template', 'default'), data.get('background_style', 'gradient'),
                     data.get('is_public', True))
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

    async def get_intro_cards_by_guild(self, guild_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all public introduction cards for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM introduction_cards WHERE guild_id = ? AND is_public = TRUE AND is_approved = TRUE ORDER BY created_at DESC LIMIT ?', 
                (guild_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def delete_intro_card(self, user_id: str) -> bool:
        """Delete introduction card for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('DELETE FROM introduction_cards WHERE user_id = ?', (user_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def add_card_interaction(self, card_id: int, user_id: str, interaction_type: str, comment_text: str = None) -> bool:
        """Add interaction to introduction card"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                cursor = await db.execute(
                    """INSERT OR REPLACE INTO intro_card_interactions 
                       (card_id, user_id, interaction_type, comment_text) 
                       VALUES (?, ?, ?, ?)""",
                    (card_id, user_id, interaction_type, comment_text)
                )
                
                # Update likes count if it's a like interaction
                if interaction_type == 'like':
                    await db.execute(
                        'UPDATE introduction_cards SET likes_count = (SELECT COUNT(*) FROM intro_card_interactions WHERE card_id = ? AND interaction_type = "like") WHERE id = ?',
                        (card_id, card_id)
                    )
                elif interaction_type == 'view':
                    await db.execute(
                        'UPDATE introduction_cards SET views_count = views_count + 1 WHERE id = ?',
                        (card_id,)
                    )
                
                await db.commit()
                return True
            except Exception as e:
                logging.error(f"Error adding card interaction: {e}")
                return False

    async def remove_card_interaction(self, card_id: int, user_id: str, interaction_type: str) -> bool:
        """Remove interaction from introduction card"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'DELETE FROM intro_card_interactions WHERE card_id = ? AND user_id = ? AND interaction_type = ?',
                (card_id, user_id, interaction_type)
            )
            
            # Update likes count if it's a like interaction
            if interaction_type == 'like':
                await db.execute(
                    'UPDATE introduction_cards SET likes_count = (SELECT COUNT(*) FROM intro_card_interactions WHERE card_id = ? AND interaction_type = "like") WHERE id = ?',
                    (card_id, card_id)
                )
            
            await db.commit()
            return cursor.rowcount > 0

    async def get_card_interactions(self, card_id: int, interaction_type: str = None) -> List[Dict[str, Any]]:
        """Get interactions for a card"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if interaction_type:
                async with db.execute(
                    'SELECT * FROM intro_card_interactions WHERE card_id = ? AND interaction_type = ? ORDER BY created_at DESC',
                    (card_id, interaction_type)
                ) as cursor:
                    rows = await cursor.fetchall()
            else:
                async with db.execute(
                    'SELECT * FROM intro_card_interactions WHERE card_id = ? ORDER BY created_at DESC',
                    (card_id,)
                ) as cursor:
                    rows = await cursor.fetchall()
            return [dict(row) for row in rows]

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
    
    async def save_server_settings(self, settings: Dict[str, Any]) -> bool:
        """Save server settings"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Check if settings exist
                existing = await self.get_server_settings(settings['guild_id'])
                
                if existing:
                    # Update existing settings
                    await db.execute(
                        """UPDATE server_settings SET 
                           intro_card_theme=?, intro_card_style=?, intro_card_background_url=?
                           WHERE guild_id=?""",
                        (settings.get('intro_card_theme'), settings.get('intro_card_style'), 
                         settings.get('intro_card_background_url'), settings['guild_id'])
                    )
                else:
                    # Insert new settings
                    await db.execute(
                        """INSERT INTO server_settings 
                           (guild_id, intro_card_theme, intro_card_style, intro_card_background_url) 
                           VALUES (?, ?, ?, ?)""",
                        (settings['guild_id'], settings.get('intro_card_theme'), 
                         settings.get('intro_card_style'), settings.get('intro_card_background_url'))
                    )
                
                await db.commit()
                return True
            except Exception as e:
                logging.error(f"Error saving server settings: {e}")
                return False

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

    async def cleanup_expired_cooldowns(self) -> None:
        """Clean up expired cooldowns (older than 24 hours)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM cooldowns WHERE datetime(last_used) < datetime("now", "-24 hours")'
            )
            await db.commit()
    
    # Category Settings Methods
    async def get_category_settings(self, guild_id: str) -> Dict[str, bool]:
        """Get category enable/disable settings for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT category_text_enabled, category_voice_enabled, 
                       category_role_enabled, category_overall_enabled
                FROM server_settings WHERE guild_id = ?
            """, (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'text': bool(row[0]) if row[0] is not None else True,
                        'voice': bool(row[1]) if row[1] is not None else True,
                        'role': bool(row[2]) if row[2] is not None else True,
                        'overall': bool(row[3]) if row[3] is not None else True
                    }
                else:
                    # Return defaults if no settings found
                    return {'text': True, 'voice': True, 'role': True, 'overall': True}
    
    async def set_category_enabled(self, guild_id: str, category: str, enabled: bool) -> bool:
        """Set category enabled/disabled for a guild"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # First ensure the guild has an entry in server_settings
                await db.execute("""
                    INSERT OR IGNORE INTO server_settings (guild_id) VALUES (?)
                """, (guild_id,))
                
                # Update the specific category
                column_map = {
                    'text': 'category_text_enabled',
                    'voice': 'category_voice_enabled',
                    'role': 'category_role_enabled',
                    'overall': 'category_overall_enabled'
                }
                
                if category not in column_map:
                    return False
                
                await db.execute(f"""
                    UPDATE server_settings 
                    SET {column_map[category]} = ?
                    WHERE guild_id = ?
                """, (enabled, guild_id))
                
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Error setting category {category} to {enabled} for guild {guild_id}: {e}")
            return False
    
    async def is_category_enabled(self, guild_id: str, category: str) -> bool:
        """Check if a specific category is enabled for a guild"""
        settings = await self.get_category_settings(guild_id)
        return settings.get(category, True)  # Default to True if not found

    async def close(self):
        """Close database connection (for cleanup)"""
        if self.use_mysql:
            await self.mysql_db.close()
        # SQLite handles connections automatically

# Global database instance
database = Database()