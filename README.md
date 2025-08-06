# 🏰 Wonder Discord Bot - Python Edition

**A comprehensive Discord bot featuring advanced economy system, interactive games, leveling, introduction cards, and role management. Now converted to Python for better performance and maintainability!**

## 🚀 Features Overview

### 💰 Economy System
- **WonderCoins Currency**: Virtual currency with daily/work commands
- **Games**: Coinflip, Dice, Slots with betting mechanics
- **Shop System**: Item purchasing and inventory management
- **Leaderboards**: Track top earners across the server
- **Transaction History**: Full audit trail of all currency movements

### 🎨 Introduction Cards
- **Visual Profiles**: Beautiful introduction cards with Pillow-generated graphics
- **Customizable Design**: Personal colors, bio, hobbies, and avatar integration
- **High Quality**: 800x600 PNG images with gradient backgrounds and decorations

### 📈 Leveling System
- **Multi-Type XP**: Text, Voice, and Role-based experience points
- **Smart Rewards**: Automatic currency and role rewards for leveling up
- **Progress Tracking**: Comprehensive rank and progress displays
- **Level Announcements**: Beautiful embeds for level-up celebrations

### 🎮 Games & Activities
- **Coinflip**: Simple heads/tails betting game
- **Dice Rolling**: Multi-sided dice with betting
- **Slot Machine**: Classic slots with different payout rates
- **Cooldown System**: Prevents spam and encourages balanced play

### 🔧 Administration
- **Server Setup**: Easy configuration for channels and settings
- **Role Management**: Automatic role assignment based on levels
- **Giveaway System**: Create and manage server giveaways
- **Premium Features**: Enhanced functionality for boosters

## 📦 Installation & Setup

### Prerequisites
- **Python 3.8+** (recommended: Python 3.10+)
- **pip** package manager
- **Discord Bot Token** ([Create one here](https://discord.com/developers/applications))

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
   # Edit .env with your bot token
   ```

4. **Run the bot**
   ```bash
   python run.py
   ```

### Environment Variables

Create a `.env` file with the following:

```env
# Required
DISCORD_TOKEN=your_discord_bot_token_here

# Optional - for premium features
PREMIUM_ROLE_ID=your_premium_role_id
BOOSTER_ROLE_ID=your_booster_role_id

# Optional - for faster development
GUILD_ID=your_test_guild_id
```

## 🎯 Commands Reference

### Economy Commands
- `w.balance` / `w.bal` - Check your WonderCoins balance
- `w.daily` - Claim daily reward (100 coins, 24h cooldown)
- `w.work` - Work for coins (50 coins, 1h cooldown)
- `w.leaderboard` / `w.lb` - View top earners

### Games (Coming Soon)
- `w.coinflip <amount>` - Bet on heads or tails
- `w.dice <amount>` - Roll dice with betting
- `w.slots <amount>` - Play slot machine

### Leveling (Coming Soon)
- `w.rank` - View your level and XP
- `w.level` - Detailed level information
- `w.leaderboard xp` - XP leaderboard

### Introduction Cards (Coming Soon)
- `w.intro` - Create your introduction card
- `w.profile` - View someone's profile

## 🗄️ Database Schema

The bot uses SQLite with the following main tables:

- **users** - Basic user data and economy info
- **user_levels** - XP and leveling data
- **transactions** - Complete transaction history
- **introduction_cards** - User profile information
- **user_inventory** - Item ownership
- **giveaways** - Active and past giveaways

## 🛠️ Development

### Project Structure
```
wonder-discord-bot/
├── src/
│   ├── main.py              # Main bot file
│   ├── config.py            # Configuration management
│   ├── database.py          # Database operations
│   ├── cooldown_manager.py  # Cooldown system
│   ├── leveling_system.py   # XP and levels
│   └── utils/
│       └── canvas_utils.py  # Image generation
├── config.json              # Bot configuration
├── requirements.txt         # Python dependencies
├── run.py                   # Bot runner script
└── .env.example             # Environment template
```

### Technology Stack
- **discord.py** - Discord API wrapper
- **aiosqlite** - Async SQLite operations
- **Pillow (PIL)** - Image generation and manipulation
- **aiohttp** - HTTP requests for avatars
- **python-dotenv** - Environment variable management

### Adding Features

1. **New Commands**: Add to `main.py` or create new cog files
2. **Database Changes**: Update `database.py` with new methods
3. **Configuration**: Modify `config.json` for new settings
4. **Images**: Extend `canvas_utils.py` for new graphics

## 🔧 Configuration

The bot uses `config.json` for its configuration. Key settings include:

```json
{
  "prefix": "w.",
  "currency": {
    "name": "WonderCoins",
    "symbol": "💰",
    "dailyAmount": 100,
    "workAmount": 50
  },
  "cooldowns": {
    "daily": 1440,
    "work": 60
  },
  "colors": {
    "primary": "#FFD700",
    "success": "#228B22",
    "error": "#DC143C"
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the bot token is correct
   - Verify the bot has necessary permissions
   - Check console for error messages

2. **Database errors**
   - Ensure the bot has write permissions in its directory
   - Check if SQLite is properly installed

3. **Image generation fails**
   - Install system fonts: `sudo apt-get install fonts-dejavu`
   - Verify Pillow is correctly installed

4. **Avatar loading issues**
   - Check internet connection
   - Verify aiohttp is installed

### Support

For issues and support:
1. Check the logs in `bot.log`
2. Review the configuration files
3. Ensure all dependencies are installed
4. Verify Discord permissions

## 📝 Migration from JavaScript

If you're migrating from the JavaScript version:

1. **Database**: The Python version uses the same SQLite database schema
2. **Configuration**: `config.json` remains unchanged
3. **Features**: All core features have been ported
4. **Performance**: Python version includes optimizations and better async handling

## 🚀 Deployment

### Production Deployment

1. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure production settings**
   - Set up proper logging
   - Configure database backups
   - Set up process monitoring (pm2, systemd, etc.)

4. **Run with process manager**
   ```bash
   # Using systemd (recommended for Linux)
   sudo systemctl enable wonder-bot
   sudo systemctl start wonder-bot
   ```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run.py"]
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Acknowledgments

- **discord.py** community for excellent Discord API wrapper
- **Pillow** team for powerful image processing
- Original JavaScript bot contributors

---

**Happy botting! 🤖✨**