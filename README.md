# 🚀 CompText MCP Server

> Token-efficient Domain-Specific Language for LLM interactions with universal multi-platform support

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

## 🎯 Overview

**CompText MCP Server** provides seamless access to your CompText DSL documentation stored in Notion. Reduce token usage by 90-95% while maintaining full LLM capabilities across multiple AI platforms.

### ✨ Key Features

- ✅ **Universal Compatibility** - Claude, Perplexity, Cursor, Cline, Continue.dev, LM Studio, Jan.ai
- ✅ **Token Efficient** - 25,000 → 500-2,000 tokens (90-95% reduction)
- ✅ **Multi-Platform** - Native MCP + REST API
- ✅ **Production Ready** - Error handling, logging, caching, tests
- ✅ **Easy Setup** - Automated scripts for all platforms

## ⚡ Quick Start

```bash
# Clone
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server

# Setup (auto-installs everything)
bash setup.sh  # macOS/Linux
# or: setup.bat  # Windows

# Configure
cp .env.example .env
# Edit .env: Add your NOTION_API_TOKEN

# Test
python -m pytest tests/ -v

# Start
python -m comptext_mcp.server
```

## 🌐 Supported Platforms

| Platform | Type | Setup | Status |
|----------|------|-------|--------|
| **Claude Desktop** | Native MCP | 2 min | ✅ |
| **Cursor AI** | Native MCP | 3 min | ✅ |
| **Cline (VS Code)** | Native MCP | 2 min | ✅ |
| **Continue.dev** | Native MCP | 3 min | ✅ |
| **Perplexity** | REST API | 5 min | ✅ |
| **ChatGPT** | REST API | 10 min | ✅ |
| **LM Studio** | Native MCP | 3 min | ✅ |
| **Jan.ai** | Native MCP | 3 min | ✅ |
| **Ollama WebUI** | Docker | 10 min | ✅ |

## 📦 Installation

### Prerequisites
- Python 3.10+
- Notion API Token ([Get one](https://www.notion.so/my-integrations))
- CompText Database access

### Quick Install

```bash
# Option 1: Automated
bash setup.sh

# Option 2: Manual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your token
```

## ⚙️ Configuration

### Environment Variables

Create `.env`:
```bash
NOTION_API_TOKEN=ntn_YOUR_TOKEN_HERE
COMPTEXT_DATABASE_ID=0e038c9b52c5466694dbac288280dd93
LOG_LEVEL=INFO
```

### Claude Desktop Setup

**macOS/Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "python3",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/path/to/comptext-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/comptext-mcp-server/src",
        "NOTION_API_TOKEN": "your_token",
        "COMPTEXT_DATABASE_ID": "0e038c9b52c5466694dbac288280dd93"
      }
    }
  }
}
```

### Perplexity Setup (REST API)

```bash
# Start REST API
python rest_api_wrapper.py

# Get public URL
ngrok http 8000
# Use generated URL in Perplexity
```

## 💻 Usage

### Available Tools

1. **list_modules** - List all modules (A-M)
2. **get_module** - Get module details
3. **get_command** - Load page content
4. **search** - Search codex
5. **get_by_tag** - Filter by tags
6. **get_by_type** - Filter by type
7. **get_statistics** - Show stats

### Example Queries

```
# In Claude/Cursor
"Show me all CompText modules"
"Search for docker commands"
"What's in Module B?"

# In Perplexity (REST API)
"Call https://your-api.com/api/search?query=docker"
```

## 🌐 REST API

Start server:
```bash
python rest_api_wrapper.py
```

Endpoints:
- `GET /api/modules` - List all
- `GET /api/modules/{A-M}` - Get module
- `GET /api/search?query=X` - Search
- `GET /api/command/{id}` - Get page
- `GET /health` - Health check

Docs: http://localhost:8000/docs

## 🚀 Deployment

### Railway (Production)

```bash
npm install -g @railway/cli
railway login
railway init
railway variables set NOTION_API_TOKEN="your_token"
railway up
railway domain
```

### Docker

```bash
docker build -f Dockerfile.rest -t comptext-api .
docker run -p 8000:8000 \
  -e NOTION_API_TOKEN="your_token" \
  comptext-api
```

### ngrok (Temporary)

```bash
python rest_api_wrapper.py  # Terminal 1
ngrok http 8000            # Terminal 2
```

## 👨‍💻 Development

### Run Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
pytest tests/ --cov=src/comptext_mcp
```

### Code Quality

```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 🔧 Troubleshooting

### MCP Server doesn't start

```bash
# Check Python version
python --version  # Must be 3.10+

# Test connection
python -c "from comptext_mcp.notion_client import get_all_modules; print(len(get_all_modules()))"
```

### Tools not in Claude

1. Check config path
2. Use absolute paths
3. Verify PYTHONPATH
4. Check logs: `~/.config/claude/logs/mcp*.log`
5. Restart Claude

## 📚 Documentation

Detailed guides available in Notion:
- [Complete Setup Guide](https://www.notion.so/0d571dc857144b199243ea951d60cef6)
- [Multi-Platform Integration](https://www.notion.so/2bf757a849b9812f955bd542456e6fe3)
- [Perplexity Integration](https://www.notion.so/2bf757a849b98139b674e10334b5d89f)
- [Public API URL Setup](https://www.notion.so/2bf757a849b98121a86df6a4b7d0b18e)

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.

## 📜 License

MIT License - see [LICENSE](LICENSE)

## 🚀 Links

- **Documentation**: [Notion Integration](https://www.notion.so/0d571dc857144b199243ea951d60cef6)
- **Issues**: [GitHub Issues](https://github.com/ProfRandom92/comptext-mcp-server/issues)
- **MCP SDK**: [Model Context Protocol](https://modelcontextprotocol.io/)

---

Made with ❤️ for CompText DSL