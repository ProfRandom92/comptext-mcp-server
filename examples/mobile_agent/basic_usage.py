#!/usr/bin/env python3
"""
Basic Mobile Agent Usage Example

Demonstrates simple Android automation tasks using CompText Mobile Agent.
"""

import asyncio
import logging

from comptext_mcp.mobile_agent import MobileAgent, MobileAgentConfig
from comptext_mcp.mobile_agent.config import AgentMode
from comptext_mcp.mobile_agent.utils import setup_mobile_logging

# Setup logging
setup_mobile_logging(level="INFO")
logger = logging.getLogger(__name__)


async def example_open_chrome():
    """Example: Open Chrome browser."""
    print("\n" + "=" * 50)
    print("Example 1: Open Chrome")
    print("=" * 50)

    async with MobileAgent() as agent:
        if not await agent.initialize():
            print("Failed to initialize agent")
            return

        result = await agent.execute("Open Chrome browser")

        print(f"\nResult: {'Success' if result.success else 'Failed'}")
        print(f"Steps: {result.step_count}")
        print(f"Tokens: {result.total_tokens}")
        print(f"Duration: {result.total_duration_ms:.0f}ms")

        if result.error:
            print(f"Error: {result.error}")


async def example_search_weather():
    """Example: Open Chrome and search for weather."""
    print("\n" + "=" * 50)
    print("Example 2: Search for Weather")
    print("=" * 50)

    async with MobileAgent() as agent:
        if not await agent.initialize():
            print("Failed to initialize agent")
            return

        result = await agent.execute(
            "Open Chrome, search for 'weather today', and wait for results"
        )

        print(f"\nResult: {'Success' if result.success else 'Failed'}")
        print(f"Steps: {result.step_count}")
        print(f"Tokens: {result.total_tokens}")
        print(f"Duration: {result.total_duration_ms:.0f}ms")

        for step in result.steps:
            status = "OK" if step.result and step.result.success else "FAIL"
            print(f"  Step {step.step_number}: [{status}] {step.action}")


async def example_navigate_settings():
    """Example: Navigate to Settings > Display."""
    print("\n" + "=" * 50)
    print("Example 3: Navigate to Display Settings")
    print("=" * 50)

    async with MobileAgent() as agent:
        if not await agent.initialize():
            print("Failed to initialize agent")
            return

        result = await agent.execute(
            "Open Settings app, navigate to Display settings"
        )

        print(f"\nResult: {'Success' if result.success else 'Failed'}")
        print(f"Steps: {result.step_count}")
        print(f"Tokens: {result.total_tokens}")

        for step in result.steps:
            print(f"  Step {step.step_number}: {step.reasoning[:50]}...")


async def example_with_custom_config():
    """Example: Using custom configuration."""
    print("\n" + "=" * 50)
    print("Example 4: Custom Configuration")
    print("=" * 50)

    config = MobileAgentConfig.from_env()
    config.mode = AgentMode.CLOUD
    config.agent.max_steps = 5
    config.agent.use_comptext = True
    config.debug = True

    async with MobileAgent(config) as agent:
        if not await agent.initialize():
            print("Failed to initialize agent")
            return

        result = await agent.execute("Take a screenshot")

        print(f"\nResult: {'Success' if result.success else 'Failed'}")
        print(f"Config: mode={config.mode.value}, comptext={config.agent.use_comptext}")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("CompText Mobile Agent - Basic Usage Examples")
    print("=" * 60)
    print("\nMake sure you have:")
    print("  1. ADB connected to a device/emulator")
    print("  2. OLLAMA_API_KEY set (for cloud mode)")
    print("  3. Device screen unlocked")

    try:
        await example_open_chrome()
        await example_search_weather()
        await example_navigate_settings()
        await example_with_custom_config()

    except Exception as e:
        logger.exception(f"Example failed: {e}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
