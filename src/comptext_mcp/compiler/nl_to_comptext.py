"""Natural Language to CompText compiler.

This module provides the main compilation function that converts
natural language requests into canonical CompText DSL using
bundle-first architecture with confidence scoring.
"""

from __future__ import annotations

from typing import Optional

from .canonicalize import pick_profile_id, render_dsl
from .matcher import best_bundle
from .registry import load_registry


def _clarifying_question() -> str:
    """Generate a deterministic clarifying question for ambiguous input.

    Note: Currently hardcoded in German. Future enhancement: i18n support.

    Returns:
        Single-sentence clarifying question in German
    """
    # TODO: Internationalization - make this configurable
    return "Meinst du Code-Review, Performance-Optimierung, Debugging, Security-Scan oder Dokumentation? Bitte wähle eines."


def compile_nl_to_comptext(
    text: str,
    audience: str = "dev",
    mode: str = "bundle_only",
    return_mode: str = "dsl_plus_confidence",
    registry_path: Optional[str] = None,
) -> str:
    """Compile natural language to canonical CompText DSL.

    This is the main entry point for the NL→CompText compiler.
    Follows hard rules:
    1. Bundle-first: prefer use:<bundle-id> over inline commands
    2. No invented commands: all IDs must exist in registry
    3. Canonical order: profile → bundles → deltas
    4. Deterministic: same input → same output
    5. Low confidence → clarifying question

    Args:
        text: Natural language input to compile
        audience: Target audience ('dev', 'audit', or 'exec')
        mode: Compilation mode ('bundle_only' or 'allow_inline_fallback')
        return_mode: Output format:
            - 'dsl_only': Just the DSL
            - 'dsl_plus_confidence': DSL + confidence score
            - 'dsl_plus_explanation': DSL + confidence + explanation
        registry_path: Optional path to bundles.yaml

    Returns:
        Compiled output string in requested format

    Raises:
        ValueError: If matched bundle not found in registry (internal error)

    Example:
        >>> compile_nl_to_comptext("review this code")
        'dsl:\\nuse:profile.dev.v1\\nuse:code.review.v1\\n\\nconfidence: 0.85\\nclarification: null'
    """
    reg = load_registry(registry_path)
    profile_id = pick_profile_id(audience)

    match, confidence = best_bundle(text, reg)

    if match is None or confidence < 0.65:
        # bundle_only: do not guess; ask
        question = _clarifying_question()
        if return_mode == "dsl_only":
            return question
        return f"dsl:\n\nconfidence: {confidence:.2f}\nclarification: {question}"

    # Guardrail: must exist
    if match.bundle_id not in reg.bundles:
        raise ValueError("Internal error: selected bundle not found in registry")

    dsl = render_dsl(profile_id, [match.bundle_id])

    if return_mode == "dsl_only":
        return dsl

    if return_mode == "dsl_plus_explanation":
        explanation = f"Matched bundle '{match.bundle_id}' via keywords: {', '.join(match.hits) if match.hits else 'n/a'}"
        return f"dsl:\n{dsl}\n\nconfidence: {confidence:.2f}\nclarification: null\nexplanation: {explanation}"

    # default: dsl_plus_confidence
    return f"dsl:\n{dsl}\n\nconfidence: {confidence:.2f}\nclarification: null"
