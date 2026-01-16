#!/usr/bin/env python
"""Test script for YAML-based CompText MCP Server"""
import sys
sys.path.insert(0, 'src')

from comptext_mcp.yaml_client import (
    get_all_modules,
    get_module_by_name,
    get_page_content,
    search_codex,
    get_statistics,
    get_modules_by_tag,
    get_modules_by_type
)
from comptext_mcp.compiler.nl_to_comptext import compile_nl_to_comptext

def test_yaml_client():
    """Test YAML client functionality"""
    print("=" * 60)
    print("YAML CLIENT TESTS")
    print("=" * 60)

    # Test 1: Get all modules
    print("\n[1] Testing get_all_modules...")
    modules = get_all_modules()
    print(f"✓ Loaded {len(modules)} modules")
    assert len(modules) == 13, f"Expected 13 modules, got {len(modules)}"

    # Test 2: Get specific module
    print("\n[2] Testing get_module_by_name...")
    module_h = get_module_by_name('H')
    print(f"✓ Module H: {module_h['name']}")
    print(f"  Commands: {len(module_h.get('commands', []))}")
    assert module_h['id'] == 'H'
    assert len(module_h.get('commands', [])) > 0

    # Test 3: Get command content
    print("\n[3] Testing get_page_content...")
    cmd_id = module_h['commands'][0]['id']
    content = get_page_content(cmd_id)
    print(f"✓ Content for {cmd_id}:")
    print(f"  {content[:100]}...")
    assert len(content) > 0

    # Test 4: Search
    print("\n[4] Testing search_codex...")
    results = search_codex('security', max_results=5)
    print(f"✓ Search 'security': {len(results)} results")
    for r in results[:3]:
        print(f"  - {r['id']}: {r.get('description', r.get('name', ''))[:50]}")
    assert len(results) > 0

    # Test 5: Statistics
    print("\n[5] Testing get_statistics...")
    stats = get_statistics()
    print(f"✓ Statistics:")
    print(f"  Modules: {stats['total_modules']}")
    print(f"  Commands: {stats['total_commands']}")
    print(f"  Types: {stats['module_types']}")
    assert stats['total_modules'] == 13

    # Test 6: By tag
    print("\n[6] Testing get_modules_by_tag...")
    security_modules = get_modules_by_tag('Security')
    print(f"✓ Modules with 'Security' tag: {len(security_modules)}")
    for m in security_modules:
        print(f"  - {m['id']}: {m['name']}")

    # Test 7: By type
    print("\n[7] Testing get_modules_by_type...")
    dev_modules = get_modules_by_type('Development')
    print(f"✓ Modules of type 'Development': {len(dev_modules)}")

    print("\n" + "=" * 60)
    print("YAML CLIENT: ALL TESTS PASSED ✓")
    print("=" * 60)


def test_compiler():
    """Test compiler with YAML backend"""
    print("\n" + "=" * 60)
    print("COMPILER TESTS")
    print("=" * 60)

    test_cases = [
        ("Review code for security issues", "dev"),
        ("Create a React dashboard", "dev"),
        ("Deploy to Kubernetes", "exec"),
        ("Run security scan", "audit"),
    ]

    for text, audience in test_cases:
        print(f"\n[TEST] '{text}' (audience: {audience})")
        result = compile_nl_to_comptext(text, audience, 'bundle_only', 'dsl_plus_confidence')
        print(f"Result:\n{result}")
        print("-" * 60)

    print("\n" + "=" * 60)
    print("COMPILER: ALL TESTS COMPLETED ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_yaml_client()
        test_compiler()
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓✓✓")
        print("YAML migration successful!")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
