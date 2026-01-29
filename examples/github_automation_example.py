#!/usr/bin/env python3
"""
Example: Using GitHub Automation Features

This example demonstrates how to use the GitHub automation tools
in the CompText MCP Server to audit repositories and auto-merge PRs.
"""

import os
import json
from comptext_mcp.github_client import (
    audit_repository,
    auto_merge_prs,
    generate_default_branch_commands,
)


def example_audit():
    """Example: Audit a repository"""
    print("=" * 60)
    print("Example 1: Auditing a Repository")
    print("=" * 60)
    
    # Set your GitHub token
    # os.environ['GITHUB_TOKEN'] = 'your_token_here'
    
    try:
        # Audit the repository
        audit = audit_repository("ProfRandom92", "comptext-mcp-server")
        
        print(f"\nRepository: {audit['owner']}/{audit['repo']}")
        print(f"Default Branch: {audit['default_branch']}")
        print(f"Total Branches: {audit['total_branches']}")
        print(f"Total Open PRs: {audit['total_open_prs']}")
        print(f"Mergeable PRs: {audit['mergeable_prs']}")
        print(f"Draft PRs: {audit['draft_prs']}")
        
        print("\n--- Latest Branches ---")
        for i, branch in enumerate(audit['branches'][:5]):
            print(f"{i+1}. {branch['name']}")
            print(f"   Last commit: {branch['last_commit']['date']}")
            print(f"   Author: {branch['last_commit']['author']}")
        
        print("\n--- Open Pull Requests ---")
        for pr in audit['open_prs']:
            print(f"PR #{pr['number']}: {pr['title']}")
            print(f"  Author: {pr['author']}")
            print(f"  Draft: {pr['draft']}")
            print(f"  Mergeable: {pr['mergeable']}")
            print(f"  Dependabot: {pr['is_dependabot']}")
            print()
        
    except Exception as e:
        print(f"Error: {e}")


def example_auto_merge():
    """Example: Auto-merge PRs (dry run)"""
    print("\n" + "=" * 60)
    print("Example 2: Auto-Merge PRs")
    print("=" * 60)
    
    # WARNING: This will actually merge PRs!
    # Uncomment only if you're sure
    """
    try:
        results = auto_merge_prs(
            "ProfRandom92",
            "comptext-mcp-server",
            merge_method="squash"
        )
        
        print(f"\nTotal PRs Processed: {results['total_prs']}")
        print(f"Successful Merges: {results['successful_merges']}")
        print(f"Failed Merges: {results['failed_merges']}")
        print(f"Skipped Drafts: {results['skipped_drafts']}")
        
        for result in results['results']:
            status = "✓" if result['success'] else "✗"
            print(f"{status} PR #{result['pr_number']}: {result['pr_title']}")
            
    except Exception as e:
        print(f"Error: {e}")
    """
    print("\n⚠️  Auto-merge example commented out for safety")
    print("Uncomment the code in this function to actually merge PRs")


def example_default_branch_commands():
    """Example: Generate default branch change commands"""
    print("\n" + "=" * 60)
    print("Example 3: Generate Default Branch Change Commands")
    print("=" * 60)
    
    commands = generate_default_branch_commands(
        "ProfRandom92",
        "comptext-mcp-server",
        "main"
    )
    
    print(f"\nChange default branch to: {commands['new_default_branch']}")
    print(f"\nNote: {commands['note']}")
    
    print("\n--- GitHub CLI Command ---")
    print(commands['commands']['gh_cli'])
    
    print("\n--- curl Command ---")
    print(commands['commands']['curl'])
    
    print("\n--- Web UI Instructions ---")
    print(commands['commands']['web_ui'])


if __name__ == "__main__":
    # Check if GitHub token is set
    if not os.getenv("GITHUB_TOKEN"):
        print("⚠️  Warning: GITHUB_TOKEN environment variable not set")
        print("Set it with: export GITHUB_TOKEN=your_token_here")
        print("\nRunning examples anyway (some may fail)...\n")
    
    # Run examples
    example_audit()
    example_auto_merge()
    example_default_branch_commands()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
