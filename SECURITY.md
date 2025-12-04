# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

### DO NOT

- Do not open a public GitHub issue
- Do not disclose the vulnerability publicly

### DO

1. **Report privately**: Open a security advisory on GitHub:
   - Go to the repository
   - Click on "Security" tab
   - Click "Report a vulnerability"

2. **Include details**:
   - Type of vulnerability
   - Full paths of source file(s) related to the issue
   - Location of the affected source code
   - Any special configuration required to reproduce
   - Step-by-step instructions to reproduce
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue

3. **Wait for response**: We will respond within 48 hours

## Security Best Practices

### Environment Variables

- Never commit `.env` files
- Use environment variables for sensitive data
- Rotate Notion API tokens regularly

### API Token Security

```bash
# GOOD: Use environment variables
export NOTION_API_TOKEN="your_token"

# BAD: Hardcode in source
NOTION_TOKEN = "ntn_abc123..."  # Never do this!
```

### Production Deployment

- Use HTTPS for all API endpoints
- Implement rate limiting
- Enable CORS only for trusted domains
- Use secrets management (Railway secrets, etc.)
- Regular security audits

### Dependencies

- Keep dependencies up to date
- Use `pip install --upgrade`
- Review security advisories
- Run security scanners

```bash
# Check for known vulnerabilities
pip audit

# Update dependencies
pip install --upgrade -r requirements.txt
```

## Security Updates

We will notify users of security updates through:

- GitHub Security Advisories
- Release notes
- Repository README

## Bug Bounty Program

We currently do not have a bug bounty program, but we recognize and appreciate security researchers who responsibly disclose vulnerabilities.

## Contact

For security concerns, please use GitHub's security advisory feature or open an issue labeled "security".
