"""CompText MCP Server - Production Ready"""

import asyncio
import logging
from typing import Any, Sequence, List
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from dotenv import load_dotenv

from .notion_client import (
    get_all_modules,
    get_module_by_name,
    get_page_content,
    search_codex,
    get_modules_by_tag,
    get_modules_by_type,
    NotionClientError,
)
from .github_client import (
    audit_repository,
    auto_merge_prs,
    generate_default_branch_commands,
    GitHubClientError,
)
from .constants import MODULE_MAP, DEFAULT_MAX_RESULTS
from .utils import (
    validate_page_id,
    validate_query_string,
    validate_github_repo_name,
    validate_branch_name,
    truncate_text,
)

# Load environment
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_BRANCHES_TO_DISPLAY = 10

# Initialize MCP server
server = Server("comptext-codex")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available CompText tools"""
    return [
        Tool(
            name="list_modules",
            description="Liste alle CompText-Module (A-M) mit Zusammenfassung auf",
            inputSchema={"type": "object", "properties": {}, "required": []},
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
                        "enum": list(MODULE_MAP.keys()) + list(MODULE_MAP.values()),
                    }
                },
                "required": ["module"],
            },
        ),
        Tool(
            name="get_command",
            description="Lade den vollständigen Inhalt eines Befehls/einer Seite",
            inputSchema={
                "type": "object",
                "properties": {"page_id": {"type": "string", "description": "Notion Page-ID"}},
                "required": ["page_id"],
            },
        ),
        Tool(
            name="search",
            description="Durchsuche den CompText-Codex nach Befehlen, Beispielen oder Dokumentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Suchbegriff"},
                    "max_results": {"type": "integer", "description": "Maximale Anzahl Ergebnisse", "default": 20},
                },
                "required": ["query"],
            },
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
                        "enum": ["Core", "Erweitert", "Optimierung", "Visualisierung", "Analyse"],
                    }
                },
                "required": ["tag"],
            },
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
                        "enum": ["Dokumentation", "Beispiel", "Test", "Referenz"],
                    }
                },
                "required": ["type"],
            },
        ),
        Tool(
            name="get_statistics",
            description="Zeige Statistiken über den CompText-Codex",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="github_audit",
            description="Audit eines GitHub-Repositories: Default-Branch, alle Branches mit letztem Commit, offene PRs, Draft-Status und Mergeable-State",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository-Owner (z.B. ProfRandom92)"},
                    "repo": {"type": "string", "description": "Repository-Name (z.B. comptext-mcp-server)"},
                },
                "required": ["owner", "repo"],
            },
        ),
        Tool(
            name="github_auto_merge",
            description="Automatisches Mergen aller nicht-draft PRs (squash & merge) von ältesten zu neuesten, inkl. Dependabot",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository-Owner"},
                    "repo": {"type": "string", "description": "Repository-Name"},
                    "merge_method": {
                        "type": "string",
                        "description": "Merge-Methode",
                        "enum": ["squash", "merge", "rebase"],
                        "default": "squash"
                    },
                },
                "required": ["owner", "repo"],
            },
        ),
        Tool(
            name="github_default_branch_commands",
            description="Generiere Befehle zum manuellen Ändern des Default-Branch (gh CLI, curl, Web-UI)",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository-Owner"},
                    "repo": {"type": "string", "description": "Repository-Name"},
                    "new_default": {"type": "string", "description": "Neuer Default-Branch Name"},
                },
                "required": ["owner", "repo", "new_default"],
            },
        ),
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
                if entry.get("beschreibung"):
                    output += f"{truncate_text(entry['beschreibung'], max_length=320)}\n"
                output += f"- **Typ:** {entry.get('typ', 'N/A')}\n"
                output += f"- **Tags:** {', '.join(entry.get('tags', []))}\n"
                output += f"- **ID:** {entry['id']}\n"
                output += f"- **URL:** {entry['url']}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_command":
            page_id = validate_page_id(arguments.get("page_id"))
            content = get_page_content(page_id)

            return [TextContent(type="text", text=truncate_text(content, max_length=4000))]

        elif name == "search":
            query = validate_query_string(arguments.get("query"))
            max_results = arguments.get("max_results", DEFAULT_MAX_RESULTS)

            results = search_codex(query, max_results)

            output = f"# Suchergebnisse für: {query}\n\n"
            output += f"**Gefunden:** {len(results)} Ergebnisse\n\n"

            for result in results:
                output += f"### {result['titel']}\n"
                 if result.get("beschreibung"):
                     output += f"{truncate_text(result['beschreibung'], max_length=320)}\n"
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

        elif name == "github_audit":
            owner = validate_github_repo_name(arguments.get("owner", ""))
            repo = validate_github_repo_name(arguments.get("repo", ""))
            
            audit = audit_repository(owner, repo)
            
            # Format output
            output = f"# GitHub Repository Audit: {owner}/{repo}\n\n"
            output += f"**Default Branch:** {audit['default_branch']}\n"
            output += f"**Total Branches:** {audit['total_branches']}\n"
            output += f"**Total Open PRs:** {audit['total_open_prs']}\n"
            output += f"**Mergeable PRs:** {audit['mergeable_prs']}\n"
            output += f"**Draft PRs:** {audit['draft_prs']}\n\n"
            
            # Branches with last commit (show top N)
            output += "## Branches (sorted by last commit, newest first)\n\n"
            for branch in audit['branches'][:MAX_BRANCHES_TO_DISPLAY]:
                commit = branch['last_commit']
                output += f"### {branch['name']}\n"
                output += f"- **Last Commit:** {commit['date']}\n"
                output += f"- **Author:** {commit['author']}\n"
                output += f"- **Message:** {commit['message']}\n"
                output += f"- **SHA:** {commit['sha'][:7]}\n\n"
            
            if audit['total_branches'] > MAX_BRANCHES_TO_DISPLAY:
                output += f"_(showing {MAX_BRANCHES_TO_DISPLAY} of {audit['total_branches']} branches)_\n\n"
            
            # Open PRs
            output += "## Open Pull Requests\n\n"
            if audit['open_prs']:
                for pr in audit['open_prs']:
                    output += f"### PR #{pr['number']}: {pr['title']}\n"
                    output += f"- **Author:** {pr['author']}\n"
                    output += f"- **Created:** {pr['created_at']}\n"
                    output += f"- **Draft:** {'Yes' if pr['draft'] else 'No'}\n"
                    output += f"- **Mergeable:** {pr['mergeable']}\n"
                    output += f"- **State:** {pr['mergeable_state']}\n"
                    output += f"- **Branch:** {pr['head_branch']} → {pr['base_branch']}\n"
                    output += f"- **Dependabot:** {'Yes' if pr['is_dependabot'] else 'No'}\n"
                    output += f"- **URL:** {pr['url']}\n\n"
            else:
                output += "No open pull requests.\n"
            
            return [TextContent(type="text", text=output)]

        elif name == "github_auto_merge":
            owner = validate_github_repo_name(arguments.get("owner", ""))
            repo = validate_github_repo_name(arguments.get("repo", ""))
            merge_method = arguments.get("merge_method", "squash")
            
            results = auto_merge_prs(owner, repo, merge_method=merge_method)
            
            # Format output
            output = f"# Auto-Merge Results: {owner}/{repo}\n\n"
            output += f"**Total PRs Processed:** {results['total_prs']}\n"
            output += f"**Merge Method:** {results['merge_method']}\n"
            output += f"**Successful Merges:** {results['successful_merges']}\n"
            output += f"**Failed Merges:** {results['failed_merges']}\n"
            output += f"**Skipped Drafts:** {results['skipped_drafts']}\n\n"
            
            if results.get('stopped_early'):
                output += f"⚠️ **Stopped Early:** {results['stop_reason']}\n\n"
            
            output += "## Detailed Results\n\n"
            for result in results['results']:
                status = "✓" if result['success'] else "✗"
                output += f"{status} **PR #{result['pr_number']}:** {result['pr_title']}\n"
                output += f"   - **Author:** {result['pr_author']}\n"
                
                if result['success']:
                    output += f"   - **Status:** Merged successfully\n"
                    if 'sha' in result:
                        output += f"   - **Commit SHA:** {result['sha'][:7]}\n"
                else:
                    output += f"   - **Status:** {result['reason']}\n"
                    output += f"   - **Message:** {result['message']}\n"
                
                output += "\n"
            
            return [TextContent(type="text", text=output)]

        elif name == "github_default_branch_commands":
            owner = validate_github_repo_name(arguments.get("owner", ""))
            repo = validate_github_repo_name(arguments.get("repo", ""))
            new_default = validate_branch_name(arguments.get("new_default", ""))
            
            commands = generate_default_branch_commands(owner, repo, new_default)
            
            # Format output
            output = f"# Change Default Branch: {owner}/{repo} → {new_default}\n\n"
            output += f"**Note:** {commands['note']}\n\n"
            
            output += "## Using GitHub CLI (gh)\n\n"
            output += "```bash\n"
            output += commands['commands']['gh_cli']
            output += "\n```\n\n"
            
            output += "## Using curl\n\n"
            output += "```bash\n"
            output += commands['commands']['curl']
            output += "\n```\n\n"
            
            output += "## Using Web UI\n\n"
            output += commands['commands']['web_ui']
            output += "\n"
            
            return [TextContent(type="text", text=output)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except GitHubClientError as e:
        logger.error(f"GitHub client error: {e}")
        return [TextContent(type="text", text=f"GitHub Error: {str(e)}")]
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
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
