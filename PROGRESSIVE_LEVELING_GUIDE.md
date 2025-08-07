# 🎯 Progressive Leveling System - Complete Guide

Wonder Discord Bot's new progressive leveling system provides a balanced, scalable approach to user engagement with customizable role rewards every 5 levels up to level 100.

## 📊 System Overview

### Key Features
- **Progressive XP Requirements**: XP needed increases intelligently across level ranges
- **Role Rewards Every 5 Levels**: Configurable roles at levels 5, 10, 15, 20, 25... up to 100
- **Manual Role Configuration**: Admins can configure roles through Discord commands
- **Balanced Progression**: Carefully tuned XP formula prevents inflation while maintaining engagement
- **Level Cap**: Maximum level 100 with 20 possible role rewards

### XP Formula Breakdown

The progressive XP system uses different scaling across level ranges:

| Level Range | Base XP | Exponent | Example (Level 25) |
|-------------|---------|----------|--------------------|
| 1-10        | 100     | 1.2      | 229 XP for Level 2 |
| 11-30       | 150     | 1.3      | 9,849 XP for Level 25 |
| 31-60       | 200     | 1.4      | 47,817 XP for Level 50 |
| 61-100      | 300     | 1.5      | 300,000 XP for Level 100 |

### Milestone XP Requirements

| Level | XP This Level | Total XP Required |
|-------|---------------|-------------------|
| 5     | 689           | 1,818             |
| 10    | 1,584         | 7,901             |
| 25    | 9,849         | 105,379           |
| 50    | 47,817        | 878,538           |
| 75    | 194,855       | 3,959,504         |
| 100   | 300,000       | 10,166,443        |

## 🎮 User Commands

### Basic Commands

#### `w.progressive-rank` (aliases: `prank`, `plevel`)
Check your progressive leveling stats with detailed progress information.

**Example:**
```
w.progressive-rank @username
```

**Features:**
- Current level and total XP
- Progress bar and percentage
- XP needed for next level
- Next role level information
- Current role rewards

#### `w.xp-calculator` (alias: `xp-calc`)
Calculate XP requirements for any level from 1-100.

**Example:**
```
w.xp-calculator 50
```

**Output:**
- Total XP required for target level
- XP needed for that specific level
- XP needed for next level
- Role reward information (if applicable)
- Milestone information

## 🛡️ Admin Commands

### Role Configuration Commands

#### `w.level-role-set`
Configure a role reward for a specific level (Admin only).

**Syntax:**
```
w.level-role-set <level> <@role> [description]
```

**Examples:**
```
w.level-role-set 5 @Newcomer "First milestone achievement!"
w.level-role-set 25 @Veteran "Quarter-century club member"
w.level-role-set 50 @Elite "Halfway to perfection"
```

**Requirements:**
- Level must be multiple of 5 (5, 10, 15, 20, 25... 100)
- Bot role must be higher than target role
- Administrator permission required

#### `w.level-role-remove`
Remove a role reward from a specific level (Admin only).

**Syntax:**
```
w.level-role-remove <level>
```

**Example:**
```
w.level-role-remove 10
```

#### `w.level-roles-list`
List all configured level roles for the server.

**Usage:**
```
w.level-roles-list
```

**Output:**
- All configured roles by level
- XP requirements for each
- Role descriptions
- Status (active/deleted roles)

## ⚙️ Setup Guide

### 1. Prerequisites
- Bot must have Administrator permissions or role management permissions
- Bot's role must be positioned above all level roles in the server hierarchy

### 2. Initial Configuration

1. **Create Level Roles**
   Create Discord roles for the levels you want to reward:
   ```
   @Level 5    - Newcomer
   @Level 10   - Regular  
   @Level 15   - Active Member
   @Level 25   - Veteran
   @Level 50   - Elite
   @Level 100  - Legendary
   ```

2. **Position Bot Role**
   Move the bot's role above all level roles in Server Settings > Roles

3. **Configure Role Rewards**
   ```
   w.level-role-set 5 @Newcomer "Welcome to the community!"
   w.level-role-set 10 @Regular "Double digits achieved!"
   w.level-role-set 15 @Active Member "Active community participant"
   w.level-role-set 25 @Veteran "Quarter-century milestone"
   w.level-role-set 50 @Elite "Halfway to maximum level"
   w.level-role-set 100 @Legendary "Maximum level achieved!"
   ```

### 3. Verification

Check your configuration:
```
w.level-roles-list
w.xp-calculator 5
w.progressive-rank
```

## 📈 XP Gain System

### Text Message XP
- **Base XP**: 15 per message
- **Bonus XP**: 0-10 random bonus
- **Cooldown**: 1 minute between XP gains
- **Total Range**: 15-25 XP per message

### Multipliers
- **Premium/VIP Role**: +50% XP bonus
- **Server Booster**: +25% XP bonus
- **Multipliers Stack**: Premium + Booster = +75% total

### Example Progression
With average XP gain of 20 per message:

| Level | Messages Needed | Estimated Time* |
|-------|-----------------|-----------------|
| 5     | ~91 messages    | 1-2 weeks      |
| 10    | ~395 messages   | 1 month        |
| 25    | ~5,269 messages | 6 months       |
| 50    | ~43,927 messages| 2+ years       |
| 100   | ~508,322 messages| 10+ years      |

*Based on moderate activity (10-20 messages/day)

## 🔧 Advanced Configuration

### Custom Role Descriptions
Add meaningful descriptions to your roles:
```
w.level-role-set 25 @Veteran "Dedicated community member who has shown consistent engagement and helpfulness to newcomers"
```

### Role Hierarchy Planning
Plan your role progression to match your community:

**Example Gaming Server:**
- Level 5: @Noob "Learning the ropes"
- Level 15: @Player "Getting comfortable"
- Level 30: @Gamer "Knows their way around"
- Level 50: @Pro "Skilled and experienced"
- Level 75: @Expert "Master of the game"
- Level 100: @Legend "Absolute legend"

**Example Study Server:**
- Level 10: @Student "Active learner"
- Level 25: @Scholar "Dedicated student"
- Level 50: @Researcher "Advanced knowledge"
- Level 75: @Professor "Teaching others"
- Level 100: @Master "Subject matter expert"

## 🎨 Role Rewards Best Practices

### Role Design
1. **Progressive Colors**: Use color gradients (blue → purple → gold)
2. **Clear Hierarchy**: Make progression visually obvious
3. **Meaningful Names**: Reflect achievement and status

### Permissions Strategy
Consider granting additional permissions with higher roles:
- Level 25+: Image/link permissions in specific channels
- Level 50+: Voice activity permissions
- Level 75+: Temporary moderation helper permissions

### Special Milestone Rewards
- **Level 50**: Special announcement in dedicated channel
- **Level 75**: Custom nickname permissions
- **Level 100**: Hall of Fame mention + special privileges

## 📊 Monitoring & Analytics

### View Server Statistics
```
w.level-roles-list    # See all configured roles
w.progressive-rank    # Individual progress
```

### Role Member Counts
Check how many users have each role to assess progression balance.

### Adjustment Recommendations
- If too many users reach high levels quickly: Consider increasing XP requirements
- If progression is too slow: Review XP multipliers or add bonus events
- If role distribution is uneven: Adjust role level spacing

## 🔍 Troubleshooting

### Common Issues

**"Role Position Error"**
- Solution: Move bot role above target role in server settings

**"Invalid Level"**
- Solution: Only use multiples of 5 (5, 10, 15, 20, etc.)

**"Permission Denied"**
- Solution: User needs Administrator permission

**"Role Not Assigned"**
- Solution: Check bot permissions and role hierarchy

### Database Issues
If using MySQL and getting table errors, ensure the `server_settings` table exists:
```sql
CREATE TABLE server_settings (
    guild_id VARCHAR(255) PRIMARY KEY,
    settings JSON
);
```

## 🚀 Migration from Old System

### Step 1: Backup Current Data
Export current level data before switching systems.

### Step 2: Configure New Roles
Set up progressive roles using the new commands.

### Step 3: Gradual Transition
- Run both systems temporarily
- Announce the change to users
- Provide migration timeline

### Step 4: Complete Switch
- Disable old leveling system
- Enable progressive leveling in bot configuration
- Update help documentation

## 📚 Integration Examples

### Bot Status Updates
```python
# Update bot status with leveling info
activity = discord.Activity(
    type=discord.ActivityType.watching,
    name=f"Progressive Leveling • Max Level 100"
)
```

### Level-Up Announcements
The system automatically sends rich embeds when users level up, including:
- Achievement celebration
- Role reward notifications
- Progress to next milestone

### Role Assignment
Automatic role assignment happens when users reach role levels, with proper error handling for permission issues.

---

## 🌟 Conclusion

The Progressive Leveling System provides a balanced, engaging experience that can grow with your community. With 20 configurable role levels and intelligent XP scaling, it offers years of progression while maintaining active engagement.

**Key Benefits:**
- ✅ Balanced progression curve
- ✅ Flexible role configuration
- ✅ Admin-friendly management
- ✅ Automatic role assignment
- ✅ Detailed progress tracking
- ✅ Performance optimized

Ready to level up your Discord server? Start configuring your progressive leveling system today!

---

*For technical support or feature requests, please refer to the main bot documentation or contact the development team.*