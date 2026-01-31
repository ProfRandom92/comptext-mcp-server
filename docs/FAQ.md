# Frequently Asked Questions (FAQ)

## General

### What is CompText MCP Server?

CompText MCP Server is an open-source tool that provides token-efficient access to your Domain-Specific Language (DSL) documentation stored in Notion. It reduces token usage by 90-95% while maintaining full LLM capabilities.

### Why should I use it?

- **Save Money**: Reduce API costs by 90-95%
- **Faster Responses**: Less data to process
- **Consistency**: Standardize team interactions
- **Flexibility**: Works with 9+ AI platforms
- **Open Source**: MIT licensed, fully customizable

### How does it work?

Instead of sending full instructions/context (25,000 tokens), you store them in Notion and reference them by ID (500 tokens). The MCP Server fetches and injects the full context when needed.

## Installation

### What are the system requirements?

- Python 3.10 or higher
- Notion account with API access
- 50MB free disk space
- Internet connection

### How long does setup take?

5-10 minutes for basic setup, depending on your platform.

### Do I need coding experience?

Basic command-line knowledge is helpful, but our setup scripts automate most of the process.

## Platform Support

### Which AI platforms are supported?

**Native MCP Support:**
- Claude Desktop
- Cursor AI
- Cline (VS Code)
- Continue.dev
- LM Studio
- Jan.ai

**REST API Support:**
- Perplexity
- ChatGPT (via Actions)
- Any HTTP client

### Can I use it with local models?

Yes! Works with Ollama, LM Studio, Jan, and any MCP-compatible client.

### Does it work with ChatGPT?

Yes, via REST API. See our [ChatGPT Integration Guide](DEPLOYMENT.md#chatgpt-actions).

## Notion Integration

### Do I need a paid Notion account?

No, free Notion accounts work perfectly.

### How do I get a Notion API token?

1. Go to https://www.notion.so/my-integrations
2. Click "+ New integration"
3. Name it "CompText MCP"
4. Copy the Internal Integration Token
5. Share your CompText database with the integration

### Can I use my own Notion database?

Yes! The default uses our CompText Codex, but you can configure any Notion database with similar structure, or use a local JSON file instead.

### Do I need a Notion account?

No! As of version 1.0, the server supports local JSON files as the default data source. Notion is now optional and only needed if you want to use Notion as your data backend.

### How do I switch between Notion and local JSON?

Set the `COMPTEXT_DATA_SOURCE` environment variable to either "local" (default) or "notion". See [MIGRATION.md](MIGRATION.md) for details.

### Where is the local codex data stored?

By default in `data/codex.json`. You can change this with the `COMPTEXT_CODEX_PATH` environment variable.

### Can I add my own modules to the local codex?

Yes! Edit `data/codex.json` and add your modules following the JSON schema. The server will automatically load them on restart.

### What database structure is required?

Minimal requirements:
- Title property (for command names)
- At least one other property (module, type, tags, etc.)
- Rich text pages (for content)

## Usage

### How do I use it in Claude?

Once configured, simply ask:
- "Show me all CompText modules"
- "Search for docker commands"
- "What's in Module B?"

### How do I use it via REST API?

```bash
curl http://localhost:8000/api/search?query=docker
```

Or integrate with any HTTP client.

### Can I use it in production?

Yes! Includes Docker support, Railway config, error handling, logging, and caching.

### Is there rate limiting?

Notion API has rate limits (3 requests/second). We implement LRU caching to minimize API calls.

## Performance

### How fast is it?

- Cached queries: 3-10ms
- Uncached queries: 150-300ms
- First load: ~1s (loads all modules)

### Does it cache responses?

Yes, LRU cache (128 entries default). You can adjust size or clear cache via API.

### What's the memory usage?

~50MB baseline, ~100MB under load.

## Troubleshooting

### Tools don't appear in Claude

1. Check config uses absolute paths
2. Verify PYTHONPATH is correct
3. Check logs: `~/.config/claude/logs/mcp*.log`
4. Restart Claude completely

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed guide.

### "ModuleNotFoundError: No module named 'comptext_mcp'"

Set PYTHONPATH:
```bash
export PYTHONPATH="/absolute/path/to/comptext-mcp-server/src"
```

### API returns 503 errors

Check:
1. NOTION_API_TOKEN is valid
2. Database is shared with integration
3. Internet connection is working
4. Notion API status: https://status.notion.so/

### Slow response times

Check cache hit rate and consider:
1. Clearing and warming cache
2. Increasing cache size
3. Checking network latency to Notion

## Development

### How can I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Can I add new features?

Yes! Fork the repo, make changes, submit a PR.

### How do I report bugs?

Open an issue on GitHub with:
- Description
- Steps to reproduce
- Environment details
- Logs (if applicable)

### Is there a roadmap?

Yes! Check [CHANGELOG.md](../CHANGELOG.md) and [TODO.md](../TODO.md).

## Licensing

### What license is it under?

MIT License - free for commercial and personal use.

### Can I use it commercially?

Yes, MIT license allows commercial use.

### Can I modify it?

Yes, modify as needed. Attribution appreciated but not required.

### Can I sell it?

Yes, but you must include the original MIT license.

## Security

### Is my Notion data secure?

Data is only accessed with your API token. We don't store or transmit your data anywhere except between you and Notion.

### Where is the API token stored?

In your `.env` file or environment variables - never in code or version control.

### Can others access my data?

Only if you deploy a public API and don't add authentication. For production, add auth middleware.

### How do I report security issues?

See [SECURITY.md](../SECURITY.md) for responsible disclosure process.

## Pricing

### Is it free?

Yes, completely free and open source.

### Are there any costs?

Only Notion API (free tier sufficient) and optional hosting costs if deploying publicly.

### What about API costs?

Notion API is free. The MCP Server itself has no cost.

## Support

### Where can I get help?

1. Check documentation
2. Search existing GitHub issues
3. Open a new issue
4. Join community discussions

### Is there a Discord/Slack?

Not yet, but may create one if community grows. For now, use GitHub Discussions.

### Can I hire someone to set it up?

Yes, though setup is designed to be straightforward. Check GitHub for contributors offering services.

## Comparison

### How is this different from RAG?

RAG retrieves documents dynamically. CompText provides structured, versioned command patterns.

### How does it compare to prompt libraries?

More dynamic and integrated. Updates in Notion reflect immediately, no code changes needed.

### Why not use context caching?

Comptext works with any LLM and provides semantic organization, not just caching.

## Future

### What's next?

See [CHANGELOG.md](../CHANGELOG.md) for roadmap:
- GraphQL API
- WebSocket support
- Multi-database support
- Admin dashboard

### Will it support [feature]?

Check roadmap or open a feature request!

### How can I stay updated?

- Star the repo
- Watch for releases
- Follow on Twitter/LinkedIn
- Subscribe to blog

---

**Still have questions?**

Open an issue: https://github.com/ProfRandom92/comptext-mcp-server/issues
