# 🛡️ Wonder Discord Bot - Admin Guide

## 📋 Overview

This guide provides comprehensive information for server administrators on managing and configuring the Wonder Discord Bot. The bot includes powerful admin tools for user management, system configuration, and server customization.

## 🔐 Admin Permissions

### Required Permissions
To use admin commands, you must have one of the following Discord permissions:
- `Administrator`
- `Manage Server`

### Command Categories
- **🎯 Leveling Management**: Control XP and leveling systems
- **💰 Economy Management**: Manage user currency and transactions
- **🪙 Drop System**: Configure WonderCoins drop channels
- **🎉 Giveaway Management**: Create and manage giveaways
- **⚙️ System Configuration**: Bot settings and toggles

## 🎯 Leveling System Management

### Category Control
Administrators can enable or disable entire leveling categories per server:

```bash
# Enable/Disable Categories
w.toggle-category text true      # Enable text leveling
w.toggle-category voice false    # Disable voice leveling
w.toggle-category role true      # Enable role leveling
w.toggle-category overall false  # Disable overall leveling
```

**Available Categories:**
- `text` - XP from chat messages
- `voice` - XP from voice channel activity
- `role` - XP from community activities
- `overall` - Combined XP from all categories

### User XP Management

#### Set User XP
Set a user's XP to a specific amount:
```bash
w.set-user-xp @user text 1000      # Set text XP to 1000
w.set-user-xp @user voice 500      # Set voice XP to 500
w.set-user-xp @user role 750       # Set role XP to 750
w.set-user-xp @user overall 2000   # Set overall XP to 2000
```

#### Add/Remove User XP
Add or remove XP from a user (use negative numbers to remove):
```bash
w.add-user-xp @user text 100       # Add 100 text XP
w.add-user-xp @user voice -50      # Remove 50 voice XP
w.add-user-xp @user role 200       # Add 200 role XP
w.add-user-xp @user overall -100   # Remove 100 overall XP
```

#### Reset User XP
Reset a user's XP in specific categories or all categories:
```bash
w.reset-user-xp @user text         # Reset only text XP
w.reset-user-xp @user voice        # Reset only voice XP
w.reset-user-xp @user all          # Reset all XP categories
```

**Interactive Confirmation:** Reset commands include a confirmation dialog for safety.

### Level Roles System

The bot features a comprehensive 29-role system:

#### Text Chat Roles (6 roles)
- Level 5: Text Chatter
- Level 10: Conversationalist (10% XP bonus)
- Level 20: Text Master (15% XP bonus)
- Level 30: Chat Legend (20% XP bonus)
- Level 40: Text Virtuoso (25% XP bonus)
- Level 50: Supreme Wordsmith (30% XP bonus)

#### Voice Activity Roles (6 roles)
- Level 5: Voice Newcomer
- Level 10: Voice Regular (10% voice XP bonus)
- Level 20: Voice Expert (15% voice XP bonus)
- Level 30: Voice Master (20% voice XP bonus)
- Level 40: Voice Virtuoso (25% voice XP bonus)
- Level 50: Voice Legend (30% voice XP bonus)

#### Community Role Roles (6 roles)
- Level 5: Helper
- Level 10: Community Member (10% role XP bonus)
- Level 20: Community Leader (15% role XP bonus)
- Level 30: Community Hero (20% role XP bonus)
- Level 40: Community Champion (25% role XP bonus)
- Level 50: Community Legend (30% role XP bonus)

#### Overall Progress Roles (5 roles)
- Level 10: Wonder Apprentice (5% overall bonus)
- Level 20: Wonder Adept (10% overall bonus)
- Level 30: Wonder Expert (15% overall bonus)
- Level 40: Wonder Master (20% overall bonus)
- Level 50: Wonder Grandmaster (25% overall bonus)

#### Prestige System (5 levels)
- ★ Wonder Prestige I (35% XP bonus)
- ★★ Wonder Prestige II (40% XP bonus)
- ★★★ Wonder Prestige III (45% XP bonus)
- ★★★★ Wonder Prestige IV (50% XP bonus)
- ★★★★★ Wonder Prestige V (60% XP bonus)

## 💰 Economy System Management

### User Currency Management

#### Set User Currency
Set a user's WonderCoins balance to a specific amount:
```bash
w.set-user-currency @user 5000     # Set balance to 5000 coins
w.set-user-currency @user 0        # Reset balance to 0
```

#### Add/Remove User Currency
Add or remove WonderCoins from a user (use negative numbers to remove):
```bash
w.add-user-currency @user 1000     # Add 1000 coins
w.add-user-currency @user -500     # Remove 500 coins
```

**Safety Features:**
- Balance cannot go below 0
- Commands show old balance, new balance, and change amount
- Validation prevents invalid amounts

### Economy System Features
- **Daily Rewards**: 100 WonderCoins every 24 hours
- **Work System**: 50 WonderCoins every hour
- **Role Bonuses**: Boosters and Premium members get multipliers
- **Transaction History**: All transactions are logged
- **Leaderboards**: Server-wide wealth rankings

## 🪙 WonderCoins Drop System

### Drop Channel Management

#### Add Drop Channels
Configure channels to receive automatic WonderCoins drops:
```bash
w.adddrops #general              # Add using channel mention
w.adddrops 123456789            # Add using channel ID
```

#### Remove Drop Channels
Remove channels from the drop system:
```bash
w.removedrops #general          # Remove using channel mention
w.removedrops 123456789         # Remove using channel ID
```

#### List Drop Channels
View all configured drop channels:
```bash
w.dropchannels                  # List all drop channels
```

### Drop Configuration

#### Force Manual Drops
Trigger manual drops for testing or special events:
```bash
w.forcedrop                     # Force a normal drop
w.forcedrop 500 epic           # Force specific amount and rarity
```

#### Configure Drop Settings
Adjust drop system parameters:
```bash
w.configdrops interval 45       # Set drop interval to 45 minutes
w.configdrops rarity_mult 2.0   # Set rarity multiplier
```

### Drop System Features

#### Rarity System
| Rarity | Chance | Multiplier | Example Amount |
|--------|--------|------------|----------------|
| Common | 84% | 1x | 150 coins |
| Rare | 10% | 3x | 450 coins |
| Epic | 5% | 5x | 750 coins |
| Legendary | 1% | 10x | 1,500 coins |

#### Collection Methods
- **💰 Standard Collection**: Normal coin collection
- **⚡ Quick Grab**: First 3 users get 2x multiplier
- **🍀 Lucky Grab**: 30% chance for 1.5x bonus

#### Timing System
- **Global Drops**: Every 30 minutes to 3 hours across all servers
- **Smart Distribution**: Automatic drop distribution across configured channels
- **Multi-Server Support**: Centralized system for all servers

## 🎉 Giveaway Management

### Creating Giveaways

#### Advanced Giveaway Creation
```bash
w.giveaway-create "Discord Nitro" 1h --winners 3 --required-role @Member
```

**Parameters:**
- **Prize**: Description of the prize
- **Duration**: Time format (s/m/h/d/w)
- **Winners**: Number of winners (1-10)
- **Requirements**: Role requirements, account age, etc.

#### Quick Giveaway Creation
```bash
w.quickgiveaway 60 1 "100 WonderCoins"
```

**Format:** `duration` `winners` `prize`

### Managing Giveaways

#### End Giveaways
```bash
w.giveaway-end 123456           # End giveaway by ID
```

#### Reroll Winners
```bash
w.giveaway-reroll 123456 2      # Reroll 2 new winners
```

#### List Active Giveaways
```bash
w.giveaway-list                 # Show all active giveaways
```

#### Giveaway Information
```bash
w.giveaway-info 123456          # Get detailed giveaway info
```

### Giveaway Features

#### Entry System
- **Weighted Entries**: Premium (3x), Boosters (2x), Regular (1x)
- **Role Requirements**: Required roles, forbidden roles, bypass roles
- **Account Verification**: Minimum account age requirements
- **Winner Cooldowns**: 7-day cooldown prevents frequent winners

#### Advanced Options
- **Multiple Winners**: Up to 10 winners per giveaway
- **Flexible Duration**: Support for complex time formats
- **Auto-Management**: Self-managing with notifications
- **Reroll Protection**: Previous winners excluded from rerolls

## ⚙️ System Configuration

### Input Parsing Security
All admin commands use secure parsing that only accepts:
- **User mentions**: `@username`
- **User IDs**: `123456789`
- **Role mentions**: `@role`
- **Role IDs**: `987654321`
- **Channel mentions**: `#channel`
- **Channel IDs**: `111222333`

**Security Note:** Name-based parsing is disabled to prevent targeting wrong users/roles/channels with similar names.

### Permission-Based Help
The help system automatically adjusts based on user permissions:
- **Regular Users**: See only basic commands
- **Administrators**: See admin commands section
- **Bot Owners**: See all commands including owner-only features

### Error Handling
Comprehensive error handling provides:
- **Detailed error messages** with specific guidance
- **Usage examples** for correct command syntax
- **Parameter validation** with acceptable ranges
- **Permission checks** with clear requirements

Example error message:
```
❌ Command Error
**Missing required argument for `set-user-xp` command**
Missing parameter: `category`

📝 Usage: `w.set-user-xp <user> <category> <amount>`
📋 Description: Set user XP to a specific amount
⚙️ Parameters:
• user (required): User mention or ID
• category (required): text, voice, role, or overall
• amount (required): XP amount (0-999999)
```

## 📊 Monitoring & Analytics

### User Statistics
View comprehensive user data:
- XP progression across all categories
- Currency balance and transaction history
- Gambling statistics and win/loss ratios
- Item inventory and usage history

### Server Analytics
Monitor server-wide metrics:
- Total currency in circulation
- Most active users by category
- Drop statistics and collection rates
- Giveaway participation and winner distribution

### Performance Monitoring
Built-in monitoring includes:
- Command execution timing
- Database operation metrics
- Memory usage tracking
- Error rate monitoring

## 🔧 Advanced Administration

### Database Management
For advanced users with database access:

#### SQLite (Default)
- Database file: `wonder.db`
- Automatic backups recommended
- Performance suitable for small-medium servers

#### MySQL (Optional)
- Better performance for large servers
- Connection pooling (1-10 connections)
- Advanced query optimization
- Professional backup solutions

#### Migration Tools
```bash
# Test MySQL connection
python3 test_mysql_connection.py

# Migrate from SQLite to MySQL
python3 migrate_to_mysql.py

# Validate database integrity
python3 debug_mysql.py
```

### Bot Configuration
Advanced configuration in `config.json`:

```json
{
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
    "slots": 5
  }
}
```

## 🚨 Emergency Procedures

### Bot Troubleshooting
If the bot becomes unresponsive:
1. Check bot status: `systemctl status wonder-bot`
2. Review logs: `tail -f bot.log`
3. Restart bot: `systemctl restart wonder-bot`
4. Validate configuration: `python3 validate_deployment.py`

### Data Recovery
For data loss scenarios:
1. **Database Corruption**: Restore from backup
2. **Config Issues**: Use `config.json.backup`
3. **User Data Loss**: Check transaction logs for recovery

### Security Incidents
If security is compromised:
1. Regenerate Discord bot token immediately
2. Review audit logs for unauthorized changes
3. Check database for suspicious transactions
4. Reset admin permissions if necessary

## 📈 Best Practices

### Regular Maintenance
- **Weekly**: Review error logs and performance metrics
- **Monthly**: Database backup and cleanup
- **Quarterly**: Security audit and permission review
- **As needed**: Bot updates and feature additions

### User Management
- Set clear guidelines for XP farming prevention
- Monitor for unusual currency accumulation patterns
- Regular review of giveaway winners for fairness
- Communicate changes to leveling system clearly

### System Optimization
- Monitor database size and performance
- Regular cleanup of old transaction data
- Optimize drop channel distribution
- Monitor bot resource usage

### Community Engagement
- Use drop system for special events
- Create themed giveaways for milestones
- Recognize top contributors with XP bonuses
- Gather feedback on system changes

## 🎯 Quick Reference

### Essential Commands
```bash
# User Management
w.set-user-xp @user text 1000
w.add-user-currency @user 500
w.reset-user-xp @user all

# Drop System
w.adddrops #channel
w.forcedrop 500 epic
w.dropchannels

# Giveaways
w.quickgiveaway 1h 1 "Prize"
w.giveaway-end 123456
w.giveaway-list

# System
w.toggle-category text false
w.help
```

### Keyboard Shortcuts
- Use tab completion for user/channel mentions
- Use up arrow to repeat last command
- Use Discord's built-in slash command completion

---

## 🆘 Admin Support

For additional help with administration:

1. **Bot Help**: Use `w.help` to see all available commands
2. **Error Logs**: Check `bot.log` for detailed error information
3. **Validation**: Run `python3 debug_bot.py` for system diagnostics
4. **Documentation**: Refer to README.md for comprehensive information

Remember: With great power comes great responsibility. Use admin commands thoughtfully to create a positive and engaging community experience!

---

**🛡️ Master your server with Wonder Discord Bot's powerful admin tools! ✨**