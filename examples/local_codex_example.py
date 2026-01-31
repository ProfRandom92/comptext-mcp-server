#!/usr/bin/env python3
"""
Example: Using CompText MCP Server with Local JSON

This example demonstrates how to use the local JSON codex client
instead of the Notion API for faster, offline access.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Set data source to local
os.environ["COMPTEXT_DATA_SOURCE"] = "local"
os.environ["COMPTEXT_CODEX_PATH"] = "data/codex.json"

from comptext_mcp.local_codex_client import (
    get_all_modules,
    search_codex,
    get_module_by_name,
    get_modules_by_tag,
    get_modules_by_type,
    get_page_content,
)


def main():
    print("=" * 70)
    print("CompText MCP Server - Local JSON Example")
    print("=" * 70)
    
    # 1. List all modules
    print("\n1. Loading all modules...")
    modules = get_all_modules()
    print(f"   ✓ Loaded {len(modules)} modules")
    
    # Group by module category
    by_category = {}
    for module in modules:
        category = module["modul"]
        by_category.setdefault(category, []).append(module)
    
    print("\n   Module categories:")
    for category, items in sorted(by_category.items()):
        print(f"   - {category}: {len(items)} entries")
    
    # 2. Search for specific topics
    print("\n2. Searching for 'Code'...")
    results = search_codex("Code", max_results=5)
    print(f"   ✓ Found {len(results)} results:")
    for result in results:
        print(f"   - {result['titel']} ({result['modul']})")
    
    # 3. Get modules by name
    print("\n3. Getting modules for 'Modul B: Programmierung'...")
    b_modules = get_module_by_name("Modul B: Programmierung")
    print(f"   ✓ Found {len(b_modules)} entries:")
    for module in b_modules:
        print(f"   - {module['titel']}")
    
    # 4. Filter by tag
    print("\n4. Filtering by tag 'Core'...")
    core_modules = get_modules_by_tag("Core")
    print(f"   ✓ Found {len(core_modules)} Core modules")
    
    # 5. Filter by type
    print("\n5. Filtering by type 'Dokumentation'...")
    doc_modules = get_modules_by_type("Dokumentation")
    print(f"   ✓ Found {len(doc_modules)} Documentation entries")
    
    # 6. Get full content
    print("\n6. Getting full content of first module...")
    if modules:
        page_id = modules[0]["id"]
        content = get_page_content(page_id)
        print(f"   ✓ Loaded content ({len(content)} characters)")
        print(f"\n   Preview:")
        print("   " + "\n   ".join(content[:200].split("\n")))
        if len(content) > 200:
            print("   ...")
    
    print("\n" + "=" * 70)
    print("✓ All examples completed successfully!")
    print("=" * 70)
    print("\nBenefits of Local JSON:")
    print("  • No API token required")
    print("  • Offline access")
    print("  • Faster response times (<10ms vs ~100-500ms)")
    print("  • No rate limits")
    print("  • Easy to version control with Git")
    print("\nTo use Notion instead, set:")
    print("  export COMPTEXT_DATA_SOURCE=notion")
    print("  export NOTION_API_TOKEN=your_token")


if __name__ == "__main__":
    main()
