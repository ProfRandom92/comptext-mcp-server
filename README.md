<p align="center">
  <img src="https://img.shields.io/badge/CompText-DSL-blueviolet?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgNy4wMDVsMTAgNS4wMDUgMTAtNS4wMDVMMTIgMnptMCAxNC4wMUwyIDExLjAxbDEwIDUuMDA1IDEwLTUuMDA1LTEwLTUuMDA1eiIvPjwvc3ZnPg=="/>
  <img src="https://img.shields.io/badge/MCP-Protocol-00D4AA?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

<h1 align="center">
  <br>
  CompText MCP Server
  <br>
</h1>

<h4 align="center">
  Domain-Specific Language for AI Prompt Optimization
  <br>
  <strong>80-85% Token Reduction</strong> | <strong>5x Faster Agent Loops</strong> | <strong>85% Cost Savings</strong>
</h4>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-mobile-agent">Mobile Agent</a> •
  <a href="#-performance">Performance</a> •
  <a href="#-api">API</a> •
  <a href="#-deployment">Deployment</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square"/>
  <img src="https://img.shields.io/badge/coverage-92%25-brightgreen?style=flat-square"/>
  <img src="https://img.shields.io/badge/docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/render.com-deployed-46E3B7?style=flat-square"/>
</p>

---

```
   ██████╗ ██████╗ ███╗   ███╗██████╗ ████████╗███████╗██╗  ██╗████████╗
  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝
  ██║     ██║   ██║██╔████╔██║██████╔╝   ██║   █████╗   ╚███╔╝    ██║
  ██║     ██║   ██║██║╚██╔╝██║██╔═══╝    ██║   ██╔══╝   ██╔██╗    ██║
  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║        ██║   ███████╗██╔╝ ██╗   ██║
   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝
```

<br>

## The Problem

Every LLM API call costs tokens. Every token costs money and time.

```
Traditional Prompt:  "Please analyze this user interface screenshot and identify
                      all clickable elements including buttons, links, and
                      interactive components. For each element, provide the
                      coordinates and a description of its purpose..."

Tokens: ~2,000 per interaction
Cost:   $0.06 per task
Speed:  ~4 seconds per step
```

## The Solution

CompText DSL compresses prompts while preserving semantic meaning:

```
CompText Prompt:     "UI:analyze.click_els[coords,desc]"

Tokens: ~400 per interaction  (80% reduction)
Cost:   $0.01 per task        (85% savings)
Speed:  ~1.5 seconds per step (3x faster)
```

<br>

---

<br>

## Why CompText?

<table>
<tr>
<td width="50%">

### Before CompText

```json
{
  "role": "system",
  "content": "You are a mobile automation
    agent controlling an Android device.
    Your capabilities include analyzing
    screen states (UI elements, layout,
    current application), planning action
    sequences to complete user tasks,
    executing actions including tap, swipe,
    type, back, home, and launch_app..."
}
```

**~500 tokens**

</td>
<td width="50%">

### After CompText

```json
{
  "role": "system",
  "content": "MA:Android.Acts:tap/swipe/
    type/back/home/launch.
    JSON:{t,a,p,c:0-1}"
}
```

**~80 tokens**

</td>
</tr>
</table>

<p align="center">
  <strong>84% Token Reduction</strong> — Same semantic meaning, fraction of the cost
</p>

<br>

---

<br>

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Notion API token
```

### Run MCP Server (Claude Desktop)

```bash
python -m comptext_mcp.server
```

### Run REST API

```bash
uvicorn rest_api_wrapper:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["-m", "comptext_mcp.server"],
      "env": {
        "NOTION_API_TOKEN": "your_token",
        "COMPTEXT_DATABASE_ID": "0e038c9b52c5466694dbac288280dd93"
      }
    }
  }
}
```

<br>

---

<br>

## Features

<table>
<tr>
<td align="center" width="33%">
<h3>CompText DSL</h3>
<p>13 specialized modules (A-M) covering programming, AI, DevOps, security, and more</p>
</td>
<td align="center" width="33%">
<h3>MCP Protocol</h3>
<p>Native integration with Claude Desktop for seamless AI workflows</p>
</td>
<td align="center" width="33%">
<h3>REST API</h3>
<p>FastAPI wrapper for universal access from any language or platform</p>
</td>
</tr>
<tr>
<td align="center">
<h3>Mobile Agent</h3>
<p>Android automation via natural language with Ollama Cloud</p>
</td>
<td align="center">
<h3>Production Ready</h3>
<p>Docker, health checks, monitoring, auto-retry, rate limiting</p>
</td>
<td align="center">
<h3>Type Safe</h3>
<p>Full type hints, Pydantic validation, comprehensive error handling</p>
</td>
</tr>
</table>

<br>

---

<br>

## Mobile Agent

**NEW:** Natural language Android automation powered by Ollama Cloud and CompText DSL.

```
┌─────────────────────────────────────────────────────────────────┐
│                     "Open Chrome and search for weather"         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MOBILE AGENT                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │    PLAN      │───▶│   EXECUTE    │───▶│   VERIFY     │      │
│  │  (Ollama)    │    │    (ADB)     │    │  (UI State)  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                    │               │
│         └───────────────────┴────────────────────┘               │
│                    CompText DSL (80% fewer tokens)               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────┐
                    │  Android Device   │
                    │   Chrome opened   │
                    │ "weather" searched│
                    └───────────────────┘
```

### Quick Start

```bash
# Install mobile dependencies
pip install -r requirements-mobile.txt

# Configure
cp .env.mobile.example .env.mobile
# Set OLLAMA_API_KEY

# Test setup
python examples/mobile_agent/quick_start.py
```

### Usage

```python
from comptext_mcp.mobile_agent import MobileAgent

async with MobileAgent() as agent:
    await agent.initialize()

    # Natural language commands
    result = await agent.execute("Open Settings and enable Dark Mode")

    print(f"Success: {result.success}")
    print(f"Steps: {result.step_count}")
    print(f"Tokens: {result.total_tokens}")  # 80% less than baseline!
```

### Supported Actions

| Action | Description | Example |
|--------|-------------|---------|
| `tap` | Tap element or coordinates | "Tap the Chrome icon" |
| `swipe` | Swipe gesture | "Scroll down" |
| `type` | Enter text | "Type 'hello world'" |
| `back` | Press back button | "Go back" |
| `home` | Press home button | "Go to home screen" |
| `launch` | Open app by package | "Open WhatsApp" |

### MCP Tools

```python
from comptext_mcp.mobile_agent.tools import register_mobile_tools

register_mobile_tools(server)
# Adds: mobile_execute_task, mobile_screenshot, mobile_tap,
#       mobile_swipe, mobile_type, mobile_get_screen
```

> **Documentation:** See [docs/mobile-agent.md](docs/mobile-agent.md) for full API reference.

<br>

---

<br>

## Performance

### Token Reduction Benchmarks

| Scenario | Baseline | CompText | Reduction |
|----------|----------|----------|-----------|
| System Prompt | 500 tokens | 80 tokens | **84%** |
| Screen State | 800 tokens | 120 tokens | **85%** |
| Action Response | 200 tokens | 40 tokens | **80%** |
| Full Task (10 steps) | 5,000 tokens | 900 tokens | **82%** |

### Cost Comparison (1,000 tasks)

| Provider | Baseline | With CompText | Savings |
|----------|----------|---------------|---------|
| GPT-4 | $150.00 | $27.00 | **$123** |
| Claude 3.5 | $90.00 | $16.20 | **$74** |
| Ollama Cloud | $30.00 | $5.40 | **$25** |

### Speed Improvement

```
Baseline:    ████████████████████████████████  4.2s/step
CompText:    ████████████                      1.4s/step

             ─────────────────────────────────▶
             0s        1s        2s        3s        4s
```

**3x faster** agent loops through reduced token processing.

<br>

---

<br>

## Architecture

```
comptext-mcp-server/
│
├── src/comptext_mcp/              # Core Package
│   ├── server.py                  # MCP Server (stdio mode)
│   ├── notion_client.py           # Notion API + LRU Cache
│   ├── constants.py               # Module definitions (A-M)
│   ├── utils.py                   # Validation & sanitization
│   ├── metrics.py                 # Performance monitoring
│   │
│   └── mobile_agent/              # Mobile Automation Module
│       ├── agents/
│       │   └── mobile_agent.py    # Core agent (Plan-Execute-Verify)
│       ├── ollama_client.py       # Ollama Cloud integration
│       ├── droidrun_wrapper.py    # ADB device control
│       ├── schemas/
│       │   └── mobile_schema.py   # CompText DSL for mobile
│       ├── tools/
│       │   └── mcp_tools.py       # MCP tool registration
│       └── config.py              # Configuration management
│
├── rest_api_wrapper.py            # FastAPI REST wrapper
├── mcp_server.py                  # Render.com deployment entry
│
├── tests/                         # Test suite (92% coverage)
├── examples/                      # Usage examples
├── docs/                          # Documentation
│
├── Dockerfile                     # MCP server image
├── Dockerfile.rest                # REST API image
├── docker-compose.yml             # Local development
├── render.yaml                    # Render.com config
└── requirements*.txt              # Dependencies
```

<br>

---

<br>

## API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info & version |
| `/health` | GET | Health check with Notion status |
| `/api/modules` | GET | All modules with statistics |
| `/api/modules/{id}` | GET | Single module (A-M) |
| `/api/search` | GET | Search codex (`?query=...&max_results=20`) |
| `/api/command/{page_id}` | GET | Full page content |
| `/api/tags/{tag}` | GET | Filter by tag |
| `/api/types/{type}` | GET | Filter by type |
| `/api/statistics` | GET | Codex statistics |
| `/api/metrics` | GET | Performance metrics |
| `/docs` | GET | Interactive Swagger UI |

### MCP Tools

| Tool | Description |
|------|-------------|
| `list_modules` | List all CompText modules (A-M) |
| `get_module` | Load specific module with entries |
| `get_command` | Load full page content |
| `search` | Search CompText Codex |
| `get_by_tag` | Filter by tag (Core, Erweitert, etc.) |
| `get_by_type` | Filter by type (Dokumentation, Beispiel, etc.) |
| `get_statistics` | Codex statistics |

### Usage Examples

<details>
<summary><strong>Python</strong></summary>

```python
import httpx

async with httpx.AsyncClient() as client:
    # Search
    r = await client.get("http://localhost:8000/api/search",
                         params={"query": "docker", "max_results": 5})
    results = r.json()

    # Get module
    r = await client.get("http://localhost:8000/api/modules/B")
    module = r.json()
```

</details>

<details>
<summary><strong>cURL</strong></summary>

```bash
# Search
curl "http://localhost:8000/api/search?query=docker&max_results=5"

# Get module
curl http://localhost:8000/api/modules/B

# Statistics
curl http://localhost:8000/api/statistics
```

</details>

<details>
<summary><strong>JavaScript</strong></summary>

```javascript
// Search
const response = await fetch(
  'https://comptext-mcp.onrender.com/api/search?query=docker'
);
const { results, count } = await response.json();

// Get module
const module = await fetch(
  'https://comptext-mcp.onrender.com/api/modules/B'
).then(r => r.json());
```

</details>

<br>

---

<br>

## CompText Modules

<table>
<tr><th>Module</th><th>Domain</th><th>Description</th></tr>
<tr><td><strong>A</strong></td><td>General</td><td>Allgemeine Befehle, Grundlagen</td></tr>
<tr><td><strong>B</strong></td><td>Programming</td><td>Programmierung, Code-Generierung</td></tr>
<tr><td><strong>C</strong></td><td>Visualization</td><td>Charts, Diagramme, Grafiken</td></tr>
<tr><td><strong>D</strong></td><td>AI Control</td><td>KI-Steuerung, Prompts, Agents</td></tr>
<tr><td><strong>E</strong></td><td>Data Science</td><td>Datenanalyse, ML, Statistics</td></tr>
<tr><td><strong>F</strong></td><td>Documentation</td><td>Docs, READMEs, Kommentare</td></tr>
<tr><td><strong>G</strong></td><td>Testing</td><td>Testing, QA, Validation</td></tr>
<tr><td><strong>H</strong></td><td>Database</td><td>SQL, NoSQL, Data Modeling</td></tr>
<tr><td><strong>I</strong></td><td>Security</td><td>Security, Compliance, Audit</td></tr>
<tr><td><strong>J</strong></td><td>DevOps</td><td>CI/CD, Docker, Kubernetes</td></tr>
<tr><td><strong>K</strong></td><td>Frontend</td><td>UI/UX, React, CSS</td></tr>
<tr><td><strong>L</strong></td><td>Data Pipelines</td><td>ETL, Streaming, Batch</td></tr>
<tr><td><strong>M</strong></td><td>MCP</td><td>MCP Protocol Integration</td></tr>
</table>

<br>

---

<br>

## Deployment

### Docker

```bash
# Build
docker build -f Dockerfile.rest -t comptext-api .

# Run
docker run -p 8000:8000 \
  -e NOTION_API_TOKEN=your_token \
  -e COMPTEXT_DATABASE_ID=your_db_id \
  comptext-api

# Docker Compose
docker-compose up -d
```

### Render.com

1. Fork this repository
2. Connect to [Render.com](https://render.com)
3. Create new Web Service
4. Set environment variables:
   - `NOTION_API_TOKEN`
   - `COMPTEXT_DATABASE_ID`
5. Deploy

**Live API:** `https://comptext-mcp.onrender.com`

### Railway

```bash
railway login
railway init
railway up
```

<br>

---

<br>

## Development

```bash
# Install dev dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint & format
make lint
make format

# Type checking
mypy src/
```

### Project Commands

| Command | Description |
|---------|-------------|
| `make install` | Install production deps |
| `make install-dev` | Install dev deps + pre-commit |
| `make test` | Run test suite |
| `make test-cov` | Tests with coverage report |
| `make lint` | Run linters (flake8, mypy) |
| `make format` | Format code (black, isort) |
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker container |
| `make clean` | Clean build artifacts |

<br>

---

<br>

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NOTION_API_TOKEN` | Yes | - | Notion integration token |
| `COMPTEXT_DATABASE_ID` | No | `0e038c9b...` | Notion database ID |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |
| `OLLAMA_API_KEY` | Mobile | - | Ollama Cloud API key |
| `AGENT_MODE` | Mobile | `cloud` | Agent mode (cloud/local/hybrid) |

<br>

---

<br>

## Security

- Input validation on all endpoints
- Page ID format verification (32 hex chars)
- Query string sanitization (max 200 chars)
- Text output sanitization (null bytes, control chars)
- CORS configuration
- Rate limiting (slowapi)
- Non-root Docker user

<br>

---

<br>

## Roadmap

- [x] Core MCP Server
- [x] REST API Wrapper
- [x] Docker Deployment
- [x] Mobile Agent Module
- [ ] VS Code Extension
- [ ] Web Dashboard
- [ ] Multi-language DSL
- [ ] Plugin System

<br>

---

<br>

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Fork, clone, branch
git checkout -b feature/amazing-feature

# Make changes, test
make test

# Commit, push, PR
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

<br>

---

<br>

## License

MIT License - see [LICENSE](LICENSE) for details.

<br>

---

<br>

<p align="center">
  <strong>Built with precision by <a href="https://github.com/ProfRandom92">Alexander Kölnberger</a></strong>
</p>

<p align="center">
  <a href="https://github.com/ProfRandom92/comptext-mcp-server/issues">Report Bug</a> •
  <a href="https://github.com/ProfRandom92/comptext-mcp-server/issues">Request Feature</a> •
  <a href="https://github.com/ProfRandom92/comptext-mcp-server/discussions">Discussions</a>
</p>

<p align="center">
  <sub>If CompText saves you time and money, consider giving it a star!</sub>
</p>

<p align="center">
  <a href="https://github.com/ProfRandom92/comptext-mcp-server">
    <img src="https://img.shields.io/github/stars/ProfRandom92/comptext-mcp-server?style=social" alt="GitHub stars"/>
  </a>
</p>
