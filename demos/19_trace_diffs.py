"""
Demo 19 - Trace Diff Artifacts

Shows how Phylax produces literal trace diffs between runs:
  - Set operations (added/removed expectations)
  - Hash comparison (definition drift)
  - No impact assessment, no risk scoring

Usage:
    python demos/19_trace_diffs.py
"""

import json

from phylax import (
    generate_trace_diff,
    compute_definition_hash,
)


def main():
    # -- Simulate two runs with different expectations --------------------
    run1_expectations = {"exp-must-include", "exp-max-latency", "exp-no-pii"}
    run2_expectations = {"exp-must-include", "exp-no-pii", "exp-tone-check"}

    run1_hash = compute_definition_hash({
        "rules": sorted(list(run1_expectations)),
    })
    run2_hash = compute_definition_hash({
        "rules": sorted(list(run2_expectations)),
    })

    diff = generate_trace_diff(
        run_id_before="ci-run-001",
        run_id_after="ci-run-002",
        expectations_before=run1_expectations,
        expectations_after=run2_expectations,
        hash_before=run1_hash,
        hash_after=run2_hash,
        changed_fields=["expectations"],
    )

    print("--- Trace Diff Artifact ---")
    print(json.dumps(json.loads(diff.model_dump_json()), indent=2))

    # -- External consumer parsing ----------------------------------------
    raw = json.loads(diff.model_dump_json())
    print(f"\n--- Diff Summary ---")
    print(f"Before: {raw['run_id_before']}")
    print(f"After:  {raw['run_id_after']}")
    print(f"Hashes match: {raw['hashes_match']}")
    if raw["added_expectations"]:
        print(f"Added: {', '.join(raw['added_expectations'])}")
    if raw["removed_expectations"]:
        print(f"Removed: {', '.join(raw['removed_expectations'])}")
    if raw["changed_fields"]:
        print(f"Changed fields: {', '.join(raw['changed_fields'])}")

    # -- No-change diff ---------------------------------------------------
    print("\n--- No-Change Diff ---")
    same_diff = generate_trace_diff(
        run_id_before="ci-run-001",
        run_id_after="ci-run-003",
        expectations_before=run1_expectations,
        expectations_after=run1_expectations,
        hash_before=run1_hash,
        hash_after=run1_hash,
    )
    print(f"Hashes match: {same_diff.hashes_match}")
    print(f"Added: {same_diff.added_expectations}")
    print(f"Removed: {same_diff.removed_expectations}")

    # -- Properties -------------------------------------------------------
    print("\n--- Properties ---")
    print("[OK] Literal diffs only - no 'impact assessment'")
    print("[OK] Sorted output - deterministic ordering")
    print("[OK] No risk scoring")
    print("[OK] Pure set operations (added = after - before)")
    print(f"[OK] Schema version: {diff.schema_version}")


if __name__ == "__main__":
    main()
