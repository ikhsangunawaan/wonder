# MySQL Database Setup for Wonder Discord Bot

This guide will help you connect your Wonder Discord Bot to the MySQL database with the configuration you provided.

## 🗂️ What Was Changed

I've successfully updated your Discord bot to support MySQL connections. Here's what was modified:

### ✅ Configuration Added
- **MySQL settings** added to `config.json` with your database credentials
- **Database type** set to "mysql" to enable MySQL usage

### ✅ Dependencies Updated  
- **aiomysql** and **PyMySQL** added to `requirements.txt`
- These provide async MySQL connectivity for Python

### ✅ Database Layer Updated
- **New MySQL adapter** created in `src/mysql_database.py`
- **Main database class** updated to use MySQL when configured
- **Automatic fallback** to SQLite when MySQL isn't configured

### ✅ Migration Tools Created
- **Migration script** (`migrate_to_mysql.py`) to transfer existing data
- **Connection test** (`test_mysql_connection.py`) to verify setup

## 📋 Your Database Configuration

The following MySQL configuration has been set up based on your image:

```json
{
  "database": {
    "type": "mysql",
    "host": "mc.anjas.id",
    "port": 3306,
    "database": "s1056_wonder_server",
    "username": "u1056_f489WrV7JK",
    "password": "9FG=AN*P7C5@BG2m6Aq02Id",
    "charset": "utf8mb4",
    "autocommit": true,
    "pool_settings": {
      "minsize": 1,
      "maxsize": 10
    }
  }
}
```

## 🚀 Setup Steps

### 1. Install MySQL Dependencies

First, install the required Python packages:

```bash
# If using pip directly
pip install aiomysql PyMySQL

# If using virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Test MySQL Connection

Run the connection test to verify everything works:

```bash
python test_mysql_connection.py
```

You should see:
```
🚀 Wonder Discord Bot - MySQL Connection Test
==============================================
🔧 Testing MySQL connection...
🏠 Host: mc.anjas.id
🗄️  Database: s1056_wonder_server
👤 Username: u1056_f489WrV7JK
✅ MySQL connection successful!

🎉 Connection test passed!
💡 You can now run the migration script: python migrate_to_mysql.py
```

### 3. Migrate Existing Data (Optional)

If you have existing SQLite data to migrate:

```bash
python migrate_to_mysql.py
```

This will:
- Create all MySQL tables
- Transfer data from SQLite to MySQL
- Verify the migration was successful

### 4. Run Your Bot

Your bot will now automatically use MySQL:

```bash
python run.py
```

## 🔧 Troubleshooting

### Connection Issues

If you get connection errors:

1. **Check firewall**: Ensure port 3306 is accessible
2. **Verify credentials**: Double-check username/password
3. **Test host connectivity**: Try `ping mc.anjas.id`
4. **Check MySQL server**: Ensure it's running and accessible

### Common Error Messages

**"Access denied for user"**
- Verify username and password in config.json
- Check if user has permissions for the database

**"Can't connect to MySQL server"**
- Check if host and port are correct
- Verify network connectivity
- Ensure MySQL server is running

**"Unknown database"**
- Verify the database name exists
- Check if user has access to the database

### Dependency Issues

**"No module named 'aiomysql'"**
```bash
pip install aiomysql PyMySQL
```

**"externally-managed-environment"**
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Database Tables Created

The following tables will be automatically created in MySQL:

- `users` - User economy data
- `introduction_cards` - User introduction cards
- `intro_card_interactions` - Card likes/views
- `server_settings` - Guild configurations
- `transactions` - Economy transactions
- `user_inventory` - User items
- `active_effects` - Temporary boosts
- `cooldowns` - Command cooldowns
- `user_profiles` - Extended user data
- `giveaways` - Giveaway system
- `giveaway_entries` - Giveaway participants
- `giveaway_winners` - Giveaway results
- `user_levels` - XP and leveling
- `level_role_config` - Level role rewards
- `drop_channels` - Coin drop settings
- `drop_stats` - Drop statistics
- `user_drop_stats` - User drop data

## 🔄 Switching Back to SQLite

If you need to switch back to SQLite, simply change the database type in `config.json`:

```json
{
  "database": {
    "type": "sqlite"
  }
}
```

Or remove the database configuration entirely.

## 💡 Performance Tips

1. **Connection Pooling**: The bot uses connection pooling (1-10 connections)
2. **Charset**: UTF8MB4 is configured for full Unicode support
3. **Autocommit**: Enabled for better performance with frequent small transactions

## 📞 Support

If you encounter any issues:

1. Check the error logs in `bot.log`
2. Run the test script to verify connectivity
3. Review your MySQL server configuration
4. Ensure all dependencies are installed

The bot now supports both SQLite and MySQL, so you can switch between them as needed without code changes!