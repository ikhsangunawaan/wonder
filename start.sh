#!/bin/bash

# Wonder Discord Bot Start Script
# This script ensures the bot runs with the correct Python interpreter

# Find Python executable
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python not found on this system"
    exit 1
fi

echo "Starting Wonder Discord Bot with $PYTHON_CMD..."

# Change to script directory
cd "$(dirname "$0")"

# Run the bot
exec $PYTHON_CMD run.py "$@"