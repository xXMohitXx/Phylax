"""
AI Support Bot — Phylax enforces response safety contracts.

Rules:
    - Response MUST mention "refund"
    - Response MUST NOT mention "lawsuit"
    - Response MUST complete within 3 seconds

Usage:
    pip install phylax[openai]
    export OPENAI_API_KEY="your-key"
    python app.py
"""
from phylax import trace, expect

@trace(provider="openai")
@expect(
    must_include=["refund"],
    must_not_include=["lawsuit"],
    max_latency_ms=3000,
)
def handle_refund_request(customer_message: str) -> str:
    """Handle a customer refund request with safety contracts."""
    # In production, this calls your LLM:
    #   from phylax import OpenAIAdapter
    #   adapter = OpenAIAdapter()
    #   response, trace = adapter.generate(prompt=customer_message)
    #   return response
    #
    # For this demo, we simulate:
    return (
        "I understand you'd like a refund. Our refund policy allows "
        "returns within 30 days of purchase. I'll process your refund "
        "request right away. You should see the credit within 5-7 "
        "business days."
    )

@trace(provider="openai")
@expect(
    must_include=["tracking", "delivery"],
    must_not_include=["lawsuit", "attorney"],
    max_latency_ms=3000,
)
def handle_shipping_inquiry(customer_message: str) -> str:
    """Handle a shipping inquiry."""
    return (
        "I can help with your delivery status. Your tracking number "
        "shows your package is currently in transit and estimated "
        "delivery is within 2-3 business days."
    )

if __name__ == "__main__":
    print("=" * 60)
    print("AI Support Bot — Phylax Safety Enforcement")
    print("=" * 60)

    # Test refund handling
    print("\n📨 Customer: 'I want a refund for my order'")
    response = handle_refund_request("I want a refund for my order")
    print(f"🤖 Bot: {response}")

    # Test shipping inquiry
    print("\n📨 Customer: 'Where is my package?'")
    response = handle_shipping_inquiry("Where is my package?")
    print(f"🤖 Bot: {response}")

    print("\n" + "=" * 60)
    print("✅ All responses passed safety contracts.")
    print("   Run 'phylax list' to inspect traces.")
    print("   Run 'phylax check' in CI to enforce.")
