# 🚀 CompText MCP Server - Claude Desktop Integration

## Schnellstart für Claude Desktop

### Option 1: Mit uv (Empfohlen - Modern & Schnell)

1. **Installiere uv** (falls nicht vorhanden):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone das Repository**:
```bash
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server
```

3. **Installiere Dependencies**:
```bash
uv pip install -e .
```

4. **Claude Desktop Konfiguration** öffnen:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

5. **Füge diese Konfiguration hinzu**:
```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTER/PFAD/ZU/comptext-mcp-server",
        "run",
        "comptext-mcp-server"
      ],
      "env": {
        "NOTION_API_TOKEN": "dein_notion_token_hier",
        "COMPTEXT_DATABASE_ID": "0e038c9b52c5466694dbac288280dd93",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Wichtig**: Ersetze `/ABSOLUTER/PFAD/ZU/comptext-mcp-server` mit dem echten Pfad!

Für vollständige Anleitung siehe Datei.
