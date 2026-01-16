# 🚀 CompText MCP Server

Ein MCP (Model Context Protocol) Server für CompText DSL - mit Natural Language zu DSL Compiler.

## 📋 Features

- ✅ **Natural Language zu CompText DSL Compiler** - Konvertiert natürliche Sprache in kanonisches CompText
- ✅ **Bundle-basiertes Matching** - Verwendet vordefinierte Bundles aus `bundles.yaml`
- ✅ **Confidence Scoring** - Berechnet Konfidenz-Score für Matches (0-1)
- ✅ **Audience Profiles** - Unterstützt dev/audit/exec Profile
- ✅ **FastAPI HTTP Wrapper** - REST API für einfache Integration
- ✅ **Stdio MCP Server** - Natives MCP-Protokoll für direkte Integration
- ✅ **Notion Integration** - Zugriff auf CompText Codex via Notion API
- ✅ **Health Check Endpoint** - Monitoring und Status
- ✅ **Automatisches Deployment** - Bereit für Render.com/Railway/etc.

## 🔧 Verwendung

### HTTP API (FastAPI Wrapper)

```bash
pip install -r requirements.txt
python mcp_server.py
```

Server läuft auf `http://localhost:10000`

#### API Endpoints

**POST /compile** - Kompiliere Natural Language zu CompText DSL

```bash
curl -X POST http://localhost:10000/compile \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Review this code and improve readability",
    "audience": "dev",
    "return_mode": "dsl_plus_confidence"
  }'
```

Response:
```json
{
  "dsl": "use:profile.dev.v1\nuse:code.review.v1",
  "confidence": 0.71
}
```

**GET /health** - Health Check

**GET /** - Server Status

### MCP Server (Stdio)

### Deployment auf Render.com

1. Push dieses Repository zu GitHub
2. Gehe zu [render.com/deploy](https://render.com/deploy)
3. Verbinde dein Repository
4. Render erkennt automatisch `render.yaml`
5. Click "Apply" → Fertig! ✅

### Nach dem Deployment

Du erhältst eine URL wie: `https://comptext-mcp.onrender.com`

Diese URL verwendest du dann in deiner MCP-Client-Konfiguration.

## 🔧 Environment Variables

Für Notion-Integration (optional für HTTP API, required für MCP Server):

```bash
NOTION_API_TOKEN=your_notion_token
COMPTEXT_DATABASE_ID=your_database_id
```

**Hinweis:** Der HTTP API Wrapper (`mcp_server.py`) funktioniert auch ohne Notion-Token, da er nur den Compiler verwendet. Der volle MCP Server benötigt die Notion-Integration.

## 🔧 MCP Client Konfiguration

Für HTTP Wrapper:

| Feld | Wert |
|------|------|
| Name | CompText MCP Server |
| URL  | https://comptext-mcp.onrender.com |
| Auth | None |

Für Stdio MCP Server in Claude Desktop:

```json
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["-m", "comptext_mcp.server"],
      "env": {
        "NOTION_API_TOKEN": "your_token",
        "COMPTEXT_DATABASE_ID": "your_db_id"
      }
    }
  }
}
```

Für direkte MCP-Integration:

```bash
python -m comptext_mcp.server
```

**MCP Tools verfügbar:**
- `nl_to_comptext` - Natural Language zu CompText DSL
- `list_modules` - Liste alle CompText Module
- `get_module` - Lade spezifisches Modul
- `search` - Durchsuche Codex
- `get_command` - Lade Seiteninhalt
- `get_by_tag` - Filtere nach Tag
- `get_by_type` - Filtere nach Typ
- `get_statistics` - Codex Statistiken

## 📊 Compiler Spec

Der Compiler konvertiert natürliche Sprache in kanonisches CompText DSL:

**Input:**
- `text`: Natural language request (required)
- `audience`: dev|audit|exec (default: dev)
- `mode`: bundle_only|allow_inline_fallback (default: bundle_only)
- `return_mode`: dsl_only|dsl_plus_confidence|dsl_plus_explanation (default: dsl_plus_confidence)

**Output:**
```
dsl:
use:profile.dev.v1
use:code.review.v1

confidence: 0.71
clarification: null
```

**Matching:**
- Keyword matching mit +2 Punkten pro Treffer
- Domain/Task Bonus mit +1 Punkt
- Ambiguity Penalty bei ähnlichen Scores
- Confidence = min(1.0, score / 7.0)
- Bei confidence < 0.65 wird Klärungsfrage gestellt

**Bundles:** Siehe `bundles/bundles.yaml` für alle verfügbaren Bundles

## ⚡ Performance-Hinweis

Der Free Tier schläft nach 15 Min Inaktivität. Erste Anfrage nach Pause dauert ~30 Sek (Cold Start).

**Lösung:** Verwende Render's Cron Jobs für Keep-Alive Pings.

## 🧪 Tests

Tests ausführen:

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## 📝 Lizenz

MIT License
