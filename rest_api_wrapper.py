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

from comptext_mcp.notion_client import (
    get_all_modules,
    get_module_by_name,
    get_page_content,
    search_codex,
    get_page_by_id,
    get_modules_by_tag,
    get_modules_by_type,
    NotionClientError,
    clear_cache
)

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
            "notion_connected": True,
            "modules_count": len(modules)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "notion_connected": False,
            "error": str(e)
        }


@app.get("/api/modules")
async def list_modules():
    try:
        modules = get_all_modules()
        by_module = {}
        for entry in modules:
            modul = entry.get("modul")
            if modul:
                by_module.setdefault(modul, []).append(entry)
        
        stats = {
            letter: {
                "name": full_name,
                "count": len(by_module.get(full_name, [])),
                "entries": by_module.get(full_name, [])
            }
            for letter, full_name in MODULE_MAP.items()
        }
        
        return {
            "total_modules": len(by_module),
            "total_entries": len(modules),
            "modules": stats
        }
    except NotionClientError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/modules/{module}")
async def get_module(module: str):
    try:
        if module in MODULE_MAP:
            module = MODULE_MAP[module]
        
        entries = get_module_by_name(module)
        return {
            "module": module,
            "count": len(entries),
            "entries": entries
        }
    except NotionClientError as e:
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
        modules = get_all_modules()
        by_module = {}
        by_type = {}
        by_tag = {}
        
        for entry in modules:
            modul = entry.get("modul")
            if modul:
                by_module[modul] = by_module.get(modul, 0) + 1
            
            typ = entry.get("typ")
            if typ:
                by_type[typ] = by_type.get(typ, 0) + 1
            
            for tag in entry.get("tags", []):
                by_tag[tag] = by_tag.get(tag, 0) + 1
        
        return {
            "total_entries": len(modules),
            "by_module": by_module,
            "by_type": by_type,
            "by_tag": by_tag
        }
    except NotionClientError as e:
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
