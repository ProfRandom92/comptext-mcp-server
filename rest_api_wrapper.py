"""REST API Wrapper für CompText MCP Server"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from comptext_mcp.yaml_client import (
    get_all_modules,
    get_module_by_name,
    get_page_content,
    search_codex,
    get_page_by_id,
    get_modules_by_tag,
    get_modules_by_type,
    get_statistics as get_codex_statistics,
    YAMLClientError,
    clear_cache
)

# Backward compatibility alias
NotionClientError = YAMLClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CompText Codex API",
    description="REST API für CompText MCP Server",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODULE_MAP = {
    "A": "Modul A: Allgemeine Befehle",
    "B": "Modul B: Programmierung",
    "C": "Modul C: Visualisierung",
    "D": "Modul D: KI-Steuerung",
    "E": "Modul E: Datenanalyse & ML",
    "F": "Modul F: Dokumentation",
    "G": "Modul G: Testing & QA",
    "H": "Modul H: Database & Data Modeling",
    "I": "Modul I: Security & Compliance",
    "J": "Modul J: DevOps & Deployment",
    "K": "Modul K: Frontend & UI",
    "L": "Modul L: Data Pipelines & ETL",
    "M": "Modul M: MCP Integration"
}


@app.get("/")
async def root():
    return {
        "name": "CompText Codex API",
        "version": "1.0.0",
        "endpoints": {
            "modules": "/api/modules",
            "module_by_id": "/api/modules/{module}",
            "search": "/api/search?query=...",
            "command": "/api/command/{page_id}",
            "by_tag": "/api/tags/{tag}",
            "by_type": "/api/types/{type}",
            "statistics": "/api/statistics",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    try:
        modules = get_all_modules()
        return {
            "status": "healthy",
            "codex_loaded": True,
            "modules_count": len(modules)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "codex_loaded": False,
            "error": str(e)
        }


@app.get("/api/modules")
async def list_modules():
    try:
        modules = get_all_modules()

        # Format modules for API response
        formatted_modules = {}
        for module in modules:
            formatted_modules[module["id"]] = {
                "name": module["name"],
                "description": module["description"],
                "type": module.get("type"),
                "tags": module.get("tags", []),
                "commands_count": len(module.get("commands", [])),
                "commands": [cmd["id"] for cmd in module.get("commands", [])]
            }

        return {
            "total_modules": len(modules),
            "modules": formatted_modules
        }
    except (YAMLClientError, NotionClientError) as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/modules/{module}")
async def get_module(module: str):
    try:
        module_data = get_module_by_name(module)
        if not module_data:
            raise HTTPException(status_code=404, detail=f"Module {module} not found")

        return {
            "module": module_data["id"],
            "name": module_data["name"],
            "description": module_data["description"],
            "type": module_data.get("type"),
            "tags": module_data.get("tags", []),
            "commands": module_data.get("commands", [])
        }
    except (YAMLClientError, NotionClientError) as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/search")
async def search(
    query: str = Query(..., description="Suchbegriff"),
    max_results: int = Query(20, ge=1, le=100)
):
    try:
        results = search_codex(query, max_results)
        return {
            "query": query,
            "count": len(results),
            "results": results
        }
    except NotionClientError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/command/{page_id}")
async def get_command(page_id: str):
    try:
        page_id = page_id.replace("-", "")
        page_info = get_page_by_id(page_id)
        content = get_page_content(page_id)
        
        return {
            "page_info": page_info,
            "content": content
        }
    except NotionClientError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/tags/{tag}")
async def get_by_tag(tag: str):
    try:
        results = get_modules_by_tag(tag)
        return {
            "tag": tag,
            "count": len(results),
            "entries": results
        }
    except NotionClientError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/types/{typ}")
async def get_by_type(typ: str):
    try:
        results = get_modules_by_type(typ)
        return {
            "type": typ,
            "count": len(results),
            "entries": results
        }
    except NotionClientError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    try:
        stats = get_codex_statistics()
        return stats
    except (YAMLClientError, NotionClientError) as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/cache/clear")
async def clear_cache_endpoint():
    try:
        clear_cache()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"API Docs: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port, log_level="info")
