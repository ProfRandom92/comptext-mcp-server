# CompText Codex Data

This directory contains the local JSON data for the CompText MCP Server.

## File Format

The `codex.json` file follows this structure:

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
      "titel": "Module Title (German)",
      "beschreibung": "Module description (German)",
      "modul": "Modul A: Allgemeine Befehle",
      "typ": "Dokumentation | Beispiel | Test | Referenz",
      "tags": ["Core", "Erweitert", "Optimierung", etc.],
      "created_time": "2024-01-01T00:00:00.000Z",
      "last_edited_time": "2024-01-15T00:00:00.000Z",
      "content": "# Full module content in Markdown..."
    }
  ]
}
```

## Module Categories (A-M)

- **Modul A**: Allgemeine Befehle (General Commands)
- **Modul B**: Programmierung (Programming)
- **Modul C**: Visualisierung (Visualization)
- **Modul D**: KI-Steuerung (AI Control)
- **Modul E**: Datenanalyse & ML (Data Analysis & ML)
- **Modul F**: Dokumentation (Documentation)
- **Modul G**: Testing & QA
- **Modul H**: Database & Data Modeling
- **Modul I**: Security & Compliance
- **Modul J**: DevOps & Deployment
- **Modul K**: Frontend & UI
- **Modul L**: Data Pipelines & ETL
- **Modul M**: MCP Integration

## Entry Types

- **Dokumentation**: Reference documentation
- **Beispiel**: Example/Tutorial
- **Test**: Test case
- **Referenz**: Quick reference

## Tags

- **Core**: Essential functionality
- **Erweitert**: Advanced features
- **Optimierung**: Performance optimization
- **Visualisierung**: Visualization features
- **Analyse**: Analysis tools
- **AI**: AI-related functionality
- **ML**: Machine Learning
- **Security**: Security features
- **DevOps**: DevOps tools
- **Frontend**: Frontend/UI
- **Database**: Database-related
- **ETL**: Data processing
- **MCP**: MCP protocol

## Adding New Modules

1. Open `codex.json` in a text editor
2. Add a new entry to the `modules` array
3. Follow the structure above
4. Ensure valid JSON syntax
5. Restart the MCP server to load changes

## Example Entry

```json
{
  "id": "my-custom-module",
  "url": "https://github.com/...",
  "titel": "Custom Module",
  "beschreibung": "A custom module description",
  "modul": "Modul A: Allgemeine Befehle",
  "typ": "Beispiel",
  "tags": ["Core", "Custom"],
  "created_time": "2024-01-31T00:00:00.000Z",
  "last_edited_time": "2024-01-31T00:00:00.000Z",
  "content": "# Custom Module\n\n## Description\nYour module content here..."
}
```

## Migration from Notion

See [../docs/MIGRATION.md](../docs/MIGRATION.md) for instructions on exporting from Notion to this format.

## Validation

Validate your JSON file:

```bash
python -m json.tool data/codex.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

## Version Control

This file is tracked in Git. To update:

```bash
git add data/codex.json
git commit -m "Update codex: add new module"
git push
```
