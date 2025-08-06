const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const database = require('./database');
const config = require('../config.json');

class GiveawaySystem {
    constructor(client) {
        this.client = client;
        this.activeGiveaways = new Map();
        
        // Odds multipliers for different member types
        this.oddsMultipliers = {
            regular: 1.0,      // Regular members: 1x
            booster: 2.0,      // Server boosters: 2x chance
            premium: 3.0       // Premium members: 3x chance
        };

        // Restriction settings
        this.restrictions = {
            winnerCooldown: 7 * 24 * 60, // 7 days in minutes
            premiumBypass: true          // Premium can bypass restrictions
        };
    }

    // Create a new giveaway
    async createGiveaway(guild, channelId, options) {
        try {
            const giveawayId = await database.createGiveaway({
                guildId: guild.id,
                channelId: channelId,
                title: options.title,
                description: options.description,
                prize: options.prize,
                winnerCount: options.winnerCount || 1,
                duration: options.duration, // in minutes
                requirements: options.requirements || {},
                createdBy: options.createdBy,
                restrictWinners: options.restrictWinners !== false // default true
            });

            const giveaway = await database.getGiveaway(giveawayId);
            this.activeGiveaways.set(giveawayId, giveaway);

            // Schedule giveaway end
            setTimeout(() => {
                this.endGiveaway(giveawayId);
            }, options.duration * 60 * 1000);

            return giveaway;
        } catch (error) {
            console.error('Error creating giveaway:', error);
            throw error;
        }
    }

    // Create giveaway embed
    createGiveawayEmbed(giveaway, isEnded = false) {
        const endTime = new Date(giveaway.created_at);
        endTime.setMinutes(endTime.getMinutes() + giveaway.duration);

        const embed = new EmbedBuilder()
            .setColor(isEnded ? config.colors.warning : config.colors.primary)
            .setTitle(`🎉 ${giveaway.title}`)
            .setDescription(giveaway.description)
            .addFields(
                {
                    name: '🎁 Prize',
                    value: giveaway.prize,
                    inline: true
                },
                {
                    name: '👥 Winners',
                    value: giveaway.winner_count.toString(),
                    inline: true
                },
                {
                    name: '⏰ Ends',
                    value: isEnded ? '**ENDED**' : `<t:${Math.floor(endTime.getTime() / 1000)}:R>`,
                    inline: true
                }
            )
            .setFooter({ 
                text: isEnded ? 'Giveaway Ended' : 'Click the button below to enter!' 
            })
            .setTimestamp();

        // Add requirements if any
        if (giveaway.requirements && Object.keys(giveaway.requirements).length > 0) {
            let reqText = '';
            if (giveaway.requirements.minLevel) reqText += `• Minimum level: ${giveaway.requirements.minLevel}\n`;
            if (giveaway.requirements.roleRequired) reqText += `• Required role: <@&${giveaway.requirements.roleRequired}>\n`;
            if (giveaway.requirements.accountAge) reqText += `• Account age: ${giveaway.requirements.accountAge} days\n`;
            
            if (reqText) {
                embed.addFields({
                    name: '📋 Requirements',
                    value: reqText,
                    inline: false
                });
            }
        }

        // Add odds information
        embed.addFields({
            name: '🎲 Entry Odds',
            value: '👤 Regular: 1x\n<:boost:> Boosters: 2x\n⭐ Premium: 3x',
            inline: true
        });

        if (giveaway.restrict_winners) {
            embed.addFields({
                name: '⚠️ Winner Restrictions',
                value: 'Previous winners cannot enter for 7 days\n⭐ Premium members can bypass this restriction',
                inline: true
            });
        }

        return embed;
    }

    // Create giveaway entry button
    createGiveawayButton(giveawayId, isEnded = false) {
        const button = new ButtonBuilder()
            .setCustomId(`giveaway_enter_${giveawayId}`)
            .setLabel('🎉 Enter Giveaway')
            .setStyle(ButtonStyle.Primary)
            .setDisabled(isEnded);

        return new ActionRowBuilder().addComponents(button);
    }

    // Check if user can enter giveaway
    async canUserEnter(userId, giveaway, member) {
        try {
            // Check if already entered
            const hasEntered = await database.hasEnteredGiveaway(userId, giveaway.id);
            if (hasEntered) {
                return { canEnter: false, reason: 'You have already entered this giveaway!' };
            }

            // Check winner restrictions
            if (giveaway.restrict_winners) {
                const isPremium = member.roles.cache.has(process.env.PREMIUM_ROLE_ID);
                
                if (!isPremium || !this.restrictions.premiumBypass) {
                    const recentWin = await database.getRecentGiveawayWin(userId, this.restrictions.winnerCooldown);
                    if (recentWin && !isPremium) {
                        const timeLeft = this.restrictions.winnerCooldown - recentWin.minutesAgo;
                        const daysLeft = Math.ceil(timeLeft / (24 * 60));
                        return { 
                            canEnter: false, 
                            reason: `You won a giveaway recently and must wait ${daysLeft} more days to enter again. Premium members can bypass this restriction!` 
                        };
                    }
                }
            }

            // Check requirements
            if (giveaway.requirements) {
                const req = giveaway.requirements;
                
                // Check role requirement
                if (req.roleRequired && !member.roles.cache.has(req.roleRequired)) {
                    return { canEnter: false, reason: `You need the required role to enter this giveaway!` };
                }

                // Check account age
                if (req.accountAge) {
                    const accountAge = (Date.now() - member.user.createdTimestamp) / (1000 * 60 * 60 * 24);
                    if (accountAge < req.accountAge) {
                        return { canEnter: false, reason: `Your account must be at least ${req.accountAge} days old to enter!` };
                    }
                }

                // Check minimum level (if you have a leveling system)
                if (req.minLevel) {
                    // This would require a leveling system - placeholder for now
                    // const userLevel = await database.getUserLevel(userId);
                    // if (userLevel < req.minLevel) {
                    //     return { canEnter: false, reason: `You need to be at least level ${req.minLevel} to enter!` };
                    // }
                }
            }

            return { canEnter: true };
        } catch (error) {
            console.error('Error checking user entry eligibility:', error);
            return { canEnter: false, reason: 'An error occurred while checking eligibility.' };
        }
    }

    // Enter user into giveaway
    async enterGiveaway(userId, giveawayId, member) {
        try {
            const giveaway = await database.getGiveaway(giveawayId);
            if (!giveaway) {
                return { success: false, message: 'Giveaway not found!' };
            }

            // Check if giveaway has ended
            const endTime = new Date(giveaway.created_at);
            endTime.setMinutes(endTime.getMinutes() + giveaway.duration);
            if (Date.now() > endTime.getTime()) {
                return { success: false, message: 'This giveaway has already ended!' };
            }

            // Check eligibility
            const eligibility = await this.canUserEnter(userId, giveaway, member);
            if (!eligibility.canEnter) {
                return { success: false, message: eligibility.reason };
            }

            // Calculate entry weight based on user type
            let entryWeight = this.oddsMultipliers.regular;
            if (member.roles.cache.has(process.env.PREMIUM_ROLE_ID)) {
                entryWeight = this.oddsMultipliers.premium;
            } else if (member.roles.cache.has(process.env.BOOSTER_ROLE_ID)) {
                entryWeight = this.oddsMultipliers.booster;
            }

            // Add entry to database
            await database.addGiveawayEntry(userId, giveawayId, entryWeight);
            
            const entryCount = await database.getGiveawayEntryCount(giveawayId);

            return { 
                success: true, 
                message: `Successfully entered the giveaway! You have **${entryWeight}x** entry odds.`,
                entryCount: entryCount,
                entryWeight: entryWeight
            };
        } catch (error) {
            console.error('Error entering giveaway:', error);
            return { success: false, message: 'An error occurred while entering the giveaway!' };
        }
    }

    // End giveaway and select winners
    async endGiveaway(giveawayId) {
        try {
            const giveaway = await database.getGiveaway(giveawayId);
            if (!giveaway || giveaway.ended) return;

            const entries = await database.getGiveawayEntries(giveawayId);
            if (entries.length === 0) {
                await this.announceNoWinners(giveaway);
                await database.endGiveaway(giveawayId, []);
                return;
            }

            // Select winners using weighted random selection
            const winners = this.selectWeightedWinners(entries, giveaway.winner_count);
            
            // Update database
            await database.endGiveaway(giveawayId, winners.map(w => w.user_id));
            
            // Record wins for restriction purposes
            for (const winner of winners) {
                await database.recordGiveawayWin(winner.user_id, giveawayId);
            }

            // Announce winners
            await this.announceWinners(giveaway, winners);
            
            this.activeGiveaways.delete(giveawayId);

        } catch (error) {
            console.error('Error ending giveaway:', error);
        }
    }

    // Select winners using weighted random selection
    selectWeightedWinners(entries, winnerCount) {
        const winners = [];
        const availableEntries = [...entries];

        for (let i = 0; i < winnerCount && availableEntries.length > 0; i++) {
            // Calculate total weight
            const totalWeight = availableEntries.reduce((sum, entry) => sum + entry.entry_weight, 0);
            
            // Generate random number
            let random = Math.random() * totalWeight;
            
            // Select winner
            let selectedIndex = 0;
            for (let j = 0; j < availableEntries.length; j++) {
                random -= availableEntries[j].entry_weight;
                if (random <= 0) {
                    selectedIndex = j;
                    break;
                }
            }

            // Add winner and remove from available entries
            winners.push(availableEntries[selectedIndex]);
            availableEntries.splice(selectedIndex, 1);
        }

        return winners;
    }

    // Announce giveaway winners
    async announceWinners(giveaway, winners) {
        try {
            const guild = this.client.guilds.cache.get(giveaway.guild_id);
            const channel = guild.channels.cache.get(giveaway.channel_id);

            if (!channel) return;

            const winnerMentions = winners.map(w => `<@${w.user_id}>`).join(', ');
            
            const embed = new EmbedBuilder()
                .setColor(config.colors.success)
                .setTitle('🎉 Giveaway Ended!')
                .setDescription(`**${giveaway.title}** has ended!`)
                .addFields(
                    {
                        name: '🏆 Winners',
                        value: winnerMentions,
                        inline: false
                    },
                    {
                        name: '🎁 Prize',
                        value: giveaway.prize,
                        inline: true
                    },
                    {
                        name: '👥 Total Entries',
                        value: (await database.getGiveawayEntryCount(giveaway.id)).toString(),
                        inline: true
                    }
                )
                .setFooter({ text: 'Congratulations to the winners!' })
                .setTimestamp();

            await channel.send({ 
                content: `🎉 **GIVEAWAY ENDED** 🎉\n\nCongratulations ${winnerMentions}! You won **${giveaway.prize}**!`,
                embeds: [embed] 
            });

            // Update original giveaway message
            try {
                const originalMessage = await channel.messages.fetch(giveaway.message_id);
                const endedEmbed = this.createGiveawayEmbed(giveaway, true);
                const disabledButton = this.createGiveawayButton(giveaway.id, true);
                
                await originalMessage.edit({ 
                    embeds: [endedEmbed], 
                    components: [disabledButton] 
                });
            } catch (error) {
                console.error('Error updating original giveaway message:', error);
            }

        } catch (error) {
            console.error('Error announcing winners:', error);
        }
    }

    // Announce no winners
    async announceNoWinners(giveaway) {
        try {
            const guild = this.client.guilds.cache.get(giveaway.guild_id);
            const channel = guild.channels.cache.get(giveaway.channel_id);

            if (!channel) return;

            const embed = new EmbedBuilder()
                .setColor(config.colors.warning)
                .setTitle('😔 Giveaway Ended - No Winners')
                .setDescription(`**${giveaway.title}** has ended with no participants.`)
                .addFields({
                    name: '🎁 Prize',
                    value: giveaway.prize,
                    inline: true
                })
                .setFooter({ text: 'Better luck next time!' })
                .setTimestamp();

            await channel.send({ embeds: [embed] });

        } catch (error) {
            console.error('Error announcing no winners:', error);
        }
    }

    // Get giveaway statistics
    async getGiveawayStats(giveawayId) {
        try {
            const giveaway = await database.getGiveaway(giveawayId);
            const entryCount = await database.getGiveawayEntryCount(giveawayId);
            const entries = await database.getGiveawayEntries(giveawayId);

            const stats = {
                totalEntries: entryCount,
                regularEntries: entries.filter(e => e.entry_weight === 1).length,
                boosterEntries: entries.filter(e => e.entry_weight === 2).length,
                premiumEntries: entries.filter(e => e.entry_weight === 3).length,
                totalWeight: entries.reduce((sum, e) => sum + e.entry_weight, 0)
            };

            return stats;
        } catch (error) {
            console.error('Error getting giveaway stats:', error);
            return null;
        }
    }

    // Reroll giveaway winners
    async rerollGiveaway(giveawayId, newWinnerCount = null) {
        try {
            const giveaway = await database.getGiveaway(giveawayId);
            if (!giveaway || !giveaway.ended) {
                return { success: false, message: 'Giveaway not found or not ended!' };
            }

            const entries = await database.getGiveawayEntries(giveawayId);
            if (entries.length === 0) {
                return { success: false, message: 'No entries found for this giveaway!' };
            }

            const winnerCount = newWinnerCount || giveaway.winner_count;
            const newWinners = this.selectWeightedWinners(entries, winnerCount);

            // Update database with new winners
            await database.updateGiveawayWinners(giveawayId, newWinners.map(w => w.user_id));

            // Record new wins
            for (const winner of newWinners) {
                await database.recordGiveawayWin(winner.user_id, giveawayId);
            }

            return {
                success: true,
                message: 'Giveaway rerolled successfully!',
                winners: newWinners
            };

        } catch (error) {
            console.error('Error rerolling giveaway:', error);
            return { success: false, message: 'An error occurred while rerolling the giveaway!' };
        }
    }

    // Cancel active giveaway
    async cancelGiveaway(giveawayId) {
        try {
            const giveaway = await database.getGiveaway(giveawayId);
            if (!giveaway) {
                return { success: false, message: 'Giveaway not found!' };
            }

            if (giveaway.ended) {
                return { success: false, message: 'Cannot cancel an ended giveaway!' };
            }

            await database.cancelGiveaway(giveawayId);
            this.activeGiveaways.delete(giveawayId);

            // Update original message
            try {
                const guild = this.client.guilds.cache.get(giveaway.guild_id);
                const channel = guild.channels.cache.get(giveaway.channel_id);
                const message = await channel.messages.fetch(giveaway.message_id);

                const cancelledEmbed = new EmbedBuilder()
                    .setColor(config.colors.error)
                    .setTitle('❌ Giveaway Cancelled')
                    .setDescription(`**${giveaway.title}** has been cancelled by an administrator.`)
                    .setTimestamp();

                await message.edit({ embeds: [cancelledEmbed], components: [] });
            } catch (error) {
                console.error('Error updating cancelled giveaway message:', error);
            }

            return { success: true, message: 'Giveaway cancelled successfully!' };

        } catch (error) {
            console.error('Error cancelling giveaway:', error);
            return { success: false, message: 'An error occurred while cancelling the giveaway!' };
        }
    }

    // Get user's giveaway history
    async getUserGiveawayHistory(userId, limit = 10) {
        try {
            return await database.getUserGiveawayHistory(userId, limit);
        } catch (error) {
            console.error('Error getting user giveaway history:', error);
            return [];
        }
    }

    // Get server's giveaway list
    async getServerGiveaways(guildId, includeEnded = false, limit = 10) {
        try {
            return await database.getServerGiveaways(guildId, includeEnded, limit);
        } catch (error) {
            console.error('Error getting server giveaways:', error);
            return [];
        }
    }
}

module.exports = GiveawaySystem;