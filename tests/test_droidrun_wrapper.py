"""
Tests for DroidRun Wrapper

Unit tests for the Android ADB automation wrapper.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from comptext_mcp.mobile_agent.droidrun_wrapper import (
    DroidRunWrapper,
    UIElement,
    ScreenState,
    ActionResult,
    ActionType,
)
from comptext_mcp.mobile_agent.config import ADBConfig


class TestUIElement:
    """Tests for UIElement dataclass."""

    def test_default_values(self):
        """Test default values."""
        element = UIElement()

        assert element.text == ""
        assert element.clickable is False
        assert element.bounds == (0, 0, 0, 0)

    def test_center_calculation(self):
        """Test center coordinate calculation."""
        element = UIElement(bounds=(0, 0, 200, 100))
        assert element.center == (100, 50)

        element2 = UIElement(bounds=(100, 200, 300, 400))
        assert element2.center == (200, 300)

    def test_display_name_priority(self):
        """Test display name selection priority."""
        # Text has highest priority
        el1 = UIElement(text="Submit", content_desc="desc", resource_id="id")
        assert el1.display_name == "Submit"

        # Content desc is second
        el2 = UIElement(content_desc="Submit button", resource_id="btn_submit")
        assert el2.display_name == "Submit button"

        # Resource ID is fallback (extracts last part)
        el3 = UIElement(resource_id="com.app:id/btn_submit")
        assert el3.display_name == "btn_submit"

        # Class name is last resort
        el4 = UIElement(class_name="android.widget.Button")
        assert el4.display_name == "Button"

    def test_to_dict(self):
        """Test dictionary conversion."""
        element = UIElement(
            text="Click me",
            bounds=(10, 20, 110, 70),
            clickable=True,
            resource_id="com.app:id/button",
        )

        data = element.to_dict()

        assert data["text"] == "Click me"
        assert data["bounds"] == (10, 20, 110, 70)
        assert data["center"] == (60, 45)
        assert data["clickable"] is True
        assert data["display_name"] == "Click me"


class TestScreenState:
    """Tests for ScreenState dataclass."""

    @pytest.fixture
    def sample_screen(self):
        """Create sample screen state."""
        return ScreenState(
            package="com.android.chrome",
            activity="MainActivity",
            elements=[
                UIElement(text="Search", clickable=True, bounds=(0, 0, 200, 50)),
                UIElement(text="Settings", clickable=True, bounds=(200, 0, 400, 50)),
                UIElement(text="Label", clickable=False),
                UIElement(content_desc="Chrome icon", clickable=True),
                UIElement(resource_id="com.app:id/input", class_name="EditText"),
            ],
        )

    def test_clickable_elements(self, sample_screen):
        """Test filtering clickable elements."""
        clickable = sample_screen.clickable_elements

        assert len(clickable) == 3
        assert all(e.clickable for e in clickable)

    def test_input_fields(self, sample_screen):
        """Test finding input fields."""
        inputs = sample_screen.input_fields

        assert len(inputs) == 1
        assert "EditText" in inputs[0].class_name

    def test_find_by_text_partial(self, sample_screen):
        """Test finding elements by partial text."""
        found = sample_screen.find_by_text("search", partial=True)
        assert len(found) == 1
        assert found[0].text == "Search"

    def test_find_by_text_content_desc(self, sample_screen):
        """Test finding by content description."""
        found = sample_screen.find_by_text("chrome", partial=True)
        assert len(found) == 1
        assert "Chrome" in found[0].content_desc

    def test_find_by_text_exact(self, sample_screen):
        """Test exact text matching."""
        found = sample_screen.find_by_text("Search", partial=False)
        assert len(found) == 1

        not_found = sample_screen.find_by_text("Sear", partial=False)
        assert len(not_found) == 0

    def test_find_by_id(self, sample_screen):
        """Test finding by resource ID."""
        found = sample_screen.find_by_id("input")
        assert found is not None
        assert "input" in found.resource_id

        not_found = sample_screen.find_by_id("nonexistent")
        assert not_found is None

    def test_compact_dict(self, sample_screen):
        """Test compact dictionary format."""
        compact = sample_screen.to_compact_dict()

        assert compact["pkg"] == "chrome"
        assert compact["act"] == "MainActivity"
        assert len(compact["els"]) <= 20


class TestActionResult:
    """Tests for ActionResult dataclass."""

    def test_success_result(self):
        """Test successful action result."""
        result = ActionResult(
            success=True,
            action=ActionType.TAP,
            message="Tapped at (100, 200)",
        )

        assert result.success is True
        assert result.action == ActionType.TAP
        assert result.error is None

    def test_failure_result(self):
        """Test failed action result."""
        result = ActionResult(
            success=False,
            action=ActionType.TYPE,
            error="Input field not focused",
        )

        assert result.success is False
        assert result.error is not None


class TestDroidRunWrapper:
    """Tests for DroidRunWrapper class."""

    @pytest.fixture
    def wrapper(self):
        """Create wrapper instance."""
        config = ADBConfig(screenshot_dir="/tmp/test_screenshots")
        return DroidRunWrapper(config)

    @pytest.fixture
    def connected_wrapper(self, wrapper):
        """Create connected wrapper with mocked ADB."""
        wrapper._device_connected = True
        wrapper.config.device_serial = "emulator-5554"
        return wrapper

    def test_wrapper_creation(self, wrapper):
        """Test wrapper can be created."""
        assert wrapper is not None
        assert wrapper.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_no_devices(self, wrapper):
        """Test connection failure with no devices."""
        with patch.object(wrapper, "_adb_command") as mock_cmd:
            mock_cmd.return_value = "List of devices attached\n"

            connected = await wrapper.connect()

            assert connected is False

    @pytest.mark.asyncio
    async def test_connect_with_device(self, wrapper):
        """Test successful connection."""
        with patch.object(wrapper, "_adb_command") as mock_cmd:
            mock_cmd.return_value = "List of devices attached\nemulator-5554\tdevice\n"

            connected = await wrapper.connect()

            assert connected is True
            assert wrapper.config.device_serial == "emulator-5554"

    @pytest.mark.asyncio
    async def test_tap(self, connected_wrapper):
        """Test tap action."""
        with patch.object(connected_wrapper, "_adb_shell") as mock_shell:
            mock_shell.return_value = ""

            result = await connected_wrapper.tap(100, 200)

            assert result.success is True
            assert result.action == ActionType.TAP
            mock_shell.assert_called_with("input tap 100 200")

    @pytest.mark.asyncio
    async def test_tap_element(self, connected_wrapper):
        """Test tapping on element."""
        element = UIElement(
            text="Submit",
            bounds=(100, 100, 200, 150),
            clickable=True,
        )

        with patch.object(connected_wrapper, "_adb_shell") as mock_shell:
            mock_shell.return_value = ""

            result = await connected_wrapper.tap_element(element)

            assert result.success is True
            assert "Submit" in result.message
            # Center is (150, 125)
            mock_shell.assert_called_with("input tap 150 125")

    @pytest.mark.asyncio
    async def test_swipe(self, connected_wrapper):
        """Test swipe action."""
        with patch.object(connected_wrapper, "_adb_shell") as mock_shell:
            mock_shell.return_value = ""

            result = await connected_wrapper.swipe(100, 500, 100, 100, 300)

            assert result.success is True
            assert result.action == ActionType.SWIPE
            mock_shell.assert_called_with("input swipe 100 500 100 100 300")

    @pytest.mark.asyncio
    async def test_type_text(self, connected_wrapper):
        """Test text input."""
        with patch.object(connected_wrapper, "_adb_shell") as mock_shell:
            mock_shell.return_value = ""

            result = await connected_wrapper.type_text("Hello World")

            assert result.success is True
            assert result.action == ActionType.TYPE

    @pytest.mark.asyncio
    async def test_back(self, connected_wrapper):
        """Test back button."""
        with patch.object(connected_wrapper, "_adb_shell") as mock_shell:
            mock_shell.return_value = ""

            result = await connected_wrapper.back()

            assert result.success is True
            mock_shell.assert_called_with("input keyevent KEYCODE_BACK")

    @pytest.mark.asyncio
    async def test_home(self, connected_wrapper):
        """Test home button."""
        with patch.object(connected_wrapper, "_adb_shell") as mock_shell:
            mock_shell.return_value = ""

            result = await connected_wrapper.home()

            assert result.success is True
            mock_shell.assert_called_with("input keyevent KEYCODE_HOME")

    @pytest.mark.asyncio
    async def test_launch_app(self, connected_wrapper):
        """Test app launching."""
        with patch.object(connected_wrapper, "_adb_shell") as mock_shell:
            mock_shell.return_value = ""

            result = await connected_wrapper.launch_app("com.android.chrome")

            assert result.success is True
            assert result.action == ActionType.LAUNCH_APP

    @pytest.mark.asyncio
    async def test_wait(self, connected_wrapper):
        """Test wait action."""
        result = await connected_wrapper.wait(0.1)

        assert result.success is True
        assert result.action == ActionType.WAIT

    @pytest.mark.asyncio
    async def test_get_device_info(self, connected_wrapper):
        """Test getting device info."""
        with patch.object(connected_wrapper, "_adb_shell") as mock_shell:
            mock_shell.side_effect = [
                "Pixel 5",  # model
                "Google",  # manufacturer
                "12",  # version
                "31",  # sdk
                "redfin",  # device
            ]

            info = await connected_wrapper.get_device_info()

            assert info["model"] == "Pixel 5"
            assert info["manufacturer"] == "Google"
            assert info["version"] == "12"

    def test_parse_ui_xml(self, wrapper):
        """Test UI XML parsing."""
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <hierarchy>
            <node text="Button" clickable="true" bounds="[0,0][100,50]"
                  class="android.widget.Button" resource-id="com.app:id/btn"/>
            <node text="" content-desc="Icon" bounds="[100,0][150,50]"
                  clickable="true" class="android.widget.ImageView"/>
        </hierarchy>'''

        elements = wrapper._parse_ui_xml(xml)

        assert len(elements) == 2
        assert elements[0].text == "Button"
        assert elements[0].clickable is True
        assert elements[1].content_desc == "Icon"


class TestActionType:
    """Tests for ActionType enum."""

    def test_action_types(self):
        """Test all action types exist."""
        assert ActionType.TAP.value == "tap"
        assert ActionType.SWIPE.value == "swipe"
        assert ActionType.TYPE.value == "type"
        assert ActionType.BACK.value == "back"
        assert ActionType.HOME.value == "home"
        assert ActionType.LAUNCH_APP.value == "launch_app"
        assert ActionType.WAIT.value == "wait"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
