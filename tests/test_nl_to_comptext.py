from __future__ import annotations

import json
from pathlib import Path

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
        assert out1 == out2  # determinism

        # Extract DSL lines
        assert "dsl:\n" in out1
        dsl_block = out1.split("dsl:\n", 1)[1].split("\n\nconfidence:", 1)[0].strip()
        lines = [ln.strip() for ln in dsl_block.splitlines() if ln.strip()]

        # Must have profile + at least one bundle
        assert lines[0].startswith("use:profile.")
        assert len(lines) >= 2

        # Every use: id must exist
        for ln in lines:
            assert ln.startswith("use:")
            use_id = ln.split()[0].replace("use:", "")
            assert (use_id in reg.profiles) or (use_id in reg.bundles), f"Unknown id emitted: {use_id}"

        # Must match expected bundle somewhere
        assert any(ln.startswith(f"use:{expected}") for ln in lines), (text, expected, lines)
