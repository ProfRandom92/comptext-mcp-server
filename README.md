# 🚀 CompText MCP Server

Ein hochperformanter MCP (Model Context Protocol) Server für CompText DSL mit REST API Wrapper - deployed auf Render.com.

## 📋 Features

- ✅ **CompText DSL Support** - Vollständiger Zugriff auf den CompText Codex
- ✅ **MCP Protocol** - Native MCP-Server-Implementierung für Claude Desktop
- ✅ **REST API** - FastAPI HTTP Wrapper für universellen Zugriff
- ✅ **Caching & Performance** - LRU-Cache mit automatischem Retry-Mechanismus
- ✅ **Type Safety** - Vollständige Type Hints und Validierung
- ✅ **Error Handling** - Exponential Backoff und umfassende Fehlerbehandlung
- ✅ **Security** - Input-Validierung und Sanitization
- ✅ **Production Ready** - Docker, Health Checks, Monitoring

## 🏗️ Architektur

```
comptext-mcp-server/
├── src/comptext_mcp/         # Hauptpaket
│   ├── server.py              # MCP Server Implementierung
│   ├── notion_client.py       # Notion API Client mit Retry-Logik
│   ├── constants.py           # Zentrale Konstanten
│   └── utils.py               # Validierungs- und Hilfsfunktionen
├── rest_api_wrapper.py        # REST API Wrapper
├── mcp_server.py              # Einfacher Server für Render.com
└── tests/                     # Test Suite
```

## 🔧 Installation & Verwendung

### Voraussetzungen

- Python 3.10+
- Notion API Token
- CompText Database ID

### Lokale Entwicklung

```bash
# 1. Repository klonen
git clone https://github.com/ProfRandom92/comptext-mcp-server.git
cd comptext-mcp-server

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Umgebungsvariablen setzen
cp .env.example .env
# Bearbeite .env und füge deine Notion Credentials ein

# 4. MCP Server starten
python -m comptext_mcp.server

# Oder REST API starten
python rest_api_wrapper.py
```

### MCP Server (für Claude Desktop)

```bash
# Server im stdio-Modus starten
python -m comptext_mcp.server
```

Konfiguration in Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "comptext": {
      "command": "python",
      "args": ["-m", "comptext_mcp.server"],
      "env": {
        "NOTION_API_TOKEN": "your_token_here",
        "COMPTEXT_DATABASE_ID": "your_db_id"
      }
    }
  }
}
```

### REST API Server

```bash
# Mit uvicorn
uvicorn rest_api_wrapper:app --reload

# Oder direkt
python rest_api_wrapper.py
```

Server läuft auf `http://localhost:8000`

## 📊 API Endpoints

### REST API

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/` | GET | API Info |
| `/health` | GET | Health Check mit Notion-Status |
| `/api/modules` | GET | Alle Module mit Statistiken |
| `/api/modules/{module}` | GET | Spezifisches Modul (A-M) |
| `/api/search?query=...` | GET | Suche im Codex |
| `/api/command/{page_id}` | GET | Vollständiger Seiteninhalt |
| `/api/tags/{tag}` | GET | Filter nach Tag |
| `/api/types/{type}` | GET | Filter nach Typ |
| `/api/statistics` | GET | Codex Statistiken |
| `/api/cache/clear` | POST | Cache leeren |
| `/docs` | GET | Interaktive API Dokumentation |

### MCP Tools

Der MCP Server bietet folgende Tools:

- `list_modules` - Liste aller Module (A-M)
- `get_module` - Lade spezifisches Modul
- `get_command` - Lade Seiteninhalt
- `search` - Durchsuche Codex
- `get_by_tag` - Filter nach Tag
- `get_by_type` - Filter nach Typ
- `get_statistics` - Codex Statistiken

## 🐳 Docker Deployment

```bash
# REST API Image bauen
docker build -f Dockerfile.rest -t comptext-api .

# Container starten
docker run -p 8000:8000 --env-file .env comptext-api

# Mit Docker Compose
docker-compose up -d
```

## 🚀 Deployment auf Render.com

### Automatisches Deployment

1. Push zu GitHub
2. Gehe zu [render.com/deploy](https://render.com/deploy)
3. Verbinde Repository
4. Render erkennt automatisch `render.yaml`
5. Setze Environment Variables:
   - `NOTION_API_TOKEN`
   - `COMPTEXT_DATABASE_ID` (optional)
6. Click "Apply" → Fertig! ✅

### Nach dem Deployment

Du erhältst eine URL wie: `https://comptext-mcp.onrender.com`

API Docs: `https://comptext-mcp.onrender.com/docs`

## 🔑 Umgebungsvariablen

```bash
# Erforderlich
NOTION_API_TOKEN=your_notion_token_here

# Optional
COMPTEXT_DATABASE_ID=0e038c9b52c5466694dbac288280dd93  # Standard-DB
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

## 📖 Verwendungsbeispiele

### Python Client

```python
from comptext_mcp import get_all_modules, search_codex, get_module_by_name

# Alle Module laden
modules = get_all_modules()
print(f"Gefunden: {len(modules)} Einträge")

# Suche durchführen
results = search_codex("docker", max_results=5)
for result in results:
    print(f"- {result['titel']}")

# Spezifisches Modul laden
modul_b = get_module_by_name("Modul B: Programmierung")
```

### REST API

```bash
# Alle Module
curl http://localhost:8000/api/modules

# Suche
curl "http://localhost:8000/api/search?query=docker&max_results=5"

# Modul B laden
curl http://localhost:8000/api/modules/B

# Statistiken
curl http://localhost:8000/api/statistics
```

### JavaScript/TypeScript

```typescript
// Suche durchführen
const response = await fetch(
  'https://comptext-mcp.onrender.com/api/search?query=docker'
);
const data = await response.json();
console.log(`Gefunden: ${data.count} Ergebnisse`);
```

## 🧪 Testing

```bash
# Tests ausführen
make test

# Mit Coverage
make test-cov

# Linting
make lint

# Code formatieren
make format
```

## ⚡ Performance-Hinweise

- **Caching**: `get_all_modules()` ist gecached (LRU, 128 Einträge)
- **Retry-Logik**: Automatische Wiederholung bei API-Fehlern (3x, exponential backoff)
- **Free Tier Sleep**: Render.com schläft nach 15 Min Inaktivität
  - Erste Anfrage nach Pause: ~30 Sek (Cold Start)
  - **Lösung**: Verwende Render's Cron Jobs für Keep-Alive Pings

## 🛡️ Security Features

- ✅ Input-Validierung für alle User-Eingaben
- ✅ Page ID Format-Validierung
- ✅ Query String Sanitization
- ✅ Text Output Sanitization
- ✅ CORS-Konfiguration
- ✅ Error Message Sanitization

## 🔧 Entwicklung

```bash
# Dev-Dependencies installieren
make install-dev

# Pre-commit hooks einrichten
pre-commit install

# Code formatieren
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

## 📚 Module Übersicht

| Modul | Beschreibung |
|-------|-------------|
| **A** | Allgemeine Befehle |
| **B** | Programmierung |
| **C** | Visualisierung |
| **D** | KI-Steuerung |
| **E** | Datenanalyse & ML |
| **F** | Dokumentation |
| **G** | Testing & QA |
| **H** | Database & Data Modeling |
| **I** | Security & Compliance |
| **J** | DevOps & Deployment |
| **K** | Frontend & UI |
| **L** | Data Pipelines & ETL |
| **M** | MCP Integration |

## 🤝 Contributing

Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Richtlinien.

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

## 🔗 Links

- [Notion Documentation](https://www.notion.so/0d571dc857144b199243ea951d60cef6)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Render.com](https://render.com/)
- [GitHub Repository](https://github.com/ProfRandom92/comptext-mcp-server)
