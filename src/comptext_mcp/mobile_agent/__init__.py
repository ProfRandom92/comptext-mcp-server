"""
CompText Mobile Agent Module

Android automation via Natural Language powered by:
- Ollama Cloud (qwen3-coder:480b, deepseek-v3.2:671b)
- DroidRun framework
- CompText DSL (80-85% token reduction)
- MCP Protocol
- WebSocket real-time feedback
- Prometheus metrics

Author: Alexander Kölnberger
Created: 2026-01-25
"""

from .agents.mobile_agent import MobileAgent, AgentResult, AgentStep, AgentState
from .config import MobileAgentConfig, AgentMode, OllamaModel
from .ollama_client import OllamaCloudClient
from .droidrun_wrapper import DroidRunWrapper, UIElement, ScreenState, ActionResult, ActionType

# Optional imports (may not be installed)
try:
    from .websocket_server import (
        MobileAgentWebSocketServer,
        WebSocketMobileAgent,
        WebSocketEvent,
        EventType,
        run_websocket_server,
    )

    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

try:
    from .prometheus_metrics import PrometheusMetrics, start_metrics_server

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

__all__ = [
    # Core
    "MobileAgent",
    "MobileAgentConfig",
    "OllamaCloudClient",
    "DroidRunWrapper",
    # Data classes
    "AgentResult",
    "AgentStep",
    "AgentState",
    "UIElement",
    "ScreenState",
    "ActionResult",
    "ActionType",
    # Config
    "AgentMode",
    "OllamaModel",
    # WebSocket (optional)
    "MobileAgentWebSocketServer",
    "WebSocketMobileAgent",
    "WebSocketEvent",
    "EventType",
    "run_websocket_server",
    "WEBSOCKET_AVAILABLE",
    # Prometheus (optional)
    "PrometheusMetrics",
    "start_metrics_server",
    "PROMETHEUS_AVAILABLE",
]

__version__ = "2.1.0"
