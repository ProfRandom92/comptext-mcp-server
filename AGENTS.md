# AGENTS.md — CompText NL→CompText Compiler (MCP-first)

## Mission
Add an MCP tool `nl_to_comptext` to comptext-mcp-server.
The tool converts Natural Language into canonical, bundle-first CompText.

## Hard Rules
1) Bundle-first: prefer `use:<bundle-id>` over inline commands.
2) No invented commands: output bundle/profile IDs must exist in `bundles/bundles.yaml`.
3) Canonical order: profile → bundles → deltas.
4) Deterministic: same input → same output.
5) Low confidence → return exactly one clarifying question.

## Deliverables
- bundles/bundles.yaml (registry)
- src/comptext_mcp/compiler/* (registry + matcher + canonicalizer + compiler)
- MCP tool wired in src/comptext_mcp/server.py
- tests with golden prompts
- CI workflow

## Acceptance Criteria
- `nl_to_comptext` appears in `list_tools()`
- For every prompt in tests/fixtures/golden_prompts.json:
  - output is valid canonical DSL
  - uses only known IDs
  - deterministic across runs
- Confidence < 0.65 → clarification question (single sentence)
