"""YAML-based Codex Client für CompText MCP-Server"""
import yaml
from typing import Optional, List, Dict, Any
import os
import logging
from functools import lru_cache
from pathlib import Path

# Logging Setup
logger = logging.getLogger(__name__)

# Configuration
CODEX_PATH = os.getenv("COMPTEXT_CODEX_PATH", "codex/modules.yaml")


class YAMLClientError(Exception):
    """Custom exception for YAML client errors"""
    pass


class CodexCache:
    """Simple cache for codex data"""
    _modules = None
    _metadata = None

    @classmethod
    def clear(cls):
        """Clear cache"""
        cls._modules = None
        cls._metadata = None
        logger.info("Cache cleared")


def _load_codex() -> Dict[str, Any]:
    """Load codex from YAML file"""
    if CodexCache._modules is not None:
        return {"modules": CodexCache._modules, "metadata": CodexCache._metadata}

    try:
        # Try absolute path first
        if os.path.isabs(CODEX_PATH):
            codex_file = Path(CODEX_PATH)
        else:
            # Try relative to project root
            project_root = Path(__file__).parent.parent.parent
            codex_file = project_root / CODEX_PATH

        if not codex_file.exists():
            raise YAMLClientError(f"Codex file not found: {codex_file}")

        with open(codex_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        CodexCache._modules = data.get("modules", [])
        CodexCache._metadata = {
            "version": data.get("version", "unknown"),
            "format": data.get("format", "comptext-codex"),
            "description": data.get("description", "")
        }

        logger.info(f"Loaded {len(CodexCache._modules)} modules from {codex_file}")
        return {"modules": CodexCache._modules, "metadata": CodexCache._metadata}

    except Exception as e:
        logger.error(f"Error loading codex: {e}")
        raise YAMLClientError(f"Failed to load codex: {e}")


def get_all_modules() -> List[Dict[str, Any]]:
    """
    Get all modules from codex

    Returns:
        List of module dictionaries with structure:
        {
            "id": "A",
            "name": "Modul A: Allgemeine Befehle",
            "description": "...",
            "type": "Core",
            "tags": [...],
            "commands": [...]
        }
    """
    try:
        codex = _load_codex()
        return codex["modules"]
    except Exception as e:
        logger.error(f"Error getting all modules: {e}")
        raise YAMLClientError(f"Failed to get modules: {e}")


def get_module_by_name(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific module by name or ID

    Args:
        module_name: Module ID (e.g., "A", "B") or full name

    Returns:
        Module dictionary or None if not found
    """
    try:
        modules = get_all_modules()

        # Try exact ID match first
        module_name_upper = module_name.upper()
        for module in modules:
            if module["id"] == module_name_upper:
                return module

        # Try name match
        for module in modules:
            if module_name.lower() in module["name"].lower():
                return module

        logger.warning(f"Module not found: {module_name}")
        return None

    except Exception as e:
        logger.error(f"Error getting module {module_name}: {e}")
        raise YAMLClientError(f"Failed to get module: {e}")


def get_page_content(command_id: str) -> str:
    """
    Get detailed content for a specific command

    Args:
        command_id: Command ID (e.g., "A.ANALYZE", "B.CODE_OPT")

    Returns:
        Formatted markdown content for the command
    """
    try:
        modules = get_all_modules()

        # Parse command_id (format: "MODULE.COMMAND")
        if "." not in command_id:
            raise YAMLClientError(f"Invalid command ID format: {command_id}")

        module_id, cmd_name = command_id.split(".", 1)

        # Find module
        module = get_module_by_name(module_id)
        if not module:
            raise YAMLClientError(f"Module not found: {module_id}")

        # Find command
        for cmd in module.get("commands", []):
            if cmd["id"] == command_id or cmd["id"].split(".")[-1] == cmd_name:
                # Format as markdown
                content = f"# {cmd['id']}\n\n"
                content += f"**Syntax:** `{cmd['syntax']}`\n\n"
                content += f"**Beschreibung:** {cmd['description']}\n\n"

                if cmd.get("examples"):
                    content += "**Beispiele:**\n"
                    for example in cmd["examples"]:
                        content += f"- `{example}`\n"

                return content

        raise YAMLClientError(f"Command not found: {command_id}")

    except Exception as e:
        logger.error(f"Error getting page content for {command_id}: {e}")
        raise YAMLClientError(f"Failed to get page content: {e}")


def search_codex(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """
    Search codex for modules and commands

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of matching items (modules or commands)
    """
    try:
        modules = get_all_modules()
        results = []
        query_lower = query.lower()

        for module in modules:
            # Search in module name and description
            if (query_lower in module["name"].lower() or
                query_lower in module["description"].lower()):
                results.append({
                    "type": "module",
                    "id": module["id"],
                    "name": module["name"],
                    "description": module["description"],
                    "match_type": "module"
                })

            # Search in commands
            for cmd in module.get("commands", []):
                if (query_lower in cmd["id"].lower() or
                    query_lower in cmd["description"].lower() or
                    query_lower in cmd["syntax"].lower()):
                    results.append({
                        "type": "command",
                        "id": cmd["id"],
                        "syntax": cmd["syntax"],
                        "description": cmd["description"],
                        "module": module["id"],
                        "match_type": "command"
                    })

                # Also search in examples
                for example in cmd.get("examples", []):
                    if query_lower in example.lower():
                        if cmd["id"] not in [r["id"] for r in results if r.get("type") == "command"]:
                            results.append({
                                "type": "command",
                                "id": cmd["id"],
                                "syntax": cmd["syntax"],
                                "description": cmd["description"],
                                "module": module["id"],
                                "match_type": "example"
                            })

        return results[:max_results]

    except Exception as e:
        logger.error(f"Error searching codex: {e}")
        raise YAMLClientError(f"Search failed: {e}")


def get_page_by_id(page_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a page by ID (module or command)

    Args:
        page_id: Page ID (module ID or command ID)

    Returns:
        Page dictionary or None
    """
    try:
        # Try as module ID first
        module = get_module_by_name(page_id)
        if module:
            return {
                "type": "module",
                **module
            }

        # Try as command ID
        if "." in page_id:
            content = get_page_content(page_id)
            return {
                "type": "command",
                "id": page_id,
                "content": content
            }

        return None

    except Exception as e:
        logger.error(f"Error getting page by ID {page_id}: {e}")
        return None


def get_modules_by_tag(tag: str) -> List[Dict[str, Any]]:
    """
    Get all modules with a specific tag

    Args:
        tag: Tag name

    Returns:
        List of modules with the tag
    """
    try:
        modules = get_all_modules()
        return [m for m in modules if tag in m.get("tags", [])]

    except Exception as e:
        logger.error(f"Error getting modules by tag {tag}: {e}")
        raise YAMLClientError(f"Failed to get modules by tag: {e}")


def get_modules_by_type(module_type: str) -> List[Dict[str, Any]]:
    """
    Get all modules of a specific type

    Args:
        module_type: Module type (e.g., "Core", "Development", "Security")

    Returns:
        List of modules of the type
    """
    try:
        modules = get_all_modules()
        return [m for m in modules if m.get("type") == module_type]

    except Exception as e:
        logger.error(f"Error getting modules by type {module_type}: {e}")
        raise YAMLClientError(f"Failed to get modules by type: {e}")


def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about the codex

    Returns:
        Dictionary with statistics
    """
    try:
        codex = _load_codex()
        modules = codex["modules"]

        total_commands = sum(len(m.get("commands", [])) for m in modules)
        module_types = set(m.get("type") for m in modules)
        all_tags = set()
        for m in modules:
            all_tags.update(m.get("tags", []))

        return {
            "version": codex["metadata"]["version"],
            "total_modules": len(modules),
            "total_commands": total_commands,
            "module_types": sorted(list(module_types)),
            "total_tags": len(all_tags),
            "tags": sorted(list(all_tags))
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise YAMLClientError(f"Failed to get statistics: {e}")


def clear_cache():
    """Clear the codex cache"""
    CodexCache.clear()


# Alias for backward compatibility with notion_client
NotionClientError = YAMLClientError
