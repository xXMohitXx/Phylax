"""
Demo 14: Metrics & Health API (Axis 3)

Shows how to:
- Create expectation identities
- Record evaluations in the ledger
- Aggregate metrics
- Generate health reports
"""

from phylax import (
    ExpectationIdentity,
    compute_definition_hash,
    EvaluationLedger,
    LedgerEntry,
    aggregate,
    aggregate_all,
    HealthReport,
    CoverageReport,
)


def main():
    print("=" * 60)
    print("  DEMO 14: Metrics & Health API")
    print("=" * 60)
    print()

    # ── 1. Identity Freezing ──────────────────────────────────
    print("1. Expectation Identity")
    print("-" * 40)

    config = {"rule": "must_include", "substrings": ["refund"]}
    identity = ExpectationIdentity.create(config)

    print(f"  ID:   {identity.expectation_id}")
    print(f"  Hash: {identity.definition_hash[:16]}...")
    print(f"  Frozen: {identity.model_config.get('frozen', True)}")

    # Same config → same hash (deterministic)
    h1 = compute_definition_hash(config)
    h2 = compute_definition_hash(config)
    print(f"  Deterministic: {h1 == h2}")
    print()

    # ── 2. Evaluation Ledger ──────────────────────────────────
    print("2. Evaluation Ledger (append-only)")
    print("-" * 40)

    ledger = EvaluationLedger()

    # Record some evaluations
    for i in range(20):
        verdict = "pass" if i % 4 != 0 else "fail"
        ledger.record(LedgerEntry(
            expectation_id=identity.expectation_id,
            verdict=verdict,
        ))

    print(f"  Total entries: {ledger.total_entries}")
    print(f"  Last 3 entries:")
    for e in ledger.get_entries_windowed(identity.expectation_id, last_n=3):
        print(f"    → {e.verdict} at {e.timestamp}")
    print()

    # ── 3. Aggregation ────────────────────────────────────────
    print("3. Deterministic Aggregation")
    print("-" * 40)

    result = aggregate(ledger.get_entries(), identity.expectation_id)
    print(f"  Total:    {result.total_evaluations}")
    print(f"  Passes:   {result.total_passes}")
    print(f"  Failures: {result.total_failures}")
    print(f"  Fail rate: {result.failure_rate:.1%}")
    print(f"  Never failed: {result.never_failed}")
    print()

    # ── 4. Health Report ──────────────────────────────────────
    print("4. Health Report (pure data)")
    print("-" * 40)

    report = HealthReport.from_aggregate(result, identity.definition_hash)
    print(f"  Expectation:  {report.expectation_id}")
    print(f"  Evaluations:  {report.total_evaluations}")
    print(f"  Failure rate: {report.failure_rate:.1%}")
    print(f"  Hash:         {report.definition_hash[:16]}...")
    print()

    # ── 5. Coverage ───────────────────────────────────────────
    print("5. Coverage Report")
    print("-" * 40)

    coverage = CoverageReport.compute(
        declared_count=10,
        evaluated_ids={identity.expectation_id, "exp-2", "exp-3"},
    )
    print(f"  Total:    {coverage.expectations_declared}")
    print(f"  Covered:  {coverage.expectations_evaluated}")
    print(f"  Coverage: {coverage.coverage_ratio:.0%}")
    print()

    print("✓ All metrics from 'from phylax import ...' — no _internal needed!")


if __name__ == "__main__":
    main()
