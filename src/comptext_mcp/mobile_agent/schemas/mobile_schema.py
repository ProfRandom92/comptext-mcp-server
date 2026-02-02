"""
CompText DSL Schema for Mobile Commands

Defines the compressed DSL format for mobile automation,
achieving 80-85% token reduction compared to verbose prompts.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

# CompText DSL Grammar for Mobile Automation
MOBILE_DSL_GRAMMAR = """
# CompText Mobile DSL v1.0
# Token-optimized grammar for Android automation

# System Context (compressed)
SYS := "MA:Android" CAPS
CAPS := "Acts:" ACT_LIST
ACT_LIST := "tap/swipe/type/back/home/launch/wait/done"

# Response Format (JSON-like, compressed keys)
RESP := "{" THOUGHT "," ACTION "," PARAMS "," CONF "}"
THOUGHT := "t:" STRING
ACTION := "a:" ACT_TYPE
PARAMS := "p:" PARAM_OBJ
CONF := "c:" FLOAT

# Action Types
ACT_TYPE := "tap" | "swipe" | "type" | "back" | "home" | "launch" | "wait" | "done"

# Parameters (action-specific)
TAP_PARAMS := "{ei:" INT "}" | "{x:" INT ",y:" INT "}"
SWIPE_PARAMS := "{d:" DIR "}" | "{x1:" INT ",y1:" INT ",x2:" INT ",y2:" INT "}"
TYPE_PARAMS := "{txt:" STRING "}"
LAUNCH_PARAMS := "{pkg:" STRING "}"
WAIT_PARAMS := "{s:" FLOAT "}"
DIR := "u" | "d" | "l" | "r"

# Screen State (compressed)
SCREEN := "App:" PKG_SHORT NEWLINE "Els:" NEWLINE EL_LIST
EL_LIST := (EL NEWLINE)*
EL := INT ":" EL_TYPE ":" NAME "@" INT "," INT
EL_TYPE := "B" | "T" | "E"  # Button, Text, Element
NAME := STRING[0:20]
PKG_SHORT := LAST_SEGMENT(PACKAGE)

# Feedback (compressed)
FEEDBACK := "R:" STATUS NEWLINE SCREEN
STATUS := "OK" | "FAIL:" ERROR

# Examples:
# Input:  "Task: Open Chrome\nApp:launcher\nEls:\n0:B:Chrome@540,1200"
# Output: {"t":"Chrome icon visible, tapping","a":"tap","p":{"ei":0},"c":0.95}

# Token Comparison:
# Verbose: "I can see the Chrome icon in the app list. I will tap on it."
#          "action": "tap", "element_index": 0, "confidence": 0.95
# CompText: {"t":"Chrome visible, tap","a":"tap","p":{"ei":0},"c":0.95}
# Reduction: ~80%
"""


class ActionType(str, Enum):
    """Compressed action types."""

    TAP = "tap"
    SWIPE = "swipe"
    TYPE = "type"
    BACK = "back"
    HOME = "home"
    LAUNCH = "launch"
    WAIT = "wait"
    DONE = "done"


class ElementType(str, Enum):
    """Compressed element types."""

    BUTTON = "B"  # Clickable
    TEXT = "T"  # Text content
    ELEMENT = "E"  # Other


class SwipeDirection(str, Enum):
    """Compressed swipe directions."""

    UP = "u"
    DOWN = "d"
    LEFT = "l"
    RIGHT = "r"


@dataclass
class MobileActionSchema:
    """
    CompText-optimized action schema.

    Verbose format (baseline):
    {
        "thought": "I can see the Chrome icon in the app launcher. I will tap on it to open Chrome.",
        "action": "tap",
        "parameters": {
            "element_index": 0,
            "element_name": "Chrome"
        },
        "confidence": 0.95
    }

    CompText format (optimized):
    {"t":"Chrome visible, tap","a":"tap","p":{"ei":0},"c":0.95}

    Token reduction: ~82%
    """

    thought: str  # "t" in DSL
    action: ActionType  # "a" in DSL
    params: dict[str, Any]  # "p" in DSL
    confidence: float  # "c" in DSL

    def to_comptext(self) -> str:
        """Convert to CompText DSL format."""
        import json

        return json.dumps(
            {
                "t": self.thought[:50],  # Truncate thought
                "a": self.action.value,
                "p": self._compress_params(),
                "c": round(self.confidence, 2),
            },
            separators=(",", ":"),
        )

    def to_verbose(self) -> str:
        """Convert to verbose format (for comparison)."""
        import json

        return json.dumps(
            {
                "thought": self.thought,
                "action": self.action.value,
                "parameters": self.params,
                "confidence": self.confidence,
            },
            indent=2,
        )

    def _compress_params(self) -> dict[str, Any]:
        """Compress parameter keys."""
        key_map = {
            "element_index": "ei",
            "text": "txt",
            "package": "pkg",
            "direction": "d",
            "seconds": "s",
        }
        return {key_map.get(k, k): v for k, v in self.params.items()}

    @classmethod
    def from_comptext(cls, data: dict[str, Any]) -> "MobileActionSchema":
        """Parse from CompText DSL format."""
        key_map = {
            "ei": "element_index",
            "txt": "text",
            "pkg": "package",
            "d": "direction",
            "s": "seconds",
        }
        params = {key_map.get(k, k): v for k, v in data.get("p", {}).items()}
        return cls(
            thought=data.get("t", ""),
            action=ActionType(data.get("a", "done")),
            params=params,
            confidence=data.get("c", 0.0),
        )


@dataclass
class ScreenStateSchema:
    """
    CompText-optimized screen state schema.

    Verbose format (baseline):
    {
        "package": "com.android.launcher",
        "activity": "MainActivity",
        "elements": [
            {
                "index": 0,
                "type": "button",
                "text": "Chrome",
                "content_description": "Chrome browser",
                "center_x": 540,
                "center_y": 1200,
                "clickable": true
            }
        ]
    }

    CompText format (optimized):
    App:launcher
    Els:
    0:B:Chrome@540,1200

    Token reduction: ~85%
    """

    package: str
    activity: str
    elements: list[dict[str, Any]]

    def to_comptext(self) -> str:
        """Convert to CompText DSL format."""
        lines = [f"App:{self.package.split('.')[-1] if self.package else '?'}"]
        lines.append("Els:")

        for el in self.elements[:15]:  # Limit to 15 elements
            idx = el.get("index", 0)
            el_type = "B" if el.get("clickable") else "T" if el.get("text") else "E"
            name = (el.get("text") or el.get("content_description") or "el")[:20]
            x = el.get("center_x", 0)
            y = el.get("center_y", 0)
            lines.append(f"{idx}:{el_type}:{name}@{x},{y}")

        return "\n".join(lines)

    def to_verbose(self) -> str:
        """Convert to verbose format (for comparison)."""
        import json

        return json.dumps(
            {
                "package": self.package,
                "activity": self.activity,
                "elements": self.elements,
            },
            indent=2,
        )


@dataclass
class AgentResponseSchema:
    """
    CompText-optimized agent response schema.

    Combines action with result feedback.
    """

    action: MobileActionSchema
    result_status: str  # "OK" or "FAIL:reason"
    new_screen: Optional[ScreenStateSchema] = None

    def to_comptext(self) -> str:
        """Convert to CompText feedback format."""
        lines = [f"R:{self.result_status}"]
        if self.new_screen:
            lines.append(self.new_screen.to_comptext())
        return "\n".join(lines)


# Token comparison utilities
def calculate_token_reduction(verbose: str, comptext: str) -> dict[str, Any]:
    """
    Calculate token reduction between verbose and CompText formats.

    Uses simple word-based estimation (actual tokens may vary by tokenizer).
    """
    # Simple estimation: ~4 chars per token on average
    verbose_tokens = len(verbose) / 4
    comptext_tokens = len(comptext) / 4

    reduction = (verbose_tokens - comptext_tokens) / verbose_tokens * 100

    return {
        "verbose_chars": len(verbose),
        "comptext_chars": len(comptext),
        "verbose_tokens_est": int(verbose_tokens),
        "comptext_tokens_est": int(comptext_tokens),
        "reduction_percent": round(reduction, 1),
    }


# Example usage and comparison
EXAMPLE_VERBOSE_PROMPT = """
You are a mobile automation agent controlling an Android device.

Your capabilities include:
- Analyzing screen states including UI elements, layout, and the current app
- Planning sequences of actions to complete user tasks
- Executing actions such as tap, swipe, type, back, home, and launch_app
- Verifying results after each action and adapting if needed

Please respond in the following JSON format:
{
    "thought": "Your reasoning about the current state and what action to take next",
    "action": "tap|swipe|type|back|home|launch_app|wait|done",
    "parameters": {
        // For tap: {"element_index": 0} or {"x": 100, "y": 200}
        // For swipe: {"direction": "up|down|left|right"}
        // For type: {"text": "text to type"}
        // For launch_app: {"package": "com.android.chrome"}
        // For wait: {"seconds": 1.0}
        // For done: {}
    },
    "confidence": 0.0-1.0
}
"""

EXAMPLE_COMPTEXT_PROMPT = """MA:Android. Acts:tap/swipe/type/back/home/launch/wait/done.
JSON:{t:"thought",a:"action",p:{params},c:0.0-1.0}
tap:{ei:N}|{x,y}. swipe:{d:"u/d/l/r"}. type:{txt:""}. launch:{pkg:""}. done:{}"""


def demo_token_reduction():
    """Demonstrate token reduction with examples."""
    results = calculate_token_reduction(
        EXAMPLE_VERBOSE_PROMPT,
        EXAMPLE_COMPTEXT_PROMPT,
    )

    print("=== CompText Token Reduction Demo ===")
    print(f"Verbose prompt: {results['verbose_chars']} chars (~{results['verbose_tokens_est']} tokens)")
    print(f"CompText prompt: {results['comptext_chars']} chars (~{results['comptext_tokens_est']} tokens)")
    print(f"Reduction: {results['reduction_percent']}%")

    return results


if __name__ == "__main__":
    demo_token_reduction()
