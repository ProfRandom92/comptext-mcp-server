"""Tests for GitHub client functionality"""

import pytest
from unittest.mock import MagicMock, patch
from comptext_mcp.github_client import (
    audit_repository,
    merge_pull_request,
    auto_merge_prs,
    generate_default_branch_commands,
    GitHubClientError,
)


@pytest.fixture
def mock_github():
    """Mock GitHub client"""
    with patch("comptext_mcp.github_client.get_github_client") as mock:
        yield mock


@pytest.fixture
def mock_repo():
    """Mock GitHub repository"""
    repo = MagicMock()
    repo.default_branch = "main"
    return repo


def test_generate_default_branch_commands():
    """Test generating default branch change commands"""
    result = generate_default_branch_commands("ProfRandom92", "comptext-mcp-server", "develop")

    assert result["owner"] == "ProfRandom92"
    assert result["repo"] == "comptext-mcp-server"
    assert result["new_default_branch"] == "develop"
    assert "gh_cli" in result["commands"]
    assert "curl" in result["commands"]
    assert "web_ui" in result["commands"]
    assert "develop" in result["commands"]["gh_cli"]


def test_audit_repository_structure(mock_github, mock_repo):
    """Test audit repository returns correct structure"""
    # Setup mock
    mock_github.return_value.get_repo.return_value = mock_repo

    # Mock branches
    mock_branch = MagicMock()
    mock_branch.name = "main"
    mock_commit = MagicMock()
    mock_commit.sha = "abc123"
    mock_commit.commit.author.name = "Test User"
    mock_commit.commit.author.date = MagicMock()
    mock_commit.commit.author.date.isoformat.return_value = "2024-01-01T00:00:00"
    mock_commit.commit.message = "Test commit"
    mock_branch.commit = mock_commit
    mock_repo.get_branches.return_value = [mock_branch]

    # Mock PRs
    mock_repo.get_pulls.return_value = []

    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        result = audit_repository("owner", "repo")

    assert "owner" in result
    assert "repo" in result
    assert "default_branch" in result
    assert "branches" in result
    assert "open_prs" in result
    assert "total_branches" in result
    assert "total_open_prs" in result


def test_merge_pull_request_draft(mock_github, mock_repo):
    """Test merging a draft PR returns skipped"""
    mock_pr = MagicMock()
    mock_pr.draft = True
    mock_pr.number = 123
    mock_repo.get_pull.return_value = mock_pr
    mock_github.return_value.get_repo.return_value = mock_repo

    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        result = merge_pull_request("owner", "repo", 123)

    assert result["success"] is False
    assert result["reason"] == "skipped_draft"
    assert result["pr_number"] == 123


def test_merge_pull_request_not_mergeable(mock_github, mock_repo):
    """Test merging a non-mergeable PR"""
    mock_pr = MagicMock()
    mock_pr.draft = False
    mock_pr.mergeable = False
    mock_pr.mergeable_state = "dirty"
    mock_pr.number = 123
    mock_repo.get_pull.return_value = mock_pr
    mock_github.return_value.get_repo.return_value = mock_repo

    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        result = merge_pull_request("owner", "repo", 123)

    assert result["success"] is False
    assert result["reason"] == "not_mergeable"
    assert result["mergeable_state"] == "dirty"


def test_merge_pull_request_success(mock_github, mock_repo):
    """Test successful PR merge"""
    mock_pr = MagicMock()
    mock_pr.draft = False
    mock_pr.mergeable = True
    mock_pr.number = 123

    mock_merge_result = MagicMock()
    mock_merge_result.merged = True
    mock_merge_result.sha = "abc123"
    mock_merge_result.message = "Merged"
    mock_pr.merge.return_value = mock_merge_result

    mock_repo.get_pull.return_value = mock_pr
    mock_github.return_value.get_repo.return_value = mock_repo

    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        result = merge_pull_request("owner", "repo", 123, "squash")

    assert result["success"] is True
    assert result["pr_number"] == 123
    assert result["method"] == "squash"
    assert result["sha"] == "abc123"


def test_auto_merge_prs_skip_drafts(mock_github, mock_repo):
    """Test auto-merge skips draft PRs"""
    # Mock audit
    with patch("comptext_mcp.github_client.audit_repository") as mock_audit:
        mock_audit.return_value = {
            "owner": "owner",
            "repo": "repo",
            "open_prs": [
                {
                    "number": 1,
                    "title": "Draft PR",
                    "author": "user1",
                    "created_at": "2024-01-01T00:00:00",
                    "draft": True,
                    "mergeable": True,
                },
                {
                    "number": 2,
                    "title": "Regular PR",
                    "author": "user2",
                    "created_at": "2024-01-02T00:00:00",
                    "draft": False,
                    "mergeable": True,
                },
            ],
        }

        # Mock merge
        with patch("comptext_mcp.github_client.merge_pull_request") as mock_merge:
            mock_merge.return_value = {
                "success": True,
                "pr_number": 2,
                "sha": "abc123",
                "message": "Merged",
            }

            with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
                result = auto_merge_prs("owner", "repo")

            # Should only process non-draft PR
            assert result["total_prs"] == 1
            assert mock_merge.call_count == 1
            mock_merge.assert_called_once_with("owner", "repo", 2, "squash")


def test_no_github_token():
    """Test error when GITHUB_TOKEN is not set"""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(GitHubClientError, match="GITHUB_TOKEN"):
            audit_repository("owner", "repo")
