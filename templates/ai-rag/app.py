"""
AI RAG Pipeline Template — Ready-to-use Phylax starter for RAG.

This template includes:
    - RAG pipeline with retrieval + generation steps
    - Grounding enforcement (response must reference retrieved context)
    - GitHub Actions CI configuration

Usage:
    1. Copy this template to your project
    2. Set your API key
    3. Run: python app.py
    4. CI: phylax check
"""
from phylax import trace, expect, execution

@trace(provider="openai")
@expect(must_include=["document"], max_latency_ms=2000)
def retrieve(query: str) -> str:
    """Retrieve relevant documents for the query."""
    # In production: vector search, database lookup, etc.
    return (
        "document: Phylax is a CI-native regression enforcement tool for "
        "LLM outputs. It captures traces, evaluates expectations, and "
        "fails builds when contracts regress."
    )

@trace(provider="openai")
@expect(
    must_include=["Phylax"],          # Must reference retrieved content
    must_not_include=["I don't know"], # Must not hallucinate
    max_latency_ms=5000,
    min_tokens=30,
)
def generate(query: str, context: str) -> str:
    """Generate a grounded response using retrieved context."""
    # In production: call LLM with context
    return (
        "Based on the documentation, Phylax is a CI-native regression "
        "enforcement tool for LLM outputs. It works by capturing traces "
        "of LLM calls, evaluating them against declared expectations, "
        "and failing CI builds when contracts are violated."
    )

def rag_pipeline(query: str) -> str:
    """Run the full RAG pipeline with execution tracking."""
    with execution() as exec_id:
        context = retrieve(query)
        response = generate(query, context)
        return response

if __name__ == "__main__":
    answer = rag_pipeline("What is Phylax?")
    print(f"Answer: {answer}")
    print("\n✅ Run 'phylax check' to enforce grounding in CI.")
