#!/usr/bin/env python3
"""
Advanced MySQL debugging - tests authentication scenarios
"""

import asyncio
import aiomysql
import urllib.parse
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from config import config

async def test_password_encoding():
    """Test different password encoding methods"""
    print("🔐 Testing password encoding variations...")
    
    db_config = config.get('database', {})
    original_password = db_config.get('password')
    
    # Different password encoding scenarios
    password_tests = [
        {
            'name': 'Original Password',
            'password': original_password
        },
        {
            'name': 'URL Decoded Password',
            'password': urllib.parse.unquote(original_password)
        },
        {
            'name': 'URL Encoded Password',
            'password': urllib.parse.quote(original_password, safe='')
        }
    ]
    
    for test in password_tests:
        print(f"\n📋 Testing: {test['name']}")
        print(f"   Password format: {test['password'][:10]}...")
        
        try:
            conn = await aiomysql.connect(
                host=db_config.get('host'),
                port=db_config.get('port', 3306),
                user=db_config.get('username'),
                password=test['password'],
                charset='utf8mb4',
                ssl=None
            )
            
            cursor = await conn.cursor()
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
            
            print(f"✅ SUCCESS! Password format works: {test['name']}")
            
            await cursor.close()
            conn.close()
            return test['password']
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    return None

async def test_manual_credentials():
    """Test with manually input credentials"""
    print("\n🔧 Manual credential testing...")
    print("Let's try connecting with step-by-step credential verification")
    
    db_config = config.get('database', {})
    
    # Test basic connection parameters
    params = {
        'host': db_config.get('host'),
        'port': db_config.get('port', 3306),
        'charset': 'utf8mb4',
        'ssl': None
    }
    
    print(f"🏠 Host: {params['host']}")
    print(f"🔌 Port: {params['port']}")
    
    # Test different credential combinations
    credential_tests = [
        {
            'name': 'Original from JDBC string',
            'user': 'u1056_f489WrV7JK',
            'password': '9FG=AN*P7C5@BG2m6Aq02Id'
        },
        {
            'name': 'URL decoded credentials',
            'user': 'u1056_f489WrV7JK',
            'password': urllib.parse.unquote('9FG%3DAN%5EP7C5%40%40BG2m6Aq0')  # From JDBC string
        },
        {
            'name': 'Escaped special characters',
            'user': 'u1056_f489WrV7JK',
            'password': '9FG=AN^P7C5@@BG2m6Aq02Id'  # Manual interpretation
        }
    ]
    
    for test in credential_tests:
        print(f"\n👤 Testing: {test['name']}")
        print(f"   Username: {test['user']}")
        print(f"   Password: {test['password'][:5]}...")
        
        try:
            test_params = params.copy()
            test_params.update({
                'user': test['user'],
                'password': test['password']
            })
            
            conn = await aiomysql.connect(**test_params)
            cursor = await conn.cursor()
            
            await cursor.execute("SELECT USER()")
            user_result = await cursor.fetchone()
            
            await cursor.execute("SELECT VERSION()")
            version_result = await cursor.fetchone()
            
            print(f"✅ SUCCESS!")
            print(f"   Connected as: {user_result[0]}")
            print(f"   MySQL version: {version_result[0]}")
            
            await cursor.close()
            conn.close()
            return test
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    return None

async def test_jdbc_string_parsing():
    """Parse and test JDBC connection string"""
    print("\n🔗 Testing JDBC string parsing...")
    
    # Original JDBC string from the image
    jdbc_string = "jdbc:mysql://u1056_f489WrV7JK:9FG%3DAN%5EP7C5%40%40BG2m6Aq0"
    
    print(f"📋 Original JDBC: {jdbc_string}")
    
    try:
        # Parse JDBC string
        if jdbc_string.startswith("jdbc:mysql://"):
            connection_part = jdbc_string[13:]  # Remove "jdbc:mysql://"
            
            # Split username:password@host part
            if '@' in connection_part:
                auth_part, host_part = connection_part.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                    
                    # URL decode the password
                    decoded_password = urllib.parse.unquote(password)
                    
                    print(f"🔍 Parsed from JDBC:")
                    print(f"   Username: {username}")
                    print(f"   Encoded password: {password}")
                    print(f"   Decoded password: {decoded_password}")
                    
                    # Test with decoded password
                    db_config = config.get('database', {})
                    
                    conn = await aiomysql.connect(
                        host=db_config.get('host'),
                        port=db_config.get('port', 3306),
                        user=username,
                        password=decoded_password,
                        charset='utf8mb4',
                        ssl=None
                    )
                    
                    cursor = await conn.cursor()
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    
                    print("✅ JDBC parsing successful!")
                    
                    await cursor.close()
                    conn.close()
                    return {'username': username, 'password': decoded_password}
        
    except Exception as e:
        print(f"❌ JDBC parsing failed: {e}")
        return None

async def suggest_fixes():
    """Suggest potential fixes based on the error pattern"""
    print("\n💡 Suggested Solutions:")
    print("=" * 25)
    
    print("1. 🔐 Password Special Characters Issue:")
    print("   The password contains special characters: =, ^, @")
    print("   Try URL encoding/decoding the password")
    
    print("\n2. 🌐 IP Whitelist Issue:")
    print("   Error shows different AWS IP addresses")
    print("   The MySQL server might only allow specific IPs")
    
    print("\n3. 🔑 User Account Issues:")
    print("   - User might not exist")
    print("   - User might be locked/disabled")
    print("   - User might need different host pattern")
    
    print("\n4. 🏠 Host Configuration:")
    print("   - Try connecting from MySQL Workbench first")
    print("   - Verify the host accepts external connections")
    print("   - Check if there's a specific connection protocol")

def create_corrected_config(working_credentials):
    """Create corrected configuration"""
    if not working_credentials:
        return
        
    print(f"\n✅ Working Configuration Found!")
    print("=" * 35)
    
    corrected_config = {
        "database": {
            "type": "mysql",
            "host": "mc.anjas.id",
            "port": 3306,
            "database": "s1056_wonder_server",
            "username": working_credentials['username'],
            "password": working_credentials['password'],
            "charset": "utf8mb4",
            "autocommit": True,
            "pool_settings": {
                "minsize": 1,
                "maxsize": 10
            }
        }
    }
    
    print("📝 Add this to your config.json:")
    import json
    print(json.dumps(corrected_config, indent=2))

async def main():
    """Main advanced debug function"""
    print("🔬 Advanced MySQL Authentication Debug")
    print("=" * 40)
    
    # Test sequence
    tests = [
        ("Password Encoding", test_password_encoding),
        ("JDBC String Parsing", test_jdbc_string_parsing),
        ("Manual Credentials", test_manual_credentials)
    ]
    
    working_credentials = None
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = await test_func()
            if result:
                print(f"✅ {test_name} found working solution!")
                working_credentials = result
                break
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
            continue
    
    if working_credentials:
        create_corrected_config(working_credentials)
    else:
        await suggest_fixes()
        
        print("\n🔧 Manual Testing Required:")
        print("1. Test connection with MySQL Workbench")
        print("2. Contact hosting provider for correct credentials")
        print("3. Verify IP whitelist settings")
        print("4. Check if username format is correct")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏸️  Debug interrupted")
    except Exception as e:
        print(f"\n💥 Debug error: {e}")