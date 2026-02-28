"""
Demo 16: Meta-Enforcement Rules (Axis 3)

Shows how to:
- Guard against expectation dilution
- Use MinExpectationCountRule
- Use ZeroSignalRule
- Use DefinitionChangeGuard
- Use ExpectationRemovalGuard
"""

from phylax import (
    MinExpectationCountRule,
    ZeroSignalRule,
    DefinitionChangeGuard,
    ExpectationRemovalGuard,
    compute_definition_hash,
)


def main():
    print("=" * 60)
    print("  DEMO 16: Meta-Enforcement Rules")
    print("=" * 60)
    print()

    # ── 1. Minimum Expectation Count ─────────────────────────
    print("1. MinExpectationCountRule")
    print("-" * 40)

    rule = MinExpectationCountRule(min_count=5)

    result = rule.evaluate(declared_count=10)
    print(f"  10 expectations declared: {result.passed} ({result.detail})")

    result = rule.evaluate(declared_count=3)
    print(f"  3 expectations declared:  {result.passed} ({result.detail})")
    print()

    # ── 2. Zero-Signal Rule ──────────────────────────────────
    print("2. ZeroSignalRule")
    print("-" * 40)

    rule = ZeroSignalRule()

    result = rule.evaluate(never_failed=True)
    print(f"  Never failed: {result.passed} — {result.detail}")

    result = rule.evaluate(never_failed=False)
    print(f"  Has failed:   {result.passed} — {result.detail}")
    print()

    # ── 3. Definition Change Guard ───────────────────────────
    print("3. DefinitionChangeGuard")
    print("-" * 40)

    guard = DefinitionChangeGuard()
    config_v1 = {"rule": "must_include", "substrings": ["refund"]}
    config_v2 = {"rule": "must_include", "substrings": ["refund", "approved"]}

    h1 = compute_definition_hash(config_v1)
    h2 = compute_definition_hash(config_v2)

    result = guard.evaluate(h1, h1)
    print(f"  Same config:    {result.passed} — {result.detail}")

    result = guard.evaluate(h1, h2)
    print(f"  Changed config: {result.passed} — {result.detail}")
    print()

    # ── 4. Expectation Removal Guard ─────────────────────────
    print("4. ExpectationRemovalGuard")
    print("-" * 40)

    guard = ExpectationRemovalGuard()

    result = guard.evaluate(
        previous_ids={"exp-1", "exp-2", "exp-3"},
        current_ids={"exp-1", "exp-2", "exp-3", "exp-4"},
    )
    print(f"  Added exp-4:   {result.passed} — {result.detail}")

    result = guard.evaluate(
        previous_ids={"exp-1", "exp-2", "exp-3"},
        current_ids={"exp-1", "exp-3"},
    )
    print(f"  Removed exp-2: {result.passed} — {result.detail}")
    print()

    print("✓ Meta-enforcement prevents expectation dilution.")


if __name__ == "__main__":
    main()
