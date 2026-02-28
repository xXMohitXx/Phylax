"""
Demo 15: Enforcement Modes (Axis 3)

Shows how to:
- Use enforce, quarantine, and observe modes
- Understand verdict invariance across modes
- Configure CI exit behavior without altering verdicts
"""

from phylax import (
    ModeHandler,
    ModeResult,
    VALID_MODES,
    evaluate,
)


def main():
    print("=" * 60)
    print("  DEMO 15: Enforcement Modes")
    print("=" * 60)
    print()

    # Simulate a failing expectation
    verdict = evaluate(
        response_text="I am not sure about that.",
        latency_ms=500,
        must_not_include=["not sure"],
    )
    print(f"Engine verdict: {verdict.status}")
    print()

    # ── Apply each mode ───────────────────────────────────────
    print("Mode Behavior Comparison:")
    print("-" * 50)
    print(f"{'Mode':<15} {'Verdict':<10} {'Exit Code':<12} {'Action'}")
    print("-" * 50)

    for mode in sorted(VALID_MODES):
        handler = ModeHandler(mode)
        result = handler.apply(verdict.status)
        print(f"{mode:<15} {result.verdict:<10} {result.exit_code:<12} {result.log_action}")

    print()
    print("Key insight: verdict is ALWAYS 'fail' — modes only change exit code.")
    print()

    # ── Passing verdict ───────────────────────────────────────
    print("With a passing verdict:")
    print("-" * 50)
    print(f"{'Mode':<15} {'Verdict':<10} {'Exit Code':<12} {'Action'}")
    print("-" * 50)

    for mode in sorted(VALID_MODES):
        handler = ModeHandler(mode)
        result = handler.apply("pass")
        print(f"{mode:<15} {result.verdict:<10} {result.exit_code:<12} {result.log_action}")

    print()
    print("✓ Modes affect CI behavior, never engine verdicts.")


if __name__ == "__main__":
    main()
