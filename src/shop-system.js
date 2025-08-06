const { EmbedBuilder, ActionRowBuilder, SelectMenuBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const database = require('./database');
const config = require('../config.json');

class ShopSystem {
    constructor() {
        this.shopItems = {
            // Consumables
            consumables: [
                {
                    id: 'daily_booster',
                    name: '🚀 Daily Booster',
                    description: 'Doubles your next daily reward',
                    price: 500,
                    type: 'consumable',
                    category: 'consumables',
                    effect: 'daily_double',
                    emoji: '🚀'
                },
                {
                    id: 'work_energy',
                    name: '⚡ Work Energy',
                    description: 'Removes work cooldown for 1 hour',
                    price: 300,
                    type: 'consumable',
                    category: 'consumables',
                    effect: 'work_cooldown_reset',
                    emoji: '⚡'
                },
                {
                    id: 'lucky_charm',
                    name: '🍀 Lucky Charm',
                    description: 'Increases gambling win rate for 3 games',
                    price: 800,
                    type: 'consumable',
                    category: 'consumables',
                    effect: 'gambling_luck',
                    emoji: '🍀'
                },
                {
                    id: 'experience_potion',
                    name: '📚 Experience Potion',
                    description: 'Gain bonus WonderCash on next 5 commands',
                    price: 400,
                    type: 'consumable',
                    category: 'consumables',
                    effect: 'exp_boost',
                    emoji: '📚'
                }
            ],
            
            // Collectibles
            collectibles: [
                {
                    id: 'golden_coin',
                    name: '🪙 Golden Coin',
                    description: 'A rare collectible coin',
                    price: 2000,
                    type: 'collectible',
                    category: 'collectibles',
                    rarity: 'legendary',
                    emoji: '🪙'
                },
                {
                    id: 'diamond_ring',
                    name: '💍 Diamond Ring',
                    description: 'Sparkling diamond ring',
                    price: 5000,
                    type: 'collectible',
                    category: 'collectibles',
                    rarity: 'legendary',
                    emoji: '💍'
                },
                {
                    id: 'trophy_bronze',
                    name: '🥉 Bronze Trophy',
                    description: 'Achievement trophy',
                    price: 1000,
                    type: 'collectible',
                    category: 'collectibles',
                    rarity: 'common',
                    emoji: '🥉'
                },
                {
                    id: 'trophy_silver',
                    name: '🥈 Silver Trophy',
                    description: 'Prestigious silver trophy',
                    price: 2500,
                    type: 'collectible',
                    category: 'collectibles',
                    rarity: 'rare',
                    emoji: '🥈'
                },
                {
                    id: 'trophy_gold',
                    name: '🥇 Gold Trophy',
                    description: 'Ultimate gold trophy',
                    price: 5000,
                    type: 'collectible',
                    category: 'collectibles',
                    rarity: 'legendary',
                    emoji: '🥇'
                }
            ],
            
            // Profile Items
            profile: [
                {
                    id: 'custom_title',
                    name: '🏷️ Custom Title',
                    description: 'Set a custom title for your profile',
                    price: 1500,
                    type: 'profile',
                    category: 'profile',
                    effect: 'custom_title',
                    emoji: '🏷️'
                },
                {
                    id: 'profile_border',
                    name: '🖼️ Profile Border',
                    description: 'Special border for introduction cards',
                    price: 2000,
                    type: 'profile',
                    category: 'profile',
                    effect: 'card_border',
                    emoji: '🖼️'
                },
                {
                    id: 'name_color',
                    name: '🌈 Name Color',
                    description: 'Colorful name display',
                    price: 1200,
                    type: 'profile',
                    category: 'profile',
                    effect: 'name_color',
                    emoji: '🌈'
                }
            ],
            
            // Special Items
            special: [
                {
                    id: 'mystery_box',
                    name: '📦 Mystery Box',
                    description: 'Contains random items worth 500-2000 WonderCash',
                    price: 1000,
                    type: 'special',
                    category: 'special',
                    effect: 'mystery_box',
                    emoji: '📦'
                },
                {
                    id: 'xp_booster',
                    name: '⚡ XP Booster',
                    description: 'Double XP gain for 1 hour (All types)',
                    price: 2500,
                    type: 'consumable',
                    category: 'special',
                    effect: 'xp_boost',
                    duration: 60,
                    emoji: '⚡',
                    levelRequirement: {
                        overall: 5
                    }
                },
                {
                    id: 'premium_xp_booster',
                    name: '🌟 Premium XP Booster',
                    description: 'Triple XP gain for 2 hours (All types)',
                    price: 5000,
                    type: 'consumable',
                    category: 'special',
                    effect: 'premium_xp_boost',
                    duration: 120,
                    emoji: '🌟',
                    levelRequirement: {
                        overall: 15
                    }
                },
                {
                    id: 'voice_magnet',
                    name: '🎤 Voice Magnet',
                    description: 'Gain extra voice XP when others join your channel for 1 hour',
                    price: 1800,
                    type: 'consumable',
                    category: 'special',
                    effect: 'voice_magnet',
                    duration: 60,
                    emoji: '🎤',
                    levelRequirement: {
                        voice: 10
                    }
                },
                {
                    id: 'chat_streak',
                    name: '💬 Chat Streak',
                    description: 'No text XP cooldown for 30 minutes',
                    price: 1500,
                    type: 'consumable',
                    category: 'special',
                    effect: 'chat_streak',
                    duration: 30,
                    emoji: '💬',
                    levelRequirement: {
                        text: 8
                    }
                },
                {
                    id: 'legend_badge',
                    name: '🏆 Legend Badge',
                    description: 'Exclusive badge for reaching max level in any category',
                    price: 25000,
                    type: 'collectible',
                    category: 'special',
                    effect: 'legend_badge',
                    emoji: '🏆',
                    levelRequirement: {
                        overall: 50
                    }
                },
                {
                    id: 'ultimate_booster',
                    name: '🌟 Ultimate XP Booster',
                    description: 'Quintuple XP gain for 3 hours (Max level exclusive)',
                    price: 50000,
                    type: 'consumable',
                    category: 'special',
                    effect: 'ultimate_xp_boost',
                    duration: 180,
                    emoji: '🌟',
                    levelRequirement: {
                        overall: 45
                    }
                },
                {
                    id: 'master_title',
                    name: '👑 Master Title',
                    description: 'Exclusive title for reaching level 40+ in all categories',
                    price: 75000,
                    type: 'collectible',
                    category: 'special',
                    effect: 'master_title',
                    emoji: '👑',
                    levelRequirement: {
                        text: 40,
                        voice: 40,
                        role: 40
                    }
                }
            ]
        };
    }

    // Get all items in a category
    getCategoryItems(category) {
        return this.shopItems[category] || [];
    }

    // Get specific item by ID
    getItem(itemId) {
        for (const category in this.shopItems) {
            const item = this.shopItems[category].find(item => item.id === itemId);
            if (item) return item;
        }
        return null;
    }

    // Create shop main menu embed
    createShopEmbed() {
        const embed = new EmbedBuilder()
            .setColor(config.colors.primary)
            .setTitle('🏪 Wonder Shop')
            .setDescription('Welcome to the Wonder Shop! Browse categories to find amazing items.')
            .addFields(
                {
                    name: '🧪 Consumables',
                    value: 'Boosters, potions, and temporary effects',
                    inline: true
                },
                {
                    name: '💎 Collectibles',
                    value: 'Rare items and trophies to show off',
                    inline: true
                },
                {
                    name: '🎨 Profile Items',
                    value: 'Customize your profile and cards',
                    inline: true
                },
                {
                    name: '✨ Special Items',
                    value: 'Mystery boxes and lottery tickets',
                    inline: true
                },
                {
                    name: '💰 Your Balance',
                    value: 'Use `/balance` to check your WonderCash',
                    inline: true
                },
                {
                    name: '🎒 Your Inventory',
                    value: 'Use `/inventory` to view your items',
                    inline: true
                }
            )
            .setFooter({ text: 'Select a category below to browse items!' })
            .setTimestamp();

        return embed;
    }

    // Create category selection menu
    createCategoryMenu() {
        const selectMenu = new SelectMenuBuilder()
            .setCustomId('shop_category')
            .setPlaceholder('Choose a category to browse')
            .addOptions([
                {
                    label: 'Consumables',
                    description: 'Boosters and temporary effects',
                    value: 'consumables',
                    emoji: '🧪'
                },
                {
                    label: 'Collectibles',
                    description: 'Rare items and trophies',
                    value: 'collectibles',
                    emoji: '💎'
                },
                {
                    label: 'Profile Items',
                    description: 'Customize your appearance',
                    value: 'profile',
                    emoji: '🎨'
                },
                {
                    label: 'Special Items',
                    description: 'Mystery boxes and more',
                    value: 'special',
                    emoji: '✨'
                }
            ]);

        return new ActionRowBuilder().addComponents(selectMenu);
    }

    // Create category items embed
    createCategoryEmbed(category) {
        const items = this.getCategoryItems(category);
        const categoryNames = {
            consumables: '🧪 Consumables',
            collectibles: '💎 Collectibles',
            profile: '🎨 Profile Items',
            special: '✨ Special Items'
        };

        const embed = new EmbedBuilder()
            .setColor(config.colors.primary)
            .setTitle(`${categoryNames[category]} - Wonder Shop`)
            .setDescription(`Browse ${category} available for purchase:`)
            .setFooter({ text: 'Click on an item to view details and purchase!' })
            .setTimestamp();

        items.forEach(item => {
            const rarityEmoji = item.rarity === 'legendary' ? '⭐' : 
                              item.rarity === 'rare' ? '🌟' : '✨';
            
            let description = item.description;
            if (item.levelRequirement) {
                const requirements = Object.entries(item.levelRequirement)
                    .map(([type, level]) => {
                        const typeDisplay = type === 'overall' ? 'Overall' : type.charAt(0).toUpperCase() + type.slice(1);
                        return `${typeDisplay} Lv.${level}`;
                    })
                    .join(', ');
                description += `\n**Requires:** ${requirements}`;
            }
            
            embed.addFields({
                name: `${item.emoji} ${item.name} ${item.rarity ? rarityEmoji : ''}`,
                value: `${description}\n**Price:** ${item.price} ${config.currency.symbol}`,
                inline: true
            });
        });

        return embed;
    }

    // Create item selection menu for category
    createItemMenu(category) {
        const items = this.getCategoryItems(category);
        
        const selectMenu = new SelectMenuBuilder()
            .setCustomId(`shop_item_${category}`)
            .setPlaceholder('Choose an item to purchase')
            .addOptions(
                items.map(item => ({
                    label: item.name,
                    description: `${item.price} ${config.currency.symbol} - ${item.description.substring(0, 50)}...`,
                    value: item.id,
                    emoji: item.emoji
                }))
            );

        return new ActionRowBuilder().addComponents(selectMenu);
    }

    // Create item detail embed with purchase button
    createItemDetailEmbed(itemId) {
        const item = this.getItem(itemId);
        if (!item) return null;

        const rarityColors = {
            common: '#10B981',
            rare: '#3B82F6',
            legendary: '#F59E0B'
        };

        const embed = new EmbedBuilder()
            .setColor(item.rarity ? rarityColors[item.rarity] : config.colors.primary)
            .setTitle(`${item.emoji} ${item.name}`)
            .setDescription(item.description)
            .addFields(
                {
                    name: '💰 Price',
                    value: `${item.price} ${config.currency.symbol}`,
                    inline: true
                },
                {
                    name: '📦 Type',
                    value: item.type.charAt(0).toUpperCase() + item.type.slice(1),
                    inline: true
                }
            )
            .setFooter({ text: 'Click the button below to purchase this item!' })
            .setTimestamp();

        if (item.rarity) {
            embed.addFields({
                name: '⭐ Rarity',
                value: item.rarity.charAt(0).toUpperCase() + item.rarity.slice(1),
                inline: true
            });
        }

        if (item.levelRequirement) {
            const requirements = Object.entries(item.levelRequirement)
                .map(([type, level]) => {
                    const typeDisplay = type === 'overall' ? 'Overall' : type.charAt(0).toUpperCase() + type.slice(1);
                    return `${typeDisplay} Level ${level}`;
                })
                .join('\n');
            
            embed.addFields({
                name: '🔒 Level Requirements',
                value: requirements,
                inline: true
            });
        }

        if (item.effect) {
            const effectDescriptions = {
                daily_double: 'Doubles your next daily reward',
                work_cooldown_reset: 'Removes work cooldown temporarily',
                gambling_luck: 'Increases win rate in games',
                exp_boost: 'Bonus WonderCash on commands',
                custom_title: 'Set custom profile title',
                card_border: 'Special introduction card border',
                name_color: 'Colorful name display',
                mystery_box: 'Random valuable items',
                lottery: 'Entry into weekly lottery'
            };

            embed.addFields({
                name: '✨ Effect',
                value: effectDescriptions[item.effect] || 'Special effect',
                inline: false
            });
        }

        return embed;
    }

    // Create purchase button
    createPurchaseButton(itemId) {
        const button = new ButtonBuilder()
            .setCustomId(`purchase_${itemId}`)
            .setLabel('Purchase Item')
            .setStyle(ButtonStyle.Success)
            .setEmoji('💳');

        const backButton = new ButtonBuilder()
            .setCustomId('shop_back')
            .setLabel('Back to Shop')
            .setStyle(ButtonStyle.Secondary)
            .setEmoji('⬅️');

        return new ActionRowBuilder().addComponents(button, backButton);
    }

    // Process item purchase
    async purchaseItem(userId, itemId) {
        const item = this.getItem(itemId);
        if (!item) {
            return { success: false, message: 'Item not found!' };
        }

        const user = await database.getUser(userId);
        if (!user || user.balance < item.price) {
            return { 
                success: false, 
                message: `Insufficient funds! You need ${item.price} ${config.currency.symbol} but only have ${user?.balance || 0} ${config.currency.symbol}.` 
            };
        }

        // Check level requirements
        if (item.levelRequirement) {
            try {
                const userLevels = await database.getUserLevels(userId);
                for (const [levelType, requiredLevel] of Object.entries(item.levelRequirement)) {
                    const userLevel = userLevels[`${levelType}_level`] || userLevels[levelType === 'overall' ? 'overall_level' : `${levelType}_level`];
                    if (userLevel < requiredLevel) {
                        const levelTypeDisplay = levelType === 'overall' ? 'Overall' : levelType.charAt(0).toUpperCase() + levelType.slice(1);
                        return {
                            success: false,
                            message: `❌ Level requirement not met! You need **${levelTypeDisplay} Level ${requiredLevel}** but you're only **Level ${userLevel}**.`
                        };
                    }
                }
            } catch (error) {
                console.error('Error checking level requirements:', error);
                return { success: false, message: 'Error checking level requirements!' };
            }
        }

        try {
            // Deduct balance
            await database.updateBalance(userId, -item.price);
            
            // Add item to inventory
            await database.addItemToInventory(userId, itemId, 1);
            
            // Add transaction
            await database.addTransaction(userId, 'purchase', -item.price, `Purchased ${item.name}`);

            return { 
                success: true, 
                message: `Successfully purchased ${item.emoji} **${item.name}** for ${item.price} ${config.currency.symbol}!`,
                item: item
            };
        } catch (error) {
            console.error('Error purchasing item:', error);
            return { success: false, message: 'An error occurred during purchase!' };
        }
    }

    // Use consumable item
    async useItem(userId, itemId) {
        const item = this.getItem(itemId);
        if (!item) {
            return { success: false, message: 'Item not found!' };
        }

        const hasItem = await database.hasItem(userId, itemId);
        if (!hasItem) {
            return { success: false, message: 'You don\'t own this item!' };
        }

        if (item.type !== 'consumable') {
            return { success: false, message: 'This item cannot be consumed!' };
        }

        try {
            // Remove item from inventory
            await database.removeItemFromInventory(userId, itemId, 1);
            
            // Apply effect
            await database.addActiveEffect(userId, item.effect, this.getEffectDuration(item.effect));

            return { 
                success: true, 
                message: `Used ${item.emoji} **${item.name}**! Effect is now active.`,
                effect: item.effect
            };
        } catch (error) {
            console.error('Error using item:', error);
            return { success: false, message: 'An error occurred while using the item!' };
        }
    }

    // Get effect duration in minutes
    getEffectDuration(effect) {
        const durations = {
            daily_double: 1440, // 24 hours
            work_cooldown_reset: 60, // 1 hour
            gambling_luck: 30, // 30 minutes (3 games)
            exp_boost: 120 // 2 hours
        };
        return durations[effect] || 60;
    }

    // Open mystery box
    async openMysteryBox(userId) {
        const possibleRewards = [
            { type: 'coins', amount: 500 },
            { type: 'coins', amount: 750 },
            { type: 'coins', amount: 1000 },
            { type: 'coins', amount: 1500 },
            { type: 'coins', amount: 2000 },
            { type: 'item', id: 'daily_booster' },
            { type: 'item', id: 'work_energy' },
            { type: 'item', id: 'lucky_charm' },
            { type: 'item', id: 'trophy_bronze' }
        ];

        const reward = possibleRewards[Math.floor(Math.random() * possibleRewards.length)];
        
        try {
            if (reward.type === 'coins') {
                await database.updateBalance(userId, reward.amount);
                await database.addTransaction(userId, 'mystery_box', reward.amount, 'Mystery box reward');
                return { 
                    success: true, 
                    type: 'coins',
                    amount: reward.amount,
                    message: `🎉 You received **${reward.amount}** ${config.currency.symbol} WonderCash!`
                };
            } else {
                const item = this.getItem(reward.id);
                await database.addItemToInventory(userId, reward.id, 1);
                return { 
                    success: true, 
                    type: 'item',
                    item: item,
                    message: `🎉 You received ${item.emoji} **${item.name}**!`
                };
            }
        } catch (error) {
            console.error('Error opening mystery box:', error);
            return { success: false, message: 'An error occurred while opening the mystery box!' };
        }
    }
}

module.exports = ShopSystem;