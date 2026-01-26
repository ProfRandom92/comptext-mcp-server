#!/usr/bin/env python3
"""
Mobile Agent Demo Use Cases

Demonstrates the 5 key use cases for the Mobile Agent:
1. App Navigation - "Open Chrome browser"
2. Search Automation - "Search for weather in Chrome"
3. Settings Automation - "Enable Dark Mode in Settings"
4. UI Analysis - "List all clickable elements"
5. Multi-App Workflow - "Check Calendar and screenshot"

Run with: python examples/mobile_agent/demo_use_cases.py
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.comptext_mcp.mobile_agent import MobileAgent, MobileAgentConfig
from src.comptext_mcp.mobile_agent.utils import TokenMetricsCollector


@dataclass
class UseCaseResult:
    """Result of a demo use case."""
    name: str
    task: str
    success: bool
    steps: int
    tokens: int
    duration_ms: float
    error: Optional[str] = None


class DemoRunner:
    """Runner for Mobile Agent demo use cases."""

    # Demo use cases with increasing complexity
    USE_CASES = [
        {
            "name": "App Navigation",
            "task": "Open the Chrome browser",
            "description": "Simple app launch - tests basic device control",
            "difficulty": "Easy",
        },
        {
            "name": "Search Automation",
            "task": "Open Chrome and search for 'weather today'",
            "description": "Multi-step task - app launch + text input + action",
            "difficulty": "Medium",
        },
        {
            "name": "Settings Navigation",
            "task": "Open Settings and navigate to Display settings",
            "description": "Deep navigation - multiple taps through menus",
            "difficulty": "Medium",
        },
        {
            "name": "UI Analysis",
            "task": "Analyze the current screen and list all buttons",
            "description": "UI understanding - element detection and classification",
            "difficulty": "Easy",
        },
        {
            "name": "Multi-App Workflow",
            "task": "Open the Clock app, then go back to Home screen",
            "description": "App switching - tests navigation and home button",
            "difficulty": "Medium",
        },
    ]

    def __init__(self, use_comptext: bool = True):
        """Initialize demo runner."""
        self.use_comptext = use_comptext
        self.metrics = TokenMetricsCollector()
        self.results: list[UseCaseResult] = []

    async def run_all(self, skip_device_check: bool = False) -> list[UseCaseResult]:
        """
        Run all demo use cases.

        Args:
            skip_device_check: Skip device connection check (for testing)

        Returns:
            List of use case results
        """
        print("=" * 60)
        print("  Mobile Agent Demo - Use Cases")
        print("=" * 60)
        print()

        config = MobileAgentConfig.from_env()
        config.agent.use_comptext = self.use_comptext

        print(f"Configuration:")
        print(f"  Mode: {config.mode.value}")
        print(f"  CompText: {'Enabled' if self.use_comptext else 'Disabled'}")
        print(f"  Max Steps: {config.agent.max_steps}")
        print()

        async with MobileAgent(config) as agent:
            # Initialize agent
            print("Initializing agent...")

            if not skip_device_check:
                if not await agent.initialize():
                    print("ERROR: Failed to initialize agent")
                    print("Make sure:")
                    print("  1. ADB is installed and in PATH")
                    print("  2. Device is connected (adb devices)")
                    print("  3. USB debugging is enabled")
                    return []

            print("Agent initialized successfully!")
            print()

            # Run each use case
            for i, use_case in enumerate(self.USE_CASES, 1):
                print("-" * 60)
                print(f"Use Case {i}/{len(self.USE_CASES)}: {use_case['name']}")
                print(f"Task: {use_case['task']}")
                print(f"Difficulty: {use_case['difficulty']}")
                print("-" * 60)

                result = await self._run_use_case(agent, use_case)
                self.results.append(result)

                self._print_result(result)
                print()

                # Wait between use cases
                await asyncio.sleep(2)

        # Print summary
        self._print_summary()

        return self.results

    async def _run_use_case(
        self,
        agent: MobileAgent,
        use_case: dict,
    ) -> UseCaseResult:
        """Run a single use case."""
        start_time = time.time()

        try:
            result = await agent.execute(use_case["task"])

            return UseCaseResult(
                name=use_case["name"],
                task=use_case["task"],
                success=result.success,
                steps=result.step_count,
                tokens=result.total_tokens,
                duration_ms=result.total_duration_ms,
                error=result.error,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return UseCaseResult(
                name=use_case["name"],
                task=use_case["task"],
                success=False,
                steps=0,
                tokens=0,
                duration_ms=duration_ms,
                error=str(e),
            )

    def _print_result(self, result: UseCaseResult):
        """Print use case result."""
        status = "✓ SUCCESS" if result.success else "✗ FAILED"
        print(f"Status: {status}")
        print(f"Steps: {result.steps}")
        print(f"Tokens: {result.tokens}")
        print(f"Duration: {result.duration_ms:.0f}ms")

        if result.error:
            print(f"Error: {result.error}")

    def _print_summary(self):
        """Print summary of all use cases."""
        print("=" * 60)
        print("  Summary")
        print("=" * 60)
        print()

        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        total_tokens = sum(r.tokens for r in self.results)
        total_duration = sum(r.duration_ms for r in self.results)

        print(f"Total Use Cases: {total}")
        print(f"Successful: {successful}/{total} ({100*successful/total:.0f}%)")
        print(f"Total Tokens: {total_tokens}")
        print(f"Total Duration: {total_duration:.0f}ms")
        print()

        # Per use case summary
        print("Per Use Case:")
        print("-" * 60)
        for result in self.results:
            status = "✓" if result.success else "✗"
            print(f"  {status} {result.name}: {result.tokens} tokens, {result.duration_ms:.0f}ms")

        print()

        # CompText impact estimate
        if self.use_comptext:
            baseline_estimate = total_tokens * 5  # ~80% reduction means 5x baseline
            savings = baseline_estimate - total_tokens
            print("CompText Impact (estimated):")
            print(f"  Baseline (no CompText): ~{baseline_estimate} tokens")
            print(f"  With CompText: {total_tokens} tokens")
            print(f"  Savings: ~{savings} tokens ({100*savings/baseline_estimate:.0f}%)")


async def run_single_demo(task: str = "Open Chrome browser"):
    """Run a single demo task."""
    print(f"Running single task: {task}")
    print()

    config = MobileAgentConfig.from_env()

    async with MobileAgent(config) as agent:
        if not await agent.initialize():
            print("Failed to initialize - check device connection")
            return

        result = await agent.execute(task)

        print(f"Success: {result.success}")
        print(f"Steps: {result.step_count}")
        print(f"Tokens: {result.total_tokens}")
        print(f"Duration: {result.total_duration_ms:.0f}ms")

        if result.error:
            print(f"Error: {result.error}")

        print("\nSteps taken:")
        for step in result.steps:
            print(f"  {step.step_number}. {step.action}: {step.reasoning[:50]}...")


async def run_simulation():
    """
    Run simulated demo without device connection.
    Useful for testing the demo structure.
    """
    print("=" * 60)
    print("  Mobile Agent Demo - SIMULATION MODE")
    print("  (No device connection required)")
    print("=" * 60)
    print()

    # Simulated results
    simulated_results = [
        UseCaseResult("App Navigation", "Open Chrome", True, 2, 180, 1500),
        UseCaseResult("Search Automation", "Search weather", True, 5, 420, 4200),
        UseCaseResult("Settings Navigation", "Open Display settings", True, 4, 350, 3100),
        UseCaseResult("UI Analysis", "List all buttons", True, 1, 90, 800),
        UseCaseResult("Multi-App Workflow", "Open Clock, go Home", True, 3, 250, 2300),
    ]

    runner = DemoRunner()

    for result in simulated_results:
        print(f"[SIM] {result.name}: {result.tokens} tokens, {result.duration_ms:.0f}ms")
        runner.results.append(result)

    print()
    runner._print_summary()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Mobile Agent Demo Use Cases")
    parser.add_argument("--task", help="Run single task instead of all demos")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")
    parser.add_argument("--no-comptext", action="store_true", help="Disable CompText optimization")

    args = parser.parse_args()

    if args.simulate:
        asyncio.run(run_simulation())
    elif args.task:
        asyncio.run(run_single_demo(args.task))
    else:
        runner = DemoRunner(use_comptext=not args.no_comptext)
        asyncio.run(runner.run_all())


if __name__ == "__main__":
    main()
