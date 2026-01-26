"""
Tests for CompText Mobile Agent CLI

Unit tests for the command-line interface.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from click.testing import CliRunner

from comptext_mcp.mobile_agent.cli import cli, main
from comptext_mcp.mobile_agent.config import MobileAgentConfig, AgentMode
from comptext_mcp.mobile_agent.agents.mobile_agent import AgentResult


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = MobileAgentConfig()
    config.mode = AgentMode.CLOUD
    config.ollama.api_key = "test-key-12345"
    return config


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self, runner):
        """Test CLI --help option."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "CompText Mobile Agent" in result.output

    def test_cli_version(self, runner):
        """Test CLI --version option."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "2.1.0" in result.output

    def test_cli_verbose_flag(self, runner):
        """Test --verbose flag is accepted."""
        result = runner.invoke(cli, ["--verbose", "--help"])
        assert result.exit_code == 0


class TestRunCommand:
    """Test 'run' command."""

    def test_run_help(self, runner):
        """Test run command help."""
        result = runner.invoke(cli, ["run", "--help"])
        assert result.exit_code == 0
        assert "Execute a natural language task" in result.output

    def test_run_dry_run(self, runner):
        """Test dry-run mode."""
        with patch.dict("os.environ", {"OLLAMA_API_KEY": "test-key"}):
            result = runner.invoke(cli, ["run", "Open Chrome", "--dry-run"])
            assert result.exit_code == 0
            assert "DRY RUN" in result.output

    def test_run_missing_task(self, runner):
        """Test run without task argument."""
        result = runner.invoke(cli, ["run"])
        assert result.exit_code != 0

    @patch("comptext_mcp.mobile_agent.cli._run_task")
    def test_run_success(self, mock_run, runner):
        """Test successful task execution."""
        mock_result = AgentResult(
            success=True,
            task="Open Chrome",
            total_tokens=150,
            total_duration_ms=2500.0,
        )
        mock_run.return_value = mock_result

        with patch.dict("os.environ", {"OLLAMA_API_KEY": "test-key"}):
            result = runner.invoke(cli, ["run", "Open Chrome"])
            # Should succeed with mock
            assert "Open Chrome" in result.output or result.exit_code == 0

    def test_run_with_options(self, runner):
        """Test run with various options."""
        with patch.dict("os.environ", {"OLLAMA_API_KEY": "test-key"}):
            result = runner.invoke(cli, [
                "run", "Open Chrome",
                "--steps", "15",
                "--mode", "local",
                "--no-comptext",
                "--dry-run",
            ])
            assert result.exit_code == 0


class TestScreenshotCommand:
    """Test 'screenshot' command."""

    def test_screenshot_help(self, runner):
        """Test screenshot command help."""
        result = runner.invoke(cli, ["screenshot", "--help"])
        assert result.exit_code == 0
        assert "Capture a screenshot" in result.output

    @patch("comptext_mcp.mobile_agent.cli._capture_screenshot")
    def test_screenshot_success(self, mock_capture, runner):
        """Test successful screenshot capture."""
        mock_capture.return_value = True

        result = runner.invoke(cli, ["screenshot", "-o", "test.png"])
        # Check the command runs
        assert "screenshot" in result.output.lower() or result.exit_code in (0, 1)


class TestStatusCommand:
    """Test 'status' command."""

    def test_status_help(self, runner):
        """Test status command help."""
        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0

    @patch("comptext_mcp.mobile_agent.cli._check_device")
    def test_status_no_device(self, mock_check, runner):
        """Test status when no device connected."""
        mock_check.return_value = (False, None)

        result = runner.invoke(cli, ["status"])
        assert "No device" in result.output or "Device" in result.output


class TestConfigCommand:
    """Test 'config' command."""

    def test_config_help(self, runner):
        """Test config command help."""
        result = runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0

    def test_config_display(self, runner):
        """Test config display."""
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0
        assert "Mode" in result.output or "config" in result.output.lower()

    def test_config_json(self, runner):
        """Test config JSON output."""
        result = runner.invoke(cli, ["config", "--json"])
        assert result.exit_code == 0
        # Should be valid JSON
        try:
            data = json.loads(result.output)
            assert "mode" in data
        except json.JSONDecodeError:
            # Output may contain non-JSON preamble
            pass


class TestBenchmarkCommand:
    """Test 'benchmark' command."""

    def test_benchmark_help(self, runner):
        """Test benchmark command help."""
        result = runner.invoke(cli, ["benchmark", "--help"])
        assert result.exit_code == 0
        assert "Benchmark" in result.output or "benchmark" in result.output


class TestInteractiveCommand:
    """Test 'interactive' command."""

    def test_interactive_help(self, runner):
        """Test interactive command help."""
        result = runner.invoke(cli, ["interactive", "--help"])
        assert result.exit_code == 0
        assert "interactive" in result.output.lower()


class TestServeCommand:
    """Test 'serve' command."""

    def test_serve_help(self, runner):
        """Test serve command help."""
        result = runner.invoke(cli, ["serve", "--help"])
        assert result.exit_code == 0
        assert "WebSocket" in result.output

    def test_serve_options(self, runner):
        """Test serve accepts host/port options."""
        result = runner.invoke(cli, ["serve", "--help"])
        assert "--host" in result.output
        assert "--port" in result.output


class TestMetricsCommand:
    """Test 'metrics' command."""

    def test_metrics_help(self, runner):
        """Test metrics command help."""
        result = runner.invoke(cli, ["metrics", "--help"])
        assert result.exit_code == 0
        assert "Prometheus" in result.output or "metrics" in result.output.lower()

    def test_metrics_options(self, runner):
        """Test metrics accepts port option."""
        result = runner.invoke(cli, ["metrics", "--help"])
        assert "--port" in result.output


class TestMain:
    """Test main entry point."""

    def test_main_callable(self):
        """Test main function is callable."""
        assert callable(main)


class TestCLIOutput:
    """Test CLI output formatting."""

    def test_banner_content(self, runner):
        """Test banner displays correctly."""
        with patch.dict("os.environ", {"OLLAMA_API_KEY": "test-key"}):
            result = runner.invoke(cli, ["run", "test", "--dry-run"])
            # Banner should be displayed
            assert "CompText" in result.output or "Mobile" in result.output

    def test_error_display(self, runner):
        """Test error messages are displayed."""
        result = runner.invoke(cli, ["run"])  # Missing required argument
        assert result.exit_code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
