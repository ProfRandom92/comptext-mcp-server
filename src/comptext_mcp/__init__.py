"""CompText MCP Server Package"""

__version__ = "1.0.0"
__author__ = "CompText Team"

from .server import server, main
from .notion_client import (
    get_all_modules as notion_get_all_modules,
    get_module_by_name as notion_get_module_by_name,
    get_page_content as notion_get_page_content,
    search_codex as notion_search_codex,
    NotionClientError,
)
from .local_codex_client import (
    get_all_modules as local_get_all_modules,
    get_module_by_name as local_get_module_by_name,
    get_page_content as local_get_page_content,
    search_codex as local_search_codex,
    LocalCodexClientError,
)
from .constants import MODULE_MAP

__all__ = [
    "server",
    "main",
    "notion_get_all_modules",
    "notion_get_module_by_name",
    "notion_get_page_content",
    "notion_search_codex",
    "NotionClientError",
    "local_get_all_modules",
    "local_get_module_by_name",
    "local_get_page_content",
    "local_search_codex",
    "LocalCodexClientError",
    "MODULE_MAP",
]
