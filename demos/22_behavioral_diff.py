"""
Demo 22: Behavioral Diff
========================
Compare two dataset runs to detect regressions.

Features demonstrated:
    - diff_runs() to compare DatasetResult objects
    - Regression detection (PASS → FAIL)
    - Resolved detection (FAIL → PASS)
    - format_diff_report() console output
    - format_diff_json() for CI pipelines
"""
from phylax import (
    Dataset,
    DatasetCase,
    run_dataset,
    diff_runs,
    format_diff_report,
    format_diff_json,
)


def handler_v1(input_text: str) -> str:
    """Version 1 handler — baseline."""
    return f"Hello! I can help with {input_text}. Here is a detailed response covering all aspects of your question."


def handler_v2(input_text: str) -> str:
    """Version 2 handler — has a regression on 'shipping' but fixes 'billing'."""
    if "shipping" in input_text.lower():
        return "OK"  # Too short — will fail min_tokens
    if "billing" in input_text.lower():
        return f"Regarding your billing inquiry: Here is a comprehensive response about {input_text} with all relevant details."
    return f"Hello! I can help with {input_text}. Here is a detailed response covering all aspects."


def main():
    print("=" * 60)
    print("Demo 22: Behavioral Diff Engine")
    print("=" * 60)

    ds = Dataset(dataset="customer_support", cases=[
        DatasetCase(input="help with shipping", name="shipping",
                    expectations={"must_include": ["help"], "min_tokens": 10}),
        DatasetCase(input="billing question", name="billing",
                    expectations={"must_include": ["billing"], "min_tokens": 10}),
        DatasetCase(input="general inquiry", name="general",
                    expectations={"min_tokens": 10}),
    ])

    # Run both versions
    result_v1 = run_dataset(ds, handler_v1)
    result_v2 = run_dataset(ds, handler_v2)

    # Diff them
    diff = diff_runs(result_v1, result_v2)

    # Console report
    print(format_diff_report(diff))

    # Check for regressions
    if diff.has_regressions:
        print(f"⚠️  Found {diff.regressions} regression(s)!")
        print("   Deploy blocked until regressions are fixed.")
    else:
        print("✅ No regressions — safe to deploy!")


if __name__ == "__main__":
    main()
