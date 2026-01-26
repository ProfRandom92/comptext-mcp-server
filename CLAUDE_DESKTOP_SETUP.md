# 🚀 Claude Desktop Integration - Complete Setup Guide

## 🎯 Quick Start

Get CompText MCP Server running in Claude Desktop in **5 minutes**!

---

## 📍 Step-by-Step Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server
```

### 2️⃣ Choose Installation Method

#### Option A: Using uv (⚡ Recommended - Fastest)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .
```

#### Option B: Using pip (Traditional)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3️⃣ Find Your Absolute Path

```bash
# In the comptext-mcp-server directory:
pwd

# Example output:
# /Users/yourname/projects/comptext-mcp-server
# Copy this path!
```

### 4️⃣ Open Claude Desktop Configuration

**macOS**:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows**:
```bash
notepad %APPDATA%\Claude\claude_desktop_config.json
```

### 5️⃣ Add CompText Server Configuration

#### For uv (Recommended):

```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "uv",
      "args": [
        "--directory",
        "/YOUR/ABSOLUTE/PATH/TO/comptext-mcp-server",
        "run",
        "comptext-mcp-server"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### For venv:

```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "python3",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/YOUR/ABSOLUTE/PATH/TO/comptext-mcp-server",
      "env": {
        "PYTHONPATH": "/YOUR/ABSOLUTE/PATH/TO/comptext-mcp-server/src",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**⚠️ WICHTIG**: Ersetze `/YOUR/ABSOLUTE/PATH/TO/comptext-mcp-server` mit dem Pfad aus Schritt 3!

### 6️⃣ Restart Claude Desktop

**Wichtig**: Vollständig schließen und neu starten (nicht nur Fenster schließen)!

**macOS**:
- Cmd+Q zum vollständigen Beenden
- Neu starten aus Applications

**Windows**:
- Taskleiste-Icon → Beenden
- Neu starten

### 7️⃣ Test It!

Öffne Claude Desktop und frage:

> "Liste alle verfügbaren CompText Module auf"

oder

> "Kompiliere: Review this code for security vulnerabilities"

---

## ✅ Verification

### Check if MCP Server is Running

1. Open Claude Desktop
2. Look for MCP indicator in the interface
3. Try listing tools:
   > "What MCP tools do you have available?"

### Expected Response

Claude should list these CompText tools:
- 🔍 `list_modules`
- 📦 `get_module`
- 🔎 `search`
- 📄 `get_command`
- 🏷️ `get_by_tag`
- 📊 `get_by_type`
- 📈 `get_statistics`
- 🤖 `nl_to_comptext`

---

## 🐛 Troubleshooting

### Problem: Server doesn't start

**Solution 1**: Check paths
```bash
# Verify path is absolute (starts with /)
echo "/YOUR/PATH" | grep "^/"
```

**Solution 2**: Check Python/uv installation
```bash
# For uv:
which uv
uv --version

# For python:
which python3
python3 --version
```

**Solution 3**: Check logs
- Claude → Preferences → Developer → Show Logs
- Look for "comptext" errors

### Problem: "Tool not found"

**Solutions**:
1. ✅ Restart Claude Desktop completely
2. ✅ Check JSON syntax (no trailing commas!)
3. ✅ Verify file was saved
4. ✅ Check paths are correct

### Problem: PYTHONPATH Error (venv only)

**Solution**:
```json
"env": {
  "PYTHONPATH": "/absolute/path/to/comptext-mcp-server/src",
  "LOG_LEVEL": "INFO"
}
```

Make sure PYTHONPATH points to the `src` directory!

### Problem: Permission Denied

**macOS/Linux**:
```bash
chmod +x comptext-mcp-server
```

### Problem: Module Import Error

**Solution**:
```bash
# Reinstall in development mode
pip install -e .

# Or with uv
uv pip install -e .
```

---

## 💡 Advanced Configuration

### Multiple MCP Servers

```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "uv",
      "args": ["--directory", "/path/to/comptext-mcp-server", "run", "comptext-mcp-server"]
    },
    "other-server": {
      "command": "node",
      "args": ["/path/to/other-server/index.js"]
    }
  }
}
```

### Environment Variables

```json
"env": {
  "LOG_LEVEL": "DEBUG",          // DEBUG, INFO, WARNING, ERROR
  "COMPTEXT_CACHE": "true",       // Enable caching
  "MAX_RESULTS": "50"             // Default search results
}
```

### Custom Port (REST API)

```json
"env": {
  "PORT": "8080",
  "HOST": "0.0.0.0"
}
```

---

## 📚 Usage Examples

### Example 1: List All Modules

In Claude Desktop:
> "Show me all CompText modules"

Claude will use the `list_modules` tool automatically.

### Example 2: Search for Commands

> "Search CompText for code review commands"

Claude will use `search` tool with query="code review".

### Example 3: Compile Natural Language

> "Compile this to CompText: Analyze this dataset and create visualizations"

Claude will use `nl_to_comptext` tool to compress your request.

---

## 🚀 Performance Tips

### For Faster Startup

1. **Use uv instead of pip** (3-5x faster)
2. **Pre-compile Python** modules:
   ```bash
   python -m compileall src/
   ```
3. **Use SSD** for repository location

### For Lower Memory Usage

```json
"env": {
  "PYTHONOPTIMIZE": "2",
  "PYTHONDONTWRITEBYTECODE": "1"
}
```

---

## 🔗 Related Documentation

- 📚 [Main README](README.md) - Project overview
- 🤝 [Contributing](CONTRIBUTING.md) - Contribution guidelines
- 🔒 [Security](SECURITY.md) - Security policy
- 🗺️ [Roadmap](ROADMAP.md) - Future plans

---

## ❓ Need Help?

- 💬 [GitHub Discussions](https://github.com/ProfRandom92/comptext-mcp-server/discussions)
- 🐛 [Issue Tracker](https://github.com/ProfRandom92/comptext-mcp-server/issues)
- 📧 Email: 159939812+ProfRandom92@users.noreply.github.com

---

<div align="center">

**Made with ❤️ by [ProfRandom92](https://github.com/ProfRandom92)**

⭐ Star us on GitHub if this helped you!

</div>
