const sqlite3 = require('sqlite3').verbose();
const path = require('path');

class Database {
    constructor() {
        this.db = new sqlite3.Database(path.join(__dirname, '..', 'wonder.db'));
        this.init();
    }

    init() {
        // Users table for economy system
        this.db.run(`
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 0,
                daily_last_claimed TEXT,
                work_last_used TEXT,
                total_earned INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Introduction cards table
        this.db.run(`
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
        `);

        // Server settings table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id TEXT PRIMARY KEY,
                welcome_channel TEXT,
                introduction_channel TEXT,
                welcome_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Transaction history
        this.db.run(`
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                type TEXT,
                amount INTEGER,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // User inventory table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS user_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                item_id TEXT,
                quantity INTEGER DEFAULT 1,
                acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Active effects table for consumables
        this.db.run(`
            CREATE TABLE IF NOT EXISTS active_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                effect_type TEXT,
                duration_minutes INTEGER,
                uses_remaining INTEGER DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            )
        `);

        // Cooldowns table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS cooldowns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                command_type TEXT,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, command_type)
            )
        `);

        // User profiles table for customization
        this.db.run(`
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                custom_title TEXT,
                name_color TEXT,
                card_border TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Giveaways table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS giveaways (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                channel_id TEXT,
                message_id TEXT,
                title TEXT,
                description TEXT,
                prize TEXT,
                winner_count INTEGER DEFAULT 1,
                duration INTEGER,
                requirements TEXT,
                created_by TEXT,
                restrict_winners INTEGER DEFAULT 1,
                ended INTEGER DEFAULT 0,
                cancelled INTEGER DEFAULT 0,
                winners TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Giveaway entries table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS giveaway_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                giveaway_id INTEGER,
                user_id TEXT,
                entry_weight REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(giveaway_id, user_id)
            )
        `);

        // Giveaway winners history table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS giveaway_winners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                giveaway_id INTEGER,
                user_id TEXT,
                won_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // User levels table for leveling system
        this.db.run(`
            CREATE TABLE IF NOT EXISTS user_levels (
                user_id TEXT PRIMARY KEY,
                text_xp INTEGER DEFAULT 0,
                text_level INTEGER DEFAULT 1,
                voice_xp INTEGER DEFAULT 0,
                voice_level INTEGER DEFAULT 1,
                role_xp INTEGER DEFAULT 0,
                role_level INTEGER DEFAULT 1,
                total_xp INTEGER DEFAULT 0,
                overall_level INTEGER DEFAULT 1,
                voice_time_total INTEGER DEFAULT 0,
                last_message_xp DATETIME,
                last_voice_xp DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Level rewards history table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS level_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                level_type TEXT,
                level INTEGER,
                reward_type TEXT,
                reward_data TEXT,
                claimed INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Voice sessions table for tracking voice activity
        this.db.run(`
            CREATE TABLE IF NOT EXISTS voice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                channel_id TEXT,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                left_at DATETIME,
                duration_minutes INTEGER,
                xp_earned INTEGER DEFAULT 0
            )
        `);

        // Level role rewards configuration table
        this.db.run(`
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
        `);
 cursor/tambahkan-fitur-leveling-roles-dan-level-d928

        // WonderCoins drop channels table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS drop_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                channel_id TEXT,
                created_by TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, channel_id)
            )
        `);

        // WonderCoins drop statistics table
        this.db.run(`
            CREATE TABLE IF NOT EXISTS drop_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                user_id TEXT,
                amount INTEGER,
                rarity TEXT,
                collection_type TEXT,
                drop_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // User drop statistics summary table
        this.db.run(`
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
        `);

 main
    }

    // User economy methods
    async getUser(userId) {
        return new Promise((resolve, reject) => {
            this.db.get('SELECT * FROM users WHERE user_id = ?', [userId], (err, row) => {
                if (err) reject(err);
                resolve(row);
            });
        });
    }

    async createUser(userId, username) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
                [userId, username],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async updateBalance(userId, amount) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE users SET balance = balance + ? WHERE user_id = ?',
                [amount, userId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async setBalance(userId, amount) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE users SET balance = ? WHERE user_id = ?',
                [amount, userId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async updateDailyClaim(userId) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            this.db.run(
                'UPDATE users SET daily_last_claimed = ? WHERE user_id = ?',
                [now, userId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async updateWorkClaim(userId) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            this.db.run(
                'UPDATE users SET work_last_used = ? WHERE user_id = ?',
                [now, userId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    // Introduction card methods
    async saveIntroCard(data) {
        return new Promise((resolve, reject) => {
            this.db.run(
                `INSERT OR REPLACE INTO introduction_cards 
                 (user_id, name, age, location, hobbies, favorite_color, bio) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)`,
                [data.userId, data.name, data.age, data.location, data.hobbies, data.favoriteColor, data.bio],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async getIntroCard(userId) {
        return new Promise((resolve, reject) => {
            this.db.get('SELECT * FROM introduction_cards WHERE user_id = ?', [userId], (err, row) => {
                if (err) reject(err);
                resolve(row);
            });
        });
    }

    // Transaction methods
    async addTransaction(userId, type, amount, description) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
                [userId, type, amount, description],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    // Server settings methods
    async getServerSettings(guildId) {
        return new Promise((resolve, reject) => {
            this.db.get('SELECT * FROM server_settings WHERE guild_id = ?', [guildId], (err, row) => {
                if (err) reject(err);
                resolve(row);
            });
        });
    }

    async updateServerSettings(guildId, settings) {
        return new Promise((resolve, reject) => {
            this.db.run(
                `INSERT OR REPLACE INTO server_settings 
                 (guild_id, welcome_channel, introduction_channel, welcome_message) 
                 VALUES (?, ?, ?, ?)`,
                [guildId, settings.welcomeChannel, settings.introductionChannel, settings.welcomeMessage],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    // Leaderboard methods
    async getTopUsers(limit = 10) {
        return new Promise((resolve, reject) => {
            this.db.all(
                'SELECT user_id, username, balance FROM users ORDER BY balance DESC LIMIT ?',
                [limit],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows);
                }
            );
        });
    }

    // Inventory methods
    async addItemToInventory(userId, itemId, quantity = 1) {
        return new Promise((resolve, reject) => {
            // Check if item already exists in inventory
            this.db.get(
                'SELECT * FROM user_inventory WHERE user_id = ? AND item_id = ?',
                [userId, itemId],
                (err, row) => {
                    if (err) reject(err);
                    
                    if (row) {
                        // Update existing quantity
                        this.db.run(
                            'UPDATE user_inventory SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?',
                            [quantity, userId, itemId],
                            function(err) {
                                if (err) reject(err);
                                resolve(this.changes);
                            }
                        );
                    } else {
                        // Add new item
                        this.db.run(
                            'INSERT INTO user_inventory (user_id, item_id, quantity) VALUES (?, ?, ?)',
                            [userId, itemId, quantity],
                            function(err) {
                                if (err) reject(err);
                                resolve(this.lastID);
                            }
                        );
                    }
                }
            );
        });
    }

    async removeItemFromInventory(userId, itemId, quantity = 1) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE user_inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ? AND quantity >= ?',
                [quantity, userId, itemId, quantity],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async getUserInventory(userId) {
        return new Promise((resolve, reject) => {
            this.db.all(
                'SELECT * FROM user_inventory WHERE user_id = ? AND quantity > 0 ORDER BY acquired_at DESC',
                [userId],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows);
                }
            );
        });
    }

    async hasItem(userId, itemId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT quantity FROM user_inventory WHERE user_id = ? AND item_id = ? AND quantity > 0',
                [userId, itemId],
                (err, row) => {
                    if (err) reject(err);
                    resolve(row ? row.quantity : 0);
                }
            );
        });
    }

    // Active effects methods
    async addActiveEffect(userId, effectType, durationMinutes, usesRemaining = null) {
        return new Promise((resolve, reject) => {
            const expiresAt = new Date();
            expiresAt.setMinutes(expiresAt.getMinutes() + durationMinutes);
            
            this.db.run(
                'INSERT INTO active_effects (user_id, effect_type, duration_minutes, uses_remaining, expires_at) VALUES (?, ?, ?, ?, ?)',
                [userId, effectType, durationMinutes, usesRemaining, expiresAt.toISOString()],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async getActiveEffects(userId) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            this.db.all(
                'SELECT * FROM active_effects WHERE user_id = ? AND (expires_at > ? OR uses_remaining > 0)',
                [userId, now],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows);
                }
            );
        });
    }

    async hasActiveEffect(userId, effectType) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            this.db.get(
                'SELECT * FROM active_effects WHERE user_id = ? AND effect_type = ? AND (expires_at > ? OR uses_remaining > 0)',
                [userId, effectType, now],
                (err, row) => {
                    if (err) reject(err);
                    resolve(row);
                }
            );
        });
    }

    async useEffect(userId, effectType) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE active_effects SET uses_remaining = uses_remaining - 1 WHERE user_id = ? AND effect_type = ? AND uses_remaining > 0',
                [userId, effectType],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async removeExpiredEffects() {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            this.db.run(
                'DELETE FROM active_effects WHERE expires_at <= ? AND (uses_remaining IS NULL OR uses_remaining <= 0)',
                [now],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    // Cooldown methods
    async setCooldown(userId, commandType) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            this.db.run(
                'INSERT OR REPLACE INTO cooldowns (user_id, command_type, last_used) VALUES (?, ?, ?)',
                [userId, commandType, now],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async getCooldown(userId, commandType) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT * FROM cooldowns WHERE user_id = ? AND command_type = ?',
                [userId, commandType],
                (err, row) => {
                    if (err) reject(err);
                    resolve(row);
                }
            );
        });
    }

    async checkCooldown(userId, commandType, cooldownMinutes) {
        return new Promise((resolve, reject) => {
            this.getCooldown(userId, commandType).then(cooldown => {
                if (!cooldown) {
                    resolve({ onCooldown: false, timeLeft: 0 });
                    return;
                }

                const lastUsed = new Date(cooldown.last_used);
                const now = new Date();
                const timeDiff = now - lastUsed;
                const minutesPassed = Math.floor(timeDiff / (1000 * 60));

                if (minutesPassed >= cooldownMinutes) {
                    resolve({ onCooldown: false, timeLeft: 0 });
                } else {
                    const timeLeft = cooldownMinutes - minutesPassed;
                    resolve({ onCooldown: true, timeLeft: timeLeft });
                }
            }).catch(reject);
        });
    }

    // User profile methods
    async getUserProfile(userId) {
        return new Promise((resolve, reject) => {
            this.db.get('SELECT * FROM user_profiles WHERE user_id = ?', [userId], (err, row) => {
                if (err) reject(err);
                resolve(row);
            });
        });
    }

    async updateUserProfile(userId, profileData) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT OR REPLACE INTO user_profiles (user_id, custom_title, name_color, card_border) VALUES (?, ?, ?, ?)',
                [userId, profileData.customTitle, profileData.nameColor, profileData.cardBorder],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    // Giveaway methods
    async createGiveaway(giveawayData) {
        return new Promise((resolve, reject) => {
            this.db.run(
                `INSERT INTO giveaways (guild_id, channel_id, title, description, prize, winner_count, duration, requirements, created_by, restrict_winners) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [
                    giveawayData.guildId,
                    giveawayData.channelId,
                    giveawayData.title,
                    giveawayData.description,
                    giveawayData.prize,
                    giveawayData.winnerCount,
                    giveawayData.duration,
                    JSON.stringify(giveawayData.requirements),
                    giveawayData.createdBy,
                    giveawayData.restrictWinners ? 1 : 0
                ],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async getGiveaway(giveawayId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT *, requirements as requirements_json FROM giveaways WHERE id = ?',
                [giveawayId],
                (err, row) => {
                    if (err) reject(err);
                    if (row) {
                        row.requirements = JSON.parse(row.requirements_json || '{}');
                        row.winners = JSON.parse(row.winners || '[]');
                    }
                    resolve(row);
                }
            );
        });
    }

    async updateGiveawayMessageId(giveawayId, messageId) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE giveaways SET message_id = ? WHERE id = ?',
                [messageId, giveawayId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async addGiveawayEntry(userId, giveawayId, entryWeight = 1.0) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT INTO giveaway_entries (giveaway_id, user_id, entry_weight) VALUES (?, ?, ?)',
                [giveawayId, userId, entryWeight],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async hasEnteredGiveaway(userId, giveawayId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT id FROM giveaway_entries WHERE giveaway_id = ? AND user_id = ?',
                [giveawayId, userId],
                (err, row) => {
                    if (err) reject(err);
                    resolve(!!row);
                }
            );
        });
    }

    async getGiveawayEntries(giveawayId) {
        return new Promise((resolve, reject) => {
            this.db.all(
                'SELECT * FROM giveaway_entries WHERE giveaway_id = ?',
                [giveawayId],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows);
                }
            );
        });
    }

    async getGiveawayEntryCount(giveawayId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT COUNT(*) as count FROM giveaway_entries WHERE giveaway_id = ?',
                [giveawayId],
                (err, row) => {
                    if (err) reject(err);
                    resolve(row.count);
                }
            );
        });
    }

    async endGiveaway(giveawayId, winners) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE giveaways SET ended = 1, winners = ? WHERE id = ?',
                [JSON.stringify(winners), giveawayId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async cancelGiveaway(giveawayId) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE giveaways SET cancelled = 1 WHERE id = ?',
                [giveawayId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async recordGiveawayWin(userId, giveawayId) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT INTO giveaway_winners (giveaway_id, user_id) VALUES (?, ?)',
                [giveawayId, userId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async getRecentGiveawayWin(userId, minutesBack) {
        return new Promise((resolve, reject) => {
            const cutoffTime = new Date();
            cutoffTime.setMinutes(cutoffTime.getMinutes() - minutesBack);
            
            this.db.get(
                `SELECT *, 
                 (julianday('now') - julianday(won_at)) * 24 * 60 as minutesAgo 
                 FROM giveaway_winners 
                 WHERE user_id = ? AND won_at > ? 
                 ORDER BY won_at DESC LIMIT 1`,
                [userId, cutoffTime.toISOString()],
                (err, row) => {
                    if (err) reject(err);
                    resolve(row);
                }
            );
        });
    }

    async updateGiveawayWinners(giveawayId, winners) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE giveaways SET winners = ? WHERE id = ?',
                [JSON.stringify(winners), giveawayId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    // ================== LEVELING SYSTEM METHODS ==================

    // Get or create user levels record
    async getUserLevels(userId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT * FROM user_levels WHERE user_id = ?',
                [userId],
                async (err, row) => {
                    if (err) reject(err);
                    if (!row) {
                        // Create new levels record
                        try {
                            await this.createUserLevels(userId);
                            // Get the newly created record
                            this.db.get(
                                'SELECT * FROM user_levels WHERE user_id = ?',
                                [userId],
                                (err, newRow) => {
                                    if (err) reject(err);
                                    resolve(newRow);
                                }
                            );
                        } catch (error) {
                            reject(error);
                        }
                    } else {
                        resolve(row);
                    }
                }
            );
        });
    }

    // Create new user levels record
    async createUserLevels(userId) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT OR IGNORE INTO user_levels (user_id) VALUES (?)',
                [userId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    // Add XP to a specific type (text, voice, role)
    async addXP(userId, xpType, amount) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            let query, params;

            switch (xpType) {
                case 'text':
                    query = `UPDATE user_levels SET 
                        text_xp = text_xp + ?, 
                        total_xp = total_xp + ?,
                        last_message_xp = ?,
                        updated_at = ?
                        WHERE user_id = ?`;
                    params = [amount, amount, now, now, userId];
                    break;
                case 'voice':
                    query = `UPDATE user_levels SET 
                        voice_xp = voice_xp + ?, 
                        total_xp = total_xp + ?,
                        last_voice_xp = ?,
                        updated_at = ?
                        WHERE user_id = ?`;
                    params = [amount, amount, now, now, userId];
                    break;
                case 'role':
                    query = `UPDATE user_levels SET 
                        role_xp = role_xp + ?, 
                        total_xp = total_xp + ?,
                        updated_at = ?
                        WHERE user_id = ?`;
                    params = [amount, amount, now, userId];
                    break;
                default:
                    reject(new Error('Invalid XP type'));
                    return;
            }

            this.db.run(query, params, function(err) {
                if (err) reject(err);
                resolve(this.changes);
            });
        });
    }

    // Update level for specific type
    async updateLevel(userId, levelType, newLevel) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            let column;

            switch (levelType) {
                case 'text':
                    column = 'text_level';
                    break;
                case 'voice':
                    column = 'voice_level';
                    break;
                case 'role':
                    column = 'role_level';
                    break;
                case 'overall':
                    column = 'overall_level';
                    break;
                default:
                    reject(new Error('Invalid level type'));
                    return;
            }

            this.db.run(
                `UPDATE user_levels SET ${column} = ?, updated_at = ? WHERE user_id = ?`,
                [newLevel, now, userId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    // Add voice time to user
    async addVoiceTime(userId, minutes) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            this.db.run(
                'UPDATE user_levels SET voice_time_total = voice_time_total + ?, updated_at = ? WHERE user_id = ?',
                [minutes, now, userId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    // Get top users by level type
    async getTopUsers(levelType = 'overall', limit = 10) {
        return new Promise((resolve, reject) => {
            let orderColumn;
            switch (levelType) {
                case 'text':
                    orderColumn = 'text_level DESC, text_xp DESC';
                    break;
                case 'voice':
                    orderColumn = 'voice_level DESC, voice_xp DESC';
                    break;
                case 'role':
                    orderColumn = 'role_level DESC, role_xp DESC';
                    break;
                case 'overall':
                    orderColumn = 'overall_level DESC, total_xp DESC';
                    break;
                default:
                    orderColumn = 'total_xp DESC';
            }

            this.db.all(
                `SELECT ul.*, u.username 
                 FROM user_levels ul 
                 JOIN users u ON ul.user_id = u.user_id 
                 ORDER BY ${orderColumn} 
                 LIMIT ?`,
                [limit],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows || []);
                }
            );
        });
    }

    // Create level reward
    async createLevelReward(userId, levelType, level, rewardType, rewardData) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT INTO level_rewards (user_id, level_type, level, reward_type, reward_data) VALUES (?, ?, ?, ?, ?)',
                [userId, levelType, level, rewardType, JSON.stringify(rewardData)],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    // Get unclaimed rewards for user
    async getUnclaimedRewards(userId) {
        return new Promise((resolve, reject) => {
            this.db.all(
                'SELECT * FROM level_rewards WHERE user_id = ? AND claimed = 0 ORDER BY created_at DESC',
                [userId],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows || []);
                }
            );
        });
    }

    // Claim level reward
    async claimLevelReward(rewardId) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'UPDATE level_rewards SET claimed = 1 WHERE id = ?',
                [rewardId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    // Start voice session
    async startVoiceSession(userId, channelId) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT INTO voice_sessions (user_id, channel_id) VALUES (?, ?)',
                [userId, channelId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    // End voice session and calculate XP
    async endVoiceSession(sessionId, xpEarned) {
        return new Promise((resolve, reject) => {
            const now = new Date().toISOString();
            this.db.run(
                `UPDATE voice_sessions SET 
                 left_at = ?, 
                 duration_minutes = ROUND((julianday(?) - julianday(joined_at)) * 24 * 60), 
                 xp_earned = ? 
                 WHERE id = ?`,
                [now, now, xpEarned, sessionId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    // Get active voice session for user
    async getActiveVoiceSession(userId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT * FROM voice_sessions WHERE user_id = ? AND left_at IS NULL ORDER BY joined_at DESC LIMIT 1',
                [userId],
                (err, row) => {
                    if (err) reject(err);
                    resolve(row);
                }
            );
        });
    }

    // ================== LEVEL ROLE CONFIGURATION METHODS ==================

    // Set role reward for specific level and type
    async setLevelRoleReward(levelType, level, roleId, roleName, createdBy) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT OR REPLACE INTO level_role_config (level_type, level, role_id, role_name, created_by) VALUES (?, ?, ?, ?, ?)',
                [levelType, level, roleId, roleName, createdBy],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    // Get role reward for specific level and type
    async getLevelRoleReward(levelType, level) {
        return new Promise((resolve, reject) => {
            this.db.get(
                'SELECT * FROM level_role_config WHERE level_type = ? AND level = ?',
                [levelType, level],
                (err, row) => {
                    if (err) reject(err);
                    resolve(row);
                }
            );
        });
    }

    // Get all role rewards for a level type
    async getAllLevelRoleRewards(levelType = null) {
        return new Promise((resolve, reject) => {
            let query = 'SELECT * FROM level_role_config';
            let params = [];
            
            if (levelType) {
                query += ' WHERE level_type = ?';
                params.push(levelType);
            }
            
            query += ' ORDER BY level_type, level';
            
            this.db.all(query, params, (err, rows) => {
                if (err) reject(err);
                resolve(rows || []);
            });
        });
    }

    // Remove role reward for specific level and type
    async removeLevelRoleReward(levelType, level) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'DELETE FROM level_role_config WHERE level_type = ? AND level = ?',
                [levelType, level],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async getUserGiveawayHistory(userId, limit = 10) {
        return new Promise((resolve, reject) => {
            this.db.all(
                `SELECT g.*, gw.won_at 
                 FROM giveaway_winners gw 
                 JOIN giveaways g ON gw.giveaway_id = g.id 
                 WHERE gw.user_id = ? 
                 ORDER BY gw.won_at DESC 
                 LIMIT ?`,
                [userId, limit],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows);
                }
            );
        });
    }

    async getServerGiveaways(guildId, includeEnded = false, limit = 10) {
        return new Promise((resolve, reject) => {
            let query = 'SELECT * FROM giveaways WHERE guild_id = ? AND cancelled = 0';
            if (!includeEnded) {
                query += ' AND ended = 0';
            }
            query += ' ORDER BY created_at DESC LIMIT ?';

            this.db.all(query, [guildId, limit], (err, rows) => {
                if (err) reject(err);
                if (rows) {
                    rows.forEach(row => {
                        row.requirements = JSON.parse(row.requirements || '{}');
                        row.winners = JSON.parse(row.winners || '[]');
                    });
                }
                resolve(rows);
            });
        });
    }

    // WonderCoins Drop System Methods
    async addDropChannel(guildId, channelId, createdBy = null) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT OR IGNORE INTO drop_channels (guild_id, channel_id, created_by) VALUES (?, ?, ?)',
                [guildId, channelId, createdBy],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async removeDropChannel(guildId, channelId) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'DELETE FROM drop_channels WHERE guild_id = ? AND channel_id = ?',
                [guildId, channelId],
                function(err) {
                    if (err) reject(err);
                    resolve(this.changes);
                }
            );
        });
    }

    async getDropChannels(guildId = null) {
        return new Promise((resolve, reject) => {
            let query = 'SELECT * FROM drop_channels';
            let params = [];
            
            if (guildId) {
                query += ' WHERE guild_id = ?';
                params = [guildId];
            }
            
            this.db.all(query, params, (err, rows) => {
                if (err) reject(err);
                resolve(rows || []);
            });
        });
    }

    async addDropStat(guildId, userId, amount, rarity, collectionType) {
        return new Promise((resolve, reject) => {
            this.db.run(
                'INSERT INTO drop_stats (guild_id, user_id, amount, rarity, collection_type) VALUES (?, ?, ?, ?, ?)',
                [guildId, userId, amount, rarity, collectionType],
                function(err) {
                    if (err) reject(err);
                    resolve(this.lastID);
                }
            );
        });
    }

    async updateUserDropStats(userId, amount, rarity) {
        return new Promise((resolve, reject) => {
            // First check if user exists in drop stats
            this.db.get('SELECT * FROM user_drop_stats WHERE user_id = ?', [userId], (err, row) => {
                if (err) {
                    reject(err);
                    return;
                }

                const rarityField = `${rarity}_drops`;
                const now = new Date().toISOString();

                if (row) {
                    // Update existing record
                    const newTotal = row.total_collected + amount;
                    const newDrops = row.total_drops + 1;
                    const newRarityCount = row[rarityField] + 1;
                    const newBest = Math.max(row.best_drop, amount);

                    this.db.run(`
                        UPDATE user_drop_stats 
                        SET total_collected = ?, total_drops = ?, ${rarityField} = ?, last_drop = ?, best_drop = ?
                        WHERE user_id = ?`,
                        [newTotal, newDrops, newRarityCount, now, newBest, userId],
                        function(err) {
                            if (err) reject(err);
                            resolve(this.changes);
                        }
                    );
                } else {
                    // Create new record
                    this.db.run(`
                        INSERT INTO user_drop_stats 
                        (user_id, total_collected, total_drops, ${rarityField}, last_drop, best_drop)
                        VALUES (?, ?, 1, 1, ?, ?)`,
                        [userId, amount, now, amount],
                        function(err) {
                            if (err) reject(err);
                            resolve(this.lastID);
                        }
                    );
                }
            });
        });
    }

    async getUserDropStats(userId) {
        return new Promise((resolve, reject) => {
            this.db.get('SELECT * FROM user_drop_stats WHERE user_id = ?', [userId], (err, row) => {
                if (err) reject(err);
                resolve(row);
            });
        });
    }

    async getDropStats(guildId) {
        return new Promise((resolve, reject) => {
            this.db.all(`
                SELECT 
                    COUNT(*) as total_drops,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    COUNT(DISTINCT user_id) as unique_collectors,
                    rarity,
                    COUNT(*) as rarity_count
                FROM drop_stats 
                WHERE guild_id = ? 
                GROUP BY rarity
                UNION ALL
                SELECT 
                    COUNT(*) as total_drops,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    COUNT(DISTINCT user_id) as unique_collectors,
                    'ALL' as rarity,
                    COUNT(*) as rarity_count
                FROM drop_stats 
                WHERE guild_id = ?`,
                [guildId, guildId],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows || []);
                }
            );
        });
    }

    async getTopDropCollectors(guildId, limit = 10) {
        return new Promise((resolve, reject) => {
            this.db.all(`
                SELECT 
                    user_id,
                    SUM(amount) as total_collected,
                    COUNT(*) as total_drops,
                    MAX(amount) as best_drop
                FROM drop_stats 
                WHERE guild_id = ? 
                GROUP BY user_id 
                ORDER BY total_collected DESC 
                LIMIT ?`,
                [guildId, limit],
                (err, rows) => {
                    if (err) reject(err);
                    resolve(rows || []);
                }
            );
        });
    }
}

module.exports = new Database();