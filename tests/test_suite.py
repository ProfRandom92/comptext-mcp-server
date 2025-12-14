"""Test Suite für CompText MCP Server"""

import pytest
import os
from unittest.mock import patch

from comptext_mcp.notion_client import (
    get_all_modules,
    get_module_by_name,
    search_codex,
    get_modules_by_tag,
    get_modules_by_type,
    parse_page,
    _extract_text_from_rich_text,
    _get_property_value,
)
from comptext_mcp.utils import validate_page_id, validate_query_string, sanitize_text_output, truncate_text
from comptext_mcp.constants import MODULE_MAP


class TestUtils:
    """Test utility functions"""

    def test_validate_page_id_valid(self):
        """Test page ID validation with valid IDs"""
        # Test with dashes
        result = validate_page_id("0e038c9b-52c5-4666-94db-ac288280dd93")
        assert result == "0e038c9b52c5466694dbac288280dd93"

        # Test without dashes
        result = validate_page_id("0e038c9b52c5466694dbac288280dd93")
        assert result == "0e038c9b52c5466694dbac288280dd93"

    def test_validate_page_id_invalid(self):
        """Test page ID validation with invalid IDs"""
        with pytest.raises(ValueError):
            validate_page_id("invalid")

        with pytest.raises(ValueError):
            validate_page_id("0e038c9b-52c5-4666")  # Too short

    def test_validate_query_string_valid(self):
        """Test query string validation"""
        result = validate_query_string("  docker  ")
        assert result == "docker"

        result = validate_query_string("test query")
        assert result == "test query"

    def test_validate_query_string_invalid(self):
        """Test query string validation with invalid inputs"""
        with pytest.raises(ValueError):
            validate_query_string("")

        with pytest.raises(ValueError):
            validate_query_string("   ")

        with pytest.raises(ValueError):
            validate_query_string("x" * 201)  # Too long

    def test_sanitize_text_output(self):
        """Test text sanitization"""
        result = sanitize_text_output("Hello\x00World")
        assert "\x00" not in result

        result = sanitize_text_output("Normal text\nwith newlines")
        assert "\n" in result

    def test_truncate_text(self):
        """Test text truncation"""
        long_text = "a" * 100
        result = truncate_text(long_text, max_length=50)
        assert len(result) == 50
        assert result.endswith("...")


class TestConstants:
    """Test constants module"""

    def test_module_map_exists(self):
        """Test that MODULE_MAP has all modules A-M"""
        assert len(MODULE_MAP) == 13
        for letter in "ABCDEFGHIJKLM":
            assert letter in MODULE_MAP
            assert MODULE_MAP[letter].startswith(f"Modul {letter}:")


class TestNotionClientHelpers:
    """Test Notion client helper functions"""

    def test_extract_text_from_rich_text(self):
        """Test rich text extraction"""
        rich_text = [{"plain_text": "Hello "}, {"plain_text": "World"}]
        result = _extract_text_from_rich_text(rich_text)
        assert result == "Hello World"

        # Test empty
        result = _extract_text_from_rich_text([])
        assert result == ""

    def test_get_property_value(self):
        """Test property value extraction"""
        page = {"properties": {"Title": {"title": [{"plain_text": "Test Title"}]}, "Status": {"select": {"name": "Active"}}}}

        title = _get_property_value(page, "Title", "title")
        assert title == "Test Title"

        status = _get_property_value(page, "Status", "select")
        assert status == "Active"


@pytest.fixture
def mock_notion_response():
    """Mock Notion API response"""
    return {
        "results": [
            {
                "id": "test-id-1",
                "url": "https://notion.so/test-1",
                "properties": {
                    "Titel": {"title": [{"plain_text": "Test Entry 1"}]},
                    "Beschreibung": {"rich_text": [{"plain_text": "Test description"}]},
                    "Modul": {"select": {"name": "Modul B: Programmierung"}},
                    "Typ": {"select": {"name": "Dokumentation"}},
                    "Tags": {"multi_select": [{"name": "Core"}]},
                },
                "created_time": "2024-01-01T00:00:00.000Z",
                "last_edited_time": "2024-01-01T00:00:00.000Z",
            }
        ]
    }


class TestNotionClientWithMock:
    """Test Notion client functions with mocked API"""

    @patch("comptext_mcp.notion_client.notion")
    def test_get_all_modules_mock(self, mock_notion, mock_notion_response):
        """Test fetching all modules with mock"""
        mock_notion.databases.query.return_value = mock_notion_response

        # Clear cache first
        get_all_modules.cache_clear()

        results = get_all_modules()
        assert len(results) == 1
        assert results[0]["titel"] == "Test Entry 1"
        assert results[0]["modul"] == "Modul B: Programmierung"

    @patch("comptext_mcp.notion_client.notion")
    def test_search_codex_mock(self, mock_notion, mock_notion_response):
        """Test search with mock"""
        mock_notion.databases.query.return_value = mock_notion_response

        # Clear cache
        get_all_modules.cache_clear()

        results = search_codex("test", max_results=5)
        assert isinstance(results, list)


# Only run integration tests if Notion token is available
@pytest.mark.skipif(not os.getenv("NOTION_API_TOKEN"), reason="NOTION_API_TOKEN not set - skipping integration tests")
class TestNotionClientIntegration:
    """Integration tests with real Notion API (requires credentials)"""

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

    def test_parse_page_structure(self):
        """Test that parse_page returns correct structure"""
        mock_page = {
            "id": "test-id",
            "url": "https://notion.so/test",
            "properties": {
                "Titel": {"title": [{"plain_text": "Test"}]},
                "Beschreibung": {"rich_text": []},
                "Modul": {"select": None},
                "Typ": {"select": None},
                "Tags": {"multi_select": []},
            },
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
        }

        result = parse_page(mock_page)

        required_fields = ["id", "url", "titel", "beschreibung", "modul", "typ", "tags", "created_time", "last_edited_time"]
        for field in required_fields:
            assert field in result


if __name__ == "__main__":
    pytest.main(["-v", __file__])
