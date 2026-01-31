from __future__ import annotations

import json
import os
from pathlib import Path

# Set dummy environment variable before any imports to avoid Notion client initialization errors
os.environ.setdefault("NOTION_API_TOKEN", "dummy_token_for_testing")
os.environ.setdefault("COMPTEXT_DATABASE_ID", "0e038c9b52c5466694dbac288280dd93")

from comptext_mcp.compiler.nl_to_comptext import compile_nl_to_comptext
from comptext_mcp.compiler.registry import load_registry


def test_no_invented_commands_and_deterministic():
    reg = load_registry()
    golden_path = Path(__file__).resolve().parent / "fixtures" / "golden_prompts.json"
    golden = json.loads(golden_path.read_text(encoding="utf-8"))

    for item in golden:
        text = item["text"]
        expected = item["expected_bundle"]

        out1 = compile_nl_to_comptext(text=text, audience="dev", mode="bundle_only", return_mode="dsl_plus_confidence")
        out2 = compile_nl_to_comptext(text=text, audience="dev", mode="bundle_only", return_mode="dsl_plus_confidence")
        assert out1 == out2, f"Not deterministic for: {text}"  # determinism

        # Debug output
        print(f"\nTesting: {text[:50]}")
        print(f"Output:\n{out1}")

        # Extract DSL lines
        assert "dsl:\n" in out1, f"No DSL in output for: {text}"
        dsl_block = out1.split("dsl:\n", 1)[1].split("\n\nconfidence:", 1)[0].strip()
        lines = [ln.strip() for ln in dsl_block.splitlines() if ln.strip()]

        print(f"DSL lines: {lines}")

        # Must have profile + at least one bundle
        assert lines[0].startswith("use:profile."), f"First line should be profile for: {text}, got: {lines}"
        assert len(lines) >= 2, f"Should have at least 2 lines for: {text}, got: {lines}"

        # Every use: id must exist
        for ln in lines:
            assert ln.startswith("use:"), f"Line should start with 'use:' for: {text}, got: {ln}"
            use_id = ln.split()[0].replace("use:", "")
            assert (use_id in reg.profiles) or (use_id in reg.bundles), f"Unknown id emitted: {use_id}"

        # Must match expected bundle somewhere
        assert any(ln.startswith(f"use:{expected}") for ln in lines), (text, expected, lines)
