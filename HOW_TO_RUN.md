# How to Run the Wonder Discord Bot

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Discord Bot Token** from Discord Developer Portal

## Setup Instructions

### 1. Install Dependencies

```bash
pip install --break-system-packages -r requirements.txt
```

Or if you prefer using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the `.env` file template:
   ```bash
   cp .env .env.local
   ```

2. Edit `.env` and add your Discord bot token:
   ```env
   DISCORD_TOKEN=your_actual_discord_bot_token_here
   PREMIUM_ROLE_ID=your_premium_role_id_here  # Optional
   BOOSTER_ROLE_ID=your_booster_role_id_here  # Optional
   ```

### 3. Get a Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Create a bot and copy the token
5. Enable necessary intents:
   - Message Content Intent
   - Server Members Intent
   - Reaction Intent

### 4. Run the Bot

```bash
python3 run.py
```

## Deployment to Hosting Services

### Option 1: Using start.sh Script (Recommended)
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Direct Python Command
```bash
python3 run.py
```

### Option 3: For Heroku/Railway/Similar Platforms
Use the included `Procfile`:
```
worker: python3 run.py
```

### Fixing Python Path Issues
If you encounter errors like "can't open file '/usr/local/bin/python'":

1. **Use the start.sh script** - it automatically detects the correct Python path
2. **Check your hosting provider's Python path** - some use `/usr/bin/python3` instead of `/usr/local/bin/python`
3. **Use environment variables** in your hosting dashboard to set the Python executable path

### Environment Variables for Hosting
Make sure to set these in your hosting provider's dashboard:
- `DISCORD_TOKEN` - Your Discord bot token
- `PREMIUM_ROLE_ID` - Optional premium role ID
- `BOOSTER_ROLE_ID` - Optional booster role ID

## Bot Features

- **Economy System**: WonderCoins, daily rewards, work commands
- **Games**: Coinflip, dice, slots
- **Shop System**: Buy items and manage inventory
- **Leveling System**: XP and level tracking
- **Giveaway System**: Create and manage giveaways
- **Auto WonderCoins Drops**: Random coin drops in channels

## Commands

The bot uses `w.` as the default prefix. Example commands:

- `w.balance` - Check your balance
- `w.daily` - Claim daily coins
- `w.work` - Work for coins
- `w.coinflip <amount>` - Play coinflip
- `w.shop` - View the shop
- `w.rank` - Check your level
- `w.help` - Get help

## Troubleshooting

1. **"Improper token" error**: Make sure your Discord token is correct in the `.env` file
2. **Import errors**: Ensure all dependencies are installed correctly
3. **Permission errors**: Make sure the bot has necessary permissions in your Discord server
4. **Python path errors**: Use the `start.sh` script or check your hosting provider's Python installation path

## Database

The bot uses SQLite database (`wonder.db`) which is created automatically on first run.