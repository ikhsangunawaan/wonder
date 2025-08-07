# 🌌 Wonder Discord Bot - Complete Documentation

**A comprehensive Discord bot featuring advanced economy system, interactive games, leveling, introduction cards, role management, and WonderCoins drop system. Built with Python for enhanced performance and maintainability!**

## 📋 Table of Contents
- [🎨 Design Philosophy](#-design-philosophy)
- [✨ Features Overview](#-features-overview)
- [📦 Installation & Setup](#-installation--setup)
- [📚 Commands Reference](#-commands-reference)
- [⚙️ Configuration](#-configuration)
- [🗄️ Database Schema](#-database-schema)
- [🛠️ Development Guide](#-development-guide)
- [🚀 Deployment](#-deployment)
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

### 🎯 Advanced Leveling System
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

**Progression Rewards:**
- **Currency Rewards**: WonderCoins bonuses at level milestones
- **Role Rewards**: Automatic role assignment (configurable)
- **Title System**: Custom titles for achievements
- **Level Announcements**: Beautiful embeds for level-up celebrations

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

### 🔧 Welcome & Setup System
**Welcome Features:**
- **Custom Messages**: Personalized welcome text with templates
- **Introduction Integration**: Direct links to introduction card creation
- **Channel Configuration**: Automatic posting to designated channels
- **Member Onboarding**: Streamlined new user experience

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

# OPTIONAL: Database and logging
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
| `w.rank` | Check levels and XP | `w.rank @user` | Everyone |

### 🎉 Giveaway Commands
| Command | Description | Usage Example | Access Level |
|---------|-------------|---------------|--------------|
| `w.giveaway create` | Create advanced giveaway | `w.giveaway create "Prize" 1h --winners 3` | Admin |
| `w.quickgiveaway` | Quick giveaway creation | `w.quickgiveaway 60 1 "100 WonderCoins"` | Admin |
| `w.giveaway end` | End giveaway manually | `w.giveaway end 123` | Admin/Host |
| `w.giveaway reroll` | Reroll giveaway winners | `w.giveaway reroll 123 2` | Admin/Host |
| `w.giveaway list` | List active giveaways | `w.giveaway list` | Everyone |

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

### WonderCoins Drop System Configuration
```python
# Configuration in wondercoins_drops.py
drop_config = {
    "minAmount": 50,
    "maxAmount": 500,
    "minInterval": 1800000,    # 30 minutes
    "maxInterval": 10800000,   # 3 hours
    "collectTime": 60000,      # 60 seconds
    
    # Rarity system
    "rarities": {
        "common": {"chance": 0.84, "multiplier": 1},
        "rare": {"chance": 0.10, "multiplier": 3},
        "epic": {"chance": 0.05, "multiplier": 5},
        "legendary": {"chance": 0.01, "multiplier": 10}
    }
}
```

## 🗄️ Database Schema

The bot uses SQLite with comprehensive table structure:

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

-- Comprehensive transaction history
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    type TEXT,
    amount INTEGER,
    description TEXT,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User leveling data (4-category system)
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
    voice_session_start DATETIME
);

-- Introduction cards system
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
```

### Advanced Tables
```sql
-- WonderCoins drop statistics
CREATE TABLE drop_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT,
    user_id TEXT,
    amount INTEGER,
    rarity TEXT,
    collection_type TEXT,
    multiplier REAL,
    drop_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Comprehensive giveaway system
CREATE TABLE giveaways (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id TEXT,
    channel_id TEXT,
    message_id TEXT,
    host_id TEXT,
    prize TEXT,
    description TEXT,
    winner_count INTEGER,
    end_time DATETIME,
    ended BOOLEAN DEFAULT FALSE,
    required_roles TEXT,
    forbidden_roles TEXT,
    bypass_roles TEXT,
    winner_role_id TEXT,
    min_account_age INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User inventory system
CREATE TABLE user_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    item_id TEXT,
    quantity INTEGER DEFAULT 1,
    acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Drop channel configuration
CREATE TABLE drop_channels (
    guild_id TEXT,
    channel_id TEXT,
    added_by TEXT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (guild_id, channel_id)
);
```

## 🛠️ Development Guide

### Project Structure
```
wonder-discord-bot/
├── src/
│   ├── main.py                 # Main bot implementation with all commands
│   ├── config.py               # Configuration management
│   ├── database.py             # Database operations and schema
│   ├── shop_system.py          # Shop and inventory management
│   ├── giveaway_system.py      # Advanced giveaway system
│   ├── role_manager.py         # Role assignment and management
│   ├── games_system.py         # Gambling games with animations
│   ├── wondercoins_drops.py    # Automatic drop system
│   ├── leveling_system.py      # 4-category leveling system
│   ├── intro_card_system.py    # Introduction card generation
│   ├── cooldown_manager.py     # Cooldown and rate limiting
│   └── utils/
│       └── canvas_utils.py     # Image generation utilities
├── config.json                 # Bot configuration
├── requirements.txt            # Python dependencies
├── run.py                      # Bot runner script
├── start.sh                    # Shell startup script
├── .env.example                # Environment template
└── README.md                   # This documentation
```

### Technology Stack
- **discord.py**: Modern Discord API wrapper with hybrid commands
- **aiosqlite**: Async SQLite operations for performance
- **Pillow (PIL)**: Advanced image generation and manipulation
- **aiohttp**: HTTP requests for avatar fetching
- **python-dotenv**: Environment variable management

### Adding New Features

1. **New Commands**: Add hybrid commands in `main.py` or create new cog files
2. **Database Changes**: Update `database.py` with new schema and methods
3. **Configuration**: Modify `config.json` for new settings
4. **Images**: Extend `canvas_utils.py` for new image generation features

## 🚀 Deployment

### Production Environment Setup

1. **Prepare Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Production Configuration**
   ```env
   NODE_ENV=production
   DEBUG=false
   DATABASE_PATH=/opt/wonderbot/data/wonder.db
   LOG_LEVEL=INFO
   ```

3. **Service Setup (systemd)**
   ```ini
   [Unit]
   Description=Wonder Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=wonderbot
   WorkingDirectory=/opt/wonder-discord-bot
   Environment=PATH=/opt/wonder-discord-bot/venv/bin
   ExecStart=/opt/wonder-discord-bot/venv/bin/python run.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

### Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run.py"]
```

### Cloud Platform Deployment

**Heroku:**
```bash
# Use provided Procfile
worker: python run.py

# Set environment variables in dashboard
# Deploy with git push heroku main
```

**Railway/Render:**
- Upload project to platform
- Set environment variables
- Use start command: `python run.py`

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

### Debug Mode
Enable detailed logging by adding to `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
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
