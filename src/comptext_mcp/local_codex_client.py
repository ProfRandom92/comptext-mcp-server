"""Local JSON Codex Client for CompText MCP Server - Production Ready"""

import json
import logging
import os
from functools import lru_cache
from typing import List, Dict, Any
from pathlib import Path

from .constants import CACHE_SIZE, DEFAULT_DATA_PATH
from .utils import validate_query_string, sanitize_text_output

# Logging Setup
logger = logging.getLogger(__name__)

# Configuration
CODEX_FILE_PATH = os.getenv("COMPTEXT_CODEX_PATH", DEFAULT_DATA_PATH)


class LocalCodexClientError(Exception):
    """Custom exception for local codex client errors"""
    pass


def _load_codex_data() -> Dict[str, Any]:
    """
    Load codex data from JSON file.
    
    Returns:
        Dictionary containing codex data
        
    Raises:
        LocalCodexClientError: If file cannot be read or parsed
    """
    try:
        codex_path = Path(CODEX_FILE_PATH)
        
        if not codex_path.exists():
            raise LocalCodexClientError(f"Codex file not found: {CODEX_FILE_PATH}")
        
        with open(codex_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data.get('modules', []))} modules from {CODEX_FILE_PATH}")
        return data
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in codex file: {e}")
        raise LocalCodexClientError(f"Invalid JSON format: {e}")
    except Exception as e:
        logger.error(f"Error loading codex data: {e}")
        raise LocalCodexClientError(f"Failed to load codex data: {e}")


@lru_cache(maxsize=1)
def _get_cached_codex() -> Dict[str, Any]:
    """
    Get cached codex data.
    
    Uses LRU cache to avoid repeated file reads.
    
    Returns:
        Dictionary containing codex data
    """
    return _load_codex_data()


def parse_module(module: Dict) -> Dict[str, Any]:
    """
    Parse module entry to standardized format.
    
    Args:
        module: Raw module entry from JSON
        
    Returns:
        Dictionary with standardized CompText module structure
    """
    return {
        "id": module.get("id", ""),
        "url": module.get("url", ""),
        "titel": sanitize_text_output(module.get("titel", "")),
        "beschreibung": sanitize_text_output(module.get("beschreibung", "")),
        "modul": module.get("modul", ""),
        "typ": module.get("typ", ""),
        "tags": module.get("tags", []),
        "created_time": module.get("created_time", ""),
        "last_edited_time": module.get("last_edited_time", ""),
    }


def get_all_modules() -> List[Dict[str, Any]]:
    """
    Load all modules from local codex file.
    
    Results are cached to improve performance. Use clear_cache() to invalidate.
    
    Returns:
        List of all module entries from the codex
        
    Raises:
        LocalCodexClientError: If loading fails
    """
    codex = _get_cached_codex()
    modules = codex.get("modules", [])
    return [parse_module(m) for m in modules]


def get_module_by_name(modul_name: str) -> List[Dict[str, Any]]:
    """
    Load all entries of a specific module.
    
    Args:
        modul_name: Full module name (e.g., "Modul B: Programmierung")
        
    Returns:
        List of entries belonging to the specified module
        
    Raises:
        LocalCodexClientError: If loading fails
    """
    all_modules = get_all_modules()
    return [m for m in all_modules if m.get("modul") == modul_name]


def get_page_content(page_id: str) -> str:
    """
    Load full content of a module by ID.
    
    Args:
        page_id: Module ID
        
    Returns:
        Markdown-formatted module content
        
    Raises:
        ValueError: If page ID is empty
        LocalCodexClientError: If module not found
    """
    if not page_id:
        raise ValueError("Page ID cannot be empty")
    
    codex = _get_cached_codex()
    modules = codex.get("modules", [])
    
    for module in modules:
        if module.get("id") == page_id:
            content = module.get("content", "")
            return sanitize_text_output(content)
    
    raise LocalCodexClientError(f"Module not found: {page_id}")


def search_codex(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """
    Search in local codex by title, description, or tags.
    
    Args:
        query: Search query string (max 200 characters)
        max_results: Maximum number of results to return (default: 20)
        
    Returns:
        List of matching entries, limited to max_results
        
    Raises:
        ValueError: If query is invalid or too long
        LocalCodexClientError: If loading fails
    """
    validated_query = validate_query_string(query)
    all_modules = get_all_modules()
    query_lower = validated_query.lower()
    
    results = []
    for module in all_modules:
        titel = (module.get("titel") or "").lower()
        beschreibung = (module.get("beschreibung") or "").lower()
        tags = " ".join(module.get("tags", [])).lower()
        
        if query_lower in titel or query_lower in beschreibung or query_lower in tags:
            results.append(module)
            
            if len(results) >= max_results:
                break
    
    return results


def get_page_by_id(page_id: str) -> Dict[str, Any]:
    """
    Get module information by ID.
    
    Args:
        page_id: Module ID
        
    Returns:
        Parsed module information dictionary
        
    Raises:
        ValueError: If page ID is empty
        LocalCodexClientError: If module not found
    """
    if not page_id:
        raise ValueError("Page ID cannot be empty")
    
    all_modules = get_all_modules()
    
    for module in all_modules:
        if module.get("id") == page_id:
            return module
    
    raise LocalCodexClientError(f"Module not found: {page_id}")


def get_modules_by_tag(tag: str) -> List[Dict[str, Any]]:
    """
    Filter modules by tag.
    
    Args:
        tag: Tag name to filter by (e.g., "Core", "Erweitert")
        
    Returns:
        List of entries containing the specified tag
        
    Raises:
        LocalCodexClientError: If loading fails
    """
    all_modules = get_all_modules()
    return [m for m in all_modules if tag in m.get("tags", [])]


def get_modules_by_type(typ: str) -> List[Dict[str, Any]]:
    """
    Filter modules by type.
    
    Args:
        typ: Type to filter by (e.g., "Dokumentation", "Beispiel")
        
    Returns:
        List of entries of the specified type
        
    Raises:
        LocalCodexClientError: If loading fails
    """
    all_modules = get_all_modules()
    return [m for m in all_modules if m.get("typ") == typ]


def clear_cache():
    """
    Clear the cache for codex data.
    
    Use this to force a reload of data from the JSON file.
    """
    _get_cached_codex.cache_clear()
    logger.info("Cache cleared")
