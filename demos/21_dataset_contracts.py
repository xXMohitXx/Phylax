"""
Demo 21: Dataset Contracts
==========================
Batch-test LLM behavior with YAML-style contracts.

Features demonstrated:
    - Dataset, DatasetCase schema
    - run_dataset() with expectations
    - format_report() console output
    - All expectation rules: must_include, must_not_include, min_tokens, max_latency_ms
"""
from phylax import (
    Dataset,
    DatasetCase,
    run_dataset,
    format_report,
    format_json_report,
)


def mock_handler(input_text: str) -> str:
    """Simulate an LLM handler for testing."""
    responses = {
        "refund": "I can help you with your refund request. Please provide your order number and we will process it promptly.",
        "shipping": "Your package is being shipped via express delivery. Track it using the link in your email confirmation.",
        "complaint": "I understand your frustration and I apologize for the inconvenience. Let me escalate this to our team.",
    }
    for key, resp in responses.items():
        if key in input_text.lower():
            return resp
    return "Thank you for contacting us. A representative will assist you shortly with your inquiry."


def main():
    print("=" * 60)
    print("Demo 21: Dataset Contracts")
    print("=" * 60)

    # Define a dataset contract
    ds = Dataset(dataset="support_bot_v1", cases=[
        DatasetCase(
            input="I want a refund for order #1234",
            name="refund_request",
            expectations={
                "must_include": ["refund", "order"],
                "must_not_include": ["lawsuit", "lawyer"],
                "min_tokens": 10,
                "max_latency_ms": 5000,
            },
        ),
        DatasetCase(
            input="Where is my shipping?",
            name="shipping_inquiry",
            expectations={
                "must_include": ["shipping"],
                "min_tokens": 8,
            },
        ),
        DatasetCase(
            input="I have a complaint about service",
            name="complaint_handling",
            expectations={
                "must_include": ["apologize", "escalate"],
                "must_not_include": ["ignore"],
            },
        ),
    ])

    # Run the dataset
    result = run_dataset(ds, mock_handler)

    # Console report
    print(format_report(result))

    # JSON report
    print("\n--- JSON Report ---")
    print(format_json_report(result)[:200] + "...")


if __name__ == "__main__":
    main()
