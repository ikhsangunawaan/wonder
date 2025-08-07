@echo off
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
