# 🚀 CompText MCP Server

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-12%20passed-brightgreen.svg)](tests/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Token-efficient Domain-Specific Language for LLM interactions with universal multi-platform support**

[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Platforms](#-supported-platforms) •
[API](#-rest-api) •
[Deployment](#-deployment)

</div>

---

## 💡 What is CompText MCP Server?

CompText MCP Server provides **seamless access to your CompText DSL documentation** stored in Notion. It dramatically reduces token usage (**90-95% reduction**) while maintaining full LLM capabilities across **9+ AI platforms**.

### ✨ Key Features

- ✅ **Universal Compatibility** - Claude, Perplexity, Cursor, Cline, Continue.dev, LM Studio, Jan.ai, and more
- ✅ **Token Efficient** - 25,000 → 500-2,000 tokens (90-95% reduction)
- ✅ **Dual Interface** - Native MCP Protocol + REST API
- ✅ **Production Ready** - CI/CD, tests, error handling, logging, caching
- ✅ **Easy Setup** - Automated installation scripts for all platforms
- ✅ **Well Documented** - Comprehensive guides and examples
- ✅ **Type Safe** - Full type hints and mypy support
- ✅ **Docker Support** - Container-ready with docker-compose

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server

# 2. Run automated setup
bash setup.sh  # macOS/Linux
# or: setup.bat  # Windows

# 3. Configure environment
cp .env.example .env
# Edit .env and add your NOTION_API_TOKEN

# 4. Test installation
pytest tests/ -v
# Expected: 12 passed ✅

# 5. Start server
python -m comptext_mcp.server  # MCP Server
# or: python rest_api_wrapper.py  # REST API
```

## 🎯 Supported Platforms

| Platform | Interface | Setup Time | Guide | Status |
|----------|-----------|------------|-------|--------|
| **Claude Desktop** | Native MCP | 2 min | [Config](configs/claude_desktop_config.json) | ✅ Production |
| **Cursor AI** | Native MCP | 3 min | [Config](configs/cursor_config.json) | ✅ Production |
| **Cline (VS Code)** | Native MCP | 2 min | [Config](configs/vscode_settings.json) | ✅ Production |
| **Continue.dev** | Native MCP | 3 min | [Docs](docs/QUICKSTART.md) | ✅ Production |
| **Perplexity** | REST API | 5 min | [Guide](docs/API.md) | ✅ Production |
| **ChatGPT** | REST API | 10 min | [Guide](docs/DEPLOYMENT.md) | ✅ Beta |
| **LM Studio** | Native MCP | 3 min | [Docs](docs/QUICKSTART.md) | ✅ Production |
| **Jan.ai** | Native MCP | 3 min | [Docs](docs/QUICKSTART.md) | ✅ Production |
| **Ollama WebUI** | Docker/API | 10 min | [Docker](docker-compose.yml) | ✅ Beta |

## 📦 Installation

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Notion API Token** ([Create one](https://www.notion.so/my-integrations))
- **CompText Database** access (ID: `0e038c9b52c5466694dbac288280dd93`)

### Method 1: Automated Setup (Recommended)

```bash
# macOS/Linux
bash setup.sh

# Windows
setup.bat
```

The script will:
1. ✅ Create virtual environment
2. ✅ Install all dependencies
3. ✅ Set up configuration
4. ✅ Run tests
5. ✅ Provide next steps

### Method 2: Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt

# Configure
cp .env.example .env
# Edit .env with your NOTION_API_TOKEN
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
NOTION_API_TOKEN=ntn_YOUR_TOKEN_HERE
COMPTEXT_DATABASE_ID=0e038c9b52c5466694dbac288280dd93
LOG_LEVEL=INFO  # Optional: DEBUG, INFO, WARNING, ERROR
```

### Platform-Specific Setup

#### Claude Desktop

**Location:**
- macOS/Linux: `~/.config/claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "python3",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/absolute/path/to/comptext-mcp-server",
      "env": {
        "PYTHONPATH": "/absolute/path/to/comptext-mcp-server/src",
        "NOTION_API_TOKEN": "your_token_here",
        "COMPTEXT_DATABASE_ID": "0e038c9b52c5466694dbac288280dd93"
      }
    }
  }
}
```

**Important:** 
- Use **absolute paths** (no ~ or relative paths)
- Restart Claude Desktop after config changes
- Check logs: `~/.config/claude/logs/mcp*.log`

#### Cursor AI

Copy [cursor_config.json](configs/cursor_config.json) to Cursor settings, adjust paths, and restart.

#### VS Code (Cline Extension)

Copy [vscode_settings.json](configs/vscode_settings.json) to `.vscode/settings.json` in your workspace.

#### Perplexity (REST API)

```bash
# Terminal 1: Start API
python rest_api_wrapper.py

# Terminal 2: Create public URL
ngrok http 8000

# Use the ngrok URL in Perplexity
# Example: https://abc123.ngrok-free.app/api/modules
```

## 💻 Usage

### MCP Tools (Native Platforms)

7 powerful tools available:

1. **list_modules** - List all CompText modules (A-M)
2. **get_module** - Get detailed module information
3. **get_command** - Load full page content
4. **search** - Search across entire codex
5. **get_by_tag** - Filter by tags (Core, Extended, etc.)
6. **get_by_type** - Filter by type (Documentation, Example, etc.)
7. **get_statistics** - Show codex statistics

### Example Queries

#### In Claude Desktop / Cursor

```
💬 "Show me all CompText modules"
💬 "Search for docker commands in the codex"
💬 "What's in Module B: Programming?"
💬 "Find all commands tagged as 'Core'"
💬 "Show statistics about the codex"
```

#### In Perplexity (REST API)

```
💬 "Call https://your-api-url.com/api/search?query=docker"
💬 "GET https://your-api-url.com/api/modules/B"
💬 "Fetch https://your-api-url.com/api/statistics"
```

## 🌐 REST API

### Starting the API Server

```bash
# Development
python rest_api_wrapper.py

# Production (with Gunicorn)
gunicorn rest_api_wrapper:app --workers 4 --bind 0.0.0.0:8000
```

API available at: http://localhost:8000

### Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|----------|
| `/health` | GET | Health check | `curl http://localhost:8000/health` |
| `/api/modules` | GET | List all modules | `curl http://localhost:8000/api/modules` |
| `/api/modules/{module}` | GET | Get specific module | `curl http://localhost:8000/api/modules/B` |
| `/api/search` | GET | Search codex | `curl "http://localhost:8000/api/search?query=docker"` |
| `/api/command/{id}` | GET | Get page content | `curl http://localhost:8000/api/command/abc123` |
| `/api/tags/{tag}` | GET | Filter by tag | `curl http://localhost:8000/api/tags/Core` |
| `/api/types/{type}` | GET | Filter by type | `curl http://localhost:8000/api/types/Dokumentation` |
| `/api/statistics` | GET | Get statistics | `curl http://localhost:8000/api/statistics` |
| `/api/cache/clear` | POST | Clear cache | `curl -X POST http://localhost:8000/api/cache/clear` |

### Interactive Documentation

When the API is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Deployment

### Railway (Recommended for Production)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Set environment variables
railway variables set NOTION_API_TOKEN="your_token"
railway variables set COMPTEXT_DATABASE_ID="0e038c9b52c5466694dbac288280dd93"

# Deploy
railway up

# Get public URL
railway domain
# Output: https://comptext-api-production.up.railway.app
```

### Docker

```bash
# Build image
docker build -f Dockerfile.rest -t comptext-api .

# Run container
docker run -p 8000:8000 \
  -e NOTION_API_TOKEN="your_token" \
  -e COMPTEXT_DATABASE_ID="0e038c9b52c5466694dbac288280dd93" \
  comptext-api
```

### Docker Compose

```bash
# Create .env file
echo "NOTION_API_TOKEN=your_token" > .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### ngrok (Development/Testing)

```bash
# Terminal 1: Start API
python rest_api_wrapper.py

# Terminal 2: Create tunnel
ngrok http 8000

# Use the generated URL
# Example: https://abc123.ngrok-free.app
```

**Note:** Free ngrok URLs change on each restart. For permanent URLs, use Railway or similar.

## 👨‍💻 Development

### Setting Up Development Environment

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/comptext_mcp --cov-report=html

# Run specific test
pytest tests/test_suite.py::TestNotionClient::test_get_all_modules -v

# Run tests in parallel
pytest tests/ -n auto
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/ --ignore-missing-imports

# Security check
pip audit
```

### Project Structure

```
comptext-mcp-server/
├── .github/              # GitHub Actions workflows
│   ├── workflows/        # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/   # Issue templates
│   └── pull_request_template.md
├── configs/             # Platform configurations
├── docs/                # Documentation
├── src/                 # Source code
│   └── comptext_mcp/
│       ├── __init__.py
│       ├── notion_client.py  # Notion API client
│       └── server.py         # MCP server
├── tests/               # Test suite
├── rest_api_wrapper.py  # REST API server
├── setup.sh             # Unix setup script
├── setup.bat            # Windows setup script
├── requirements.txt     # Core dependencies
├── requirements-rest.txt # REST API dependencies
├── requirements-dev.txt  # Development dependencies
├── Dockerfile.rest      # Docker image
├── docker-compose.yml   # Docker Compose config
├── railway.json         # Railway deployment
├── .pre-commit-config.yaml
└── README.md
```

## 🔧 Troubleshooting

### MCP Server doesn't start

```bash
# 1. Check Python version
python --version  # Must be 3.10+

# 2. Test Notion connection
python -c "from comptext_mcp.notion_client import get_all_modules; print(f'Modules: {len(get_all_modules())}')" 

# 3. Check environment
echo $NOTION_API_TOKEN
echo $COMPTEXT_DATABASE_ID

# 4. Verify dependencies
pip list | grep mcp
pip list | grep notion
```

### Tools not visible in Claude

1. ✅ **Check config path** - Must use absolute paths
2. ✅ **Verify PYTHONPATH** - Should point to `src/` directory
3. ✅ **Check logs** - `~/.config/claude/logs/mcp*.log`
4. ✅ **Restart Claude** - Quit completely and relaunch
5. ✅ **Test manually** - Run `python -m comptext_mcp.server` in terminal

### REST API errors

```bash
# Check if port is already in use
lsof -i :8000

# Test API health
curl http://localhost:8000/health

# Check logs
tail -f logs/api.log
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'comptext_mcp'` | Set PYTHONPATH correctly |
| `NotionClientError: Invalid token` | Check NOTION_API_TOKEN in .env |
| `Connection refused` | Ensure API server is running |
| `Permission denied` | Make setup.sh executable: `chmod +x setup.sh` |

## 📚 Documentation

### In Repository

- [Quick Start Guide](docs/QUICKSTART.md) - Get started in 5 minutes
- [API Documentation](docs/API.md) - Complete API reference
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Security Policy](SECURITY.md) - Security guidelines
- [Changelog](CHANGELOG.md) - Version history

### In Notion

- [Main Documentation](https://www.notion.so/0d571dc857144b199243ea951d60cef6) - Complete setup guide
- [Multi-Platform Guide](https://www.notion.so/2bf757a849b9812f955bd542456e6fe3) - Platform-specific instructions
- [Perplexity Integration](https://www.notion.so/2bf757a849b98139b674e10334b5d89f) - REST API setup
- [Public URL Setup](https://www.notion.so/2bf757a849b98121a86df6a4b7d0b18e) - Deployment options

## 🪧 Testing

### Test Coverage

```bash
# Run tests with coverage
pytest tests/ --cov=src/comptext_mcp --cov-report=term --cov-report=html

# View HTML report
open htmlcov/index.html
```

Current coverage: **95%+**

### Test Categories

- ✅ **Notion Client** - API interaction tests
- ✅ **Module Structure** - Data validation tests
- ✅ **Search Functionality** - Search algorithm tests
- ✅ **Error Handling** - Exception and edge case tests

### Continuous Integration

GitHub Actions automatically runs:
- ✅ Tests on Python 3.10, 3.11, 3.12
- ✅ Code linting (flake8, black)
- ✅ Type checking (mypy)
- ✅ Security audit
- ✅ Docker build

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Format code: `black src/ tests/`
6. Commit: `git commit -m 'feat: add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Development Workflow

```bash
# Setup
git clone https://github.com/YOUR_USERNAME/comptext-mcp-server.git
cd comptext-mcp-server
pip install -r requirements-dev.txt
pre-commit install

# Make changes
# ...

# Test
pytest tests/ -v
black src/ tests/
flake8 src/ tests/

# Commit
git add .
git commit -m "feat: your feature"
git push
```

## 📦 Versioning

We use [SemVer](http://semver.org/) for versioning. See [CHANGELOG.md](CHANGELOG.md) for version history.

**Current Version:** 1.0.0

## 📊 Project Status

| Metric | Value |
|--------|-------|
| **Version** | 1.0.0 |
| **Status** | ✅ Production Ready |
| **Tests** | 12/12 passing |
| **Coverage** | 95%+ |
| **Python** | 3.10+ |
| **Platforms** | 9+ supported |
| **License** | MIT |
| **Last Updated** | December 2024 |

## 🔒 Security

See [SECURITY.md](SECURITY.md) for security policies and how to report vulnerabilities.

**Best Practices:**
- ✅ Never commit `.env` files
- ✅ Use environment variables for secrets
- ✅ Rotate API tokens regularly
- ✅ Enable HTTPS for production APIs
- ✅ Keep dependencies updated

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP SDK
- [Anthropic](https://www.anthropic.com/) - Claude AI
- [Notion](https://www.notion.so/) - Database platform
- All contributors and users of CompText

## 🔗 Links

- **GitHub Repository**: https://github.com/ProfRandom92/comptext-mcp-server
- **Documentation**: [Notion](https://www.notion.so/0d571dc857144b199243ea951d60cef6)
- **Issues**: [GitHub Issues](https://github.com/ProfRandom92/comptext-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ProfRandom92/comptext-mcp-server/discussions)
- **MCP Protocol**: https://modelcontextprotocol.io/

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=ProfRandom92/comptext-mcp-server&type=Date)](https://star-history.com/#ProfRandom92/comptext-mcp-server&Date)

---

<div align="center">

**Made with ❤️ for the CompText DSL Community**

[Report Bug](https://github.com/ProfRandom92/comptext-mcp-server/issues) ·
[Request Feature](https://github.com/ProfRandom92/comptext-mcp-server/issues) ·
[Documentation](https://www.notion.so/0d571dc857144b199243ea951d60cef6)

</div>