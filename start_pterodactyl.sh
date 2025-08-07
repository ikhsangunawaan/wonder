#!/bin/bash
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
