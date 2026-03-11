"""
Summarization Example — Quality + latency enforcement.

Demonstrates:
    - Quality guardrail pack (min tokens, no placeholders)
    - Max latency enforcement
    - Dataset contracts for regression testing

Run:
    pip install phylax
    python app.py
"""
from phylax import (
    trace, expect, execution,
    quality_pack, apply_pack,
    Dataset, DatasetCase, run_dataset,
    format_report,
)


# Apply quality guardrails
_quality = quality_pack()
_quality_rules = _quality.to_expectations()


@trace(provider="mock")
@expect(
    min_tokens=20,
    max_latency_ms=5000,
)
def summarize(text: str) -> str:
    """Summarize text with quality and latency requirements."""
    words = text.split()
    key_points = words[:10]
    return (
        f"Summary of the provided text: The content discusses "
        f"{' '.join(key_points)} and covers multiple important aspects "
        f"of the topic with detailed analysis and supporting evidence."
    )


def main():
    print("=== Summarization with Quality Enforcement ===\n")

    # Test individual summarization
    with execution():
        r1 = summarize("Machine learning is a subset of artificial intelligence")
        print(f"Summary: {r1[:80]}...\n")

    # Batch test with dataset contracts
    ds = Dataset(dataset="summarization", cases=[
        DatasetCase(
            input="Artificial intelligence is transforming healthcare with diagnostic tools",
            name="healthcare_summary",
            expectations={"min_tokens": 15, "must_include": ["summary"]},
        ),
        DatasetCase(
            input="Climate change requires immediate global cooperation to reduce emissions",
            name="climate_summary",
            expectations={"min_tokens": 15, "must_include": ["summary"]},
        ),
        DatasetCase(
            input="Python is a versatile programming language used in web development and data science",
            name="tech_summary",
            expectations={"min_tokens": 15, "must_include": ["summary"]},
        ),
    ])

    result = run_dataset(ds, summarize)
    print(format_report(result))


if __name__ == "__main__":
    main()
