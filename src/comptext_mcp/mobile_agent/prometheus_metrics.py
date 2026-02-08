"""
Prometheus Metrics for Mobile Agent

Provides production-grade monitoring metrics including:
- Task execution metrics
- Token usage tracking
- Step performance
- Error rates
- Device status
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Optional

try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Info,
        Summary,
        start_http_server,
        generate_latest,
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        REGISTRY,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """
    Prometheus metrics collector for CompText Mobile Agent.

    Metrics exposed:
    - comptext_mobile_tasks_total: Total tasks executed
    - comptext_mobile_tasks_success: Successful tasks
    - comptext_mobile_tasks_failed: Failed tasks
    - comptext_mobile_task_duration_seconds: Task duration histogram
    - comptext_mobile_tokens_total: Total tokens used
    - comptext_mobile_tokens_saved: Tokens saved by CompText
    - comptext_mobile_steps_total: Total steps executed
    - comptext_mobile_actions_total: Actions by type
    - comptext_mobile_device_connected: Device connection status
    - comptext_mobile_agent_state: Current agent state
    """

    def __init__(self, registry: Optional["CollectorRegistry"] = None):
        if not PROMETHEUS_AVAILABLE:
            raise ImportError("prometheus_client not installed. " "Install with: pip install prometheus-client")

        self.registry = registry or REGISTRY
        self._init_metrics()

    def _init_metrics(self):
        """Initialize all Prometheus metrics."""
        # Counters
        self.tasks_total = Counter(
            "comptext_mobile_tasks_total",
            "Total number of tasks executed",
            ["mode", "comptext_enabled"],
            registry=self.registry,
        )

        self.tasks_success = Counter(
            "comptext_mobile_tasks_success_total",
            "Number of successful tasks",
            ["mode"],
            registry=self.registry,
        )

        self.tasks_failed = Counter(
            "comptext_mobile_tasks_failed_total",
            "Number of failed tasks",
            ["mode", "error_type"],
            registry=self.registry,
        )

        self.tokens_total = Counter(
            "comptext_mobile_tokens_total",
            "Total tokens used across all tasks",
            ["type"],  # prompt, completion
            registry=self.registry,
        )

        self.tokens_saved = Counter(
            "comptext_mobile_tokens_saved_total",
            "Tokens saved by CompText DSL optimization",
            registry=self.registry,
        )

        self.steps_total = Counter(
            "comptext_mobile_steps_total",
            "Total steps executed across all tasks",
            ["action_type"],
            registry=self.registry,
        )

        self.actions_total = Counter(
            "comptext_mobile_actions_total",
            "Total actions executed by type",
            ["action", "success"],
            registry=self.registry,
        )

        self.llm_requests_total = Counter(
            "comptext_mobile_llm_requests_total",
            "Total LLM API requests",
            ["model", "status"],
            registry=self.registry,
        )

        # Histograms
        self.task_duration = Histogram(
            "comptext_mobile_task_duration_seconds",
            "Task execution duration in seconds",
            ["mode", "comptext_enabled"],
            buckets=(0.5, 1, 2, 5, 10, 20, 30, 60, 120, 300),
            registry=self.registry,
        )

        self.step_duration = Histogram(
            "comptext_mobile_step_duration_seconds",
            "Single step execution duration",
            ["action_type"],
            buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10),
            registry=self.registry,
        )

        self.llm_latency = Histogram(
            "comptext_mobile_llm_latency_seconds",
            "LLM API response latency",
            ["model"],
            buckets=(0.5, 1, 2, 3, 5, 10, 20, 30),
            registry=self.registry,
        )

        self.tokens_per_task = Histogram(
            "comptext_mobile_tokens_per_task",
            "Token usage per task",
            ["comptext_enabled"],
            buckets=(100, 250, 500, 1000, 2000, 5000, 10000),
            registry=self.registry,
        )

        # Summaries
        self.token_reduction = Summary(
            "comptext_mobile_token_reduction_percent",
            "Token reduction percentage from CompText",
            registry=self.registry,
        )

        # Gauges
        self.device_connected = Gauge(
            "comptext_mobile_device_connected",
            "Whether Android device is connected (1=yes, 0=no)",
            registry=self.registry,
        )

        self.active_tasks = Gauge(
            "comptext_mobile_active_tasks",
            "Number of currently running tasks",
            registry=self.registry,
        )

        self.websocket_clients = Gauge(
            "comptext_mobile_websocket_clients",
            "Number of connected WebSocket clients",
            registry=self.registry,
        )

        self.agent_state = Gauge(
            "comptext_mobile_agent_state",
            "Current agent state (0=idle, 1=planning, 2=executing, 3=verifying, 4=completed, 5=failed)",
            registry=self.registry,
        )

        # Info
        self.agent_info = Info(
            "comptext_mobile_agent",
            "Mobile agent information",
            registry=self.registry,
        )
        self.agent_info.info(
            {
                "version": "2.1.0",
                "framework": "comptext-mcp",
            }
        )

    # Recording methods
    def record_task_start(self, mode: str, comptext_enabled: bool):
        """Record task start."""
        self.tasks_total.labels(
            mode=mode,
            comptext_enabled=str(comptext_enabled).lower(),
        ).inc()
        self.active_tasks.inc()

    def record_task_end(
        self,
        mode: str,
        comptext_enabled: bool,
        success: bool,
        duration_seconds: float,
        total_tokens: int,
        error_type: Optional[str] = None,
    ):
        """Record task completion."""
        self.active_tasks.dec()

        self.task_duration.labels(
            mode=mode,
            comptext_enabled=str(comptext_enabled).lower(),
        ).observe(duration_seconds)

        self.tokens_per_task.labels(
            comptext_enabled=str(comptext_enabled).lower(),
        ).observe(total_tokens)

        if success:
            self.tasks_success.labels(mode=mode).inc()
        else:
            self.tasks_failed.labels(
                mode=mode,
                error_type=error_type or "unknown",
            ).inc()

    def record_step(
        self,
        action_type: str,
        success: bool,
        duration_seconds: float,
    ):
        """Record step execution."""
        self.steps_total.labels(action_type=action_type).inc()
        self.step_duration.labels(action_type=action_type).observe(duration_seconds)
        self.actions_total.labels(
            action=action_type,
            success=str(success).lower(),
        ).inc()

    def record_tokens(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        baseline_tokens: Optional[int] = None,
    ):
        """Record token usage."""
        self.tokens_total.labels(type="prompt").inc(prompt_tokens)
        self.tokens_total.labels(type="completion").inc(completion_tokens)

        if baseline_tokens and baseline_tokens > prompt_tokens:
            saved = baseline_tokens - prompt_tokens
            self.tokens_saved.inc(saved)
            reduction = (saved / baseline_tokens) * 100
            self.token_reduction.observe(reduction)

    def record_llm_request(
        self,
        model: str,
        success: bool,
        latency_seconds: float,
    ):
        """Record LLM API request."""
        status = "success" if success else "error"
        self.llm_requests_total.labels(model=model, status=status).inc()
        self.llm_latency.labels(model=model).observe(latency_seconds)

    def set_device_connected(self, connected: bool):
        """Set device connection status."""
        self.device_connected.set(1 if connected else 0)

    def set_websocket_clients(self, count: int):
        """Set WebSocket client count."""
        self.websocket_clients.set(count)

    def set_agent_state(self, state: str):
        """Set agent state gauge."""
        state_map = {
            "idle": 0,
            "planning": 1,
            "executing": 2,
            "verifying": 3,
            "completed": 4,
            "failed": 5,
        }
        self.agent_state.set(state_map.get(state.lower(), 0))


@dataclass
class MetricsContext:
    """Context manager for recording task metrics."""

    metrics: PrometheusMetrics
    mode: str
    comptext_enabled: bool
    start_time: float = field(default_factory=time.time)
    total_tokens: int = 0
    success: bool = False
    error_type: Optional[str] = None

    def __enter__(self):
        self.metrics.record_task_start(self.mode, self.comptext_enabled)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            self.success = False
            self.error_type = exc_type.__name__
        self.metrics.record_task_end(
            self.mode,
            self.comptext_enabled,
            self.success,
            duration,
            self.total_tokens,
            self.error_type,
        )


def with_metrics(metrics: PrometheusMetrics):
    """
    Decorator to automatically record metrics for async functions.

    Usage:
        @with_metrics(prometheus_metrics)
        async def execute_task(task: str) -> AgentResult:
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start

                # Try to extract metrics from result
                if hasattr(result, "total_tokens"):
                    metrics.record_tokens(result.total_tokens, 0)
                if hasattr(result, "success"):
                    (
                        metrics.tasks_success.labels(mode="default").inc()
                        if result.success
                        else metrics.tasks_failed.labels(mode="default", error_type="task_error").inc()
                    )

                return result
            except Exception as e:
                metrics.tasks_failed.labels(
                    mode="default",
                    error_type=type(e).__name__,
                ).inc()
                raise

        return wrapper

    return decorator


def start_metrics_server(port: int = 9090, host: str = "0.0.0.0") -> None:
    """
    Start Prometheus metrics HTTP server.

    Args:
        port: HTTP port for metrics endpoint
        host: Hostname to bind to

    The metrics will be available at http://{host}:{port}/metrics
    """
    if not PROMETHEUS_AVAILABLE:
        raise ImportError("prometheus_client not installed")

    start_http_server(port, host)
    logger.info(f"Prometheus metrics server started on http://{host}:{port}/metrics")


async def start_metrics_server_async(port: int = 9090, host: str = "0.0.0.0"):
    """
    Start metrics server asynchronously.

    Can be used with asyncio.create_task() for non-blocking startup.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, start_metrics_server, port, host)


# FastAPI integration
def create_metrics_app():
    """
    Create FastAPI app with Prometheus metrics endpoint.

    Returns:
        FastAPI app with /metrics endpoint
    """
    try:
        from fastapi import FastAPI, Response
    except ImportError:
        raise ImportError("FastAPI not installed. Install with: pip install fastapi")

    app = FastAPI(
        title="CompText Mobile Agent Metrics",
        description="Prometheus metrics for mobile agent monitoring",
        version="2.1.0",
    )

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST,
        )

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "version": "2.1.0"}

    return app


# Global metrics instance (lazy initialization)
_global_metrics: Optional[PrometheusMetrics] = None


def get_metrics() -> PrometheusMetrics:
    """
    Get global metrics instance.

    Creates instance on first call (singleton pattern).
    """
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = PrometheusMetrics()
    return _global_metrics


# CLI command
def main():
    """Standalone metrics server."""
    import argparse

    parser = argparse.ArgumentParser(description="CompText Mobile Agent Metrics Server")
    parser.add_argument("--port", type=int, default=9090, help="Metrics port")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
    )

    # Initialize metrics
    metrics = PrometheusMetrics()
    metrics.agent_info.info(
        {
            "version": "2.1.0",
            "framework": "comptext-mcp",
            "metrics_port": str(args.port),
        }
    )

    start_metrics_server(args.port, args.host)
    logger.info(f"Metrics available at http://{args.host}:{args.port}/metrics")
    logger.info("Press Ctrl+C to stop")

    try:
        import signal

        signal.pause()
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()
