"""Utility functions and validators for CompText MCP Server"""

import re
from typing import Optional  # noqa: F401


def validate_page_id(page_id: str) -> str:
    """
    Validate and normalize a Notion page ID.

    Args:
        page_id: Raw page ID (with or without dashes)

    Returns:
        Normalized page ID without dashes

    Raises:
        ValueError: If page ID format is invalid
    """
    if not page_id or not str(page_id).strip():
        raise ValueError("Page ID cannot be empty")

    # Normalize to string in case callers pass UUID objects
    page_id = str(page_id)
    # Remove dashes
    clean_id = page_id.replace("-", "")

    # Validate format (32 hex characters)
    if not re.match(r"^[a-f0-9]{32}$", clean_id, re.IGNORECASE):
        raise ValueError(f"Invalid page ID format: {page_id}")

    return clean_id


def validate_query_string(query: str, max_length: int = 200) -> str:
    """
    Validate and sanitize search query string.

    Args:
        query: Search query string
        max_length: Maximum allowed length

    Returns:
        Sanitized query string

    Raises:
        ValueError: If query is invalid
    """
    if not query or not query.strip():
        raise ValueError("Query string cannot be empty")

    query = query.strip()

    if len(query) > max_length:
        raise ValueError(f"Query too long (max {max_length} characters)")

    return query


def sanitize_text_output(text: str) -> str:
    """
    Sanitize text output to prevent injection attacks.

    Args:
        text: Raw text

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes and other control characters except newlines and tabs
    sanitized = "".join(char for char in text if char == "\n" or char == "\t" or ord(char) >= 32)

    return sanitized


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with optional suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def validate_github_repo_name(name: str) -> str:
    """
    Validate GitHub repository or owner name.
    
    Args:
        name: Repository or owner name
    
    Returns:
        Validated name
    
    Raises:
        ValueError: If name is invalid
    """
    if not name or not name.strip():
        raise ValueError("Repository/owner name cannot be empty")
    
    name = name.strip()
    
    # GitHub allows alphanumeric, hyphen, underscore, and period
    if not re.match(r"^[a-zA-Z0-9._-]+$", name):
        raise ValueError(f"Invalid repository/owner name: {name}")
    
    return name


def validate_branch_name(name: str) -> str:
    """
    Validate Git branch name.
    
    Args:
        name: Branch name
    
    Returns:
        Validated name
    
    Raises:
        ValueError: If name is invalid
    """
    if not name or not name.strip():
        raise ValueError("Branch name cannot be empty")
    
    name = name.strip()
    
    # Basic validation - branch names should not contain certain characters
    if any(char in name for char in [" ", "~", "^", ":", "?", "*", "["]):
        raise ValueError(f"Invalid branch name: {name}")
    
    return name
