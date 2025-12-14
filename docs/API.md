# API Documentation

## REST API Endpoints

Base URL: `http://localhost:8000` (development) or `https://your-domain.com` (production)

### Core Information

#### Health Check

```bash
GET /health
```

**Rate Limit:** 120 requests/minute

Returns:
```json
{
  "status": "healthy",
  "notion_connected": true,
  "modules_count": 150
}
```

#### Root Information

```bash
GET /
```

**Rate Limit:** 60 requests/minute

Returns API information and available endpoints.

---

### Module Operations

#### List All Modules

```bash
GET /api/modules
```

**Rate Limit:** 30 requests/minute

Returns all modules grouped by type with statistics.

**Response:**
```json
{
  "total_modules": 13,
  "total_entries": 150,
  "modules": {
    "A": {
      "name": "Modul A: Allgemeine Befehle",
      "count": 15,
      "entries": [...]
    },
    ...
  }
}
```

#### Get Specific Module

```bash
GET /api/modules/{module}
```

**Rate Limit:** 30 requests/minute

**Parameters:**
- `module`: Module letter (A-M) or full name

**Example:**
```bash
curl http://localhost:8000/api/modules/B

# Or with full name
curl http://localhost:8000/api/modules/Modul%20B:%20Programmierung
```

**Response:**
```json
{
  "module": "Modul B: Programmierung",
  "count": 23,
  "entries": [
    {
      "id": "...",
      "url": "https://notion.so/...",
      "titel": "Python Development",
      "beschreibung": "...",
      "modul": "Modul B: Programmierung",
      "typ": "Dokumentation",
      "tags": ["Core", "Python"]
    },
    ...
  ]
}
```

---

### Search & Filtering

#### Search

```bash
GET /api/search?query={query}&max_results={limit}
```

**Rate Limit:** 20 requests/minute (lower due to computational cost)

**Parameters:**
- `query`: Search term (required, max 200 characters)
- `max_results`: Max results (1-100, default: 20)

**Validation:**
- Query string is sanitized
- Empty queries are rejected
- Maximum length enforced

**Example:**
```bash
curl "http://localhost:8000/api/search?query=docker&max_results=10"
```

**Response:**
```json
{
  "query": "docker",
  "count": 5,
  "results": [...]
}
```

#### Filter by Tag

```bash
GET /api/tags/{tag}
```

**Rate Limit:** 30 requests/minute

**Valid Tags:**
- Core
- Erweitert
- Optimierung
- Visualisierung
- Analyse

**Example:**
```bash
curl http://localhost:8000/api/tags/Core
```

#### Filter by Type

```bash
GET /api/types/{type}
```

**Rate Limit:** 30 requests/minute

**Valid Types:**
- Dokumentation
- Beispiel
- Test
- Referenz

**Example:**
```bash
curl http://localhost:8000/api/types/Dokumentation
```

---

### Content Retrieval

#### Get Command/Page Content

```bash
GET /api/command/{page_id}
```

**Rate Limit:** 30 requests/minute

**Parameters:**
- `page_id`: Notion page ID (with or without dashes)

**Validation:**
- Page ID format is validated (32 hex characters)
- Dashes are automatically removed

**Example:**
```bash
# With dashes
curl http://localhost:8000/api/command/0e038c9b-52c5-4666-94db-ac288280dd93

# Without dashes
curl http://localhost:8000/api/command/0e038c9b52c5466694dbac288280dd93
```

**Response:**
```json
{
  "page_info": {
    "id": "...",
    "titel": "...",
    "beschreibung": "...",
    ...
  },
  "content": "# Heading\n\nMarkdown content..."
}
```

---

### Statistics & Monitoring

#### Get Statistics

```bash
GET /api/statistics
```

**Rate Limit:** 30 requests/minute

Returns comprehensive statistics about the codex.

**Response:**
```json
{
  "total_entries": 150,
  "by_module": {
    "Modul A: Allgemeine Befehle": 15,
    "Modul B: Programmierung": 23,
    ...
  },
  "by_type": {
    "Dokumentation": 80,
    "Beispiel": 40,
    ...
  },
  "by_tag": {
    "Core": 50,
    "Erweitert": 30,
    ...
  }
}
```

#### Get Performance Metrics

```bash
GET /api/metrics
```

**Rate Limit:** 30 requests/minute

Returns server performance metrics.

**Response:**
```json
{
  "uptime_seconds": 3600,
  "total_requests": 1234,
  "total_errors": 5,
  "cache_hits": 800,
  "cache_misses": 200,
  "cache_hit_rate": 80.0,
  "endpoints": {
    "list_modules": {
      "count": 50,
      "errors": 0,
      "avg_response_time": 0.123,
      "min_response_time": 0.050,
      "max_response_time": 0.500
    },
    ...
  }
}
```

---

### Administrative Operations

#### Clear Cache

```bash
POST /api/cache/clear
```

**Rate Limit:** 5 requests/minute (very restrictive)

Clears the LRU cache, forcing fresh data from Notion on next request.

**Response:**
```json
{
  "status": "success",
  "message": "Cache cleared"
}
```

#### Reset Metrics

```bash
POST /api/metrics/reset
```

**Rate Limit:** 5 requests/minute

Resets all performance metrics to zero.

**Response:**
```json
{
  "status": "success",
  "message": "Metrics reset"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

- **200 OK**: Successful request
- **400 Bad Request**: Invalid input (e.g., malformed page ID, invalid query)
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Notion API unavailable

### Rate Limit Headers

When rate limited, response includes:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
Retry-After: 60
```

---

## MCP Tools

Available via MCP protocol (stdio mode):

### 1. list_modules

List all modules (A-M) with summary.

**Input:** None

**Output:** Markdown-formatted module overview

### 2. get_module

Load specific module with all entries.

**Input:**
```json
{
  "module": "B"  // or "Modul B: Programmierung"
}
```

**Output:** Markdown-formatted module details

### 3. get_command

Load full page content.

**Input:**
```json
{
  "page_id": "0e038c9b-52c5-4666-94db-ac288280dd93"
}
```

**Output:** Markdown-formatted page content

### 4. search

Search the codex.

**Input:**
```json
{
  "query": "docker",
  "max_results": 20  // optional
}
```

**Output:** Markdown-formatted search results

### 5. get_by_tag

Filter entries by tag.

**Input:**
```json
{
  "tag": "Core"
}
```

**Output:** Markdown-formatted filtered entries

### 6. get_by_type

Filter entries by type.

**Input:**
```json
{
  "type": "Dokumentation"
}
```

**Output:** Markdown-formatted filtered entries

### 7. get_statistics

Show codex statistics.

**Input:** None

**Output:** Markdown-formatted statistics

---

## Interactive Documentation

When REST API is running, interactive documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Request/response schemas
- Authentication testing (if enabled)
- Example requests and responses

---

## Rate Limiting Details

| Endpoint Pattern | Limit | Notes |
|-----------------|-------|-------|
| `/` | 60/min | General info |
| `/health` | 120/min | Monitoring |
| `/api/modules*` | 30/min | Module operations |
| `/api/search` | 20/min | Computationally expensive |
| `/api/command/*` | 30/min | Content retrieval |
| `/api/tags/*` | 30/min | Filtering |
| `/api/types/*` | 30/min | Filtering |
| `/api/statistics` | 30/min | Stats |
| `/api/metrics` | 30/min | Monitoring |
| `/api/cache/clear` | 5/min | Admin operation |
| `/api/metrics/reset` | 5/min | Admin operation |

Rate limits are per IP address. Consider implementing authentication for higher limits in production.

---

## Security Considerations

### Input Validation

All inputs are validated:
- Page IDs: 32 hex characters
- Query strings: Max 200 characters, sanitized
- Numeric parameters: Range-checked

### Output Sanitization

All text output is sanitized to prevent:
- Control character injection
- Script injection
- Information leakage

### Authentication

Current version has no authentication. For production:

1. Add API key authentication:
```python
from fastapi import Header

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
```

2. Use in endpoints:
```python
@app.get("/api/modules", dependencies=[Depends(verify_api_key)])
```

### CORS

Default configuration allows all origins. For production, restrict to your domains:

```python
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

---

## Client Examples

### Python

```python
import requests

# Search
response = requests.get(
    "http://localhost:8000/api/search",
    params={"query": "docker", "max_results": 10}
)
data = response.json()
print(f"Found {data['count']} results")

# Get module
response = requests.get("http://localhost:8000/api/modules/B")
module = response.json()
print(f"{module['module']}: {module['count']} entries")
```

### JavaScript/TypeScript

```javascript
// Search
const response = await fetch(
  'http://localhost:8000/api/search?query=docker&max_results=10'
);
const data = await response.json();
console.log(`Found ${data.count} results`);

// Get module
const moduleResponse = await fetch('http://localhost:8000/api/modules/B');
const module = await moduleResponse.json();
console.log(`${module.module}: ${module.count} entries`);
```

### cURL

```bash
# Search
curl -X GET "http://localhost:8000/api/search?query=docker&max_results=10"

# Get module
curl -X GET "http://localhost:8000/api/modules/B"

# Get statistics
curl -X GET "http://localhost:8000/api/statistics"

# Clear cache (POST)
curl -X POST "http://localhost:8000/api/cache/clear"
```

---

## Performance Tips

1. **Use Caching**: First call fetches from Notion, subsequent calls use cache
2. **Batch Requests**: Get full module data instead of individual items
3. **Monitor Metrics**: Use `/api/metrics` to track performance
4. **Rate Limits**: Respect rate limits to avoid 429 errors
5. **Keep-Alive**: Use HTTP keep-alive for multiple requests

---

## Troubleshooting

### Common Issues

**429 Too Many Requests**
- Wait for rate limit to reset (check Retry-After header)
- Implement exponential backoff in your client

**503 Service Unavailable**
- Notion API may be temporarily unavailable
- Server will retry automatically with exponential backoff
- Check `/health` endpoint

**400 Bad Request**
- Check input validation (page ID format, query length)
- Review error message for specific issue

**Cache Issues**
- Use `/api/cache/clear` to force refresh
- Cache TTL is 1 hour by default

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/ProfRandom92/comptext-mcp-server/issues
- Documentation: https://www.notion.so/0d571dc857144b199243ea951d60cef6
