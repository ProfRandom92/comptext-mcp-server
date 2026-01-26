"""
UI Tree XML Parser

Parses Android UI hierarchy XML (from `adb shell uiautomator dump`)
into structured UIElement objects with CompText optimization.
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class UINode:
    """Represents a single UI node from the hierarchy."""
    index: int
    text: str = ""
    resource_id: str = ""
    class_name: str = ""
    package: str = ""
    content_desc: str = ""
    checkable: bool = False
    checked: bool = False
    clickable: bool = False
    enabled: bool = True
    focusable: bool = False
    focused: bool = False
    scrollable: bool = False
    long_clickable: bool = False
    password: bool = False
    selected: bool = False
    visible: bool = True
    bounds: tuple[int, int, int, int] = (0, 0, 0, 0)
    children: list["UINode"] = field(default_factory=list)

    @property
    def center(self) -> tuple[int, int]:
        """Calculate center coordinates."""
        x1, y1, x2, y2 = self.bounds
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    @property
    def width(self) -> int:
        return self.bounds[2] - self.bounds[0]

    @property
    def height(self) -> int:
        return self.bounds[3] - self.bounds[1]

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def display_name(self) -> str:
        """Get best display name for this element."""
        if self.text:
            return self.text[:30]
        if self.content_desc:
            return self.content_desc[:30]
        if self.resource_id:
            # Extract ID name from full resource ID
            parts = self.resource_id.split("/")
            return parts[-1][:30] if len(parts) > 1 else self.resource_id[:30]
        # Fallback to class name
        return self.class_name.split(".")[-1][:20]

    @property
    def element_type(self) -> str:
        """Determine element type for CompText shorthand."""
        class_lower = self.class_name.lower()

        if "button" in class_lower:
            return "B"  # Button
        elif "edittext" in class_lower or "textfield" in class_lower:
            return "I"  # Input
        elif "checkbox" in class_lower:
            return "C"  # Checkbox
        elif "switch" in class_lower or "toggle" in class_lower:
            return "S"  # Switch
        elif "image" in class_lower:
            return "G"  # Graphic/Image
        elif "text" in class_lower:
            return "T"  # Text
        elif "list" in class_lower or "recycler" in class_lower:
            return "L"  # List
        elif "scroll" in class_lower:
            return "R"  # Scrollable Region
        elif self.clickable:
            return "K"  # Clickable (generic)
        else:
            return "E"  # Element (generic)

    def to_comptext(self) -> str:
        """Convert to CompText format: index:type:name@x,y"""
        cx, cy = self.center
        return f"{self.index}:{self.element_type}:{self.display_name}@{cx},{cy}"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "text": self.text,
            "resource_id": self.resource_id,
            "class": self.class_name,
            "content_desc": self.content_desc,
            "clickable": self.clickable,
            "enabled": self.enabled,
            "scrollable": self.scrollable,
            "bounds": self.bounds,
            "center": self.center,
            "type": self.element_type,
        }


class UITreeParser:
    """
    Parser for Android UI hierarchy XML.

    Converts raw XML from `adb shell uiautomator dump` into
    structured UINode objects optimized for agent consumption.
    """

    # Bounds pattern: [x1,y1][x2,y2]
    BOUNDS_PATTERN = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')

    def __init__(self, min_area: int = 100, max_elements: int = 50):
        """
        Initialize parser.

        Args:
            min_area: Minimum element area to include (filters tiny elements)
            max_elements: Maximum elements to return (for token efficiency)
        """
        self.min_area = min_area
        self.max_elements = max_elements
        self._index_counter = 0

    def parse(self, xml_content: str) -> list[UINode]:
        """
        Parse UI hierarchy XML into UINode list.

        Args:
            xml_content: Raw XML string from uiautomator dump

        Returns:
            List of UINode objects, sorted by relevance
        """
        self._index_counter = 0

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse UI XML: {e}")
            return []

        nodes = []
        self._parse_node(root, nodes)

        # Filter and sort
        filtered = self._filter_nodes(nodes)
        sorted_nodes = self._sort_by_relevance(filtered)

        # Re-index after sorting
        for i, node in enumerate(sorted_nodes[:self.max_elements]):
            node.index = i

        return sorted_nodes[:self.max_elements]

    def _parse_node(self, element: ET.Element, nodes: list[UINode], depth: int = 0):
        """Recursively parse XML element into UINode."""
        attrib = element.attrib

        # Parse bounds
        bounds_str = attrib.get("bounds", "[0,0][0,0]")
        bounds_match = self.BOUNDS_PATTERN.match(bounds_str)
        if bounds_match:
            bounds = tuple(int(x) for x in bounds_match.groups())
        else:
            bounds = (0, 0, 0, 0)

        node = UINode(
            index=self._index_counter,
            text=attrib.get("text", ""),
            resource_id=attrib.get("resource-id", ""),
            class_name=attrib.get("class", ""),
            package=attrib.get("package", ""),
            content_desc=attrib.get("content-desc", ""),
            checkable=attrib.get("checkable", "false") == "true",
            checked=attrib.get("checked", "false") == "true",
            clickable=attrib.get("clickable", "false") == "true",
            enabled=attrib.get("enabled", "true") == "true",
            focusable=attrib.get("focusable", "false") == "true",
            focused=attrib.get("focused", "false") == "true",
            scrollable=attrib.get("scrollable", "false") == "true",
            long_clickable=attrib.get("long-clickable", "false") == "true",
            password=attrib.get("password", "false") == "true",
            selected=attrib.get("selected", "false") == "true",
            bounds=bounds,
        )

        self._index_counter += 1
        nodes.append(node)

        # Parse children
        for child in element:
            child_node = self._parse_node(child, nodes, depth + 1)
            if child_node:
                node.children.append(child_node)

        return node

    def _filter_nodes(self, nodes: list[UINode]) -> list[UINode]:
        """Filter nodes based on relevance criteria."""
        filtered = []

        for node in nodes:
            # Skip invisible or disabled elements
            if not node.enabled:
                continue

            # Skip elements that are too small
            if node.area < self.min_area:
                continue

            # Skip elements with no meaningful content and not interactive
            has_content = bool(node.text or node.content_desc or node.resource_id)
            is_interactive = node.clickable or node.scrollable or node.checkable

            if not has_content and not is_interactive:
                continue

            filtered.append(node)

        return filtered

    def _sort_by_relevance(self, nodes: list[UINode]) -> list[UINode]:
        """Sort nodes by relevance for agent interaction."""
        def relevance_score(node: UINode) -> tuple:
            # Higher score = more relevant
            score = 0

            # Interactive elements are most important
            if node.clickable:
                score += 100
            if node.scrollable:
                score += 50
            if node.checkable:
                score += 40

            # Elements with text/description are valuable
            if node.text:
                score += 30
            if node.content_desc:
                score += 20
            if node.resource_id:
                score += 10

            # Prefer elements higher on screen (usually more important)
            y_position = node.bounds[1]

            return (-score, y_position, node.bounds[0])

        return sorted(nodes, key=relevance_score)

    def to_comptext_format(self, nodes: list[UINode], package: str = "", activity: str = "") -> str:
        """
        Convert nodes to CompText format for minimal token usage.

        Args:
            nodes: List of UINode objects
            package: Current app package name
            activity: Current activity name

        Returns:
            CompText formatted string
        """
        lines = []

        # App context (shortened)
        if package:
            app_name = package.split(".")[-1]
            lines.append(f"App:{app_name}")
        if activity:
            act_name = activity.split(".")[-1]
            lines.append(f"Act:{act_name}")

        # Elements
        lines.append("Els:")
        for node in nodes:
            lines.append(node.to_comptext())

        return "\n".join(lines)

    def to_verbose_format(self, nodes: list[UINode], package: str = "", activity: str = "") -> str:
        """
        Convert nodes to verbose format for debugging.

        Args:
            nodes: List of UINode objects
            package: Current app package name
            activity: Current activity name

        Returns:
            Verbose formatted string
        """
        lines = []

        lines.append(f"Package: {package}")
        lines.append(f"Activity: {activity}")
        lines.append("")
        lines.append(f"UI Elements ({len(nodes)} total):")
        lines.append("-" * 60)

        for node in nodes:
            parts = [f"[{node.index}]"]

            if node.text:
                parts.append(f'text="{node.text}"')
            if node.content_desc:
                parts.append(f'desc="{node.content_desc}"')
            if node.resource_id:
                parts.append(f'id="{node.resource_id.split("/")[-1]}"')

            parts.append(f"type={node.element_type}")
            parts.append(f"clickable={node.clickable}")
            parts.append(f"center={node.center}")
            parts.append(f"bounds={node.bounds}")

            lines.append(" ".join(parts))

        return "\n".join(lines)


def parse_ui_dump(xml_content: str, comptext: bool = True) -> tuple[list[UINode], str]:
    """
    Convenience function to parse UI dump.

    Args:
        xml_content: Raw XML from uiautomator dump
        comptext: If True, return CompText format; else verbose

    Returns:
        Tuple of (nodes list, formatted string)
    """
    parser = UITreeParser()
    nodes = parser.parse(xml_content)

    if comptext:
        formatted = parser.to_comptext_format(nodes)
    else:
        formatted = parser.to_verbose_format(nodes)

    return nodes, formatted


# Example XML for testing
EXAMPLE_UI_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.android.launcher3" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[0,0][1080,1920]">
    <node index="0" text="Chrome" resource-id="com.android.launcher3:id/icon" class="android.widget.TextView" package="com.android.launcher3" content-desc="Chrome" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="true" password="false" selected="false" bounds="[120,800][280,1000]" />
    <node index="1" text="Settings" resource-id="com.android.launcher3:id/icon" class="android.widget.TextView" package="com.android.launcher3" content-desc="Settings" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="true" password="false" selected="false" bounds="[400,800][560,1000]" />
    <node index="2" text="Messages" resource-id="com.android.launcher3:id/icon" class="android.widget.TextView" package="com.android.launcher3" content-desc="Messages" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="true" password="false" selected="false" bounds="[680,800][840,1000]" />
  </node>
</hierarchy>'''


if __name__ == "__main__":
    # Test the parser
    nodes, comptext_output = parse_ui_dump(EXAMPLE_UI_XML, comptext=True)
    print("CompText Format:")
    print(comptext_output)
    print()

    _, verbose_output = parse_ui_dump(EXAMPLE_UI_XML, comptext=False)
    print("Verbose Format:")
    print(verbose_output)
    print()

    print(f"Token comparison:")
    print(f"  CompText: ~{len(comptext_output.split())} words")
    print(f"  Verbose:  ~{len(verbose_output.split())} words")
    print(f"  Reduction: {100 - (len(comptext_output) / len(verbose_output) * 100):.1f}%")
