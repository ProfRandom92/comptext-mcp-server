"""
Tests for CompText Mobile Agent

Unit tests for the mobile agent module components.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from comptext_mcp.mobile_agent.config import (
    MobileAgentConfig,
    OllamaConfig,
    ADBConfig,
    AgentConfig,
    OllamaModel,
    AgentMode,
)
from comptext_mcp.mobile_agent.schemas import (
    MobileActionSchema,
    ScreenStateSchema,
    ActionType,
    calculate_token_reduction,
    EXAMPLE_VERBOSE_PROMPT,
    EXAMPLE_COMPTEXT_PROMPT,
)
from comptext_mcp.mobile_agent.droidrun_wrapper import (
    UIElement,
    ScreenState,
    ActionResult,
    ActionType as DeviceActionType,
)
from comptext_mcp.mobile_agent.utils.metrics import (
    TokenMetricsCollector,
    TaskMetrics,
)


class TestConfig:
    """Tests for configuration classes."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MobileAgentConfig()

        assert config.mode == AgentMode.CLOUD
        assert config.ollama.model == OllamaModel.QWEN3_CODER
        assert config.agent.max_steps == 10
        assert config.agent.use_comptext is True

    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict("os.environ", {
            "AGENT_MODE": "hybrid",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
        }):
            config = MobileAgentConfig.from_env()

            assert config.mode == AgentMode.HYBRID
            assert config.debug is True
            assert config.log_level == "DEBUG"

    def test_config_validation_cloud_without_key(self):
        """Test validation fails for cloud mode without API key."""
        config = MobileAgentConfig()
        config.mode = AgentMode.CLOUD
        config.ollama.api_key = None

        errors = config.validate()

        assert len(errors) > 0
        assert "OLLAMA_API_KEY" in errors[0]

    def test_config_validation_invalid_steps(self):
        """Test validation fails for invalid max_steps."""
        config = MobileAgentConfig()
        config.agent.max_steps = 0

        errors = config.validate()

        assert len(errors) > 0
        assert "max_steps" in errors[0]


class TestUIElement:
    """Tests for UIElement dataclass."""

    def test_center_calculation(self):
        """Test center coordinate calculation."""
        element = UIElement(bounds=(100, 200, 300, 400))

        center = element.center

        assert center == (200, 300)

    def test_display_name_from_text(self):
        """Test display name uses text when available."""
        element = UIElement(text="Submit", resource_id="btn_submit")

        assert element.display_name == "Submit"

    def test_display_name_from_content_desc(self):
        """Test display name uses content_desc when text is empty."""
        element = UIElement(content_desc="Submit button")

        assert element.display_name == "Submit button"

    def test_display_name_from_resource_id(self):
        """Test display name uses resource_id as fallback."""
        element = UIElement(resource_id="com.app:id/btn_submit")

        assert element.display_name == "btn_submit"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        element = UIElement(
            text="Chrome",
            bounds=(100, 200, 300, 400),
            clickable=True,
        )

        data = element.to_dict()

        assert data["text"] == "Chrome"
        assert data["clickable"] is True
        assert data["center"] == (200, 300)


class TestScreenState:
    """Tests for ScreenState dataclass."""

    def test_clickable_elements(self):
        """Test filtering clickable elements."""
        state = ScreenState(
            elements=[
                UIElement(text="Button", clickable=True),
                UIElement(text="Label", clickable=False),
                UIElement(text="Link", clickable=True),
            ]
        )

        clickable = state.clickable_elements

        assert len(clickable) == 2
        assert all(e.clickable for e in clickable)

    def test_find_by_text(self):
        """Test finding elements by text."""
        state = ScreenState(
            elements=[
                UIElement(text="Chrome Browser"),
                UIElement(text="Settings"),
                UIElement(content_desc="Chrome icon"),
            ]
        )

        found = state.find_by_text("chrome", partial=True)

        assert len(found) == 2

    def test_find_by_id(self):
        """Test finding element by resource ID."""
        state = ScreenState(
            elements=[
                UIElement(resource_id="com.app:id/button1"),
                UIElement(resource_id="com.app:id/button2"),
            ]
        )

        found = state.find_by_id("button1")

        assert found is not None
        assert "button1" in found.resource_id

    def test_compact_dict(self):
        """Test compact dictionary format."""
        state = ScreenState(
            package="com.android.chrome",
            activity="MainActivity",
            elements=[
                UIElement(text="Search", clickable=True, bounds=(0, 0, 100, 50)),
            ]
        )

        compact = state.to_compact_dict()

        assert compact["pkg"] == "chrome"
        assert compact["act"] == "MainActivity"
        assert len(compact["els"]) == 1


class TestMobileActionSchema:
    """Tests for CompText action schema."""

    def test_to_comptext(self):
        """Test conversion to CompText format."""
        action = MobileActionSchema(
            thought="Chrome icon visible, tapping",
            action=ActionType.TAP,
            params={"element_index": 0},
            confidence=0.95,
        )

        comptext = action.to_comptext()

        assert '"t":"Chrome icon visible, tapping"' in comptext or '"t":' in comptext
        assert '"a":"tap"' in comptext
        assert '"ei":0' in comptext
        assert '"c":0.95' in comptext

    def test_from_comptext(self):
        """Test parsing from CompText format."""
        data = {
            "t": "Tapping button",
            "a": "tap",
            "p": {"ei": 2},
            "c": 0.9,
        }

        action = MobileActionSchema.from_comptext(data)

        assert action.thought == "Tapping button"
        assert action.action == ActionType.TAP
        assert action.params["element_index"] == 2
        assert action.confidence == 0.9

    def test_verbose_vs_comptext(self):
        """Test that CompText is shorter than verbose."""
        action = MobileActionSchema(
            thought="I can see the Chrome browser icon in the app drawer. I will tap on it to open Chrome.",
            action=ActionType.TAP,
            params={"element_index": 0, "element_name": "Chrome"},
            confidence=0.95,
        )

        verbose = action.to_verbose()
        comptext = action.to_comptext()

        assert len(comptext) < len(verbose)
        # Expect at least 50% reduction
        assert len(comptext) < len(verbose) * 0.5


class TestScreenStateSchema:
    """Tests for screen state schema."""

    def test_to_comptext(self):
        """Test screen state to CompText conversion."""
        schema = ScreenStateSchema(
            package="com.android.chrome",
            activity="MainActivity",
            elements=[
                {
                    "index": 0,
                    "text": "Search",
                    "clickable": True,
                    "center_x": 540,
                    "center_y": 100,
                }
            ]
        )

        comptext = schema.to_comptext()

        assert "App:chrome" in comptext
        assert "0:B:Search@540,100" in comptext

    def test_token_reduction(self):
        """Test token reduction calculation."""
        schema = ScreenStateSchema(
            package="com.android.chrome",
            activity="MainActivity",
            elements=[
                {
                    "index": i,
                    "text": f"Element {i}",
                    "clickable": True,
                    "center_x": 100 + i * 10,
                    "center_y": 200 + i * 20,
                }
                for i in range(10)
            ]
        )

        verbose = schema.to_verbose()
        comptext = schema.to_comptext()

        reduction = calculate_token_reduction(verbose, comptext)

        assert reduction["reduction_percent"] > 70  # At least 70% reduction


class TestTokenMetricsCollector:
    """Tests for metrics collection."""

    def test_task_tracking(self):
        """Test basic task tracking."""
        collector = TokenMetricsCollector()

        collector.start_task("task1", "Open Chrome")
        collector.record_step(
            prompt_tokens=100,
            completion_tokens=50,
            duration_ms=1500,
            success=True,
            baseline_tokens=500,
        )
        collector.complete_task(success=True)

        assert len(collector.tasks) == 1
        task = collector.tasks[0]
        assert task.total_tokens == 150
        assert task.success is True

    def test_token_reduction_calculation(self):
        """Test token reduction percentage calculation."""
        collector = TokenMetricsCollector()

        collector.start_task("task1", "Test")
        collector.record_step(
            prompt_tokens=100,
            completion_tokens=50,
            duration_ms=1000,
            success=True,
            baseline_tokens=500,
        )
        collector.complete_task(success=True)

        task = collector.tasks[0]
        # Reduction: (500 - 100) / 500 = 80%
        assert task.token_reduction_percent == 80.0

    def test_performance_metrics_aggregation(self):
        """Test aggregated performance metrics."""
        collector = TokenMetricsCollector()

        # Add two tasks
        collector.start_task("task1", "Task 1")
        collector.record_step(100, 50, 1000, True, 400)
        collector.complete_task(success=True)

        collector.start_task("task2", "Task 2")
        collector.record_step(80, 40, 800, True, 300)
        collector.complete_task(success=True)

        metrics = collector.get_performance_metrics()

        assert metrics.total_tasks == 2
        assert metrics.successful_tasks == 2
        assert metrics.total_tokens == 270  # 150 + 120
        assert metrics.task_success_rate == 100.0

    def test_comparison_report(self):
        """Test comparison report generation."""
        collector = TokenMetricsCollector()

        collector.start_task("task1", "Test task")
        collector.record_step(100, 50, 1000, True, 500)
        collector.complete_task(success=True)

        report = collector.get_comparison_report()

        assert "CompText Mobile Agent" in report
        assert "Token Reduction" in report


class TestPromptComparison:
    """Tests for system prompt comparison."""

    def test_example_prompt_reduction(self):
        """Test the example prompts achieve expected reduction."""
        result = calculate_token_reduction(
            EXAMPLE_VERBOSE_PROMPT,
            EXAMPLE_COMPTEXT_PROMPT,
        )

        # Should achieve at least 75% reduction
        assert result["reduction_percent"] > 75


class TestActionResult:
    """Tests for action result handling."""

    def test_success_result(self):
        """Test successful action result."""
        result = ActionResult(
            success=True,
            action=DeviceActionType.TAP,
            message="Tapped at (100, 200)",
        )

        assert result.success is True
        assert result.error is None

    def test_failure_result(self):
        """Test failed action result."""
        result = ActionResult(
            success=False,
            action=DeviceActionType.TAP,
            error="Element not found",
        )

        assert result.success is False
        assert "not found" in result.error


# Integration test (requires actual device - marked for manual run)
@pytest.mark.skip(reason="Requires connected Android device")
class TestDeviceIntegration:
    """Integration tests with real device."""

    @pytest.fixture
    async def device(self):
        from comptext_mcp.mobile_agent import DroidRunWrapper
        device = DroidRunWrapper()
        await device.connect()
        yield device

    async def test_screenshot(self, device):
        """Test screenshot capture."""
        path = await device.screenshot()
        assert path.endswith(".png")

    async def test_screen_state(self, device):
        """Test getting screen state."""
        state = await device.get_screen_state()
        assert state.package != ""
        assert len(state.elements) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
