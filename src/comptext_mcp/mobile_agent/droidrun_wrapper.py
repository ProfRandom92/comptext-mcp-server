"""
DroidRun Wrapper

Wrapper for DroidRun framework providing Android automation capabilities.
Includes ADB integration, UI tree parsing, and action execution.
"""

import asyncio
import base64
import json
import logging
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .config import ADBConfig

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Available Android actions."""
    TAP = "tap"
    SWIPE = "swipe"
    TYPE = "type"
    KEY = "key"
    BACK = "back"
    HOME = "home"
    RECENT = "recent"
    SCREENSHOT = "screenshot"
    LAUNCH_APP = "launch_app"
    WAIT = "wait"


@dataclass
class UIElement:
    """Represents a UI element from the accessibility tree."""
    resource_id: str = ""
    class_name: str = ""
    text: str = ""
    content_desc: str = ""
    bounds: tuple[int, int, int, int] = (0, 0, 0, 0)  # left, top, right, bottom
    clickable: bool = False
    scrollable: bool = False
    focusable: bool = False
    enabled: bool = True
    selected: bool = False
    checkable: bool = False
    checked: bool = False
    index: int = 0
    package: str = ""

    @property
    def center(self) -> tuple[int, int]:
        """Get center coordinates of the element."""
        left, top, right, bottom = self.bounds
        return ((left + right) // 2, (top + bottom) // 2)

    @property
    def display_name(self) -> str:
        """Get a human-readable name for the element."""
        if self.text:
            return self.text
        if self.content_desc:
            return self.content_desc
        if self.resource_id:
            return self.resource_id.split("/")[-1]
        return self.class_name.split(".")[-1]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "resource_id": self.resource_id,
            "class_name": self.class_name,
            "text": self.text,
            "content_desc": self.content_desc,
            "bounds": self.bounds,
            "center": self.center,
            "clickable": self.clickable,
            "scrollable": self.scrollable,
            "enabled": self.enabled,
            "display_name": self.display_name,
        }


@dataclass
class ScreenState:
    """Current screen state including UI tree and screenshot."""
    package: str = ""
    activity: str = ""
    elements: list[UIElement] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    screenshot_base64: Optional[str] = None
    raw_xml: Optional[str] = None
    timestamp: float = 0.0

    @property
    def clickable_elements(self) -> list[UIElement]:
        """Get all clickable elements."""
        return [e for e in self.elements if e.clickable]

    @property
    def input_fields(self) -> list[UIElement]:
        """Get all input fields."""
        return [
            e for e in self.elements
            if "EditText" in e.class_name or "TextField" in e.class_name
        ]

    def find_by_text(self, text: str, partial: bool = True) -> list[UIElement]:
        """Find elements by text content."""
        text_lower = text.lower()
        if partial:
            return [
                e for e in self.elements
                if text_lower in e.text.lower() or text_lower in e.content_desc.lower()
            ]
        return [
            e for e in self.elements
            if e.text.lower() == text_lower or e.content_desc.lower() == text_lower
        ]

    def find_by_id(self, resource_id: str) -> Optional[UIElement]:
        """Find element by resource ID."""
        for e in self.elements:
            if resource_id in e.resource_id:
                return e
        return None

    def to_compact_dict(self) -> dict[str, Any]:
        """Convert to compact dictionary for LLM context (CompText optimized)."""
        return {
            "pkg": self.package.split(".")[-1] if self.package else "",
            "act": self.activity.split(".")[-1] if self.activity else "",
            "els": [
                {
                    "i": i,
                    "n": e.display_name[:30],
                    "c": e.center,
                    "t": "btn" if e.clickable else "txt" if e.text else "el",
                }
                for i, e in enumerate(self.elements[:20])  # Limit to 20 elements
            ],
        }


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    action: ActionType
    message: str = ""
    error: Optional[str] = None
    screen_state: Optional[ScreenState] = None


class DroidRunWrapper:
    """
    Wrapper for Android automation via ADB.

    Provides:
    - Device connection and management
    - UI tree parsing (accessibility API)
    - Screenshot capture
    - Action execution (tap, swipe, type, etc.)
    - App launching and control
    """

    def __init__(self, config: Optional[ADBConfig] = None):
        self.config = config or ADBConfig()
        self._device_connected = False
        self._screen_cache: Optional[ScreenState] = None

        # Ensure screenshot directory exists
        Path(self.config.screenshot_dir).mkdir(parents=True, exist_ok=True)

    async def connect(self) -> bool:
        """
        Connect to Android device.

        Returns:
            True if device connected successfully
        """
        try:
            result = await self._adb_command("devices")
            lines = result.strip().split("\n")[1:]  # Skip header
            devices = [line.split("\t")[0] for line in lines if "\tdevice" in line]

            if not devices:
                logger.error("No Android devices found")
                return False

            if self.config.device_serial:
                if self.config.device_serial not in devices:
                    logger.error(f"Device {self.config.device_serial} not found")
                    return False
            else:
                # Use first available device
                self.config.device_serial = devices[0]
                logger.info(f"Using device: {self.config.device_serial}")

            self._device_connected = True
            return True

        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False

    async def get_screen_state(self, include_screenshot: bool = True) -> ScreenState:
        """
        Get current screen state including UI tree and optional screenshot.

        Args:
            include_screenshot: Whether to capture screenshot

        Returns:
            ScreenState with UI elements and metadata
        """
        import time
        state = ScreenState(timestamp=time.time())

        # Get current activity
        try:
            activity_output = await self._adb_shell(
                "dumpsys activity activities | grep mResumedActivity"
            )
            if activity_output:
                # Parse: mResumedActivity: ActivityRecord{... com.package/.Activity ...}
                parts = activity_output.split()
                for part in parts:
                    if "/" in part:
                        pkg_activity = part.strip("{}")
                        if "/" in pkg_activity:
                            state.package, activity = pkg_activity.split("/", 1)
                            state.activity = activity.lstrip(".")
                            break
        except Exception as e:
            logger.warning(f"Failed to get current activity: {e}")

        # Get UI hierarchy
        try:
            # Dump UI hierarchy to device
            await self._adb_shell("uiautomator dump /sdcard/ui_dump.xml")
            # Pull the file
            xml_content = await self._adb_shell("cat /sdcard/ui_dump.xml")
            state.raw_xml = xml_content
            state.elements = self._parse_ui_xml(xml_content)
        except Exception as e:
            logger.warning(f"Failed to get UI hierarchy: {e}")

        # Capture screenshot
        if include_screenshot:
            try:
                screenshot_path = await self.screenshot()
                state.screenshot_path = screenshot_path

                # Optionally encode as base64 for LLM
                with open(screenshot_path, "rb") as f:
                    state.screenshot_base64 = base64.b64encode(f.read()).decode()
            except Exception as e:
                logger.warning(f"Failed to capture screenshot: {e}")

        self._screen_cache = state
        return state

    def _parse_ui_xml(self, xml_content: str) -> list[UIElement]:
        """Parse UI hierarchy XML into UIElement list."""
        elements = []

        try:
            root = ET.fromstring(xml_content)

            for node in root.iter("node"):
                bounds_str = node.get("bounds", "[0,0][0,0]")
                # Parse bounds: [left,top][right,bottom]
                bounds_parts = bounds_str.replace("][", ",").strip("[]").split(",")
                try:
                    bounds = tuple(int(x) for x in bounds_parts)
                except ValueError:
                    bounds = (0, 0, 0, 0)

                element = UIElement(
                    resource_id=node.get("resource-id", ""),
                    class_name=node.get("class", ""),
                    text=node.get("text", ""),
                    content_desc=node.get("content-desc", ""),
                    bounds=bounds,
                    clickable=node.get("clickable", "false") == "true",
                    scrollable=node.get("scrollable", "false") == "true",
                    focusable=node.get("focusable", "false") == "true",
                    enabled=node.get("enabled", "true") == "true",
                    selected=node.get("selected", "false") == "true",
                    checkable=node.get("checkable", "false") == "true",
                    checked=node.get("checked", "false") == "true",
                    index=int(node.get("index", "0")),
                    package=node.get("package", ""),
                )

                # Only include meaningful elements
                if element.text or element.content_desc or element.clickable:
                    elements.append(element)

        except ET.ParseError as e:
            logger.error(f"Failed to parse UI XML: {e}")

        return elements

    async def tap(self, x: int, y: int) -> ActionResult:
        """
        Tap at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            ActionResult indicating success/failure
        """
        try:
            await self._adb_shell(f"input tap {x} {y}")
            await asyncio.sleep(self.config.timeout / 1000 * 0.1)  # Brief delay
            return ActionResult(
                success=True,
                action=ActionType.TAP,
                message=f"Tapped at ({x}, {y})",
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=ActionType.TAP,
                error=str(e),
            )

    async def tap_element(self, element: UIElement) -> ActionResult:
        """
        Tap on a UI element.

        Args:
            element: UIElement to tap

        Returns:
            ActionResult indicating success/failure
        """
        x, y = element.center
        result = await self.tap(x, y)
        result.message = f"Tapped on '{element.display_name}' at ({x}, {y})"
        return result

    async def swipe(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration_ms: int = 300,
    ) -> ActionResult:
        """
        Swipe from one point to another.

        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration_ms: Swipe duration in milliseconds

        Returns:
            ActionResult indicating success/failure
        """
        try:
            await self._adb_shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")
            return ActionResult(
                success=True,
                action=ActionType.SWIPE,
                message=f"Swiped from ({x1}, {y1}) to ({x2}, {y2})",
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=ActionType.SWIPE,
                error=str(e),
            )

    async def type_text(self, text: str) -> ActionResult:
        """
        Type text into focused input field.

        Args:
            text: Text to type

        Returns:
            ActionResult indicating success/failure
        """
        try:
            # Escape special characters for shell
            escaped = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
            await self._adb_shell(f"input text '{escaped}'")
            return ActionResult(
                success=True,
                action=ActionType.TYPE,
                message=f"Typed: {text[:20]}{'...' if len(text) > 20 else ''}",
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=ActionType.TYPE,
                error=str(e),
            )

    async def press_key(self, keycode: str) -> ActionResult:
        """
        Press a key.

        Args:
            keycode: Android keycode (e.g., "KEYCODE_BACK", "KEYCODE_HOME")

        Returns:
            ActionResult indicating success/failure
        """
        try:
            await self._adb_shell(f"input keyevent {keycode}")
            return ActionResult(
                success=True,
                action=ActionType.KEY,
                message=f"Pressed key: {keycode}",
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=ActionType.KEY,
                error=str(e),
            )

    async def back(self) -> ActionResult:
        """Press back button."""
        return await self.press_key("KEYCODE_BACK")

    async def home(self) -> ActionResult:
        """Press home button."""
        return await self.press_key("KEYCODE_HOME")

    async def recent_apps(self) -> ActionResult:
        """Open recent apps."""
        return await self.press_key("KEYCODE_APP_SWITCH")

    async def screenshot(self, filename: Optional[str] = None) -> str:
        """
        Capture screenshot.

        Args:
            filename: Optional filename (defaults to timestamp)

        Returns:
            Path to saved screenshot
        """
        import time

        if not filename:
            filename = f"screenshot_{int(time.time() * 1000)}.png"

        local_path = os.path.join(self.config.screenshot_dir, filename)
        device_path = f"/sdcard/{filename}"

        try:
            await self._adb_shell(f"screencap -p {device_path}")
            await self._adb_command(f"pull {device_path} {local_path}")
            await self._adb_shell(f"rm {device_path}")
            return local_path
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise

    async def launch_app(self, package: str, activity: Optional[str] = None) -> ActionResult:
        """
        Launch an app.

        Args:
            package: Package name (e.g., "com.android.chrome")
            activity: Optional activity name

        Returns:
            ActionResult indicating success/failure
        """
        try:
            if activity:
                cmd = f"am start -n {package}/{activity}"
            else:
                cmd = f"monkey -p {package} -c android.intent.category.LAUNCHER 1"

            await self._adb_shell(cmd)
            await asyncio.sleep(1)  # Wait for app to launch

            return ActionResult(
                success=True,
                action=ActionType.LAUNCH_APP,
                message=f"Launched app: {package}",
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action=ActionType.LAUNCH_APP,
                error=str(e),
            )

    async def wait(self, seconds: float) -> ActionResult:
        """
        Wait for specified duration.

        Args:
            seconds: Duration to wait

        Returns:
            ActionResult
        """
        await asyncio.sleep(seconds)
        return ActionResult(
            success=True,
            action=ActionType.WAIT,
            message=f"Waited {seconds}s",
        )

    async def _adb_command(self, command: str) -> str:
        """Execute ADB command."""
        full_cmd = [self.config.adb_path]
        if self.config.device_serial:
            full_cmd.extend(["-s", self.config.device_serial])
        full_cmd.extend(command.split())

        proc = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=self.config.timeout,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"ADB command failed: {stderr.decode()}")

        return stdout.decode()

    async def _adb_shell(self, command: str) -> str:
        """Execute ADB shell command."""
        return await self._adb_command(f"shell {command}")

    @property
    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self._device_connected

    @property
    def cached_screen(self) -> Optional[ScreenState]:
        """Get cached screen state."""
        return self._screen_cache
