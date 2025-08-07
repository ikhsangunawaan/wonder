#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to MySQL database
Run this script to migrate existing SQLite data to MySQL
"""

import asyncio
import aiosqlite
import aiomysql
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from config import config
from mysql_database import MySQLDatabase

async def migrate_data():
    """Migrate data from SQLite to MySQL"""
    print("🔄 Starting migration from SQLite to MySQL...")
    
    # Setup SQLite connection
    sqlite_db_path = Path(__file__).parent / "wonder.db"
    if not sqlite_db_path.exists():
        print("❌ SQLite database not found. Nothing to migrate.")
        return
    
    # Setup MySQL connection
    mysql_db = MySQLDatabase()
    
    try:
        # Initialize MySQL database (create tables)
        print("📋 Creating MySQL tables...")
        await mysql_db.init()
        print("✅ MySQL tables created successfully")
        
        # Connect to SQLite
        async with aiosqlite.connect(sqlite_db_path) as sqlite_conn:
            sqlite_conn.row_factory = aiosqlite.Row
            
            # Get MySQL connection
            async with await mysql_db._get_connection() as mysql_conn:
                mysql_cursor = await mysql_conn.cursor()
                
                # Tables to migrate
                tables_to_migrate = [
                    "users",
                    "introduction_cards", 
                    "intro_card_interactions",
                    "server_settings",
                    "transactions",
                    "user_inventory",
                    "active_effects",
                    "cooldowns",
                    "user_profiles",
                    "giveaways",
                    "giveaway_entries", 
                    "giveaway_winners",
                    "user_levels",
                    "level_role_config",
                    "drop_channels",
                    "drop_stats",
                    "user_drop_stats"
                ]
                
                total_migrated = 0
                
                for table_name in tables_to_migrate:
                    print(f"📦 Migrating table: {table_name}")
                    
                    try:
                        # Check if table exists in SQLite
                        async with sqlite_conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                            (table_name,)
                        ) as cursor:
                            if not await cursor.fetchone():
                                print(f"⏭️  Table {table_name} doesn't exist in SQLite, skipping...")
                                continue
                        
                        # Get all data from SQLite table
                        async with sqlite_conn.execute(f"SELECT * FROM {table_name}") as cursor:
                            rows = await cursor.fetchall()
                            
                        if not rows:
                            print(f"⏭️  Table {table_name} is empty, skipping...")
                            continue
                            
                        # Get column names
                        column_names = [description[0] for description in cursor.description]
                        
                        # Prepare insert statement for MySQL
                        placeholders = ", ".join(["%s"] * len(column_names))
                        columns_str = ", ".join(column_names)
                        insert_sql = f"INSERT IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                        
                        # Insert data into MySQL
                        row_count = 0
                        for row in rows:
                            try:
                                await mysql_cursor.execute(insert_sql, tuple(row))
                                row_count += 1
                            except Exception as e:
                                print(f"⚠️  Error inserting row in {table_name}: {e}")
                                continue
                                
                        total_migrated += row_count
                        print(f"✅ Migrated {row_count} rows from {table_name}")
                        
                    except Exception as e:
                        print(f"❌ Error migrating table {table_name}: {e}")
                        continue
                
                await mysql_cursor.close()
                print(f"🎉 Migration completed! Total rows migrated: {total_migrated}")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    finally:
        await mysql_db.close()
    
    return True

async def verify_migration():
    """Verify that migration was successful"""
    print("\n🔍 Verifying migration...")
    
    # Setup connections
    sqlite_db_path = Path(__file__).parent / "wonder.db"
    mysql_db = MySQLDatabase()
    
    try:
        async with aiosqlite.connect(sqlite_db_path) as sqlite_conn:
            async with await mysql_db._get_connection() as mysql_conn:
                mysql_cursor = await mysql_conn.cursor()
                
                # Check users table as example
                async with sqlite_conn.execute("SELECT COUNT(*) FROM users") as cursor:
                    sqlite_count = (await cursor.fetchone())[0]
                    
                await mysql_cursor.execute("SELECT COUNT(*) FROM users")
                mysql_count = (await mysql_cursor.fetchone())[0]
                
                print(f"📊 Users table:")
                print(f"   SQLite: {sqlite_count} records")
                print(f"   MySQL:  {mysql_count} records")
                
                if sqlite_count == mysql_count:
                    print("✅ User count matches!")
                else:
                    print("⚠️  User count mismatch!")
                
                await mysql_cursor.close()
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    finally:
        await mysql_db.close()

def main():
    """Main migration function"""
    print("🚀 Wonder Discord Bot - SQLite to MySQL Migration")
    print("=" * 50)
    
    # Check if MySQL is configured
    db_config = config.get('database', {})
    if db_config.get('type') != 'mysql':
        print("❌ MySQL is not configured in config.json")
        print("Please configure MySQL settings first:")
        print('{"database": {"type": "mysql", "host": "...", ...}}')
        return
    
    print("🔧 MySQL configuration found:")
    print(f"   Host: {db_config.get('host')}")
    print(f"   Database: {db_config.get('database')}")
    print(f"   Username: {db_config.get('username')}")
    
    response = input("\n❓ Continue with migration? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("⏸️  Migration cancelled")
        return
        
    # Run migration
    try:
        success = asyncio.run(migrate_data())
        if success:
            asyncio.run(verify_migration())
            print("\n🎯 Migration process completed!")
            print("💡 Tip: You can now update your config.json to use MySQL")
        else:
            print("\n❌ Migration failed. Check the error messages above.")
    except KeyboardInterrupt:
        print("\n⏸️  Migration interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()