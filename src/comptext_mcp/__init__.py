"""CompText MCP Server Package"""

__version__ = "1.0.0"
__author__ = "CompText Team"

from .server import server, main
from .notion_client import get_all_modules, get_module_by_name, get_page_content, search_codex, NotionClientError
from .constants import MODULE_MAP

__all__ = [
    "server",
    "main",
    "get_all_modules",
    "get_module_by_name",
    "get_page_content",
    "search_codex",
    "NotionClientError",
    "MODULE_MAP",
]
