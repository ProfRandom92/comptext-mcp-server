# API Documentation

Es gibt zwei HTTP APIs:

1. **Compiler API** (`mcp_server.py`) - Port 10000 - Natural Language zu DSL
2. **Codex API** (`rest_api_wrapper.py`) - Port 8000 - Notion Codex Zugriff

## Compiler API (Port 10000)

Base URL: `http://localhost:10000`

### Compile Natural Language to DSL

```bash
POST /compile
```

Request Body:
```json
{
  "text": "Review this code and improve readability",
  "audience": "dev",
  "mode": "bundle_only",
  "return_mode": "dsl_plus_confidence"
}
```

Parameters:
- `text` (required): Natural language request
- `audience` (optional): dev|audit|exec (default: dev)
- `mode` (optional): bundle_only|allow_inline_fallback (default: bundle_only)
- `return_mode` (optional): dsl_only|dsl_plus_confidence|dsl_plus_explanation (default: dsl_plus_confidence)

Response:
```json
{
  "dsl": "use:profile.dev.v1\nuse:code.review.v1",
  "confidence": 0.71
}
```

Bei niedriger Konfidenz (<0.65):
```json
{
  "dsl": "",
  "confidence": 0.0,
  "clarification": "Meinst du Code-Review, Performance-Optimierung, Debugging, Security-Scan oder Dokumentation? Bitte wähle eines."
}
```

### Health Check

```bash
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "registry_loaded": true
}
```

### Server Status

```bash
GET /
```

Returns server information and available endpoints.

### Interactive Documentation

- Swagger UI: http://localhost:10000/docs
- ReDoc: http://localhost:10000/redoc

## Codex API (Port 8000)

Base URL: `http://localhost:8000`

Siehe `rest_api_wrapper.py` für vollständige Notion Codex API mit:
- `/api/modules` - Liste Module
- `/api/search` - Suche im Codex
- `/api/command/{page_id}` - Lade Seiteninhalt
- `/api/tags/{tag}` - Filtere nach Tag
- `/api/types/{type}` - Filtere nach Typ
- `/api/statistics` - Codex Statistiken

**Hinweis:** Benötigt `NOTION_API_TOKEN` Environment Variable.

## MCP Server (Stdio)

Der native MCP Server bietet alle Tools via stdio:

**Compiler Tools:**
1. **nl_to_comptext** - Natural Language zu CompText DSL konvertieren

**Codex Tools:**
2. **list_modules** - Liste alle Module
3. **get_module** - Lade spezifisches Modul
4. **get_command** - Lade Seiteninhalt
5. **search** - Durchsuche Codex
6. **get_by_tag** - Filtere nach Tag
7. **get_by_type** - Filtere nach Typ
8. **get_statistics** - Zeige Statistiken

Nutzung:
```bash
python -m comptext_mcp.server
```

Integration in Claude Desktop siehe README.md.
