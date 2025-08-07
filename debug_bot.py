#!/usr/bin/env python3
"""
Debug and Test Script for Wonder Discord Bot
Comprehensive testing without Discord connection
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import traceback
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

class BotDebugger:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log_test(self, test_name, success, error=None):
        """Log test result"""
        if success:
            print(f"✅ {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ {test_name}")
            if error:
                print(f"   Error: {error}")
                self.errors.append(f"{test_name}: {error}")
            self.tests_failed += 1
    
    def test_imports(self):
        """Test all critical imports"""
        print("\n🔍 Testing imports...")
        
        # Test Discord.py
        try:
            import discord
            self.log_test("Discord.py import", True)
        except Exception as e:
            self.log_test("Discord.py import", False, str(e))
        
        # Test main bot
        try:
            from main import WonderBot
            self.log_test("Main bot import", True)
        except Exception as e:
            self.log_test("Main bot import", False, str(e))
        
        # Test config
        try:
            from config import config
            self.log_test("Config import", True)
        except Exception as e:
            self.log_test("Config import", False, str(e))
        
        # Test database
        try:
            from database import database
            self.log_test("Database import", True)
        except Exception as e:
            self.log_test("Database import", False, str(e))
        
        # Test systems
        systems = [
            ('shop_system', 'Shop system'),
            ('games_system', 'Games system'),
            ('giveaway_system', 'Giveaway system'),
            ('leveling_system', 'Leveling system'),
            ('cooldown_manager', 'Cooldown manager'),
            ('wondercoins_drops', 'WonderCoins drops'),
            ('role_manager', 'Role manager'),
            ('intro_card_system', 'Intro card system')
        ]
        
        for module, name in systems:
            try:
                __import__(module)
                self.log_test(f"{name} import", True)
            except Exception as e:
                self.log_test(f"{name} import", False, str(e))
    
    def test_config_loading(self):
        """Test configuration loading"""
        print("\n⚙️ Testing configuration...")
        
        try:
            from config import config
            
            # Test basic config access
            prefix = config.prefix
            self.log_test("Config prefix access", prefix is not None)
            
            # Test currency config
            currency = config.currency
            self.log_test("Currency config", isinstance(currency, dict))
            
            # Test branding config
            branding = config.branding
            self.log_test("Branding config", isinstance(branding, dict))
            
            # Test colors config
            colors = config.colors
            self.log_test("Colors config", isinstance(colors, dict))
            
            print(f"   Bot name: {branding.get('name', 'N/A')}")
            print(f"   Prefix: {prefix}")
            print(f"   Currency: {currency.get('name', 'N/A')}")
            
        except Exception as e:
            self.log_test("Config loading", False, str(e))
    
    async def test_database_initialization(self):
        """Test database initialization"""
        print("\n💾 Testing database...")
        
        try:
            from database import database
            
            # Test database initialization
            await database.init()
            self.log_test("Database initialization", True)
            
            # Test basic database operations
            await database.create_user("test_user_123", "TestUser")
            self.log_test("User creation", True)
            
            user_data = await database.get_user("test_user_123")
            self.log_test("User retrieval", user_data is not None)
            
            # Clean up test user
            try:
                await database.close()
            except:
                pass
            
        except Exception as e:
            self.log_test("Database operations", False, str(e))
    
    def test_bot_initialization(self):
        """Test bot instance creation"""
        print("\n🤖 Testing bot initialization...")
        
        try:
            from main import WonderBot
            
            # Create bot instance
            bot = WonderBot()
            self.log_test("Bot instance creation", True)
            
            # Test bot attributes
            self.log_test("Bot has database", hasattr(bot, 'database'))
            self.log_test("Bot has config", hasattr(bot, 'config'))
            self.log_test("Bot has shop_system", hasattr(bot, 'shop_system'))
            self.log_test("Bot has games_system", hasattr(bot, 'games_system'))
            
            # Test intents
            self.log_test("Bot has intents", bot.intents is not None)
            self.log_test("Message content intent", bot.intents.message_content)
            self.log_test("Members intent", bot.intents.members)
            
        except Exception as e:
            self.log_test("Bot initialization", False, str(e))
    
    def test_shop_system(self):
        """Test shop system"""
        print("\n🛒 Testing shop system...")
        
        try:
            from shop_system import shop_system
            
            # Test shop items loading
            items = shop_system.get_all_items()
            self.log_test("Shop items loading", isinstance(items, list))
            
            if items:
                print(f"   Found {len(items)} shop items")
                # Test first item structure
                first_item = items[0]
                required_keys = ['id', 'name', 'price', 'description']
                has_all_keys = all(key in first_item for key in required_keys)
                self.log_test("Shop item structure", has_all_keys)
            
        except Exception as e:
            self.log_test("Shop system", False, str(e))
    
    def test_games_system(self):
        """Test games system"""
        print("\n🎮 Testing games system...")
        
        try:
            from games_system import games_system
            
            # Test game methods exist
            self.log_test("Coinflip method", hasattr(games_system, 'coinflip'))
            self.log_test("Dice method", hasattr(games_system, 'dice_roll'))
            self.log_test("Slots method", hasattr(games_system, 'slots'))
            
        except Exception as e:
            self.log_test("Games system", False, str(e))
    
    def test_cooldown_system(self):
        """Test cooldown system"""
        print("\n⏰ Testing cooldown system...")
        
        try:
            from cooldown_manager import cooldown_manager
            
            # Test cooldown methods
            self.log_test("Check cooldown method", hasattr(cooldown_manager, 'check_cooldown'))
            self.log_test("Set cooldown method", hasattr(cooldown_manager, 'set_cooldown'))
            
        except Exception as e:
            self.log_test("Cooldown system", False, str(e))
    
    def test_command_definitions(self):
        """Test command definitions"""
        print("\n📝 Testing command definitions...")
        
        try:
            from main import (
                balance, daily, work, coinflip, dice, slots,
                shop, buy, inventory, rank, help_command
            )
            
            commands = [
                ('balance', balance),
                ('daily', daily),
                ('work', work),
                ('coinflip', coinflip),
                ('dice', dice),
                ('slots', slots),
                ('shop', shop),
                ('buy', buy),
                ('inventory', inventory),
                ('rank', rank),
                ('help', help_command)
            ]
            
            for cmd_name, cmd_func in commands:
                self.log_test(f"Command {cmd_name}", callable(cmd_func))
            
        except Exception as e:
            self.log_test("Command definitions", False, str(e))
    
    def test_environment_variables(self):
        """Test environment variables"""
        print("\n🌍 Testing environment variables...")
        
        # Load environment
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            # Check Discord token
            token = os.getenv('DISCORD_TOKEN')
            if token and token != 'YOUR_DISCORD_BOT_TOKEN_HERE':
                self.log_test("Discord token configured", True)
            else:
                self.log_test("Discord token configured", False, "Token not set or placeholder")
            
            # Check optional variables
            premium_role = os.getenv('PREMIUM_ROLE_ID')
            self.log_test("Premium role ID", premium_role is not None)
            
            booster_role = os.getenv('BOOSTER_ROLE_ID')
            self.log_test("Booster role ID", booster_role is not None)
            
        except Exception as e:
            self.log_test("Environment variables", False, str(e))
    
    def test_file_structure(self):
        """Test project file structure"""
        print("\n📁 Testing file structure...")
        
        critical_files = [
            'src/main.py',
            'src/config.py',
            'src/database.py',
            'requirements.txt',
            'config.json',
            '.env',
            'run.py'
        ]
        
        for file_path in critical_files:
            full_path = self.project_dir / file_path
            self.log_test(f"File {file_path}", full_path.exists())
    
    def generate_debug_report(self):
        """Generate comprehensive debug report"""
        print("\n" + "="*60)
        print("📊 DEBUG REPORT")
        print("="*60)
        
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total tests run: {total_tests}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_failed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if self.tests_failed > 0:
            print(f"\n❌ Failed tests:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if success_rate >= 90:
            print("\n✅ Bot is in excellent condition!")
        elif success_rate >= 75:
            print("\n🟡 Bot is mostly working with minor issues")
        elif success_rate >= 50:
            print("\n🟠 Bot has significant issues that need attention")
        else:
            print("\n🔴 Bot has critical issues that must be fixed")
        
        return success_rate >= 75
    
    async def run_all_tests(self):
        """Run all debug tests"""
        print("🐛 Wonder Discord Bot - Debug & Test Suite")
        print("="*60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests
        self.test_file_structure()
        self.test_imports()
        self.test_config_loading()
        await self.test_database_initialization()
        self.test_bot_initialization()
        self.test_shop_system()
        self.test_games_system()
        self.test_cooldown_system()
        self.test_command_definitions()
        self.test_environment_variables()
        
        # Generate report
        success = self.generate_debug_report()
        
        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return success

async def main():
    """Main debug function"""
    try:
        debugger = BotDebugger()
        success = await debugger.run_all_tests()
        
        if success:
            print("\n🚀 Bot is ready for deployment!")
            print("Next steps:")
            print("1. Set Discord token in .env file")
            print("2. Run: python3 run.py")
        else:
            print("\n🔧 Please fix the issues above before running the bot")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())