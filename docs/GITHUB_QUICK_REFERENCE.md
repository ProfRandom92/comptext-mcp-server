# GitHub Automation Quick Reference

## Quick Start

### 1. Set up GitHub Token
```bash
export GITHUB_TOKEN=your_personal_access_token
```

### 2. Add to .env file
```bash
echo "GITHUB_TOKEN=your_token" >> .env
```

## MCP Tool Usage

### Audit a Repository
```json
{
  "tool": "github_audit",
  "arguments": {
    "owner": "ProfRandom92",
    "repo": "comptext-mcp-server"
  }
}
```

**Returns:**
- Default branch name
- All branches with last commit info (showing top 10)
- All open PRs with:
  - Draft status
  - Mergeable state
  - Dependabot indicator
  - Branch information

### Auto-Merge Pull Requests
```json
{
  "tool": "github_auto_merge",
  "arguments": {
    "owner": "ProfRandom92",
    "repo": "comptext-mcp-server",
    "merge_method": "squash"
  }
}
```

**Merge Methods:**
- `squash` - Squash all commits into one (default)
- `merge` - Standard merge commit
- `rebase` - Rebase and merge

**Behavior:**
- Processes PRs from oldest to newest
- Skips draft PRs automatically
- Includes Dependabot PRs
- Stops on first failure (conflict or CI error)

### Generate Default Branch Commands
```json
{
  "tool": "github_default_branch_commands",
  "arguments": {
    "owner": "ProfRandom92",
    "repo": "comptext-mcp-server",
    "new_default": "main"
  }
}
```

**Returns:**
- GitHub CLI command
- curl command
- Web UI instructions

## Python API Usage

### Direct Function Calls
```python
from comptext_mcp.github_client import (
    audit_repository,
    auto_merge_prs,
    generate_default_branch_commands,
)

# Audit
audit = audit_repository("owner", "repo")
print(f"Open PRs: {audit['total_open_prs']}")

# Auto-merge (careful!)
results = auto_merge_prs("owner", "repo", merge_method="squash")
print(f"Merged: {results['successful_merges']}")

# Get commands
commands = generate_default_branch_commands("owner", "repo", "main")
print(commands['commands']['gh_cli'])
```

## Common Workflows

### Workflow 1: Audit Before Merge
```bash
# 1. Audit all repos
github_audit -> ProfRandom92/comptext-mcp-server
github_audit -> ProfRandom92/comptext-codex
github_audit -> ProfRandom92/comptext-docs

# 2. Review results, note draft PRs

# 3. Auto-merge each repo
github_auto_merge -> ProfRandom92/comptext-mcp-server
github_auto_merge -> ProfRandom92/comptext-codex
github_auto_merge -> ProfRandom92/comptext-docs
```

### Workflow 2: Handle Merge Conflicts
If auto-merge stops due to conflicts:

1. Check the PR that caused the stop
2. Resolve conflicts manually on GitHub
3. Re-run auto-merge for remaining repos
4. Continue with next repository

### Workflow 3: Update Default Branches
```bash
# 1. Identify current default
github_audit -> owner/repo

# 2. Get commands
github_default_branch_commands -> owner/repo, new_default: main

# 3. Execute command (choose one):
# - Run gh CLI command
# - Run curl command  
# - Use Web UI
```

## Troubleshooting

### "GITHUB_TOKEN environment variable not set"
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

### "Repository not found"
- Check repository name spelling
- Verify token has access to the repo
- Ensure owner name is correct

### "PR is not mergeable"
Causes:
- Merge conflicts exist
- CI checks are failing
- Required reviews missing
- Branch protection rules not met

Solution: Fix the issue manually, then continue

### Rate Limiting
GitHub API limits:
- 5000 requests/hour (authenticated)
- 60 requests/hour (unauthenticated)

Wait for rate limit to reset if exceeded.

## Safety Tips

✅ **DO:**
- Audit before merging
- Review draft PRs separately
- Check CI status before auto-merge
- Start with least critical repos
- Keep token secure

❌ **DON'T:**
- Auto-merge without auditing first
- Commit tokens to version control
- Merge with failing CI
- Skip manual review for important changes
- Use on production without testing

## Token Permissions

Required permissions:
- ✅ `repo` (full repository access)
- ✅ `workflow` (optional, for workflow updates)

## Examples

See `examples/github_automation_example.py` for complete code examples.
