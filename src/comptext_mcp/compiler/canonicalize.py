from __future__ import annotations

from typing import List, Optional

from .registry import Registry


def pick_profile_id(audience: str, registry: Registry) -> str:
    audience = (audience or "dev").lower().strip()
    if audience == "audit":
        return "profile.audit.v1"
    if audience == "exec":
        return "profile.exec.v1"
    return "profile.dev.v1"


def render_dsl(profile_id: str, bundle_ids: List[str], deltas: Optional[List[str]] = None) -> str:
    lines: List[str] = []
    lines.append(f"use:{profile_id}")
    for bid in bundle_ids:
        line = f"use:{bid}"
        if deltas:
            # keep deltas short and deterministic
            line += " " + " ".join(sorted(deltas))
        lines.append(line)
    return "\n".join(lines)
