from __future__ import annotations

from typing import Optional

from .canonicalize import pick_profile_id, render_dsl
from .matcher import best_bundle
from .registry import load_registry


def _clarifying_question(text: str) -> str:
    # single-sentence, deterministic question
    return "Meinst du Code-Review, Performance-Optimierung, Debugging, Security-Scan oder Dokumentation? Bitte wähle eines."


def compile_nl_to_comptext(
    text: str,
    audience: str = "dev",
    mode: str = "bundle_only",
    return_mode: str = "dsl_plus_confidence",
    registry_path: Optional[str] = None,
) -> str:
    reg = load_registry(registry_path)
    profile_id = pick_profile_id(audience, reg)

    match, confidence = best_bundle(text, reg)

    if match is None or confidence < 0.65:
        # bundle_only: do not guess; ask
        question = _clarifying_question(text)
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
