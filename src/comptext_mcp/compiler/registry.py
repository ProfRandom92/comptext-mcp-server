from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass(frozen=True)
class Profile:
    id: str
    name: str
    expansion: List[str]


@dataclass(frozen=True)
class Bundle:
    id: str
    domain: str
    task: str
    keywords_any: List[str]
    expansion: List[str]


@dataclass(frozen=True)
class Registry:
    profiles: Dict[str, Profile]
    bundles: Dict[str, Bundle]


def _repo_root() -> Path:
    # file is: src/comptext_mcp/compiler/registry.py → go up 4 to repo root
    return Path(__file__).resolve().parents[4]


def load_registry(path: Optional[str] = None) -> Registry:
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
