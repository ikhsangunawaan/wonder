const { Client, GatewayIntentBits, Collection, Events, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, ModalBuilder, TextInputBuilder, TextInputStyle, AttachmentBuilder } = require('discord.js');
const fs = require('fs');
const path = require('path');
const database = require('./database');
const config = require('../config.json');
const CanvasUtils = require('./utils/canvas');
const { deployCommands } = require('./slash-commands');
const SlashHandlers = require('./slash-handlers');
const RoleManager = require('./role-manager');
const ShopSystem = require('./shop-system');
const CooldownManager = require('./cooldown-manager');
const GiveawaySystem = require('./giveaway-system');
const LevelingSystem = require('./leveling-system');
 cursor/tambahkan-fitur-leveling-roles-dan-level-d928
const WonderCoinsDropSystem = require('./wondercoins-drop-system');

 main

// Load environment variables
require('dotenv').config();

class WonderBot {
    constructor() {
        this.client = new Client({
            intents: [
                GatewayIntentBits.Guilds,
                GatewayIntentBits.GuildMessages,
                GatewayIntentBits.MessageContent,
                GatewayIntentBits.GuildMembers,
                GatewayIntentBits.GuildMessageReactions
            ]
        });

        this.commands = new Collection();
        this.slashCommands = new Collection();
        this.canvas = new CanvasUtils();
        this.slashHandlers = new SlashHandlers();
        this.roleManager = new RoleManager(this.client);
        this.shopSystem = new ShopSystem();
        this.cooldownManager = new CooldownManager();
        this.giveawaySystem = new GiveawaySystem(this.client);
        this.levelingSystem = new LevelingSystem(this.client);
 cursor/tambahkan-fitur-leveling-roles-dan-level-d928
        this.dropSystem = new WonderCoinsDropSystem(this.client);

 main
        
        this.setupEventHandlers();
        this.loadCommands();
        this.loadSlashCommands();
    }

    setupEventHandlers() {
        this.client.once(Events.ClientReady, async () => {
            console.log(`✅ Luxury Kingdom Bot is ready! Logged in as ${this.client.user.tag}`);
            this.client.user.setActivity('w.help | Luxury Kingdom 🏰 WonderCoins 💰', { type: 'WATCHING' });
 cursor/tambahkan-fitur-leveling-roles-dan-level-d928
            
            // Initialize drop system reference
            this.client.bot = this;

 main
            
            // Deploy slash commands
            await deployCommands();
            
            // Start periodic cleanup of expired effects
            setInterval(() => {
                this.cooldownManager.cleanupExpiredEffects();
            }, 10 * 60 * 1000); // Every 10 minutes
        });

        this.client.on(Events.MessageCreate, this.handleMessage.bind(this));
        this.client.on(Events.InteractionCreate, this.handleInteraction.bind(this));
        this.client.on(Events.GuildMemberAdd, this.handleMemberJoin.bind(this));
        this.client.on(Events.GuildMemberUpdate, this.handleMemberUpdate.bind(this));
        this.client.on(Events.VoiceStateUpdate, this.handleVoiceStateUpdate.bind(this));
        
        // Start periodic cleanup and voice session updates
        setInterval(() => {
            this.cooldownManager.cleanupExpiredEffects();
            this.levelingSystem.updateActiveVoiceSessions();
        }, 60 * 1000); // Every minute
    }

    async handleMessage(message) {
        if (message.author.bot) return;

        // Handle leveling XP for non-command messages
        if (!message.content.startsWith(config.prefix) && config.leveling?.enabled) {
            try {
                await database.createUser(message.author.id, message.author.username);
                await this.levelingSystem.addTextXP(message.author.id, message);
            } catch (error) {
                console.error('Error adding text XP:', error);
            }
            return;
        }

        // Handle commands
        if (!message.content.startsWith(config.prefix)) return;

        const args = message.content.slice(config.prefix.length).trim().split(/ +/);
        const commandName = args.shift().toLowerCase();

        const command = this.commands.get(commandName) || this.commands.find(cmd => cmd.aliases && cmd.aliases.includes(commandName));
        if (!command) return;

        try {
            // Ensure user exists in database
            await database.createUser(message.author.id, message.author.username);
            await command.execute(message, args, this);
        } catch (error) {
            console.error('Error executing command:', error);
            message.reply('❌ There was an error executing that command!');
        }
    }

    async handleInteraction(interaction) {
        if (interaction.isChatInputCommand()) {
            try {
                await database.createUser(interaction.user.id, interaction.user.username);
                
                // Route to appropriate handler
                switch (interaction.commandName) {
                    case 'balance':
                        await this.slashHandlers.handleBalance(interaction);
                        break;
                    case 'daily':
                        await this.slashHandlers.handleDaily(interaction);
                        break;
                    case 'work':
                        await this.slashHandlers.handleWork(interaction);
                        break;
                    case 'leaderboard':
                        await this.slashHandlers.handleLeaderboard(interaction);
                        break;
                    case 'coinflip':
                        await this.slashHandlers.handleCoinflip(interaction);
                        break;
                    case 'dice':
                        await this.slashHandlers.handleDice(interaction);
                        break;
                    case 'slots':
                        await this.slashHandlers.handleSlots(interaction);
                        break;
                    case 'intro':
                        // Pass bot instance for modal handling
                        interaction.bot = this;
                        await this.slashHandlers.handleIntro(interaction);
                        break;
                    case 'setup':
                        await this.slashHandlers.handleSetup(interaction);
                        break;
                    case 'help':
                        await this.slashHandlers.handleHelp(interaction);
                        break;
                    case 'giveaway':
                        // Pass bot instance for giveaway system access
                        interaction.bot = this;
                        await this.slashHandlers.handleGiveaway(interaction);
                        break;
                    case 'level':
                        interaction.client.bot = this;
                        await this.slashHandlers.handleLevel(interaction);
                        break;
                    case 'rank':
                        interaction.client.bot = this;
                        await this.slashHandlers.handleRank(interaction);
                        break;
                    case 'rewards':
                        await this.slashHandlers.handleRewards(interaction);
                        break;
                    case 'give-xp':
                        interaction.client.bot = this;
                        await this.slashHandlers.handleGiveXP(interaction);
                        break;
                    case 'reset-level':
                        await this.slashHandlers.handleResetLevel(interaction);
                        break;
                    case 'level-role':
                        await this.slashHandlers.handleLevelRole(interaction);
                        break;
 cursor/tambahkan-fitur-leveling-roles-dan-level-d928
                    case 'drops':
                        await this.slashHandlers.handleDrops(interaction);
                        break;

 main
                }
            } catch (error) {
                console.error('Error executing slash command:', error);
                await interaction.reply({ content: '❌ There was an error executing that command!', ephemeral: true });
            }
        } else if (interaction.isButton()) {
            await this.handleButtonInteraction(interaction);
        } else if (interaction.isStringSelectMenu()) {
            await this.handleSelectMenuInteraction(interaction);
        } else if (interaction.isModalSubmit()) {
            await this.handleModalSubmit(interaction);
        }
    }

    async handleButtonInteraction(interaction) {
        const [action, ...params] = interaction.customId.split('_');

        switch (action) {
            case 'intro':
                await this.showIntroductionModal(interaction);
                break;
            case 'giveaway':
                if (params[0] === 'enter') {
                    await this.handleGiveawayEntry(interaction, params[1]);
                }
                break;
            case 'purchase':
                await this.handleItemPurchase(interaction, params[0]);
                break;
            case 'shop':
                if (params[0] === 'back') {
                    const embed = this.shopSystem.createShopEmbed();
                    const categoryMenu = this.shopSystem.createCategoryMenu();
                    await interaction.update({ embeds: [embed], components: [categoryMenu] });
                }
                break;
            case 'coinflip':
                await this.handleCoinflipGame(interaction, params[0], parseInt(params[1]));
                break;
            case 'dice':
                await this.handleDiceGame(interaction, parseInt(params[0]));
                break;
            case 'slots':
                await this.handleSlotsGame(interaction, parseInt(params[0]));
                break;
            case 'collect':
            case 'quick':
            case 'lucky':
                await this.dropSystem.handleDropCollection(interaction);
                break;
        }
    }

    async handleSelectMenuInteraction(interaction) {
        const [action, ...params] = interaction.customId.split('_');

        if (action === 'shop') {
            if (params[0] === 'category') {
                const category = interaction.values[0];
                const embed = this.shopSystem.createCategoryEmbed(category);
                const itemMenu = this.shopSystem.createItemMenu(category);
                await interaction.update({ embeds: [embed], components: [itemMenu] });
            } else if (params[0] === 'item') {
                const itemId = interaction.values[0];
                const embed = this.shopSystem.createItemDetailEmbed(itemId);
                const purchaseButton = this.shopSystem.createPurchaseButton(itemId);
                await interaction.update({ embeds: [embed], components: [purchaseButton] });
            }
        }
    }

    async handleItemPurchase(interaction, itemId) {
        const result = await this.shopSystem.purchaseItem(interaction.user.id, itemId);
        
        if (result.success) {
            const embed = new EmbedBuilder()
                .setColor(config.colors.success)
                .setTitle('✅ Purchase Successful!')
                .setDescription(result.message)
                .setTimestamp();
            
            await interaction.reply({ embeds: [embed], ephemeral: true });
        } else {
            const embed = new EmbedBuilder()
                .setColor(config.colors.error)
                .setTitle('❌ Purchase Failed')
                .setDescription(result.message)
                .setTimestamp();
            
            await interaction.reply({ embeds: [embed], ephemeral: true });
        }
    }

    async handleGiveawayEntry(interaction, giveawayId) {
        const member = interaction.guild.members.cache.get(interaction.user.id);
        const result = await this.giveawaySystem.enterGiveaway(interaction.user.id, parseInt(giveawayId), member);
        
        if (result.success) {
            const embed = new EmbedBuilder()
                .setColor(config.colors.success)
                .setTitle('🎉 Successfully Entered!')
                .setDescription(result.message)
                .addFields({
                    name: '📊 Total Entries',
                    value: result.entryCount.toString(),
                    inline: true
                })
                .setTimestamp();
            
            await interaction.reply({ embeds: [embed], ephemeral: true });
        } else {
            const embed = new EmbedBuilder()
                .setColor(config.colors.error)
                .setTitle('❌ Entry Failed')
                .setDescription(result.message)
                .setTimestamp();
            
            await interaction.reply({ embeds: [embed], ephemeral: true });
        }
    }

    async handleModalSubmit(interaction) {
        if (interaction.customId === 'introduction_modal') {
            await this.processIntroductionForm(interaction);
        }
    }

    async handleMemberJoin(member) {
        const settings = await database.getServerSettings(member.guild.id);
        if (!settings || !settings.welcome_channel) return;

        const welcomeChannel = member.guild.channels.cache.get(settings.welcome_channel);
        if (!welcomeChannel) return;

        const embed = new EmbedBuilder()
            .setColor(config.colors.primary)
            .setTitle('🎉 Welcome to the server!')
            .setDescription(`Hey ${member}, welcome to **${member.guild.name}**!\n\n${settings.welcome_message || 'We\'re glad to have you here!'}`)
            .setThumbnail(member.user.displayAvatarURL())
            .setFooter({ text: 'Wonder Bot', iconURL: this.client.user.displayAvatarURL() })
            .setTimestamp();

        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('intro_create')
                    .setLabel('Create Introduction Card')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('📝')
            );

        await welcomeChannel.send({ embeds: [embed], components: [row] });
        
        // Create user in database
        await database.createUser(member.id, member.user.username);
        
        // Auto-assign roles if applicable
        await this.roleManager.autoAssignRoles(member);
    }

    async handleMemberUpdate(oldMember, newMember) {
        // Handle role updates
        await this.roleManager.handleRoleUpdate(oldMember, newMember);
    }

    async showIntroductionModal(interaction) {
        const modal = new ModalBuilder()
            .setCustomId('introduction_modal')
            .setTitle('Create Your Introduction Card');

        const nameInput = new TextInputBuilder()
            .setCustomId('name')
            .setLabel('Your Name')
            .setStyle(TextInputStyle.Short)
            .setRequired(true)
            .setMaxLength(50);

        const ageInput = new TextInputBuilder()
            .setCustomId('age')
            .setLabel('Your Age')
            .setStyle(TextInputStyle.Short)
            .setRequired(true)
            .setMaxLength(3);

        const locationInput = new TextInputBuilder()
            .setCustomId('location')
            .setLabel('Your Location')
            .setStyle(TextInputStyle.Short)
            .setRequired(true)
            .setMaxLength(100);

        const hobbiesInput = new TextInputBuilder()
            .setCustomId('hobbies')
            .setLabel('Hobbies & Interests')
            .setStyle(TextInputStyle.Paragraph)
            .setRequired(true)
            .setMaxLength(200);

        const bioInput = new TextInputBuilder()
            .setCustomId('bio')
            .setLabel('About You')
            .setStyle(TextInputStyle.Paragraph)
            .setRequired(true)
            .setMaxLength(300);

        const colorInput = new TextInputBuilder()
            .setCustomId('color')
            .setLabel('Favorite Color (hex code, e.g., #7C3AED)')
            .setStyle(TextInputStyle.Short)
            .setRequired(false)
            .setMaxLength(7);

        modal.addComponents(
            new ActionRowBuilder().addComponents(nameInput),
            new ActionRowBuilder().addComponents(ageInput),
            new ActionRowBuilder().addComponents(locationInput),
            new ActionRowBuilder().addComponents(hobbiesInput),
            new ActionRowBuilder().addComponents(bioInput)
        );

        await interaction.showModal(modal);
    }

    async processIntroductionForm(interaction) {
        const name = interaction.fields.getTextInputValue('name');
        const age = parseInt(interaction.fields.getTextInputValue('age'));
        const location = interaction.fields.getTextInputValue('location');
        const hobbies = interaction.fields.getTextInputValue('hobbies');
        const bio = interaction.fields.getTextInputValue('bio');
        const favoriteColor = interaction.fields.getTextInputValue('color') || '#7C3AED';

        if (isNaN(age) || age < 1 || age > 150) {
            return await interaction.reply({ content: '❌ Please enter a valid age!', ephemeral: true });
        }

        try {
            // Save to database
            await database.saveIntroCard({
                userId: interaction.user.id,
                name,
                age,
                location,
                hobbies,
                favoriteColor,
                bio
            });

            // Generate image
            const cardBuffer = await this.canvas.createIntroductionCard(interaction.user, {
                name, age, location, hobbies, favorite_color: favoriteColor, bio
            });

            const attachment = new AttachmentBuilder(cardBuffer, { name: 'introduction.png' });

            const embed = new EmbedBuilder()
                .setColor(favoriteColor)
                .setTitle('📝 New Introduction Card!')
                .setDescription(`Welcome ${name} to our community!`)
                .setImage('attachment://introduction.png')
                .setFooter({ text: 'Wonder Bot', iconURL: this.client.user.displayAvatarURL() })
                .setTimestamp();

            // Send to introduction channel
            const introChannel = interaction.guild.channels.cache.get(process.env.INTRODUCTION_CHANNEL_ID);
            if (introChannel) {
                await introChannel.send({ embeds: [embed], files: [attachment] });
            }

            // Reward user with WonderCash
            await database.updateBalance(interaction.user.id, 200);
            await database.addTransaction(interaction.user.id, 'intro_reward', 200, 'Introduction card creation reward');

            await interaction.reply({ 
                content: `✅ Your introduction card has been created and posted! You earned 200 ${config.currency.symbol} ${config.currency.name}!`, 
                ephemeral: true 
            });

        } catch (error) {
            console.error('Error creating introduction card:', error);
            await interaction.reply({ content: '❌ There was an error creating your introduction card!', ephemeral: true });
        }
    }

    loadCommands() {
        // Economy commands
        this.addCommand('balance', {
            description: 'Check your WonderCash balance',
            aliases: ['bal', 'money'],
            execute: async (message, args, bot) => {
                const targetUser = message.mentions.users.first() || message.author;
                const user = await database.getUser(targetUser.id);
                
                if (!user) {
                    await database.createUser(targetUser.id, targetUser.username);
                    const newUser = await database.getUser(targetUser.id);
                    user = newUser;
                }

                const embed = new EmbedBuilder()
                    .setColor(config.colors.primary)
                    .setTitle(`💰 ${targetUser.username}'s Wallet`)
                    .setDescription(`**Balance:** ${user.balance} ${config.currency.symbol} ${config.currency.name}`)
                    .setThumbnail(targetUser.displayAvatarURL())
                    .setFooter({ text: 'Wonder Bot Economy' })
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });

        this.addCommand('daily', {
            description: 'Claim your daily WonderCash',
            execute: async (message, args, bot) => {
                // Check cooldown
                const cooldownCheck = await bot.cooldownManager.checkCooldown(message.author.id, 'daily');
                if (cooldownCheck.onCooldown) {
                    const cooldownMessage = bot.cooldownManager.createCooldownMessage('daily', cooldownCheck.timeLeft);
                    return await message.reply(cooldownMessage);
                }

                let amount = config.currency.dailyAmount;
                
                // Check for booster/premium bonuses
                const member = message.guild.members.cache.get(message.author.id);
                if (member.roles.cache.has(process.env.BOOSTER_ROLE_ID)) {
                    amount += config.booster.dailyBonus;
                }
                if (member.roles.cache.has(process.env.PREMIUM_ROLE_ID)) {
                    amount += config.premium.dailyBonus;
                }

                // Check for daily double effect
                const hasDouble = await bot.cooldownManager.hasDailyDouble(message.author.id);
                if (hasDouble) {
                    amount *= 2;
                }

                // Check for experience boost
                const hasExpBoost = await bot.cooldownManager.hasExperienceBoost(message.author.id);
                if (hasExpBoost) {
                    amount += Math.floor(amount * 0.2); // 20% bonus
                }

                await database.updateBalance(message.author.id, amount);
                await bot.cooldownManager.setCooldown(message.author.id, 'daily');
                await database.addTransaction(message.author.id, 'daily', amount, 'Daily reward claimed');

                const embed = new EmbedBuilder()
                    .setColor(config.colors.success)
                    .setTitle('💰 Daily Reward Claimed!')
                    .setDescription(`You received **${amount}** ${config.currency.symbol} ${config.currency.name}!${hasDouble ? '\n🚀 **Daily Booster** activated! (2x reward)' : ''}${hasExpBoost ? '\n📚 **Experience Boost** applied! (+20%)' : ''}`)
                    .setFooter({ text: 'Come back tomorrow for another reward!' })
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });

        this.addCommand('work', {
            description: 'Work to earn WonderCash',
            execute: async (message, args, bot) => {
                // Check cooldown
                const cooldownCheck = await bot.cooldownManager.checkCooldown(message.author.id, 'work');
                if (cooldownCheck.onCooldown) {
                    const cooldownMessage = bot.cooldownManager.createCooldownMessage('work', cooldownCheck.timeLeft);
                    return await message.reply(cooldownMessage);
                }

                const jobs = [
                    'delivered packages', 'coded a website', 'taught a class', 'wrote articles',
                    'designed graphics', 'managed social media', 'fixed computers', 'cooked meals',
                    'cleaned offices', 'walked dogs', 'painted houses', 'tutored students'
                ];

                let baseAmount = config.currency.workAmount;
                const randomMultiplier = Math.random() * 0.5 + 0.75; // 0.75x to 1.25x
                let amount = Math.floor(baseAmount * randomMultiplier);

                // Check for booster/premium bonuses
                const member = message.guild.members.cache.get(message.author.id);
                if (member.roles.cache.has(process.env.BOOSTER_ROLE_ID)) {
                    amount += config.booster.workBonus;
                }
                if (member.roles.cache.has(process.env.PREMIUM_ROLE_ID)) {
                    amount += config.premium.workBonus;
                }

                // Check for experience boost
                const hasExpBoost = await bot.cooldownManager.hasExperienceBoost(message.author.id);
                if (hasExpBoost) {
                    amount += Math.floor(amount * 0.2); // 20% bonus
                }

                const randomJob = jobs[Math.floor(Math.random() * jobs.length)];

                await database.updateBalance(message.author.id, amount);
                await bot.cooldownManager.setCooldown(message.author.id, 'work');
                await database.addTransaction(message.author.id, 'work', amount, `Worked: ${randomJob}`);

                const embed = new EmbedBuilder()
                    .setColor(config.colors.success)
                    .setTitle('💼 Work Complete!')
                    .setDescription(`You ${randomJob} and earned **${amount}** ${config.currency.symbol} ${config.currency.name}!${hasExpBoost ? '\n📚 **Experience Boost** applied! (+20%)' : ''}`)
                    .setFooter({ text: 'You can work again in 1 hour!' })
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });

        this.addCommand('leaderboard', {
            description: 'View the WonderCash leaderboard',
            aliases: ['lb', 'top'],
            execute: async (message, args, bot) => {
                const topUsers = await database.getTopUsers(10);
                
                if (topUsers.length === 0) {
                    return await message.reply('📊 No users found in the leaderboard yet!');
                }

                let description = '';
                for (let i = 0; i < topUsers.length; i++) {
                    const user = topUsers[i];
                    const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`;
                    description += `${medal} **${user.username}** - ${user.balance} ${config.currency.symbol}\n`;
                }

                const embed = new EmbedBuilder()
                    .setColor(config.colors.primary)
                    .setTitle('🏆 WonderCash Leaderboard')
                    .setDescription(description)
                    .setFooter({ text: 'Keep earning to climb the ranks!' })
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });

        // Game commands
        this.addCommand('coinflip', {
            description: 'Bet WonderCash on a coin flip',
            aliases: ['cf'],
            execute: async (message, args, bot) => {
                // Check cooldown
                const member = message.guild.members.cache.get(message.author.id);
                const cooldownCheck = await bot.cooldownManager.checkCooldown(message.author.id, 'coinflip');
                const canBypass = await bot.cooldownManager.canBypassCooldown(message.author.id, 'coinflip', member);
                
                if (cooldownCheck.onCooldown && !canBypass) {
                    const cooldownMessage = bot.cooldownManager.createCooldownMessage('coinflip', cooldownCheck.timeLeft);
                    return await message.reply(cooldownMessage);
                }

                if (!args[0] || !args[1]) {
                    return await message.reply('❌ Usage: `w.coinflip <heads/tails> <amount>`');
                }

                const choice = args[0].toLowerCase();
                const amount = parseInt(args[1]);

                if (!['heads', 'tails'].includes(choice)) {
                    return await message.reply('❌ Choose either `heads` or `tails`!');
                }

                if (isNaN(amount) || amount < config.games.coinflip.minBet || amount > config.games.coinflip.maxBet) {
                    return await message.reply(`❌ Bet amount must be between ${config.games.coinflip.minBet} and ${config.games.coinflip.maxBet} ${config.currency.symbol}!`);
                }

                const user = await database.getUser(message.author.id);
                if (user.balance < amount) {
                    return await message.reply(`❌ You don't have enough ${config.currency.name}! Your balance: ${user.balance} ${config.currency.symbol}`);
                }

                // Check for gambling luck effect
                const hasLuck = await bot.cooldownManager.applyGamblingLuck(message.author.id);
                let winChance = 0.5;
                if (hasLuck) {
                    winChance = 0.65; // 65% win chance with luck
                }

                const result = Math.random() < 0.5 ? 'heads' : 'tails';
                let won = choice === result;
                
                // Apply luck effect
                if (hasLuck && !won && Math.random() < 0.3) {
                    won = true; // 30% chance to turn loss into win with luck
                }

                const winAmount = won ? amount : -amount;

                await database.updateBalance(message.author.id, winAmount);
                await bot.cooldownManager.setCooldown(message.author.id, 'coinflip');
                await database.addTransaction(message.author.id, 'coinflip', winAmount, `Coinflip ${won ? 'win' : 'loss'}: ${choice} vs ${result}`);

                const embed = new EmbedBuilder()
                    .setColor(won ? config.colors.success : config.colors.error)
                    .setTitle('🪙 Coin Flip Result')
                    .setDescription(`The coin landed on **${result}**!\n\n${won ? '🎉 You won!' : '😔 You lost!'}\n**${won ? '+' : ''}${winAmount}** ${config.currency.symbol} ${config.currency.name}${hasLuck ? '\n🍀 **Lucky Charm** used!' : ''}`)
                    .setFooter({ text: `Your balance: ${user.balance + winAmount} ${config.currency.symbol} | Next flip in 2 minutes` })
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });

        this.addCommand('dice', {
            description: 'Roll dice and bet on the outcome',
            execute: async (message, args, bot) => {
                if (!args[0]) {
                    return await message.reply('❌ Usage: `w.dice <amount>`');
                }

                const amount = parseInt(args[0]);

                if (isNaN(amount) || amount < config.games.dice.minBet || amount > config.games.dice.maxBet) {
                    return await message.reply(`❌ Bet amount must be between ${config.games.dice.minBet} and ${config.games.dice.maxBet} ${config.currency.symbol}!`);
                }

                const user = await database.getUser(message.author.id);
                if (user.balance < amount) {
                    return await message.reply(`❌ You don't have enough ${config.currency.name}! Your balance: ${user.balance} ${config.currency.symbol}`);
                }

                const dice1 = Math.floor(Math.random() * 6) + 1;
                const dice2 = Math.floor(Math.random() * 6) + 1;
                const total = dice1 + dice2;

                let multiplier = 0;
                let result = '';

                if (total === 7) {
                    multiplier = 3;
                    result = '🎉 Lucky 7! Triple your bet!';
                } else if (total === 2 || total === 12) {
                    multiplier = 2;
                    result = '🎊 Snake eyes or Boxcars! Double your bet!';
                } else if (total >= 8 && total <= 10) {
                    multiplier = 1.5;
                    result = '😊 Good roll! 1.5x your bet!';
                } else {
                    multiplier = 0;
                    result = '😔 Better luck next time!';
                }

                const winAmount = Math.floor(amount * multiplier) - amount;

                await database.updateBalance(message.author.id, winAmount);
                await database.addTransaction(message.author.id, 'dice', winAmount, `Dice roll: ${dice1}+${dice2}=${total}`);

                const embed = new EmbedBuilder()
                    .setColor(winAmount > 0 ? config.colors.success : config.colors.error)
                    .setTitle('🎲 Dice Roll Result')
                    .setDescription(`🎲 ${dice1} + ${dice2} = **${total}**\n\n${result}\n**${winAmount >= 0 ? '+' : ''}${winAmount}** ${config.currency.symbol} ${config.currency.name}`)
                    .setFooter({ text: `Your balance: ${user.balance + winAmount} ${config.currency.symbol}` })
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });

        this.addCommand('slots', {
            description: 'Play the slot machine',
            execute: async (message, args, bot) => {
                if (!args[0]) {
                    return await message.reply('❌ Usage: `w.slots <amount>`');
                }

                const amount = parseInt(args[0]);

                if (isNaN(amount) || amount < config.games.slots.minBet || amount > config.games.slots.maxBet) {
                    return await message.reply(`❌ Bet amount must be between ${config.games.slots.minBet} and ${config.games.slots.maxBet} ${config.currency.symbol}!`);
                }

                const user = await database.getUser(message.author.id);
                if (user.balance < amount) {
                    return await message.reply(`❌ You don't have enough ${config.currency.name}! Your balance: ${user.balance} ${config.currency.symbol}`);
                }

                const symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣'];
                const reel1 = symbols[Math.floor(Math.random() * symbols.length)];
                const reel2 = symbols[Math.floor(Math.random() * symbols.length)];
                const reel3 = symbols[Math.floor(Math.random() * symbols.length)];

                let multiplier = 0;
                let result = '';

                if (reel1 === reel2 && reel2 === reel3) {
                    if (reel1 === '💎') {
                        multiplier = 10;
                        result = '💎 JACKPOT! Diamond Triple!';
                    } else if (reel1 === '7️⃣') {
                        multiplier = 7;
                        result = '🎰 Lucky 777!';
                    } else {
                        multiplier = 3;
                        result = '🎉 Triple Match!';
                    }
                } else if (reel1 === reel2 || reel2 === reel3 || reel1 === reel3) {
                    multiplier = 1.5;
                    result = '😊 Double Match!';
                } else {
                    multiplier = 0;
                    result = '😔 No match, try again!';
                }

                const winAmount = Math.floor(amount * multiplier) - amount;

                await database.updateBalance(message.author.id, winAmount);
                await database.addTransaction(message.author.id, 'slots', winAmount, `Slots: ${reel1}${reel2}${reel3}`);

                const embed = new EmbedBuilder()
                    .setColor(winAmount > 0 ? config.colors.success : config.colors.error)
                    .setTitle('🎰 Slot Machine')
                    .setDescription(`${reel1} | ${reel2} | ${reel3}\n\n${result}\n**${winAmount >= 0 ? '+' : ''}${winAmount}** ${config.currency.symbol} ${config.currency.name}`)
                    .setFooter({ text: `Your balance: ${user.balance + winAmount} ${config.currency.symbol}` })
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });

        // Shop and inventory commands
        this.addCommand('shop', {
            description: 'Browse the Wonder Shop',
            execute: async (message, args, bot) => {
                const embed = bot.shopSystem.createShopEmbed();
                const categoryMenu = bot.shopSystem.createCategoryMenu();
                await message.reply({ embeds: [embed], components: [categoryMenu] });
            }
        });

        this.addCommand('inventory', {
            description: 'View your inventory',
            aliases: ['inv'],
            execute: async (message, args, bot) => {
                const inventory = await database.getUserInventory(message.author.id);
                
                if (inventory.length === 0) {
                    return await message.reply('🎒 Your inventory is empty! Visit the shop with `w.shop` to buy items.');
                }

                const embed = new EmbedBuilder()
                    .setColor(config.colors.primary)
                    .setTitle('🎒 Your Inventory')
                    .setDescription('Here are all your items:')
                    .setFooter({ text: 'Use w.use <item_name> to use consumable items!' })
                    .setTimestamp();

                let itemsList = '';
                for (const item of inventory) {
                    const itemData = bot.shopSystem.getItem(item.item_id);
                    if (itemData) {
                        itemsList += `${itemData.emoji} **${itemData.name}** x${item.quantity}\n`;
                    }
                }

                embed.addFields({
                    name: '📦 Items',
                    value: itemsList || 'No items found',
                    inline: false
                });

                await message.reply({ embeds: [embed] });
            }
        });

        this.addCommand('use', {
            description: 'Use a consumable item',
            execute: async (message, args, bot) => {
                if (!args[0]) {
                    return await message.reply('❌ Usage: `w.use <item_name>`\nExample: `w.use daily_booster`');
                }

                // Check cooldown for item usage
                const cooldownCheck = await bot.cooldownManager.checkCooldown(message.author.id, 'use_item');
                if (cooldownCheck.onCooldown) {
                    const cooldownMessage = bot.cooldownManager.createCooldownMessage('use_item', cooldownCheck.timeLeft);
                    return await message.reply(cooldownMessage);
                }

                const itemId = args[0].toLowerCase();
                const result = await bot.shopSystem.useItem(message.author.id, itemId);

                if (!result.success) {
                    return await message.reply(`❌ ${result.message}`);
                }

                await bot.cooldownManager.setCooldown(message.author.id, 'use_item');

                const embed = new EmbedBuilder()
                    .setColor(config.colors.success)
                    .setTitle('✨ Item Used!')
                    .setDescription(result.message)
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });

        // Giveaway commands
        this.addCommand('gstart', {
            description: 'Start a giveaway (Admin only)',
            execute: async (message, args, bot) => {
                if (!message.member.permissions.has('MANAGE_GUILD')) {
                    return await message.reply('❌ You need **Manage Server** permissions to create giveaways!');
                }

                if (args.length < 4) {
                    return await message.reply('❌ Usage: `w.gstart <duration> <winners> <prize> [title]`\nExample: `w.gstart 1h 1 100 WonderCash Daily Giveaway`');
                }

                const duration = this.parseDuration(args[0]);
                if (!duration) {
                    return await message.reply('❌ Invalid duration! Use format like: 1h, 30m, 2d, etc.');
                }

                const winnerCount = parseInt(args[1]);
                if (isNaN(winnerCount) || winnerCount < 1 || winnerCount > 10) {
                    return await message.reply('❌ Winner count must be between 1 and 10!');
                }

                const prize = args.slice(2).join(' ');
                const title = args.length > 4 ? args.slice(3).join(' ') : 'Giveaway';

                try {
                    const giveaway = await bot.giveawaySystem.createGiveaway(message.guild, message.channel.id, {
                        title: title,
                        description: `Win **${prize}**!`,
                        prize: prize,
                        winnerCount: winnerCount,
                        duration: duration,
                        createdBy: message.author.id,
                        restrictWinners: true
                    });

                    const embed = bot.giveawaySystem.createGiveawayEmbed(giveaway);
                    const button = bot.giveawaySystem.createGiveawayButton(giveaway.id);

                    const giveawayMessage = await message.channel.send({
                        content: '🎉 **GIVEAWAY** 🎉',
                        embeds: [embed],
                        components: [button]
                    });

                    await database.updateGiveawayMessageId(giveaway.id, giveawayMessage.id);
                    await message.delete();

                } catch (error) {
                    console.error('Error creating giveaway:', error);
                    await message.reply('❌ Failed to create giveaway!');
                }
            }
        });

        this.addCommand('gend', {
            description: 'End a giveaway early (Admin only)',
            execute: async (message, args, bot) => {
                if (!message.member.permissions.has('MANAGE_GUILD')) {
                    return await message.reply('❌ You need **Manage Server** permissions to end giveaways!');
                }

                if (!args[0]) {
                    return await message.reply('❌ Usage: `w.gend <giveaway_id>`');
                }

                const giveawayId = parseInt(args[0]);
                if (isNaN(giveawayId)) {
                    return await message.reply('❌ Please provide a valid giveaway ID!');
                }

                try {
                    await bot.giveawaySystem.endGiveaway(giveawayId);
                    await message.reply('✅ Giveaway ended successfully!');
                } catch (error) {
                    console.error('Error ending giveaway:', error);
                    await message.reply('❌ Failed to end giveaway!');
                }
            }
        });

        this.addCommand('greroll', {
            description: 'Reroll giveaway winners (Admin only)',
            execute: async (message, args, bot) => {
                if (!message.member.permissions.has('MANAGE_GUILD')) {
                    return await message.reply('❌ You need **Manage Server** permissions to reroll giveaways!');
                }

                if (!args[0]) {
                    return await message.reply('❌ Usage: `w.greroll <giveaway_id>`');
                }

                const giveawayId = parseInt(args[0]);
                if (isNaN(giveawayId)) {
                    return await message.reply('❌ Please provide a valid giveaway ID!');
                }

                try {
                    const result = await bot.giveawaySystem.rerollGiveaway(giveawayId);
                    if (result.success) {
                        const winnerMentions = result.winners.map(w => `<@${w.user_id}>`).join(', ');
                        await message.reply(`🎉 New winners: ${winnerMentions}!`);
                    } else {
                        await message.reply(`❌ ${result.message}`);
                    }
                } catch (error) {
                    console.error('Error rerolling giveaway:', error);
                    await message.reply('❌ Failed to reroll giveaway!');
                }
            }
        });

        this.addCommand('glist', {
            description: 'List active giveaways',
            execute: async (message, args, bot) => {
                try {
                    const giveaways = await bot.giveawaySystem.getServerGiveaways(message.guild.id, false, 5);
                    
                    if (giveaways.length === 0) {
                        return await message.reply('📭 No active giveaways in this server!');
                    }

                    const embed = new EmbedBuilder()
                        .setColor(config.colors.primary)
                        .setTitle('🎉 Active Giveaways')
                        .setDescription('Here are the current active giveaways:')
                        .setTimestamp();

                    for (const giveaway of giveaways) {
                        const endTime = new Date(giveaway.created_at);
                        endTime.setMinutes(endTime.getMinutes() + giveaway.duration);
                        
                        embed.addFields({
                            name: `ID: ${giveaway.id} - ${giveaway.title}`,
                            value: `**Prize:** ${giveaway.prize}\n**Winners:** ${giveaway.winner_count}\n**Ends:** <t:${Math.floor(endTime.getTime() / 1000)}:R>`,
                            inline: true
                        });
                    }

                    await message.reply({ embeds: [embed] });
                } catch (error) {
                    console.error('Error listing giveaways:', error);
                    await message.reply('❌ Failed to list giveaways!');
                }
            }
        });

        this.addCommand('gwins', {
            description: 'View your giveaway wins',
            execute: async (message, args, bot) => {
                try {
                    const wins = await bot.giveawaySystem.getUserGiveawayHistory(message.author.id, 10);
                    
                    if (wins.length === 0) {
                        return await message.reply('🎭 You haven\'t won any giveaways yet!');
                    }

                    const embed = new EmbedBuilder()
                        .setColor(config.colors.success)
                        .setTitle('🏆 Your Giveaway Wins')
                        .setDescription(`You've won ${wins.length} giveaway${wins.length > 1 ? 's' : ''}!`)
                        .setTimestamp();

                    for (const win of wins.slice(0, 5)) {
                        const wonDate = new Date(win.won_at);
                        embed.addFields({
                            name: `${win.title}`,
                            value: `**Prize:** ${win.prize}\n**Won:** <t:${Math.floor(wonDate.getTime() / 1000)}:R>`,
                            inline: true
                        });
                    }

                    if (wins.length > 5) {
                        embed.setFooter({ text: `Showing 5 of ${wins.length} total wins` });
                    }

                    await message.reply({ embeds: [embed] });
                } catch (error) {
                    console.error('Error getting user wins:', error);
                    await message.reply('❌ Failed to get your giveaway history!');
                }
            }
        });

        // Role and perks commands
        this.addCommand('perks', {
            description: 'View your role perks and bonuses',
            execute: async (message, args, bot) => {
                const member = message.guild.members.cache.get(message.author.id);
                const embed = bot.roleManager.createPerksEmbed(member);
                await message.reply({ embeds: [embed] });
            }
        });

        // Utility commands
        this.addCommand('help', {
            description: 'Show all available commands',
            execute: async (message, args, bot) => {
                const embed = new EmbedBuilder()
                    .setColor(config.colors.primary)
                    .setTitle('🤖 Wonder Bot Commands')
                    .setDescription('Here are all the available commands:')
                    .addFields(
                        {
                            name: '💰 Economy Commands',
                            value: '`w.balance` - Check WonderCash balance\n`w.daily` - Claim daily reward\n`w.work` - Work for WonderCash\n`w.leaderboard` - View top earners',
                            inline: false
                        },
                        {
                            name: '🎮 Game Commands',
                            value: '`w.coinflip <heads/tails> <amount>` - Coin flip game\n`w.dice <amount>` - Dice rolling game\n`w.slots <amount>` - Slot machine',
                            inline: false
                        },
                        {
                            name: '🏪 Shop Commands',
                            value: '`w.shop` - Browse the Wonder Shop\n`w.inventory` - View your items\n`w.use <item>` - Use consumable items',
                            inline: false
                        },
                        {
                            name: '🎉 Giveaway Commands',
                            value: '`w.gstart <time> <winners> <prize>` - Start giveaway (Admin)\n`w.gend <id>` - End giveaway (Admin)\n`w.greroll <id>` - Reroll winners (Admin)\n`w.glist` - List active giveaways\n`w.gwins` - View your wins',
                            inline: false
                        },
                        {
                            name: '💎 Role Commands',
                            value: '`w.perks` - View your role perks and bonuses',
                            inline: false
                        },
                        {
                            name: '📝 Other Features',
                            value: '• Introduction cards with `/intro` slash command\n• Welcome messages for new members\n• Exclusive perks for boosters and premium members\n• Advanced shop system with consumables and collectibles\n• Cooldown system prevents spamming\n• **NEW:** Giveaway system with role-based odds and restrictions',
                            inline: false
                        }
                    )
                    .setFooter({ text: 'Wonder Bot - Making Discord communities amazing!' })
                    .setTimestamp();

                await message.reply({ embeds: [embed] });
            }
        });
    }

    loadSlashCommands() {
        // Slash commands are loaded dynamically in the handler
        console.log('✅ Slash commands loaded successfully');
    }

    addCommand(name, command) {
        this.commands.set(name, command);
    }

    // Handle voice state updates for leveling
    async handleVoiceStateUpdate(oldState, newState) {
        if (!config.leveling?.enabled) return;
        
        const userId = newState.member.id;
        
        try {
            // User joined a voice channel
            if (!oldState.channel && newState.channel) {
                await database.createUser(userId, newState.member.user.username);
                await this.levelingSystem.startVoiceSession(userId, newState.channel.id);
            }
            
            // User left a voice channel
            if (oldState.channel && !newState.channel) {
                await this.levelingSystem.endVoiceSession(userId);
            }
            
            // User moved between voice channels
            if (oldState.channel && newState.channel && oldState.channel.id !== newState.channel.id) {
                await this.levelingSystem.endVoiceSession(userId);
                await this.levelingSystem.startVoiceSession(userId, newState.channel.id);
            }
        } catch (error) {
            console.error('Error handling voice state update:', error);
        }
    }

    // Parse duration string (e.g., "1h", "30m", "2d") to minutes
    parseDuration(durationStr) {
        const match = durationStr.match(/^(\d+)([smhd])$/i);
        if (!match) return null;

        const value = parseInt(match[1]);
        const unit = match[2].toLowerCase();

        switch (unit) {
            case 's': return Math.max(1, Math.floor(value / 60)); // seconds to minutes, minimum 1
            case 'm': return value; // minutes
            case 'h': return value * 60; // hours to minutes
            case 'd': return value * 60 * 24; // days to minutes
            default: return null;
        }
    }

    async start() {
        try {
            await this.client.login(process.env.DISCORD_TOKEN);
        } catch (error) {
            console.error('Error starting bot:', error);
        }
    }
}

// Create and start the bot
const bot = new WonderBot();
bot.start();