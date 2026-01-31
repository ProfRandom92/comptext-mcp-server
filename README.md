# 🚀 CompText MCP Server
### Token-efficient DSL server for MCP, REST, and mobile agents

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK 1.1.0](https://img.shields.io/badge/MCP-1.1.0-00D4AA.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

CompText compiles verbose instructions into a compact DSL to cut LLM token usage by up to 90–95%. This repository ships a production-ready MCP server, REST gateway, and a mobile automation agent.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
  - [MCP Server](#mcp-server)
  - [REST API](#rest-api)
  - [Mobile Agent CLI](#mobile-agent-cli)
- [Testing & Linting](#testing--linting)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

---

## Overview
CompText MCP Server exposes the CompText DSL through:
- **MCP** for native tool access (Claude Desktop, Cursor, etc.)
- **REST** for HTTP clients (Perplexity, ChatGPT API-style callers)
- **Mobile agent** for Android automation with minimal tokens

All services share the same validation, caching, metrics, and security hardening described in [`OPTIMIZATION_SUMMARY.md`](OPTIMIZATION_SUMMARY.md).

## Features
- Token-efficient DSL with caching and input validation
- Dual interfaces: MCP server and REST wrapper
- Mobile agent with Ollama/Cloud modes and Prometheus metrics
- Rate limiting, sanitization, and structured logging
- Docker support plus Railway/render configs
- **GitHub repository automation**: Audit, auto-merge PRs, and manage default branches

## Architecture
```
Client (MCP / REST / Mobile) -> CompText Server -> Data Source (Local JSON or Notion)
                                   |-> Validation & rate limiting
                                   |-> Metrics & logging
                                   |-> Caching layer
```

### Data Sources
The server supports two data source modes:
- **Local JSON** (default): Uses `data/codex.json` for fast, offline access
- **Notion API**: Uses Notion database for cloud-based content management

Switch between modes using the `COMPTEXT_DATA_SOURCE` environment variable.

## Prerequisites
- Python 3.10+
- (Optional) Notion API token if using Notion as data source
- Recommended: virtualenv

## Quick Start
```bash
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

pip install -e .[rest,mobile]
cp .env.example .env

# Option 1: Use local JSON (default, no additional config needed)
python -m comptext_mcp.server

# Option 2: Use Notion API (edit .env first)
# Set COMPTEXT_DATA_SOURCE=notion
# Fill in NOTION_API_TOKEN and COMPTEXT_DATABASE_ID
python -m comptext_mcp.server

# (Optional) Start REST API
python rest_api_wrapper.py
```

## Configuration
All configuration uses environment variables (see [.env.example](.env.example)):

### Data Source Configuration
- `COMPTEXT_DATA_SOURCE` – Data source: "local" (default) or "notion"
- `COMPTEXT_CODEX_PATH` – Path to local JSON file (default: "data/codex.json")

### Notion API Configuration (only if using Notion)
- `NOTION_API_TOKEN` – Notion API token
- `COMPTEXT_DATABASE_ID` – Notion database ID

### Other Configuration
- `GITHUB_TOKEN` – GitHub API token (for automation features)
- `HOST` / `PORT` – REST server host/port
- `LOG_LEVEL` – Logging level

## Usage
### MCP Server
Add to your MCP client (example for Claude Desktop):

**Using Local JSON (default):**
```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "python3",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/path/to/comptext-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/comptext-mcp-server/src",
        "COMPTEXT_DATA_SOURCE": "local",
        "COMPTEXT_CODEX_PATH": "data/codex.json"
      }
    }
  }
}
```

**Using Notion API:**
```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "python3",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/path/to/comptext-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/comptext-mcp-server/src",
        "COMPTEXT_DATA_SOURCE": "notion",
        "NOTION_API_TOKEN": "your_token",
        "COMPTEXT_DATABASE_ID": "0e038c9b52c5466694dbac288280dd93"
      }
    }
  }
}
```

### REST API
```bash
python rest_api_wrapper.py
curl http://localhost:8000/health
```
See [`docs/API.md`](docs/API.md) for endpoints, rate limits, and examples.

### Mobile Agent CLI
```bash
comptext-mobile run "Open Chrome and search for weather" --steps 10
comptext-mobile status
comptext-mobile screenshot --output screen.png
```
Configure via environment or a config file; details in [`docs/mobile-agent.md`](docs/mobile-agent.md).

## Testing & Linting
```bash
pip install -e .[dev]
pytest
black . && flake8 && mypy
```

## Documentation
- [Quick Start](docs/QUICKSTART.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [GitHub Automation](docs/GITHUB_AUTOMATION.md)
- [FAQ](docs/FAQ.md)
- [Optimization Summary](OPTIMIZATION_SUMMARY.md)

## Contributing
We welcome issues and PRs. Please see [CONTRIBUTING.md](CONTRIBUTING.md) and follow the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security
Report vulnerabilities via [SECURITY.md](SECURITY.md). The project uses input validation, rate limiting, and CodeQL scanning (see CI).

## License
MIT © [ProfRandom92](https://github.com/ProfRandom92)
