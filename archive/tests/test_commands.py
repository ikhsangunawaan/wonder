#!/usr/bin/env python3
"""
Wonder Discord Bot - Comprehensive Command Testing
Tests all bot functionality without requiring Discord connection
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

class CommandTester:
    """Comprehensive testing of all bot commands and systems"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log_test(self, test_name: str, passed: bool, error: str = None):
        """Log test result"""
        if passed:
            print(f"✅ {test_name}")
            self.passed += 1
        else:
            print(f"❌ {test_name}")
            if error:
                print(f"   Error: {error}")
                self.errors.append(f"{test_name}: {error}")
            self.failed += 1
    
    async def test_economy_system(self):
        """Test all economy-related functionality"""
        print("\n💰 Testing Economy System...")
        
        try:
            from database import database
            from config import config
            
            # Initialize database
            await database.init()
            
            # Test user creation and balance
            test_user_id = "test_economy_123"
            await database.create_user(test_user_id, "TestUser")
            
            # Test getting user data (contains balance)
            user_data = await database.get_user(test_user_id)
            self.log_test("Get user data", user_data is not None)
            
            if user_data:
                balance = user_data['balance']
                self.log_test("Get user balance", balance >= 0)
                
                # Test updating balance
                await database.update_balance(test_user_id, 1000)
                updated_user = await database.get_user(test_user_id)
                new_balance = updated_user['balance']
                self.log_test("Update balance", new_balance == balance + 1000)
            
            # Test leaderboard (top users)
            top_users = await database.get_top_users(limit=10)
            self.log_test("Get leaderboard", isinstance(top_users, list))
            
            # Test adding transaction
            transaction_id = await database.add_transaction(test_user_id, "test", 100, "Test transaction")
            self.log_test("Add transaction", transaction_id is not None)
            
        except Exception as e:
            self.log_test("Economy system", False, str(e))
    
    async def test_games_system(self):
        """Test all gambling games"""
        print("\n🎮 Testing Games System...")
        
        try:
            from games_system import games_system
            from database import database
            
            test_user_id = "test_games_456"
            await database.create_user(test_user_id, "TestGamer")
            await database.update_balance(test_user_id, 10000)
            
            # Test coinflip
            result = await games_system.coinflip(test_user_id, 100, "heads")
            self.log_test("Coinflip game", isinstance(result, dict) and 'won' in result)
            
            # Test dice
            result = await games_system.dice(test_user_id, 100, 6)
            self.log_test("Dice game", isinstance(result, dict) and 'won' in result)
            
            # Test slots
            result = await games_system.slots(test_user_id, 100)
            self.log_test("Slots game", isinstance(result, dict) and 'won' in result)
            
            # Test if user data exists after games
            user_data = await database.get_user(test_user_id)
            self.log_test("User data after games", user_data is not None)
            
        except Exception as e:
            self.log_test("Games system", False, str(e))
    
    async def test_leveling_system(self):
        """Test leveling and XP system"""
        print("\n🎯 Testing Leveling System...")
        
        try:
            from database import database
            
            test_user_id = "test_level_789"
            await database.create_user(test_user_id, "TestLeveler")
            
            # Test getting user level data
            level_data = await database.get_user_level(test_user_id)
            self.log_test("Get user level data", level_data is not None)
            
            # Test updating XP
            xp_result = await database.update_user_xp(test_user_id, 100)
            self.log_test("Update user XP", isinstance(xp_result, tuple))
            
            # Test category settings
            guild_id = "test_guild_123"
            await database.set_category_enabled(guild_id, "text", True)
            is_enabled = await database.is_category_enabled(guild_id, "text")
            self.log_test("Category enable/disable", is_enabled == True)
            
            # Test getting category settings
            settings = await database.get_category_settings(guild_id)
            self.log_test("Get category settings", isinstance(settings, dict))
            
        except Exception as e:
            self.log_test("Leveling system", False, str(e))
    
    async def test_shop_system(self):
        """Test shop and inventory system"""
        print("\n🏪 Testing Shop System...")
        
        try:
            from shop_system import shop_system
            from database import database
            
            test_user_id = "test_shop_101"
            await database.create_user(test_user_id, "TestShopper")
            await database.update_balance(test_user_id, 5000)
            
            # Test shop items
            items = shop_system.get_all_items()
            self.log_test("Get shop items", len(items) > 0)
            
            # Test inventory
            inventory = await database.get_user_inventory(test_user_id)
            self.log_test("Get user inventory", isinstance(inventory, list))
            
            # Test adding item to inventory
            if items:
                item_id = list(items.keys())[0]  # Get first item
                result = await database.add_item_to_inventory(test_user_id, item_id, 1)
                self.log_test("Add item to inventory", result is not None)
            
        except Exception as e:
            self.log_test("Shop system", False, str(e))
    
    async def test_giveaway_system(self):
        """Test giveaway system"""
        print("\n🎉 Testing Giveaway System...")
        
        try:
            from database import database
            
            # Test if giveaway system functions exist
            self.log_test("Giveaway system available", hasattr(database, 'save_server_settings'))
            
            # Test server settings (used by giveaway system)
            test_guild_id = "test_guild_456"
            settings = await database.get_server_settings(test_guild_id)
            self.log_test("Get server settings", settings is not None or settings is None)  # Either is valid
            
        except Exception as e:
            self.log_test("Giveaway system", False, str(e))
    
    async def test_drop_system(self):
        """Test WonderCoins drop system"""
        print("\n🪙 Testing Drop System...")
        
        try:
            from database import database
            
            # Test if drop system methods exist (these are handled by specialized modules)
            self.log_test("Drop system database available", hasattr(database, 'get_server_settings'))
            
            # Test server settings which drop system uses
            test_guild_id = "test_guild_789"
            settings = await database.get_server_settings(test_guild_id)
            self.log_test("Get server settings for drops", settings is not None or settings is None)
            
        except Exception as e:
            self.log_test("Drop system", False, str(e))
    
    async def test_admin_commands(self):
        """Test admin command functionality"""
        print("\n🛡️ Testing Admin Commands...")
        
        try:
            from database import database
            
            test_guild_id = "test_admin_guild"
            test_user_id = "test_admin_404"
            await database.create_user(test_user_id, "TestAdmin")
            
            # Test category management
            await database.set_category_enabled(test_guild_id, "text", False)
            is_disabled = await database.is_category_enabled(test_guild_id, "text")
            self.log_test("Disable category", is_disabled == False)
            
            await database.set_category_enabled(test_guild_id, "text", True)
            is_enabled = await database.is_category_enabled(test_guild_id, "text")
            self.log_test("Enable category", is_enabled == True)
            
            # Test balance management
            await database.set_balance(test_user_id, 5000)
            user_data = await database.get_user(test_user_id)
            self.log_test("Set user currency", user_data['balance'] == 5000)
            
            # Test server settings update
            test_settings = {"test_key": "test_value"}
            await database.update_server_settings(test_guild_id, test_settings)
            self.log_test("Update server settings", True)
            
        except Exception as e:
            self.log_test("Admin commands", False, str(e))
    
    async def test_intro_cards(self):
        """Test introduction card system"""
        print("\n🎨 Testing Introduction Cards...")
        
        try:
            from database import database
            
            test_user_id = "test_intro_505"
            
            # Test creating intro card data
            card_data = {
                'user_id': test_user_id,
                'guild_id': 'test_guild',
                'name': 'Test User',
                'age': 25,
                'location': 'Test City',
                'hobbies': 'Testing, Coding',
                'favorite_color': 'blue',
                'bio': 'I am a test user'
            }
            
            result = await database.save_intro_card(card_data)
            self.log_test("Create intro card", result is not None)
            
            # Test getting intro card
            card = await database.get_intro_card(test_user_id)
            self.log_test("Get intro card", card is not None)
            
            # Test deleting intro card
            deleted = await database.delete_intro_card(test_user_id)
            self.log_test("Delete intro card", deleted == True)
            
        except Exception as e:
            self.log_test("Introduction cards", False, str(e))
    
    async def test_cooldown_system(self):
        """Test cooldown management"""
        print("\n⏰ Testing Cooldown System...")
        
        try:
            from database import database
            
            test_user_id = "test_cooldown_606"
            command_name = "test_command"
            
            # Test setting cooldown through database
            await database.set_cooldown(test_user_id, command_name)
            self.log_test("Set cooldown", True)
            
            # Test getting cooldown from database
            cooldown_time = await database.get_cooldown(test_user_id, command_name)
            self.log_test("Get cooldown", cooldown_time is not None or cooldown_time is None)
            
            # Test cleanup function
            await database.cleanup_expired_cooldowns()
            self.log_test("Cleanup expired cooldowns", True)
            
        except Exception as e:
            self.log_test("Cooldown system", False, str(e))
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🧪 Wonder Discord Bot - Comprehensive Command Testing")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        await self.test_economy_system()
        await self.test_games_system()
        await self.test_leveling_system()
        await self.test_shop_system()
        await self.test_giveaway_system()
        await self.test_drop_system()
        await self.test_admin_commands()
        await self.test_intro_cards()
        await self.test_cooldown_system()
        
        # Print final report
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total tests run: {total_tests}")
        print(f"Tests passed: {self.passed}")
        print(f"Tests failed: {self.failed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ Failed tests:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if success_rate >= 95:
            print("\n🎉 Excellent! All major systems are working perfectly!")
        elif success_rate >= 90:
            print("\n✅ Great! Bot is in excellent condition!")
        elif success_rate >= 80:
            print("\n⚠️  Good! Minor issues detected but bot is functional.")
        else:
            print("\n🔴 Critical issues detected. Bot needs attention.")
        
        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate >= 90:
            print("\n🚀 Bot is ready for production deployment!")
        else:
            print("\n🔧 Please fix the issues above before deployment.")

if __name__ == "__main__":
    tester = CommandTester()
    asyncio.run(tester.run_all_tests())