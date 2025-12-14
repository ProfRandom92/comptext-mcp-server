"""REST API Wrapper für CompText MCP Server"""
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import logging
import os
import sys
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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
from comptext_mcp.constants import MODULE_MAP, MAX_SEARCH_RESULTS
from comptext_mcp.utils import validate_page_id, validate_query_string
from comptext_mcp.metrics import track_performance, get_metrics, reset_metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="CompText Codex API",
    description="REST API für CompText MCP Server mit Rate Limiting",
    version="1.0.0"
)

# Add rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@limiter.limit("60/minute")
@track_performance("root")
async def root(request: Request):
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
            "metrics": "/api/metrics",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
@limiter.limit("120/minute")
@track_performance("health")
async def health_check(request: Request):
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
@limiter.limit("30/minute")
@track_performance("list_modules")
async def list_modules(request: Request):
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
@limiter.limit("30/minute")
async def get_module(request: Request, module: str):
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
@limiter.limit("20/minute")
async def search(
    request: Request,
    query: str = Query(..., description="Suchbegriff"),
    max_results: int = Query(20, ge=1, le=MAX_SEARCH_RESULTS)
):
    try:
        validated_query = validate_query_string(query)
        results = search_codex(validated_query, max_results)
        return {
            "query": validated_query,
            "count": len(results),
            "results": results
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotionClientError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/command/{page_id}")
@limiter.limit("30/minute")
async def get_command(request: Request, page_id: str):
    try:
        validated_id = validate_page_id(page_id)
        page_info = get_page_by_id(validated_id)
        content = get_page_content(validated_id)
        
        return {
            "page_info": page_info,
            "content": content
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotionClientError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/tags/{tag}")
@limiter.limit("30/minute")
async def get_by_tag(request: Request, tag: str):
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
@limiter.limit("30/minute")
async def get_by_type(request: Request, typ: str):
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
@limiter.limit("30/minute")
async def get_statistics(request: Request):
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
@limiter.limit("5/minute")
async def clear_cache_endpoint(request: Request):
    try:
        clear_cache()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
@limiter.limit("30/minute")
async def get_metrics_endpoint(request: Request):
    """Get server performance metrics"""
    try:
        return get_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/metrics/reset")
@limiter.limit("5/minute")
async def reset_metrics_endpoint(request: Request):
    """Reset performance metrics"""
    try:
        reset_metrics()
        return {"status": "success", "message": "Metrics reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"API Docs: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port, log_level="info")
