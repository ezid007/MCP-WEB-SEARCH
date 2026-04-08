#!/usr/bin/env python3
"""Final Test Script for MCP Web Search"""

import sys
sys.path.insert(0, '.')

from main import perform_web_search

print("Testing perform_web_search (with fallback)...")
print("=" * 50)

results = perform_web_search("Python programming tutorial", max_results=3)

if results and "error" in results[0]:
    print(f"Error: {results[0]['error']}")
else:
    print(f"Success! Found {len(results)} results:")
    for result in results:
        print(f"{result['rank']}. {result['title']}")
        print(f"   URL: {result['url']}")
        print()

print("=" * 50)
print("Test completed!")
