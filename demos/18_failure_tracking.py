"""
Demo 18 - Failure Tracking Artifacts

Shows how Phylax produces structured failure records:
  - Mechanical fact only
  - No explanation, no severity ranking
  - Machine-parseable by external tools

Usage:
    python demos/18_failure_tracking.py
"""

import json

from phylax import (
    generate_failure_artifact,
    FailureEntry,
)


def main():
    # -- Generate failure artifact from violations ------------------------
    failures = generate_failure_artifact(
        run_id="ci-run-20260301-001",
        failures=[
            {
                "expectation_id": "exp-must-include-refund",
                "violated_rule": "must_include",
                "raw_value": "Thank you for contacting us. We will look into your request.",
                "expected_value": "refund",
            },
            {
                "expectation_id": "exp-max-latency",
                "violated_rule": "max_latency_ms",
                "raw_value": "2500",
                "expected_value": "1500",
            },
            {
                "expectation_id": "exp-no-pii",
                "violated_rule": "must_not_include",
                "raw_value": "Your SSN is 123-45-6789",
                "expected_value": "NO_PII",
            },
        ],
    )

    print("--- Failure Artifact ---")
    print(json.dumps(json.loads(failures.model_dump_json()), indent=2))

    # -- External consumer parsing ----------------------------------------
    raw = json.loads(failures.model_dump_json())
    print(f"\n--- External CI Consumer ---")
    print(f"Run: {raw['run_id']}")
    print(f"Total failures: {len(raw['failures'])}")
    for f in raw["failures"]:
        print(f"  [FAIL] {f['expectation_id']}: {f['violated_rule']}")
        print(f"    got: {f['raw_value'][:50]}...")
        print(f"    expected: {f['expected_value']}")

    # -- Key properties ---------------------------------------------------
    print("\n--- Properties ---")
    print("[OK] No 'explanation' field - Phylax reports, doesn't explain")
    print("[OK] No 'severity' field - all failures are equal")
    print("[OK] No 'suggestion' field - Phylax enforces, doesn't coach")
    print("[OK] Frozen after creation")
    print(f"[OK] Schema version: {failures.schema_version}")


if __name__ == "__main__":
    main()
