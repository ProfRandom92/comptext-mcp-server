"""
MCP Tools for Mobile Agent

Exposes mobile automation capabilities as MCP tools for integration
with Claude Desktop and other MCP clients.
"""

import asyncio
import json
import logging
from typing import Any, Optional

from ..config import MobileAgentConfig
from ..agents.mobile_agent import MobileAgent, AgentResult
from ..droidrun_wrapper import DroidRunWrapper, ScreenState

logger = logging.getLogger(__name__)

# Global agent instance (lazy initialized)
_agent: Optional[MobileAgent] = None
_device: Optional[DroidRunWrapper] = None


async def _get_agent() -> MobileAgent:
    """Get or create global agent instance."""
    global _agent
    if _agent is None:
        _agent = MobileAgent()
        await _agent.initialize()
    return _agent


async def _get_device() -> DroidRunWrapper:
    """Get or create global device instance."""
    global _device
    if _device is None:
        _device = DroidRunWrapper()
        await _device.connect()
    return _device


async def mobile_execute_task(task: str) -> dict[str, Any]:
    """
    Execute a natural language task on the Android device.

    Args:
        task: Natural language task description
              e.g., "Open Chrome and search for weather"

    Returns:
        Task execution result with steps, tokens, and status
    """
    try:
        agent = await _get_agent()
        result = await agent.execute(task)

        return {
            "success": result.success,
            "task": result.task,
            "steps_count": result.step_count,
            "total_tokens": result.total_tokens,
            "duration_ms": result.total_duration_ms,
            "error": result.error,
            "steps": [
                {
                    "number": s.step_number,
                    "action": s.action,
                    "reasoning": s.reasoning,
                    "success": s.result.success if s.result else False,
                }
                for s in result.steps
            ],
        }

    except Exception as e:
        logger.exception(f"Task execution failed: {e}")
        return {
            "success": False,
            "task": task,
            "error": str(e),
        }


async def mobile_screenshot(filename: Optional[str] = None) -> dict[str, Any]:
    """
    Capture a screenshot from the Android device.

    Args:
        filename: Optional filename for the screenshot

    Returns:
        Screenshot path and base64 data
    """
    try:
        device = await _get_device()
        path = await device.screenshot(filename)

        return {
            "success": True,
            "path": path,
        }

    except Exception as e:
        logger.exception(f"Screenshot failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def mobile_get_screen_state() -> dict[str, Any]:
    """
    Get current screen state including UI elements.

    Returns:
        Screen state with package, activity, and UI elements
    """
    try:
        device = await _get_device()
        state = await device.get_screen_state(include_screenshot=False)

        return {
            "success": True,
            "package": state.package,
            "activity": state.activity,
            "elements": [e.to_dict() for e in state.elements[:20]],
            "clickable_count": len(state.clickable_elements),
            "input_field_count": len(state.input_fields),
        }

    except Exception as e:
        logger.exception(f"Get screen state failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def mobile_tap(
    x: Optional[int] = None,
    y: Optional[int] = None,
    element_text: Optional[str] = None,
) -> dict[str, Any]:
    """
    Tap on the screen.

    Args:
        x: X coordinate (if not using element_text)
        y: Y coordinate (if not using element_text)
        element_text: Text of element to tap (alternative to coordinates)

    Returns:
        Tap result
    """
    try:
        device = await _get_device()

        if element_text:
            # Find element by text and tap
            state = await device.get_screen_state(include_screenshot=False)
            elements = state.find_by_text(element_text)
            if not elements:
                return {
                    "success": False,
                    "error": f"Element with text '{element_text}' not found",
                }
            result = await device.tap_element(elements[0])
        elif x is not None and y is not None:
            result = await device.tap(x, y)
        else:
            return {
                "success": False,
                "error": "Either (x, y) or element_text must be provided",
            }

        return {
            "success": result.success,
            "message": result.message,
            "error": result.error,
        }

    except Exception as e:
        logger.exception(f"Tap failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def mobile_swipe(
    direction: Optional[str] = None,
    x1: Optional[int] = None,
    y1: Optional[int] = None,
    x2: Optional[int] = None,
    y2: Optional[int] = None,
) -> dict[str, Any]:
    """
    Swipe on the screen.

    Args:
        direction: Swipe direction (up, down, left, right)
        x1, y1: Start coordinates (alternative to direction)
        x2, y2: End coordinates (alternative to direction)

    Returns:
        Swipe result
    """
    try:
        device = await _get_device()

        if direction:
            # Calculate coordinates based on direction
            cx, cy = 540, 960  # Screen center (adjust for device)
            distance = 500
            directions = {
                "up": (cx, cy + distance, cx, cy - distance),
                "down": (cx, cy - distance, cx, cy + distance),
                "left": (cx + distance, cy, cx - distance, cy),
                "right": (cx - distance, cy, cx + distance, cy),
            }
            if direction not in directions:
                return {
                    "success": False,
                    "error": f"Invalid direction: {direction}",
                }
            x1, y1, x2, y2 = directions[direction]

        if all(v is not None for v in [x1, y1, x2, y2]):
            result = await device.swipe(x1, y1, x2, y2)
            return {
                "success": result.success,
                "message": result.message,
                "error": result.error,
            }
        else:
            return {
                "success": False,
                "error": "Either direction or (x1, y1, x2, y2) must be provided",
            }

    except Exception as e:
        logger.exception(f"Swipe failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def mobile_type(text: str) -> dict[str, Any]:
    """
    Type text on the screen.

    Args:
        text: Text to type

    Returns:
        Type result
    """
    try:
        device = await _get_device()
        result = await device.type_text(text)

        return {
            "success": result.success,
            "message": result.message,
            "error": result.error,
        }

    except Exception as e:
        logger.exception(f"Type failed: {e}")
        return {
            "success": False,
            "error": str(e),
        }


def register_mobile_tools(server) -> None:
    """
    Register mobile tools with MCP server.

    Args:
        server: MCP server instance
    """
    from mcp.server import Server

    @server.tool("mobile_execute_task")
    async def tool_execute_task(task: str) -> str:
        """Execute a natural language task on Android device."""
        result = await mobile_execute_task(task)
        return json.dumps(result, indent=2)

    @server.tool("mobile_screenshot")
    async def tool_screenshot(filename: str = "") -> str:
        """Capture screenshot from Android device."""
        result = await mobile_screenshot(filename or None)
        return json.dumps(result, indent=2)

    @server.tool("mobile_get_screen")
    async def tool_get_screen() -> str:
        """Get current screen state with UI elements."""
        result = await mobile_get_screen_state()
        return json.dumps(result, indent=2)

    @server.tool("mobile_tap")
    async def tool_tap(
        x: int = 0,
        y: int = 0,
        element_text: str = "",
    ) -> str:
        """Tap on screen at coordinates or element."""
        result = await mobile_tap(
            x=x if x > 0 else None,
            y=y if y > 0 else None,
            element_text=element_text or None,
        )
        return json.dumps(result, indent=2)

    @server.tool("mobile_swipe")
    async def tool_swipe(direction: str = "") -> str:
        """Swipe on screen (up/down/left/right)."""
        result = await mobile_swipe(direction=direction or None)
        return json.dumps(result, indent=2)

    @server.tool("mobile_type")
    async def tool_type(text: str) -> str:
        """Type text on focused input field."""
        result = await mobile_type(text)
        return json.dumps(result, indent=2)

    logger.info("Mobile agent tools registered with MCP server")
