# 🚀 Wonder Discord Bot - Pterodactyl Hosting Guide

## Overview
This guide will help you successfully host the Wonder Discord Bot using Anjas Hosting with Pterodactyl Daemon terminal.

## ✅ Prerequisites Fixed
- ✅ Python dependencies installed
- ✅ Code errors resolved (`drop_channels` naming issue)
- ✅ Startup scripts created
- ✅ Configuration files ready

## 🔧 Step-by-Step Setup

### 1. Discord Bot Token Setup

First, you need to get your Discord bot token:

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select an existing one
3. Go to the **Bot** section
4. Copy the bot token

### 2. Environment Configuration

In your Pterodactyl terminal, set the Discord token:

```bash
export DISCORD_TOKEN='your_actual_discord_bot_token_here'
```

**Important:** Replace `your_actual_discord_bot_token_here` with your real Discord bot token.

### 3. Start the Bot

You have several options to start the bot:

#### Option A: Using the Pterodactyl start script (Recommended)
```bash
./start_pterodactyl.sh
```

#### Option B: Using the original start script
```bash
./start.sh
```

#### Option C: Direct Python execution
```bash
python3 run.py
```

## 🛠️ Common Pterodactyl Issues & Solutions

### Issue 1: "Improper token has been passed"
**Solution:** Set the correct Discord bot token:
```bash
export DISCORD_TOKEN='your_real_token_here'
```

### Issue 2: Dependencies not found
**Solution:** Reinstall dependencies:
```bash
pip3 install --break-system-packages -r requirements.txt
```

### Issue 3: Permission denied on start script
**Solution:** Make script executable:
```bash
chmod +x start_pterodactyl.sh
chmod +x start.sh
```

### Issue 4: Python not found
**Solution:** Use the full path:
```bash
/usr/bin/python3 run.py
```

## 📋 Pre-configured Files

The following files have been created/fixed for you:

1. **`setup_pterodactyl.py`** - Setup and configuration checker
2. **`start_pterodactyl.sh`** - Optimized start script for Pterodactyl
3. **`.env`** - Environment configuration (needs token update)
4. **Fixed code issues** - Resolved naming conflicts in main.py

## 🔄 Persistent Hosting

For 24/7 hosting on Pterodactyl:

1. Set the startup command in Pterodactyl panel to:
   ```bash
   ./start_pterodactyl.sh
   ```

2. Or use:
   ```bash
   python3 run.py
   ```

3. Make sure to set environment variables in the Pterodactyl panel:
   - Variable: `DISCORD_TOKEN`
   - Value: Your actual Discord bot token

## 🚨 Security Notes

- Never share your Discord bot token
- Keep your `.env` file secure
- Use environment variables in production
- Regularly regenerate your bot token if compromised

## 📊 Bot Features

Your Wonder Discord Bot includes:

- 💰 Economy system with WonderCoins
- 🎮 Games (coinflip, dice, slots)
- 🏆 Leveling and XP system
- 🎁 Giveaway system
- 🛒 Shop system
- 🎯 Drop channels for rewards
- 👋 Intro card system
- 📈 Leaderboards and statistics

## 🔧 Configuration

Bot settings can be modified in:
- `config.json` - Main bot configuration
- `.env` - Environment variables
- Database settings in the database files

## 🆘 Troubleshooting

Run the setup checker anytime:
```bash
python3 setup_pterodactyl.py
```

This will check:
- Dependencies installation
- Configuration status
- Environment variables
- File permissions

## 📞 Support

If you encounter issues:

1. Check the bot logs: `cat bot.log`
2. Run the setup checker: `python3 setup_pterodactyl.py`
3. Verify your Discord bot token is correct
4. Check Pterodactyl console for error messages

## 🎉 Success!

Once configured correctly, you should see:
```
🚀 Starting Wonder Discord Bot...
🐍 Using python3
📦 Checking dependencies...
✅ discord.py installed
🎯 Starting bot...
[Bot Name] is ready!
```

Your bot is now running 24/7 on Anjas Hosting with Pterodactyl!