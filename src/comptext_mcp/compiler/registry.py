"""Registry module for CompText bundles and profiles.

This module provides the core data structures and loading functionality
for the CompText bundle registry, which defines audience profiles and
pre-optimized command bundles.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass(frozen=True)
class Profile:
    """Represents an audience profile with default configurations.

    Attributes:
        id: Unique profile identifier (e.g., 'profile.dev.v1')
        name: Human-readable name
        expansion: List of CompText commands to expand into
    """

    id: str
    name: str
    expansion: List[str]


@dataclass(frozen=True)
class Bundle:
    """Represents a pre-optimized command bundle.

    Attributes:
        id: Unique bundle identifier (e.g., 'code.review.v1')
        domain: Domain category (code, docs, security, etc.)
        task: Task type (review, optimize, debug, etc.)
        keywords_any: Keywords for matching natural language input
        expansion: List of CompText commands to expand into
    """

    id: str
    domain: str
    task: str
    keywords_any: List[str]
    expansion: List[str]


@dataclass(frozen=True)
class Registry:
    """Registry containing all profiles and bundles.

    Attributes:
        profiles: Mapping of profile IDs to Profile objects
        bundles: Mapping of bundle IDs to Bundle objects
    """

    profiles: Dict[str, Profile]
    bundles: Dict[str, Bundle]


def _repo_root() -> Path:
    """Get the repository root directory.

    Returns:
        Path to repository root (3 levels up from this file)
    """
    # file is: src/comptext_mcp/compiler/registry.py → go up 3 to repo root
    return Path(__file__).resolve().parents[3]


def load_registry(path: Optional[str] = None) -> Registry:
    """Load the bundle registry from YAML file.

    Args:
        path: Optional path to bundles.yaml. If None, uses default location.

    Returns:
        Registry object with all profiles and bundles loaded

    Raises:
        ValueError: If required profiles are missing or YAML is invalid
        FileNotFoundError: If bundles.yaml file not found
    """
    yaml_path = Path(path) if path else (_repo_root() / "bundles" / "bundles.yaml")
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    profiles: Dict[str, Profile] = {}
    for p in data.get("profiles", []):
        prof = Profile(
            id=p["id"],
            name=p.get("name", p["id"]),
            expansion=list(p.get("expansion", [])),
        )
        profiles[prof.id] = prof

    bundles: Dict[str, Bundle] = {}
    for b in data.get("bundles", []):
        keywords = list(((b.get("match") or {}).get("keywords_any")) or [])
        bun = Bundle(
            id=b["id"],
            domain=b.get("domain", ""),
            task=b.get("task", ""),
            keywords_any=keywords,
            expansion=list(b.get("expansion", [])),
        )
        bundles[bun.id] = bun

    # Guardrails: unique IDs and required profiles
    required_profiles = {"profile.dev.v1", "profile.audit.v1", "profile.exec.v1"}
    missing = required_profiles - set(profiles.keys())
    if missing:
        raise ValueError(f"Missing required profiles in registry: {sorted(missing)}")

    return Registry(profiles=profiles, bundles=bundles)
