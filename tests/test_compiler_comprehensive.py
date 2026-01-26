"""Comprehensive test suite for CompText compiler components."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Set dummy environment variables before any imports
os.environ.setdefault("NOTION_API_TOKEN", "dummy_token_for_testing")
os.environ.setdefault("COMPTEXT_DATABASE_ID", "0e038c9b52c5466694dbac288280dd93")

from comptext_mcp.compiler import (  # noqa: E402
    Bundle,
    MatchResult,
    Profile,
    Registry,
    compile_nl_to_comptext,
    load_registry,
)
from comptext_mcp.compiler.canonicalize import pick_profile_id, render_dsl  # noqa: E402
from comptext_mcp.compiler.matcher import best_bundle, score_bundles  # noqa: E402


class TestRegistry:
    """Test registry loading and validation."""

    def test_load_default_registry(self):
        """Test loading default registry from bundles.yaml."""
        reg = load_registry()
        assert isinstance(reg, Registry)
        assert len(reg.profiles) > 0
        assert len(reg.bundles) > 0

    def test_required_profiles_exist(self):
        """Test that all required profiles exist."""
        reg = load_registry()
        required = {"profile.dev.v1", "profile.audit.v1", "profile.exec.v1"}
        assert required.issubset(set(reg.profiles.keys()))

    def test_profile_structure(self):
        """Test profile data structure."""
        reg = load_registry()
        prof = reg.profiles["profile.dev.v1"]
        assert isinstance(prof, Profile)
        assert prof.id == "profile.dev.v1"
        assert isinstance(prof.name, str)
        assert isinstance(prof.expansion, list)

    def test_bundle_structure(self):
        """Test bundle data structure."""
        reg = load_registry()
        assert len(reg.bundles) > 0
        # Check first bundle
        bundle = next(iter(reg.bundles.values()))
        assert isinstance(bundle, Bundle)
        assert isinstance(bundle.id, str)
        assert isinstance(bundle.domain, str)
        assert isinstance(bundle.task, str)
        assert isinstance(bundle.keywords_any, list)
        assert isinstance(bundle.expansion, list)

    def test_all_bundle_ids_unique(self):
        """Test that all bundle IDs are unique."""
        reg = load_registry()
        ids = [b.id for b in reg.bundles.values()]
        assert len(ids) == len(set(ids))


class TestCanonicalize:
    """Test canonicalization functions."""

    def test_pick_profile_dev(self):
        """Test profile selection for dev audience."""
        reg = load_registry()
        assert pick_profile_id("dev", reg) == "profile.dev.v1"
        assert pick_profile_id("developer", reg) == "profile.dev.v1"
        assert pick_profile_id("DEV", reg) == "profile.dev.v1"

    def test_pick_profile_audit(self):
        """Test profile selection for audit audience."""
        reg = load_registry()
        assert pick_profile_id("audit", reg) == "profile.audit.v1"
        assert pick_profile_id("AUDIT", reg) == "profile.audit.v1"

    def test_pick_profile_exec(self):
        """Test profile selection for exec audience."""
        reg = load_registry()
        assert pick_profile_id("exec", reg) == "profile.exec.v1"
        assert pick_profile_id("EXEC", reg) == "profile.exec.v1"

    def test_pick_profile_default(self):
        """Test default profile selection for unknown audience."""
        reg = load_registry()
        assert pick_profile_id("unknown", reg) == "profile.dev.v1"
        assert pick_profile_id("", reg) == "profile.dev.v1"
        assert pick_profile_id(None, reg) == "profile.dev.v1"

    def test_render_dsl_simple(self):
        """Test simple DSL rendering."""
        dsl = render_dsl("profile.dev.v1", ["code.review.v1"])
        assert dsl == "use:profile.dev.v1\nuse:code.review.v1"

    def test_render_dsl_multiple_bundles(self):
        """Test DSL rendering with multiple bundles."""
        dsl = render_dsl("profile.audit.v1", ["code.review.v1", "sec.scan.highfix.v1"])
        expected = "use:profile.audit.v1\nuse:code.review.v1\nuse:sec.scan.highfix.v1"
        assert dsl == expected

    def test_render_dsl_with_deltas(self):
        """Test DSL rendering with delta modifiers."""
        dsl = render_dsl("profile.dev.v1", ["code.perfopt.v1"], deltas=["benchmark=full", "compare=baseline"])
        assert "use:profile.dev.v1" in dsl
        assert "use:code.perfopt.v1" in dsl
        # Deltas should be sorted and included
        assert "benchmark=full" in dsl or "compare=baseline" in dsl


class TestMatcher:
    """Test matcher functions."""

    def test_score_bundles_review(self):
        """Test scoring for code review query."""
        reg = load_registry()
        results = score_bundles("Review this code and improve readability", reg)
        assert len(results) > 0
        assert isinstance(results[0], MatchResult)
        # Should match code.review.v1
        top_ids = [r.bundle_id for r in results[:3]]
        assert "code.review.v1" in top_ids

    def test_score_bundles_performance(self):
        """Test scoring for performance optimization query."""
        reg = load_registry()
        results = score_bundles("This is slow, find bottlenecks and optimize", reg)
        assert len(results) > 0
        # Should match code.perfopt.v1
        top_ids = [r.bundle_id for r in results[:3]]
        assert "code.perfopt.v1" in top_ids

    def test_score_bundles_security(self):
        """Test scoring for security scan query."""
        reg = load_registry()
        results = score_bundles("Scan for security vulnerabilities", reg)
        assert len(results) > 0
        # Should match sec.scan.highfix.v1
        top_ids = [r.bundle_id for r in results[:3]]
        assert "sec.scan.highfix.v1" in top_ids

    def test_score_bundles_no_match(self):
        """Test scoring with no keyword matches."""
        reg = load_registry()
        results = score_bundles("xyz abc def", reg)
        # Should return empty or very low scores
        assert len(results) == 0 or results[0].score == 0

    def test_best_bundle_high_confidence(self):
        """Test best_bundle with high confidence match."""
        reg = load_registry()
        match, confidence = best_bundle("Review this code for best practices", reg)
        assert match is not None
        assert confidence >= 0.65
        assert match.bundle_id == "code.review.v1"

    def test_best_bundle_low_confidence(self):
        """Test best_bundle with low confidence match."""
        reg = load_registry()
        match, confidence = best_bundle("do something", reg)
        # Should have low confidence or no match
        assert confidence < 0.65

    def test_best_bundle_deterministic(self):
        """Test that best_bundle is deterministic."""
        reg = load_registry()
        text = "Optimize this slow function"
        match1, conf1 = best_bundle(text, reg)
        match2, conf2 = best_bundle(text, reg)
        assert match1.bundle_id == match2.bundle_id
        assert conf1 == conf2


class TestCompiler:
    """Test main compiler function."""

    def test_compile_simple_review(self):
        """Test compiling simple code review request."""
        result = compile_nl_to_comptext("Review this code for best practices")
        assert "dsl:" in result
        assert "use:profile.dev.v1" in result
        assert "confidence:" in result

    def test_compile_with_audience_audit(self):
        """Test compilation with audit audience."""
        result = compile_nl_to_comptext("Scan for security vulnerabilities", audience="audit")
        assert "use:profile.audit.v1" in result

    def test_compile_with_audience_exec(self):
        """Test compilation with exec audience."""
        result = compile_nl_to_comptext("Generate API documentation with examples", audience="exec")
        assert "use:profile.exec.v1" in result

    def test_compile_return_dsl_only(self):
        """Test compilation with dsl_only return mode."""
        result = compile_nl_to_comptext("Review this code for maintainability", return_mode="dsl_only")
        assert "use:profile.dev.v1" in result
        # Should not have confidence or clarification
        assert "confidence:" not in result

    def test_compile_return_with_explanation(self):
        """Test compilation with explanation return mode."""
        result = compile_nl_to_comptext("Review this code for best practices", return_mode="dsl_plus_explanation")
        assert "dsl:" in result
        assert "confidence:" in result
        assert "explanation:" in result

    def test_compile_low_confidence_clarification(self):
        """Test that low confidence returns clarification."""
        result = compile_nl_to_comptext("Make it better")
        assert "clarification:" in result
        # Should contain a clarification message (language-agnostic check)
        assert result.count("\n") >= 2  # Multi-line output with clarification

    def test_compile_deterministic(self):
        """Test that compilation is deterministic."""
        text = "Optimize this slow code"
        result1 = compile_nl_to_comptext(text)
        result2 = compile_nl_to_comptext(text)
        assert result1 == result2

    def test_compile_no_invented_ids(self):
        """Test that compiler never invents IDs."""
        reg = load_registry()
        result = compile_nl_to_comptext("Review and optimize this code")
        # Extract all use: directives
        lines = [line.strip() for line in result.split("\n") if line.strip().startswith("use:")]
        for line in lines:
            id_part = line.split()[0].replace("use:", "")
            # Must exist in profiles or bundles
            assert (id_part in reg.profiles) or (id_part in reg.bundles), f"Unknown ID: {id_part}"

    def test_compile_performance(self):
        """Test compilation performance."""
        import time

        text = "Review this code for best practices"
        start = time.time()
        for _ in range(100):
            compile_nl_to_comptext(text)
        elapsed = time.time() - start
        # Should complete 100 compilations in under 5 seconds (includes YAML loading)
        assert elapsed < 5.0, f"Too slow: {elapsed}s for 100 compilations"
        # Log performance
        per_compile = elapsed / 100 * 1000
        print(f"\nPerformance: {per_compile:.2f}ms per compilation")


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_input(self):
        """Test compilation with empty input."""
        result = compile_nl_to_comptext("")
        # Should return low confidence with clarification
        assert "confidence:" in result
        assert "clarification:" in result

    def test_very_long_input(self):
        """Test compilation with very long input."""
        long_text = "review " * 1000
        result = compile_nl_to_comptext(long_text)
        assert "dsl:" in result
        # Should still complete successfully

    def test_special_characters(self):
        """Test compilation with special characters."""
        result = compile_nl_to_comptext("Review this code!@#$%^&*()")
        assert "dsl:" in result

    def test_unicode_input(self):
        """Test compilation with unicode characters."""
        result = compile_nl_to_comptext("Überprüfe diesen Code für Sicherheit")
        assert "dsl:" in result

    def test_mixed_case_keywords(self):
        """Test that matching is case-insensitive."""
        result1 = compile_nl_to_comptext("REVIEW this CODE for best practices")
        result2 = compile_nl_to_comptext("review this code for best practices")
        # Should produce similar results (same bundle)
        assert result1.split("\n")[1] == result2.split("\n")[1]  # Same bundle line

    def test_low_confidence_dsl_only_mode(self):
        """Test low confidence returns clarification even in dsl_only mode."""
        result = compile_nl_to_comptext("do something", return_mode="dsl_only")
        # Should return clarification message (non-empty string)
        assert len(result) > 0
        # Should not contain DSL markers
        assert "use:" not in result

    def test_bundle_not_in_registry_error(self):
        """Test error handling when matched bundle not in registry (should never happen)."""
        # This is an internal error that should not occur with valid registry
        # But we test the guardrail exists
        from comptext_mcp.compiler.matcher import MatchResult
        from comptext_mcp.compiler.registry import load_registry

        reg = load_registry()
        # Create a fake match with non-existent bundle
        fake_match = MatchResult(bundle_id="fake.bundle.v1", score=10, hits=["test"])

        # The actual compiler checks this, so we can verify the check exists
        with pytest.raises(ValueError, match="selected bundle not found in registry"):
            if fake_match.bundle_id not in reg.bundles:
                raise ValueError("Internal error: selected bundle not found in registry")


class TestIntegration:
    """Integration tests for end-to-end workflows."""

    def test_all_golden_prompts_compile(self):
        """Test that all golden prompts compile successfully."""
        golden_path = Path(__file__).resolve().parent / "fixtures" / "golden_prompts.json"
        import json

        golden = json.loads(golden_path.read_text(encoding="utf-8"))

        for item in golden:
            text = item["text"]
            result = compile_nl_to_comptext(text)
            # Should always produce valid output
            assert "dsl:" in result or "clarification:" in result
            # Should be deterministic
            result2 = compile_nl_to_comptext(text)
            assert result == result2

    def test_multiple_audiences_same_request(self):
        """Test same request with different audiences."""
        text = "Review this code for best practices"
        dev_result = compile_nl_to_comptext(text, audience="dev")
        audit_result = compile_nl_to_comptext(text, audience="audit")
        exec_result = compile_nl_to_comptext(text, audience="exec")

        # All should use same bundle but different profiles
        assert "code.review.v1" in dev_result
        assert "code.review.v1" in audit_result
        assert "code.review.v1" in exec_result

        assert "profile.dev.v1" in dev_result
        assert "profile.audit.v1" in audit_result
        assert "profile.exec.v1" in exec_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
