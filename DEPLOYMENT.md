# 🚀 Wonder Discord Bot - Complete Deployment Guide

## 📋 Overview

This guide provides comprehensive instructions for deploying the Wonder Discord Bot on any platform. The bot supports multiple deployment methods and environments.

## ⚡ Quick Start

### Universal Deployment (Recommended)
```bash
# Download and run the universal deployment script
python3 deploy.py

# Configure your Discord token
# Edit .env file and set: DISCORD_TOKEN=your_actual_token_here

# Start the bot
./start.sh     # Linux/macOS
start.bat      # Windows
python3 run.py # Manual start
```

## 🛠️ Platform-Specific Deployment

### 💻 Local Development

#### Prerequisites
- Python 3.8+ (recommended: 3.10+)
- Git (optional)
- 1GB+ RAM, 1GB+ storage

#### Setup
```bash
# Clone repository
git clone <repository_url>
cd wonder-discord-bot

# Use deployment script
python3 deploy.py

# Or manual installation
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Discord token

# Start bot
python3 run.py
```

### ☁️ Cloud Platform Deployment

#### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-bot-name

# Set environment variables
heroku config:set DISCORD_TOKEN=your_token_here

# Deploy
git push heroku main

# Uses Procfile: worker: python run.py
```

#### Railway
1. Connect GitHub repository to Railway
2. Set environment variable: `DISCORD_TOKEN=your_token`
3. Uses `railway.json` configuration
4. Deploy automatically on git push

#### Render
1. Connect GitHub repository to Render
2. Set as Background Worker service
3. Set environment variable: `DISCORD_TOKEN=your_token`
4. Uses `render.yaml` configuration

### 🐳 Docker Deployment

#### Standalone Docker
```bash
# Build image
docker build -t wonder-discord-bot .

# Run with environment file
docker run -d --env-file .env wonder-discord-bot

# Or with environment variable
docker run -d -e DISCORD_TOKEN=your_token wonder-discord-bot
```

#### Docker Compose
```bash
# Use the provided docker-compose.yml
docker-compose up -d

# Check logs
docker-compose logs -f wonder-bot
```

Docker Compose Configuration:
```yaml
version: '3.8'
services:
  wonder-bot:
    build: .
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
    restart: unless-stopped
    volumes:
      - ./data:/app/data
```

### 🖥️ VPS/Dedicated Server Deployment

#### Automated Installation (Linux)
```bash
# Download and run the automated installer
sudo bash install.sh
```

The installer will:
- Install Python 3.8+ and dependencies
- Create a dedicated user for the bot
- Set up systemd service
- Configure firewall
- Set up log rotation

#### Manual VPS Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install python3 python3-pip python3-venv git -y

# Clone repository
git clone <repository_url>
cd wonder-discord-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your configuration

# Test run
python3 run.py
```

#### Systemd Service Setup
```bash
# Copy service file
sudo cp wonder-bot.service /etc/systemd/system/

# Edit service file with correct paths
sudo nano /etc/systemd/system/wonder-bot.service

# Enable and start service
sudo systemctl enable wonder-bot
sudo systemctl start wonder-bot

# Check status
sudo systemctl status wonder-bot
```

### 🏠 Pterodactyl Panel Deployment

#### Setup Steps
1. **Create Python Server**
   - Choose Python 3.8+ environment
   - Allocate minimum 1GB RAM

2. **Upload Files**
   - Upload entire bot directory
   - Ensure file permissions are correct

3. **Configure Environment**
   - Set startup command: `python3 run.py`
   - Add environment variables:
     - `DISCORD_TOKEN`: Your Discord bot token

4. **Start Server**
   ```bash
   # Use provided Pterodactyl script
   ./start_pterodactyl.sh
   
   # Or direct command
   python3 run.py
   ```

#### Pterodactyl Troubleshooting
```bash
# Fix permissions
chmod +x start_pterodactyl.sh
chmod +x start.sh

# Install dependencies manually
pip3 install --break-system-packages -r requirements.txt

# Test setup
python3 setup_pterodactyl.py
```

### 🌐 Other Hosting Platforms

#### Repl.it
1. Import from GitHub
2. Set environment variable: `DISCORD_TOKEN`
3. Run: `python3 run.py`

#### Glitch
1. Import from GitHub
2. Add `.env` file with token
3. Start command: `python3 run.py`

#### DigitalOcean App Platform
1. Connect GitHub repository
2. Set as Worker service
3. Configure environment variables
4. Deploy automatically

## ⚙️ Environment Configuration

### Required Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | ✅ | Your Discord bot token |

### Optional Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `PREMIUM_ROLE_ID` | None | Premium role ID for bonuses |
| `BOOSTER_ROLE_ID` | None | Server booster role ID |
| `DB_TYPE` | sqlite | Database type (sqlite/mysql) |
| `DB_HOST` | localhost | MySQL host (if using MySQL) |
| `DB_PORT` | 3306 | MySQL port |
| `DB_NAME` | wonder_bot | MySQL database name |
| `DB_USER` | root | MySQL username |
| `DB_PASSWORD` | | MySQL password |
| `LOG_LEVEL` | INFO | Logging level |

### Environment File Template (.env)
```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here

# Optional Role IDs
PREMIUM_ROLE_ID=
BOOSTER_ROLE_ID=

# Database Configuration (Optional - uses SQLite by default)
# DB_TYPE=mysql
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=wonder_bot
# DB_USER=your_username
# DB_PASSWORD=your_password

# Logging
LOG_LEVEL=INFO
```

## 🗄️ Database Configuration

### SQLite (Default)
No additional configuration needed. The bot will create `wonder.db` automatically.

### MySQL Setup
1. **Configure MySQL in config.json:**
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

2. **Test Connection:**
```bash
python3 test_mysql_connection.py
```

3. **Migrate Data (if needed):**
```bash
python3 migrate_to_mysql.py
```

## 🔐 Discord Bot Setup

### 1. Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name your application

### 2. Create Bot
1. Go to "Bot" section
2. Click "Add Bot"
3. Copy the bot token
4. Enable required intents:
   - Server Members Intent
   - Message Content Intent

### 3. Bot Permissions
Required permissions:
- Send Messages
- Embed Links
- Add Reactions
- Use Slash Commands
- Manage Roles (for leveling)
- Manage Messages (for giveaways)
- Read Message History

### 4. Invite Bot
1. Go to OAuth2 → URL Generator
2. Select "bot" and "applications.commands"
3. Select required permissions
4. Use generated URL to invite bot

## 🧪 Validation & Testing

### Pre-Deployment Validation
```bash
# Validate deployment readiness
python3 validate_deployment.py

# Test bot functionality (no Discord connection)
python3 debug_bot.py

# Test specific components
python3 debug_advanced.py
```

### Post-Deployment Testing
```bash
# Check bot status
systemctl status wonder-bot  # Linux systemd

# View logs
tail -f bot.log
journalctl -u wonder-bot -f  # Linux systemd

# Test commands in Discord
w.help
/balance
w.daily
```

## 📊 Monitoring & Maintenance

### Log Management
```bash
# View real-time logs
tail -f bot.log

# Rotate logs (Linux)
sudo logrotate /etc/logrotate.d/wonder-bot

# Clear old logs
find /path/to/logs -name "*.log" -mtime +30 -delete
```

### Performance Monitoring
The bot includes built-in monitoring:
- Memory usage tracking
- Command execution timing
- Database operation metrics
- Error rate monitoring

### Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart bot
sudo systemctl restart wonder-bot  # Linux
```

## 🚨 Troubleshooting

### Common Issues

#### "Improper token has been passed"
**Solution:** 
1. Verify token in `.env` file
2. Regenerate token in Discord Developer Portal
3. Ensure no extra spaces in token

#### "Module not found" errors
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Use deployment script
python3 deploy.py
```

#### Bot not responding to commands
**Solution:**
1. Check bot permissions in Discord
2. Verify intents are enabled
3. Check bot status and logs
4. Ensure bot is online

#### Database connection errors
**Solution:**
```bash
# For SQLite
chmod 664 wonder.db

# For MySQL
python3 test_mysql_connection.py

# Reset database if corrupted
rm wonder.db  # SQLite only
python3 run.py  # Will recreate
```

#### Permission denied on scripts
**Solution:**
```bash
chmod +x start.sh
chmod +x start_pterodactyl.sh
chmod +x install.sh
```

### Debug Tools
The bot includes comprehensive debugging tools:

```bash
# Quick validation
python3 validate_deployment.py

# Full system test
python3 debug_bot.py

# Database testing
python3 test_mysql_connection.py

# Advanced diagnostics
python3 debug_advanced.py

# MySQL-specific debugging
python3 debug_mysql.py
```

### Performance Issues
1. **High memory usage:** Check for memory leaks in logs
2. **Slow response:** Monitor database performance
3. **Connection timeouts:** Verify network connectivity
4. **Rate limiting:** Check Discord API rate limits

## 🔒 Security Best Practices

### Token Security
- Never commit tokens to version control
- Use environment variables
- Rotate tokens regularly
- Restrict bot permissions to minimum required

### Server Security
- Keep system updated
- Use firewall
- Regular backups
- Monitor logs for suspicious activity

### Database Security
- Use strong passwords
- Enable SSL/TLS for MySQL
- Regular database backups
- Limit database user permissions

## 📈 Scaling & Load Balancing

### Single Server Optimization
- Use MySQL for better performance
- Enable connection pooling
- Optimize database queries
- Monitor resource usage

### Multi-Server Deployment
- Use external MySQL database
- Load balance multiple bot instances
- Implement Redis for shared caching
- Use container orchestration (Kubernetes)

## 🎯 Production Checklist

### Pre-Deployment
- [ ] Bot token configured
- [ ] Environment variables set
- [ ] Database configured and tested
- [ ] Bot permissions verified
- [ ] Validation tests passed

### Post-Deployment
- [ ] Bot responds to commands
- [ ] Database operations working
- [ ] Logs are clean
- [ ] Monitoring enabled
- [ ] Backups configured

### Ongoing Maintenance
- [ ] Regular updates
- [ ] Log monitoring
- [ ] Performance monitoring
- [ ] Security updates
- [ ] Database maintenance

---

## 🆘 Support

If you encounter issues during deployment:

1. **Check the logs:** `tail -f bot.log`
2. **Run diagnostics:** `python3 debug_bot.py`
3. **Verify configuration:** `python3 validate_deployment.py`
4. **Test connectivity:** `python3 test_mysql_connection.py` (MySQL)
5. **Review Discord setup:** Check bot permissions and intents

For additional help, review the troubleshooting section in the main README.md file.

---

**🎉 Deployment successful? Your Wonder Discord Bot is ready to transform your server! ✨**