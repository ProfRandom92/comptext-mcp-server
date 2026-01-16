"""CompText MCP Server Package"""
__version__ = "1.0.0"
__author__ = "CompText Team"

from .server import server, main
from .yaml_client import (
    get_all_modules,
    get_module_by_name,
    get_page_content,
    search_codex,
    YAMLClientError,
    get_page_by_id,
    get_modules_by_tag,
    get_modules_by_type,
    get_statistics,
    clear_cache
)

# Backward compatibility alias
NotionClientError = YAMLClientError

__all__ = [
    "server",
    "main",
    "get_all_modules",
    "get_module_by_name",
    "get_page_content",
    "search_codex",
    "YAMLClientError",
    "NotionClientError",
    "get_page_by_id",
    "get_modules_by_tag",
    "get_modules_by_type",
    "get_statistics",
    "clear_cache"
]

