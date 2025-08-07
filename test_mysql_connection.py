#!/usr/bin/env python3
"""
Simple test script to verify MySQL connection
Run this to test if MySQL configuration is working
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from config import config
    from mysql_database import MySQLDatabase
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📝 Make sure to install dependencies: pip install aiomysql PyMySQL")
    sys.exit(1)

async def test_connection():
    """Test MySQL connection"""
    print("🔧 Testing MySQL connection...")
    
    # Check configuration
    db_config = config.get('database', {})
    if db_config.get('type') != 'mysql':
        print("❌ MySQL not configured in config.json")
        return False
        
    print(f"🏠 Host: {db_config.get('host')}")
    print(f"🗄️  Database: {db_config.get('database')}")
    print(f"👤 Username: {db_config.get('username')}")
    
    try:
        mysql_db = MySQLDatabase()
        
        # Test connection
        async with await mysql_db._get_connection() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
            await cursor.close()
            
        await mysql_db.close()
        
        if result and result[0] == 1:
            print("✅ MySQL connection successful!")
            return True
        else:
            print("❌ MySQL connection failed - unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Wonder Discord Bot - MySQL Connection Test")
    print("=" * 45)
    
    try:
        success = asyncio.run(test_connection())
        if success:
            print("\n🎉 Connection test passed!")
            print("💡 You can now run the migration script: python migrate_to_mysql.py")
        else:
            print("\n❌ Connection test failed!")
            print("🔧 Please check your MySQL configuration in config.json")
    except Exception as e:
        print(f"\n💥 Test error: {e}")

if __name__ == "__main__":
    main()