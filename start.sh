#!/bin/bash
# Wonder Discord Bot - Universal Startup Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Wonder Discord Bot - Universal Launcher${NC}"
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
    echo -e "${RED}❌ Python 3.8+ not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Using Python: $PYTHON_CMD${NC}"

# Check if .env exists and has token
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please run deploy.py first${NC}"
    exit 1
fi

if grep -q "YOUR_DISCORD_BOT_TOKEN_HERE" .env; then
    echo -e "${YELLOW}⚠️  Please set your Discord token in .env file${NC}"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Start bot
echo -e "${BLUE}🚀 Starting Wonder Discord Bot...${NC}"
exec $PYTHON_CMD run.py "$@"
