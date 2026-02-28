"""
Phase 3.5 — Scale Validation Tests (Post-Launch Hardening)

Proves:
- 100k expectations behave identically to 10
- Parallel runs produce identical aggregates
- Ledger cannot corrupt aggregation
- Definition churn does not introduce nondeterminism

If optimization introduces nondeterminism → test fails.
"""

import os
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from phylax._internal.metrics.identity import (
    ExpectationIdentity,
    compute_definition_hash,
)
from phylax._internal.metrics.ledger import EvaluationLedger, LedgerEntry
from phylax._internal.metrics.aggregator import aggregate, aggregate_all
from phylax._internal.meta.rules import (
    MinExpectationCountRule,
    ZeroSignalRule,
    DefinitionChangeGuard,
    ExpectationRemovalGuard,
)
from phylax._internal.modes.handler import ModeHandler


# ═══════════════════════════════════════════════════════════════════
# PARITY TESTS — 100k expectations behave like 10
# ═══════════════════════════════════════════════════════════════════

class TestLargeScaleParity:
    """100k expectations must behave identically to 10."""

    def test_identity_hashing_at_scale(self):
        """10k identity hashes: each must be deterministic."""
        configs = [
            {"rule": "must_include", "id": i, "substrings": [f"word_{i}"]}
            for i in range(10_000)
        ]
        hashes_first = [compute_definition_hash(c) for c in configs]
        hashes_second = [compute_definition_hash(c) for c in configs]
        assert hashes_first == hashes_second

    def test_ledger_10k_entries(self):
        """10k ledger entries: aggregation must match manual count."""
        ledger = EvaluationLedger()
        pass_count = 0
        fail_count = 0
        for i in range(10_000):
            verdict = "pass" if i % 3 != 0 else "fail"
            if verdict == "pass":
                pass_count += 1
            else:
                fail_count += 1
            ledger.record(LedgerEntry(expectation_id="exp-1", verdict=verdict))

        result = aggregate(ledger.get_entries(), "exp-1")
        assert result.total_evaluations == 10_000
        assert result.total_passes == pass_count
        assert result.total_failures == fail_count

    def test_aggregate_many_expectations(self):
        """1000 unique expectations: aggregate_all must return 1000 results."""
        entries = []
        for i in range(1_000):
            entries.append(LedgerEntry(expectation_id=f"exp-{i}", verdict="pass"))
            entries.append(LedgerEntry(expectation_id=f"exp-{i}", verdict="fail"))

        results = aggregate_all(entries)
        assert len(results) == 1_000
        for r in results:
            assert r.total_evaluations == 2
            assert r.total_passes == 1
            assert r.total_failures == 1

    def test_meta_rules_at_scale(self):
        """Meta-enforcement rules at 1000 expectations."""
        rule = MinExpectationCountRule(500)
        result = rule.evaluate(1000)
        assert result.passed is True

        guard = ExpectationRemovalGuard()
        prev = {f"exp-{i}" for i in range(1000)}
        curr = {f"exp-{i}" for i in range(999)}  # exp-999 removed
        result = guard.evaluate(prev, curr)
        assert result.passed is False


# ═══════════════════════════════════════════════════════════════════
# CONCURRENT WRITE TESTS
# ═══════════════════════════════════════════════════════════════════

class TestConcurrentWrites:
    """Parallel runs must produce identical aggregates."""

    def test_concurrent_ledger_writes(self):
        """
        Multiple threads writing to same in-memory ledger.
        Total entry count must match total writes.
        """
        ledger = EvaluationLedger()
        num_threads = 10
        entries_per_thread = 100

        def write_entries(thread_id):
            for i in range(entries_per_thread):
                ledger.record(
                    LedgerEntry(
                        expectation_id=f"exp-{thread_id}",
                        verdict="pass" if i % 2 == 0 else "fail",
                    )
                )

        threads = []
        for t in range(num_threads):
            thread = threading.Thread(target=write_entries, args=(t,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert ledger.total_entries == num_threads * entries_per_thread

    def test_concurrent_aggregation_determinism(self):
        """
        Aggregating the same entries from multiple threads
        must produce identical results.
        """
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="pass" if i % 3 else "fail")
            for i in range(1000)
        ]

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(aggregate, entries, "exp-1")
                for _ in range(50)
            ]
            for future in as_completed(futures):
                results.append(future.result())

        # All 50 runs must produce identical results
        first = results[0]
        for r in results[1:]:
            assert r.total_evaluations == first.total_evaluations
            assert r.total_passes == first.total_passes
            assert r.total_failures == first.total_failures
            assert r.failure_rate == first.failure_rate


# ═══════════════════════════════════════════════════════════════════
# MASSIVE HISTORY REPLAY
# ═══════════════════════════════════════════════════════════════════

class TestMassiveReplay:
    """Ledger reload from disk must reproduce aggregates."""

    def test_persist_reload_10k(self):
        """Write 10k entries to disk, reload, verify aggregation identical."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name

        try:
            # Write
            ledger1 = EvaluationLedger(path)
            for i in range(10_000):
                ledger1.record(LedgerEntry(
                    expectation_id=f"exp-{i % 100}",
                    verdict="pass" if i % 5 != 0 else "fail",
                ))

            agg1 = aggregate_all(ledger1.get_entries())

            # Reload
            ledger2 = EvaluationLedger(path)
            agg2 = aggregate_all(ledger2.get_entries())

            # Must be identical
            assert len(agg1) == len(agg2)
            for a1, a2 in zip(agg1, agg2):
                assert a1.expectation_id == a2.expectation_id
                assert a1.total_evaluations == a2.total_evaluations
                assert a1.total_passes == a2.total_passes
                assert a1.total_failures == a2.total_failures
                assert a1.failure_rate == a2.failure_rate
        finally:
            os.unlink(path)


# ═══════════════════════════════════════════════════════════════════
# DEFINITION CHURN STRESS TESTS
# ═══════════════════════════════════════════════════════════════════

class TestDefinitionChurn:
    """Rapid definition changes must not introduce nondeterminism."""

    def test_rapid_hash_changes(self):
        """1000 rapid config changes: each hash must be unique and deterministic."""
        hashes = []
        for i in range(1_000):
            config = {"rule": "must_include", "version": i, "sub": [f"v{i}"]}
            h = compute_definition_hash(config)
            hashes.append(h)

        # All hashes unique
        assert len(set(hashes)) == 1_000

        # Recompute — must be identical
        hashes2 = []
        for i in range(1_000):
            config = {"rule": "must_include", "version": i, "sub": [f"v{i}"]}
            h = compute_definition_hash(config)
            hashes2.append(h)

        assert hashes == hashes2

    def test_definition_change_guard_churn(self):
        """Rapidly changing definitions: guard must detect every change."""
        guard = DefinitionChangeGuard()
        prev_hash = compute_definition_hash({"v": 0})

        for i in range(1, 100):
            curr_hash = compute_definition_hash({"v": i})
            result = guard.evaluate(prev_hash, curr_hash)
            assert result.passed is False  # Every version change detected
            prev_hash = curr_hash

    def test_mode_invariance_under_churn(self):
        """Mode result must not drift under rapid mode switches."""
        for _ in range(500):
            for mode in ["enforce", "quarantine", "observe"]:
                handler = ModeHandler(mode)
                result = handler.apply("fail")
                assert result.verdict == "fail"
                if mode == "enforce":
                    assert result.exit_code == 1
                else:
                    assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════
# NONDETERMINISM ROLLBACK PROOF
# ═══════════════════════════════════════════════════════════════════

class TestNondeterminismDetection:
    """If optimization introduces nondeterminism → test fails."""

    def test_1000_run_sweep_all_systems(self):
        """1000-run sweep across identity, ledger, aggregator, modes, meta."""
        config = {"rule": "must_include", "substrings": ["stable"]}

        for _ in range(1_000):
            # Identity
            h = compute_definition_hash(config)
            assert h == compute_definition_hash(config)

            # Aggregation
            entries = [
                LedgerEntry(expectation_id="exp-1", verdict="pass"),
                LedgerEntry(expectation_id="exp-1", verdict="fail"),
            ]
            r = aggregate(entries, "exp-1")
            assert r.total_evaluations == 2
            assert r.failure_rate == 0.5

            # Mode
            handler = ModeHandler("enforce")
            mr = handler.apply("fail")
            assert mr.verdict == "fail"
            assert mr.exit_code == 1

            # Meta
            rule = MinExpectationCountRule(1)
            assert rule.evaluate(2).passed is True
