@echo off
REM CompText MCP Server - Windows Setup

echo 🚀 CompText MCP Server Setup
echo ================================
echo.

echo 🔍 Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    pause
    exit /b 1
)
echo ✓ Python found

echo.
echo 📝 Creating structure...
if not exist "src\comptext_mcp" mkdir src\comptext_mcp
if not exist "tests" mkdir tests
if not exist "logs" mkdir logs
echo ✓ Structure created

echo.
echo 📦 Creating venv...
if exist "venv" (
    echo ! venv exists
) else (
    python -m venv venv
    echo ✓ venv created
)

echo.
echo ⚙️ Activating venv...
call venv\Scripts\activate.bat
echo ✓ Activated

echo.
echo 📦 Installing dependencies...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo ✓ Installed

echo.
echo 🔑 Creating .env...
if exist ".env" (
    echo ! .env exists
) else (
    copy .env.example .env
    echo ✓ .env created
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add NOTION_API_TOKEN
echo 2. Test: python -m comptext_mcp.server
echo.
pause
