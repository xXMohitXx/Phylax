"""
Demo 03: Execution Context

Demonstrates:
- execution() context manager for grouping traces
- Shared execution_id across multiple calls
- Parent-child relationships

Requirements:
- pip install phylax[all]
- GOOGLE_API_KEY environment variable
"""

import os
import sys

from phylax._internal.decorator import trace, expect
from phylax._internal.context import execution
from phylax._internal.adapters.gemini import GeminiAdapter
import phylax


@trace(provider="gemini")
@expect(must_include=["hello", "hi", "greet"])
def step_1_greeting():
    """First step in the execution."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="Say hello briefly.",
        model="gemini-2.5-flash",
    )
    return response


@trace(provider="gemini")
@expect(must_include=["4", "four"])
def step_2_math():
    """Second step - simple math."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="What is 2 + 2? Answer with just the number.",
        model="gemini-2.5-flash",
    )
    return response


@trace(provider="gemini")
@expect(must_include=["yes", "correct", "right"])
def step_3_confirm(answer: str):
    """Third step - confirm the answer."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=f"The answer to 2+2 is: {answer}. Is this correct? Say yes or no.",
        model="gemini-2.5-flash",
    )
    return response


def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        return 1
    
    print("=" * 60)
    print("🧪 DEMO 03: Execution Context")
    print("=" * 60)
    print(f"📦 Phylax version: {phylax.__version__}")
    print()
    
    # Group traces in an execution context
    print("📍 Starting execution context...")
    
    with execution() as exec_id:
        print(f"   Execution ID: {exec_id[:20]}...")
        print()
        
        # Step 1
        print("   Step 1: Greeting")
        result1 = step_1_greeting()
        print(f"   → {result1.text.strip()[:40]}...")
        
        # Step 2
        print("   Step 2: Math")
        result2 = step_2_math()
        print(f"   → {result2.text.strip()[:40]}...")
        
        # Step 3
        print("   Step 3: Confirm")
        result3 = step_3_confirm(result2.text.strip())
        print(f"   → {result3.text.strip()[:40]}...")
    
    print()
    print("✅ All 3 traces share the same execution_id")
    print("   View as graph in UI: phylax server → http://127.0.0.1:8000/ui")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
