"""
Support Bot Example — Content safety enforcement with guardrail packs.

Demonstrates:
    - Safety guardrail pack (blocks hate speech, PII, harmful content)
    - Dataset contracts for batch testing
    - Behavioral diff for regression detection

Run:
    pip install phylax
    python app.py
"""
from phylax import (
    trace, expect, execution,
    safety_pack, apply_pack,
    Dataset, DatasetCase, run_dataset,
    format_report,
)


# Apply safety guardrails
_safety = safety_pack()
_safety_rules = _safety.to_expectations()


@trace(provider="mock")
@expect(**_safety_rules)
def handle_support(message: str) -> str:
    """Handle a customer support message with safety guardrails."""
    responses = {
        "refund": "I'd be happy to help with your refund request. Please provide your order number and I'll process it within 24 hours.",
        "shipping": "Your package is on its way! Standard shipping takes 5-7 business days. You can track it using the link in your confirmation email.",
        "complaint": "I'm sorry to hear about your experience. Let me escalate this to our team who will reach out within 24 hours to resolve it.",
    }
    for key, response in responses.items():
        if key in message.lower():
            return response
    return "Thank you for reaching out. A support agent will be with you shortly to assist with your inquiry."


def main():
    print("=== Support Bot with Safety Guardrails ===\n")
    print(f"Safety rules applied: {len(_safety.rules)} rules\n")

    # Test individual messages
    with execution():
        r1 = handle_support("I want a refund for my order")
        print(f"Refund: {r1[:60]}...")

        r2 = handle_support("Where is my shipping?")
        print(f"Shipping: {r2[:60]}...")

    # Batch test with dataset contracts
    ds = Dataset(dataset="support_bot", cases=[
        DatasetCase(
            input="I need a refund",
            name="refund_request",
            expectations={**_safety_rules, "must_include": ["refund"]},
        ),
        DatasetCase(
            input="My package is late",
            name="shipping_inquiry",
            expectations={**_safety_rules, "must_include": ["shipping", "track"]},
        ),
        DatasetCase(
            input="I have a complaint",
            name="complaint",
            expectations=_safety_rules,
        ),
    ])

    result = run_dataset(ds, handle_support)
    print(f"\n{format_report(result)}")


if __name__ == "__main__":
    main()
