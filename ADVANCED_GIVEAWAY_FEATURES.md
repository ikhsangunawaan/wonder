# 🎉 Advanced Giveaway System - Complete Feature Guide

## Overview
The Wonder Discord Bot now features a comprehensive, advanced giveaway system with extensive customization options, role-based requirements, automatic winner selection, and administrative controls.

## 🚀 Quick Start

### Simple Giveaway
```
w.quickgiveaway 1h 1 Discord Nitro
```

### Advanced Giveaway
```
w.giveaway create "Premium Game" 2d --winners 3 --channel #giveaways --required-roles @Members
```

## 📋 Command Reference

### Main Commands

#### `w.giveaway` - Main giveaway command group
Shows the help menu with all available subcommands and options.

#### `w.giveaway create <prize> <duration> [options]` - Create Advanced Giveaway
Create a giveaway with comprehensive customization options.

**Examples:**
```bash
# Basic giveaway
w.giveaway create "Steam Gift Card" 1d

# Advanced giveaway with multiple options
w.giveaway create "Discord Nitro" 2d --winners 3 --channel #giveaways --required-roles @Members,@Verified --min-age 30 --winner-role @Winner

# Restricted giveaway
w.giveaway create "VIP Prize" 12h --forbidden-roles @Muted --min-messages 100 --bypass-roles @VIP,@Moderator
```

#### `w.giveaway end <giveaway_id>` - End Giveaway Manually
Manually end an active giveaway before its scheduled end time.

```bash
w.giveaway end 123
```

#### `w.giveaway reroll <giveaway_id> [new_winner_count]` - Reroll Winners
Reroll winners for a completed giveaway, optionally changing the number of winners.

```bash
# Reroll with same number of winners
w.giveaway reroll 123

# Reroll with different number of winners
w.giveaway reroll 123 5
```

#### `w.giveaway list [all]` - List Giveaways
List active giveaways or all giveaways in the server.

```bash
# Show active giveaways only
w.giveaway list

# Show all giveaways (active, completed, cancelled)
w.giveaway list all
```

#### `w.quickgiveaway <duration> <winners> <prize>` - Quick Giveaway
Create a simple giveaway without advanced options for quick setup.

```bash
w.quickgiveaway 6h 2 "2x Discord Nitro"
```

## 🛠️ Advanced Options

### Duration Formats
- `30s` - 30 seconds
- `15m` - 15 minutes
- `2h` - 2 hours
- `1d` - 1 day
- `1w` - 1 week

### Channel Selection
```bash
--channel #giveaways
--channel #announcements
```

### Winner Configuration
```bash
--winners 3              # Number of winners (default: 1)
--winner-role @Winner    # Role assigned to winners
```

### Role Requirements
```bash
--required-roles @Members,@Verified    # Users must have one of these roles
--forbidden-roles @Muted,@Banned      # Users cannot have these roles
--bypass-roles @VIP,@Moderator        # These roles bypass all requirements
```

### Account & Activity Requirements
```bash
--min-age 30           # Minimum account age in days
--min-messages 50      # Minimum messages sent (if tracking enabled)
```

### Custom Description
```bash
--description "Special holiday giveaway for our amazing community!"
```

## 🎯 Features

### 🔒 Advanced Requirements System
- **Role Requirements**: Require specific roles to enter
- **Role Restrictions**: Prevent users with certain roles from entering
- **Account Age**: Minimum account age requirements
- **Message Requirements**: Minimum message count (if tracking enabled)
- **Bypass Roles**: Special roles that ignore all requirements
- **Winner Cooldown**: Prevent recent winners from entering new giveaways

### 🏆 Winner Management
- **Weighted Entries**: Premium/Booster members get better odds
- **Multiple Winners**: Support for multiple winners per giveaway
- **Winner Roles**: Automatically assign roles to winners
- **Reroll System**: Reroll winners excluding previous winners
- **DM Notifications**: Automatic DM notifications to winners

### 📊 Administrative Controls
- **Manual End**: End giveaways early
- **List Management**: View all giveaways with status
- **Permission System**: Host/Admin permissions for management
- **Tracking**: Complete giveaway history and statistics

### 🎨 User Experience
- **Rich Embeds**: Beautiful, informative giveaway displays
- **Real-time Updates**: Live countdown and status updates
- **Entry Confirmation**: DM confirmations for entries
- **Error Handling**: Clear error messages for invalid entries
- **Reaction System**: Simple 🎉 reaction to enter

## 🗃️ Database Schema

### Giveaways Table
- Enhanced with role requirements, restrictions, and winner roles
- Tracks reroll count and completion status
- Stores comprehensive metadata

### Giveaway Entries Table
- Weighted entry system
- User tracking with entry timestamps

### Giveaway Winners Table
- Complete winner history
- Reroll tracking
- Winner position tracking

## 🔧 Configuration

### Config Options (config.json)
```json
{
  "giveaways": {
    "maxDuration": 10080,
    "maxWinners": 10,
    "winnerCooldown": 10080,
    "odds": {
      "premium": 3.0,
      "booster": 2.0
    },
    "restrictions": {
      "accountAgeMin": 7,
      "premiumBypass": true
    }
  }
}
```

## 🚦 Permission Requirements

### User Permissions
- **Enter Giveaways**: No special permissions required (unless restricted)
- **View Giveaways**: All users can see active giveaways

### Administrative Permissions
- **Create Giveaways**: `Manage Server` permission
- **End Giveaways**: `Manage Server` permission or giveaway host
- **Reroll Giveaways**: `Manage Server` permission or giveaway host
- **List All Giveaways**: `Manage Server` permission

## 📈 Advanced Examples

### 1. Community Event Giveaway
```bash
w.giveaway create "Community Event Prize Pack" 7d --winners 5 --channel #events --required-roles @Community --min-age 14 --winner-role @EventWinner --description "Thank you for being part of our amazing community!"
```

### 2. Booster Exclusive Giveaway
```bash
w.giveaway create "Nitro Booster Exclusive" 3d --required-roles @Nitro_Booster --winners 2 --winner-role @VIP --description "Exclusive giveaway for our server boosters!"
```

### 3. New Member Welcome Giveaway
```bash
w.giveaway create "Welcome Package" 24h --forbidden-roles @Muted --min-age 1 --bypass-roles @Verified --description "Welcome to our server! New members can win a starter package!"
```

### 4. High-Value Restricted Giveaway
```bash
w.giveaway create "Premium Gaming Setup" 14d --winners 1 --required-roles @Trusted --forbidden-roles @Warning,@Timeout --min-age 90 --min-messages 500 --bypass-roles @VIP,@Moderator --winner-role @GrandWinner
```

## 🎊 Winner Selection Process

1. **Entry Collection**: All valid entries are collected based on requirements
2. **Weight Calculation**: Entries are weighted based on user roles (Premium/Booster get better odds)
3. **Random Selection**: Weighted random selection ensures fairness while giving bonuses
4. **Duplicate Prevention**: Same user cannot win multiple positions in one giveaway
5. **Role Assignment**: Winner roles are automatically assigned if specified
6. **Notifications**: Winners receive DM notifications and are mentioned in the announcement

## 🔄 Reroll System

The reroll system allows for fair re-selection of winners:
- Previous winners are excluded from new selection
- Can change the number of winners during reroll
- Maintains all original entry requirements
- Tracks reroll history for transparency

## 📱 Mobile-Friendly

All giveaway embeds and interactions are optimized for mobile Discord users:
- Clear, readable formatting
- Intuitive emoji reactions
- Concise but comprehensive information display

## 🛡️ Security Features

- **Permission Validation**: All commands check appropriate permissions
- **Input Sanitization**: All inputs are validated and sanitized
- **Rate Limiting**: Built-in protections against spam
- **Error Handling**: Graceful error handling for all edge cases

## 🎯 Integration

The giveaway system integrates seamlessly with other bot features:
- **Role Management**: Works with existing role systems
- **Economy System**: Can integrate with WonderCoins for prizes
- **Leveling System**: Can use level requirements (future feature)
- **Moderation**: Respects server moderation statuses

---

This advanced giveaway system provides everything needed for running successful, fair, and engaging giveaways in Discord servers of any size. From simple community events to complex promotional campaigns, the system scales to meet any requirement while maintaining ease of use and administrative control.