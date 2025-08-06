# 🏰 Wonder Discord Bot - Luxury Kingdom Edition

A comprehensive Discord bot featuring advanced economy system, interactive games, WonderCoins drop system, introduction cards, role management, and exclusive perks. Built with luxury kingdom aesthetics and premium user experience.

## 📋 Table of Contents
- [Features Overview](#-features-overview)
- [Installation & Setup](#-installation--setup)
- [Commands Reference](#-commands-reference)
- [System Configuration](#-system-configuration)
- [Database Schema](#-database-schema)
- [Development Guide](#-development-guide)
- [Troubleshooting](#-troubleshooting)

## ✨ Features Overview

### 💰 Advanced Economy System
**Core Features:**
- **WonderCoins Currency**: Virtual currency system with transaction tracking
- **Daily Rewards**: 100 WonderCoins every 24 hours (boosters +50, premium +100)
- **Work System**: 50 WonderCoins every hour (boosters +25, premium +50)
- **Balance Management**: Check, transfer, and track all transactions
- **Anti-Spam Protection**: Cooldown system prevents abuse
- **Leaderboard System**: Server-wide wealth competition

**Role-Based Bonuses:**
- **Server Boosters**: +50 daily, +25 work bonus
- **Premium Members**: +100 daily, +50 work bonus
- **Multiplier Stacking**: Bonuses stack with other systems

### 🪙 WonderCoins Drop System
**Automated Drop Features:**
- **Random Timing**: Drops occur every 30 minutes to 3 hours globally
- **Multi-Server Support**: Single system serves all configured servers
- **Channel-Based**: Admin-configured channels receive drops

**Rarity & Rewards System:**
| Rarity | Multiplier | Chance | Example Amount |
|--------|------------|--------|----------------|
| Common | 1x | ~84% | 150 coins |
| Rare | 3x | 10% | 450 coins |
| Epic | 5x | 5% | 750 coins |
| Legendary | 10x | 1% | 1,500 coins |

**Interactive Collection Mechanics:**
- **💰 Standard Collection**: Click to collect normal amount
- **⚡ Quick Grab**: First 3 collectors get 2x coins (competition element)
- **🍀 Lucky Grab**: 30% chance for 1.5x bonus coins (gambling element)

**Role Multipliers:**
- **Premium Members**: +50% on all collections
- **Server Boosters**: +25% on all collections
- **Stacking**: Works with collection type bonuses

**Time Management:**
- **Collection Window**: 60 seconds to collect
- **Auto-Expiry**: Shows collection summary when expired
- **One Per User**: Prevents duplicate collections

### 🎮 Interactive Games
**Available Games:**
- **Coin Flip**: Bet 10-1,000 WonderCoins on heads/tails (2min cooldown)
- **Dice Rolling**: Bet 10-500 WonderCoins, various multipliers (3min cooldown)
- **Slot Machine**: Bet 20-200 WonderCoins, emoji-based slots (5min cooldown)

**Game Features:**
- **Lucky Charm Effects**: Use consumable items to boost win rates
- **Premium Perks**: Reduced cooldowns for boosters and premium
- **Fair RNG**: Cryptographically secure random number generation
- **Betting Limits**: Configurable min/max bets per game

### 📝 Introduction Cards System
**Card Creation:**
- **Interactive Forms**: Modal-based form interface
- **Custom Fields**: Name, age, location, hobbies, favorite color, bio
- **Image Generation**: Automatically generated cards using Canvas
- **Profile Integration**: Links to user profiles and avatars

**Visual Features:**
- **Dynamic Backgrounds**: Color-based backgrounds from favorite color
- **Typography**: Custom fonts and text styling
- **Avatar Integration**: User Discord avatar overlay
- **Responsive Design**: Adapts to different text lengths

### 🎭 Role Management & Perks
**Automatic Role Benefits:**
- **Server Booster Detection**: Automatic perk activation
- **Premium Role Integration**: VIP benefits system
- **Exclusive Access**: Special channels and features
- **Status Display**: Visual indicators in all commands

**Perk System:**
- **Economy Bonuses**: Enhanced daily/work rewards
- **Game Benefits**: Reduced cooldowns and better odds
- **Drop Advantages**: Multiplied collection amounts
- **Shop Discounts**: Reduced prices on items

### 🏪 Advanced Shop System
**Item Categories:**
- **Consumables**: Temporary effect items (boosters, potions)
- **Collectibles**: Rare trophies and valuable items
- **Profile Items**: Custom titles, colors, borders
- **Special Items**: Unique and event-exclusive items

**Shopping Experience:**
- **Interactive Interface**: Category menus and item browsers
- **Detailed Previews**: Item effects and descriptions
- **Purchase Confirmation**: Clear transaction details
- **Inventory Management**: Track owned items and quantities

### 🎉 Advanced Giveaway System
**Entry Management:**
- **Weighted Odds**: Regular (1x), Boosters (2x), Premium (3x)
- **Winner Restrictions**: 7-day cooldown between wins
- **Account Age**: Minimum requirements for participation
- **Role Requirements**: Configurable role-based entry

**Giveaway Features:**
- **Flexible Duration**: Minutes to weeks support
- **Multiple Winners**: Up to 10 winners per giveaway
- **Auto-Management**: Automatic winner selection and notification
- **Statistics Tracking**: Detailed analytics per giveaway

### 🎯 Leveling System
**XP Categories:**
- **Text XP**: 15-25 XP per message (1min cooldown)
- **Voice XP**: 10-15 XP per minute (unmuted required)
- **Role XP**: Activity-based bonuses (daily login, streaks)
- **Overall Level**: Combined progress from all categories

**Progression Features:**
- **Max Level**: 50 in all categories
- **Role Rewards**: Automatic role assignment at milestones
- **Currency Rewards**: WonderCoins bonuses at level-ups
- **Title System**: Custom titles for achievements

### 🔧 Welcome & Setup System
**Welcome Features:**
- **Custom Messages**: Personalized welcome text
- **Introduction Buttons**: Quick access to card creation
- **Channel Integration**: Automatic posting to designated channels
- **Member Onboarding**: Streamlined new user experience

**Admin Configuration:**
- **Channel Setup**: Configure welcome and introduction channels
- **Message Customization**: Custom welcome message templates
- **Auto-Role Assignment**: Optional role assignment on join
- **Logging**: Join/leave event tracking

## 🚀 Installation & Setup

### Prerequisites
```bash
# Required Software
Node.js >= 18.0.0
npm >= 8.0.0
Git

# System Dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev libpixman-1-dev
```

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/wonder-discord-bot.git
cd wonder-discord-bot
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```env
# Discord Bot Configuration
DISCORD_TOKEN=your_bot_token_here
CLIENT_ID=your_bot_client_id
GUILD_ID=your_test_server_id (optional, for development)

# Role IDs (get from Discord Developer Mode)
BOOSTER_ROLE_ID=server_booster_role_id
PREMIUM_ROLE_ID=premium_member_role_id

# Database Configuration (optional)
DATABASE_PATH=./wonder.db

# Development Settings
NODE_ENV=production
DEBUG=false
```

### Step 4: Deploy Commands
```bash
# Deploy slash commands to Discord
npm run deploy-commands
```

### Step 5: Start Bot
```bash
# Production mode
npm start

# Development mode (with auto-restart)
npm run dev
```

### Step 6: Initial Server Setup
```bash
# In Discord, use these commands to configure your server:
/setup welcome #welcome-channel "Welcome to our server!"
/setup introduction #introductions

# Setup WonderCoins drops
/drops setup #general
/drops setup #bot-commands
```

## 📚 Commands Reference

### 💰 Economy Commands
| Command | Description | Usage Example | Cooldown |
|---------|-------------|---------------|----------|
| `/balance` | Check WonderCoins balance | `/balance @user` | None |
| `/daily` | Claim daily reward | `/daily` | 24 hours |
| `/work` | Work for WonderCoins | `/work` | 1 hour |
| `/leaderboard` | View wealth rankings | `/leaderboard` | None |
| `/pay` | Transfer coins to user | `/pay @user 100` | None |
| `/transactions` | View transaction history | `/transactions` | None |

### 🪙 WonderCoins Drop Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `/drops setup` | Add drop channel | `/drops setup channel:#general` | Admin |
| `/drops remove` | Remove drop channel | `/drops remove channel:#general` | Admin |
| `/drops list` | List active channels | `/drops list` | Everyone |
| `/drops stats` | Server statistics | `/drops stats` | Everyone |
| `/drops mystats` | Personal statistics | `/drops mystats` | Everyone |
| `/drops trigger` | Manual drop | `/drops trigger channel:#general amount:100 rarity:epic` | Admin |

### 🎮 Game Commands
| Command | Description | Usage Example | Cooldown |
|---------|-------------|---------------|----------|
| `/coinflip` | Bet on coin flip | `/coinflip choice:heads amount:100` | 2 minutes |
| `/dice` | Roll dice game | `/dice amount:50` | 3 minutes |
| `/slots` | Slot machine | `/slots amount:25` | 5 minutes |

### 🎉 Giveaway Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `/giveaway start` | Create giveaway | `/giveaway start duration:1h winners:1 prize:100 WonderCoins` | Admin |
| `/giveaway end` | End early | `/giveaway end giveaway_id:1` | Admin |
| `/giveaway reroll` | Reroll winners | `/giveaway reroll giveaway_id:1` | Admin |
| `/giveaway list` | List active | `/giveaway list` | Everyone |
| `/giveaway wins` | Your wins | `/giveaway wins` | Everyone |
| `/giveaway stats` | Statistics | `/giveaway stats giveaway_id:1` | Everyone |

### 🎯 Leveling Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `/level` | Check levels | `/level @user` | Everyone |
| `/rank` | Level ranking | `/rank type:overall` | Everyone |
| `/rewards` | Level rewards | `/rewards` | Everyone |
| `/give-xp` | Give XP | `/give-xp @user type:text amount:100` | Admin |
| `/reset-level` | Reset levels | `/reset-level @user type:text` | Admin |
| `/level-role` | Configure role rewards | `/level-role add type:text level:10 role:@Member` | Admin |

### 📝 Introduction Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `/intro create` | Create card | `/intro create` | Everyone |
| `/intro view` | View cards | `/intro view @user` | Everyone |

### 🏪 Shop Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `/shop` | Browse shop | `/shop` | Everyone |
| `/inventory` | View items | `/inventory` | Everyone |
| `/use` | Use item | `/use item:lucky_charm` | Everyone |

### ⚙️ Admin Commands
| Command | Description | Usage Example | Required Permission |
|---------|-------------|---------------|-------------------|
| `/setup welcome` | Welcome config | `/setup welcome channel:#welcome message:Welcome!` | Administrator |
| `/setup introduction` | Intro config | `/setup introduction channel:#intros` | Administrator |
| `/give` | Give currency | `/give @user 1000` | Administrator |
| `/take` | Take currency | `/take @user 500` | Administrator |
| `/reset` | Reset user data | `/reset @user` | Administrator |

## ⚙️ System Configuration

### Bot Configuration (config.json)
```json
{
  "prefix": "w.",
  "currency": {
    "name": "WonderCoins",
    "symbol": "💰",
    "dailyAmount": 100,
    "workAmount": 50
  },
  "branding": {
    "name": "Luxury Kingdom Bot",
    "tagline": "Royal Elegance Awaits",
    "version": "2.0.0",
    "theme": "Luxury Kingdom Aesthetic"
  },
  "booster": {
    "dailyBonus": 50,
    "workBonus": 25,
    "exclusiveChannels": true
  },
  "premium": {
    "dailyBonus": 100,
    "workBonus": 50,
    "exclusiveChannels": true,
    "customColor": true
  },
  "games": {
    "coinflip": { "minBet": 10, "maxBet": 1000 },
    "dice": { "minBet": 10, "maxBet": 500 },
    "slots": { "minBet": 20, "maxBet": 200 }
  },
  "cooldowns": {
    "daily": 1440,
    "work": 60,
    "coinflip": 2,
    "dice": 3,
    "slots": 5,
    "mystery_box": 30,
    "use_item": 1
  }
}
```

### WonderCoins Drop Configuration
```javascript
// Default configuration in wondercoins-drop-system.js
config: {
  minAmount: 10,           // Minimum drop amount
  maxAmount: 500,          // Maximum drop amount
  minInterval: 1800000,    // 30 minutes in milliseconds
  maxInterval: 10800000,   // 3 hours in milliseconds
  collectTime: 60000,      // 60 seconds to collect
  
  // Rarity probabilities and multipliers
  rareDrop: { chance: 0.1, multiplier: 3 },      // 10%
  epicDrop: { chance: 0.05, multiplier: 5 },     // 5%
  legendaryDrop: { chance: 0.01, multiplier: 10 } // 1%
}
```

### Color Scheme
```json
"colors": {
  "primary": "#FFD700",    // Gold
  "secondary": "#DAA520",  // Dark gold
  "accent": "#8B4513",     // Saddle brown
  "success": "#228B22",    // Forest green
  "error": "#DC143C",      // Crimson
  "warning": "#FF8C00",    // Dark orange
  "info": "#4169E1",       // Royal blue
  "royal": "#800080",      // Purple
  "luxury": "#FF69B4",     // Hot pink
  "kingdom": "#FFD700",    // Gold
  "background": "#2F1B69", // Dark purple
  "text": "#F5F5DC"        // Beige
}
```

## 🗄️ Database Schema

### Core Tables
```sql
-- User economy and profile data
CREATE TABLE users (
  user_id TEXT PRIMARY KEY,
  username TEXT,
  balance INTEGER DEFAULT 0,
  daily_last_claimed TEXT,
  work_last_used TEXT,
  total_earned INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Transaction history
CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  type TEXT,                    -- 'daily', 'work', 'game_win', 'drop', etc.
  amount INTEGER,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Introduction cards
CREATE TABLE introduction_cards (
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
);

-- Server configuration
CREATE TABLE server_settings (
  guild_id TEXT PRIMARY KEY,
  welcome_channel TEXT,
  introduction_channel TEXT,
  welcome_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### WonderCoins Drop System Tables
```sql
-- Drop channel configuration
CREATE TABLE drop_channels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id TEXT,
  channel_id TEXT,
  created_by TEXT,              -- Admin who added the channel
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(guild_id, channel_id)
);

-- Detailed drop statistics
CREATE TABLE drop_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id TEXT,
  user_id TEXT,
  amount INTEGER,               -- Amount collected
  rarity TEXT,                  -- 'common', 'rare', 'epic', 'legendary'
  collection_type TEXT,         -- 'collect', 'quick', 'lucky'
  drop_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User drop statistics summary
CREATE TABLE user_drop_stats (
  user_id TEXT PRIMARY KEY,
  total_collected INTEGER DEFAULT 0,
  total_drops INTEGER DEFAULT 0,
  common_drops INTEGER DEFAULT 0,
  rare_drops INTEGER DEFAULT 0,
  epic_drops INTEGER DEFAULT 0,
  legendary_drops INTEGER DEFAULT 0,
  last_drop DATETIME,
  best_drop INTEGER DEFAULT 0
);
```

### Shop & Inventory Tables
```sql
-- User inventory
CREATE TABLE user_inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  item_id TEXT,
  quantity INTEGER DEFAULT 1,
  acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Active consumable effects
CREATE TABLE active_effects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  effect_type TEXT,             -- 'lucky_charm', 'xp_boost', etc.
  duration_minutes INTEGER,
  uses_remaining INTEGER DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME
);
```

### Leveling System Tables
```sql
-- User leveling data
CREATE TABLE user_levels (
  user_id TEXT PRIMARY KEY,
  text_level INTEGER DEFAULT 1,
  text_xp INTEGER DEFAULT 0,
  voice_level INTEGER DEFAULT 1,
  voice_xp INTEGER DEFAULT 0,
  role_level INTEGER DEFAULT 1,
  role_xp INTEGER DEFAULT 0,
  overall_level INTEGER DEFAULT 1,
  total_xp INTEGER DEFAULT 0,
  last_text_xp DATETIME,
  voice_session_start DATETIME,
  last_daily_login DATETIME,
  message_streak INTEGER DEFAULT 0,
  voice_streak INTEGER DEFAULT 0
);

-- Level role rewards configuration
CREATE TABLE level_role_config (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  level_type TEXT,              -- 'text', 'voice', 'role', 'overall'
  level INTEGER,
  role_id TEXT,
  role_name TEXT,
  created_by TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(level_type, level)
);
```

### Giveaway System Tables
```sql
-- Giveaway data
CREATE TABLE giveaways (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  guild_id TEXT,
  channel_id TEXT,
  message_id TEXT,
  host_id TEXT,
  prize TEXT,
  winner_count INTEGER,
  end_time DATETIME,
  ended BOOLEAN DEFAULT FALSE,
  requirements TEXT,            -- JSON string
  winners TEXT,                 -- JSON array
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Giveaway entries
CREATE TABLE giveaway_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  giveaway_id INTEGER,
  user_id TEXT,
  weight REAL,                  -- Entry weight based on roles
  entered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (giveaway_id) REFERENCES giveaways(id)
);
```

## 📁 Project Structure

```
wonder-discord-bot/
├── src/
│   ├── index.js                      # Main bot entry point
│   ├── database.js                   # SQLite database management
│   ├── slash-commands.js             # Slash command definitions
│   ├── slash-handlers.js             # Command handler implementations
│   ├── role-manager.js               # Role and perks management
│   ├── shop-system.js                # Shop and inventory system
│   ├── cooldown-manager.js           # Cooldown and effects management
│   ├── giveaway-system.js            # Giveaway management
│   ├── leveling-system.js            # XP and leveling system
│   ├── wondercoins-drop-system.js    # WonderCoins drop system
│   └── utils/
│       ├── canvas.js                 # Image generation utilities
│       └── luxury-design.js          # UI design components
├── config.json                       # Bot configuration settings
├── package.json                      # Node.js dependencies
├── deploy-commands.js                # Command deployment script
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── README.md                         # This documentation
├── LEVELING_SYSTEM.md               # Detailed leveling guide
└── Y2K_KINGDOM_DESIGN.md            # Design system documentation
```

## 🛠️ Development Guide

### Adding New Commands
1. **Define Command Structure** (src/slash-commands.js):
```javascript
new SlashCommandBuilder()
    .setName('newcommand')
    .setDescription('Command description')
    .addStringOption(option =>
        option.setName('parameter')
            .setDescription('Parameter description')
            .setRequired(true))
```

2. **Implement Handler** (src/slash-handlers.js):
```javascript
async handleNewCommand(interaction) {
    const parameter = interaction.options.getString('parameter');
    // Implementation logic
    await interaction.reply({ content: 'Response' });
}
```

3. **Register Handler** (src/index.js):
```javascript
case 'newcommand':
    await this.slashHandlers.handleNewCommand(interaction);
    break;
```

### Database Operations
```javascript
// Create new database method
async createNewTable() {
    this.db.run(`
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
}

// Add to database.js init() method
```

### Error Handling
```javascript
try {
    // Database operations
    await database.someOperation();
    await interaction.reply({ content: '✅ Success' });
} catch (error) {
    console.error('Error in command:', error);
    await interaction.reply({ 
        content: '❌ An error occurred. Please try again.', 
        ephemeral: true 
    });
}
```

### Testing
```bash
# Run tests
npm test

# Check for syntax errors
npm run lint

# Development with hot reload
npm run dev
```

## 🔧 Troubleshooting

### Common Issues

**1. Canvas Installation Errors**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev libpixman-1-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install cairo-devel pango-devel libjpeg-turbo-devel giflib-devel
```

**2. Database Permission Errors**
```bash
# Fix database permissions
chmod 755 wonder.db
chown $USER:$USER wonder.db
```

**3. Command Deployment Issues**
```bash
# Clear and redeploy commands
rm -f deploy-commands.log
npm run deploy-commands

# Check bot permissions in Discord
# Ensure bot has "applications.commands" scope
```

**4. Role Detection Problems**
```bash
# Enable Developer Mode in Discord
# Right-click roles → Copy ID
# Update .env with correct role IDs
```

### Debug Mode
```env
# Add to .env file
DEBUG=true
NODE_ENV=development

# Enables verbose logging
# Shows detailed error messages
# Logs all database operations
```

### Log Analysis
```bash
# View recent logs
tail -f bot.log

# Search for errors
grep -i error bot.log

# Monitor database operations
grep -i "database" bot.log
```

### Performance Monitoring
```javascript
// Add to index.js for monitoring
setInterval(() => {
    const memUsage = process.memoryUsage();
    console.log(`Memory usage: ${Math.round(memUsage.heapUsed / 1024 / 1024)}MB`);
}, 300000); // Every 5 minutes
```

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- **Documentation**: Check this README and system docs
- **Issues**: Report bugs via GitHub Issues
- **Discord**: Join our support server [invite link]
- **Email**: support@wonderbot.com

---

**Built with ❤️ for the Discord community**