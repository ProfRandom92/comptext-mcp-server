# 🚀 CompText MCP Server

Ein MCP (Model Context Protocol) Server für CompText DSL - deployed auf Render.com.

## 📋 Features

- ✅ CompText DSL Validierung
- ✅ CompText zu natürlicher Sprache Parser
- ✅ FastAPI HTTP Wrapper
- ✅ Health Check Endpoint
- ✅ Automatisches Deployment auf Render.com

## 🔧 Verwendung

### Lokale Entwicklung

```bash
pip install -r requirements.txt
python mcp_server.py
```

Server läuft auf `http://localhost:10000`

### Deployment auf Render.com

1. Push dieses Repository zu GitHub
2. Gehe zu [render.com/deploy](https://render.com/deploy)
3. Verbinde dein Repository
4. Render erkennt automatisch `render.yaml`
5. Click "Apply" → Fertig! ✅

### Nach dem Deployment

Du erhältst eine URL wie: `https://comptext-mcp.onrender.com`

Diese URL verwendest du dann in deiner MCP-Client-Konfiguration.

## 🔧 MCP Client Konfiguration

| Feld | Wert |
|------|------|
| Name | CompText MCP Server |
| URL  | https://comptext-mcp.onrender.com |
| Auth | None |

## 📊 API Endpoints

- `GET /` - Server Status
- `GET /health` - Health Check
- MCP Tools: `validate_comptext`, `parse_comptext`

## ⚡ Performance-Hinweis

Der Free Tier schläft nach 15 Min Inaktivität. Erste Anfrage nach Pause dauert ~30 Sek (Cold Start).

**Lösung:** Verwende Render's Cron Jobs für Keep-Alive Pings.

## 📝 Lizenz

MIT License
