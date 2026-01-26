#!/bin/bash
# Quick verification and start script for CompText MCP Server

set -e

echo "=============================================="
echo "🚀 CompText MCP Server - Quick Start"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install package if not already installed
if ! python -c "import comptext_mcp" 2>/dev/null; then
    echo "📥 Installing package..."
    pip install -e . > /dev/null 2>&1
    echo "✅ Package installed"
else
    echo "✅ Package already installed"
fi

# Run comprehensive tests
echo ""
echo "🧪 Running comprehensive tests..."
python test_everything.py

echo ""
echo "=============================================="
echo "✨ System is ready!"
echo "=============================================="
echo ""
echo "Choose how to start:"
echo "  1) MCP Server (for Claude Desktop):  python -m comptext_mcp.server"
echo "  2) REST API Server:                  python mcp_server.py"
echo ""
echo "For Claude Desktop integration, see: CLAUDE_SETUP.md"
echo ""
