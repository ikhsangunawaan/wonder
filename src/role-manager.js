const { EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const config = require('../config.json');

class RoleManager {
    constructor(client) {
        this.client = client;
        this.boosterRoleId = process.env.BOOSTER_ROLE_ID;
        this.premiumRoleId = process.env.PREMIUM_ROLE_ID;
    }

    // Check if user has booster role
    isBooster(member) {
        return member.roles.cache.has(this.boosterRoleId);
    }

    // Check if user has premium role
    isPremium(member) {
        return member.roles.cache.has(this.premiumRoleId);
    }

    // Get all perks for a member
    getMemberPerks(member) {
        const perks = {
            isBooster: this.isBooster(member),
            isPremium: this.isPremium(member),
            dailyBonus: 0,
            workBonus: 0,
            exclusiveChannels: false,
            customColor: false
        };

        if (perks.isBooster) {
            perks.dailyBonus += config.booster.dailyBonus;
            perks.workBonus += config.booster.workBonus;
            perks.exclusiveChannels = config.booster.exclusiveChannels;
        }

        if (perks.isPremium) {
            perks.dailyBonus += config.premium.dailyBonus;
            perks.workBonus += config.premium.workBonus;
            perks.exclusiveChannels = config.premium.exclusiveChannels;
            perks.customColor = config.premium.customColor;
        }

        return perks;
    }

    // Create embed showing user's perks
    createPerksEmbed(member) {
        const perks = this.getMemberPerks(member);
        
        const embed = new EmbedBuilder()
            .setColor(config.colors.primary)
            .setTitle(`💎 ${member.user.username}'s Perks`)
            .setThumbnail(member.user.displayAvatarURL())
            .setTimestamp();

        let description = '';
        let fields = [];

        if (perks.isBooster) {
            description += '🚀 **Server Booster** - Thank you for boosting!\n';
            fields.push({
                name: '🚀 Booster Perks',
                value: `• +${config.booster.dailyBonus} ${config.currency.symbol} daily bonus\n• +${config.booster.workBonus} ${config.currency.symbol} work bonus\n• Access to exclusive channels`,
                inline: true
            });
        }

        if (perks.isPremium) {
            description += '⭐ **Premium Member** - Welcome to the VIP club!\n';
            fields.push({
                name: '⭐ Premium Perks',
                value: `• +${config.premium.dailyBonus} ${config.currency.symbol} daily bonus\n• +${config.premium.workBonus} ${config.currency.symbol} work bonus\n• Access to premium channels\n• Custom embed colors`,
                inline: true
            });
        }

        if (!perks.isBooster && !perks.isPremium) {
            description = '📝 You don\'t have any special roles yet.\n\n**Available Perks:**\n🚀 **Server Booster** - Boost the server to unlock exclusive perks!\n⭐ **Premium Member** - Purchase premium for VIP benefits!';
        } else {
            fields.push({
                name: '📊 Total Bonuses',
                value: `• Daily: +${perks.dailyBonus} ${config.currency.symbol}\n• Work: +${perks.workBonus} ${config.currency.symbol}`,
                inline: false
            });
        }

        embed.setDescription(description);
        if (fields.length > 0) {
            embed.addFields(fields);
        }

        return embed;
    }

    // Check if member can access exclusive channels
    canAccessExclusiveChannels(member) {
        const perks = this.getMemberPerks(member);
        return perks.exclusiveChannels;
    }

    // Auto-assign roles based on certain criteria
    async autoAssignRoles(member) {
        try {
            // Check if member boosted the server
            if (member.premiumSince && !this.isBooster(member)) {
                const boosterRole = member.guild.roles.cache.get(this.boosterRoleId);
                if (boosterRole) {
                    await member.roles.add(boosterRole);
                    console.log(`Auto-assigned booster role to ${member.user.username}`);
                }
            }
        } catch (error) {
            console.error('Error auto-assigning roles:', error);
        }
    }

    // Create exclusive channel permissions
    createExclusiveChannelPermissions(channel) {
        const permissions = [
            {
                id: channel.guild.roles.everyone.id,
                deny: [PermissionFlagsBits.ViewChannel]
            }
        ];

        // Add booster role permissions
        if (this.boosterRoleId) {
            permissions.push({
                id: this.boosterRoleId,
                allow: [
                    PermissionFlagsBits.ViewChannel,
                    PermissionFlagsBits.SendMessages,
                    PermissionFlagsBits.ReadMessageHistory
                ]
            });
        }

        // Add premium role permissions
        if (this.premiumRoleId) {
            permissions.push({
                id: this.premiumRoleId,
                allow: [
                    PermissionFlagsBits.ViewChannel,
                    PermissionFlagsBits.SendMessages,
                    PermissionFlagsBits.ReadMessageHistory,
                    PermissionFlagsBits.UseExternalEmojis,
                    PermissionFlagsBits.AddReactions
                ]
            });
        }

        return permissions;
    }

    // Setup exclusive channels
    async setupExclusiveChannels(guild) {
        try {
            // Create booster lounge if it doesn't exist
            let boosterChannel = guild.channels.cache.find(ch => ch.name === 'booster-lounge');
            if (!boosterChannel) {
                boosterChannel = await guild.channels.create({
                    name: 'booster-lounge',
                    type: 0, // Text channel
                    topic: 'Exclusive channel for server boosters! 🚀',
                    permissionOverwrites: this.createExclusiveChannelPermissions()
                });

                const embed = new EmbedBuilder()
                    .setColor(config.colors.primary)
                    .setTitle('🚀 Welcome to the Booster Lounge!')
                    .setDescription('Thank you for boosting our server! This exclusive channel is just for our amazing boosters.\n\n**Your perks include:**\n• Enhanced WonderCash rewards\n• Early access to new features\n• Special recognition in the community')
                    .setFooter({ text: 'Wonder Bot - Exclusive Perks' })
                    .setTimestamp();

                await boosterChannel.send({ embeds: [embed] });
            }

            // Create premium lounge if it doesn't exist
            let premiumChannel = guild.channels.cache.find(ch => ch.name === 'premium-lounge');
            if (!premiumChannel) {
                premiumChannel = await guild.channels.create({
                    name: 'premium-lounge',
                    type: 0, // Text channel
                    topic: 'VIP lounge for premium members! ⭐',
                    permissionOverwrites: this.createExclusiveChannelPermissions()
                });

                const embed = new EmbedBuilder()
                    .setColor(config.colors.primary)
                    .setTitle('⭐ Welcome to the Premium Lounge!')
                    .setDescription('Welcome to the VIP experience! This exclusive channel is for our premium members.\n\n**Your premium perks include:**\n• Maximum WonderCash bonuses\n• Custom embed colors\n• Priority support\n• Exclusive premium-only events')
                    .setFooter({ text: 'Wonder Bot - Premium Benefits' })
                    .setTimestamp();

                await premiumChannel.send({ embeds: [embed] });
            }

            console.log('✅ Exclusive channels setup complete');
        } catch (error) {
            console.error('Error setting up exclusive channels:', error);
        }
    }

    // Handle role updates
    async handleRoleUpdate(oldMember, newMember) {
        const hadBooster = oldMember.roles.cache.has(this.boosterRoleId);
        const hasBooster = newMember.roles.cache.has(this.boosterRoleId);
        const hadPremium = oldMember.roles.cache.has(this.premiumRoleId);
        const hasPremium = newMember.roles.cache.has(this.premiumRoleId);

        // Booster role added
        if (!hadBooster && hasBooster) {
            await this.sendRoleWelcome(newMember, 'booster');
        }

        // Premium role added
        if (!hadPremium && hasPremium) {
            await this.sendRoleWelcome(newMember, 'premium');
        }

        // Role removed notifications could be added here
    }

    // Send welcome message for new role
    async sendRoleWelcome(member, roleType) {
        try {
            const embeds = {
                booster: new EmbedBuilder()
                    .setColor('#F47FFF')
                    .setTitle('🚀 Thank you for boosting!')
                    .setDescription(`Hey ${member}, thank you for boosting **${member.guild.name}**!\n\nYou now have access to exclusive booster perks:\n• +${config.booster.dailyBonus} ${config.currency.symbol} daily bonus\n• +${config.booster.workBonus} ${config.currency.symbol} work bonus\n• Access to #booster-lounge`)
                    .setThumbnail(member.user.displayAvatarURL())
                    .setFooter({ text: 'Wonder Bot - Booster Perks' })
                    .setTimestamp(),

                premium: new EmbedBuilder()
                    .setColor('#FFD700')
                    .setTitle('⭐ Welcome to Premium!')
                    .setDescription(`Welcome ${member}, you're now a premium member!\n\nYour VIP perks include:\n• +${config.premium.dailyBonus} ${config.currency.symbol} daily bonus\n• +${config.premium.workBonus} ${config.currency.symbol} work bonus\n• Access to #premium-lounge\n• Custom embed colors`)
                    .setThumbnail(member.user.displayAvatarURL())
                    .setFooter({ text: 'Wonder Bot - Premium Benefits' })
                    .setTimestamp()
            };

            // Send DM to user
            await member.send({ embeds: [embeds[roleType]] });

            // Send notification in appropriate channel
            const channelName = roleType === 'booster' ? 'booster-lounge' : 'premium-lounge';
            const channel = member.guild.channels.cache.find(ch => ch.name === channelName);
            if (channel) {
                await channel.send({ content: `🎉 Welcome ${member} to the ${roleType} club!`, embeds: [embeds[roleType]] });
            }
        } catch (error) {
            console.error(`Error sending ${roleType} welcome:`, error);
        }
    }

    // Get role statistics
    async getRoleStats(guild) {
        const boosterRole = guild.roles.cache.get(this.boosterRoleId);
        const premiumRole = guild.roles.cache.get(this.premiumRoleId);

        return {
            boosters: boosterRole ? boosterRole.members.size : 0,
            premium: premiumRole ? premiumRole.members.size : 0,
            total: guild.memberCount
        };
    }
}

module.exports = RoleManager;