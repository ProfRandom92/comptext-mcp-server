#!/bin/bash
# CompText MCP Server - Setup Script
set -e

echo "🚀 CompText MCP Server Setup"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Python
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo "${GREEN}✓${NC} Python found"

# Create structure
echo ""
echo "📝 Creating project structure..."
mkdir -p src/comptext_mcp tests logs
echo "${GREEN}✓${NC} Structure created"

# Create venv
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "${YELLOW}!${NC} venv exists"
else
    python3 -m venv venv
    echo "${GREEN}✓${NC} venv created"
fi

# Activate
echo ""
echo "⚙️ Activating venv..."
source venv/bin/activate
echo "${GREEN}✓${NC} Activated"

# Install
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "${GREEN}✓${NC} Installed"

# Create .env
echo ""
echo "🔑 Setting up .env..."
if [ -f ".env" ]; then
    echo "${YELLOW}!${NC} .env exists"
else
    cp .env.example .env
    echo "${GREEN}✓${NC} .env created"
    echo "${YELLOW}!${NC} Edit .env and add NOTION_API_TOKEN"
fi

echo ""
echo "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your NOTION_API_TOKEN"
echo "2. Test: python -c 'from comptext_mcp.notion_client import get_all_modules; print(len(get_all_modules()))'"
echo "3. Start: python -m comptext_mcp.server"
