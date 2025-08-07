#!/usr/bin/env python3
"""
Deployment Validation Script for Wonder Discord Bot
Tests all aspects of deployment readiness
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
import importlib.util

class DeploymentValidator:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.system = platform.system().lower()
        
    def log_error(self, message):
        """Log an error"""
        self.errors.append(message)
        print(f"❌ {message}")
    
    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(message)
        print(f"⚠️  {message}")
    
    def log_success(self, message):
        """Log a success"""
        print(f"✅ {message}")
    
    def check_python_version(self):
        """Check Python version compatibility"""
        print("\n🐍 Checking Python version...")
        
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            if version.major < 3:
                self.log_error(f"Python 2.x detected ({version_str}). Python 3.8+ required.")
                return False
            elif version.major == 3 and version.minor < 8:
                self.log_error(f"Python 3.{version.minor} detected. Python 3.8+ required.")
                return False
            else:
                self.log_success(f"Python {version_str} - Compatible")
                return True
                
        except Exception as e:
            self.log_error(f"Could not check Python version: {e}")
            return False
    
    def check_required_files(self):
        """Check if all required files exist"""
        print("\n📁 Checking required files...")
        
        required_files = [
            'requirements.txt',
            'run.py',
            'Procfile',
            '.env',
            'src/main.py',
            'src/config.py',
            'src/database.py',
            'config.json'
        ]
        
        missing_files = []
        
        for file_path in required_files:
            full_path = self.project_dir / file_path
            if full_path.exists():
                self.log_success(f"Found: {file_path}")
            else:
                missing_files.append(file_path)
                self.log_error(f"Missing: {file_path}")
        
        return len(missing_files) == 0
    
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        print("\n📦 Checking dependencies...")
        
        try:
            with open(self.project_dir / 'requirements.txt', 'r') as f:
                requirements = f.read().strip().split('\n')
        except FileNotFoundError:
            self.log_error("requirements.txt not found")
            return False
        
        missing_deps = []
        
        for requirement in requirements:
            if not requirement.strip() or requirement.startswith('#'):
                continue
                
            # Extract package name (before >= or ==)
            package_name = requirement.split('>=')[0].split('==')[0].replace('-', '_')
            
            try:
                # Try to import the package
                if package_name == 'discord.py':
                    import discord
                    self.log_success(f"discord.py {discord.__version__}")
                elif package_name == 'python_dotenv':
                    import dotenv
                    self.log_success("python-dotenv")
                elif package_name == 'PyMySQL':
                    import pymysql
                    self.log_success("PyMySQL")
                elif package_name == 'PyNaCl':
                    import nacl
                    self.log_success("PyNaCl")
                elif package_name == 'Pillow':
                    import PIL
                    self.log_success(f"Pillow {PIL.__version__}")
                else:
                    # Generic import check
                    spec = importlib.util.find_spec(package_name.lower())
                    if spec is not None:
                        self.log_success(package_name)
                    else:
                        missing_deps.append(package_name)
                        self.log_error(f"Missing: {package_name}")
                        
            except ImportError:
                missing_deps.append(package_name)
                self.log_error(f"Missing: {package_name}")
        
        if missing_deps:
            self.log_error(f"Run: pip install {' '.join(missing_deps)}")
            return False
        
        return True
    
    def check_environment_config(self):
        """Check environment configuration"""
        print("\n🔧 Checking environment configuration...")
        
        env_path = self.project_dir / '.env'
        
        if not env_path.exists():
            self.log_error(".env file not found")
            return False
        
        try:
            with open(env_path, 'r') as f:
                env_content = f.read()
            
            # Check for Discord token
            if 'DISCORD_TOKEN=' not in env_content:
                self.log_error("DISCORD_TOKEN not found in .env")
                return False
            elif 'YOUR_DISCORD_BOT_TOKEN_HERE' in env_content:
                self.log_warning("Discord token not configured (still placeholder)")
            else:
                self.log_success("Discord token configured")
            
            # Check optional configurations
            if 'PREMIUM_ROLE_ID=' in env_content:
                self.log_success("Premium role ID configured")
            
            if 'BOOSTER_ROLE_ID=' in env_content:
                self.log_success("Booster role ID configured")
                
            return True
            
        except Exception as e:
            self.log_error(f"Could not read .env file: {e}")
            return False
    
    def check_config_json(self):
        """Check config.json validity"""
        print("\n⚙️ Checking config.json...")
        
        config_path = self.project_dir / 'config.json'
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required sections
            required_sections = ['prefix', 'currency', 'branding', 'colors', 'cooldowns']
            
            for section in required_sections:
                if section in config:
                    self.log_success(f"Config section: {section}")
                else:
                    self.log_error(f"Missing config section: {section}")
            
            return True
            
        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON in config.json: {e}")
            return False
        except FileNotFoundError:
            self.log_error("config.json not found")
            return False
    
    def check_bot_imports(self):
        """Test bot imports"""
        print("\n🤖 Testing bot imports...")
        
        # Add src to path
        sys.path.insert(0, str(self.project_dir / 'src'))
        
        try:
            # Test main imports
            from main import WonderBot
            self.log_success("Main bot import successful")
            
            from config import config
            self.log_success("Config import successful")
            
            from database import database
            self.log_success("Database import successful")
            
            # Test system imports
            from shop_system import shop_system
            self.log_success("Shop system import successful")
            
            from games_system import games_system
            self.log_success("Games system import successful")
            
            return True
            
        except ImportError as e:
            self.log_error(f"Import error: {e}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error during imports: {e}")
            return False
    
    def check_deployment_files(self):
        """Check deployment-specific files"""
        print("\n🚀 Checking deployment files...")
        
        deployment_files = {
            'Procfile': 'Heroku/Railway deployment',
            'Dockerfile': 'Docker deployment',
            'docker-compose.yml': 'Docker Compose deployment',
            'railway.json': 'Railway deployment',
            'render.yaml': 'Render deployment',
            'start.sh': 'Unix startup script',
            'start.bat': 'Windows startup script'
        }
        
        all_present = True
        
        for file_name, description in deployment_files.items():
            file_path = self.project_dir / file_name
            if file_path.exists():
                self.log_success(f"{description}: {file_name}")
            else:
                self.log_warning(f"Missing {description}: {file_name}")
                all_present = False
        
        return all_present
    
    def check_permissions(self):
        """Check file permissions"""
        print("\n🔐 Checking file permissions...")
        
        executable_files = ['start.sh', 'run.py']
        
        for file_name in executable_files:
            file_path = self.project_dir / file_name
            if file_path.exists():
                if self.system != 'windows':
                    # Check if file is executable on Unix systems
                    if os.access(file_path, os.X_OK):
                        self.log_success(f"{file_name} is executable")
                    else:
                        self.log_warning(f"{file_name} is not executable (run: chmod +x {file_name})")
                else:
                    self.log_success(f"{file_name} exists (Windows)")
        
        return True
    
    def test_bot_initialization(self):
        """Test bot can be initialized"""
        print("\n🧪 Testing bot initialization...")
        
        try:
            sys.path.insert(0, str(self.project_dir / 'src'))
            from main import WonderBot
            
            # Create bot instance
            bot = WonderBot()
            self.log_success("Bot instance created successfully")
            
            # Test basic attributes
            if hasattr(bot, 'database'):
                self.log_success("Database attribute present")
            
            if hasattr(bot, 'config'):
                self.log_success("Config attribute present")
            
            return True
            
        except Exception as e:
            self.log_error(f"Bot initialization failed: {e}")
            return False
    
    def check_database_setup(self):
        """Test database setup"""
        print("\n💾 Testing database setup...")
        
        try:
            sys.path.insert(0, str(self.project_dir / 'src'))
            from database import database
            
            # Check database path for SQLite
            if hasattr(database, 'db_path'):
                db_path = database.db_path
                if db_path.parent.exists():
                    self.log_success(f"Database directory exists: {db_path.parent}")
                else:
                    self.log_warning(f"Database directory missing: {db_path.parent}")
            
            self.log_success("Database module loaded successfully")
            return True
            
        except Exception as e:
            self.log_error(f"Database test failed: {e}")
            return False
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*50)
        print("📋 DEPLOYMENT VALIDATION REPORT")
        print("="*50)
        
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        
        if total_errors == 0:
            print("✅ No critical errors found - Ready for deployment!")
        else:
            print(f"❌ {total_errors} critical error(s) found:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if total_warnings > 0:
            print(f"\n⚠️  {total_warnings} warning(s):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        print(f"\n📊 Summary:")
        print(f"  - Errors: {total_errors}")
        print(f"  - Warnings: {total_warnings}")
        print(f"  - Status: {'✅ READY' if total_errors == 0 else '❌ NOT READY'}")
        
        return total_errors == 0
    
    def validate(self):
        """Run complete validation"""
        print("🔍 Wonder Discord Bot - Deployment Validation")
        print("="*50)
        
        validation_steps = [
            ("Python version", self.check_python_version),
            ("Required files", self.check_required_files),
            ("Dependencies", self.check_dependencies),
            ("Environment config", self.check_environment_config),
            ("Config JSON", self.check_config_json),
            ("Bot imports", self.check_bot_imports),
            ("Deployment files", self.check_deployment_files),
            ("File permissions", self.check_permissions),
            ("Bot initialization", self.test_bot_initialization),
            ("Database setup", self.check_database_setup),
        ]
        
        for step_name, step_func in validation_steps:
            try:
                step_func()
            except Exception as e:
                self.log_error(f"{step_name} validation failed: {e}")
        
        return self.generate_report()

def main():
    """Main validation function"""
    try:
        validator = DeploymentValidator()
        success = validator.validate()
        
        if success:
            print("\n🚀 Next steps:")
            print("1. Set your Discord token in .env file")
            print("2. Run: ./start.sh (Unix) or start.bat (Windows)")
            print("3. Deploy to your chosen platform")
        else:
            print("\n🔧 Please fix the errors above before deploying")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()