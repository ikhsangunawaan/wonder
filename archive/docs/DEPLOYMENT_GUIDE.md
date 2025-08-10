# 🚀 Universal Deployment Guide - Wonder Discord Bot

## Quick Start (Any Platform)

### 1. Run Deployment Script
```bash
python3 deploy.py
# or
python deploy.py
```

### 2. Configure Discord Token
Edit `.env` file and set your Discord bot token:
```env
DISCORD_TOKEN=your_actual_bot_token_here
```

### 3. Start the Bot
**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Manual:**
```bash
python3 run.py
```

## Platform-Specific Deployment

### 🔧 Local Development
```bash
# Clone repository
git clone <repository_url>
cd wonder-discord-bot

# Run deployment script
python3 deploy.py

# Configure token in .env
# Start bot
./start.sh  # or start.bat on Windows
```

### ☁️ Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-bot-name

# Set environment variables
heroku config:set DISCORD_TOKEN=your_token_here

# Deploy
git push heroku main
```

### 🚂 Railway
1. Connect GitHub repository to Railway
2. Set environment variable: `DISCORD_TOKEN`
3. Deploy automatically

### 🎨 Render
1. Connect GitHub repository to Render
2. Set environment variable: `DISCORD_TOKEN`
3. Deploy as Background Worker

### 🐳 Docker
```bash
# Build image
docker build -t wonder-discord-bot .

# Run with environment file
docker run -d --env-file .env wonder-discord-bot

# Or use docker-compose
docker-compose up -d
```

### 🖥️ VPS/Dedicated Server
```bash
# Install Python 3.8+
sudo apt update
sudo apt install python3 python3-pip

# Clone and setup
git clone <repository_url>
cd wonder-discord-bot
python3 deploy.py

# Configure .env file
nano .env

# Start with screen/tmux
screen -S discord-bot
./start.sh

# Or create systemd service (Linux)
sudo cp wonder-bot.service /etc/systemd/system/
sudo systemctl enable wonder-bot
sudo systemctl start wonder-bot
```

### 🏠 Pterodactyl Panel
1. Create new Python server
2. Upload bot files
3. Set startup command: `python3 run.py`
4. Configure environment variables

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | ✅ | Your Discord bot token |
| `PREMIUM_ROLE_ID` | ❌ | Premium role ID for bonuses |
| `BOOSTER_ROLE_ID` | ❌ | Server booster role ID |
| `DB_TYPE` | ❌ | Database type (sqlite/mysql) |
| `DB_HOST` | ❌ | MySQL host (if using MySQL) |
| `DB_PORT` | ❌ | MySQL port (if using MySQL) |
| `DB_NAME` | ❌ | MySQL database name |
| `DB_USER` | ❌ | MySQL username |
| `DB_PASSWORD` | ❌ | MySQL password |

## Bot Permissions

Required Discord permissions:
- Send Messages
- Embed Links
- Add Reactions
- Use Slash Commands
- Manage Roles (for leveling system)
- Manage Messages (for giveaways)

## Troubleshooting

### Common Issues
1. **"Improper token"**: Check Discord token in .env
2. **Module not found**: Run `python3 deploy.py` to install dependencies
3. **Permission denied**: Make startup scripts executable with `chmod +x start.sh`
4. **Database errors**: Check database configuration in .env

### Getting Help
1. Check `bot.log` for error details
2. Verify Python version (3.8+ required)
3. Ensure all dependencies are installed
4. Check Discord bot permissions

## Features
- ✅ Economy system with WonderCoins
- ✅ Gambling games (coinflip, dice, slots)
- ✅ Leveling system with roles
- ✅ Shop system with items
- ✅ Giveaway system
- ✅ Admin management tools
- ✅ Both prefix (`w.`) and slash commands
- ✅ Comprehensive error handling
- ✅ Auto-drops system
- ✅ User profiles and intro cards

Total: 100+ commands available!
