"""
Demo 01: Basic Trace with Expectations

Demonstrates:
- @trace decorator for LLM call tracing
- @expect decorator for validation rules
- Basic PASS/FAIL verdict

Requirements:
- pip install phylax[all]
- GOOGLE_API_KEY environment variable
"""

import os
import sys

# Ensure phylax is importable
from phylax._internal.decorator import trace, expect
from phylax._internal.adapters.gemini import GeminiAdapter
import phylax


@trace(provider="gemini")
@expect(must_include=["hello", "hi"], max_latency_ms=5000)
def greet_user(name: str):
    """
    A traced LLM call with expectations.
    
    Expectations:
    - Response must include "hello" or "hi"
    - Must complete within 5000ms
    """
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=f"Say hello to {name} in a friendly way.",
        model="gemini-2.5-flash",
    )
    return response


def main():
    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        print('Set it with: $env:GOOGLE_API_KEY = "your-key"')
        return 1
    
    print("=" * 60)
    print("🧪 DEMO 01: Basic Trace with Expectations")
    print("=" * 60)
    print(f"📦 Phylax version: {phylax.__version__}")
    print()
    
    # Run the traced function
    print("📍 Calling greet_user('World')...")
    result = greet_user("World")
    
    print(f"✅ Response: {result.text.strip()[:100]}")
    print()
    print("📝 Trace created with verdict (PASS/FAIL)")
    print("   View in UI: phylax server → http://127.0.0.1:8000/ui")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
