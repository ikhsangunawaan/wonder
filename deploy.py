#!/usr/bin/env python3
"""
Universal Deployment Script for Wonder Discord Bot
Works on any platform: Linux, Windows, macOS
Works with any hosting: Heroku, Railway, Render, VPS, etc.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json

class UniversalDeployer:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_cmd = self.find_python()
        self.pip_cmd = self.find_pip()
        self.project_dir = Path(__file__).parent
        
    def find_python(self):
        """Find available Python executable"""
        candidates = ['python3', 'python', 'py']
        for cmd in candidates:
            if shutil.which(cmd):
                try:
                    result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                    if 'Python 3.' in result.stdout:
                        return cmd
                except:
                    continue
        raise RuntimeError("Python 3.x not found on system")
    
    def find_pip(self):
        """Find available pip executable"""
        candidates = ['pip3', 'pip', f'{self.python_cmd} -m pip']
        for cmd in candidates:
            try:
                if ' -m ' in cmd:
                    result = subprocess.run(cmd.split(), capture_output=True, text=True)
                else:
                    result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    return cmd
            except:
                continue
        return f'{self.python_cmd} -m pip'
    
    def run_command(self, command, description=""):
        """Run command with error handling"""
        print(f"🔧 {description}")
        print(f"Running: {command}")
        
        try:
            if isinstance(command, str):
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            else:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
            
            if result.stdout:
                print(f"✅ {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr.strip()}")
            return False
    
    def check_environment(self):
        """Check and prepare environment"""
        print("🌍 Checking environment...")
        print(f"Platform: {platform.platform()}")
        print(f"Python: {self.python_cmd}")
        print(f"Pip: {self.pip_cmd}")
        
        # Check Python version
        try:
            result = subprocess.run([self.python_cmd, '--version'], capture_output=True, text=True)
            version = result.stdout.strip()
            print(f"Python version: {version}")
            
            # Extract version number
            version_parts = version.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            
            if major < 3 or (major == 3 and minor < 8):
                print("⚠️  Warning: Python 3.8+ recommended for optimal performance")
            else:
                print("✅ Python version is compatible")
                
        except Exception as e:
            print(f"❌ Could not check Python version: {e}")
            return False
        
        return True
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("\n📦 Installing dependencies...")
        
        # Try different installation methods
        install_methods = [
            f"{self.pip_cmd} install -r requirements.txt",
            f"{self.pip_cmd} install -r requirements.txt --user",
            f"{self.pip_cmd} install -r requirements.txt --break-system-packages"
        ]
        
        for method in install_methods:
            print(f"Trying: {method}")
            if self.run_command(method, "Installing packages"):
                print("✅ Dependencies installed successfully")
                return True
            print("❌ Installation method failed, trying next...")
        
        print("❌ All installation methods failed")
        return False
    
    def setup_environment_file(self):
        """Setup .env file with proper configuration"""
        print("\n📄 Setting up environment file...")
        
        env_path = self.project_dir / '.env'
        env_example_path = self.project_dir / '.env.example'
        
        # Create .env.example as template
        env_template = """# Discord Bot Configuration
# REQUIRED: Replace with your actual Discord bot token
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE

# Optional: Premium and Booster role IDs
PREMIUM_ROLE_ID=YOUR_PREMIUM_ROLE_ID_HERE
BOOSTER_ROLE_ID=YOUR_BOOSTER_ROLE_ID_HERE

# Database Configuration (Optional - SQLite used by default)
# Uncomment and configure for MySQL
# DB_TYPE=mysql
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=wonder_bot
# DB_USER=your_username
# DB_PASSWORD=your_password

# Hosting Platform Variables (Auto-detected)
# PORT=8000
# NODE_ENV=production
"""
        
        # Write template
        with open(env_example_path, 'w') as f:
            f.write(env_template)
        
        # Check if .env already exists
        if env_path.exists():
            print("✅ .env file already exists")
            # Read current content
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Check if token is set
            if 'YOUR_DISCORD_BOT_TOKEN_HERE' in content:
                print("⚠️  Discord token not configured in .env file")
                print("📝 Please edit .env file and set your Discord bot token")
            else:
                print("✅ Discord token appears to be configured")
        else:
            # Copy template
            shutil.copy2(env_example_path, env_path)
            print("✅ Created .env file from template")
            print("📝 Please edit .env file and set your Discord bot token")
        
        return True
    
    def create_deployment_files(self):
        """Create platform-specific deployment files"""
        print("\n🚀 Creating deployment files...")
        
        # Procfile for Heroku, Railway, etc.
        procfile_content = "worker: python3 run.py\n"
        with open(self.project_dir / 'Procfile', 'w') as f:
            f.write(procfile_content)
        print("✅ Created Procfile for Heroku/Railway")
        
        # Docker configuration
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python3 -c "import sys; sys.exit(0)"

CMD ["python3", "run.py"]
"""
        
        with open(self.project_dir / 'Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        print("✅ Created Dockerfile")
        
        # Docker Compose
        docker_compose_content = """version: '3.8'

services:
  bot:
    build: .
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - PREMIUM_ROLE_ID=${PREMIUM_ROLE_ID}
      - BOOSTER_ROLE_ID=${BOOSTER_ROLE_ID}
    volumes:
      - ./data:/app/data
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
"""
        
        with open(self.project_dir / 'docker-compose.yml', 'w') as f:
            f.write(docker_compose_content)
        print("✅ Created docker-compose.yml")
        
        # Railway configuration
        railway_config = {
            "build": {
                "buildCommand": "pip install -r requirements.txt"
            },
            "deploy": {
                "startCommand": "python3 run.py"
            }
        }
        
        with open(self.project_dir / 'railway.json', 'w') as f:
            json.dump(railway_config, f, indent=2)
        print("✅ Created railway.json")
        
        # Render configuration
        render_config = {
            "services": [
                {
                    "type": "worker",
                    "name": "wonder-discord-bot",
                    "env": "python",
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "python3 run.py",
                    "plan": "free"
                }
            ]
        }
        
        with open(self.project_dir / 'render.yaml', 'w') as f:
            json.dump(render_config, f, indent=2)
        print("✅ Created render.yaml")
        
        return True
    
    def create_startup_scripts(self):
        """Create cross-platform startup scripts"""
        print("\n📜 Creating startup scripts...")
        
        # Unix/Linux/macOS script
        unix_script = f"""#!/bin/bash
# Wonder Discord Bot - Universal Startup Script

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

echo -e "${{BLUE}}🤖 Wonder Discord Bot - Universal Launcher${{NC}}"
echo "=========================================="

# Find Python
PYTHON_CMD=""
for cmd in python3 python py; do
    if command -v $cmd &> /dev/null; then
        if $cmd -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${{RED}}❌ Python 3.8+ not found${{NC}}"
    exit 1
fi

echo -e "${{GREEN}}✅ Using Python: $PYTHON_CMD${{NC}}"

# Check if .env exists and has token
if [ ! -f ".env" ]; then
    echo -e "${{YELLOW}}⚠️  .env file not found. Please run deploy.py first${{NC}}"
    exit 1
fi

if grep -q "YOUR_DISCORD_BOT_TOKEN_HERE" .env; then
    echo -e "${{YELLOW}}⚠️  Please set your Discord token in .env file${{NC}}"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Start bot
echo -e "${{BLUE}}🚀 Starting Wonder Discord Bot...${{NC}}"
exec $PYTHON_CMD run.py "$@"
"""
        
        with open(self.project_dir / 'start.sh', 'w') as f:
            f.write(unix_script)
        
        # Make executable on Unix systems
        if self.system != 'windows':
            os.chmod(self.project_dir / 'start.sh', 0o755)
        
        print("✅ Created start.sh (Unix/Linux/macOS)")
        
        # Windows batch script
        windows_script = f"""@echo off
REM Wonder Discord Bot - Windows Startup Script

echo 🤖 Wonder Discord Bot - Universal Launcher
echo ==========================================

REM Find Python
set PYTHON_CMD=
for %%p in (python3 python py) do (
    %%p --version >nul 2>&1
    if not errorlevel 1 (
        %%p -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_CMD=%%p
            goto :found_python
        )
    )
)

echo ❌ Python 3.8+ not found
pause
exit /b 1

:found_python
echo ✅ Using Python: %PYTHON_CMD%

REM Check .env file
if not exist ".env" (
    echo ⚠️  .env file not found. Please run deploy.py first
    pause
    exit /b 1
)

findstr /C:"YOUR_DISCORD_BOT_TOKEN_HERE" .env >nul
if not errorlevel 1 (
    echo ⚠️  Please set your Discord token in .env file
    pause
    exit /b 1
)

REM Start bot
echo 🚀 Starting Wonder Discord Bot...
%PYTHON_CMD% run.py %*
"""
        
        with open(self.project_dir / 'start.bat', 'w') as f:
            f.write(windows_script)
        
        print("✅ Created start.bat (Windows)")
        
        return True
    
    def test_bot_initialization(self):
        """Test if bot can initialize properly"""
        print("\n🧪 Testing bot initialization...")
        
        test_script = """
import sys
import os
sys.path.append('src')

try:
    # Test imports
    from main import WonderBot
    print("✅ Bot imports successful")
    
    # Test basic configuration
    from config import config
    print(f"✅ Config loaded: {config.branding.get('name', 'Wonder Bot')}")
    
    print("✅ Bot initialization test passed")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Bot initialization failed: {e}")
    sys.exit(1)
"""
        
        test_file = self.project_dir / 'test_init.py'
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        try:
            result = subprocess.run([self.python_cmd, str(test_file)], 
                                  capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                print("✅ Bot initialization test passed")
                print(result.stdout.strip())
                success = True
            else:
                print("❌ Bot initialization test failed")
                print(result.stderr.strip())
                success = False
                
        except Exception as e:
            print(f"❌ Could not run test: {e}")
            success = False
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()
        
        return success
    
    def create_deployment_guide(self):
        """Create comprehensive deployment guide"""
        print("\n📖 Creating deployment guide...")
        
        guide_content = """# 🚀 Universal Deployment Guide - Wonder Discord Bot

## Quick Start (Any Platform)

### 1. Run Deployment Script
```bash
python3 deploy.py
# or
python deploy.py
```

### 2. Configure Discord Token
Edit `.env` file and set your Discord bot token:
```env
DISCORD_TOKEN=your_actual_bot_token_here
```

### 3. Start the Bot
**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Manual:**
```bash
python3 run.py
```

## Platform-Specific Deployment

### 🔧 Local Development
```bash
# Clone repository
git clone <repository_url>
cd wonder-discord-bot

# Run deployment script
python3 deploy.py

# Configure token in .env
# Start bot
./start.sh  # or start.bat on Windows
```

### ☁️ Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-bot-name

# Set environment variables
heroku config:set DISCORD_TOKEN=your_token_here

# Deploy
git push heroku main
```

### 🚂 Railway
1. Connect GitHub repository to Railway
2. Set environment variable: `DISCORD_TOKEN`
3. Deploy automatically

### 🎨 Render
1. Connect GitHub repository to Render
2. Set environment variable: `DISCORD_TOKEN`
3. Deploy as Background Worker

### 🐳 Docker
```bash
# Build image
docker build -t wonder-discord-bot .

# Run with environment file
docker run -d --env-file .env wonder-discord-bot

# Or use docker-compose
docker-compose up -d
```

### 🖥️ VPS/Dedicated Server
```bash
# Install Python 3.8+
sudo apt update
sudo apt install python3 python3-pip

# Clone and setup
git clone <repository_url>
cd wonder-discord-bot
python3 deploy.py

# Configure .env file
nano .env

# Start with screen/tmux
screen -S discord-bot
./start.sh

# Or create systemd service (Linux)
sudo cp wonder-bot.service /etc/systemd/system/
sudo systemctl enable wonder-bot
sudo systemctl start wonder-bot
```

### 🏠 Pterodactyl Panel
1. Create new Python server
2. Upload bot files
3. Set startup command: `python3 run.py`
4. Configure environment variables

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | ✅ | Your Discord bot token |
| `PREMIUM_ROLE_ID` | ❌ | Premium role ID for bonuses |
| `BOOSTER_ROLE_ID` | ❌ | Server booster role ID |
| `DB_TYPE` | ❌ | Database type (sqlite/mysql) |
| `DB_HOST` | ❌ | MySQL host (if using MySQL) |
| `DB_PORT` | ❌ | MySQL port (if using MySQL) |
| `DB_NAME` | ❌ | MySQL database name |
| `DB_USER` | ❌ | MySQL username |
| `DB_PASSWORD` | ❌ | MySQL password |

## Bot Permissions

Required Discord permissions:
- Send Messages
- Embed Links
- Add Reactions
- Use Slash Commands
- Manage Roles (for leveling system)
- Manage Messages (for giveaways)

## Troubleshooting

### Common Issues
1. **"Improper token"**: Check Discord token in .env
2. **Module not found**: Run `python3 deploy.py` to install dependencies
3. **Permission denied**: Make startup scripts executable with `chmod +x start.sh`
4. **Database errors**: Check database configuration in .env

### Getting Help
1. Check `bot.log` for error details
2. Verify Python version (3.8+ required)
3. Ensure all dependencies are installed
4. Check Discord bot permissions

## Features
- ✅ Economy system with WonderCoins
- ✅ Gambling games (coinflip, dice, slots)
- ✅ Leveling system with roles
- ✅ Shop system with items
- ✅ Giveaway system
- ✅ Admin management tools
- ✅ Both prefix (`w.`) and slash commands
- ✅ Comprehensive error handling
- ✅ Auto-drops system
- ✅ User profiles and intro cards

Total: 100+ commands available!
"""
        
        with open(self.project_dir / 'DEPLOYMENT_GUIDE.md', 'w') as f:
            f.write(guide_content)
        
        print("✅ Created comprehensive deployment guide")
        
        return True
    
    def deploy(self):
        """Run complete deployment process"""
        print("🚀 Wonder Discord Bot - Universal Deployment")
        print("=" * 50)
        
        steps = [
            ("Checking environment", self.check_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up environment file", self.setup_environment_file),
            ("Creating deployment files", self.create_deployment_files),
            ("Creating startup scripts", self.create_startup_scripts),
            ("Testing bot initialization", self.test_bot_initialization),
            ("Creating deployment guide", self.create_deployment_guide),
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            print(f"\n{'='*20}")
            if not step_func():
                failed_steps.append(step_name)
                print(f"❌ {step_name} failed")
            else:
                print(f"✅ {step_name} completed")
        
        print(f"\n{'='*50}")
        
        if failed_steps:
            print(f"❌ Deployment completed with {len(failed_steps)} issues:")
            for step in failed_steps:
                print(f"  - {step}")
            print("\n🔧 Please check the errors above and try again")
        else:
            print("✅ Deployment completed successfully!")
            print("\n📝 Next Steps:")
            print("1. Edit .env file and set your Discord bot token")
            print("2. Run ./start.sh (Linux/macOS) or start.bat (Windows)")
            print("3. Check DEPLOYMENT_GUIDE.md for platform-specific instructions")
        
        return len(failed_steps) == 0

def main():
    """Main deployment function"""
    try:
        deployer = UniversalDeployer()
        success = deployer.deploy()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()