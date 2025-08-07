#!/usr/bin/env python3
"""
Debug script for MySQL connection issues
Tests various connection scenarios
"""

import asyncio
import aiomysql
import socket
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from config import config

async def test_basic_connectivity():
    """Test basic network connectivity"""
    print("🌐 Testing basic network connectivity...")
    
    db_config = config.get('database', {})
    host = db_config.get('host')
    port = db_config.get('port', 3306)
    
    try:
        # Test socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Network connection to {host}:{port} successful")
            return True
        else:
            print(f"❌ Cannot connect to {host}:{port} (error code: {result})")
            return False
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

async def test_mysql_versions():
    """Test different MySQL connection parameters"""
    print("\n🔧 Testing MySQL connection variations...")
    
    db_config = config.get('database', {})
    
    # Basic configuration
    configs = [
        {
            'name': 'Original Config',
            'config': {
                'host': db_config.get('host'),
                'port': db_config.get('port', 3306),
                'user': db_config.get('username'),
                'password': db_config.get('password'),
                'db': db_config.get('database'),
                'charset': 'utf8mb4'
            }
        },
        {
            'name': 'Without Database Selection',
            'config': {
                'host': db_config.get('host'),
                'port': db_config.get('port', 3306),
                'user': db_config.get('username'),
                'password': db_config.get('password'),
                'charset': 'utf8mb4'
            }
        },
        {
            'name': 'With SSL Disabled',
            'config': {
                'host': db_config.get('host'),
                'port': db_config.get('port', 3306),
                'user': db_config.get('username'),
                'password': db_config.get('password'),
                'db': db_config.get('database'),
                'charset': 'utf8mb4',
                'ssl': None
            }
        }
    ]
    
    for test in configs:
        print(f"\n📋 Testing: {test['name']}")
        try:
            conn = await aiomysql.connect(**test['config'])
            cursor = await conn.cursor()
            
            # Test basic query
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
            
            # Test database access if db is specified
            if 'db' in test['config']:
                await cursor.execute("SELECT DATABASE()")
                db_result = await cursor.fetchone()
                print(f"✅ Connected! Current database: {db_result[0] if db_result else 'None'}")
            else:
                print("✅ Connected! (No database selected)")
                
            await cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    return False

async def test_database_access():
    """Test if we can access the specific database"""
    print("\n🗄️  Testing database access...")
    
    db_config = config.get('database', {})
    
    try:
        # Connect without specifying database first
        conn = await aiomysql.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 3306),
            user=db_config.get('username'),
            password=db_config.get('password'),
            charset='utf8mb4'
        )
        cursor = await conn.cursor()
        
        # Check if database exists
        await cursor.execute("SHOW DATABASES")
        databases = await cursor.fetchall()
        
        print("📋 Available databases:")
        target_db = db_config.get('database')
        db_found = False
        
        for db in databases:
            db_name = db[0]
            if db_name == target_db:
                print(f"   ✅ {db_name} (target)")
                db_found = True
            else:
                print(f"   📁 {db_name}")
        
        if not db_found:
            print(f"❌ Target database '{target_db}' not found!")
        
        # Test selecting the database
        if db_found:
            await cursor.execute(f"USE `{target_db}`")
            await cursor.execute("SELECT DATABASE()")
            current_db = await cursor.fetchone()
            print(f"✅ Successfully switched to database: {current_db[0]}")
        
        await cursor.close()
        conn.close()
        return db_found
        
    except Exception as e:
        print(f"❌ Database access error: {e}")
        return False

async def test_permissions():
    """Test user permissions"""
    print("\n🔐 Testing user permissions...")
    
    db_config = config.get('database', {})
    
    try:
        conn = await aiomysql.connect(
            host=db_config.get('host'),
            port=db_config.get('port', 3306),
            user=db_config.get('username'),
            password=db_config.get('password'),
            charset='utf8mb4'
        )
        cursor = await conn.cursor()
        
        # Check user privileges
        await cursor.execute("SHOW GRANTS")
        grants = await cursor.fetchall()
        
        print("🔑 User privileges:")
        for grant in grants:
            print(f"   📜 {grant[0]}")
        
        await cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Permission check error: {e}")
        return False

def print_config_debug():
    """Print current configuration for debugging"""
    print("⚙️  Current MySQL Configuration:")
    print("=" * 35)
    
    db_config = config.get('database', {})
    
    # Mask password for security
    masked_config = db_config.copy()
    if 'password' in masked_config:
        masked_config['password'] = '*' * len(masked_config['password'])
    
    for key, value in masked_config.items():
        print(f"   {key}: {value}")
    print()

async def main():
    """Main debug function"""
    print("🚀 Wonder Discord Bot - MySQL Debug Tool")
    print("=" * 45)
    
    print_config_debug()
    
    # Test sequence
    tests = [
        ("Network Connectivity", test_basic_connectivity),
        ("MySQL Connections", test_mysql_versions),
        ("Database Access", test_database_access),
        ("User Permissions", test_permissions)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Debug Summary")
    print("=" * 20)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if not results.get("Network Connectivity", False):
        print("   🌐 Check network connectivity to the MySQL server")
        print("   🔥 Verify firewall settings allow port 3306")
    
    if not results.get("MySQL Connections", False):
        print("   🔐 Verify MySQL username and password")
        print("   👤 Check if user account exists and is active")
        print("   🏠 Ensure MySQL server allows connections from your IP")
    
    if not results.get("Database Access", False):
        print("   🗄️  Check if database name is correct")
        print("   🔑 Verify user has access to the specific database")
    
    if all(results.values()):
        print("   🎉 All tests passed! MySQL should work correctly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏸️  Debug interrupted by user")
    except Exception as e:
        print(f"\n💥 Debug error: {e}")