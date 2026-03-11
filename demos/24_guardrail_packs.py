"""
Demo 24: Guardrail Packs
=========================
Pre-built expectation rule sets for common use cases.

Features demonstrated:
    - Built-in packs: safety_pack(), quality_pack(), compliance_pack()
    - Pack registry: list_packs(), get_pack()
    - apply_pack() to merge rules
    - to_expectations() for dataset integration
    - Integration with dataset contracts
"""
from phylax import (
    list_packs,
    get_pack,
    apply_pack,
    safety_pack,
    quality_pack,
    compliance_pack,
    Dataset,
    DatasetCase,
    run_dataset,
    format_report,
)


def test_handler(input_text: str) -> str:
    """A handler that produces safe, quality responses."""
    return (
        f"Thank you for your inquiry about '{input_text}'. "
        f"Based on available information, here is a helpful and "
        f"comprehensive response that addresses your question "
        f"with relevant details and practical guidance."
    )


def main():
    print("=" * 60)
    print("Demo 24: Guardrail Packs")
    print("=" * 60)

    # 1. List available packs
    print("\n--- Available Guardrail Packs ---")
    for name in list_packs():
        pack = get_pack(name)
        print(f"  [pack] {name}: {pack.description}")
        print(f"     Rules: {len(pack.rules)}, Version: {pack.version}")

    # 2. Inspect safety pack
    print("\n--- Safety Pack Rules ---")
    safety = safety_pack()
    for rule in safety.rules:
        print(f"  [rule] {rule.name} ({rule.severity}): {rule.type}")

    # 3. Convert to expectations
    print("\n--- Safety Expectations ---")
    expectations = safety.to_expectations()
    for key, value in expectations.items():
        if isinstance(value, list):
            print(f"  {key}: [{len(value)} items]")
        else:
            print(f"  {key}: {value}")

    # 4. Merge packs with custom rules
    print("\n--- Merged Pack + Custom Rules ---")
    custom = {"must_include": ["thank you"], "min_tokens": 20}
    merged = apply_pack(safety, custom)
    print(f"  must_include: {merged.get('must_include', [])}")
    print(f"  must_not_include: [{len(merged.get('must_not_include', []))} items]")
    print(f"  min_tokens: {merged.get('min_tokens')}")

    # 5. Use with dataset contracts
    print("\n--- Dataset Contract with Guardrails ---")
    quality = quality_pack()
    quality_expectations = quality.to_expectations()

    ds = Dataset(dataset="guardrail_demo", cases=[
        DatasetCase(
            input="How do I reset my password?",
            name="password_reset",
            expectations=quality_expectations,
        ),
        DatasetCase(
            input="What are your business hours?",
            name="business_hours",
            expectations=quality_expectations,
        ),
    ])

    result = run_dataset(ds, test_handler)
    print(format_report(result))


if __name__ == "__main__":
    main()
