import aiomysql
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from config import config

class MySQLDatabase:
    """Async MySQL database manager for Wonder Discord Bot"""
    
    def __init__(self):
        # MySQL configuration from config
        self.db_config = config.get('database', {})
        self.mysql_config = {
            'host': self.db_config.get('host', 'localhost'),
            'port': self.db_config.get('port', 3306),
            'user': self.db_config.get('username'),
            'password': self.db_config.get('password'),
            'db': self.db_config.get('database'),
            'charset': self.db_config.get('charset', 'utf8mb4'),
            'autocommit': self.db_config.get('autocommit', True),
            'minsize': self.db_config.get('pool_settings', {}).get('minsize', 1),
            'maxsize': self.db_config.get('pool_settings', {}).get('maxsize', 10)
        }
        self.pool = None
    
    async def _get_connection(self):
        """Get MySQL database connection from pool"""
        if self.pool is None:
            self.pool = await aiomysql.create_pool(**self.mysql_config)
        return self.pool.acquire()
        
    async def init(self):
        """Initialize database and create all tables with MySQL syntax"""
        async with await self._get_connection() as db:
            cursor = await db.cursor()
            
            # Users table for economy system
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    username TEXT,
                    balance INT DEFAULT 0,
                    daily_last_claimed TEXT,
                    work_last_used TEXT,
                    total_earned INT DEFAULT 0,
                    created_at DATETIME DEFAULT NOW()
                )
            """)

            # Introduction cards table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS introduction_cards (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id VARCHAR(255) UNIQUE,
                    guild_id VARCHAR(255),
                    name TEXT,
                    age INT,
                    location TEXT,
                    hobbies TEXT,
                    favorite_color VARCHAR(255) DEFAULT '#7C3AED',
                    bio TEXT,
                    social_media TEXT,
                    occupation TEXT,
                    pronouns TEXT,
                    timezone TEXT,
                    fun_fact TEXT,
                    card_template VARCHAR(255) DEFAULT 'default',
                    background_style VARCHAR(255) DEFAULT 'gradient',
                    is_public BOOLEAN DEFAULT TRUE,
                    is_approved BOOLEAN DEFAULT TRUE,
                    likes_count INT DEFAULT 0,
                    views_count INT DEFAULT 0,
                    image_url TEXT,
                    created_at DATETIME DEFAULT NOW(),
                    updated_at DATETIME DEFAULT NOW()
                )
            """)

            # Introduction card interactions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS intro_card_interactions (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    card_id INT,
                    user_id VARCHAR(255),
                    interaction_type VARCHAR(255),
                    comment_text TEXT,
                    created_at DATETIME DEFAULT NOW(),
                    FOREIGN KEY (card_id) REFERENCES introduction_cards (id),
                    UNIQUE KEY unique_interaction (card_id, user_id, interaction_type)
                )
            """)

            # Server settings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS server_settings (
                    guild_id VARCHAR(255) PRIMARY KEY,
                    welcome_channel VARCHAR(255),
                    introduction_channel VARCHAR(255),
                    welcome_message TEXT,
                    intro_card_theme VARCHAR(255) DEFAULT '#7C3AED',
                    intro_card_style VARCHAR(255) DEFAULT 'gradient',
                    intro_card_background_url TEXT,
                    category_text_enabled BOOLEAN DEFAULT TRUE,
                    category_voice_enabled BOOLEAN DEFAULT TRUE,
                    category_role_enabled BOOLEAN DEFAULT TRUE,
                    category_overall_enabled BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT NOW()
                )
            """)

            # Transactions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id VARCHAR(255),
                    transaction_type VARCHAR(255),
                    amount INT,
                    description TEXT,
                    created_at DATETIME DEFAULT NOW()
                )
            """)

            # User inventory table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_inventory (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id VARCHAR(255),
                    item_id VARCHAR(255),
                    quantity INT DEFAULT 1,
                    acquired_at DATETIME DEFAULT NOW()
                )
            """)

            # Active effects table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_effects (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id VARCHAR(255),
                    effect_type VARCHAR(255),
                    multiplier DECIMAL(3,2),
                    expires_at DATETIME,
                    created_at DATETIME DEFAULT NOW()
                )
            """)

            # Cooldowns table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS cooldowns (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id VARCHAR(255),
                    command_type VARCHAR(255),
                    expires_at DATETIME,
                    UNIQUE KEY unique_cooldown (user_id, command_type)
                )
            """)

            # User profiles table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id VARCHAR(255) PRIMARY KEY,
                    display_name VARCHAR(255),
                    bio TEXT,
                    avatar_url TEXT,
                    banner_url TEXT,
                    accent_color VARCHAR(7),
                    created_at DATETIME DEFAULT NOW(),
                    updated_at DATETIME DEFAULT NOW()
                )
            """)

            # Giveaways table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS giveaways (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    guild_id VARCHAR(255),
                    channel_id VARCHAR(255),
                    message_id VARCHAR(255),
                    creator_id VARCHAR(255),
                    title VARCHAR(255),
                    description TEXT,
                    prize TEXT,
                    winner_count INT DEFAULT 1,
                    requirement_type VARCHAR(255) DEFAULT 'none',
                    requirement_data TEXT,
                    ends_at DATETIME,
                    status VARCHAR(255) DEFAULT 'active',
                    created_at DATETIME DEFAULT NOW(),
                    ended_at DATETIME
                )
            """)

            # Giveaway entries table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS giveaway_entries (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    giveaway_id INT,
                    user_id VARCHAR(255),
                    created_at DATETIME DEFAULT NOW(),
                    FOREIGN KEY (giveaway_id) REFERENCES giveaways (id),
                    UNIQUE KEY unique_entry (giveaway_id, user_id)
                )
            """)

            # Giveaway winners table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS giveaway_winners (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    giveaway_id INT,
                    user_id VARCHAR(255),
                    position INT,
                    created_at DATETIME DEFAULT NOW(),
                    FOREIGN KEY (giveaway_id) REFERENCES giveaways (id)
                )
            """)

            # User levels table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_levels (
                    user_id VARCHAR(255) PRIMARY KEY,
                    xp INT DEFAULT 0,
                    level INT DEFAULT 1,
                    messages_sent INT DEFAULT 0,
                    voice_time INT DEFAULT 0,
                    last_xp_gain DATETIME,
                    updated_at DATETIME DEFAULT NOW()
                )
            """)

            # Level role config table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS level_role_config (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    guild_id VARCHAR(255),
                    level INT,
                    role_id VARCHAR(255),
                    created_at DATETIME DEFAULT NOW(),
                    UNIQUE KEY unique_level_role (guild_id, level)
                )
            """)

            # Drop channels table  
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS drop_channels (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    guild_id VARCHAR(255),
                    channel_id VARCHAR(255),
                    drop_type VARCHAR(255) DEFAULT 'wondercoins',
                    is_enabled BOOLEAN DEFAULT TRUE,
                    min_amount INT DEFAULT 10,
                    max_amount INT DEFAULT 100,
                    drop_chance DECIMAL(5,4) DEFAULT 0.0500,
                    cooldown_minutes INT DEFAULT 30,
                    last_drop DATETIME,
                    created_at DATETIME DEFAULT NOW(),
                    UNIQUE KEY unique_channel_drop (guild_id, channel_id, drop_type)
                )
            """)

            # Drop stats table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS drop_stats (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    guild_id VARCHAR(255),
                    channel_id VARCHAR(255),
                    drop_type VARCHAR(255),
                    amount INT,
                    claimed_by VARCHAR(255),
                    claimed_at DATETIME,
                    created_at DATETIME DEFAULT NOW()
                )
            """)

            # User drop stats table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_drop_stats (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id VARCHAR(255),
                    guild_id VARCHAR(255),
                    total_claimed INT DEFAULT 0,
                    total_amount INT DEFAULT 0,
                    last_claim DATETIME,
                    updated_at DATETIME DEFAULT NOW(),
                    UNIQUE KEY unique_user_guild (user_id, guild_id)
                )
            """)

            await cursor.close()
            
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data"""
        async with await self._get_connection() as db:
            cursor = await db.cursor(aiomysql.DictCursor)
            await cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            result = await cursor.fetchone()
            await cursor.close()
            return result
    
    async def create_user(self, user_id: str, username: str) -> int:
        """Create new user"""
        async with await self._get_connection() as db:
            cursor = await db.cursor()
            await cursor.execute(
                "INSERT IGNORE INTO users (user_id, username) VALUES (%s, %s)",
                (user_id, username)
            )
            rowcount = cursor.rowcount
            await cursor.close()
            return rowcount
    
    async def update_balance(self, user_id: str, amount: int) -> int:
        """Update user balance"""
        async with await self._get_connection() as db:
            cursor = await db.cursor()
            await cursor.execute(
                "UPDATE users SET balance = balance + %s, total_earned = total_earned + %s WHERE user_id = %s",
                (amount, max(0, amount), user_id)
            )
            rowcount = cursor.rowcount
            await cursor.close()
            return rowcount
    
    async def set_balance(self, user_id: str, amount: int) -> int:
        """Set user balance"""
        async with await self._get_connection() as db:
            cursor = await db.cursor()
            await cursor.execute(
                "UPDATE users SET balance = %s WHERE user_id = %s",
                (amount, user_id)
            )
            rowcount = cursor.rowcount
            await cursor.close()
            return rowcount
    
    async def update_daily_claim(self, user_id: str) -> int:
        """Update daily claim timestamp"""
        now = datetime.now().isoformat()
        async with await self._get_connection() as db:
            cursor = await db.cursor()
            await cursor.execute(
                "UPDATE users SET daily_last_claimed = %s WHERE user_id = %s",
                (now, user_id)
            )
            await cursor.close()
            return cursor.rowcount
    
    async def update_work_claim(self, user_id: str) -> int:
        """Update work claim timestamp"""
        now = datetime.now().isoformat()
        async with await self._get_connection() as db:
            cursor = await db.cursor()
            await cursor.execute(
                "UPDATE users SET work_last_used = %s WHERE user_id = %s",
                (now, user_id)
            )
            await cursor.close()
            return cursor.rowcount
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    # Leveling system methods
    async def get_user_level(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user level data"""
        async with await self._get_connection() as db:
            cursor = await db.cursor(aiomysql.DictCursor)
            await cursor.execute('SELECT * FROM user_levels WHERE user_id = %s', (user_id,))
            result = await cursor.fetchone()
            await cursor.close()
            return result

    async def update_user_xp(self, user_id: str, xp_gain: int) -> Tuple[int, bool]:
        """Update user XP and return new level and whether they leveled up"""
        async with await self._get_connection() as db:
            cursor = await db.cursor()
            
            # Get current data
            await cursor.execute(
                'SELECT xp, level FROM user_levels WHERE user_id = %s', (user_id,)
            )
            current = await cursor.fetchone()
            
            if not current:
                # Create new user level record
                await cursor.execute(
                    'INSERT INTO user_levels (user_id, xp, level) VALUES (%s, %s, %s)',
                    (user_id, xp_gain, 1)
                )
                await cursor.close()
                return 1, False
            
            current_xp, current_level = current
            new_xp = current_xp + xp_gain
            new_level = self._calculate_level(new_xp)
            leveled_up = new_level > current_level
            
            await cursor.execute(
                'UPDATE user_levels SET xp = %s, level = %s, last_xp_gain = NOW() WHERE user_id = %s',
                (new_xp, new_level, user_id)
            )
            await cursor.close()
            
            return new_level, leveled_up

    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP"""
        # Simple level calculation: level = sqrt(xp / 100)
        import math
        return max(1, int(math.sqrt(xp / 100)) + 1)