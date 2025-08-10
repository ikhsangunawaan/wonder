#!/usr/bin/env python3
"""
🤖 Wonder Bot - Setup Script Super Gampang!
Script ini otomatis setup bot biar lu gak ribet.
"""

import os
import sys
import json
import subprocess

def print_banner():
    print("""
    🤖 WONDER BOT SETUP 🤖
    =====================
    Script ini bakal setup bot otomatis!
    Tinggal ikutin aja step-by-stepnya.
    """)

def check_python():
    """Cek versi Python"""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or version.minor < 8:
        print("❌ Error: Butuh Python 3.8 atau lebih baru!")
        print("   Download di: https://python.org")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected - OK!")
    return True

def install_requirements():
    """Install dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies!")
        print("   Try manual: pip install -r requirements.txt")
        return False

def setup_config():
    """Setup config.json"""
    print("\n⚙️ Setting up config...")
    
    # Baca config yang ada
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except:
        print("❌ Error: config.json not found!")
        return False
    
    print("\n🔑 DISCORD BOT TOKEN SETUP:")
    print("1. Buka https://discord.com/developers/applications")
    print("2. Create New Application")
    print("3. Masuk ke Bot tab")
    print("4. Copy token bot lu")
    print()
    
    token = input("Masukin Discord Bot Token lu: ").strip()
    if not token:
        print("❌ Token gak boleh kosong!")
        return False
    
    # Update config
    config['token'] = token
    
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Config saved!")
        return True
    except:
        print("❌ Error saving config!")
        return False

def create_run_script():
    """Bikin script run yang simple"""
    script_content = '''#!/usr/bin/env python3
"""
Simple script to run Wonder Bot
Usage: python run_bot.py
"""

import os
import sys

# Change to src directory
os.chdir('src')

# Run the bot
if __name__ == "__main__":
    try:
        import main
        print("🤖 Starting Wonder Bot...")
        import asyncio
        asyncio.run(main.main())
    except ImportError:
        print("❌ Error: Missing dependencies!")
        print("   Run: python SIMPLE_SETUP.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Check your config.json and try again")
'''
    
    try:
        with open('run_bot.py', 'w') as f:
            f.write(script_content)
        print("✅ Created run_bot.py - Use this to start your bot!")
        return True
    except:
        print("❌ Error creating run script!")
        return False

def final_instructions():
    """Kasih tau gimana pake bot"""
    print("""
    🎉 SETUP COMPLETE! 🎉
    ====================
    
    Bot lu udah siap dijalanin!
    
    📝 CARA JALANIN BOT:
    1. python run_bot.py
    2. Tunggu sampe muncul "Bot is ready!"
    3. Test di Discord server lu
    
    🔧 KALO ADA MASALAH:
    - Cek token di config.json
    - Restart bot (Ctrl+C terus jalanin lagi)
    - Hapus folder src/__pycache__ kalo ada error aneh
    
    💡 TIPS:
    - File penting cuma: config.json, run_bot.py, src/
    - File di folder archive/ gak usah diutak-atik
    - Kalo bingung, restart aja bot-nya
    
    🚀 SELAMAT! Bot lu udah ready to rock! 🚀
    """)

def main():
    print_banner()
    
    # Check Python version
    if not check_python():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Setup config
    if not setup_config():
        return
    
    # Create simple run script
    if not create_run_script():
        return
    
    # Final instructions
    final_instructions()

if __name__ == "__main__":
    main()