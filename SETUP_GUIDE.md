# 🚀 Wonder Discord Bot - Complete Setup Guide

## 📋 Table of Contents
- [Prerequisites](#-prerequisites)
- [Discord Bot Setup](#-discord-bot-setup)
- [Installation Steps](#-installation-steps)
- [Configuration](#-configuration)
- [First Run](#-first-run)
- [Server Setup](#-server-setup)
- [Testing & Verification](#-testing--verification)
- [Troubleshooting](#-troubleshooting)
- [Production Deployment](#-production-deployment)

## 🔧 Prerequisites

### System Requirements
```bash
# Required Software
Node.js >= 18.0.0 (LTS recommended)
npm >= 8.0.0
Git >= 2.0

# Operating System
Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)

# Hardware
Minimum: 1GB RAM, 1GB storage
Recommended: 2GB+ RAM, 2GB+ storage
```

### Check Your System
```bash
# Verify Node.js installation
node --version
# Should return v18.x.x or higher

# Verify npm installation
npm --version
# Should return 8.x.x or higher

# Verify Git installation
git --version
# Should return git version 2.x.x
```

### Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev libpixman-1-dev
```

#### CentOS/RHEL
```bash
sudo yum groupinstall "Development Tools"
sudo yum install cairo-devel pango-devel libjpeg-turbo-devel giflib-devel
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Or install via Homebrew
brew install cairo pango libffi
```

#### Windows
```powershell
# Install build tools via npm
npm install -g windows-build-tools

# Or install Visual Studio Build Tools 2019/2022
# Download from: https://visualstudio.microsoft.com/downloads/
```

## 🤖 Discord Bot Setup

### Step 1: Create Discord Application
1. **Go to Discord Developer Portal**
   - Visit: https://discord.com/developers/applications
   - Click "New Application"
   - Enter name: "Wonder Bot" (or your preferred name)
   - Click "Create"

2. **Configure Application**
   - **General Information Tab**:
     - Copy "Application ID" (this is your CLIENT_ID)
     - Add description: "Luxury Kingdom Discord Bot"
     - Upload app icon (optional)

### Step 2: Create Bot User
1. **Navigate to Bot Tab**
   - Click "Bot" in left sidebar
   - Click "Add Bot" → "Yes, do it!"

2. **Configure Bot Settings**
   - **Username**: Set to "Wonder Bot" or preferred name
   - **Avatar**: Upload bot avatar (optional)
   - **Public Bot**: ✅ Enable (allows others to add your bot)
   - **Requires OAuth2 Code Grant**: ❌ Disable
   - **Bot Permissions**: Configure as needed

3. **Get Bot Token**
   - Click "Reset Token" → "Yes, do it!"
   - **IMPORTANT**: Copy the token immediately and save securely
   - This is your DISCORD_TOKEN (never share this!)

### Step 3: Configure Bot Permissions
1. **In Bot Tab, scroll to "Privileged Gateway Intents"**
   - ✅ Enable "Server Members Intent"
   - ✅ Enable "Message Content Intent"
   - ❌ "Presence Intent" (not required)

2. **Save Changes**
   - Click "Save Changes" at bottom

### Step 4: Generate Invite Link
1. **Navigate to OAuth2 → URL Generator**
2. **Select Scopes**:
   - ✅ `bot`
   - ✅ `applications.commands`

3. **Select Bot Permissions**:
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Use External Emojis
   - ✅ Manage Roles (if using role rewards)
   - ✅ Connect (for voice XP tracking)
   - ✅ View Channels

4. **Copy Generated URL**
   - Copy the generated URL at bottom
   - Save this for adding bot to servers

### Step 5: Add Bot to Server
1. **Use Generated Invite URL**
   - Open the copied URL in browser
   - Select your Discord server
   - Click "Authorize"
   - Complete CAPTCHA if prompted

2. **Verify Bot Added**
   - Check your Discord server
   - Bot should appear in member list (offline until started)

## 📥 Installation Steps

### Step 1: Clone Repository
```bash
# Option A: Clone via HTTPS
git clone https://github.com/your-username/wonder-discord-bot.git

# Option B: Clone via SSH (if you have SSH keys set up)
git clone git@github.com:your-username/wonder-discord-bot.git

# Navigate to project directory
cd wonder-discord-bot
```

### Step 2: Install Dependencies
```bash
# Install all required packages
npm install

# Verify installation
npm list --depth=0
```

**If you encounter Canvas installation errors**, refer to the [Troubleshooting](#-troubleshooting) section.

### Step 3: Verify File Structure
```bash
# Check that all files are present
ls -la

# Should include:
# - src/ (source code directory)
# - config.json (bot configuration)
# - package.json (dependencies)
# - .env.example (environment template)
# - README.md (documentation)
```

## ⚙️ Configuration

### Step 1: Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit the .env file
nano .env
# or use your preferred text editor
```

### Step 2: Fill Required Variables
**Edit `.env` file with your values:**

```env
# REQUIRED: Discord bot token from Step 2.3
DISCORD_TOKEN=your_bot_token_here

# REQUIRED: Application ID from Step 1.2
CLIENT_ID=your_application_id_here

# OPTIONAL: Your server ID for testing (recommended for development)
GUILD_ID=your_server_id_here

# REQUIRED: Server booster role ID
BOOSTER_ROLE_ID=your_booster_role_id

# REQUIRED: Premium member role ID  
PREMIUM_ROLE_ID=your_premium_role_id
```

### Step 3: Get Role IDs
1. **Enable Developer Mode in Discord**
   - User Settings → Advanced → Developer Mode ✅

2. **Get Server Booster Role ID**
   - Go to Server Settings → Roles
   - Right-click "Server Booster" role → Copy ID
   - Paste as BOOSTER_ROLE_ID

3. **Create and Get Premium Role ID**
   - Server Settings → Roles → Create Role
   - Name it "Premium" or "VIP"
   - Set color and permissions as desired
   - Right-click the role → Copy ID
   - Paste as PREMIUM_ROLE_ID

### Step 4: Optional Configuration
**Edit `config.json` if needed:**

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
    "work": 60,
    "coinflip": 2,
    "dice": 3,
    "slots": 5
  }
}
```

## 🚀 First Run

### Step 1: Deploy Commands
```bash
# Deploy slash commands to Discord
npm run deploy-commands

# Expected output:
# Started refreshing application (/) commands.
# Successfully reloaded application (/) commands.
```

### Step 2: Start Bot
```bash
# Production mode
npm start

# Development mode (auto-restart on changes)
npm run dev

# Expected output:
# ✅ Luxury Kingdom Bot is ready! Logged in as Wonder Bot#1234
# ✅ Loaded drop channels for 0 guilds
# 🎯 Started global drop interval
```

### Step 3: Verify Bot Status
1. **Check Discord Server**
   - Bot should show as online
   - Green dot next to bot name

2. **Test Basic Command**
   ```
   /help
   ```
   - Should respond with help menu
   - If not, check console for errors

## 🏰 Server Setup

### Step 1: Configure Welcome System
```bash
# Set welcome channel
/setup welcome channel:#welcome-channel message:Welcome to our luxury kingdom! 👑

# Set introduction channel
/setup introduction channel:#introductions
```

### Step 2: Configure Drop System
```bash
# Add drop channels (can add multiple)
/drops setup channel:#general
/drops setup channel:#bot-commands

# Verify configuration
/drops list
```

### Step 3: Configure Leveling Rewards (Optional)
```bash
# Set role rewards for level milestones
/level-role add type:overall level:10 role:@Active Member
/level-role add type:overall level:25 role:@Veteran
/level-role add type:overall level:50 role:@Legend

# View configured rewards
/level-role list
```

### Step 4: Test Core Features
```bash
# Test economy system
/balance
/daily
/work

# Test drop system (if configured)
/drops trigger channel:#general amount:100 rarity:common

# Test leveling system
/level
/rank type:overall

# Test games
/coinflip choice:heads amount:10
```

## ✅ Testing & Verification

### Functional Tests
```bash
# Economy System
/balance          # Should show 0 coins for new users
/daily            # Should give daily reward
/work             # Should give work reward
/leaderboard      # Should show empty or minimal data

# Drop System
/drops list       # Should show configured channels
/drops stats      # Should show empty stats initially
/drops mystats    # Should show no drops collected

# Leveling System
/level            # Should show level 1 in all categories
/rewards          # Should show available rewards

# Games
/coinflip choice:heads amount:10  # Should work if user has coins
/dice amount:10                   # Should work if user has coins
/slots amount:20                  # Should work if user has coins
```

### Error Testing
```bash
# Test error handling
/coinflip choice:heads amount:999999  # Should show insufficient funds
/daily                                # Should show cooldown after first use
/level @non_existent_user            # Should handle gracefully
```

### Performance Testing
```bash
# Check memory usage
# Monitor console output for memory usage reports

# Check response times
# Commands should respond within 2-3 seconds maximum

# Check database operations
# Enable DEBUG=true in .env for detailed logging
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Canvas Installation Errors
**Problem**: `npm install` fails on canvas package

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev libpixman-1-dev

# Try installing canvas separately
npm install canvas --force

# If still failing, try with Python 2.7
npm install --python=python2.7
```

#### 2. Bot Not Responding
**Problem**: Bot appears online but doesn't respond to commands

**Checklist**:
- [ ] Bot has correct permissions in server
- [ ] Slash commands were deployed (`npm run deploy-commands`)
- [ ] DISCORD_TOKEN is correct in `.env`
- [ ] Bot has "Use Slash Commands" permission
- [ ] No console errors during startup

#### 3. Database Errors
**Problem**: Database connection or write errors

**Solution**:
```bash
# Check file permissions
ls -la wonder.db

# Fix permissions if needed
chmod 664 wonder.db
chown $USER:$USER wonder.db

# If database is corrupted, delete and restart
rm wonder.db
npm start
```

#### 4. Role Detection Issues
**Problem**: Premium/booster bonuses not working

**Solution**:
- Verify role IDs are correct in `.env`
- Check that bot can see member roles
- Ensure bot has "View Server Members" permission

#### 5. Command Deployment Failures
**Problem**: Slash commands not appearing

**Solution**:
```bash
# Clear command cache and redeploy
rm -f deploy-commands.log
npm run deploy-commands

# Check bot permissions
# Ensure bot was invited with "applications.commands" scope
```

### Debug Mode
```env
# Enable debug logging in .env
DEBUG=true
NODE_ENV=development

# Restart bot to see detailed logs
npm start
```

### Log Analysis
```bash
# View recent logs
tail -f bot.log

# Search for specific errors
grep -i "error" bot.log
grep -i "database" bot.log
grep -i "permission" bot.log
```

## 🌐 Production Deployment

### Environment Setup
```env
# Production environment variables
NODE_ENV=production
DEBUG=false

# Remove test server ID for global commands
GUILD_ID=

# Use secure database path
DATABASE_PATH=/opt/wonderbot/data/wonder.db
```

### Process Management
```bash
# Install PM2 for process management
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'wonder-bot',
    script: 'src/index.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Security Considerations
```bash
# Set secure file permissions
chmod 600 .env
chmod 644 config.json
chmod 755 src/

# Create dedicated user (recommended)
sudo useradd -r -s /bin/false wonderbot
sudo chown -R wonderbot:wonderbot /opt/wonderbot
```

### Monitoring
```bash
# Monitor with PM2
pm2 status
pm2 logs wonder-bot
pm2 monit

# Set up log rotation
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 100M
pm2 set pm2-logrotate:retain 7
```

### Backup Strategy
```bash
# Create backup script
cat > backup.sh << EOF
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp wonder.db backups/wonder_db_$DATE.db
# Keep only last 30 days
find backups/ -name "wonder_db_*.db" -mtime +30 -delete
EOF

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

## 📞 Support

### Getting Help
1. **Check Documentation**: Review README.md and this guide
2. **Console Logs**: Check bot console for error messages
3. **Debug Mode**: Enable DEBUG=true for detailed logging
4. **Community**: Join our Discord support server
5. **Issues**: Report bugs on GitHub Issues

### Reporting Issues
**Include this information:**
- Operating system and version
- Node.js version (`node --version`)
- npm version (`npm --version`)
- Error messages (full stack trace)
- Steps to reproduce
- Configuration (without sensitive data)

---

**🎉 Congratulations! Your Wonder Discord Bot is now ready to transform your server into a luxury kingdom! 👑**