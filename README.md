<div align="center">

# 🚀 CompText MCP Server

### Token-Efficient DSL for LLM Interactions
*Reduce token usage by 90-95% with intelligent domain-specific language compilation*

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-1.1.0-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Test Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](https://github.com/ProfRandom92/comptext-mcp-server)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-passing-brightgreen.svg)](https://github.com/ProfRandom92/comptext-mcp-server/actions)

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Documentation](#-documentation) • [Contributing](#-contributing)

![CompText Banner](https://via.placeholder.com/800x200/1a1a1a/00ff00?text=CompText+MCP+Server)

</div>

---

## 📖 Overview

**CompText MCP Server** is a production-ready Model Context Protocol (MCP) server that provides a powerful domain-specific language (DSL) for efficient LLM interactions. By converting natural language requests into optimized CompText commands, it dramatically reduces token usage while maintaining full semantic clarity.

### 🎯 Key Benefits

- **🎨 90-95% Token Reduction** - Compress verbose instructions into canonical DSL
- **🧠 Smart NL Compiler** - Automatic natural language to DSL translation
- **📦 Bundle-First Architecture** - Pre-optimized command bundles for common workflows
- **🔌 Universal Integration** - Works with Claude Desktop, Cursor, VS Code, and custom clients
- **🎭 Audience Profiles** - Tailored output for developers, auditors, and executives
- **⚡ Zero External Dependencies** - All data stored locally in YAML
- **🛡️ Production Ready** - Comprehensive testing, logging, and error handling

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Core Features
- ✅ **Natural Language Compiler** with confidence scoring
- ✅ **13 Specialized Modules** (A-M) with 32+ commands
- ✅ **Notion Integration** for codex management
- ✅ **MCP Protocol Support** for direct LLM integration
- ✅ **REST API Wrapper** for HTTP-based access
- ✅ **Audience-Aware Output** (dev/audit/exec profiles)

</td>
<td width="50%">

### 🚀 Professional Features
- ✅ **Comprehensive Testing** with pytest suite
- ✅ **Type Safety** with full mypy annotations
- ✅ **Code Quality** enforced with black, isort, flake8
- ✅ **CI/CD Pipeline** with GitHub Actions
- ✅ **Docker Support** for containerized deployment
- ✅ **Metrics & Monitoring** built-in

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Optional: [uv](https://github.com/astral-sh/uv) for faster package management

### Installation

#### Option 1: Using uv (Recommended ⚡)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server

# Install with uv
uv pip install -e .
```

#### Option 2: Using pip

```bash
# Clone repository
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -e .
```

### Test the Installation

```bash
# Run MCP server directly
python -m comptext_mcp.server

# Or use REST API wrapper
python mcp_server.py
```

---

## 💡 Usage Examples

### Natural Language Compilation

The `nl_to_comptext` tool converts natural language into optimized CompText DSL:

**Input:**
```
"Review this code for best practices and maintainability"
```

**Output:**
```
dsl:
use:profile.dev.v1
use:code.review.v1

confidence: 1.00
clarification: null
```

### More Examples

<table>
<tr>
<th>Natural Language</th>
<th>Generated DSL</th>
</tr>
<tr>
<td>

```
"Find performance bottlenecks and 
optimize this slow function"
```

</td>
<td>

```
use:profile.dev.v1
use:code.perfopt.v1
```

</td>
</tr>
<tr>
<td>

```
"Scan for high-risk security 
vulnerabilities and suggest fixes"
```

</td>
<td>

```
use:profile.dev.v1
use:sec.scan.highfix.v1
```

</td>
</tr>
<tr>
<td>

```
"Generate API documentation in 
markdown with examples"
```

</td>
<td>

```
use:profile.dev.v1
use:doc.api.md.examples.v1
```

</td>
</tr>
<tr>
<td>

```
"Set up CI/CD pipeline and deploy 
to Kubernetes with Helm"
```

</td>
<td>

```
use:profile.dev.v1
use:devops.k8s.cicd.full.v1
```

</td>
</tr>
</table>

### Python API Usage

```python
from comptext_mcp.compiler import compile_nl_to_comptext

# Simple compilation
result = compile_nl_to_comptext("Review this code")
print(result)

# With specific audience
result = compile_nl_to_comptext(
    "Scan for vulnerabilities", 
    audience="audit"
)

# With detailed explanation
result = compile_nl_to_comptext(
    "Optimize this function",
    return_mode="dsl_plus_explanation"
)
```

---

## 🔌 Integration

See [CLAUDE_SETUP.md](CLAUDE_SETUP.md) for detailed Claude Desktop integration guide.

---

## 🛠️ Available MCP Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| 🔍 `list_modules` | List all CompText modules (A-M) | Browse available functionality |
| 📦 `get_module` | Load specific module with all commands | Deep dive into module details |
| 🔎 `search` | Search codex by keywords | Find relevant commands quickly |
| 📄 `get_command` | Get full command documentation | Learn command syntax |
| 🏷️ `get_by_tag` | Filter by tags (Core, Advanced, etc.) | Curated command sets |
| 📊 `get_by_type` | Filter by type (Docs, Examples, etc.) | Find learning resources |
| 📈 `get_statistics` | View codex statistics | Overview of capabilities |
| 🤖 `nl_to_comptext` | Compile natural language to DSL | Primary compiler interface |

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  (Claude Desktop, Cursor, VS Code, Custom Clients)          │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol / REST API
┌─────────────────────▼───────────────────────────────────────┐
│                 CompText MCP Server                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Natural Language Compiler                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │
│  │  │ Registry │→ │ Matcher  │→ │ Canonicalizer   │   │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Bundle Registry (YAML)                   │  │
│  │  - 3 Audience Profiles (dev/audit/exec)              │  │
│  │  - 11+ Specialized Bundles                           │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Codex (YAML Storage)                     │  │
│  │  - 13 Modules (A-M)                                   │  │
│  │  - 32+ Commands & Examples                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Compilation Pipeline

```
Natural Language Input
        ↓
┌───────────────────┐
│  Text Normalization│
└────────┬──────────┘
         ↓
┌────────────────────┐
│  Bundle Matching   │  ← Keywords from Registry
│  (Keyword-based)   │
└────────┬───────────┘
         ↓
┌────────────────────┐
│  Confidence Scoring│  → < 0.65? Ask clarification
└────────┬───────────┘
         ↓
┌────────────────────┐
│  Profile Selection │  ← Based on audience
└────────┬───────────┘
         ↓
┌────────────────────┐
│  DSL Rendering     │  → Canonical format
└────────┬───────────┘
         ↓
    CompText DSL Output
```

### Key Components

- **Registry**: Loads and validates bundles/profiles from YAML
- **Matcher**: Keyword-based scoring to find best bundle
- **Canonicalizer**: Renders DSL in deterministic format
- **Compiler**: Main entry point coordinating all components

---

## 📚 Documentation

- 📖 [CLAUDE_SETUP.md](CLAUDE_SETUP.md) - Claude Desktop integration
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- 🔒 [SECURITY.md](SECURITY.md) - Security policy
- 📝 [CHANGELOG.md](CHANGELOG.md) - Version history
- 🗺️ [ROADMAP.md](ROADMAP.md) - Future plans
- 📚 [Full Documentation](https://www.notion.so/0d571dc857144b199243ea951d60cef6)

---

## 🧪 Development

### Setup Development Environment

```bash
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server
pip install -e ".[dev]"
pre-commit install
```

### Testing

```bash
# Run tests
pytest tests/ -v --cov

# Code quality
black src/ tests/
mypy src/
flake8 src/ tests/
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **MCP Protocol** team
- **Python Community**
- All **Contributors**

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for full list.

---

<div align="center">

### ⭐ Star us on GitHub!

Made with ❤️ by [ProfRandom92](https://github.com/ProfRandom92)

[![GitHub stars](https://img.shields.io/github/stars/ProfRandom92/comptext-mcp-server?style=social)](https://github.com/ProfRandom92/comptext-mcp-server/stargazers)

</div>
