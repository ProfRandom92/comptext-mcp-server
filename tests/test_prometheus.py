"""
Tests for CompText Mobile Agent Prometheus Metrics

Unit tests for the Prometheus metrics collection system.
"""

import pytest
from unittest.mock import MagicMock, patch

# Import with fallback
try:
    from comptext_mcp.mobile_agent.prometheus_metrics import (
        PrometheusMetrics,
        MetricsContext,
        get_metrics,
        with_metrics,
        PROMETHEUS_AVAILABLE,
    )

    HAS_PROMETHEUS = PROMETHEUS_AVAILABLE
except ImportError:
    HAS_PROMETHEUS = False
    PrometheusMetrics = None


@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
class TestPrometheusMetrics:
    """Test PrometheusMetrics class."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance with fresh registry."""
        from prometheus_client import CollectorRegistry

        registry = CollectorRegistry()
        return PrometheusMetrics(registry=registry)

    def test_metrics_creation(self, metrics):
        """Test metrics can be created."""
        assert metrics is not None
        assert hasattr(metrics, "tasks_total")
        assert hasattr(metrics, "tokens_total")

    def test_record_task_start(self, metrics):
        """Test recording task start."""
        metrics.record_task_start("cloud", True)

        # Should increment counter
        value = metrics.tasks_total.labels(
            mode="cloud",
            comptext_enabled="true",
        )._value.get()
        assert value == 1.0

    def test_record_task_end_success(self, metrics):
        """Test recording successful task end."""
        metrics.record_task_start("cloud", True)
        metrics.record_task_end(
            mode="cloud",
            comptext_enabled=True,
            success=True,
            duration_seconds=5.0,
            total_tokens=500,
        )

        # Check success counter
        value = metrics.tasks_success.labels(mode="cloud")._value.get()
        assert value == 1.0

    def test_record_task_end_failure(self, metrics):
        """Test recording failed task."""
        metrics.record_task_start("local", False)
        metrics.record_task_end(
            mode="local",
            comptext_enabled=False,
            success=False,
            duration_seconds=2.0,
            total_tokens=100,
            error_type="DeviceError",
        )

        # Check failure counter
        value = metrics.tasks_failed.labels(
            mode="local",
            error_type="DeviceError",
        )._value.get()
        assert value == 1.0

    def test_record_step(self, metrics):
        """Test recording step execution."""
        metrics.record_step("tap", True, 0.5)

        # Check step counter
        value = metrics.steps_total.labels(action_type="tap")._value.get()
        assert value == 1.0

        # Check actions counter
        action_value = metrics.actions_total.labels(
            action="tap",
            success="true",
        )._value.get()
        assert action_value == 1.0

    def test_record_tokens(self, metrics):
        """Test recording token usage."""
        metrics.record_tokens(
            prompt_tokens=100,
            completion_tokens=50,
            baseline_tokens=300,
        )

        # Check prompt tokens
        prompt_value = metrics.tokens_total.labels(type="prompt")._value.get()
        assert prompt_value == 100.0

        # Check completion tokens
        completion_value = metrics.tokens_total.labels(type="completion")._value.get()
        assert completion_value == 50.0

        # Check saved tokens (300 - 100 = 200)
        saved_value = metrics.tokens_saved._value.get()
        assert saved_value == 200.0

    def test_record_llm_request(self, metrics):
        """Test recording LLM request."""
        metrics.record_llm_request(
            model="qwen3-coder:480b",
            success=True,
            latency_seconds=2.5,
        )

        value = metrics.llm_requests_total.labels(
            model="qwen3-coder:480b",
            status="success",
        )._value.get()
        assert value == 1.0

    def test_set_device_connected(self, metrics):
        """Test setting device connection status."""
        metrics.set_device_connected(True)
        assert metrics.device_connected._value.get() == 1.0

        metrics.set_device_connected(False)
        assert metrics.device_connected._value.get() == 0.0

    def test_set_websocket_clients(self, metrics):
        """Test setting WebSocket client count."""
        metrics.set_websocket_clients(5)
        assert metrics.websocket_clients._value.get() == 5.0

    def test_set_agent_state(self, metrics):
        """Test setting agent state."""
        metrics.set_agent_state("idle")
        assert metrics.agent_state._value.get() == 0.0

        metrics.set_agent_state("planning")
        assert metrics.agent_state._value.get() == 1.0

        metrics.set_agent_state("executing")
        assert metrics.agent_state._value.get() == 2.0

        metrics.set_agent_state("completed")
        assert metrics.agent_state._value.get() == 4.0


@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
class TestMetricsContext:
    """Test MetricsContext context manager."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance."""
        from prometheus_client import CollectorRegistry

        registry = CollectorRegistry()
        return PrometheusMetrics(registry=registry)

    def test_context_manager(self, metrics):
        """Test context manager records metrics."""
        with MetricsContext(
            metrics=metrics,
            mode="cloud",
            comptext_enabled=True,
        ) as ctx:
            ctx.total_tokens = 250
            ctx.success = True

        # Check task was recorded
        success_value = metrics.tasks_success.labels(mode="cloud")._value.get()
        assert success_value == 1.0

    def test_context_manager_failure(self, metrics):
        """Test context manager handles exceptions."""
        try:
            with MetricsContext(
                metrics=metrics,
                mode="local",
                comptext_enabled=False,
            ):
                raise ValueError("Test error")
        except ValueError:
            pass

        # Check failure was recorded
        failure_value = metrics.tasks_failed.labels(
            mode="local",
            error_type="ValueError",
        )._value.get()
        assert failure_value == 1.0


@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
class TestGetMetrics:
    """Test get_metrics singleton."""

    def test_get_metrics_returns_instance(self):
        """Test get_metrics returns an instance."""
        # Reset global state
        import comptext_mcp.mobile_agent.prometheus_metrics as pm

        pm._global_metrics = None

        metrics = get_metrics()
        assert metrics is not None
        assert isinstance(metrics, PrometheusMetrics)

    def test_get_metrics_singleton(self):
        """Test get_metrics returns same instance."""
        # Reset global state
        import comptext_mcp.mobile_agent.prometheus_metrics as pm

        pm._global_metrics = None

        metrics1 = get_metrics()
        metrics2 = get_metrics()

        assert metrics1 is metrics2


@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
class TestWithMetricsDecorator:
    """Test with_metrics decorator."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance."""
        from prometheus_client import CollectorRegistry

        registry = CollectorRegistry()
        return PrometheusMetrics(registry=registry)

    @pytest.mark.asyncio
    async def test_decorator_success(self, metrics):
        """Test decorator records successful calls."""

        @with_metrics(metrics)
        async def successful_task():
            result = MagicMock()
            result.total_tokens = 100
            result.success = True
            return result

        await successful_task()

        # Check metrics were recorded
        success_value = metrics.tasks_success.labels(mode="default")._value.get()
        assert success_value == 1.0

    @pytest.mark.asyncio
    async def test_decorator_failure(self, metrics):
        """Test decorator records failed calls."""

        @with_metrics(metrics)
        async def failing_task():
            raise RuntimeError("Test failure")

        with pytest.raises(RuntimeError):
            await failing_task()

        # Check failure was recorded
        failure_value = metrics.tasks_failed.labels(
            mode="default",
            error_type="RuntimeError",
        )._value.get()
        assert failure_value == 1.0


@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
class TestMetricsHistograms:
    """Test histogram metrics."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance."""
        from prometheus_client import CollectorRegistry

        registry = CollectorRegistry()
        return PrometheusMetrics(registry=registry)

    def test_task_duration_histogram(self, metrics):
        """Test task duration histogram."""
        metrics.record_task_start("cloud", True)
        metrics.record_task_end("cloud", True, True, 3.5, 200)

        # Histogram should have recorded observation
        # Can verify by checking sum
        info = metrics.task_duration.labels(
            mode="cloud",
            comptext_enabled="true",
        )._sum.get()
        assert info == 3.5

    def test_step_duration_histogram(self, metrics):
        """Test step duration histogram."""
        metrics.record_step("swipe", True, 0.75)

        info = metrics.step_duration.labels(action_type="swipe")._sum.get()
        assert info == 0.75

    def test_tokens_per_task_histogram(self, metrics):
        """Test tokens per task histogram."""
        metrics.record_task_start("cloud", True)
        metrics.record_task_end("cloud", True, True, 5.0, 750)

        info = metrics.tokens_per_task.labels(comptext_enabled="true")._sum.get()
        assert info == 750.0


@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
class TestMetricsInfo:
    """Test info metrics."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance."""
        from prometheus_client import CollectorRegistry

        registry = CollectorRegistry()
        return PrometheusMetrics(registry=registry)

    def test_agent_info(self, metrics):
        """Test agent info metric."""
        # Info should be set during initialization
        assert metrics.agent_info is not None


@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
class TestTokenReduction:
    """Test token reduction tracking."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance."""
        from prometheus_client import CollectorRegistry

        registry = CollectorRegistry()
        return PrometheusMetrics(registry=registry)

    def test_token_reduction_calculation(self, metrics):
        """Test token reduction is calculated correctly."""
        # Simulate: baseline 500 tokens, actual 100 tokens = 80% reduction
        metrics.record_tokens(
            prompt_tokens=100,
            completion_tokens=50,
            baseline_tokens=500,
        )

        # Check saved tokens
        saved = metrics.tokens_saved._value.get()
        assert saved == 400.0  # 500 - 100

    def test_no_reduction_without_baseline(self, metrics):
        """Test no reduction recorded without baseline."""
        metrics.record_tokens(
            prompt_tokens=200,
            completion_tokens=100,
            baseline_tokens=None,
        )

        saved = metrics.tokens_saved._value.get()
        assert saved == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
