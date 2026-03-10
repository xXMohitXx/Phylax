"""
AI Summarizer — Phylax enforces latency and quality contracts.

Rules:
    - Summary MUST complete within 2 seconds
    - Summary MUST be at least 50 tokens
    - Summary MUST NOT contain hedging language

Usage:
    pip install phylax[openai]
    export OPENAI_API_KEY="your-key"
    python app.py
"""
from phylax import trace, expect

@trace(provider="openai")
@expect(
    max_latency_ms=2000,
    min_tokens=50,
    must_not_include=["I think", "maybe", "perhaps"],
)
def summarize(article: str) -> str:
    """Summarize an article with enforced quality contracts."""
    # In production, this calls your LLM:
    #   from phylax import OpenAIAdapter
    #   adapter = OpenAIAdapter()
    #   response, trace = adapter.generate(
    #       prompt=f"Summarize this article:\n\n{article}"
    #   )
    #   return response
    #
    # For this demo, we simulate:
    return (
        "The article discusses the growing importance of automated testing "
        "for AI systems. As organizations deploy large language models in "
        "production, they face challenges with output consistency across "
        "model versions. The author argues that deterministic contract "
        "enforcement — rather than subjective evaluation — is the most "
        "reliable approach to preventing regressions. Key recommendations "
        "include capturing baseline outputs, defining explicit expectations, "
        "and integrating checks into CI/CD pipelines."
    )

if __name__ == "__main__":
    article = """
    AI systems are increasingly deployed in production, but testing them
    remains a challenge. Unlike traditional software, LLM outputs can change
    unpredictably across model versions. This article explores how
    deterministic contract enforcement can solve the regression problem.
    """

    print("=" * 60)
    print("AI Summarizer — Phylax Quality Enforcement")
    print("=" * 60)

    print(f"\n📄 Article: {article.strip()[:80]}...")
    summary = summarize(article)
    print(f"\n📝 Summary: {summary}")

    print("\n" + "=" * 60)
    print("✅ Summary passed all quality contracts.")
    print("   - Completed within 2s latency limit")
    print("   - Met minimum 50-token threshold")
    print("   - No hedging language detected")
