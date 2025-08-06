const database = require('./database');
const config = require('../config.json');

class CooldownManager {
    constructor() {
        // Cooldown durations in minutes
        this.cooldowns = {
            daily: 24 * 60, // 24 hours
            work: 60, // 1 hour
            coinflip: 2, // 2 minutes
            dice: 3, // 3 minutes
            slots: 5, // 5 minutes
            mystery_box: 30, // 30 minutes
            use_item: 1 // 1 minute between item uses
        };
    }

    // Check if user is on cooldown for a command
    async checkCooldown(userId, commandType) {
        try {
            // Check for work energy effect that removes work cooldown
            if (commandType === 'work') {
                const hasWorkEnergy = await database.hasActiveEffect(userId, 'work_cooldown_reset');
                if (hasWorkEnergy) {
                    return { onCooldown: false, timeLeft: 0 };
                }
            }

            const cooldownTime = this.cooldowns[commandType];
            if (!cooldownTime) {
                return { onCooldown: false, timeLeft: 0 };
            }

            const cooldownData = await database.checkCooldown(userId, commandType, cooldownTime);
            return cooldownData;
        } catch (error) {
            console.error('Error checking cooldown:', error);
            return { onCooldown: false, timeLeft: 0 };
        }
    }

    // Set cooldown for a command
    async setCooldown(userId, commandType) {
        try {
            await database.setCooldown(userId, commandType);
        } catch (error) {
            console.error('Error setting cooldown:', error);
        }
    }

    // Format time remaining for display
    formatTimeLeft(minutes) {
        if (minutes >= 60) {
            const hours = Math.floor(minutes / 60);
            const remainingMinutes = minutes % 60;
            if (remainingMinutes === 0) {
                return `${hours}h`;
            }
            return `${hours}h ${remainingMinutes}m`;
        }
        return `${minutes}m`;
    }

    // Create cooldown error message
    createCooldownMessage(commandType, timeLeft) {
        const timeFormatted = this.formatTimeLeft(timeLeft);
        const messages = {
            daily: `⏰ You can claim your daily reward in **${timeFormatted}**!`,
            work: `⏰ You can work again in **${timeFormatted}**! Use ⚡ Work Energy to skip this cooldown.`,
            coinflip: `🪙 Coin flip is on cooldown for **${timeFormatted}**. Take a break!`,
            dice: `🎲 Dice game is on cooldown for **${timeFormatted}**. Try again soon!`,
            slots: `🎰 Slot machine is on cooldown for **${timeFormatted}**. Patience pays off!`,
            mystery_box: `📦 You can open another mystery box in **${timeFormatted}**!`,
            use_item: `⏱️ You can use another item in **${timeFormatted}**!`
        };

        return messages[commandType] || `⏰ Command is on cooldown for **${timeFormatted}**!`;
    }

    // Check if user can bypass cooldown with premium perks
    async canBypassCooldown(userId, commandType, member) {
        try {
            // Premium members get reduced game cooldowns
            if (['coinflip', 'dice', 'slots'].includes(commandType)) {
                const isPremium = member.roles.cache.has(process.env.PREMIUM_ROLE_ID);
                if (isPremium) {
                    // Reduce cooldown by 50% for premium members
                    const cooldown = await database.getCooldown(userId, commandType);
                    if (cooldown) {
                        const lastUsed = new Date(cooldown.last_used);
                        const now = new Date();
                        const timeDiff = now - lastUsed;
                        const minutesPassed = Math.floor(timeDiff / (1000 * 60));
                        const reducedCooldown = Math.floor(this.cooldowns[commandType] * 0.5);
                        
                        if (minutesPassed >= reducedCooldown) {
                            return true;
                        }
                    }
                }
            }

            return false;
        } catch (error) {
            console.error('Error checking cooldown bypass:', error);
            return false;
        }
    }

    // Get all active cooldowns for a user
    async getUserCooldowns(userId) {
        try {
            const cooldowns = {};
            for (const commandType of Object.keys(this.cooldowns)) {
                const cooldownData = await this.checkCooldown(userId, commandType);
                if (cooldownData.onCooldown) {
                    cooldowns[commandType] = {
                        timeLeft: cooldownData.timeLeft,
                        formatted: this.formatTimeLeft(cooldownData.timeLeft)
                    };
                }
            }
            return cooldowns;
        } catch (error) {
            console.error('Error getting user cooldowns:', error);
            return {};
        }
    }

    // Apply gambling luck effect
    async applyGamblingLuck(userId) {
        try {
            const hasLuck = await database.hasActiveEffect(userId, 'gambling_luck');
            if (hasLuck) {
                // Use one charge of the luck effect
                await database.useEffect(userId, 'gambling_luck');
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error applying gambling luck:', error);
            return false;
        }
    }

    // Check if user has experience boost
    async hasExperienceBoost(userId) {
        try {
            const hasBoost = await database.hasActiveEffect(userId, 'exp_boost');
            if (hasBoost) {
                await database.useEffect(userId, 'exp_boost');
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error checking experience boost:', error);
            return false;
        }
    }

    // Check if user has daily double effect
    async hasDailyDouble(userId) {
        try {
            const hasDouble = await database.hasActiveEffect(userId, 'daily_double');
            if (hasDouble) {
                // Remove the effect after use (it's single use)
                await database.db.run(
                    'DELETE FROM active_effects WHERE user_id = ? AND effect_type = ?',
                    [userId, 'daily_double']
                );
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error checking daily double:', error);
            return false;
        }
    }

    // Clean up expired effects (run periodically)
    async cleanupExpiredEffects() {
        try {
            await database.removeExpiredEffects();
            console.log('🧹 Cleaned up expired effects');
        } catch (error) {
            console.error('Error cleaning up expired effects:', error);
        }
    }

    // Get cooldown reduction for premium users
    getCooldownReduction(commandType, member) {
        if (!member) return 1;

        const isPremium = member.roles.cache.has(process.env.PREMIUM_ROLE_ID);
        const isBooster = member.roles.cache.has(process.env.BOOSTER_ROLE_ID);

        // Premium gets better reductions
        if (isPremium && ['coinflip', 'dice', 'slots'].includes(commandType)) {
            return 0.5; // 50% cooldown reduction
        }

        // Boosters get moderate reductions
        if (isBooster && ['coinflip', 'dice', 'slots'].includes(commandType)) {
            return 0.75; // 25% cooldown reduction
        }

        return 1; // No reduction
    }

    // Calculate actual cooldown time with reductions
    async getActualCooldown(userId, commandType, member) {
        try {
            const baseCooldown = this.cooldowns[commandType];
            if (!baseCooldown) return 0;

            const reduction = this.getCooldownReduction(commandType, member);
            const actualCooldown = Math.floor(baseCooldown * reduction);

            return actualCooldown;
        } catch (error) {
            console.error('Error calculating actual cooldown:', error);
            return this.cooldowns[commandType] || 0;
        }
    }
}

module.exports = CooldownManager;