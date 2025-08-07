#!/usr/bin/env python3
"""
Wonder Discord Bot - Pterodactyl Setup Script
This script helps configure the bot for Pterodactyl hosting
"""

import os
import sys
from pathlib import Path

def setup_bot():
    """Setup the bot for Pterodactyl hosting"""
    print("🚀 Wonder Discord Bot - Pterodactyl Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    print("📋 Current configuration:")
    print(content)
    print("-" * 30)
    
    # Check if token is set
    if "YOUR_DISCORD_BOT_TOKEN_HERE" in content:
        print("⚠️  Discord bot token not configured!")
        print("\n🔧 To fix this:")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Create a new application or select existing one")
        print("3. Go to the 'Bot' section")
        print("4. Copy the bot token")
        print("5. In Pterodactyl terminal, run:")
        print("   export DISCORD_TOKEN='your_actual_token_here'")
        print("\n💡 Alternative: Edit the .env file directly:")
        print("   nano .env")
        print("   Replace YOUR_DISCORD_BOT_TOKEN_HERE with your actual token")
        return False
    
    # Check if environment variable is set
    token = os.getenv('DISCORD_TOKEN')
    if not token or token == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("⚠️  DISCORD_TOKEN environment variable not set!")
        print("\n🔧 Run this command in Pterodactyl terminal:")
        print("   export DISCORD_TOKEN='your_actual_token_here'")
        return False
    
    print("✅ Configuration looks good!")
    return True

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'discord.py',
        'aiofiles',
        'aiosqlite',
        'aiomysql',
        'PyMySQL',
        'Pillow',
        'python-dotenv',
        'schedule',
        'colorama',
        'typing-extensions',
        'PyNaCl',
        'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').lower())
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("🔧 Run: pip3 install --break-system-packages -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def create_start_script():
    """Create an improved start script for Pterodactyl"""
    script_content = """#!/bin/bash
# Wonder Discord Bot - Pterodactyl Start Script

echo "🚀 Starting Wonder Discord Bot..."

# Check if token is set
if [ -z "$DISCORD_TOKEN" ]; then
    echo "❌ DISCORD_TOKEN environment variable not set!"
    echo "Run: export DISCORD_TOKEN='your_token_here'"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found!"
    exit 1
fi

echo "🐍 Using $PYTHON_CMD"

# Change to script directory
cd "$(dirname "$0")"

# Check dependencies
echo "📦 Checking dependencies..."
$PYTHON_CMD -c "import discord; print('✅ discord.py installed')" || {
    echo "❌ Dependencies missing! Run setup first."
    exit 1
}

# Start the bot
echo "🎯 Starting bot..."
exec $PYTHON_CMD run.py "$@"
"""
    
    with open("start_pterodactyl.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("start_pterodactyl.sh", 0o755)
    print("✅ Created start_pterodactyl.sh script")

def main():
    """Main setup function"""
    print("🔧 Setting up Wonder Discord Bot for Pterodactyl...")
    
    # Create start script
    create_start_script()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check configuration
    config_ok = setup_bot()
    
    print("\n" + "=" * 50)
    if deps_ok and config_ok:
        print("🎉 Setup complete! Bot is ready to run.")
        print("\n🚀 To start the bot:")
        print("   ./start_pterodactyl.sh")
        print("\n   or")
        print("   python3 run.py")
    else:
        print("⚠️  Setup incomplete. Fix the issues above and run again.")
        print("\n🔧 Quick fix commands:")
        if not deps_ok:
            print("   pip3 install --break-system-packages -r requirements.txt")
        if not config_ok:
            print("   export DISCORD_TOKEN='your_actual_token_here'")

if __name__ == "__main__":
    main()