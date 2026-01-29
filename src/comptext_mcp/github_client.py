"""GitHub API Client for Repository Automation"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from github import Github, GithubException
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Branch import Branch

logger = logging.getLogger(__name__)


class GitHubClientError(Exception):
    """GitHub client error"""
    pass


def get_github_client() -> Github:
    """Get authenticated GitHub client"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise GitHubClientError("GITHUB_TOKEN environment variable not set")
    return Github(token)


def get_repository(owner: str, repo: str) -> Repository:
    """Get a GitHub repository"""
    try:
        client = get_github_client()
        return client.get_repo(f"{owner}/{repo}")
    except GithubException as e:
        raise GitHubClientError(f"Failed to get repository {owner}/{repo}: {e}")


def audit_repository(owner: str, repo: str) -> Dict[str, Any]:
    """
    Audit a repository: list default branch, all branches with last commit,
    open PRs, draft status, and mergeable state.
    """
    try:
        repository = get_repository(owner, repo)
        
        # Get default branch
        default_branch = repository.default_branch
        
        # Get all branches with last commit info
        branches = []
        for branch in repository.get_branches():
            commit = branch.commit
            branches.append({
                "name": branch.name,
                "last_commit": {
                    "sha": commit.sha,
                    "author": commit.commit.author.name if commit.commit.author else "Unknown",
                    "date": commit.commit.author.date.isoformat() if commit.commit.author else None,
                    "message": commit.commit.message.split("\n")[0]  # First line only
                }
            })
        
        # Sort branches by last commit date (newest first)
        branches.sort(key=lambda b: b["last_commit"]["date"] or "", reverse=True)
        
        # Get open pull requests
        open_prs = []
        for pr in repository.get_pulls(state="open", sort="created", direction="asc"):
            pr_info = {
                "number": pr.number,
                "title": pr.title,
                "author": pr.user.login,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "draft": pr.draft,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
                "head_branch": pr.head.ref,
                "base_branch": pr.base.ref,
                "url": pr.html_url,
                "is_dependabot": pr.user.login == "dependabot[bot]" or pr.user.login.startswith("dependabot"),
            }
            open_prs.append(pr_info)
        
        return {
            "owner": owner,
            "repo": repo,
            "default_branch": default_branch,
            "branches": branches,
            "open_prs": open_prs,
            "total_branches": len(branches),
            "total_open_prs": len(open_prs),
            "mergeable_prs": len([pr for pr in open_prs if pr["mergeable"] and not pr["draft"]]),
            "draft_prs": len([pr for pr in open_prs if pr["draft"]]),
        }
    except GithubException as e:
        raise GitHubClientError(f"Failed to audit repository {owner}/{repo}: {e}")


def merge_pull_request(owner: str, repo: str, pr_number: int, merge_method: str = "squash") -> Dict[str, Any]:
    """
    Merge a pull request using the specified method.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        merge_method: Merge method ("squash", "merge", or "rebase")
    
    Returns:
        Dict with merge result information
    """
    try:
        repository = get_repository(owner, repo)
        pr = repository.get_pull(pr_number)
        
        # Check if it's a draft
        if pr.draft:
            return {
                "success": False,
                "pr_number": pr_number,
                "reason": "skipped_draft",
                "message": f"PR #{pr_number} is a draft and was skipped"
            }
        
        # Check if mergeable
        if not pr.mergeable:
            return {
                "success": False,
                "pr_number": pr_number,
                "reason": "not_mergeable",
                "message": f"PR #{pr_number} is not mergeable (state: {pr.mergeable_state})",
                "mergeable_state": pr.mergeable_state
            }
        
        # Attempt to merge
        merge_result = pr.merge(merge_method=merge_method)
        
        return {
            "success": merge_result.merged,
            "pr_number": pr_number,
            "sha": merge_result.sha,
            "message": merge_result.message,
            "method": merge_method
        }
    except GithubException as e:
        return {
            "success": False,
            "pr_number": pr_number,
            "reason": "github_error",
            "message": f"GitHub API error: {e}",
            "error": str(e)
        }


def auto_merge_prs(owner: str, repo: str, merge_method: str = "squash", skip_drafts: bool = True) -> Dict[str, Any]:
    """
    Automatically merge all non-draft pull requests in order from oldest to newest.
    
    Args:
        owner: Repository owner
        repo: Repository name
        merge_method: Merge method ("squash", "merge", or "rebase")
        skip_drafts: Whether to skip draft PRs (default: True)
    
    Returns:
        Dict with merge results for all PRs
    """
    try:
        # First, audit to get the list of PRs
        audit = audit_repository(owner, repo)
        prs = audit["open_prs"]
        
        # Filter out drafts if requested
        if skip_drafts:
            prs = [pr for pr in prs if not pr["draft"]]
        
        # Sort by creation date (oldest first) to minimize conflicts
        prs.sort(key=lambda p: p["created_at"])
        
        results = {
            "owner": owner,
            "repo": repo,
            "total_prs": len(prs),
            "merge_method": merge_method,
            "results": []
        }
        
        for pr in prs:
            logger.info(f"Processing PR #{pr['number']}: {pr['title']}")
            merge_result = merge_pull_request(owner, repo, pr["number"], merge_method)
            merge_result["pr_title"] = pr["title"]
            merge_result["pr_author"] = pr["author"]
            results["results"].append(merge_result)
            
            # If merge failed due to not being mergeable, stop
            if not merge_result["success"] and merge_result.get("reason") in ["not_mergeable", "github_error"]:
                results["stopped_early"] = True
                results["stop_reason"] = f"PR #{pr['number']} could not be merged"
                logger.warning(f"Stopping auto-merge due to: {results['stop_reason']}")
                break
        
        # Calculate summary
        results["successful_merges"] = len([r for r in results["results"] if r["success"]])
        results["failed_merges"] = len([r for r in results["results"] if not r["success"]])
        results["skipped_drafts"] = len([r for r in results["results"] if r.get("reason") == "skipped_draft"])
        
        return results
    except Exception as e:
        raise GitHubClientError(f"Failed to auto-merge PRs in {owner}/{repo}: {e}")


def generate_default_branch_commands(owner: str, repo: str, new_default: str) -> Dict[str, Any]:
    """
    Generate commands to change the default branch of a repository.
    
    Note: This cannot be done automatically via the GitHub API without admin permissions.
    This function provides the commands the user can run manually.
    
    Args:
        owner: Repository owner
        repo: Repository name
        new_default: New default branch name
    
    Returns:
        Dict with commands in various formats
    """
    return {
        "owner": owner,
        "repo": repo,
        "new_default_branch": new_default,
        "note": "Changing the default branch requires admin permissions and cannot be fully automated via the GitHub API",
        "commands": {
            "gh_cli": f"gh api repos/{owner}/{repo} --method PATCH -f default_branch='{new_default}'",
            "curl": f"curl -X PATCH https://api.github.com/repos/{owner}/{repo} \\\n"
                   f"  -H 'Authorization: Bearer $GITHUB_TOKEN' \\\n"
                   f"  -H 'Accept: application/vnd.github+json' \\\n"
                   f"  -d '{{\"default_branch\": \"{new_default}\"}}'",
            "web_ui": f"1. Go to https://github.com/{owner}/{repo}/settings/branches\n"
                     f"2. In 'Default branch' section, click the switch icon\n"
                     f"3. Select '{new_default}' from the dropdown\n"
                     f"4. Click 'Update' and confirm"
        }
    }
