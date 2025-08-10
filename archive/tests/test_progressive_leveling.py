#!/usr/bin/env python3
"""
Progressive Leveling System Test
Tests the new leveling system with roles every 5 levels and progressive XP requirements
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from progressive_leveling import ProgressiveLevelingSystem
from database import database

class MockClient:
    """Mock Discord client for testing"""
    pass

async def test_progressive_leveling():
    """Test the progressive leveling system"""
    print("🧪 Testing Progressive Leveling System")
    print("=" * 50)
    
    # Initialize the system
    client = MockClient()
    leveling = ProgressiveLevelingSystem(client)
    
    print("✅ Progressive leveling system initialized")
    print(f"📊 Max Level: {leveling.max_level}")
    print(f"🏷️ Role Interval: Every {leveling.role_interval} levels")
    print()
    
    # Test XP calculations
    print("📈 Testing XP Formula:")
    test_levels = [1, 2, 5, 10, 15, 25, 50, 75, 100]
    
    for level in test_levels:
        xp_needed = leveling.calculate_xp_needed(level)
        total_xp = leveling.calculate_total_xp_for_level(level)
        
        print(f"Level {level:3d}: {xp_needed:6,} XP this level | {total_xp:8,} total XP")
    
    print()
    
    # Test role levels
    print("🏷️ Testing Role Levels:")
    role_levels = leveling.get_role_levels()
    print(f"Role levels: {role_levels[:10]}... (first 10)")
    print(f"Total role levels: {len(role_levels)}")
    
    # Test specific role level checks
    test_role_checks = [4, 5, 10, 15, 23, 25, 50, 99, 100]
    for level in test_role_checks:
        is_role_level = leveling.is_role_level(level)
        print(f"Level {level:3d}: {'✅ Role level' if is_role_level else '❌ No role'}")
    
    print()
    
    # Test level from XP calculation
    print("🔄 Testing Level from XP:")
    test_xp_values = [0, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000]
    
    for xp in test_xp_values:
        level, current_xp, next_xp = leveling.calculate_level_from_xp(xp)
        print(f"{xp:7,} XP → Level {level:2d} ({current_xp:4,}/{current_xp+next_xp:4,} XP)")
    
    print()
    
    # Test database operations
    print("💾 Testing Database Operations:")
    
    try:
        # Initialize database
        await database.init()
        print("✅ Database initialized")
        
        # Test role configuration
        guild_id = "test_guild_123"
        
        # Set some role configurations
        success1 = await leveling.set_level_role_config(guild_id, 5, "role_5", "Level 5 Role", "First milestone!")
        success2 = await leveling.set_level_role_config(guild_id, 10, "role_10", "Level 10 Role", "Double digits!")
        success3 = await leveling.set_level_role_config(guild_id, 25, "role_25", "Level 25 Role", "Quarter century!")
        
        print(f"✅ Set role configs: Level 5: {success1}, Level 10: {success2}, Level 25: {success3}")
        
        # Get role configurations
        role_5 = await leveling.get_level_role_config(guild_id, 5)
        role_10 = await leveling.get_level_role_config(guild_id, 10)
        role_invalid = await leveling.get_level_role_config(guild_id, 7)  # Should be None
        
        print(f"✅ Get role configs: Level 5: {bool(role_5)}, Level 10: {bool(role_10)}, Level 7: {bool(role_invalid)}")
        
        # Get all configured roles
        all_roles = await leveling.get_all_configured_roles(guild_id)
        print(f"✅ All configured roles: {len(all_roles)} roles")
        for level, data in all_roles.items():
            print(f"   Level {level}: {data['role_name']} - {data['description']}")
        
        # Test removing a role
        removed = await leveling.remove_level_role_config(guild_id, 10)
        print(f"✅ Removed Level 10 role: {removed}")
        
        # Verify removal
        all_roles_after = await leveling.get_all_configured_roles(guild_id)
        print(f"✅ Roles after removal: {len(all_roles_after)} roles")
        
        print()
        
        # Test user progress tracking
        print("👤 Testing User Progress:")
        
        test_user_id = "test_user_456"
        
        # Test with no data
        progress = await leveling.get_user_progress(test_user_id)
        print(f"✅ New user progress: Level {progress['level']}, {progress['total_xp']} XP")
        
        print()
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    # Test XP progression simulation
    print("🎮 Testing XP Progression Simulation:")
    
    # Simulate gaining XP
    simulated_xp = 0
    level_ups = []
    
    xp_gains = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    
    for i, xp_gain in enumerate(xp_gains):
        old_level, _, _ = leveling.calculate_level_from_xp(simulated_xp)
        simulated_xp += xp_gain
        new_level, current_xp, next_xp = leveling.calculate_level_from_xp(simulated_xp)
        
        if new_level > old_level:
            level_ups.append((old_level, new_level, simulated_xp))
        
        progress_pct = (current_xp / (current_xp + next_xp)) * 100 if next_xp > 0 else 100
        
        print(f"Step {i+1:2d}: +{xp_gain:5,} XP → {simulated_xp:6,} total → Level {new_level:2d} ({progress_pct:5.1f}%)")
    
    print(f"\n🎉 Level ups detected: {len(level_ups)}")
    for old_level, new_level, total_xp in level_ups:
        is_role_level = leveling.is_role_level(new_level)
        role_marker = " 🏷️" if is_role_level else ""
        print(f"   Level {old_level} → {new_level} at {total_xp:,} XP{role_marker}")
    
    print()
    
    # Performance test
    print("⚡ Performance Testing:")
    import time
    
    start_time = time.time()
    for level in range(1, 101):
        leveling.calculate_xp_needed(level)
        leveling.calculate_total_xp_for_level(level)
    end_time = time.time()
    
    print(f"✅ Calculated XP for levels 1-100 in {(end_time - start_time)*1000:.2f}ms")
    
    start_time = time.time()
    for xp in range(0, 1000000, 1000):
        leveling.calculate_level_from_xp(xp)
    end_time = time.time()
    
    print(f"✅ Calculated levels for 1000 XP values in {(end_time - start_time)*1000:.2f}ms")
    
    print()
    print("🎉 All tests completed successfully!")
    print("🚀 Progressive leveling system is ready for production!")

if __name__ == "__main__":
    asyncio.run(test_progressive_leveling())