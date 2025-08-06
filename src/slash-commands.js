const { SlashCommandBuilder, REST, Routes } = require('discord.js');
require('dotenv').config();

const commands = [
    new SlashCommandBuilder()
        .setName('balance')
        .setDescription('Check your WonderCash balance')
        .addUserOption(option =>
            option.setName('user')
                .setDescription('User to check balance for')
                .setRequired(false)),

    new SlashCommandBuilder()
        .setName('daily')
        .setDescription('Claim your daily WonderCash reward'),

    new SlashCommandBuilder()
        .setName('work')
        .setDescription('Work to earn WonderCash'),

    new SlashCommandBuilder()
        .setName('leaderboard')
        .setDescription('View the WonderCash leaderboard'),

    new SlashCommandBuilder()
        .setName('coinflip')
        .setDescription('Bet WonderCash on a coin flip')
        .addStringOption(option =>
            option.setName('choice')
                .setDescription('Heads or Tails')
                .setRequired(true)
                .addChoices(
                    { name: 'Heads', value: 'heads' },
                    { name: 'Tails', value: 'tails' }
                ))
        .addIntegerOption(option =>
            option.setName('amount')
                .setDescription('Amount to bet (10-1000)')
                .setRequired(true)
                .setMinValue(10)
                .setMaxValue(1000)),

    new SlashCommandBuilder()
        .setName('dice')
        .setDescription('Roll dice and bet on the outcome')
        .addIntegerOption(option =>
            option.setName('amount')
                .setDescription('Amount to bet (10-500)')
                .setRequired(true)
                .setMinValue(10)
                .setMaxValue(500)),

    new SlashCommandBuilder()
        .setName('slots')
        .setDescription('Play the slot machine')
        .addIntegerOption(option =>
            option.setName('amount')
                .setDescription('Amount to bet (20-200)')
                .setRequired(true)
                .setMinValue(20)
                .setMaxValue(200)),

    new SlashCommandBuilder()
        .setName('intro')
        .setDescription('Create or view introduction cards')
        .addSubcommand(subcommand =>
            subcommand
                .setName('create')
                .setDescription('Create your introduction card'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('view')
                .setDescription('View someone\'s introduction card')
                .addUserOption(option =>
                    option.setName('user')
                        .setDescription('User to view introduction card for')
                        .setRequired(false))),

    new SlashCommandBuilder()
        .setName('setup')
        .setDescription('Setup server settings (Admin only)')
        .addSubcommand(subcommand =>
            subcommand
                .setName('welcome')
                .setDescription('Setup welcome channel and message')
                .addChannelOption(option =>
                    option.setName('channel')
                        .setDescription('Welcome channel')
                        .setRequired(true))
                .addStringOption(option =>
                    option.setName('message')
                        .setDescription('Welcome message')
                        .setRequired(false)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('introduction')
                .setDescription('Setup introduction channel')
                .addChannelOption(option =>
                    option.setName('channel')
                        .setDescription('Introduction channel')
                        .setRequired(true))),

    new SlashCommandBuilder()
        .setName('help')
        .setDescription('Show bot commands and information'),

    new SlashCommandBuilder()
        .setName('giveaway')
        .setDescription('Giveaway management commands')
        .addSubcommand(subcommand =>
            subcommand
                .setName('start')
                .setDescription('Start a new giveaway (Admin only)')
                .addStringOption(option =>
                    option.setName('duration')
                        .setDescription('Giveaway duration (e.g., 1h, 30m, 2d)')
                        .setRequired(true))
                .addIntegerOption(option =>
                    option.setName('winners')
                        .setDescription('Number of winners')
                        .setRequired(true)
                        .setMinValue(1)
                        .setMaxValue(10))
                .addStringOption(option =>
                    option.setName('prize')
                        .setDescription('Prize description')
                        .setRequired(true))
                .addStringOption(option =>
                    option.setName('title')
                        .setDescription('Giveaway title')
                        .setRequired(false))
                .addChannelOption(option =>
                    option.setName('channel')
                        .setDescription('Channel to post giveaway in')
                        .setRequired(false))
                .addBooleanOption(option =>
                    option.setName('restrict_winners')
                        .setDescription('Restrict previous winners from entering')
                        .setRequired(false)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('end')
                .setDescription('End a giveaway early (Admin only)')
                .addIntegerOption(option =>
                    option.setName('giveaway_id')
                        .setDescription('ID of the giveaway to end')
                        .setRequired(true)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('reroll')
                .setDescription('Reroll giveaway winners (Admin only)')
                .addIntegerOption(option =>
                    option.setName('giveaway_id')
                        .setDescription('ID of the giveaway to reroll')
                        .setRequired(true)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('list')
                .setDescription('List active giveaways'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('stats')
                .setDescription('View giveaway statistics')
                .addIntegerOption(option =>
                    option.setName('giveaway_id')
                        .setDescription('ID of the giveaway to view stats for')
                        .setRequired(true)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('wins')
                .setDescription('View your giveaway wins')
                .addUserOption(option =>
                    option.setName('user')
                        .setDescription('User to check wins for')
                        .setRequired(false))),

    // Leveling Commands
    new SlashCommandBuilder()
        .setName('level')
        .setDescription('Check your or someone else\'s level information')
        .addUserOption(option =>
            option.setName('user')
                .setDescription('User to check levels for')
                .setRequired(false)),

    new SlashCommandBuilder()
        .setName('rank')
        .setDescription('View leveling leaderboards')
        .addStringOption(option =>
            option.setName('type')
                .setDescription('Type of leaderboard to view')
                .setRequired(false)
                .addChoices(
                    { name: 'Overall', value: 'overall' },
                    { name: 'Text', value: 'text' },
                    { name: 'Voice', value: 'voice' },
                    { name: 'Role', value: 'role' }
                )),

    new SlashCommandBuilder()
        .setName('rewards')
        .setDescription('View and claim your unclaimed level rewards'),

    new SlashCommandBuilder()
        .setName('give-xp')
        .setDescription('Give XP to a user (Admin only)')
        .addUserOption(option =>
            option.setName('user')
                .setDescription('User to give XP to')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('type')
                .setDescription('Type of XP to give')
                .setRequired(true)
                .addChoices(
                    { name: 'Text', value: 'text' },
                    { name: 'Voice', value: 'voice' },
                    { name: 'Role', value: 'role' }
                ))
        .addIntegerOption(option =>
            option.setName('amount')
                .setDescription('Amount of XP to give')
                .setRequired(true)
                .setMinValue(1)
                .setMaxValue(10000)),

    new SlashCommandBuilder()
        .setName('reset-level')
        .setDescription('Reset a user\'s levels (Admin only)')
        .addUserOption(option =>
            option.setName('user')
                .setDescription('User to reset levels for')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('type')
                .setDescription('Type of level to reset')
                .setRequired(false)
                .addChoices(
                    { name: 'All', value: 'all' },
                    { name: 'Text', value: 'text' },
                    { name: 'Voice', value: 'voice' },
                    { name: 'Role', value: 'role' }
                )),

    new SlashCommandBuilder()
        .setName('level-role')
        .setDescription('Manage level role rewards (Admin only)')
        .addSubcommand(subcommand =>
            subcommand
                .setName('set')
                .setDescription('Set a role reward for a specific level')
                .addStringOption(option =>
                    option.setName('level_type')
                        .setDescription('Type of level')
                        .setRequired(true)
                        .addChoices(
                            { name: 'Text', value: 'text' },
                            { name: 'Voice', value: 'voice' },
                            { name: 'Role', value: 'role' },
                            { name: 'Overall', value: 'overall' }
                        ))
                .addIntegerOption(option =>
                    option.setName('level')
                        .setDescription('Level number (1-50)')
                        .setRequired(true)
                        .setMinValue(1)
                        .setMaxValue(50))
                .addRoleOption(option =>
                    option.setName('role')
                        .setDescription('Role to give as reward')
                        .setRequired(true)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('remove')
                .setDescription('Remove a role reward for a specific level')
                .addStringOption(option =>
                    option.setName('level_type')
                        .setDescription('Type of level')
                        .setRequired(true)
                        .addChoices(
                            { name: 'Text', value: 'text' },
                            { name: 'Voice', value: 'voice' },
                            { name: 'Role', value: 'role' },
                            { name: 'Overall', value: 'overall' }
                        ))
                .addIntegerOption(option =>
                    option.setName('level')
                        .setDescription('Level number (1-50)')
                        .setRequired(true)
                        .setMinValue(1)
                        .setMaxValue(50)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('list')
                .setDescription('List all configured role rewards')
                .addStringOption(option =>
                    option.setName('level_type')
                        .setDescription('Filter by level type (optional)')
                        .setRequired(false)
                        .addChoices(
                            { name: 'Text', value: 'text' },
                            { name: 'Voice', value: 'voice' },
                            { name: 'Role', value: 'role' },
                            { name: 'Overall', value: 'overall' }
 cursor/tambahkan-fitur-leveling-roles-dan-level-d928
                        ))),

    new SlashCommandBuilder()
        .setName('drops')
        .setDescription('WonderCoins drop system management and stats')
        .addSubcommand(subcommand =>
            subcommand
                .setName('setup')
                .setDescription('Setup drop channels (Admin only)')
                .addChannelOption(option =>
                    option.setName('channel')
                        .setDescription('Channel for WonderCoins drops')
                        .setRequired(true)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('remove')
                .setDescription('Remove drop channel (Admin only)')
                .addChannelOption(option =>
                    option.setName('channel')
                        .setDescription('Channel to remove from drops')
                        .setRequired(true)))
        .addSubcommand(subcommand =>
            subcommand
                .setName('list')
                .setDescription('List configured drop channels'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('stats')
                .setDescription('View drop statistics'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('mystats')
                .setDescription('View your personal drop statistics'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('trigger')
                .setDescription('Manually trigger a drop (Admin only)')
                .addChannelOption(option =>
                    option.setName('channel')
                        .setDescription('Channel to drop coins in')
                        .setRequired(true))
                .addIntegerOption(option =>
                    option.setName('amount')
                        .setDescription('Amount of coins (optional)')
                        .setRequired(false)
                        .setMinValue(10)
                        .setMaxValue(5000))
                .addStringOption(option =>
                    option.setName('rarity')
                        .setDescription('Drop rarity (optional)')
                        .setRequired(false)
                        .addChoices(
                            { name: 'Common', value: 'common' },
                            { name: 'Rare', value: 'rare' },
                            { name: 'Epic', value: 'epic' },
                            { name: 'Legendary', value: 'legendary' }

 main
                        )))
];

async function deployCommands() {
    const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

    try {
        console.log('Started refreshing application (/) commands.');

        if (process.env.GUILD_ID) {
            // Guild-specific commands for development
            await rest.put(
                Routes.applicationGuildCommands(process.env.CLIENT_ID, process.env.GUILD_ID),
                { body: commands }
            );
            console.log('Successfully reloaded guild application (/) commands.');
        } else {
            // Global commands for production
            await rest.put(
                Routes.applicationCommands(process.env.CLIENT_ID),
                { body: commands }
            );
            console.log('Successfully reloaded global application (/) commands.');
        }
    } catch (error) {
        console.error('Error deploying commands:', error);
    }
}

module.exports = { commands, deployCommands };