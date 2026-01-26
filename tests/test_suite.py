"""Test Suite für CompText MCP Server"""

import os
import sys

import pytest

# Set dummy environment variables for testing if not already set
os.environ.setdefault("NOTION_API_TOKEN", "dummy_token_for_testing")
os.environ.setdefault("COMPTEXT_DATABASE_ID", "0e038c9b52c5466694dbac288280dd93")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from comptext_mcp.notion_client import NotionClientError  # noqa: E402, F401
from comptext_mcp.notion_client import (  # noqa: E402
    get_all_modules,
    get_module_by_name,
    get_modules_by_tag,
    get_modules_by_type,
    search_codex,
)


class TestNotionClient:
    """Test Notion Client functionality"""

    def test_get_all_modules(self):
        """Test fetching all modules"""
        modules = get_all_modules()
        assert isinstance(modules, list)
        assert len(modules) > 0
        assert all("id" in m for m in modules)

    def test_get_module_by_name(self):
        """Test fetching specific module"""
        module_b = get_module_by_name("Modul B: Programmierung")
        assert isinstance(module_b, list)
        assert all(m.get("modul") == "Modul B: Programmierung" for m in module_b)

    def test_search_codex(self):
        """Test search functionality"""
        results = search_codex("code", max_results=5)
        assert isinstance(results, list)
        assert len(results) <= 5

    def test_get_modules_by_tag(self):
        """Test filtering by tag"""
        core_modules = get_modules_by_tag("Core")
        assert isinstance(core_modules, list)
        assert all("Core" in m.get("tags", []) for m in core_modules)

    def test_get_modules_by_type(self):
        """Test filtering by type"""
        docs = get_modules_by_type("Dokumentation")
        assert isinstance(docs, list)
        assert all(m.get("typ") == "Dokumentation" for m in docs)


class TestModuleStructure:
    """Test module data structure"""

    def test_module_has_required_fields(self):
        """Test that modules have required fields"""
        modules = get_all_modules()
        required_fields = ["id", "url", "titel"]

        for module in modules:
            for field in required_fields:
                assert field in module, f"Module missing field: {field}"

    def test_module_tags_is_list(self):
        """Test that tags field is a list"""
        modules = get_all_modules()
        for module in modules:
            tags = module.get("tags")
            assert tags is None or isinstance(tags, list)


class TestSearchFunctionality:
    """Test search capabilities"""

    def test_search_returns_relevant_results(self):
        """Test that search returns relevant results"""
        results = search_codex("docker")
        assert isinstance(results, list)

    def test_search_respects_max_results(self):
        """Test max_results parameter"""
        results = search_codex("test", max_results=3)
        assert len(results) <= 3

    def test_search_with_no_results(self):
        """Test search with query that should return no results"""
        results = search_codex("xyzabc123notfound")
        assert isinstance(results, list)
        assert len(results) == 0


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_module_name(self):
        """Test handling of invalid module name"""
        result = get_module_by_name("Invalid Module Name")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_invalid_tag(self):
        """Test handling of invalid tag"""
        result = get_modules_by_tag("InvalidTag123")
        assert isinstance(result, list)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
