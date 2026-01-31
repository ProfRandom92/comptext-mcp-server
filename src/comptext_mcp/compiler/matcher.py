from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .registry import Bundle, Registry


@dataclass(frozen=True)
class MatchResult:
    bundle_id: str
    score: int
    hits: List[str]


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def score_bundles(text: str, registry: Registry) -> List[MatchResult]:
    t = _normalize(text)
    results: List[MatchResult] = []

    for b in registry.bundles.values():
        score = 0
        hits: List[str] = []
        for kw in b.keywords_any:
            nkw = _normalize(kw)
            if nkw and nkw in t:
                score += 2
                hits.append(kw)

        # light domain/task bias via obvious tokens (keeps it deterministic, no LLM needed)
        if b.domain in ("docs",) and any(x in t for x in ["docs", "documentation", "readme", "openapi", "swagger"]):
            score += 1
        if b.domain in ("security",) and any(x in t for x in ["security", "vulnerability", "cve", "owasp"]):
            score += 1
        if b.domain in ("devops",) and any(x in t for x in ["ci", "cd", "github actions", "kubernetes", "helm", "deploy"]):
            score += 1
        if b.domain in ("code",) and any(x in t for x in ["code", "function", "class", "refactor", "debug", "performance"]):
            score += 1

        if score > 0:
            results.append(MatchResult(bundle_id=b.id, score=score, hits=hits))

    # deterministic sort: highest score, then lexicographic ID
    results.sort(key=lambda r: (-r.score, r.bundle_id))
    return results


def best_bundle(text: str, registry: Registry) -> Tuple[MatchResult | None, float]:
    results = score_bundles(text, registry)
    if not results:
        return None, 0.0

    top = results[0]
    # ambiguity penalty if next score is very close
    ambiguity_penalty = 0
    if len(results) > 1 and (top.score - results[1].score) <= 1:
        ambiguity_penalty = 1

    raw = max(0, top.score - ambiguity_penalty)
    confidence = min(1.0, raw / 7.0)  # Adjusted to 7.0 for reasonable confidence scores
    return top, confidence
