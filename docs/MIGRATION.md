# Migration Guide: Notion to Local JSON

## Overview
This guide explains how to migrate from Notion-based data storage to local JSON files.

## Why Use Local JSON?
- **Offline Access**: No internet connection required
- **Faster Performance**: No API calls, instant data access
- **Version Control**: Track changes in Git
- **No API Limits**: No rate limiting concerns
- **Free**: No Notion API costs

## Data Format

The local JSON format (`data/codex.json`) follows this structure:

```json
{
  "version": "1.0.0",
  "metadata": {
    "title": "CompText Codex",
    "description": "Domain-Specific Language for efficient LLM interaction",
    "last_updated": "2024-01-31"
  },
  "modules": [
    {
      "id": "unique-module-id",
      "url": "https://github.com/...",
      "titel": "Module Title",
      "beschreibung": "Module description",
      "modul": "Modul A: Allgemeine Befehle",
      "typ": "Dokumentation",
      "tags": ["Core", "Basis"],
      "created_time": "2024-01-01T00:00:00.000Z",
      "last_edited_time": "2024-01-15T00:00:00.000Z",
      "content": "# Full module content in Markdown\n\n..."
    }
  ]
}
```

## Migration Steps

### Option 1: Manual Export

1. **Export from Notion**:
   - Open your Notion database
   - Click "..." menu → Export
   - Choose "Markdown & CSV" format
   - Download the export

2. **Convert to JSON**:
   - Use the provided conversion script (see below)
   - Or manually create JSON following the format above

3. **Update Configuration**:
   ```bash
   # In .env file
   COMPTEXT_DATA_SOURCE=local
   COMPTEXT_CODEX_PATH=data/codex.json
   ```

### Option 2: Use Export Script (Recommended)

Create a Python script to export from Notion:

```python
#!/usr/bin/env python3
"""Export Notion database to local JSON format"""

import json
import os
from datetime import datetime
from notion_client import Client

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_API_TOKEN"))
database_id = os.getenv("COMPTEXT_DATABASE_ID")

# Query all pages
response = notion.databases.query(database_id=database_id)

# Convert to local format
modules = []
for page in response["results"]:
    # Extract properties
    props = page["properties"]
    
    # Get content blocks
    blocks = notion.blocks.children.list(block_id=page["id"])
    content = convert_blocks_to_markdown(blocks["results"])  # Implement this
    
    module = {
        "id": page["id"],
        "url": page["url"],
        "titel": get_text(props.get("Titel", {}).get("title", [])),
        "beschreibung": get_text(props.get("Beschreibung", {}).get("rich_text", [])),
        "modul": props.get("Modul", {}).get("select", {}).get("name", ""),
        "typ": props.get("Typ", {}).get("select", {}).get("name", ""),
        "tags": [t["name"] for t in props.get("Tags", {}).get("multi_select", [])],
        "created_time": page["created_time"],
        "last_edited_time": page["last_edited_time"],
        "content": content
    }
    modules.append(module)

# Create output structure
output = {
    "version": "1.0.0",
    "metadata": {
        "title": "CompText Codex",
        "description": "Exported from Notion",
        "last_updated": datetime.now().isoformat()
    },
    "modules": modules
}

# Save to file
with open("data/codex.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Exported {len(modules)} modules to data/codex.json")
```

### Option 3: Use Sample Data

The repository includes sample data in `data/codex.json` with 15 example modules covering all module categories (A-M). You can:
- Use it directly for testing
- Extend it with your own modules
- Replace it completely with your content

## Switching Between Data Sources

You can switch between Notion and local JSON at any time:

**To use Local JSON:**
```bash
export COMPTEXT_DATA_SOURCE=local
export COMPTEXT_CODEX_PATH=data/codex.json
python -m comptext_mcp.server
```

**To use Notion:**
```bash
export COMPTEXT_DATA_SOURCE=notion
export NOTION_API_TOKEN=your_token
export COMPTEXT_DATABASE_ID=your_db_id
python -m comptext_mcp.server
```

## Maintaining Local Data

### Adding New Modules

Edit `data/codex.json` and add entries to the `modules` array:

```json
{
  "id": "new-module-id",
  "url": "https://...",
  "titel": "New Module",
  "beschreibung": "Description",
  "modul": "Modul X: Category",
  "typ": "Dokumentation",
  "tags": ["Core"],
  "created_time": "2024-01-31T00:00:00.000Z",
  "last_edited_time": "2024-01-31T00:00:00.000Z",
  "content": "# Module content..."
}
```

### Version Control

Track your codex changes with Git:

```bash
git add data/codex.json
git commit -m "Add new module: XYZ"
git push
```

### Sync with Team

Share your local codex with team members:
1. Commit to Git repository
2. Team members pull latest changes
3. Server automatically reloads data

## Benefits of Local JSON

| Feature | Notion API | Local JSON |
|---------|------------|------------|
| Setup Complexity | High (API token, DB ID) | Low (just a file) |
| Offline Access | ❌ No | ✅ Yes |
| Performance | ~100-500ms | <10ms |
| Rate Limits | ✅ 3 req/sec | ✅ None |
| Cost | Paid Notion account | Free |
| Version Control | Limited | Full Git support |
| Team Sync | Notion sharing | Git workflow |

## Troubleshooting

### Error: "Codex file not found"
Make sure `data/codex.json` exists and `COMPTEXT_CODEX_PATH` points to it.

### Error: "Invalid JSON format"
Validate your JSON with `python -m json.tool data/codex.json`

### Changes Not Reflected
Clear cache: The local client caches data. Restart the server to reload.

## Support

For questions or issues:
- Check [FAQ.md](docs/FAQ.md)
- Open an issue on GitHub
- Review sample data in `data/codex.json`
