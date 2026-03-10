"""
Phylax Quickstart — Trace and enforce LLM behavior in 10 lines.

Usage:
    pip install phylax[openai]
    export OPENAI_API_KEY="your-key"
    python app.py
"""
from phylax import trace, expect

@trace(provider="openai")
@expect(must_include=["hello"], max_latency_ms=5000)
def greet(name: str) -> str:
    """A simple LLM call with enforced expectations."""
    # In a real app, this would call OpenAI/Gemini/etc.
    # For this demo, we simulate a response.
    return f"hello {name}, how can I help you today?"

if __name__ == "__main__":
    result = greet("World")
    print(f"Response: {result}")
    print()
    print("✅ Trace captured. Run 'phylax list' to see it.")
    print("   Run 'phylax check' in CI to enforce contracts.")
