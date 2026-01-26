"""
Tests for CompText Mobile Agent WebSocket Server

Unit tests for the WebSocket real-time communication system.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import asdict

# Import with fallback for when websockets is not installed
try:
    from comptext_mcp.mobile_agent.websocket_server import (
        EventType,
        WebSocketEvent,
        WebSocketMobileAgent,
        MobileAgentWebSocketServer,
        WEBSOCKETS_AVAILABLE,
    )
    HAS_WEBSOCKETS = WEBSOCKETS_AVAILABLE
except ImportError:
    HAS_WEBSOCKETS = False
    EventType = None
    WebSocketEvent = None


@pytest.mark.skipif(not HAS_WEBSOCKETS, reason="websockets not installed")
class TestEventType:
    """Test EventType enum."""

    def test_event_types_exist(self):
        """Test all event types are defined."""
        assert EventType.CONNECTED.value == "connected"
        assert EventType.TASK_STARTED.value == "task_started"
        assert EventType.TASK_COMPLETED.value == "task_completed"
        assert EventType.STEP_STARTED.value == "step_started"
        assert EventType.ACTION_EXECUTED.value == "action_executed"
        assert EventType.ERROR.value == "error"

    def test_event_type_string(self):
        """Test event types are strings."""
        for event_type in EventType:
            assert isinstance(event_type.value, str)


@pytest.mark.skipif(not HAS_WEBSOCKETS, reason="websockets not installed")
class TestWebSocketEvent:
    """Test WebSocketEvent dataclass."""

    def test_event_creation(self):
        """Test creating an event."""
        event = WebSocketEvent(
            type=EventType.TASK_STARTED,
            task_id="test-123",
            data={"task": "Open Chrome"},
        )

        assert event.type == EventType.TASK_STARTED
        assert event.task_id == "test-123"
        assert event.data["task"] == "Open Chrome"
        assert event.timestamp > 0

    def test_event_to_json(self):
        """Test JSON serialization."""
        event = WebSocketEvent(
            type=EventType.CONNECTED,
            data={"message": "Hello"},
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "connected"
        assert parsed["data"]["message"] == "Hello"
        assert "timestamp" in parsed

    def test_event_with_task_id(self):
        """Test event with task ID."""
        event = WebSocketEvent(
            type=EventType.STEP_COMPLETED,
            task_id="abc-123",
            data={"step": 1},
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["task_id"] == "abc-123"


@pytest.mark.skipif(not HAS_WEBSOCKETS, reason="websockets not installed")
class TestWebSocketMobileAgent:
    """Test WebSocketMobileAgent class."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        from comptext_mcp.mobile_agent.config import MobileAgentConfig
        config = MobileAgentConfig()
        config.ollama.api_key = "test-key"
        return config

    def test_agent_creation(self, mock_config):
        """Test agent can be created."""
        broadcast_called = []

        def mock_broadcast(event):
            broadcast_called.append(event)

        agent = WebSocketMobileAgent(mock_config, mock_broadcast)

        assert agent._broadcast == mock_broadcast

    def test_emit_event(self, mock_config):
        """Test event emission."""
        events = []

        def capture_event(event):
            events.append(event)

        agent = WebSocketMobileAgent(mock_config, capture_event)
        agent._task_id = "test-task"
        agent._emit(EventType.TASK_STARTED, {"task": "Test"})

        assert len(events) == 1
        assert events[0].type == EventType.TASK_STARTED
        assert events[0].task_id == "test-task"


@pytest.mark.skipif(not HAS_WEBSOCKETS, reason="websockets not installed")
class TestMobileAgentWebSocketServer:
    """Test MobileAgentWebSocketServer class."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        from comptext_mcp.mobile_agent.config import MobileAgentConfig
        config = MobileAgentConfig()
        config.ollama.api_key = "test-key"
        return config

    def test_server_creation(self, mock_config):
        """Test server can be created."""
        server = MobileAgentWebSocketServer(
            host="localhost",
            port=8765,
            config=mock_config,
        )

        assert server.host == "localhost"
        assert server.port == 8765
        assert not server._running

    def test_server_default_values(self, mock_config):
        """Test server has default values."""
        server = MobileAgentWebSocketServer(config=mock_config)

        assert server.host == "localhost"
        assert server.port == 8765

    @pytest.mark.asyncio
    async def test_server_broadcast(self, mock_config):
        """Test broadcasting to clients."""
        server = MobileAgentWebSocketServer(config=mock_config)

        # Mock client
        mock_client = AsyncMock()
        server._clients.add(mock_client)

        event = WebSocketEvent(
            type=EventType.CONNECTED,
            data={"test": True},
        )

        await server._broadcast(event)

        mock_client.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_server_no_clients_broadcast(self, mock_config):
        """Test broadcasting with no clients."""
        server = MobileAgentWebSocketServer(config=mock_config)

        event = WebSocketEvent(type=EventType.CONNECTED)

        # Should not raise
        await server._broadcast(event)


@pytest.mark.skipif(not HAS_WEBSOCKETS, reason="websockets not installed")
class TestMessageHandling:
    """Test message handling."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        from comptext_mcp.mobile_agent.config import MobileAgentConfig
        config = MobileAgentConfig()
        config.ollama.api_key = "test-key"
        return config

    @pytest.mark.asyncio
    async def test_handle_invalid_json(self, mock_config):
        """Test handling invalid JSON message."""
        server = MobileAgentWebSocketServer(config=mock_config)
        mock_ws = AsyncMock()

        await server._handle_message(mock_ws, "not valid json")

        # Should send error
        mock_ws.send.assert_called()
        sent_msg = mock_ws.send.call_args[0][0]
        parsed = json.loads(sent_msg)
        assert parsed["type"] == "error"

    @pytest.mark.asyncio
    async def test_handle_unknown_command(self, mock_config):
        """Test handling unknown command."""
        server = MobileAgentWebSocketServer(config=mock_config)
        mock_ws = AsyncMock()

        await server._handle_message(mock_ws, '{"command": "unknown_cmd"}')

        mock_ws.send.assert_called()

    @pytest.mark.asyncio
    async def test_handle_status_command(self, mock_config):
        """Test handling status command."""
        server = MobileAgentWebSocketServer(config=mock_config)
        mock_ws = AsyncMock()

        await server._handle_message(mock_ws, '{"command": "status"}')

        mock_ws.send.assert_called()

    @pytest.mark.asyncio
    async def test_handle_config_command(self, mock_config):
        """Test handling config command."""
        server = MobileAgentWebSocketServer(config=mock_config)
        mock_ws = AsyncMock()

        await server._handle_message(mock_ws, '{"command": "config"}')

        mock_ws.send.assert_called()


@pytest.mark.skipif(not HAS_WEBSOCKETS, reason="websockets not installed")
class TestEventSerialization:
    """Test event JSON serialization."""

    def test_connected_event(self):
        """Test connected event serialization."""
        event = WebSocketEvent(
            type=EventType.CONNECTED,
            data={"version": "2.1.0", "client_id": 12345},
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "connected"
        assert parsed["data"]["version"] == "2.1.0"

    def test_task_started_event(self):
        """Test task started event."""
        event = WebSocketEvent(
            type=EventType.TASK_STARTED,
            task_id="task-001",
            data={
                "task": "Open Chrome",
                "max_steps": 10,
                "use_comptext": True,
            },
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "task_started"
        assert parsed["task_id"] == "task-001"
        assert parsed["data"]["task"] == "Open Chrome"

    def test_step_completed_event(self):
        """Test step completed event."""
        event = WebSocketEvent(
            type=EventType.STEP_COMPLETED,
            task_id="task-001",
            data={
                "step": 3,
                "action": "tap",
                "success": True,
                "duration_ms": 1500,
            },
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["data"]["step"] == 3
        assert parsed["data"]["success"] is True

    def test_error_event(self):
        """Test error event."""
        event = WebSocketEvent(
            type=EventType.ERROR,
            data={"error": "Device not connected"},
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "error"
        assert "Device not connected" in parsed["data"]["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
