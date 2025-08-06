const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, Collection } = require('discord.js');
const database = require('./database');
const config = require('../config.json');

class WonderCoinsDropSystem {
    constructor(client) {
        this.client = client;
        this.activeDrops = new Collection(); // channelId -> dropData
        this.dropChannels = new Collection(); // guildId -> [channelIds]
        this.globalDropInterval = null; // Single global interval
        this.userStats = new Collection(); // userId -> stats
        
        // Drop configuration
        this.config = {
            minAmount: 10,
            maxAmount: 500,
            minInterval: 30 * 60 * 1000, // 30 minutes
            maxInterval: 3 * 60 * 60 * 1000, // 3 hours
            collectTime: 60 * 1000, // 60 seconds to collect
            
            // Special drop chances
            rareDrop: {
                chance: 0.1, // 10%
                multiplier: 3
            },
            
            epicDrop: {
                chance: 0.05, // 5%
                multiplier: 5
            },
            
            legendaryDrop: {
                chance: 0.01, // 1%
                multiplier: 10
            }
        };
        
        this.loadDropChannels();
    }

    async loadDropChannels() {
        try {
            const channels = await database.getDropChannels();
            for (const channel of channels) {
                if (!this.dropChannels.has(channel.guild_id)) {
                    this.dropChannels.set(channel.guild_id, []);
                }
                this.dropChannels.get(channel.guild_id).push(channel.channel_id);
            }
            console.log('✅ Loaded drop channels for', this.dropChannels.size, 'guilds');
            
            // Start single global drop interval for all guilds
            this.startGlobalDropInterval();
        } catch (error) {
            console.error('Error loading drop channels:', error);
        }
    }

    startGlobalDropInterval() {
        // Clear existing interval if any
        if (this.globalDropInterval) {
            clearInterval(this.globalDropInterval);
        }

        const scheduleNextDrop = () => {
            const randomInterval = Math.random() * (this.config.maxInterval - this.config.minInterval) + this.config.minInterval;
            
            setTimeout(() => {
                this.triggerGlobalRandomDrop();
                scheduleNextDrop(); // Schedule the next drop
            }, randomInterval);
        };

        scheduleNextDrop();
        console.log(`🎯 Started global drop interval`);
    }

    async triggerGlobalRandomDrop() {
        // Get all channels from all guilds
        const allChannels = [];
        for (const [guildId, channelIds] of this.dropChannels) {
            for (const channelId of channelIds) {
                allChannels.push({ guildId, channelId });
            }
        }

        if (allChannels.length === 0) return;

        // Pick a random channel from all available channels
        const randomChannel = allChannels[Math.floor(Math.random() * allChannels.length)];
        const channel = this.client.channels.cache.get(randomChannel.channelId);
        
        if (!channel) {
            console.log(`Channel ${randomChannel.channelId} not found, removing from drop list`);
            this.removeDropChannel(randomChannel.guildId, randomChannel.channelId);
            return;
        }

        await this.createDrop(channel);
    }

    async triggerRandomDrop(guildId) {
        const channelIds = this.dropChannels.get(guildId);
        if (!channelIds || channelIds.length === 0) return;

        // Pick a random channel
        const randomChannelId = channelIds[Math.floor(Math.random() * channelIds.length)];
        const channel = this.client.channels.cache.get(randomChannelId);
        
        if (!channel) {
            console.log(`Channel ${randomChannelId} not found, removing from drop list`);
            this.removeDropChannel(guildId, randomChannelId);
            return;
        }

        await this.createDrop(channel);
    }

    async createDrop(channel) {
        const dropData = this.generateDropData();
        const dropId = `drop_${channel.id}_${Date.now()}`;
        
        // Create embed based on drop rarity
        const embed = this.createDropEmbed(dropData);
        
        // Create collection buttons
        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId(`collect_${dropId}`)
                    .setLabel('💰 Grab Coins!')
                    .setStyle(ButtonStyle.Success),
                new ButtonBuilder()
                    .setCustomId(`quick_${dropId}`)
                    .setLabel('⚡ Quick Grab!')
                    .setStyle(ButtonStyle.Primary),
                new ButtonBuilder()
                    .setCustomId(`lucky_${dropId}`)
                    .setLabel('🍀 Lucky Grab!')
                    .setStyle(ButtonStyle.Secondary)
            );

        try {
            const message = await channel.send({ 
                embeds: [embed], 
                components: [row] 
            });

            // Store drop data
            this.activeDrops.set(dropId, {
                ...dropData,
                messageId: message.id,
                channelId: channel.id,
                guildId: channel.guild.id,
                collectors: [],
                createdAt: Date.now()
            });

            // Auto-expire after collect time
            setTimeout(() => {
                this.expireDrop(dropId, message);
            }, this.config.collectTime);

            console.log(`💰 Drop created in ${channel.guild.name}/#${channel.name}: ${dropData.amount} coins (${dropData.rarity})`);
        } catch (error) {
            console.error('Error creating drop:', error);
        }
    }

    generateDropData() {
        let amount = Math.floor(Math.random() * (this.config.maxAmount - this.config.minAmount + 1)) + this.config.minAmount;
        let rarity = 'common';
        let multiplier = 1;

        // Check for special drops
        const rand = Math.random();
        
        if (rand < this.config.legendaryDrop.chance) {
            rarity = 'legendary';
            multiplier = this.config.legendaryDrop.multiplier;
        } else if (rand < this.config.epicDrop.chance) {
            rarity = 'epic';
            multiplier = this.config.epicDrop.multiplier;
        } else if (rand < this.config.rareDrop.chance) {
            rarity = 'rare';
            multiplier = this.config.rareDrop.multiplier;
        }

        amount = Math.floor(amount * multiplier);

        return {
            amount,
            rarity,
            multiplier,
            collectMethod: this.getRandomCollectMethod()
        };
    }

    getRandomCollectMethod() {
        const methods = [
            {
                type: 'normal',
                name: 'Standard Collection',
                description: 'Click the button to collect!',
                bonus: 1
            },
            {
                type: 'quick',
                name: 'Quick Reflexes',
                description: 'First 3 collectors get double coins!',
                bonus: 2,
                limit: 3
            },
            {
                type: 'lucky',
                name: 'Lucky Draw',
                description: 'Random chance for bonus coins!',
                bonus: 1.5,
                luckyChance: 0.3
            }
        ];

        return methods[Math.floor(Math.random() * methods.length)];
    }

    createDropEmbed(dropData) {
        const rarityConfig = {
            common: { color: '#95a5a6', emoji: '💰', title: 'WonderCoins Drop!' },
            rare: { color: '#3498db', emoji: '✨', title: 'Rare WonderCoins Drop!' },
            epic: { color: '#9b59b6', emoji: '🌟', title: 'Epic WonderCoins Drop!' },
            legendary: { color: '#f1c40f', emoji: '👑', title: 'LEGENDARY WonderCoins Drop!' }
        };

        const config = rarityConfig[dropData.rarity];
        
        const embed = new EmbedBuilder()
            .setColor(config.color)
            .setTitle(`${config.emoji} ${config.title}`)
            .setDescription(`💎 **${dropData.amount}** ${config.emoji} WonderCoins have appeared!\n\n🎯 **Collection Method:** ${dropData.collectMethod.name}\n📝 ${dropData.collectMethod.description}`)
            .addFields([
                {
                    name: '⏰ Time Limit',
                    value: `${this.config.collectTime / 1000} seconds`,
                    inline: true
                },
                {
                    name: '🎭 Rarity',
                    value: dropData.rarity.toUpperCase(),
                    inline: true
                }
            ])
            .setFooter({ text: 'Click a button below to collect the coins!' })
            .setTimestamp();

        if (dropData.rarity === 'legendary') {
            embed.setImage('https://media.giphy.com/media/67ThRZlYBvibtdF9JH/giphy.gif');
        }

        return embed;
    }

    async handleDropCollection(interaction) {
        const dropId = interaction.customId.split('_').slice(1).join('_');
        const collectType = interaction.customId.split('_')[0];
        
        const drop = this.activeDrops.get(dropId);
        if (!drop) {
            return await interaction.reply({ 
                content: '❌ This drop has already expired!', 
                ephemeral: true 
            });
        }

        // Check if user already collected
        if (drop.collectors.some(c => c.userId === interaction.user.id)) {
            return await interaction.reply({ 
                content: '❌ You already collected from this drop!', 
                ephemeral: true 
            });
        }

        // Calculate final amount based on collection method
        let finalAmount = await this.calculateCollectionAmount(drop, collectType, interaction.user.id);
        
        // Add collector
        drop.collectors.push({
            userId: interaction.user.id,
            username: interaction.user.username,
            amount: finalAmount,
            collectType,
            timestamp: Date.now()
        });

        // Update user balance
        await database.createUser(interaction.user.id, interaction.user.username);
        await database.updateBalance(interaction.user.id, finalAmount);
        await database.addTransaction(interaction.user.id, 'wondercoins_drop', finalAmount, `Collected from ${drop.rarity} drop`);

        // Update user stats
        await this.updateUserDropStats(interaction.user.id, finalAmount, drop.rarity);
        
        // Add to drop statistics
        await database.addDropStat(drop.guildId, interaction.user.id, finalAmount, drop.rarity, collectType);

        const embed = new EmbedBuilder()
            .setColor('#2ecc71')
            .setTitle('💰 Coins Collected!')
            .setDescription(`🎉 ${interaction.user.username} collected **${finalAmount}** WonderCoins!\n\n🎯 Collection Type: ${collectType.charAt(0).toUpperCase() + collectType.slice(1)}\n🏆 Drop Rarity: ${drop.rarity.toUpperCase()}`)
            .setTimestamp();

        await interaction.reply({ embeds: [embed], ephemeral: true });

        // Update the original message if needed
        if (drop.collectMethod.limit && drop.collectors.length >= drop.collectMethod.limit) {
            await this.expireDrop(dropId, null, 'Collection limit reached');
        }
    }

    async calculateCollectionAmount(drop, collectType, userId) {
        let amount = drop.amount;
        
        switch (collectType) {
            case 'quick':
                if (drop.collectMethod.type === 'quick' && drop.collectors.length < drop.collectMethod.limit) {
                    amount = Math.floor(amount * drop.collectMethod.bonus);
                }
                break;
                
            case 'lucky':
                if (drop.collectMethod.type === 'lucky') {
                    const isLucky = Math.random() < drop.collectMethod.luckyChance;
                    if (isLucky) {
                        amount = Math.floor(amount * drop.collectMethod.bonus);
                    }
                }
                break;
                
            default: // normal collect
                break;
        }

        // Apply global multipliers (booster/premium roles)
        const guild = this.client.guilds.cache.get(drop.guildId);
        if (guild) {
            const member = guild.members.cache.get(userId);
            if (member) {
                if (member.roles.cache.has(process.env.PREMIUM_ROLE_ID)) {
                    amount = Math.floor(amount * 1.5);
                } else if (member.roles.cache.has(process.env.BOOSTER_ROLE_ID)) {
                    amount = Math.floor(amount * 1.25);
                }
            }
        }

        return amount;
    }

    async updateUserDropStats(userId, amount, rarity) {
        try {
            await database.updateUserDropStats(userId, amount, rarity);
        } catch (error) {
            console.error('Error updating user drop stats:', error);
        }
    }

    async expireDrop(dropId, message = null, reason = 'Time expired') {
        const drop = this.activeDrops.get(dropId);
        if (!drop) return;

        try {
            if (!message) {
                const channel = this.client.channels.cache.get(drop.channelId);
                if (channel) {
                    message = await channel.messages.fetch(drop.messageId);
                }
            }

            if (message) {
                const expiredEmbed = new EmbedBuilder()
                    .setColor('#e74c3c')
                    .setTitle('💸 Drop Expired')
                    .setDescription(`The WonderCoins drop has expired!\n\n📊 **Collectors:** ${drop.collectors.length}\n💰 **Total Collected:** ${drop.collectors.reduce((sum, c) => sum + c.amount, 0)} WonderCoins\n\n⏰ Reason: ${reason}`)
                    .setTimestamp();

                await message.edit({ 
                    embeds: [expiredEmbed], 
                    components: [] 
                });
            }
        } catch (error) {
            console.error('Error expiring drop:', error);
        }

        this.activeDrops.delete(dropId);
    }

    // Admin methods
    async addDropChannel(guildId, channelId) {
        try {
            await database.addDropChannel(guildId, channelId);
            
            if (!this.dropChannels.has(guildId)) {
                this.dropChannels.set(guildId, []);
                // Restart global interval if this is the first channel being added
                if (this.dropChannels.size === 1) {
                    this.startGlobalDropInterval();
                }
            }
            
            if (!this.dropChannels.get(guildId).includes(channelId)) {
                this.dropChannels.get(guildId).push(channelId);
            }
            
            return true;
        } catch (error) {
            console.error('Error adding drop channel:', error);
            return false;
        }
    }

    async removeDropChannel(guildId, channelId) {
        try {
            await database.removeDropChannel(guildId, channelId);
            
            const channels = this.dropChannels.get(guildId);
            if (channels) {
                const index = channels.indexOf(channelId);
                if (index > -1) {
                    channels.splice(index, 1);
                }
                
                // If no channels left, remove guild and stop global interval if no guilds left
                if (channels.length === 0) {
                    this.dropChannels.delete(guildId);
                    
                    // Stop global interval if no guilds have channels
                    if (this.dropChannels.size === 0 && this.globalDropInterval) {
                        clearInterval(this.globalDropInterval);
                        this.globalDropInterval = null;
                        console.log('🛑 Stopped global drop interval - no active channels');
                    }
                }
            }
            
            return true;
        } catch (error) {
            console.error('Error removing drop channel:', error);
            return false;
        }
    }

    async getDropChannels(guildId) {
        return this.dropChannels.get(guildId) || [];
    }

    async getDropStats(guildId) {
        try {
            return await database.getDropStats(guildId);
        } catch (error) {
            console.error('Error getting drop stats:', error);
            return null;
        }
    }

    async getUserDropStats(userId) {
        try {
            return await database.getUserDropStats(userId);
        } catch (error) {
            console.error('Error getting user drop stats:', error);
            return null;
        }
    }

    // Manual drop trigger for admins
    async triggerManualDrop(channelId, amount = null, rarity = null) {
        const channel = this.client.channels.cache.get(channelId);
        if (!channel) return false;

        // Override generation if specific parameters provided
        let dropData;
        if (amount || rarity) {
            dropData = {
                amount: amount || this.config.minAmount,
                rarity: rarity || 'common',
                multiplier: 1,
                collectMethod: this.getRandomCollectMethod()
            };
            
            // Override the createDrop method call to use specific data
            const dropId = `drop_${channel.id}_${Date.now()}`;
            
            // Create embed based on drop rarity
            const embed = this.createDropEmbed(dropData);
            
            // Create collection buttons
            const row = new ActionRowBuilder()
                .addComponents(
                    new ButtonBuilder()
                        .setCustomId(`collect_${dropId}`)
                        .setLabel('💰 Grab Coins!')
                        .setStyle(ButtonStyle.Success),
                    new ButtonBuilder()
                        .setCustomId(`quick_${dropId}`)
                        .setLabel('⚡ Quick Grab!')
                        .setStyle(ButtonStyle.Primary),
                    new ButtonBuilder()
                        .setCustomId(`lucky_${dropId}`)
                        .setLabel('🍀 Lucky Grab!')
                        .setStyle(ButtonStyle.Secondary)
                );

            try {
                const message = await channel.send({ 
                    embeds: [embed], 
                    components: [row] 
                });

                // Store drop data
                this.activeDrops.set(dropId, {
                    ...dropData,
                    messageId: message.id,
                    channelId: channel.id,
                    guildId: channel.guild.id,
                    collectors: [],
                    createdAt: Date.now()
                });

                // Auto-expire after collect time
                setTimeout(() => {
                    this.expireDrop(dropId, message);
                }, this.config.collectTime);

                console.log(`💰 Manual drop created in ${channel.guild.name}/#${channel.name}: ${dropData.amount} coins (${dropData.rarity})`);
                return true;
            } catch (error) {
                console.error('Error creating manual drop:', error);
                return false;
            }
        } else {
            await this.createDrop(channel);
            return true;
        }
    }
}

module.exports = WonderCoinsDropSystem;