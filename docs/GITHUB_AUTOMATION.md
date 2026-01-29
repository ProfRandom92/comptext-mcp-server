# GitHub Repository Automation

CompText MCP Server now includes tools for automating GitHub repository management tasks such as auditing repositories, automatically merging pull requests, and managing default branches.

## Features

### 1. Repository Audit (`github_audit`)

Audit a GitHub repository to get comprehensive information about:
- Default branch
- All branches with last commit information
- Open pull requests
- Draft status
- Mergeable state
- Dependabot PRs

**Usage:**
```json
{
  "tool": "github_audit",
  "arguments": {
    "owner": "ProfRandom92",
    "repo": "comptext-mcp-server"
  }
}
```

### 2. Auto-Merge Pull Requests (`github_auto_merge`)

Automatically merge all non-draft pull requests using squash & merge strategy:
- Processes PRs from oldest to newest to minimize conflicts
- Skips draft PRs
- Includes Dependabot PRs
- Stops if a PR cannot be merged due to conflicts or CI failures

**Usage:**
```json
{
  "tool": "github_auto_merge",
  "arguments": {
    "owner": "ProfRandom92",
    "repo": "comptext-mcp-server",
    "merge_method": "squash"  // Options: "squash", "merge", "rebase"
  }
}
```

**Merge Strategy:**
- **squash**: Combines all commits into a single commit (default)
- **merge**: Creates a merge commit
- **rebase**: Rebases and merges

### 3. Default Branch Commands (`github_default_branch_commands`)

Generate commands for changing the default branch of a repository. This cannot be done automatically via the GitHub API without admin permissions, so this tool provides the exact commands you need to run:

**Usage:**
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

**Outputs:**
- GitHub CLI command (`gh`)
- curl command with API token
- Web UI instructions

## Setup

### Prerequisites

1. **GitHub Personal Access Token** with the following permissions:
   - `repo` (full repository access)
   - `workflow` (for updating workflows if needed)

2. **Environment Variable**:
   ```bash
   export GITHUB_TOKEN=your_personal_access_token_here
   ```

### Installation

Add the GitHub token to your `.env` file:
```bash
# GitHub API Configuration (optional, for GitHub automation features)
GITHUB_TOKEN=your_github_token_here
```

## Workflow Example

### Auditing and Auto-Merging Multiple Repositories

1. **Audit all repositories:**
```json
// For comptext-mcp-server
{"tool": "github_audit", "arguments": {"owner": "ProfRandom92", "repo": "comptext-mcp-server"}}

// For comptext-codex
{"tool": "github_audit", "arguments": {"owner": "ProfRandom92", "repo": "comptext-codex"}}

// etc.
```

2. **Review the audit results** to understand:
   - How many PRs are open
   - Which PRs are drafts (will be skipped)
   - Which PRs are mergeable
   - Which PRs are from Dependabot

3. **Auto-merge non-draft PRs:**
```json
{"tool": "github_auto_merge", "arguments": {"owner": "ProfRandom92", "repo": "comptext-mcp-server"}}
```

4. **Handle stopped merges:**
   If the auto-merge stops due to a conflict or CI failure, the tool will report which PR caused the issue. You can then:
   - Fix the PR manually
   - Skip it and continue with other repositories
   - Re-run the auto-merge after fixing

5. **Update default branch (if needed):**
```json
{"tool": "github_default_branch_commands", "arguments": {"owner": "ProfRandom92", "repo": "comptext-mcp-server", "new_default": "main"}}
```

## Safety Features

- **Draft PRs are skipped** by default to avoid merging work-in-progress
- **Mergeable check** ensures only ready PRs are merged
- **Oldest-first strategy** minimizes merge conflicts
- **Stop on failure** prevents cascading issues
- **Detailed reporting** for transparency

## Limitations

- Cannot automatically change default branch (requires admin permissions)
- Cannot resolve merge conflicts automatically
- Requires valid GitHub token with appropriate permissions
- Rate limited by GitHub API (typically 5000 requests/hour)

## Troubleshooting

### "GITHUB_TOKEN environment variable not set"
Make sure you've set the `GITHUB_TOKEN` in your `.env` file or environment.

### "Failed to get repository"
Check that:
- The repository exists
- Your token has access to the repository
- The owner and repo names are correct

### "PR is not mergeable"
This means:
- There are merge conflicts
- CI checks are failing
- Required reviews are missing
- Branch protection rules are not satisfied

### Rate Limiting
If you hit rate limits, wait for them to reset or use a token with higher limits.

## Security

- Never commit your `GITHUB_TOKEN` to version control
- Use tokens with minimal required permissions
- Rotate tokens regularly
- Monitor token usage in GitHub settings

## References

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
