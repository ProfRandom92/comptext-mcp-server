"""
Mobile Agent Utilities

Provides helper functions for UI parsing, screenshots, metrics, and logging.
"""

from .logging import setup_mobile_logging, JsonFormatter, AgentLogAdapter
from .metrics import TokenMetricsCollector, PerformanceMetrics
from .ui_parser import UITreeParser, UINode, parse_ui_dump, EXAMPLE_UI_XML
from .screenshot import (
    ScreenshotPipeline,
    ScreenshotResult,
    ScreenContextBuilder,
    capture_screen_context,
)

__all__ = [
    # Logging
    "setup_mobile_logging",
    "JsonFormatter",
    "AgentLogAdapter",
    # Metrics
    "TokenMetricsCollector",
    "PerformanceMetrics",
    # UI Parser
    "UITreeParser",
    "UINode",
    "parse_ui_dump",
    "EXAMPLE_UI_XML",
    # Screenshot
    "ScreenshotPipeline",
    "ScreenshotResult",
    "ScreenContextBuilder",
    "capture_screen_context",
]
