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
git checkout claude/update-mcp-integration-JpZH5
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

### Option 2: Mit venv (Traditionell)

1. **Clone & Setup**:
```bash
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server
git checkout claude/update-mcp-integration-JpZH5

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

2. **Claude Desktop Config**:
```json
{
  "mcpServers": {
    "comptext-codex": {
      "command": "python3",
      "args": ["-m", "comptext_mcp.server"],
      "cwd": "/ABSOLUTER/PFAD/ZU/comptext-mcp-server",
      "env": {
        "PYTHONPATH": "/ABSOLUTER/PFAD/ZU/comptext-mcp-server/src",
        "NOTION_API_TOKEN": "dein_notion_token_hier",
        "COMPTEXT_DATABASE_ID": "0e038c9b52c5466694dbac288280dd93",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Pfad finden

```bash
# Im comptext-mcp-server Verzeichnis:
pwd
# Kopiere die Ausgabe und ersetze damit den Pfad in der Config
```

### Claude Desktop neu starten

Nach dem Speichern der Config, starte Claude Desktop vollständig neu.

### Verfügbare MCP Tools

Nach dem Neustart kannst du in Claude diese Tools nutzen:

- 🔍 `list_modules` - Alle CompText Module auflisten
- 📦 `get_module` - Spezifisches Modul laden (A-M)
- 🔎 `search` - Codex durchsuchen
- 🏷️ `get_by_tag` - Nach Tags filtern
- 📊 `get_statistics` - Codex Statistiken
- 🤖 `nl_to_comptext` - Natural Language → DSL Compiler

### Test

Frage Claude:
> "Liste alle verfügbaren CompText Module auf"

oder

> "Kompiliere: Review this code for security issues"

## 🐛 Troubleshooting

**Server startet nicht:**
1. Prüfe Pfade in der Config (müssen absolut sein!)
2. Prüfe ob Python/uv im PATH ist
3. Logs ansehen: Claude → Preferences → Developer → Show Logs

**"Tool not found":**
- Claude Desktop neu starten
- Config Syntax prüfen (gültiges JSON?)

**PYTHONPATH Fehler (venv):**
- Stelle sicher, dass PYTHONPATH auf `/pfad/zu/comptext-mcp-server/src` zeigt

## 📚 Weitere Informationen

Siehe Haupt-README.md für vollständige Dokumentation.
