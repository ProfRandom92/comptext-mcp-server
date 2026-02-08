"""Tests for utility validation functions"""

import pytest
from comptext_mcp.utils import (
    validate_github_repo_name,
    validate_branch_name,
    validate_page_id,
    truncate_text,
)


def test_validate_github_repo_name_valid():
    """Test valid GitHub repo names"""
    assert validate_github_repo_name("comptext-mcp-server") == "comptext-mcp-server"
    assert validate_github_repo_name("test_repo") == "test_repo"
    assert validate_github_repo_name("repo.name") == "repo.name"
    assert validate_github_repo_name("Repo123") == "Repo123"


def test_validate_github_repo_name_empty():
    """Test empty repo name raises error"""
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_github_repo_name("")
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_github_repo_name("   ")


def test_validate_github_repo_name_invalid():
    """Test invalid repo name raises error"""
    with pytest.raises(ValueError, match="Invalid"):
        validate_github_repo_name("repo name")  # Space not allowed
    with pytest.raises(ValueError, match="Invalid"):
        validate_github_repo_name("repo@name")  # @ not allowed


def test_validate_branch_name_valid():
    """Test valid branch names"""
    assert validate_branch_name("main") == "main"
    assert validate_branch_name("feature/new-feature") == "feature/new-feature"
    assert validate_branch_name("v1.0.0") == "v1.0.0"


def test_validate_branch_name_empty():
    """Test empty branch name raises error"""
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_branch_name("")
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_branch_name("   ")


def test_validate_branch_name_invalid():
    """Test invalid branch names raise error"""
    with pytest.raises(ValueError, match="Invalid"):
        validate_branch_name("branch name")  # Space not allowed
    with pytest.raises(ValueError, match="Invalid"):
        validate_branch_name("branch~1")  # ~ not allowed
    with pytest.raises(ValueError, match="Invalid"):
        validate_branch_name("branch:name")  # : not allowed


def test_validate_page_id_empty_and_uuid():
    """Page ID validation handles empty and UUID inputs."""
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_page_id("")
    import uuid

    uid = uuid.uuid4()
    normalized = validate_page_id(uid.hex)
    assert normalized == uid.hex


def test_truncate_text_token_efficiency():
    """Truncates long NL text with custom suffix to preserve tokens."""
    text = "Dies ist ein sehr langer natürlicher Sprachbefehl für Claude, der gekürzt werden sollte, um Tokens zu sparen."
    truncated = truncate_text(text, max_length=50, suffix="…")
    assert truncated.endswith("…")
    assert len(truncated) == 50
    assert "Tokens zu sparen" not in truncated


def test_truncate_text_no_truncation_needed():
    """Returns original text when below limit (no extra tokens)."""
    text = "Kurzer NL Befehl"
    truncated = truncate_text(text, max_length=50, suffix="…")
    assert truncated == text


def test_truncate_text_empty():
    """Handles empty text safely for NL flows."""
    assert truncate_text("", max_length=10) == ""
