"""
Demo 05: Golden Workflow

Demonstrates the complete CI workflow:
1. Create traces with expectations
2. Bless a trace as golden reference
3. Run phylax check for regressions

Requirements:
- pip install phylax[all]
- GOOGLE_API_KEY environment variable

Note: This demo shows the commands, not full automation.
"""

import os
import sys

from phylax._internal.decorator import trace, expect
from phylax._internal.adapters.gemini import GeminiAdapter
import phylax


@trace(provider="gemini")
@expect(must_include=["python"], max_latency_ms=10000)
def describe_python():
    """A traced function that describes Python."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt="What is Python programming language? One sentence.",
        model="gemini-2.5-flash",
    )
    return response


def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        return 1
    
    print("=" * 60)
    print("🧪 DEMO 05: Golden Workflow")
    print("=" * 60)
    print(f"📦 Phylax version: {phylax.__version__}")
    print()
    
    # Step 1: Create a trace
    print("📍 Step 1: Create a trace with expectations")
    result = describe_python()
    print(f"   Response: {result.text.strip()[:60]}...")
    print()
    
    # Step 2: Instructions to bless
    print("📍 Step 2: Bless the trace as golden")
    print("   Run these commands:")
    print()
    print("   # List traces to find the ID")
    print("   phylax list")
    print()
    print("   # Bless the trace")
    print("   phylax bless <trace_id> --yes")
    print()
    
    # Step 3: Instructions to check
    print("📍 Step 3: Run regression check (CI command)")
    print("   phylax check")
    print()
    print("   Exit codes:")
    print("   - 0: All golden traces pass")
    print("   - 1: Regression detected")
    print()
    
    # CI integration example
    print("📍 GitHub Actions integration:")
    print("""
    # .github/workflows/phylax.yml
    - run: phylax check
      env:
        GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
    """)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
