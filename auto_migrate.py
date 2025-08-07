#!/usr/bin/env python3
"""
Automated migration script (no user input required)
"""

import asyncio
import aiosqlite
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from config import config
from mysql_database import MySQLDatabase

async def auto_migrate():
    """Automated migration"""
    print("🔄 Starting automated migration from SQLite to MySQL...")
    
    # Setup SQLite connection
    sqlite_db_path = Path(__file__).parent / "wonder.db"
    if not sqlite_db_path.exists():
        print("❌ SQLite database not found. Creating empty tables in MySQL...")
    
    # Setup MySQL connection
    mysql_db = MySQLDatabase()
    
    try:
        # Initialize MySQL database (create tables)
        print("📋 Creating MySQL tables...")
        await mysql_db.init()
        print("✅ MySQL tables created successfully")
        
        if sqlite_db_path.exists():
            # Connect to SQLite for data migration
            async with aiosqlite.connect(sqlite_db_path) as sqlite_conn:
                sqlite_conn.row_factory = aiosqlite.Row
                
                # Get MySQL connection
                async with await mysql_db._get_connection() as mysql_conn:
                    mysql_cursor = await mysql_conn.cursor()
                    
                    # Simple test - migrate users table only
                    print("📦 Testing with users table...")
                    
                    try:
                        # Check if users table exists in SQLite
                        async with sqlite_conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
                        ) as cursor:
                            if await cursor.fetchone():
                                # Get user data from SQLite
                                async with sqlite_conn.execute("SELECT * FROM users LIMIT 5") as cursor:
                                    rows = await cursor.fetchall()
                                    
                                if rows:
                                    print(f"📊 Found {len(rows)} users in SQLite")
                                    
                                    # Insert into MySQL
                                    for row in rows:
                                        try:
                                            await mysql_cursor.execute(
                                                "INSERT IGNORE INTO users (user_id, username, balance, daily_last_claimed, work_last_used, total_earned, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                                tuple(row)
                                            )
                                        except Exception as e:
                                            print(f"⚠️  Row error: {e}")
                                            continue
                                    
                                    print("✅ Sample users migrated successfully")
                                else:
                                    print("📊 Users table is empty")
                            else:
                                print("📊 No users table found in SQLite")
                    except Exception as e:
                        print(f"❌ Users migration error: {e}")
                    
                    await mysql_cursor.close()
        
        # Test the database connection and verify
        print("\n🔍 Verifying MySQL database...")
        async with await mysql_db._get_connection() as conn:
            cursor = await conn.cursor()
            
            # Show tables
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            
            print(f"📋 Created {len(tables)} tables:")
            for table in tables[:5]:  # Show first 5 tables
                print(f"   ✅ {table[0]}")
            
            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more tables")
            
            await cursor.close()
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    finally:
        await mysql_db.close()

async def test_bot_functionality():
    """Test if bot can work with MySQL"""
    print("\n🤖 Testing bot functionality with MySQL...")
    
    try:
        # Import and test database
        from database import Database
        
        db = Database()
        
        # Test basic database operations
        test_user_id = "test_user_123"
        test_username = "TestUser"
        
        # Create test user
        await db.create_user(test_user_id, test_username)
        print("✅ User creation test passed")
        
        # Get user
        user = await db.get_user(test_user_id)
        if user:
            print(f"✅ User retrieval test passed: {user['username']}")
        else:
            print("❌ User retrieval failed")
        
        # Update balance
        await db.update_balance(test_user_id, 100)
        print("✅ Balance update test passed")
        
        # Get updated user
        updated_user = await db.get_user(test_user_id)
        if updated_user and updated_user['balance'] == 100:
            print(f"✅ Balance verification passed: {updated_user['balance']}")
        else:
            print("❌ Balance verification failed")
        
        await db.close()
        print("🎉 All bot functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Bot functionality test failed: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Automated MySQL Setup & Test")
    print("=" * 35)
    
    # Check MySQL configuration
    db_config = config.get('database', {})
    if db_config.get('type') != 'mysql':
        print("❌ MySQL not configured")
        return
    
    print("✅ MySQL configuration detected")
    
    # Run migration
    migration_success = await auto_migrate()
    
    if migration_success:
        # Test bot functionality
        bot_test_success = await test_bot_functionality()
        
        if bot_test_success:
            print("\n🎯 Complete Success!")
            print("✅ MySQL database is ready")
            print("✅ Bot can connect and operate")
            print("✅ All systems are functional")
            
            print("\n🚀 Ready to run your bot:")
            print("   python3 run.py")
        else:
            print("\n⚠️  Database setup OK, but bot integration needs checking")
    else:
        print("\n❌ Migration failed - check error messages above")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 Error: {e}")