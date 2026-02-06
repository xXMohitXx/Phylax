"""
Demo 02: Expectation Rules

Demonstrates all 4 @expect validation rules:
1. must_include - Required substrings
2. must_not_include - Forbidden substrings
3. max_latency_ms - Maximum response time
4. min_tokens - Minimum token count

Requirements:
- pip install phylax[all]
- GOOGLE_API_KEY environment variable
"""

import os
import sys

from phylax._internal.decorator import trace, expect
from phylax._internal.adapters.gemini import GeminiAdapter
import phylax


# Rule 1: must_include
@trace(provider="gemini")
@expect(must_include=["4", "four"])
def math_answer():
    """Response must include "4" or "four"."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="What is 2 + 2? Answer with the number.",
        model="gemini-2.5-flash",
    )
    return response


# Rule 2: must_not_include
@trace(provider="gemini")
@expect(must_not_include=["sorry", "cannot", "error"])
def helpful_response():
    """Response must NOT include apology phrases."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="Tell me a fun fact about Python programming.",
        model="gemini-2.5-flash",
    )
    return response


# Rule 3: max_latency_ms
@trace(provider="gemini")
@expect(max_latency_ms=10000)
def fast_response():
    """Response must complete within 10 seconds."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="Say 'quick!' in one word.",
        model="gemini-2.5-flash",
    )
    return response


# Rule 4: Combined rules
@trace(provider="gemini")
@expect(
    must_include=["python"],
    must_not_include=["error", "sorry"],
    max_latency_ms=15000,
)
def combined_rules():
    """Multiple expectations combined."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="What is Python? Answer briefly.",
        model="gemini-2.5-flash",
    )
    return response


def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        return 1
    
    print("=" * 60)
    print("🧪 DEMO 02: Expectation Rules")
    print("=" * 60)
    print(f"📦 Phylax version: {phylax.__version__}")
    print()
    
    # Test each rule
    tests = [
        ("must_include", math_answer),
        ("must_not_include", helpful_response),
        ("max_latency_ms", fast_response),
        ("combined rules", combined_rules),
    ]
    
    for name, func in tests:
        print(f"📍 Testing: {name}")
        try:
            result = func()
            print(f"   ✅ {result.text.strip()[:50]}...")
        except Exception as e:
            print(f"   ❌ {e}")
        print()
    
    print("📝 All traces created with verdicts")
    print("   View in UI: phylax server → http://127.0.0.1:8000/ui")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
