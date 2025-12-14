"""CompText MCP Server - Production Ready"""
import asyncio
import logging
from typing import Any, Sequence, Dict, List
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl
from dotenv import load_dotenv

from .notion_client import (
    get_all_modules,
    get_module_by_name,
    get_page_content,
    search_codex,
    get_modules_by_tag,
    get_modules_by_type,
    NotionClientError
)
from .constants import MODULE_MAP, DEFAULT_MAX_RESULTS
from .utils import validate_page_id, validate_query_string

# Load environment
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("comptext-codex")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available CompText tools"""
    return [
        Tool(
            name="list_modules",
            description="Liste alle CompText-Module (A-M) mit Zusammenfassung auf",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_module",
            description="Lade ein spezifisches Modul mit allen Einträgen (A-M)",
            inputSchema={
                "type": "object",
                "properties": {
                    "module": {
                        "type": "string",
                        "description": "Modul-Buchstabe (A-M) oder vollständiger Name",
                        "enum": list(MODULE_MAP.keys()) + list(MODULE_MAP.values())
                    }
                },
                "required": ["module"]
            }
        ),
        Tool(
            name="get_command",
            description="Lade den vollständigen Inhalt eines Befehls/einer Seite",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Notion Page-ID"
                    }
                },
                "required": ["page_id"]
            }
        ),
        Tool(
            name="search",
            description="Durchsuche den CompText-Codex nach Befehlen, Beispielen oder Dokumentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Suchbegriff"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximale Anzahl Ergebnisse",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_by_tag",
            description="Filtere Einträge nach Tag (Core, Erweitert, Optimierung, Visualisierung, Analyse)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Tag-Name",
                        "enum": ["Core", "Erweitert", "Optimierung", "Visualisierung", "Analyse"]
                    }
                },
                "required": ["tag"]
            }
        ),
        Tool(
            name="get_by_type",
            description="Filtere Einträge nach Typ (Dokumentation, Beispiel, Test, Referenz)",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Typ-Name",
                        "enum": ["Dokumentation", "Beispiel", "Test", "Referenz"]
                    }
                },
                "required": ["type"]
            }
        ),
        Tool(
            name="get_statistics",
            description="Zeige Statistiken über den CompText-Codex",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    try:
        if name == "list_modules":
            modules = get_all_modules()
            
            # Group by module
            by_module = {}
            for entry in modules:
                modul = entry.get("modul")
                if modul:
                    by_module.setdefault(modul, []).append(entry)
            
            # Format output
            output = "# CompText Module Übersicht\n\n"
            for letter, full_name in MODULE_MAP.items():
                entries = by_module.get(full_name, [])
                output += f"## {letter}: {full_name}\n"
                output += f"Einträge: {len(entries)}\n\n"
            
            output += f"\n**Gesamt:** {len(modules)} Einträge"
            
            return [TextContent(type="text", text=output)]
        
        elif name == "get_module":
            module = arguments.get("module")
            
            # Convert letter to full name
            if module in MODULE_MAP:
                module = MODULE_MAP[module]
            
            entries = get_module_by_name(module)
            
            # Format output
            output = f"# {module}\n\n"
            output += f"**Anzahl Einträge:** {len(entries)}\n\n"
            
            for entry in entries:
                output += f"### {entry['titel']}\n"
                if entry.get('beschreibung'):
                    output += f"{entry['beschreibung']}\n"
                output += f"- **Typ:** {entry.get('typ', 'N/A')}\n"
                output += f"- **Tags:** {', '.join(entry.get('tags', []))}\n"
                output += f"- **ID:** {entry['id']}\n"
                output += f"- **URL:** {entry['url']}\n\n"
            
            return [TextContent(type="text", text=output)]
        
        elif name == "get_command":
            page_id = validate_page_id(arguments.get("page_id"))
            content = get_page_content(page_id)
            
            return [TextContent(type="text", text=content)]
        
        elif name == "search":
            query = validate_query_string(arguments.get("query"))
            max_results = arguments.get("max_results", DEFAULT_MAX_RESULTS)
            
            results = search_codex(query, max_results)
            
            output = f"# Suchergebnisse für: {query}\n\n"
            output += f"**Gefunden:** {len(results)} Ergebnisse\n\n"
            
            for result in results:
                output += f"### {result['titel']}\n"
                if result.get('beschreibung'):
                    output += f"{result['beschreibung']}\n"
                output += f"- **Modul:** {result.get('modul', 'N/A')}\n"
                output += f"- **Typ:** {result.get('typ', 'N/A')}\n"
                output += f"- **Tags:** {', '.join(result.get('tags', []))}\n"
                output += f"- **ID:** {result['id']}\n\n"
            
            return [TextContent(type="text", text=output)]
        
        elif name == "get_by_tag":
            tag = arguments.get("tag")
            results = get_modules_by_tag(tag)
            
            output = f"# Einträge mit Tag: {tag}\n\n"
            output += f"**Anzahl:** {len(results)}\n\n"
            
            for result in results:
                output += f"### {result['titel']}\n"
                output += f"- **Modul:** {result.get('modul', 'N/A')}\n"
                output += f"- **Typ:** {result.get('typ', 'N/A')}\n\n"
            
            return [TextContent(type="text", text=output)]
        
        elif name == "get_by_type":
            typ = arguments.get("type")
            results = get_modules_by_type(typ)
            
            output = f"# Einträge vom Typ: {typ}\n\n"
            output += f"**Anzahl:** {len(results)}\n\n"
            
            for result in results:
                output += f"### {result['titel']}\n"
                output += f"- **Modul:** {result.get('modul', 'N/A')}\n"
                output += f"- **Tags:** {', '.join(result.get('tags', []))}\n\n"
            
            return [TextContent(type="text", text=output)]
        
        elif name == "get_statistics":
            modules = get_all_modules()
            
            # Calculate statistics
            by_module = {}
            by_type = {}
            by_tag = {}
            
            for entry in modules:
                # By module
                modul = entry.get("modul")
                if modul:
                    by_module[modul] = by_module.get(modul, 0) + 1
                
                # By type
                typ = entry.get("typ")
                if typ:
                    by_type[typ] = by_type.get(typ, 0) + 1
                
                # By tag
                for tag in entry.get("tags", []):
                    by_tag[tag] = by_tag.get(tag, 0) + 1
            
            # Format output
            output = "# CompText-Codex Statistiken\n\n"
            output += f"**Gesamt Einträge:** {len(modules)}\n\n"
            
            output += "## Nach Modul\n"
            for modul, count in sorted(by_module.items()):
                output += f"- {modul}: {count}\n"
            
            output += "\n## Nach Typ\n"
            for typ, count in sorted(by_type.items()):
                output += f"- {typ}: {count}\n"
            
            output += "\n## Nach Tags\n"
            for tag, count in sorted(by_tag.items()):
                output += f"- {tag}: {count}\n"
            
            return [TextContent(type="text", text=output)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except NotionClientError as e:
        logger.error(f"Notion client error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return [TextContent(type="text", text=f"Validation error: {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("CompText MCP Server starting...")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
