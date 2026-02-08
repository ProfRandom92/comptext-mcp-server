"""
Mobile Agent - Core Implementation

AI agent for Android automation using:
- Ollama Cloud for reasoning
- CompText DSL for token optimization
- DroidRun for device control
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from ..config import MobileAgentConfig, AgentMode
from ..ollama_client import OllamaCloudClient, ChatMessage, ChatResponse
from ..droidrun_wrapper import DroidRunWrapper, ScreenState, ActionResult, ActionType, UIElement

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Agent execution state."""

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentStep:
    """Single step in agent execution."""

    step_number: int
    action: str
    reasoning: str
    result: Optional[ActionResult] = None
    screen_before: Optional[ScreenState] = None
    screen_after: Optional[ScreenState] = None
    tokens_used: int = 0
    duration_ms: float = 0.0


@dataclass
class AgentResult:
    """Result of agent task execution."""

    success: bool
    task: str
    steps: list[AgentStep] = field(default_factory=list)
    total_tokens: int = 0
    total_duration_ms: float = 0.0
    error: Optional[str] = None
    final_screen: Optional[ScreenState] = None

    @property
    def step_count(self) -> int:
        return len(self.steps)


class MobileAgent:
    """
    AI-powered mobile automation agent.

    Features:
    - Natural language task understanding
    - Plan-Execute-Verify loop
    - Multi-step action sequences
    - Error recovery with retry logic
    - CompText DSL optimization for token reduction
    - Context memory (last N screens)
    """

    SYSTEM_PROMPT = """You are a mobile automation agent controlling an Android device.

Your capabilities:
- Analyze screen states (UI elements, layout, current app)
- Plan action sequences to complete user tasks
- Execute actions: tap, swipe, type, back, home, launch_app
- Verify results and adapt if needed

Response format (JSON):
{
    "thought": "Brief reasoning about current state and next action",
    "action": "tap|swipe|type|back|home|launch_app|wait|done",
    "params": {
        // For tap: {"element_index": 0} or {"x": 100, "y": 200}
        // For swipe: {"direction": "up|down|left|right"} or {"x1":..., "y1":..., "x2":..., "y2":...}
        // For type: {"text": "text to type"}
        // For launch_app: {"package": "com.android.chrome"}
        // For wait: {"seconds": 1.0}
        // For done: {}
    },
    "confidence": 0.0-1.0
}

Rules:
- Use element_index when possible (more reliable than coordinates)
- Always verify action success before proceeding
- If stuck, try alternative approaches
- Report "done" when task is complete
- Keep thoughts concise (CompText optimized)
"""

    COMPTEXT_SYSTEM_PROMPT = """MA:Android. Acts:tap/swipe/type/back/home/launch/wait/done.
JSON:{t:"thought",a:"action",p:{params},c:0.0-1.0}
tap:{ei:N}|{x,y}. swipe:{d:"u/d/l/r"}. type:{txt:""}. launch:{pkg:""}. done:{}
Verify after act. Concise."""

    def __init__(self, config: Optional[MobileAgentConfig] = None):
        self.config = config or MobileAgentConfig.from_env()
        self.ollama = OllamaCloudClient(self.config.ollama)
        self.device = DroidRunWrapper(self.config.adb)

        self._state = AgentState.IDLE
        self._context_memory: list[ScreenState] = []
        self._current_task: Optional[str] = None

    async def __aenter__(self):
        await self.ollama.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.ollama.__aexit__(exc_type, exc_val, exc_tb)

    async def initialize(self) -> bool:
        """
        Initialize agent and connect to device.

        Returns:
            True if initialization successful
        """
        errors = self.config.validate()
        if errors:
            logger.error(f"Configuration errors: {errors}")
            return False

        connected = await self.device.connect()
        if not connected:
            logger.error("Failed to connect to Android device")
            return False

        logger.info("Mobile agent initialized successfully")
        return True

    async def execute(self, task: str) -> AgentResult:
        """
        Execute a natural language task.

        Args:
            task: Natural language description of the task
                  e.g., "Open Chrome and search for weather"

        Returns:
            AgentResult with execution details
        """
        start_time = time.time()
        self._current_task = task
        self._state = AgentState.PLANNING

        result = AgentResult(success=False, task=task)

        try:
            # Initial screen state
            screen = await self.device.get_screen_state()
            self._add_to_context(screen)

            messages = self._build_initial_messages(task, screen)

            for step_num in range(self.config.agent.max_steps):
                step_start = time.time()
                self._state = AgentState.PLANNING

                # Get LLM response
                response = await self.ollama.chat(messages)
                result.total_tokens += response.total_tokens

                # Parse action
                action_data = self._parse_action(response.message.content)
                if not action_data:
                    logger.warning(f"Failed to parse action from: {response.message.content}")
                    continue

                step = AgentStep(
                    step_number=step_num + 1,
                    action=action_data.get("action", "unknown"),
                    reasoning=action_data.get("thought", ""),
                    screen_before=screen,
                    tokens_used=response.total_tokens,
                )

                # Check for completion
                if action_data.get("action") == "done":
                    step.result = ActionResult(
                        success=True,
                        action=ActionType.WAIT,
                        message="Task completed",
                    )
                    result.steps.append(step)
                    result.success = True
                    self._state = AgentState.COMPLETED
                    break

                # Execute action
                self._state = AgentState.EXECUTING
                action_result = await self._execute_action(action_data, screen)
                step.result = action_result

                # Verify and get new screen state
                self._state = AgentState.VERIFYING
                await asyncio.sleep(self.config.agent.step_delay)
                screen = await self.device.get_screen_state()
                step.screen_after = screen
                self._add_to_context(screen)

                step.duration_ms = (time.time() - step_start) * 1000
                result.steps.append(step)

                # Update conversation
                messages.append(
                    ChatMessage(
                        role="assistant",
                        content=response.message.content,
                    )
                )
                messages.append(
                    ChatMessage(
                        role="user",
                        content=self._build_step_feedback(action_result, screen),
                    )
                )

                # Handle failure with retry
                if not action_result.success:
                    if step_num < self.config.agent.retry_attempts:
                        logger.warning(f"Action failed, retrying: {action_result.error}")
                        continue
                    else:
                        result.error = f"Action failed: {action_result.error}"
                        self._state = AgentState.FAILED
                        break

            result.final_screen = screen
            result.total_duration_ms = (time.time() - start_time) * 1000

            if not result.success and self._state != AgentState.FAILED:
                result.error = "Max steps reached without completing task"
                self._state = AgentState.FAILED

        except Exception as e:
            logger.exception(f"Agent execution failed: {e}")
            result.error = str(e)
            self._state = AgentState.FAILED

        return result

    def _build_initial_messages(
        self,
        task: str,
        screen: ScreenState,
    ) -> list[ChatMessage]:
        """Build initial message list for LLM."""
        system_prompt = self.COMPTEXT_SYSTEM_PROMPT if self.config.agent.use_comptext else self.SYSTEM_PROMPT

        screen_context = self._format_screen_context(screen)

        return [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(
                role="user",
                content=f"Task: {task}\n\nCurrent screen:\n{screen_context}",
            ),
        ]

    def _format_screen_context(self, screen: ScreenState) -> str:
        """Format screen state for LLM context."""
        if self.config.agent.use_comptext:
            # CompText optimized format
            return self._format_screen_compact(screen)
        else:
            return self._format_screen_verbose(screen)

    def _format_screen_compact(self, screen: ScreenState) -> str:
        """CompText-optimized screen format (80-85% token reduction)."""
        lines = [
            f"App:{screen.package.split('.')[-1] if screen.package else '?'}",
            "Els:",
        ]

        for i, el in enumerate(screen.elements[:15]):  # Limit elements
            el_type = "B" if el.clickable else "T" if el.text else "E"
            name = el.display_name[:20]
            x, y = el.center
            lines.append(f"{i}:{el_type}:{name}@{x},{y}")

        return "\n".join(lines)

    def _format_screen_verbose(self, screen: ScreenState) -> str:
        """Verbose screen format for debugging."""
        lines = [
            f"Package: {screen.package}",
            f"Activity: {screen.activity}",
            "",
            "UI Elements:",
        ]

        for i, el in enumerate(screen.elements[:20]):
            el_info = [f"[{i}]"]
            if el.text:
                el_info.append(f'text="{el.text}"')
            if el.content_desc:
                el_info.append(f'desc="{el.content_desc}"')
            if el.resource_id:
                el_info.append(f'id="{el.resource_id.split("/")[-1]}"')
            el_info.append(f"clickable={el.clickable}")
            el_info.append(f"center={el.center}")

            lines.append(" ".join(el_info))

        return "\n".join(lines)

    def _build_step_feedback(
        self,
        result: ActionResult,
        screen: ScreenState,
    ) -> str:
        """Build feedback message after action execution."""
        status = "OK" if result.success else f"FAIL:{result.error}"
        screen_context = self._format_screen_context(screen)

        if self.config.agent.use_comptext:
            return f"R:{status}\n{screen_context}"
        else:
            return f"Action result: {status}\n\nNew screen state:\n{screen_context}"

    def _parse_action(self, content: str) -> Optional[dict[str, Any]]:
        """Parse action from LLM response."""
        import json
        import re

        # Try to extract JSON from response
        try:
            # Look for JSON object
            json_match = re.search(r"\{[^{}]*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Fallback: try to parse structured text
        action_match = re.search(r'"?action"?\s*:\s*"?(\w+)"?', content, re.IGNORECASE)
        if action_match:
            return {
                "action": action_match.group(1).lower(),
                "thought": content[:100],
                "params": {},
            }

        return None

    async def _execute_action(
        self,
        action_data: dict[str, Any],
        screen: ScreenState,
    ) -> ActionResult:
        """Execute parsed action on device."""
        action = action_data.get("action", "").lower()
        params = action_data.get("params", {})

        try:
            if action == "tap":
                if "element_index" in params or "ei" in params:
                    idx = params.get("element_index", params.get("ei", 0))
                    if 0 <= idx < len(screen.elements):
                        return await self.device.tap_element(screen.elements[idx])
                    else:
                        return ActionResult(
                            success=False,
                            action=ActionType.TAP,
                            error=f"Invalid element index: {idx}",
                        )
                elif "x" in params and "y" in params:
                    return await self.device.tap(int(params["x"]), int(params["y"]))
                else:
                    return ActionResult(
                        success=False,
                        action=ActionType.TAP,
                        error="Missing tap coordinates or element_index",
                    )

            elif action == "swipe":
                if "direction" in params or "d" in params:
                    direction = params.get("direction", params.get("d", "up"))
                    # Calculate swipe coordinates based on screen center
                    # Assuming 1080x1920 screen, adjust as needed
                    cx, cy = 540, 960
                    distance = 500
                    directions = {
                        "up": (cx, cy + distance, cx, cy - distance),
                        "u": (cx, cy + distance, cx, cy - distance),
                        "down": (cx, cy - distance, cx, cy + distance),
                        "d": (cx, cy - distance, cx, cy + distance),
                        "left": (cx + distance, cy, cx - distance, cy),
                        "l": (cx + distance, cy, cx - distance, cy),
                        "right": (cx - distance, cy, cx + distance, cy),
                        "r": (cx - distance, cy, cx + distance, cy),
                    }
                    if direction in directions:
                        x1, y1, x2, y2 = directions[direction]
                        return await self.device.swipe(x1, y1, x2, y2)
                elif all(k in params for k in ["x1", "y1", "x2", "y2"]):
                    return await self.device.swipe(
                        int(params["x1"]),
                        int(params["y1"]),
                        int(params["x2"]),
                        int(params["y2"]),
                    )
                return ActionResult(
                    success=False,
                    action=ActionType.SWIPE,
                    error="Invalid swipe parameters",
                )

            elif action == "type":
                text = params.get("text", params.get("txt", ""))
                if text:
                    return await self.device.type_text(text)
                return ActionResult(
                    success=False,
                    action=ActionType.TYPE,
                    error="Missing text to type",
                )

            elif action == "back":
                return await self.device.back()

            elif action == "home":
                return await self.device.home()

            elif action == "launch_app" or action == "launch":
                package = params.get("package", params.get("pkg", ""))
                if package:
                    return await self.device.launch_app(package)
                return ActionResult(
                    success=False,
                    action=ActionType.LAUNCH_APP,
                    error="Missing package name",
                )

            elif action == "wait":
                seconds = float(params.get("seconds", params.get("s", 1.0)))
                return await self.device.wait(seconds)

            else:
                return ActionResult(
                    success=False,
                    action=ActionType.TAP,  # Default
                    error=f"Unknown action: {action}",
                )

        except Exception as e:
            return ActionResult(
                success=False,
                action=ActionType.TAP,
                error=str(e),
            )

    def _add_to_context(self, screen: ScreenState):
        """Add screen to context memory."""
        self._context_memory.append(screen)
        # Keep only last N screens
        max_size = self.config.agent.context_memory_size
        if len(self._context_memory) > max_size:
            self._context_memory = self._context_memory[-max_size:]

    @property
    def state(self) -> AgentState:
        """Get current agent state."""
        return self._state

    @property
    def context_memory(self) -> list[ScreenState]:
        """Get context memory (last N screens)."""
        return self._context_memory


# Convenience function
async def run_mobile_task(task: str, config: Optional[MobileAgentConfig] = None) -> AgentResult:
    """
    Run a mobile automation task.

    Args:
        task: Natural language task description
        config: Optional agent configuration

    Returns:
        AgentResult with execution details
    """
    async with MobileAgent(config) as agent:
        if not await agent.initialize():
            return AgentResult(
                success=False,
                task=task,
                error="Failed to initialize agent",
            )
        return await agent.execute(task)
