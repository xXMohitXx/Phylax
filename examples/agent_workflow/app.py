"""
AI Agent Workflow — Multi-step agent with execution graph tracking.

Demonstrates:
    - execution() context for grouping traces
    - Per-step expectations
    - Agent flow: classify → research → respond

Usage:
    pip install phylax[openai]
    export OPENAI_API_KEY="your-key"
    python app.py
"""
from phylax import trace, expect, execution

# Step 1: Classify user intent
@trace(provider="openai")
@expect(must_include=["intent"], max_latency_ms=2000)
def classify_intent(user_message: str) -> str:
    """Classify the user's intent."""
    # In production: call your LLM
    return f"intent: refund_request — The user wants a refund for their order."

# Step 2: Research relevant information
@trace(provider="openai")
@expect(must_include=["policy"], max_latency_ms=3000)
def research(intent: str) -> str:
    """Look up relevant policies and information."""
    # In production: call your LLM with RAG context
    return (
        "policy: Refunds are available within 30 days of purchase. "
        "Customer must provide order number. Refund processed in 5-7 days."
    )

# Step 3: Generate the response
@trace(provider="openai")
@expect(
    must_include=["refund"],
    must_not_include=["lawsuit", "attorney"],
    max_latency_ms=3000,
    min_tokens=20,
)
def respond(intent: str, research_context: str) -> str:
    """Generate a grounded response using research context."""
    # In production: call your LLM with the research context
    return (
        "I'd be happy to help with your refund! Based on our policy, "
        "refunds are available within 30 days of purchase. Could you "
        "please provide your order number? Once confirmed, your refund "
        "will be processed within 5-7 business days."
    )

if __name__ == "__main__":
    print("=" * 60)
    print("AI Agent Workflow — Phylax Execution Graph Demo")
    print("=" * 60)

    user_message = "I want a refund for my recent order"
    print(f"\n📨 User: {user_message}")

    # Group all steps into one execution context
    with execution() as exec_id:
        print(f"\n🔗 Execution ID: {exec_id}")

        # Step 1
        print("\n[Step 1] Classifying intent...")
        intent = classify_intent(user_message)
        print(f"   → {intent}")

        # Step 2
        print("\n[Step 2] Researching...")
        context = research(intent)
        print(f"   → {context[:60]}...")

        # Step 3
        print("\n[Step 3] Generating response...")
        response = respond(intent, context)
        print(f"   🤖 {response}")

    print("\n" + "=" * 60)
    print("✅ All 3 agent steps passed their contracts.")
    print(f"   Execution graph saved: {exec_id}")
    print("   Run 'phylax server' → visit /ui to see the graph.")
    print("   Run 'phylax check' in CI to enforce all steps.")
