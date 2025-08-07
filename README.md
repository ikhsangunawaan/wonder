# 🌌 Wonder Discord Bot - Complete Documentation

**A comprehensive Discord bot featuring advanced economy system, interactive games, leveling, introduction cards, role management, and WonderCoins drop system. Built with Python for enhanced performance and maintainability!**

## 📋 Table of Contents
- [🎨 Design Philosophy](#-design-philosophy)
- [✨ Features Overview](#-features-overview)
- [📦 Installation & Setup](#-installation--setup)
- [📚 Commands Reference](#-commands-reference)
- [⚙️ Configuration](#-configuration)
- [🗄️ Database Support](#-database-support)
- [🚀 Deployment](#-deployment)
- [🔧 Admin Features](#-admin-features)
- [🛠️ Development Guide](#-development-guide)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)

## 🎨 Design Philosophy

### Core Aesthetic: **"Where Wonder Meets Chrome Dreams"**
The Wonder Discord Bot embraces a **dreamy wonder** aesthetic combined with **chrome elegance**, creating a mystical Discord experience that feels both ethereal and sophisticated. Our design uses soft, muted tones and chrome accents to create a calming, wonder-filled atmosphere.

### Visual Identity
- **Primary Symbols**: ✨ (Wonder), 🔮 (Mystical), ⭐ (Excellence), 🌙 (Peace)
- **Color Palette**: Soft chrome blues, dreamy purples, muted accent colors
- **Typography**: Clean, modern fonts with gentle character
- **UI Style**: Gentle minimalism with harmonious information hierarchy

## ✨ Features Overview

### 💰 Advanced Economy System
**Core Features:**
- **WonderCoins Currency**: Virtual currency system with comprehensive transaction tracking
- **Daily Rewards**: 100 WonderCoins every 24 hours (boosters +50, premium +100)
- **Work System**: 50 WonderCoins every hour (boosters +25, premium +50)
- **Balance Management**: Check, transfer, and track all transactions with detailed history
- **Anti-Spam Protection**: Intelligent cooldown system prevents abuse
- **Leaderboard System**: Server-wide wealth competition with ranking displays

**Role-Based Bonuses:**
- **Server Boosters**: +50 daily, +25 work bonus, +25% drop multiplier
- **Premium Members**: +100 daily, +50 work bonus, +50% drop multiplier
- **Multiplier Stacking**: Bonuses stack with other reward systems

### 🪙 WonderCoins Drop System
**Automated Drop Features:**
- **Smart Timing**: Drops occur every 30 minutes to 3 hours globally across all servers
- **Multi-Server Support**: Single centralized system serves all configured servers
- **Channel Configuration**: Admin-configurable channels receive automated drops

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

### 🎮 Interactive Games & Activities
**Available Games:**
- **Coin Flip**: Bet 10-1,000 WonderCoins on heads/tails (2min cooldown)
- **Dice Rolling**: Bet 10-500 WonderCoins, various multipliers (3min cooldown)
- **Slot Machine**: Bet 20-200 WonderCoins, emoji-based slots (5min cooldown)

**Game Features:**
- **Animated Results**: Beautiful animations for all game outcomes
- **Lucky Charm Effects**: Use consumable items to boost win rates
- **Premium Perks**: Reduced cooldowns for boosters and premium members
- **Fair RNG**: Cryptographically secure random number generation
- **Statistics Tracking**: Comprehensive gambling statistics and history

### 🎯 Comprehensive Leveling System

**4-Category Progression System:**
| Category | Max Level | XP Source | Cooldown |
|----------|-----------|-----------|----------|
| **Text** | 50 | Chat messages (15-25 XP) | 60 seconds |
| **Voice** | 50 | Voice channel time (10-15 XP/min) | None |
| **Role** | 50 | Special activities | Varies |
| **Overall** | 50 | Combined progress from all categories | None |

**XP Multipliers:**
- **Regular Users**: 1.0x base XP
- **Server Boosters**: 1.5x multiplier
- **Premium Members**: 1.75x multiplier

**24 Level Roles + 5 Prestige Levels:**
- **Text Chat Roles (6)**: Text Chatter → Supreme Wordsmith
- **Voice Activity Roles (6)**: Voice Newcomer → Voice Legend
- **Community Role Roles (6)**: Helper → Community Legend
- **Overall Progress Roles (5)**: Wonder Apprentice → Wonder Grandmaster
- **Prestige System (5)**: Wonder Prestige I-V (35%-60% XP bonus)

### 🚀 NEW: Progressive Leveling System

**Enhanced Leveling Experience:**
- **Level 1-100 Progression**: Balanced XP formula with intelligent scaling
- **Role Rewards Every 5 Levels**: 20 configurable milestone roles
- **Progressive XP Requirements**: Increases by level ranges (1-10, 11-30, 31-60, 61-100)
- **Manual Role Configuration**: Admin commands for flexible role setup
- **Automatic Role Assignment**: Seamless rewards upon reaching role levels
- **Rich Progress Tracking**: Detailed embeds with progress bars and statistics

**Admin Configuration Commands:**
- `w.level-role-set <level> <@role> [description]` - Configure role rewards
- `w.level-role-remove <level>` - Remove role configurations  
- `w.level-roles-list` - View all configured roles
- `w.xp-calculator <level>` - Calculate XP requirements

**User Commands:**
- `w.progressive-rank [@user]` - View progressive leveling stats
- `w.xp-calc <level>` - Calculate XP needed for specific level

*See `PROGRESSIVE_LEVELING_GUIDE.md` for complete setup instructions.*

### 🎨 Introduction Cards System
**Card Creation:**
- **Interactive Forms**: Modal-based form interface for easy creation
- **Custom Fields**: Name, age, location, hobbies, favorite color, bio
- **Dynamic Generation**: Automatically generated cards using Pillow imaging
- **Profile Integration**: Links to user Discord profiles and avatars

**Visual Features:**
- **Dynamic Backgrounds**: Color-based backgrounds from user's favorite color
- **Typography**: Custom fonts and professional text styling
- **Avatar Integration**: Discord avatar overlay with professional design
- **High Quality Output**: 800x600 PNG images with gradient backgrounds

### 🎉 Advanced Giveaway System
**Comprehensive Management:**
- **Flexible Duration**: Support for minutes to weeks (s/m/h/d/w format)
- **Multiple Winners**: Up to 10 winners per giveaway
- **Advanced Requirements**: Role requirements, account age, message count
- **Weighted Entry System**: Premium (3x), Boosters (2x), Regular (1x)
- **Winner Cooldowns**: 7-day cooldown system prevents frequent winners

**Entry Management Features:**
- **Role Restrictions**: Required roles, forbidden roles, bypass roles
- **Account Verification**: Minimum account age requirements
- **Automatic Management**: Self-managing system with notifications
- **Reroll System**: Advanced reroll with previous winner exclusion

### 🏪 Advanced Shop System
**Item Categories:**
- **Consumables**: Temporary effect items (lucky charms, boosters)
- **Collectibles**: Rare trophies and valuable display items
- **Profile Items**: Custom titles, colors, profile enhancements
- **Special Items**: Unique and event-exclusive limited items

**Shopping Experience:**
- **Interactive Interface**: Category-based browsing with detailed menus
- **Item Previews**: Detailed descriptions and effect explanations
- **Purchase Confirmation**: Clear transaction details and confirmations
- **Inventory Management**: Comprehensive item tracking and usage

## 📦 Installation & Setup

### Prerequisites
```bash
# Required Software
Python 3.8+ (recommended: Python 3.10+)
pip package manager
Git (optional, for cloning)

# System Requirements
Minimum: 1GB RAM, 1GB storage
Recommended: 2GB+ RAM, 2GB+ storage
```

### Quick Setup

**Option 1: Universal Deployment Script (Recommended)**
```bash
# Download and run the deployment script
python3 deploy.py
```

**Option 2: Manual Setup**
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wonder-discord-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the bot**
   ```bash
   python run.py
   ```

### Environment Configuration

Create a `.env` file with the following:

```env
# REQUIRED: Discord bot token
DISCORD_TOKEN=your_discord_bot_token_here

# OPTIONAL: Role IDs for premium features
PREMIUM_ROLE_ID=your_premium_role_id
BOOSTER_ROLE_ID=your_booster_role_id

# OPTIONAL: Database configuration
DATABASE_PATH=wonder.db
LOG_LEVEL=INFO
```

### Discord Bot Setup

1. **Create Discord Application**
   - Visit: https://discord.com/developers/applications
   - Click "New Application" and create your bot
   - Navigate to "Bot" tab and get your token

2. **Configure Bot Permissions**
   - Enable "Server Members Intent"
   - Enable "Message Content Intent"
   - Set appropriate bot permissions in your server

3. **Invite Bot to Server**
   - Use OAuth2 URL Generator with required permissions
   - Select your server and authorize the bot

## 📚 Commands Reference

### 💰 Economy Commands
| Command | Description | Usage Example | Cooldown |
|---------|-------------|---------------|----------|
| `/balance` or `w.balance` | Check WonderCoins balance | `/balance @user` | None |
| `/daily` or `w.daily` | Claim daily reward | `/daily` | 24 hours |
| `/work` or `w.work` | Work for WonderCoins | `/work` | 1 hour |
| `/leaderboard` or `w.leaderboard` | View wealth rankings | `/leaderboard` | None |

### 🎮 Game Commands
| Command | Description | Usage Example | Cooldown |
|---------|-------------|---------------|----------|
| `/coinflip` or `w.coinflip` | Animated coin flip betting | `/coinflip 100 heads` | 2 minutes |
| `/dice` or `w.dice` | Animated dice roll betting | `/dice 50 6` | 3 minutes |
| `/slots` or `w.slots` | Animated slot machine | `/slots 25` | 5 minutes |
| `w.gamestats` | View gambling statistics | `w.gamestats @user` | None |

### 🎯 Leveling Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `w.rank` | Check levels and XP (original) | `w.rank @user` | Everyone |
| `w.roles` | View level roles information | `w.roles text` | Everyone |
| `w.prestige` | View prestige system info | `w.prestige` | Everyone |

### 🚀 Progressive Leveling Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `w.progressive-rank` (aliases: `prank`, `plevel`) | View progressive leveling stats | `w.progressive-rank @user` | Everyone |
| `w.xp-calculator` (alias: `xp-calc`) | Calculate XP for any level | `w.xp-calc 50` | Everyone |
| `w.level-role-set` | Configure role reward | `w.level-role-set 25 @Veteran "Quarter-century!"` | Admin |
| `w.level-role-remove` | Remove role reward | `w.level-role-remove 10` | Admin |
| `w.level-roles-list` | List all configured roles | `w.level-roles-list` | Everyone |

### 🎉 Giveaway Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `w.giveaway-create` | Create advanced giveaway | `w.giveaway-create "Prize" 1h --winners 3` | Admin |
| `w.quickgiveaway` | Quick giveaway creation | `w.quickgiveaway 60 1 "100 WonderCoins"` | Admin |
| `w.giveaway-end` | End giveaway manually | `w.giveaway-end 123` | Admin/Host |
| `w.giveaway-reroll` | Reroll giveaway winners | `w.giveaway-reroll 123 2` | Admin/Host |
| `w.giveaway-list` | List active giveaways | `w.giveaway-list` | Everyone |

### 🪙 WonderCoins Drop Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `/adddrops` or `w.adddrops` | Add drop channel | `/adddrops #general` | Admin |
| `/removedrops` or `w.removedrops` | Remove drop channel | `/removedrops #general` | Admin |
| `/forcedrop` or `w.forcedrop` | Manual drop trigger | `/forcedrop 500 epic` | Admin |
| `w.configdrops` | Configure drop settings | `w.configdrops interval 45` | Admin |
| `w.dropchannels` | List drop channels | `w.dropchannels` | Admin |

### 🏪 Shop Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `w.shop` | Browse shop categories | `w.shop consumables` | Everyone |
| `w.buy` | Purchase items | `w.buy lucky_charm 2` | Everyone |
| `w.inventory` | View owned items | `w.inventory` | Everyone |
| `w.use` | Use consumable items | `w.use lucky_charm` | Everyone |

### 🔧 Utility Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `/help` or `w.help` | Complete help system | `/help` | Everyone |

## ⚙️ Configuration

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
    "name": "Wonder Discord Bot",
    "tagline": "Python Edition",
    "version": "2.0.0",
    "theme": "Dreamy Wonder meets Chrome"
  },
  "multipliers": {
    "booster": {
      "daily": 1.5,
      "work": 1.5,
      "drops": 1.25,
      "xp": 1.5
    },
    "premium": {
      "daily": 2.0,
      "work": 2.0,
      "drops": 1.5,
      "xp": 1.75
    }
  },
  "cooldowns": {
    "daily": 1440,
    "work": 60,
    "coinflip": 2,
    "dice": 3,
    "slots": 5,
    "text_xp": 1,
    "use_item": 1
  },
  "colors": {
    "primary": "#B8C5D6",
    "secondary": "#A89CC8",
    "success": "#8FBC8F",
    "error": "#CD919E",
    "warning": "#E6B077",
    "info": "#87CEEB"
  }
}
```

## 🗄️ Database Support

The bot supports both **SQLite** (default) and **MySQL** databases:

### SQLite Configuration (Default)
```json
{
  "database": {
    "type": "sqlite",
    "path": "wonder.db"
  }
}
```

### MySQL Configuration
```json
{
  "database": {
    "type": "mysql",
    "host": "your-mysql-host",
    "port": 3306,
    "database": "your_database_name",
    "username": "your_username",
    "password": "your_password",
    "charset": "utf8mb4",
    "autocommit": true,
    "pool_settings": {
      "minsize": 1,
      "maxsize": 10
    }
  }
}
```

### Database Migration
To migrate from SQLite to MySQL:
```bash
python migrate_to_mysql.py
```

## 🚀 Deployment

### Supported Platforms

The bot can be deployed on any platform with Python 3.8+:

#### ☁️ Cloud Platforms
- **Heroku**: Use `Procfile` - `worker: python run.py`
- **Railway**: Use `railway.json` configuration
- **Render**: Deploy as Background Worker with `render.yaml`

#### 🐳 Docker
```bash
# Build and run with Docker
docker build -t wonder-bot .
docker run -d --env-file .env wonder-bot

# Or use Docker Compose
docker-compose up -d
```

#### 🖥️ VPS/Dedicated Servers
```bash
# Automated installation
sudo bash install.sh

# Manual installation
python3 deploy.py
systemctl start wonder-bot
```

#### 🏠 Pterodactyl Panel
1. Create new Python server
2. Upload bot files
3. Set startup command: `python3 run.py`
4. Configure environment variables

### Universal Deployment Script
The bot includes a universal deployment script that works on any platform:

```bash
python3 deploy.py
```

This script automatically:
- Detects your system configuration
- Installs dependencies
- Creates configuration files
- Sets up startup scripts
- Validates the installation

## 🔧 Admin Features

### Category Management
Admins can control leveling categories per server:
```
w.toggle-category text false    # Disable text leveling
w.toggle-category voice true    # Enable voice leveling
```

### User Management
Comprehensive user data management:
```
w.set-user-xp @user text 1000      # Set user XP
w.add-user-xp @user voice 500      # Add XP
w.reset-user-xp @user all          # Reset all XP
w.set-user-currency @user 5000     # Set currency
w.add-user-currency @user -1000    # Remove currency
```

### Enhanced Input Parsing
All admin commands accept:
- **User mentions**: `@username`
- **User IDs**: `123456789`
- **Role mentions**: `@role`
- **Role IDs**: `987654321`
- **Channel mentions**: `#channel`
- **Channel IDs**: `111222333`

### Permission-Based Help
The help system automatically shows different commands based on user permissions:
- **Regular users**: Basic commands only
- **Administrators**: Admin commands included
- **Bot owners**: All commands visible

## 🛠️ Development Guide

### Project Structure
```
wonder-discord-bot/
├── src/
│   ├── main.py                 # Main bot implementation
│   ├── config.py               # Configuration management
│   ├── database.py             # Database operations
│   ├── mysql_database.py       # MySQL adapter
│   ├── shop_system.py          # Shop and inventory
│   ├── giveaway_system.py      # Giveaway system
│   ├── role_manager.py         # Role management
│   ├── games_system.py         # Gambling games
│   ├── wondercoins_drops.py    # Drop system
│   ├── leveling_system.py      # Leveling system
│   ├── intro_card_system.py    # Introduction cards
│   ├── cooldown_manager.py     # Cooldown management
│   └── utils/
├── deploy.py                   # Universal deployment
├── validate_deployment.py      # Deployment validation
├── migrate_to_mysql.py         # Database migration
├── config.json                 # Bot configuration
├── requirements.txt            # Dependencies
├── run.py                      # Entry point
├── Dockerfile                  # Docker deployment
├── docker-compose.yml          # Docker Compose
└── README.md                   # This documentation
```

### Technology Stack
- **discord.py**: Modern Discord API wrapper with hybrid commands
- **aiosqlite/aiomysql**: Async database operations
- **Pillow (PIL)**: Image generation and manipulation
- **aiohttp**: HTTP requests for avatar fetching
- **python-dotenv**: Environment variable management

### Error Handling System
The bot includes comprehensive error handling:
- **Detailed Error Messages**: Clear explanations of what went wrong
- **Usage Guidance**: Shows correct command usage
- **Parameter Validation**: Validates input before execution
- **Graceful Fallbacks**: Automatic recovery from non-critical errors

Example error message:
```
❌ Command Error
**Invalid argument provided for `coinflip` command**
Bet amount must be between 10 and 1000 WonderCoins.

📝 Usage: `w.coinflip <amount> <choice>` or `/coinflip <amount> <choice>`
📋 Description: Flip a coin and bet WonderCoins
⚙️ Parameters:
• amount (required): Amount to bet (10-1000 coins)
• choice (required): h/heads or t/tails
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Bot Not Responding
**Symptoms**: Bot appears online but doesn't respond to commands
**Solutions**:
- Verify DISCORD_TOKEN in `.env` file
- Check bot has necessary permissions in Discord server
- Ensure Message Content Intent is enabled
- Review console logs for error messages

#### Database Errors
**Symptoms**: Database write/read failures
**Solutions**:
```bash
# Check file permissions
ls -la wonder.db
chmod 664 wonder.db

# Test database connection
python test_mysql_connection.py  # For MySQL

# Recreate database if corrupted
rm wonder.db
python run.py  # Will recreate database
```

#### Python Import Errors
**Symptoms**: Module not found errors
**Solutions**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Use deployment script
python3 deploy.py

# Check virtual environment
which python
pip list
```

#### Image Generation Failures
**Symptoms**: Introduction cards fail to generate
**Solutions**:
```bash
# Install system fonts (Linux)
sudo apt-get install fonts-dejavu fonts-liberation

# Verify Pillow installation
pip install Pillow --upgrade
```

### Debug Tools
The bot includes several debug and validation tools:

```bash
# Validate deployment
python3 validate_deployment.py

# Test bot functionality
python3 debug_bot.py

# Test MySQL connection
python3 test_mysql_connection.py

# Advanced debugging
python3 debug_advanced.py
```

### Performance Monitoring
The bot includes built-in monitoring:
- Memory usage tracking
- Command execution timing
- Database operation metrics
- Error rate monitoring

## 🤝 Contributing

### Development Guidelines
- Follow PEP 8 coding standards
- Add type hints to all functions
- Include comprehensive docstrings
- Write tests for new features
- Update documentation as needed

### Contributing Process
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Reporting Issues
**Include this information:**
- Operating system and version
- Python version (`python --version`)
- Error messages (full stack trace)
- Steps to reproduce the issue
- Configuration (without sensitive data)

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Acknowledgments

- **discord.py** community for excellent Discord API wrapper
- **Pillow** team for powerful image processing capabilities
- **aiosqlite** developers for async SQLite support
- **Python community** for amazing tools and libraries

---

**🌌 Wonder Discord Bot - Where Wonder Meets Chrome Dreams! ✨**

*Built with ❤️ for the Discord community. Transform your server into a wonderland of engagement, gaming, and magical experiences.*
