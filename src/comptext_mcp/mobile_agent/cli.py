"""
CompText Mobile Agent CLI

Command-line interface for Android automation via natural language.

Usage:
    comptext-mobile run "Open Chrome and search for weather"
    comptext-mobile screenshot
    comptext-mobile status
    comptext-mobile config
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .config import MobileAgentConfig, AgentMode, OllamaModel
from .agents.mobile_agent import MobileAgent, AgentResult


# Configure logging
def setup_logging(level: str, verbose: bool = False):
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    if verbose:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )


def print_banner():
    """Print CLI banner."""
    click.echo(
        click.style(
            """
╔═══════════════════════════════════════════════════════════╗
║           CompText Mobile Agent CLI v2.1.0                ║
║       Android Automation via Natural Language             ║
╚═══════════════════════════════════════════════════════════╝
""",
            fg="cyan",
        )
    )


def print_result(result: AgentResult, verbose: bool = False):
    """Print agent execution result."""
    if result.success:
        click.echo(click.style("\n✓ Task completed successfully!", fg="green", bold=True))
    else:
        click.echo(click.style(f"\n✗ Task failed: {result.error}", fg="red", bold=True))

    click.echo(f"\n{'─' * 50}")
    click.echo(f"  Task:     {result.task}")
    click.echo(f"  Steps:    {result.step_count}")
    click.echo(f"  Tokens:   {result.total_tokens:,}")
    click.echo(f"  Duration: {result.total_duration_ms:.0f}ms")
    click.echo(f"{'─' * 50}")

    if verbose and result.steps:
        click.echo(click.style("\nExecution Steps:", fg="yellow", bold=True))
        for step in result.steps:
            status = "✓" if step.result and step.result.success else "✗"
            click.echo(f"  {status} Step {step.step_number}: {step.action}")
            if step.reasoning:
                click.echo(f"    └─ {step.reasoning[:80]}...")


@click.group()
@click.version_option(version="2.1.0", prog_name="comptext-mobile")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
@click.option("--config-file", "-c", type=click.Path(exists=True), help="Path to config file")
@click.pass_context
def cli(ctx, verbose: bool, debug: bool, config_file: Optional[str]):
    """
    CompText Mobile Agent - Android automation via natural language.

    Powered by Ollama Cloud and CompText DSL for 80%+ token reduction.

    Examples:

        comptext-mobile run "Open Chrome"

        comptext-mobile run "Search for weather in Berlin" --steps 15

        comptext-mobile screenshot --output ./screen.png

        comptext-mobile status
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug

    log_level = "DEBUG" if debug else "INFO"
    setup_logging(log_level, verbose)

    # Load config
    if config_file:
        # TODO: Load from file
        ctx.obj["config"] = MobileAgentConfig.from_env()
    else:
        ctx.obj["config"] = MobileAgentConfig.from_env()


@cli.command()
@click.argument("task")
@click.option("--steps", "-s", default=10, help="Maximum steps (default: 10)")
@click.option("--no-comptext", is_flag=True, help="Disable CompText optimization")
@click.option("--mode", "-m", type=click.Choice(["cloud", "local", "hybrid"]), default="cloud")
@click.option("--model", type=click.Choice(["qwen3-coder:480b", "deepseek-v3.2:671b", "nemotron-3-nano:30b"]))
@click.option("--output", "-o", type=click.Path(), help="Save result to JSON file")
@click.option("--dry-run", is_flag=True, help="Parse task without executing")
@click.pass_context
def run(ctx, task: str, steps: int, no_comptext: bool, mode: str, model: Optional[str], output: Optional[str], dry_run: bool):
    """
    Execute a natural language task on Android device.

    TASK: Natural language description of what to do.

    Examples:

        comptext-mobile run "Open Chrome and search for weather"

        comptext-mobile run "Send a message to John" --steps 15

        comptext-mobile run "Take a photo" --mode local
    """
    print_banner()
    verbose = ctx.obj["verbose"]
    config: MobileAgentConfig = ctx.obj["config"]

    # Apply CLI options
    config.agent.max_steps = steps
    config.agent.use_comptext = not no_comptext
    config.mode = AgentMode(mode)

    if model:
        config.ollama.model = OllamaModel(model)

    click.echo(f"Task: {click.style(task, fg='yellow', bold=True)}")
    click.echo(f"Mode: {config.mode.value} | CompText: {config.agent.use_comptext} | Max Steps: {steps}")

    if dry_run:
        click.echo(click.style("\n[DRY RUN] Task parsed successfully. No execution.", fg="yellow"))
        return

    # Validate config
    errors = config.validate()
    if errors:
        for error in errors:
            click.echo(click.style(f"Config error: {error}", fg="red"))
        sys.exit(1)

    click.echo(click.style("\nExecuting...", fg="cyan"))

    # Run agent
    result = asyncio.run(_run_task(config, task))

    # Print result
    print_result(result, verbose)

    # Save output
    if output:
        output_data = {
            "task": result.task,
            "success": result.success,
            "steps": result.step_count,
            "tokens": result.total_tokens,
            "duration_ms": result.total_duration_ms,
            "error": result.error,
        }
        Path(output).write_text(json.dumps(output_data, indent=2))
        click.echo(f"\nResult saved to: {output}")

    sys.exit(0 if result.success else 1)


async def _run_task(config: MobileAgentConfig, task: str) -> AgentResult:
    """Run task with agent."""
    async with MobileAgent(config) as agent:
        if not await agent.initialize():
            return AgentResult(
                success=False,
                task=task,
                error="Failed to initialize agent (check device connection)",
            )
        return await agent.execute(task)


@cli.command()
@click.option("--output", "-o", type=click.Path(), default="screenshot.png", help="Output path")
@click.option("--open", "open_file", is_flag=True, help="Open screenshot after capture")
@click.pass_context
def screenshot(ctx, output: str, open_file: bool):
    """
    Capture a screenshot from the connected Android device.

    Examples:

        comptext-mobile screenshot

        comptext-mobile screenshot -o ./screens/current.png

        comptext-mobile screenshot --open
    """
    config: MobileAgentConfig = ctx.obj["config"]

    click.echo("Capturing screenshot...")

    result = asyncio.run(_capture_screenshot(config, output))

    if result:
        click.echo(click.style(f"✓ Screenshot saved: {output}", fg="green"))
        if open_file:
            click.launch(output)
    else:
        click.echo(click.style("✗ Failed to capture screenshot", fg="red"))
        sys.exit(1)


async def _capture_screenshot(config: MobileAgentConfig, output: str) -> bool:
    """Capture screenshot from device."""
    from .droidrun_wrapper import DroidRunWrapper

    device = DroidRunWrapper(config.adb)
    if not await device.connect():
        return False

    path = await device.screenshot(output)
    return path is not None


@cli.command()
@click.pass_context
def status(ctx):
    """
    Show device connection status and agent configuration.
    """
    config: MobileAgentConfig = ctx.obj["config"]

    click.echo(click.style("\nDevice Status", fg="cyan", bold=True))
    click.echo("─" * 40)

    # Check device connection
    connected, device_info = asyncio.run(_check_device(config))

    if connected:
        click.echo(click.style("  ✓ Device connected", fg="green"))
        if device_info:
            click.echo(f"    Serial:  {device_info.get('serial', 'N/A')}")
            click.echo(f"    Model:   {device_info.get('model', 'N/A')}")
            click.echo(f"    Android: {device_info.get('version', 'N/A')}")
    else:
        click.echo(click.style("  ✗ No device connected", fg="red"))
        click.echo("    Run: adb devices")

    click.echo(click.style("\nAgent Configuration", fg="cyan", bold=True))
    click.echo("─" * 40)
    click.echo(f"  Mode:       {config.mode.value}")
    click.echo(f"  Model:      {config.ollama.model.value}")
    click.echo(f"  CompText:   {'enabled' if config.agent.use_comptext else 'disabled'}")
    click.echo(f"  Max Steps:  {config.agent.max_steps}")
    click.echo(f"  Debug:      {config.debug}")

    # Check API key
    click.echo(click.style("\nAPI Status", fg="cyan", bold=True))
    click.echo("─" * 40)
    if config.ollama.api_key:
        masked_key = config.ollama.api_key[:8] + "..." + config.ollama.api_key[-4:]
        click.echo(click.style(f"  ✓ API Key: {masked_key}", fg="green"))
    else:
        click.echo(click.style("  ✗ API Key: not set", fg="red"))
        click.echo("    Set OLLAMA_API_KEY environment variable")


async def _check_device(config: MobileAgentConfig) -> tuple[bool, Optional[dict]]:
    """Check device connection status."""
    from .droidrun_wrapper import DroidRunWrapper

    device = DroidRunWrapper(config.adb)
    connected = await device.connect()

    if connected:
        info = await device.get_device_info()
        return True, info
    return False, None


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def config(ctx, as_json: bool):
    """
    Display current configuration.
    """
    cfg: MobileAgentConfig = ctx.obj["config"]

    if as_json:
        config_dict = {
            "mode": cfg.mode.value,
            "debug": cfg.debug,
            "log_level": cfg.log_level,
            "ollama": {
                "api_base": cfg.ollama.api_base,
                "model": cfg.ollama.model.value,
                "timeout": cfg.ollama.timeout,
                "max_tokens": cfg.ollama.max_tokens,
            },
            "adb": {
                "adb_path": cfg.adb.adb_path,
                "device_serial": cfg.adb.device_serial,
                "screenshot_dir": cfg.adb.screenshot_dir,
            },
            "agent": {
                "max_steps": cfg.agent.max_steps,
                "retry_attempts": cfg.agent.retry_attempts,
                "use_comptext": cfg.agent.use_comptext,
                "verify_actions": cfg.agent.verify_actions,
            },
        }
        click.echo(json.dumps(config_dict, indent=2))
    else:
        click.echo(click.style("\nCompText Mobile Agent Configuration", fg="cyan", bold=True))
        click.echo("═" * 50)

        click.echo(click.style("\n[General]", fg="yellow"))
        click.echo(f"  Mode:      {cfg.mode.value}")
        click.echo(f"  Debug:     {cfg.debug}")
        click.echo(f"  Log Level: {cfg.log_level}")

        click.echo(click.style("\n[Ollama]", fg="yellow"))
        click.echo(f"  API Base:   {cfg.ollama.api_base}")
        click.echo(f"  Model:      {cfg.ollama.model.value}")
        click.echo(f"  Timeout:    {cfg.ollama.timeout}s")
        click.echo(f"  Max Tokens: {cfg.ollama.max_tokens}")

        click.echo(click.style("\n[ADB]", fg="yellow"))
        click.echo(f"  ADB Path:       {cfg.adb.adb_path}")
        click.echo(f"  Device Serial:  {cfg.adb.device_serial or 'auto'}")
        click.echo(f"  Screenshot Dir: {cfg.adb.screenshot_dir}")

        click.echo(click.style("\n[Agent]", fg="yellow"))
        click.echo(f"  Max Steps:      {cfg.agent.max_steps}")
        click.echo(f"  Retry Attempts: {cfg.agent.retry_attempts}")
        click.echo(f"  CompText:       {cfg.agent.use_comptext}")
        click.echo(f"  Verify Actions: {cfg.agent.verify_actions}")


@cli.command()
@click.argument("task")
@click.option("--baseline", "-b", is_flag=True, help="Compare with baseline (verbose mode)")
@click.pass_context
def benchmark(ctx, task: str, baseline: bool):
    """
    Benchmark token usage for a task.

    Compares CompText DSL vs verbose prompts.

    Examples:

        comptext-mobile benchmark "Open Chrome"

        comptext-mobile benchmark "Search for weather" --baseline
    """
    config: MobileAgentConfig = ctx.obj["config"]

    click.echo(click.style("\nToken Benchmark", fg="cyan", bold=True))
    click.echo("═" * 50)
    click.echo(f"Task: {task}\n")

    # Run with CompText
    config.agent.use_comptext = True
    click.echo("Running with CompText DSL...")
    comptext_result = asyncio.run(_run_task(config, task))

    click.echo(f"  Tokens: {comptext_result.total_tokens:,}")
    click.echo(f"  Steps:  {comptext_result.step_count}")

    if baseline:
        # Run without CompText
        config.agent.use_comptext = False
        click.echo("\nRunning with verbose prompts (baseline)...")
        baseline_result = asyncio.run(_run_task(config, task))

        click.echo(f"  Tokens: {baseline_result.total_tokens:,}")
        click.echo(f"  Steps:  {baseline_result.step_count}")

        # Calculate reduction
        if baseline_result.total_tokens > 0:
            reduction = (1 - comptext_result.total_tokens / baseline_result.total_tokens) * 100
            click.echo(click.style(f"\n  Token Reduction: {reduction:.1f}%", fg="green", bold=True))
            click.echo(f"  Saved: {baseline_result.total_tokens - comptext_result.total_tokens:,} tokens")


@cli.command()
@click.pass_context
def interactive(ctx):
    """
    Start interactive mode for continuous task execution.

    Type tasks and see results in real-time. Type 'exit' to quit.
    """
    print_banner()
    config: MobileAgentConfig = ctx.obj["config"]
    verbose = ctx.obj["verbose"]

    click.echo(click.style("Interactive Mode", fg="cyan", bold=True))
    click.echo("Type a task and press Enter. Type 'exit' to quit.\n")

    while True:
        try:
            task = click.prompt(click.style("Task", fg="yellow"), type=str)

            if task.lower() in ("exit", "quit", "q"):
                click.echo("Goodbye!")
                break

            if not task.strip():
                continue

            click.echo(click.style("\nExecuting...", fg="cyan"))
            result = asyncio.run(_run_task(config, task))
            print_result(result, verbose)
            click.echo()

        except click.Abort:
            click.echo("\nGoodbye!")
            break
        except Exception as e:
            click.echo(click.style(f"Error: {e}", fg="red"))


@cli.command()
@click.option("--port", "-p", default=9090, type=int, help="Metrics port")
@click.option("--host", default="0.0.0.0", help="Bind host")
@click.pass_context
def metrics(ctx, port: int, host: str):
    """
    Start Prometheus metrics server.

    Exposes metrics at http://host:port/metrics for Prometheus scraping.

    Available metrics:
    - comptext_mobile_tasks_total - Total tasks executed
    - comptext_mobile_task_duration_seconds - Task duration
    - comptext_mobile_tokens_total - Token usage
    - comptext_mobile_steps_total - Steps executed
    - comptext_mobile_device_connected - Device status

    Examples:

        comptext-mobile metrics

        comptext-mobile metrics --port 8080
    """
    try:
        from .prometheus_metrics import start_metrics_server, PrometheusMetrics
    except ImportError:
        click.echo(
            click.style(
                "Prometheus support not available. Install with: pip install prometheus-client",
                fg="red",
            )
        )
        sys.exit(1)

    click.echo(
        click.style(
            """
╔═══════════════════════════════════════════════════════════╗
║       CompText Mobile Agent Prometheus Metrics            ║
╚═══════════════════════════════════════════════════════════╝
""",
            fg="cyan",
        )
    )

    # Initialize metrics
    PrometheusMetrics()

    click.echo(f"Starting metrics server on http://{host}:{port}/metrics")
    click.echo("Press Ctrl+C to stop\n")

    try:
        start_metrics_server(port, host)
        import signal

        signal.pause()
    except KeyboardInterrupt:
        click.echo("\nMetrics server stopped")


@cli.command()
@click.option("--host", "-h", default="localhost", help="Server hostname")
@click.option("--port", "-p", default=8765, type=int, help="Server port")
@click.pass_context
def serve(ctx, host: str, port: int):
    """
    Start WebSocket server for real-time agent communication.

    Enables live updates during task execution via WebSocket.

    Examples:

        comptext-mobile serve

        comptext-mobile serve --host 0.0.0.0 --port 9000

    Connect with: ws://localhost:8765

    Send commands:
        {"command": "run", "task": "Open Chrome"}
        {"command": "screenshot"}
        {"command": "status"}
        {"command": "stop"}
    """
    try:
        from .websocket_server import run_websocket_server
    except ImportError:
        click.echo(
            click.style(
                "WebSocket support not available. Install with: pip install websockets",
                fg="red",
            )
        )
        sys.exit(1)

    config: MobileAgentConfig = ctx.obj["config"]

    click.echo(
        click.style(
            """
╔═══════════════════════════════════════════════════════════╗
║         CompText Mobile Agent WebSocket Server            ║
╚═══════════════════════════════════════════════════════════╝
""",
            fg="cyan",
        )
    )
    click.echo(f"Starting server on ws://{host}:{port}")
    click.echo("Press Ctrl+C to stop\n")

    try:
        asyncio.run(run_websocket_server(host, port, config))
    except KeyboardInterrupt:
        click.echo("\nServer stopped")


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
