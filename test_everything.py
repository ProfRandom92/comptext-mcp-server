#!/usr/bin/env python3
"""Comprehensive test script to verify all functionality works correctly."""

import sys


def test_imports():
    """Test that all modules import correctly."""
    print("📦 Testing imports...")
    try:
        from comptext_mcp import server
        from comptext_mcp.compiler import compile_nl_to_comptext, load_registry
        from comptext_mcp.yaml_client import get_all_modules, get_statistics, search_codex

        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_registry():
    """Test registry loading."""
    print("\n📚 Testing registry...")
    try:
        from comptext_mcp.compiler import load_registry

        reg = load_registry()
        print(f"  ✅ Registry loaded: {len(reg.bundles)} bundles, {len(reg.profiles)} profiles")
        return True
    except Exception as e:
        print(f"  ❌ Registry loading failed: {e}")
        return False


def test_compiler():
    """Test NL to CompText compilation."""
    print("\n🔧 Testing compiler...")
    try:
        from comptext_mcp.compiler import compile_nl_to_comptext

        test_cases = [
            "Review this code for best practices",
            "Find security vulnerabilities",
            "Generate API documentation",
            "Optimize performance",
        ]

        for test_input in test_cases:
            result = compile_nl_to_comptext(test_input)
            if "dsl:" in result and "confidence:" in result:
                print(f"  ✅ Compiled: '{test_input[:30]}...'")
            else:
                print(f"  ⚠️  Unexpected output for: '{test_input}'")
                return False

        return True
    except Exception as e:
        print(f"  ❌ Compiler failed: {e}")
        return False


def test_yaml_client():
    """Test YAML client functions."""
    print("\n📄 Testing YAML client...")
    try:
        from comptext_mcp.yaml_client import get_all_modules, get_statistics

        # Test get_all_modules
        modules = get_all_modules()
        print(f"  ✅ get_all_modules: {len(modules)} modules loaded")

        # Test get_statistics
        stats = get_statistics()
        print(f"  ✅ get_statistics: {stats['total_modules']} modules, {stats['total_commands']} commands")

        return True
    except Exception as e:
        print(f"  ❌ YAML client failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 CompText MCP Server - Comprehensive Functionality Test")
    print("=" * 60)

    results = []
    results.append(("Imports", test_imports()))
    results.append(("Registry", test_registry()))
    results.append(("Compiler", test_compiler()))
    results.append(("YAML Client", test_yaml_client()))

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:20s} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed! The system is fully functional and ready to use!")
        print("\n📝 Next steps:")
        print("  1. Run the MCP server: python -m comptext_mcp.server")
        print("  2. Or use the REST API: python mcp_server.py")
        print("  3. See CLAUDE_SETUP.md for Claude Desktop integration")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
