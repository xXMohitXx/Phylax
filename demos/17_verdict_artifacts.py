"""
Demo 17 - Verdict Artifacts

Shows how Phylax produces frozen, machine-consumable verdict artifacts
that external systems can parse without importing Phylax.

Usage:
    python demos/17_verdict_artifacts.py
"""

import json

from phylax import (
    generate_verdict_artifact,
    compute_definition_hash,
)


def main():
    # -- Generate a PASS verdict ------------------------------------------
    definition = {"rule": "must_include", "substrings": ["refund"]}
    snapshot_hash = compute_definition_hash(definition)

    verdict_pass = generate_verdict_artifact(
        mode="enforce",
        verdict="PASS",
        expectations_evaluated=5,
        failures=0,
        definition_snapshot_hash=snapshot_hash,
        engine_version="1.6.3",
    )

    print("--- PASS Verdict Artifact ---")
    print(json.dumps(json.loads(verdict_pass.model_dump_json()), indent=2))

    # -- Generate a FAIL verdict ------------------------------------------
    verdict_fail = generate_verdict_artifact(
        mode="enforce",
        verdict="FAIL",
        expectations_evaluated=10,
        failures=3,
        definition_snapshot_hash=snapshot_hash,
        engine_version="1.6.3",
    )

    print("\n--- FAIL Verdict Artifact ---")
    print(json.dumps(json.loads(verdict_fail.model_dump_json()), indent=2))

    # -- External consumer simulation -------------------------------------
    raw_json = verdict_fail.model_dump_json()
    # This is what an external CI tool sees - plain JSON, no Phylax needed
    parsed = json.loads(raw_json)
    print("\n--- External Consumer ---")
    print(f"Verdict: {parsed['verdict']}")
    print(f"Failures: {parsed['failures']}/{parsed['expectations_evaluated']}")
    print(f"Mode: {parsed['mode']}")
    print(f"Schema: {parsed['schema_version']}")

    # -- Key properties ---------------------------------------------------
    print("\n--- Properties ---")
    print(f"[OK] Frozen (immutable after creation)")
    print(f"[OK] Schema versioned: {verdict_pass.schema_version}")
    print(f"[OK] No commentary fields")
    print(f"[OK] Machine-consumable JSON")
    print(f"[OK] External systems parse without Phylax SDK")


if __name__ == "__main__":
    main()
