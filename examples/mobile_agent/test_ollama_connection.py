#!/usr/bin/env python3
"""
Test Ollama Cloud Connection

Verifies that the Ollama Cloud API is accessible and working.
Run with: python examples/mobile_agent/test_ollama_connection.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env.mobile")


async def test_connection():
    """Test Ollama Cloud API connection."""
    print("=" * 60)
    print("  Ollama Cloud Connection Test")
    print("=" * 60)
    print()

    api_key = os.getenv("OLLAMA_API_KEY", "")
    api_base = os.getenv("OLLAMA_API_BASE", "https://api.ollama.com")

    print(f"API Base: {api_base}")
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT SET")
    print()

    if not api_key:
        print("ERROR: OLLAMA_API_KEY not set in environment")
        print("Set it in .env.mobile or export OLLAMA_API_KEY=...")
        return False

    try:
        import httpx

        print("Testing connection...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test models endpoint
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # Try a simple chat completion
            response = await client.post(
                f"{api_base}/v1/chat/completions",
                headers=headers,
                json={
                    "model": "qwen2.5:7b",  # Small model for testing
                    "messages": [
                        {"role": "user", "content": "Say 'Hello' in one word."}
                    ],
                    "max_tokens": 10,
                },
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})

                print("✓ Connection successful!")
                print()
                print(f"Response: {content}")
                print(f"Tokens used: {usage.get('total_tokens', 'N/A')}")
                print()
                return True

            elif response.status_code == 401:
                print("✗ Authentication failed - check API key")
                print(f"Response: {response.text}")
                return False

            elif response.status_code == 404:
                print("✗ Model not found - trying different model...")
                # Try with a different model name
                response = await client.post(
                    f"{api_base}/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "llama3.2:3b",
                        "messages": [
                            {"role": "user", "content": "Say 'Hello' in one word."}
                        ],
                        "max_tokens": 10,
                    },
                )

                if response.status_code == 200:
                    print("✓ Connection successful with llama3.2:3b!")
                    return True
                else:
                    print(f"✗ Failed with status {response.status_code}")
                    print(f"Response: {response.text[:500]}")
                    return False

            else:
                print(f"✗ Unexpected status: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False

    except httpx.ConnectError as e:
        print(f"✗ Connection error: {e}")
        print("Check your internet connection and API endpoint")
        return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def list_available_models():
    """List available models on Ollama Cloud."""
    api_key = os.getenv("OLLAMA_API_KEY", "")
    api_base = os.getenv("OLLAMA_API_BASE", "https://api.ollama.com")

    if not api_key:
        return

    try:
        import httpx

        print("Fetching available models...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {api_key}"}

            response = await client.get(
                f"{api_base}/v1/models",
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                print(f"\nAvailable models ({len(models)}):")
                for model in models[:10]:
                    print(f"  - {model.get('id', 'unknown')}")
                if len(models) > 10:
                    print(f"  ... and {len(models) - 10} more")
            else:
                print(f"Could not fetch models: {response.status_code}")

    except Exception as e:
        print(f"Could not list models: {e}")


def main():
    """Main entry point."""
    success = asyncio.run(test_connection())

    if success:
        asyncio.run(list_available_models())
        print()
        print("=" * 60)
        print("  Setup Complete - Ready to use Mobile Agent!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Connect Android device: adb devices")
        print("  2. Run demo: python examples/mobile_agent/demo_use_cases.py --simulate")
        print("  3. Run with device: python examples/mobile_agent/demo_use_cases.py")
    else:
        print()
        print("Please fix the connection issues and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
