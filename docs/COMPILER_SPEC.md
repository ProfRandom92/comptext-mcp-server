# CompText NL→CompText Compiler Spec

## Input
- text: string (required)
- audience: dev|audit|exec (default dev)
- mode: bundle_only|allow_inline_fallback (default bundle_only)
- return: dsl_only|dsl_plus_confidence|dsl_plus_explanation (default dsl_plus_confidence)

## Output (text)
dsl:
<canonical lines>

confidence: <0..1>
clarification: <null or question>

## Canonicalization
- Always emit exactly one profile line:
  - dev → use:profile.dev.v1
  - audit → use:profile.audit.v1
  - exec → use:profile.exec.v1
- Then emit one or more bundle lines: use:<bundle-id>
- Optional deltas (rare): `+key=value` tokens appended on the same line as the bundle.

## Matching / Scoring
- keywords_any hit: +2 each
- domain match: +1
- task match: +1
- ambiguity penalty: -1 if top-2 scores are too close

Confidence:
- confidence = min(1.0, score / 7.0)
- if confidence < 0.65:
  - return a single clarifying question (no DSL in bundle_only mode unless a safe default exists)

## Guardrails
- Only IDs that exist in bundles.yaml are allowed in output.
- If mode=bundle_only and no bundle matches → return clarification.
