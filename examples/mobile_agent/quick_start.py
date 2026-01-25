#!/usr/bin/env python3
"""
Quick Start - Mobile Agent First Test

Simple script to verify your mobile agent setup is working.
Run this after completing the setup steps.
"""

import asyncio
import sys


async def check_adb():
    """Check if ADB is working."""
    print("\n1. Checking ADB connection...")

    try:
        proc = await asyncio.create_subprocess_exec(
            "adb", "devices",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        output = stdout.decode()
        lines = output.strip().split("\n")[1:]  # Skip header
        devices = [l for l in lines if "\tdevice" in l]

        if devices:
            print(f"   Found {len(devices)} device(s)")
            for d in devices:
                print(f"     - {d.split()[0]}")
            return True
        else:
            print("   No devices found!")
            print("   Tips:")
            print("   - Connect your phone via USB with USB debugging enabled")
            print("   - Or start an Android emulator")
            return False

    except FileNotFoundError:
        print("   ADB not found! Install Android SDK Platform Tools")
        return False


async def check_screen():
    """Take a test screenshot."""
    print("\n2. Testing screenshot capture...")

    try:
        proc = await asyncio.create_subprocess_exec(
            "adb", "shell", "screencap", "-p", "/sdcard/test_screenshot.png",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        if proc.returncode == 0:
            print("   Screenshot captured successfully")
            # Clean up
            await asyncio.create_subprocess_exec(
                "adb", "shell", "rm", "/sdcard/test_screenshot.png"
            )
            return True
        else:
            print("   Screenshot failed")
            return False

    except Exception as e:
        print(f"   Error: {e}")
        return False


async def check_ui_dump():
    """Test UI hierarchy dump."""
    print("\n3. Testing UI hierarchy dump...")

    try:
        proc = await asyncio.create_subprocess_exec(
            "adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0 or b"UI hierchary" in stdout:
            print("   UI dump successful")
            # Clean up
            await asyncio.create_subprocess_exec(
                "adb", "shell", "rm", "/sdcard/ui_dump.xml"
            )
            return True
        else:
            print("   UI dump failed")
            print(f"   {stderr.decode()}")
            return False

    except Exception as e:
        print(f"   Error: {e}")
        return False


async def check_ollama():
    """Check Ollama connectivity."""
    import os

    print("\n4. Checking Ollama configuration...")

    api_key = os.getenv("OLLAMA_API_KEY")
    if api_key:
        print("   OLLAMA_API_KEY is set")
        return True
    else:
        print("   OLLAMA_API_KEY not set")
        print("   For cloud mode, set: export OLLAMA_API_KEY=your_key")
        print("   For local mode, ensure Ollama is running: ollama serve")

        # Check if local Ollama is running
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://localhost:11434/api/tags", timeout=2)
                if resp.status_code == 200:
                    print("   Local Ollama is running")
                    return True
        except Exception:
            pass

        return False


async def run_simple_test():
    """Run a simple agent test."""
    print("\n5. Running simple agent test...")

    try:
        from comptext_mcp.mobile_agent import MobileAgent

        async with MobileAgent() as agent:
            if not await agent.initialize():
                print("   Agent initialization failed")
                return False

            print("   Agent initialized, getting screen state...")

            screen = await agent.device.get_screen_state(include_screenshot=False)
            print(f"   Current app: {screen.package}")
            print(f"   Elements found: {len(screen.elements)}")
            print(f"   Clickable elements: {len(screen.clickable_elements)}")

            return True

    except ImportError as e:
        print(f"   Import error: {e}")
        print("   Run: pip install -e .")
        return False
    except Exception as e:
        print(f"   Test failed: {e}")
        return False


async def main():
    """Run all checks."""
    print("=" * 60)
    print("CompText Mobile Agent - Quick Start Check")
    print("=" * 60)

    results = {}

    results["adb"] = await check_adb()
    if results["adb"]:
        results["screen"] = await check_screen()
        results["ui_dump"] = await check_ui_dump()
    else:
        results["screen"] = False
        results["ui_dump"] = False

    results["ollama"] = await check_ollama()

    if all(results.values()):
        results["agent"] = await run_simple_test()
    else:
        results["agent"] = False
        print("\n5. Skipping agent test (prerequisites not met)")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {check.upper():<15} [{status}]")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All checks passed! You're ready to use the Mobile Agent.")
        print("\nNext steps:")
        print("  python examples/mobile_agent/basic_usage.py")
    else:
        print("Some checks failed. Please fix the issues above.")
        print("\nSetup guide:")
        print("  1. Install ADB: https://developer.android.com/tools/adb")
        print("  2. Enable USB debugging on your device")
        print("  3. Set OLLAMA_API_KEY or run local Ollama")
        print("  4. Run: pip install -e .")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
