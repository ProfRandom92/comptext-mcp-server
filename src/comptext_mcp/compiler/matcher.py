"""Matcher module for bundle selection from natural language.

This module implements deterministic keyword-based matching to select
the most appropriate bundle for a given natural language input.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .registry import Bundle, Registry


@dataclass(frozen=True)
class MatchResult:
    """Result of matching natural language to a bundle.
    
    Attributes:
        bundle_id: ID of the matched bundle
        score: Match score (higher is better)
        hits: List of matched keywords
    """
    bundle_id: str
    score: int
    hits: List[str]


def _normalize(text: str) -> str:
    """Normalize text for matching (lowercase, single spaces).
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text string
    """
    return " ".join(text.lower().strip().split())


def score_bundles(text: str, registry: Registry) -> List[MatchResult]:
    """Score all bundles against input text using keyword matching.
    
    Scoring rules:
    - Each matched keyword: +2 points
    - Domain-specific bonus: +1 point for domain relevance
    - Results sorted by score (desc), then bundle ID (asc) for determinism
    
    Args:
        text: Natural language input text
        registry: Registry containing bundles to match against
        
    Returns:
        List of MatchResult objects sorted by relevance (best first)
    """
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
    """Find the best matching bundle with confidence score.
    
    Applies ambiguity penalty if top two matches are very close.
    Confidence is normalized to [0.0, 1.0] range.
    
    Args:
        text: Natural language input text
        registry: Registry containing bundles to match against
        
    Returns:
        Tuple of (MatchResult or None, confidence)
        - MatchResult is None if no matches found
        - confidence < 0.65 indicates low confidence (clarification needed)
        
    Example:
        >>> match, conf = best_bundle("review this code", registry)
        >>> match.bundle_id
        'code.review.v1'
        >>> conf > 0.65
        True
    """
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
