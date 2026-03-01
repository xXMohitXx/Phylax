"""
Demo 17 â€” Verdict Artifacts

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
    # â”€â”€ Generate a PASS verdict â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    definition = {"rule": "must_include", "substrings": ["refund"]}
    snapshot_hash = compute_definition_hash(definition)

    verdict_pass = generate_verdict_artifact(
        mode="enforce",
        verdict="PASS",
        expectations_evaluated=5,
        failures=0,
        definition_snapshot_hash=snapshot_hash,
        engine_version="1.4.1",
    )

    print("â•â•â• PASS Verdict Artifact â•â•â•")
    print(json.dumps(json.loads(verdict_pass.model_dump_json()), indent=2))

    # â”€â”€ Generate a FAIL verdict â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    verdict_fail = generate_verdict_artifact(
        mode="enforce",
        verdict="FAIL",
        expectations_evaluated=10,
        failures=3,
        definition_snapshot_hash=snapshot_hash,
        engine_version="1.4.1",
    )

    print("\nâ•â•â• FAIL Verdict Artifact â•â•â•")
    print(json.dumps(json.loads(verdict_fail.model_dump_json()), indent=2))

    # â”€â”€ External consumer simulation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    raw_json = verdict_fail.model_dump_json()
    # This is what an external CI tool sees â€” plain JSON, no Phylax needed
    parsed = json.loads(raw_json)
    print(f"\nâ•â•â• External Consumer â•â•â•")
    print(f"Verdict: {parsed['verdict']}")
    print(f"Failures: {parsed['failures']}/{parsed['expectations_evaluated']}")
    print(f"Mode: {parsed['mode']}")
    print(f"Schema: {parsed['schema_version']}")

    # â”€â”€ Key properties â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ•â•â• Properties â•â•â•")
    print(f"âœ“ Frozen (immutable after creation)")
    print(f"âœ“ Schema versioned: {verdict_pass.schema_version}")
    print(f"âœ“ No commentary fields")
    print(f"âœ“ Machine-consumable JSON")
    print(f"âœ“ External systems parse without Phylax SDK")


if __name__ == "__main__":
    main()

