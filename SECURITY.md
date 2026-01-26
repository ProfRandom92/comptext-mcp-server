# Security Policy

## 🛡️ Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## 🔒 Reporting a Vulnerability

We take the security of CompText MCP Server seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do NOT:

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed

### Please DO:

1. **Email us privately**: 159939812+ProfRandom92@users.noreply.github.com
2. **Provide details**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. **Allow us time** to investigate and fix the issue before any public disclosure

### What to Expect:

- **Within 48 hours**: We will acknowledge receipt of your report
- **Within 7 days**: We will provide an initial assessment
- **Within 30 days**: We will release a fix or provide a mitigation plan

## 🔐 Security Measures

### Code Security

- **Type Safety**: Full type hints with mypy checking
- **Input Validation**: Pydantic models for all inputs
- **Error Handling**: Comprehensive error handling without leaking sensitive data
- **Logging**: Structured logging without sensitive information

### Dependencies

- **Regular Updates**: Dependencies updated monthly
- **Vulnerability Scanning**: Automated scanning with dependabot
- **Minimal Dependencies**: Only essential packages included

### API Security

- **Input Sanitization**: All inputs validated and sanitized
- **Rate Limiting**: Protection against abuse (when deployed)
- **CORS Configuration**: Proper CORS headers in REST API
- **No Sensitive Data**: No credentials stored in code

### Deployment Security

- **Environment Variables**: Secrets managed via environment variables
- **Docker Security**: Minimal base images, non-root user
- **HTTPS Only**: Enforce HTTPS in production deployments

## 🔍 Security Best Practices for Users

### When Deploying

1. **Use Environment Variables**: Never hardcode secrets
   ```bash
   export NOTION_API_TOKEN="your_token_here"
   export COMPTEXT_DATABASE_ID="your_db_id"
   ```

2. **Enable HTTPS**: Always use HTTPS in production
   ```python
   uvicorn_ssl_keyfile = "/path/to/keyfile.pem"
   uvicorn_ssl_certfile = "/path/to/certfile.pem"
   ```

3. **Restrict Access**: Use firewall rules to limit access
   ```bash
   # Only allow specific IPs
   ufw allow from 192.168.1.0/24 to any port 10000
   ```

4. **Keep Updated**: Regularly update to latest version
   ```bash
   pip install --upgrade comptext-mcp-server
   ```

### When Integrating

1. **Validate Inputs**: Always validate user inputs before passing to MCP
2. **Handle Errors**: Implement proper error handling
3. **Monitor Logs**: Set up log monitoring for suspicious activity
4. **Limit Scope**: Use minimal permissions for API tokens

## 🚨 Known Security Considerations

### MCP Protocol

- **Stdio Communication**: MCP uses stdio for communication - ensure proper process isolation
- **Tool Execution**: MCP tools execute with same permissions as server process
- **Input Validation**: Always validate inputs from MCP clients

### REST API

- **No Built-in Authentication**: REST API has no built-in auth - add authentication layer when exposing publicly
- **Rate Limiting**: Implement rate limiting for public deployments
- **Input Size**: Set reasonable request size limits

## 📜 Security Updates

Security updates are released as patch versions (X.X.X) and documented in:
- This SECURITY.md file
- CHANGELOG.md
- GitHub Security Advisories

Subscribe to repository releases to stay informed about security updates.

## 🏆 Security Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities:

*(No vulnerabilities reported yet)*

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [MCP Security Guidelines](https://modelcontextprotocol.io/security)

---

Thank you for helping keep CompText MCP Server secure! 🙏
