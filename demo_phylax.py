"""
Phylax Demo - Testing the PyPI package with Gemini 2.5 Flash

Demonstrates:
- phylax installed from PyPI
- @trace decorator with GeminiAdapter
- execution() context for grouping traces
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()   
# Add project root to path for local testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import phylax
from phylax import trace, execution
from phylax._internal.adapters.gemini import GeminiAdapter


@trace(provider="gemini")
def step_1_greeting():
    """First step: Get a greeting."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="Say hello in a friendly way, in 5 words or less.",
        model="gemini-2.5-flash",
    )
    return response


@trace(provider="gemini")
def step_2_math():
    """Second step: Simple math."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="What is 2 + 2? Answer with just the number.",
        model="gemini-2.5-flash",
    )
    return response


@trace(provider="gemini")
def step_3_confirm(answer):
    """Third step: Confirm the answer."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=f"The answer was: {answer}. Is this correct? Yes or No.",
        model="gemini-2.5-flash",
    )
    return response


def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set!")
        print('Set it with: $env:GOOGLE_API_KEY = "your-key"')
        return 1
    
    print("=" * 60)
    print("🧪 PHYLAX DEMO - Testing PyPI Package")
    print("=" * 60)
    print()
    print(f"📦 Phylax version: {phylax.__version__}")
    print()
    
    # Test 1: Single trace
    print("📍 Test 1: Single traced call")
    print("-" * 40)
    greeting = step_1_greeting()
    print(f"✅ Result: {greeting.text.strip()[:50]}")
    print()
    
    # Test 2: Execution context - groups traces together
    print("📍 Test 2: Execution context (grouped traces)")
    print("-" * 40)
    
    with execution() as exec_id:
        print(f"   Execution ID: {exec_id[:20]}...")
        
        math_result = step_2_math()
        print(f"   Step 1: {math_result.text.strip()[:30]}")
        
        confirm = step_3_confirm(math_result.text.strip())
        print(f"   Step 2: {confirm.text.strip()[:30]}")
    
    print()
    print("=" * 60)
    print("🎉 DEMO COMPLETE - Phylax v1.0.0 from PyPI!")
    print("=" * 60)
    print()
    print("📦 Install: pip install phylax")
    print("📝 Import: from phylax import trace, execution")
    print("🌐 UI: Start server with 'phylax server' then open http://127.0.0.1:8000/ui")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
