const { EmbedBuilder } = require('discord.js');
const database = require('./database');
const config = require('../config.json');
const LuxuryDesign = require('./utils/luxury-design');

class LevelingSystem {
    constructor(client) {
        this.client = client;
        this.voiceSessions = new Map(); // Track active voice sessions
        this.xpCooldowns = new Map(); // Text XP cooldowns
        this.design = new LuxuryDesign(); // Luxury Design utility
        
        // XP Configuration
        this.xpConfig = {
            text: {
                base: 15,
                bonus: 5,
                cooldown: 60000, // 1 minute cooldown between XP gains
                maxPerMessage: 25
            },
            voice: {
                base: 10, // XP per minute in voice
                bonus: 5, // Bonus for being in voice with others
                minDuration: 60000 // Minimum 1 minute to earn XP
            },
            role: {
                dailyLogin: 50,
                messageStreak: 25,
                voiceStreak: 30,
                helpingOthers: 100,
                eventParticipation: 200
            }
        };

        // Level calculation formula: XP needed = 100 * level^1.5, capped at level 50
        this.levelFormula = {
            calculateXPNeeded: (level) => Math.floor(100 * Math.pow(level, 1.5)),
            calculateLevel: (xp) => Math.min(Math.floor(Math.pow(xp / 100, 1 / 1.5)), 50),
            maxLevel: 50
        };

        // Level rewards configuration (currency and titles only, roles are configurable)
        this.levelRewards = {
            text: {
                5: { type: 'currency', amount: 500, message: 'Chatty Beginner Bonus!' },
                10: { type: 'currency', amount: 1000, message: 'Active Chatter Reward!' },
                // Role rewards are now configurable via database
                20: { type: 'currency', amount: 2000, message: 'Text Master Bonus!' },
                25: { type: 'title', title: 'Text Master', message: 'You can now use the Text Master title!' },
                30: { type: 'currency', amount: 5000, message: 'Legendary Chatter Reward!' },
                35: { type: 'currency', amount: 7500, message: 'Text Elite Bonus!' },
                40: { type: 'currency', amount: 10000, message: 'Text Supreme Reward!' },
                45: { type: 'currency', amount: 15000, message: 'Text Grandmaster Bonus!' },
                50: { type: 'currency', amount: 25000, message: 'MAX LEVEL ACHIEVED! Text Legend!' }
            },
            voice: {
                5: { type: 'currency', amount: 750, message: 'Voice Newbie Bonus!' },
                10: { type: 'currency', amount: 1500, message: 'Social Speaker Reward!' },
                // Role rewards are now configurable via database
                20: { type: 'currency', amount: 3000, message: 'Voice Champion Bonus!' },
                25: { type: 'title', title: 'Voice Champion', message: 'You can now use the Voice Champion title!' },
                30: { type: 'currency', amount: 7500, message: 'Voice Legend Reward!' },
                35: { type: 'currency', amount: 10000, message: 'Voice Elite Bonus!' },
                40: { type: 'currency', amount: 15000, message: 'Voice Supreme Reward!' },
                45: { type: 'currency', amount: 20000, message: 'Voice Grandmaster Bonus!' },
                50: { type: 'currency', amount: 35000, message: 'MAX LEVEL ACHIEVED! Voice Legend!' }
            },
            role: {
                5: { type: 'currency', amount: 1000, message: 'Community Helper Bonus!' },
                10: { type: 'currency', amount: 2500, message: 'Server Contributor Reward!' },
                // Role rewards are now configurable via database
                20: { type: 'currency', amount: 5000, message: 'Community Leader Bonus!' },
                25: { type: 'title', title: 'Community Leader', message: 'You can now use the Community Leader title!' },
                30: { type: 'currency', amount: 10000, message: 'Server Legend Reward!' },
                35: { type: 'currency', amount: 15000, message: 'Role Elite Bonus!' },
                40: { type: 'currency', amount: 20000, message: 'Role Supreme Reward!' },
                45: { type: 'currency', amount: 30000, message: 'Role Grandmaster Bonus!' },
                50: { type: 'currency', amount: 50000, message: 'MAX LEVEL ACHIEVED! Ultimate Leader!' }
            },
            overall: {
                10: { type: 'currency', amount: 2000, message: 'Rising Star Bonus!' },
                // Role rewards are now configurable via database
                30: { type: 'currency', amount: 10000, message: 'Server Veteran Reward!' },
                35: { type: 'currency', amount: 15000, message: 'Elite Member Bonus!' },
                40: { type: 'currency', amount: 25000, message: 'Supreme Member Reward!' },
                45: { type: 'title', title: 'Server Grandmaster', message: 'You can now use the Server Grandmaster title!' },
                50: { type: 'currency', amount: 100000, message: 'MAX LEVEL ACHIEVED! ULTIMATE LEGEND STATUS!' }
            }
        };
    }

    // Calculate XP needed for next level
    getXPForLevel(level) {
        return this.levelFormula.calculateXPNeeded(level);
    }

    // Calculate level from XP
    getLevelFromXP(xp) {
        return this.levelFormula.calculateLevel(xp) + 1; // +1 because we start at level 1
    }

    // Calculate XP progress to next level
    getXPProgress(currentXP, currentLevel) {
        // If at max level, show as completed
        if (currentLevel >= this.levelFormula.maxLevel) {
            return {
                current: this.getXPForLevel(this.levelFormula.maxLevel - 1),
                needed: this.getXPForLevel(this.levelFormula.maxLevel - 1),
                percentage: 100,
                isMaxLevel: true
            };
        }
        
        const currentLevelXP = this.getXPForLevel(currentLevel - 1);
        const nextLevelXP = this.getXPForLevel(currentLevel);
        const progressXP = currentXP - currentLevelXP;
        const neededXP = nextLevelXP - currentLevelXP;
        
        return {
            current: progressXP,
            needed: neededXP,
            percentage: Math.floor((progressXP / neededXP) * 100),
            isMaxLevel: false
        };
    }

    // Add text XP when user sends a message
    async addTextXP(userId, message) {
        const now = Date.now();
        const cooldownKey = `${userId}_text`;
        
        // Check cooldown
        if (this.xpCooldowns.has(cooldownKey)) {
            const lastXP = this.xpCooldowns.get(cooldownKey);
            if (now - lastXP < this.xpConfig.text.cooldown) {
                return null; // Still on cooldown
            }
        }

        // Calculate XP based on message length and quality
        let xpGain = this.xpConfig.text.base;
        
        // Bonus for longer messages (up to limit)
        if (message.content.length > 50) {
            xpGain += Math.min(this.xpConfig.text.bonus, this.xpConfig.text.maxPerMessage - this.xpConfig.text.base);
        }

        // Apply multipliers from roles/boosts
        const member = message.guild?.members.cache.get(userId);
        if (member) {
            const multiplier = this.getXPMultiplier(member);
            xpGain = Math.floor(xpGain * multiplier);
        }

        // Set cooldown
        this.xpCooldowns.set(cooldownKey, now);

        // Add XP to database
        await database.getUserLevels(userId); // Ensure user exists
        await database.addXP(userId, 'text', xpGain);

        // Check for level up
        const levelData = await database.getUserLevels(userId);
        const newLevel = this.getLevelFromXP(levelData.text_xp);
        
        // Don't level up beyond max level
        if (newLevel > this.levelFormula.maxLevel) {
            return { xpGain, newLevel: false, maxLevel: true };
        }
        
        if (newLevel > levelData.text_level) {
            await this.handleLevelUp(userId, 'text', levelData.text_level, newLevel, message.channel);
        }

        return { xpGain, newLevel: newLevel > levelData.text_level };
    }

    // Add voice XP for time spent in voice channels
    async addVoiceXP(userId, minutes, channelMemberCount = 1) {
        // Check if user is muted (server mute or self mute)
        const guild = this.client.guilds.cache.first();
        const member = guild?.members.cache.get(userId);
        
        if (!member) {
            console.log(`Member ${userId} not found for voice XP`);
            return null;
        }

        // Check if member is muted (server mute or self mute)
        const voiceState = member.voice;
        if (!voiceState || voiceState.serverMute || voiceState.selfMute) {
            console.log(`Member ${userId} is muted, no voice XP awarded`);
            return null;
        }

        let xpGain = this.xpConfig.voice.base * minutes;
        
        // Bonus for being in voice with others
        if (channelMemberCount > 1) {
            xpGain += this.xpConfig.voice.bonus * minutes;
        }

        // Apply multipliers
        if (member) {
            const multiplier = this.getXPMultiplier(member);
            xpGain = Math.floor(xpGain * multiplier);
        }

        // Add XP to database
        await database.getUserLevels(userId);
        await database.addXP(userId, 'voice', xpGain);
        await database.addVoiceTime(userId, minutes);

        // Check for level up
        const levelData = await database.getUserLevels(userId);
        const newLevel = this.getLevelFromXP(levelData.voice_xp);
        
        // Don't level up beyond max level
        if (newLevel > this.levelFormula.maxLevel) {
            return { xpGain, newLevel: false, maxLevel: true };
        }
        
        if (newLevel > levelData.voice_level) {
            await this.handleLevelUp(userId, 'voice', levelData.voice_level, newLevel);
        }

        return { xpGain, newLevel: newLevel > levelData.voice_level };
    }

    // Add role-based XP for achievements
    async addRoleXP(userId, activityType, amount = null) {
        let xpGain;
        
        switch (activityType) {
            case 'daily_login':
                xpGain = this.xpConfig.role.dailyLogin;
                break;
            case 'message_streak':
                xpGain = this.xpConfig.role.messageStreak;
                break;
            case 'voice_streak':
                xpGain = this.xpConfig.role.voiceStreak;
                break;
            case 'helping_others':
                xpGain = this.xpConfig.role.helpingOthers;
                break;
            case 'event_participation':
                xpGain = this.xpConfig.role.eventParticipation;
                break;
            case 'custom':
                xpGain = amount || 0;
                break;
            default:
                return null;
        }

        // Apply multipliers
        const guild = this.client.guilds.cache.first();
        const member = guild?.members.cache.get(userId);
        if (member) {
            const multiplier = this.getXPMultiplier(member);
            xpGain = Math.floor(xpGain * multiplier);
        }

        // Add XP to database
        await database.getUserLevels(userId);
        await database.addXP(userId, 'role', xpGain);

        // Check for level up
        const levelData = await database.getUserLevels(userId);
        const newLevel = this.getLevelFromXP(levelData.role_xp);
        
        // Don't level up beyond max level
        if (newLevel > this.levelFormula.maxLevel) {
            return { xpGain, newLevel: false, maxLevel: true };
        }
        
        if (newLevel > levelData.role_level) {
            await this.handleLevelUp(userId, 'role', levelData.role_level, newLevel);
        }

        return { xpGain, newLevel: newLevel > levelData.role_level };
    }

    // Get XP multiplier based on user roles
    getXPMultiplier(member) {
        let multiplier = 1.0;
        
        // Check for booster role
        if (member.roles.cache.has(process.env.BOOSTER_ROLE_ID)) {
            multiplier += 0.5; // 50% bonus
        }
        
        // Check for premium role
        if (member.roles.cache.has(process.env.PREMIUM_ROLE_ID)) {
            multiplier += 0.75; // 75% bonus
        }

        return multiplier;
    }

    // Handle level up and rewards
    async handleLevelUp(userId, levelType, oldLevel, newLevel, channel = null) {
        // Cap the new level at max level
        const cappedLevel = Math.min(newLevel, this.levelFormula.maxLevel);
        
        // Update level in database
        await database.updateLevel(userId, levelType, cappedLevel);
        
        // Update overall level
        await this.updateOverallLevel(userId);

        // Check for hardcoded rewards (currency and titles)
        const rewards = this.levelRewards[levelType];
        if (rewards && rewards[cappedLevel]) {
            const reward = rewards[cappedLevel];
            await this.grantReward(userId, levelType, cappedLevel, reward);
        }

        // Check for configurable role rewards
        try {
            const roleReward = await database.getLevelRoleReward(levelType, cappedLevel);
            if (roleReward) {
                const roleRewardData = {
                    type: 'role',
                    roleId: roleReward.role_id,
                    roleName: roleReward.role_name,
                    message: `You earned the ${roleReward.role_name} role!`
                };
                await this.grantReward(userId, levelType, cappedLevel, roleRewardData);
            }
        } catch (error) {
            console.error('Error checking role rewards:', error);
        }

        // Send level up message
        if (channel) {
            await this.sendLevelUpMessage(channel, userId, levelType, cappedLevel);
        }
    }

    // Update overall level based on all XP types
    async updateOverallLevel(userId) {
        const levelData = await database.getUserLevels(userId);
        const newOverallLevel = Math.min(this.getLevelFromXP(levelData.total_xp), this.levelFormula.maxLevel);
        
        if (newOverallLevel > levelData.overall_level) {
            await database.updateLevel(userId, 'overall', newOverallLevel);
            
            // Check for overall level rewards
            const rewards = this.levelRewards.overall;
            if (rewards && rewards[newOverallLevel]) {
                const reward = rewards[newOverallLevel];
                await this.grantReward(userId, 'overall', newOverallLevel, reward);
            }
        }
    }

    // Grant level rewards
    async grantReward(userId, levelType, level, reward) {
        try {
            switch (reward.type) {
                case 'currency':
                    await database.updateBalance(userId, reward.amount);
                    break;
                case 'role':
                    const guild = this.client.guilds.cache.first();
                    const member = guild?.members.cache.get(userId);
                    const role = guild?.roles.cache.get(reward.roleId);
                    if (member && role) {
                        await member.roles.add(role);
                    }
                    break;
                case 'title':
                    // Custom titles would be stored in user profiles
                    // This could be expanded based on your profile system
                    break;
            }

            // Create reward record
            await database.createLevelReward(userId, levelType, level, reward.type, reward);
            
        } catch (error) {
            console.error(`Error granting reward for ${userId}:`, error);
        }
    }

    // Send level up message
    async sendLevelUpMessage(channel, userId, levelType, newLevel) {
        const user = await this.client.users.fetch(userId);
        const isMaxLevel = newLevel >= this.levelFormula.maxLevel;
        
        // Get appropriate colors and styling
        const embedColor = isMaxLevel ? this.design.colors.kingdom : this.design.getLevelColor(newLevel);
        const levelIcon = this.design.getLevelTypeIcon(levelType, isMaxLevel);
        const levelBadge = this.design.createLevelBadge(newLevel);
        
        // Create title with royal styling
        const titlePrefix = isMaxLevel ? 'legend' : (newLevel >= 40 ? 'royal' : (newLevel >= 25 ? 'luxury' : null));
        const title = isMaxLevel ? 
            this.design.styleTitle('ROYAL ASCENSION!', 'legend') : 
            this.design.styleTitle('NOBILITY ACHIEVED!', titlePrefix);
        
        // Create description with royal aesthetic
        const styledUsername = this.design.styleUsername(user.username, newLevel);
        const levelTypeName = levelType === 'overall' ? 'Kingdom' : levelType.charAt(0).toUpperCase() + levelType.slice(1);
        
        const description = isMaxLevel ?
            `${this.design.theme.emojis.crown} **${styledUsername}** has ascended to the ultimate **${levelTypeName} Level ${newLevel}**!\n\n${this.design.theme.emojis.magic} **CONGRATULATIONS! You are now a KINGDOM LEGEND!** ${this.design.theme.emojis.magic}` :
            `${this.design.theme.emojis.star} **${styledUsername}** has achieved **${levelTypeName} ${levelBadge}**!`;

        const embed = this.design.createEmbed(isMaxLevel ? 'kingdom' : 'royal')
            .setTitle(`${levelIcon} ${title}`)
            .setDescription(description)
            .setThumbnail(user.displayAvatarURL({ dynamic: true, size: 256 }));

        // Add reward info if there's a reward for this level
        const rewards = this.levelRewards[levelType];
        if (rewards && rewards[newLevel]) {
            const reward = rewards[newLevel];
            let rewardText = reward.message;
            
            // Style currency rewards
            if (reward.type === 'currency') {
                rewardText = `${this.design.styleRewardMessage(reward.amount, config.currency.symbol)} ${reward.message}`;
            }
            
            embed.addFields([{
                name: `${this.design.theme.emojis.treasure} Royal Treasury Reward`,
                value: rewardText,
                inline: false
            }]);
        }

        // Add special styling for max level
        if (isMaxLevel) {
            embed.addFields([{
                name: `${this.design.theme.emojis.crown} Royal Status`,
                value: `${this.design.theme.emojis.magic} **LEGENDARY NOBILITY UNLOCKED** ${this.design.theme.emojis.magic}\n${this.design.createDivider()}\nYou have reached the pinnacle of the Luxury Kingdom!`,
                inline: false
            }]);
            embed.setFooter({ text: `${this.design.theme.emojis.crown} KINGDOM LEGEND ${this.design.theme.emojis.crown} • Ultimate Nobility Achieved` });
        } else {
            embed.setFooter({ text: this.design.createFooter() });
        }

        try {
            await channel.send({ embeds: [embed] });
        } catch (error) {
            console.error('Error sending level up message:', error);
        }
    }

    // Create level info embed
    async createLevelEmbed(userId, targetUserId = null) {
        const displayUserId = targetUserId || userId;
        const user = await this.client.users.fetch(displayUserId);
        const levelData = await database.getUserLevels(displayUserId);
        
        // Determine overall status and color
        const maxLevel = Math.max(levelData.text_level, levelData.voice_level, levelData.role_level, levelData.overall_level);
        const embedColor = this.design.getLevelColor(maxLevel);
        const isLegendary = maxLevel >= this.levelFormula.maxLevel;
        
        // Create styled title
        const styledUsername = this.design.styleUsername(user.username, maxLevel);
        const titlePrefix = isLegendary ? 'legend' : (maxLevel >= 40 ? 'royal' : (maxLevel >= 25 ? 'elite' : 'cyber'));
        const title = this.design.styleTitle(`${styledUsername}'s Kingdom Profile`, titlePrefix);
        
        const embed = this.design.createEmbed(isLegendary ? 'kingdom' : 'royal')
            .setTitle(`${this.design.theme.emojis.kingdom} ${title}`)
            .setThumbnail(user.displayAvatarURL({ dynamic: true, size: 256 }));

        // Calculate progress for each level type with Y2K styling
        const types = ['text', 'voice', 'role', 'overall'];
        const fields = [];

        types.forEach(type => {
            const xpKey = type === 'overall' ? 'total_xp' : `${type}_xp`;
            const levelKey = type === 'overall' ? 'overall_level' : `${type}_level`;
            
            const currentXP = levelData[xpKey];
            const currentLevel = levelData[levelKey];
            const progress = this.getXPProgress(currentXP, currentLevel);
            const isMaxForType = currentLevel >= this.levelFormula.maxLevel;
            
            // Get styled elements
            const icon = this.design.getLevelTypeIcon(type, isMaxForType);
            const levelBadge = this.design.createLevelBadge(currentLevel);
            const typeName = type === 'overall' ? 'Kingdom' : type.charAt(0).toUpperCase() + type.slice(1);
            
            // Create progress bar
            const progressBar = progress.isMaxLevel ? 
                `${this.design.theme.emojis.crown} MAX LEVEL ${this.design.theme.emojis.crown}` :
                `${this.design.createProgressBar(progress.current, progress.needed)} ${progress.percentage}%`;
            
            const xpDisplay = progress.isMaxLevel ?
                `**XP:** ${this.design.formatNumber(currentXP)}\n**Status:** ${this.design.theme.emojis.magic} LEGENDARY ${this.design.theme.emojis.magic}` :
                `**XP:** ${this.design.formatNumber(currentXP)}\n**Progress:** ${progressBar}`;
            
            fields.push({
                name: `${icon} ${typeName} ${levelBadge}`,
                value: xpDisplay,
                inline: true
            });
        });

        embed.addFields(fields);

        // Add additional stats with Y2K styling
        if (levelData.voice_time_total > 0) {
            const hours = Math.floor(levelData.voice_time_total / 60);
            const minutes = levelData.voice_time_total % 60;
            embed.addFields([{
                name: `${this.design.theme.emojis.cyber} Voice Activity`,
                value: `${this.design.theme.emojis.magic} **${hours}h ${minutes}m** total engagement`,
                inline: true
            }]);
        }

        // Add Kingdom Status
        const kingdomStatus = this.getKingdomStatus(maxLevel);
        embed.addFields([{
            name: `${this.design.theme.emojis.royal} Kingdom Status`,
            value: kingdomStatus,
            inline: false
        }]);

        // Add configured role rewards info with Y2K styling
        try {
            const allRoleRewards = await database.getAllLevelRoleRewards();
            if (allRoleRewards.length > 0) {
                const upcomingRewards = allRoleRewards.filter(reward => {
                    const userLevel = levelData[reward.level_type === 'overall' ? 'overall_level' : `${reward.level_type}_level`];
                    return userLevel < reward.level;
                }).slice(0, 3);

                if (upcomingRewards.length > 0) {
                    const rewardsText = upcomingRewards.map(reward => {
                        const icon = this.design.getLevelTypeIcon(reward.level_type);
                        const badge = this.design.createLevelBadge(reward.level);
                        return `${icon} ${badge} ${this.design.createFieldSeparator()} **${reward.role_name}**`;
                    }).join('\n');

                    embed.addFields([{
                        name: `${this.design.theme.emojis.gem} Upcoming Royal Rewards`,
                        value: rewardsText,
                        inline: false
                    }]);
                }
            }
        } catch (error) {
            console.error('Error fetching role rewards for embed:', error);
        }

        embed.setFooter({ text: this.design.createFooter() });
        return embed;
    }

    // Get Kingdom Status based on level
    getKingdomStatus(maxLevel) {
        if (maxLevel >= this.levelFormula.maxLevel) {
            return `${this.design.theme.emojis.crown} **KINGDOM LEGEND** ${this.design.createDivider()} Ultimate Nobility Achieved`;
        } else if (maxLevel >= 40) {
            return `${this.design.theme.emojis.diamond} **ROYAL NOBILITY** ${this.design.createDivider()} Noble Court Member`;
        } else if (maxLevel >= 25) {
            return `${this.design.theme.emojis.medal} **COURT ARISTOCRAT** ${this.design.createDivider()} High Society Member`;
        } else if (maxLevel >= 10) {
            return `${this.design.theme.emojis.gem} **KINGDOM COURTIER** ${this.design.createDivider()} Rising Noble`;
        } else {
            return `${this.design.theme.emojis.magic} **NEW SUBJECT** ${this.design.createDivider()} Welcome to the Kingdom`;
        }
    }

    // Start voice session tracking
    async startVoiceSession(userId, channelId) {
        const sessionId = await database.startVoiceSession(userId, channelId);
        this.voiceSessions.set(userId, {
            sessionId,
            channelId,
            startTime: Date.now(),
            lastXPTime: Date.now()
        });
    }

    // End voice session tracking
    async endVoiceSession(userId) {
        const session = this.voiceSessions.get(userId);
        if (!session) return;

        const duration = Date.now() - session.startTime;
        const minutes = Math.floor(duration / 60000);
        
        if (minutes >= 1) { // Only award XP for sessions longer than 1 minute
            const result = await this.addVoiceXP(userId, minutes);
            await database.endVoiceSession(session.sessionId, result?.xpGain || 0);
        }

        this.voiceSessions.delete(userId);
    }

    // Periodic voice XP update (called every minute for active sessions)
    async updateActiveVoiceSessions() {
        const now = Date.now();
        
        for (const [userId, session] of this.voiceSessions.entries()) {
            const timeSinceLastXP = now - session.lastXPTime;
            
            if (timeSinceLastXP >= 60000) { // 1 minute passed
                const guild = this.client.guilds.cache.first();
                const member = guild?.members.cache.get(userId);
                const channel = guild?.channels.cache.get(session.channelId);
                
                // Check if member is still in voice and not muted
                if (!member || !member.voice || member.voice.channelId !== session.channelId) {
                    // Member left the channel, end session
                    this.voiceSessions.delete(userId);
                    continue;
                }
                
                // Check if member is muted
                if (member.voice.serverMute || member.voice.selfMute) {
                    console.log(`Member ${userId} is muted, skipping voice XP for this interval`);
                    session.lastXPTime = now; // Update timer but don't award XP
                    continue;
                }
                
                const memberCount = channel?.members?.size || 1;
                
                await this.addVoiceXP(userId, 1, memberCount);
                session.lastXPTime = now;
            }
        }
    }
}

module.exports = LevelingSystem;