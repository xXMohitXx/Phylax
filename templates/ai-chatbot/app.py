"""
AI Chatbot Template — Ready-to-use chatbot with Phylax enforcement.

Features:
    - Safety guardrails (hate speech, PII, harmful content)
    - Quality enforcement (min response length, latency ceiling)
    - Dataset contract testing

Usage:
    pip install phylax
    python app.py
"""
from phylax import (
    trace, expect, execution,
    safety_pack, quality_pack, apply_pack,
)


# Combine safety + quality guardrails
_safety = safety_pack().to_expectations()
_quality = quality_pack().to_expectations()
_rules = {**_safety, **_quality}
# Merge must_not_include lists
_rules["must_not_include"] = _safety.get("must_not_include", []) + _quality.get("must_not_include", [])


@trace(provider="mock")
@expect(**_rules)
def chat(message: str) -> str:
    """Process a chat message with safety + quality enforcement."""
    # Replace this with your actual LLM call
    return (
        f"Thank you for your message. Here's a thoughtful response "
        f"regarding '{message}'. I've considered multiple perspectives "
        f"and can provide helpful guidance on this topic."
    )


def main():
    print("=== AI Chatbot with Phylax Enforcement ===\n")

    messages = [
        "Hello, how are you?",
        "Can you help me with Python?",
        "What's the weather like today?",
    ]

    with execution():
        for msg in messages:
            response = chat(msg)
            print(f"User: {msg}")
            print(f"Bot:  {response[:60]}...")
            print()

    print("✅ All messages passed safety + quality checks!")


if __name__ == "__main__":
    main()
