"""Canonicalization module for CompText DSL output.

This module handles conversion of matched bundles and profiles into
canonical CompText DSL format with deterministic ordering.
"""

from __future__ import annotations

from typing import List, Optional

from .registry import Registry


def pick_profile_id(audience: str) -> str:
    """Select appropriate profile ID based on audience.

    Args:
        audience: Target audience ('dev', 'audit', or 'exec')

    Returns:
        Profile ID string (defaults to 'profile.dev.v1' if unknown)
    """
    audience = (audience or "dev").lower().strip()
    if audience == "audit":
        return "profile.audit.v1"
    if audience == "exec":
        return "profile.exec.v1"
    return "profile.dev.v1"


def render_dsl(profile_id: str, bundle_ids: List[str], deltas: Optional[List[str]] = None) -> str:
    """Render canonical CompText DSL from profile and bundles.

    Output follows canonical order: profile → bundles → deltas

    Args:
        profile_id: Profile identifier to use
        bundle_ids: List of bundle identifiers to include
        deltas: Optional list of delta modifications (sorted deterministically)

    Returns:
        Canonical DSL string with newline-separated use: directives

    Example:
        >>> render_dsl('profile.dev.v1', ['code.review.v1'])
        'use:profile.dev.v1\\nuse:code.review.v1'
    """
    lines: List[str] = []
    lines.append(f"use:{profile_id}")
    for bid in bundle_ids:
        line = f"use:{bid}"
        if deltas:
            # keep deltas short and deterministic
            line += " " + " ".join(sorted(deltas))
        lines.append(line)
    return "\n".join(lines)
