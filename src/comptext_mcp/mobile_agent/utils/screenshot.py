"""
Screenshot Pipeline

Capture and process Android device screenshots for agent context.
Supports both raw screenshot capture and annotated visualizations.
"""

import asyncio
import base64
import io
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ScreenshotResult:
    """Result of a screenshot capture."""

    success: bool
    path: Optional[str] = None
    base64_data: Optional[str] = None
    width: int = 0
    height: int = 0
    timestamp: float = 0.0
    error: Optional[str] = None

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)


class ScreenshotPipeline:
    """
    Pipeline for capturing and processing Android screenshots.

    Features:
    - Async screenshot capture via ADB
    - Base64 encoding for LLM context
    - Element annotation overlay
    - Screenshot history management
    """

    def __init__(
        self,
        output_dir: str = "/tmp/mobile_agent/screenshots",
        max_history: int = 10,
        adb_path: str = "adb",
    ):
        """
        Initialize screenshot pipeline.

        Args:
            output_dir: Directory to store screenshots
            max_history: Maximum screenshots to keep in history
            adb_path: Path to ADB executable
        """
        self.output_dir = Path(output_dir)
        self.max_history = max_history
        self.adb_path = adb_path
        self._history: list[ScreenshotResult] = []

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def capture(
        self,
        filename: Optional[str] = None,
        include_base64: bool = False,
    ) -> ScreenshotResult:
        """
        Capture screenshot from connected device.

        Args:
            filename: Custom filename (default: timestamp-based)
            include_base64: Include base64 encoded data

        Returns:
            ScreenshotResult with capture details
        """
        timestamp = time.time()

        if not filename:
            dt = datetime.fromtimestamp(timestamp)
            filename = f"screenshot_{dt.strftime('%Y%m%d_%H%M%S')}.png"

        output_path = self.output_dir / filename

        try:
            # Capture screenshot via ADB
            # Method 1: Direct screencap to local file
            device_path = "/sdcard/screenshot_temp.png"

            # Take screenshot on device
            proc = await asyncio.create_subprocess_exec(
                self.adb_path,
                "shell",
                "screencap",
                "-p",
                device_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()

            if proc.returncode != 0:
                return ScreenshotResult(
                    success=False,
                    error=f"screencap failed: {stderr.decode()}",
                    timestamp=timestamp,
                )

            # Pull screenshot to local
            proc = await asyncio.create_subprocess_exec(
                self.adb_path,
                "pull",
                device_path,
                str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()

            if proc.returncode != 0:
                return ScreenshotResult(
                    success=False,
                    error=f"pull failed: {stderr.decode()}",
                    timestamp=timestamp,
                )

            # Clean up device file
            await asyncio.create_subprocess_exec(
                self.adb_path,
                "shell",
                "rm",
                device_path,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            # Get image dimensions
            width, height = await self._get_image_dimensions(output_path)

            # Encode to base64 if requested
            base64_data = None
            if include_base64:
                with open(output_path, "rb") as f:
                    base64_data = base64.b64encode(f.read()).decode("utf-8")

            result = ScreenshotResult(
                success=True,
                path=str(output_path),
                base64_data=base64_data,
                width=width,
                height=height,
                timestamp=timestamp,
            )

            # Add to history
            self._add_to_history(result)

            logger.info(f"Screenshot captured: {output_path} ({width}x{height})")
            return result

        except Exception as e:
            logger.exception(f"Screenshot capture failed: {e}")
            return ScreenshotResult(
                success=False,
                error=str(e),
                timestamp=timestamp,
            )

    async def capture_with_annotations(
        self,
        elements: list,
        filename: Optional[str] = None,
    ) -> ScreenshotResult:
        """
        Capture screenshot with UI element annotations.

        Args:
            elements: List of UINode objects to annotate
            filename: Custom filename

        Returns:
            ScreenshotResult with annotated screenshot
        """
        # First capture raw screenshot
        result = await self.capture(filename, include_base64=False)

        if not result.success:
            return result

        try:
            # Try to import PIL for annotation
            from PIL import Image, ImageDraw, ImageFont

            img = Image.open(result.path)
            draw = ImageDraw.Draw(img)

            # Load font (fallback to default if not available)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                font = ImageFont.load_default()

            # Draw annotations
            colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]

            for i, element in enumerate(elements[:20]):  # Limit to 20 elements
                color = colors[i % len(colors)]
                bounds = element.bounds

                # Draw rectangle
                draw.rectangle(bounds, outline=color, width=2)

                # Draw index label
                cx, cy = element.center
                label = f"{element.index}"
                draw.text((bounds[0] + 2, bounds[1] + 2), label, fill=color, font=font)

            # Save annotated image
            annotated_path = result.path.replace(".png", "_annotated.png")
            img.save(annotated_path)

            return ScreenshotResult(
                success=True,
                path=annotated_path,
                width=result.width,
                height=result.height,
                timestamp=result.timestamp,
            )

        except ImportError:
            logger.warning("PIL not available, returning raw screenshot")
            return result
        except Exception as e:
            logger.warning(f"Annotation failed: {e}, returning raw screenshot")
            return result

    async def _get_image_dimensions(self, path: Path) -> tuple[int, int]:
        """Get image dimensions without loading full image."""
        try:
            from PIL import Image

            with Image.open(path) as img:
                return img.size
        except ImportError:
            # Fallback: read PNG header directly
            with open(path, "rb") as f:
                f.seek(16)
                width = int.from_bytes(f.read(4), "big")
                height = int.from_bytes(f.read(4), "big")
                return width, height
        except:
            return 0, 0

    def _add_to_history(self, result: ScreenshotResult):
        """Add screenshot to history, removing old ones if needed."""
        self._history.append(result)

        # Remove old screenshots
        while len(self._history) > self.max_history:
            old = self._history.pop(0)
            if old.path and os.path.exists(old.path):
                try:
                    os.remove(old.path)
                except:
                    pass

    @property
    def history(self) -> list[ScreenshotResult]:
        """Get screenshot history."""
        return list(self._history)

    def get_latest(self) -> Optional[ScreenshotResult]:
        """Get most recent screenshot."""
        return self._history[-1] if self._history else None

    def clear_history(self):
        """Clear screenshot history and delete files."""
        for result in self._history:
            if result.path and os.path.exists(result.path):
                try:
                    os.remove(result.path)
                except:
                    pass
        self._history.clear()


class ScreenContextBuilder:
    """
    Builds context for LLM from screenshots and UI state.

    Combines screenshot data with UI hierarchy for comprehensive
    device state representation.
    """

    def __init__(self, use_comptext: bool = True):
        """
        Initialize context builder.

        Args:
            use_comptext: Use CompText format for token efficiency
        """
        self.use_comptext = use_comptext

    def build_context(
        self,
        screenshot: Optional[ScreenshotResult],
        ui_elements: list,
        package: str = "",
        activity: str = "",
    ) -> dict:
        """
        Build complete context for LLM.

        Args:
            screenshot: Screenshot result (optional)
            ui_elements: List of UINode elements
            package: Current app package
            activity: Current activity

        Returns:
            Context dictionary with all relevant information
        """
        context = {
            "has_screenshot": screenshot is not None and screenshot.success,
            "screen_size": screenshot.size if screenshot else (0, 0),
            "timestamp": screenshot.timestamp if screenshot else time.time(),
        }

        if self.use_comptext:
            context["format"] = "comptext"
            context["ui_state"] = self._build_comptext_state(ui_elements, package, activity)
        else:
            context["format"] = "verbose"
            context["ui_state"] = self._build_verbose_state(ui_elements, package, activity)

        # Include base64 image if available
        if screenshot and screenshot.base64_data:
            context["screenshot_base64"] = screenshot.base64_data

        return context

    def _build_comptext_state(
        self,
        elements: list,
        package: str,
        activity: str,
    ) -> str:
        """Build CompText formatted UI state."""
        lines = []

        # App context (shortened)
        if package:
            app_name = package.split(".")[-1]
            lines.append(f"App:{app_name}")

        # Screen info
        lines.append(f"Els:{len(elements)}")

        # Elements (limited for token efficiency)
        for el in elements[:15]:
            if hasattr(el, "to_comptext"):
                lines.append(el.to_comptext())
            else:
                # Fallback for dict-like elements
                idx = el.get("index", 0)
                text = el.get("text", el.get("content_desc", ""))[:20]
                cx = el.get("center", (0, 0))[0] if isinstance(el.get("center"), tuple) else 0
                cy = el.get("center", (0, 0))[1] if isinstance(el.get("center"), tuple) else 0
                el_type = "K" if el.get("clickable") else "T"
                lines.append(f"{idx}:{el_type}:{text}@{cx},{cy}")

        return "\n".join(lines)

    def _build_verbose_state(
        self,
        elements: list,
        package: str,
        activity: str,
    ) -> str:
        """Build verbose UI state for debugging."""
        lines = [
            f"Current Application: {package}",
            f"Current Activity: {activity}",
            f"",
            f"UI Elements ({len(elements)} visible):",
            "-" * 50,
        ]

        for el in elements[:20]:
            if hasattr(el, "to_dict"):
                d = el.to_dict()
            else:
                d = el

            parts = [f"[{d.get('index', '?')}]"]
            if d.get("text"):
                parts.append(f"text=\"{d['text']}\"")
            if d.get("content_desc"):
                parts.append(f"desc=\"{d['content_desc']}\"")
            parts.append(f"clickable={d.get('clickable', False)}")
            parts.append(f"center={d.get('center', (0,0))}")

            lines.append(" ".join(parts))

        return "\n".join(lines)


# Convenience function
async def capture_screen_context(
    adb_path: str = "adb",
    use_comptext: bool = True,
) -> dict:
    """
    Capture complete screen context in one call.

    Args:
        adb_path: Path to ADB executable
        use_comptext: Use CompText format

    Returns:
        Complete context dictionary
    """
    from .ui_parser import UITreeParser

    pipeline = ScreenshotPipeline(adb_path=adb_path)
    parser = UITreeParser()
    builder = ScreenContextBuilder(use_comptext=use_comptext)

    # Capture screenshot
    screenshot = await pipeline.capture(include_base64=False)

    # Get UI hierarchy
    proc = await asyncio.create_subprocess_exec(
        adb_path,
        "shell",
        "uiautomator",
        "dump",
        "/dev/tty",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()

    # Parse UI
    xml_content = stdout.decode("utf-8", errors="ignore")
    elements = parser.parse(xml_content)

    # Get current package/activity
    proc = await asyncio.create_subprocess_exec(
        adb_path,
        "shell",
        "dumpsys",
        "window",
        "windows",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()

    package, activity = "", ""
    for line in stdout.decode().split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            # Extract package/activity from line like:
            # mCurrentFocus=Window{... com.android.chrome/org.chromium.chrome.browser.ChromeTabbedActivity}
            import re

            match = re.search(r"(\S+)/(\S+)\}", line)
            if match:
                package = match.group(1)
                activity = match.group(2)
                break

    return builder.build_context(screenshot, elements, package, activity)
