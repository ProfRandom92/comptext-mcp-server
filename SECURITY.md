# Security Policy

## Supported Versions

We release patches for the most recent version as needed.

| Version | Supported          |
| ------- | ----------------- |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:               |

## Reporting a Vulnerability

If you discover a security vulnerability, please send an e-mail to the maintainers at 159939812+ProfRandom92@users.noreply.github.com. All security vulnerabilities will be promptly addressed.

Please include the following information:

- A description of the vulnerability
- Steps to reproduce the vulnerability
- Possible impact of the vulnerability
- Any potential solutions or workarounds

## Security Features

### Input Validation & Sanitization

- **Page ID Validation**: All Notion page IDs are validated against regex patterns
- **Query String Sanitization**: Search queries are sanitized and length-limited (max 200 chars)
- **Text Output Sanitization**: All text output is sanitized to prevent control character injection
- **Type Validation**: Strong type checking with Pydantic models

### Rate Limiting

The REST API implements rate limiting per IP address:

- **Root/Info endpoints**: 60 requests/minute
- **Health checks**: 120 requests/minute
- **Data endpoints**: 30 requests/minute
- **Search endpoints**: 20 requests/minute
- **Cache/Admin operations**: 5 requests/minute

### Authentication & Authorization

- **API Token**: Notion API token stored securely in environment variables
- **Non-root Docker User**: Containers run as non-privileged user (UID 1000)
- **CORS Configuration**: Configurable CORS settings for production deployment

### Error Handling

- **Retry Logic**: Exponential backoff for API failures (3 retries max)
- **Error Sanitization**: Error messages are sanitized to prevent information leakage
- **Graceful Degradation**: Services continue operating when non-critical components fail

### Dependency Security

- **Minimal Dependencies**: Only essential packages are included
- **Version Pinning**: All dependencies use minimum version constraints
- **Regular Updates**: Dependencies are regularly reviewed and updated

### Docker Security

- **Multi-stage Builds**: Minimize attack surface with smaller images
- **Non-root User**: All containers run as non-privileged user
- **Health Checks**: Built-in health monitoring
- **Minimal Base Image**: Using slim Python images

## Security Best Practices for Deployment

### Environment Variables

Never commit sensitive information:

```bash
# ❌ Never do this
NOTION_API_TOKEN=secret_xyz123

# ✅ Use environment-specific configurations
NOTION_API_TOKEN=${NOTION_TOKEN_FROM_ENV}
```

### CORS Configuration

For production, restrict CORS origins:

```python
# Development (permissive)
allow_origins=["*"]

# Production (restrictive)
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

### Rate Limiting

Adjust rate limits based on your usage patterns:

```python
# More restrictive for public APIs
@limiter.limit("10/minute")

# More permissive for internal services
@limiter.limit("100/minute")
```

### Monitoring

- Enable logging in production
- Monitor failed authentication attempts
- Track unusual API usage patterns
- Set up alerts for security events

### Infrastructure

- Use HTTPS for all deployments
- Keep Render.com/hosting platform updated
- Enable automatic security updates
- Use secrets management (not .env files in production)

## Known Security Considerations

### Current Limitations

1. **No Authentication on REST API**: The public REST API has no authentication. Consider adding API key authentication for production use.

2. **CORS Wide Open**: Current configuration allows all origins. Restrict this in production.

3. **No Request Size Limits**: Consider adding request body size limits.

4. **Cache Timing Attacks**: LRU cache might leak timing information. Consider constant-time operations for sensitive data.

### Recommended Improvements

1. **Add API Key Authentication**:
   ```python
   from fastapi import Header, HTTPException
   
   async def verify_api_key(x_api_key: str = Header(...)):
       if x_api_key != os.getenv("API_KEY"):
           raise HTTPException(status_code=403)
   ```

2. **Implement Request Signing**: For critical operations, implement HMAC request signing.

3. **Add Audit Logging**: Log all API access with timestamps and IP addresses.

4. **Implement Circuit Breakers**: Prevent cascade failures with circuit breaker pattern.

## Security Checklist for Production

- [ ] Set strong Notion API token
- [ ] Restrict CORS origins to known domains
- [ ] Enable HTTPS
- [ ] Configure stricter rate limits
- [ ] Add API key authentication
- [ ] Enable audit logging
- [ ] Set up monitoring and alerts
- [ ] Review and minimize CORS settings
- [ ] Use secrets management system
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Configure firewall rules

## Acknowledgments

We thank the security research community for helping keep CompText secure.

## Contact

For security concerns, contact: 159939812+ProfRandom92@users.noreply.github.com