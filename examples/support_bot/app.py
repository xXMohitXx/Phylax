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
    Dataset, DatasetCase, run_dataset,
    format_report,
)
from phylax.guardrails import safety_pack, apply_pack


# Apply safety guardrails
_safety = safety_pack()
_safety_rules = _safety.to_expectations()


@trace(provider="mock")
@expect(**_safety_rules)
def handle_support(message: str) -> str:
    """Handle a customer support message with safety guardrails."""
    responses = {
        "refund": "I would be more than happy to help with your refund request. Please provide your order number, the date of purchase, and the email address associated with your account, and I will ensure it is processed within 24 business hours.",
        "shipping": "Your package is currently on its way! Standard shipping typically takes 5-7 business days depending on your region. You can track its live status using the dedicated tracking link provided in your original order confirmation email.",
        "complaint": "I sincerely apologize for the negative experience you have encountered. Please provide me with the full details of what occurred. Let me immediately escalate this issue to our specialized resolutions team, who will reach out to you within the next 24 hours to fully resolve the situation.",
    }
    for key, response in responses.items():
        if key in message.lower():
            return response
    return "Thank you so much for reaching out to us today. A dedicated support agent has been notified and will be with you shortly to assist with your inquiry. We appreciate your continued patience."


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
            input="My shipping is late, where is the package?",
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
    report = format_report(result)
    with open("C:/tmp/support_err.txt", "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    main()
