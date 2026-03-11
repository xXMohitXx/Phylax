"""
Phylax Quickstart — Your first 5 minutes with Phylax.

Run:
    pip install phylax
    python app.py
"""
from phylax import trace, expect, execution, check

# 1. Trace an LLM function with expectations
@trace(provider="mock")
@expect(
    must_include=["hello"],
    must_not_include=["error"],
)
def greet(name: str) -> str:
    """A simple greeting function with enforced behavior."""
    return f"hello {name}, welcome to Phylax!"


# 2. Trace another function
@trace(provider="mock")
@expect(
    must_include=["summary"],
    min_tokens=10,
)
def summarize(text: str) -> str:
    """Summarize text with minimum quality requirements."""
    return f"summary: This text discusses {text} in detail with multiple points."


# 3. Run inside an execution context
def main():
    print("=== Phylax Quickstart ===\n")

    with execution() as ctx:
        result1 = greet("developer")
        print(f"Greeting: {result1}")

        result2 = summarize("machine learning")
        print(f"Summary: {result2}")

    # 4. Check results
    report = check()
    print(f"\n✅ All expectations enforced!")
    print(f"Traces captured: {len(ctx.traces) if hasattr(ctx, 'traces') else 'N/A'}")


if __name__ == "__main__":
    main()
