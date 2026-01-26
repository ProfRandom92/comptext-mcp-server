"""
WebSocket Server for Mobile Agent Real-Time Feedback

Provides live updates during agent task execution including:
- Step progress
- Action execution
- Token usage
- Screenshots
- Completion status
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Optional, Set
from weakref import WeakSet

try:
    import websockets
    from websockets.server import WebSocketServerProtocol, serve
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = Any

from .config import MobileAgentConfig
from .agents.mobile_agent import MobileAgent, AgentResult, AgentStep, AgentState

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """WebSocket event types."""
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"

    # Task lifecycle events
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"

    # Step events
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    ACTION_EXECUTED = "action_executed"

    # State changes
    STATE_CHANGED = "state_changed"
    SCREEN_UPDATED = "screen_updated"

    # Metrics
    TOKENS_USED = "tokens_used"
    PROGRESS_UPDATE = "progress_update"


@dataclass
class WebSocketEvent:
    """WebSocket event payload."""
    type: EventType
    timestamp: float = field(default_factory=time.time)
    task_id: Optional[str] = None
    data: dict = field(default_factory=dict)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps({
            "type": self.type.value,
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "data": self.data,
        })


class WebSocketMobileAgent(MobileAgent):
    """
    Mobile Agent with WebSocket broadcast capabilities.

    Extends MobileAgent to send real-time updates via WebSocket.
    """

    def __init__(
        self,
        config: Optional[MobileAgentConfig] = None,
        broadcast_callback: Optional[Callable[[WebSocketEvent], None]] = None,
    ):
        super().__init__(config)
        self._broadcast = broadcast_callback
        self._task_id: Optional[str] = None
        self._step_count = 0

    def _emit(self, event_type: EventType, data: dict = None):
        """Emit WebSocket event."""
        if self._broadcast:
            event = WebSocketEvent(
                type=event_type,
                task_id=self._task_id,
                data=data or {},
            )
            try:
                self._broadcast(event)
            except Exception as e:
                logger.warning(f"Failed to broadcast event: {e}")

    async def execute(self, task: str) -> AgentResult:
        """Execute task with WebSocket updates."""
        import uuid
        self._task_id = str(uuid.uuid4())[:8]
        self._step_count = 0

        self._emit(EventType.TASK_STARTED, {
            "task": task,
            "max_steps": self.config.agent.max_steps,
            "use_comptext": self.config.agent.use_comptext,
        })

        # Override state transitions
        original_state = self._state

        try:
            result = await self._execute_with_events(task)

            if result.success:
                self._emit(EventType.TASK_COMPLETED, {
                    "task": task,
                    "steps": result.step_count,
                    "tokens": result.total_tokens,
                    "duration_ms": result.total_duration_ms,
                })
            else:
                self._emit(EventType.TASK_FAILED, {
                    "task": task,
                    "error": result.error,
                    "steps": result.step_count,
                })

            return result

        except Exception as e:
            self._emit(EventType.ERROR, {"error": str(e)})
            raise

    async def _execute_with_events(self, task: str) -> AgentResult:
        """Execute task with step-by-step event emission."""
        from .droidrun_wrapper import ActionResult
        from .ollama_client import ChatMessage

        start_time = time.time()
        self._current_task = task
        self._state = AgentState.PLANNING

        result = AgentResult(success=False, task=task)

        try:
            # Initial screen state
            screen = await self.device.get_screen_state()
            self._add_to_context(screen)

            self._emit(EventType.SCREEN_UPDATED, {
                "package": screen.package,
                "activity": screen.activity,
                "element_count": len(screen.elements),
            })

            messages = self._build_initial_messages(task, screen)

            for step_num in range(self.config.agent.max_steps):
                self._step_count = step_num + 1
                step_start = time.time()

                # Emit step started
                self._emit(EventType.STEP_STARTED, {
                    "step": step_num + 1,
                    "max_steps": self.config.agent.max_steps,
                })

                self._state = AgentState.PLANNING
                self._emit(EventType.STATE_CHANGED, {"state": self._state.value})

                # Get LLM response
                response = await self.ollama.chat(messages)
                result.total_tokens += response.total_tokens

                self._emit(EventType.TOKENS_USED, {
                    "step_tokens": response.total_tokens,
                    "total_tokens": result.total_tokens,
                })

                # Parse action
                action_data = self._parse_action(response.message.content)
                if not action_data:
                    logger.warning(f"Failed to parse action: {response.message.content}")
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
                        action=self.device.__class__.__name__,
                        message="Task completed",
                    )
                    result.steps.append(step)
                    result.success = True
                    self._state = AgentState.COMPLETED
                    self._emit(EventType.STATE_CHANGED, {"state": self._state.value})
                    break

                # Execute action
                self._state = AgentState.EXECUTING
                self._emit(EventType.STATE_CHANGED, {"state": self._state.value})

                action_result = await self._execute_action(action_data, screen)
                step.result = action_result

                self._emit(EventType.ACTION_EXECUTED, {
                    "action": action_data.get("action"),
                    "success": action_result.success,
                    "message": action_result.message,
                    "error": action_result.error,
                })

                # Verify and get new screen state
                self._state = AgentState.VERIFYING
                self._emit(EventType.STATE_CHANGED, {"state": self._state.value})

                await asyncio.sleep(self.config.agent.step_delay)
                screen = await self.device.get_screen_state()
                step.screen_after = screen
                self._add_to_context(screen)

                self._emit(EventType.SCREEN_UPDATED, {
                    "package": screen.package,
                    "activity": screen.activity,
                    "element_count": len(screen.elements),
                })

                step.duration_ms = (time.time() - step_start) * 1000
                result.steps.append(step)

                # Emit step completed
                self._emit(EventType.STEP_COMPLETED, {
                    "step": step_num + 1,
                    "action": step.action,
                    "success": action_result.success,
                    "duration_ms": step.duration_ms,
                })

                # Progress update
                progress = (step_num + 1) / self.config.agent.max_steps * 100
                self._emit(EventType.PROGRESS_UPDATE, {
                    "progress": progress,
                    "step": step_num + 1,
                    "max_steps": self.config.agent.max_steps,
                })

                # Update conversation
                messages.append(ChatMessage(
                    role="assistant",
                    content=response.message.content,
                ))
                messages.append(ChatMessage(
                    role="user",
                    content=self._build_step_feedback(action_result, screen),
                ))

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
            self._emit(EventType.ERROR, {"error": str(e)})

        return result


class MobileAgentWebSocketServer:
    """
    WebSocket server for Mobile Agent real-time communication.

    Features:
    - Multiple client connections
    - Task execution with live updates
    - Command reception (start, stop, screenshot)
    - Automatic reconnection support
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
        config: Optional[MobileAgentConfig] = None,
    ):
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError(
                "websockets package not installed. "
                "Install with: pip install websockets"
            )

        self.host = host
        self.port = port
        self.config = config or MobileAgentConfig.from_env()

        self._clients: Set[WebSocketServerProtocol] = set()
        self._server = None
        self._agent: Optional[WebSocketMobileAgent] = None
        self._running = False
        self._current_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the WebSocket server."""
        self._server = await serve(
            self._handler,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10,
        )
        self._running = True
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")

    async def stop(self):
        """Stop the WebSocket server."""
        self._running = False

        # Cancel any running task
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

        # Close all client connections
        for client in list(self._clients):
            await client.close()
        self._clients.clear()

        # Stop server
        if self._server:
            self._server.close()
            await self._server.wait_closed()

        logger.info("WebSocket server stopped")

    async def _handler(self, websocket: WebSocketServerProtocol):
        """Handle WebSocket client connections."""
        self._clients.add(websocket)
        client_id = id(websocket)
        logger.info(f"Client {client_id} connected")

        # Send welcome message
        await self._send_to_client(websocket, WebSocketEvent(
            type=EventType.CONNECTED,
            data={
                "message": "Connected to CompText Mobile Agent",
                "version": "2.1.0",
                "client_id": client_id,
            },
        ))

        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        finally:
            self._clients.discard(websocket)

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            command = data.get("command")

            if command == "run":
                task = data.get("task")
                if task:
                    await self._run_task(task)
                else:
                    await self._send_error(websocket, "Missing 'task' parameter")

            elif command == "stop":
                if self._current_task and not self._current_task.done():
                    self._current_task.cancel()
                    await self._broadcast(WebSocketEvent(
                        type=EventType.TASK_FAILED,
                        data={"error": "Task cancelled by user"},
                    ))

            elif command == "screenshot":
                await self._capture_screenshot()

            elif command == "status":
                await self._send_status(websocket)

            elif command == "config":
                await self._send_config(websocket)

            else:
                await self._send_error(websocket, f"Unknown command: {command}")

        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON message")
        except Exception as e:
            await self._send_error(websocket, str(e))

    async def _run_task(self, task: str):
        """Run a task with the mobile agent."""
        if self._current_task and not self._current_task.done():
            await self._broadcast(WebSocketEvent(
                type=EventType.ERROR,
                data={"error": "Another task is already running"},
            ))
            return

        async def execute():
            async with WebSocketMobileAgent(
                self.config,
                broadcast_callback=lambda e: asyncio.create_task(self._broadcast(e)),
            ) as agent:
                if not await agent.initialize():
                    await self._broadcast(WebSocketEvent(
                        type=EventType.ERROR,
                        data={"error": "Failed to initialize agent"},
                    ))
                    return
                await agent.execute(task)

        self._current_task = asyncio.create_task(execute())

    async def _capture_screenshot(self):
        """Capture and broadcast screenshot."""
        from .droidrun_wrapper import DroidRunWrapper

        device = DroidRunWrapper(self.config.adb)
        if await device.connect():
            path = await device.screenshot()
            await self._broadcast(WebSocketEvent(
                type=EventType.SCREEN_UPDATED,
                data={"screenshot_path": path},
            ))

    async def _send_status(self, websocket: WebSocketServerProtocol):
        """Send current status to client."""
        status = {
            "running": self._current_task is not None and not self._current_task.done(),
            "clients": len(self._clients),
            "mode": self.config.mode.value,
            "comptext_enabled": self.config.agent.use_comptext,
        }
        await self._send_to_client(websocket, WebSocketEvent(
            type=EventType.PROGRESS_UPDATE,
            data=status,
        ))

    async def _send_config(self, websocket: WebSocketServerProtocol):
        """Send configuration to client."""
        config_data = {
            "mode": self.config.mode.value,
            "model": self.config.ollama.model.value,
            "max_steps": self.config.agent.max_steps,
            "use_comptext": self.config.agent.use_comptext,
        }
        await self._send_to_client(websocket, WebSocketEvent(
            type=EventType.CONNECTED,
            data={"config": config_data},
        ))

    async def _send_error(self, websocket: WebSocketServerProtocol, error: str):
        """Send error to specific client."""
        await self._send_to_client(websocket, WebSocketEvent(
            type=EventType.ERROR,
            data={"error": error},
        ))

    async def _send_to_client(self, websocket: WebSocketServerProtocol, event: WebSocketEvent):
        """Send event to specific client."""
        try:
            await websocket.send(event.to_json())
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")

    async def _broadcast(self, event: WebSocketEvent):
        """Broadcast event to all connected clients."""
        if not self._clients:
            return

        message = event.to_json()
        await asyncio.gather(
            *[client.send(message) for client in self._clients],
            return_exceptions=True,
        )


async def run_websocket_server(
    host: str = "localhost",
    port: int = 8765,
    config: Optional[MobileAgentConfig] = None,
):
    """
    Run the WebSocket server.

    Args:
        host: Server hostname
        port: Server port
        config: Optional agent configuration
    """
    server = MobileAgentWebSocketServer(host, port, config)
    await server.start()

    try:
        await asyncio.Future()  # Run forever
    except asyncio.CancelledError:
        pass
    finally:
        await server.stop()


# CLI integration
def main():
    """Main entry point for standalone WebSocket server."""
    import argparse

    parser = argparse.ArgumentParser(description="CompText Mobile Agent WebSocket Server")
    parser.add_argument("--host", default="localhost", help="Server hostname")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
    )

    asyncio.run(run_websocket_server(args.host, args.port))


if __name__ == "__main__":
    main()
