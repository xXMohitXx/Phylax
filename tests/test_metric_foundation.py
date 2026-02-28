"""
Phase 3.1 — Metric Foundation Layer Tests

Tests for:
- 3.1.1 Expectation Identity Freezing
- 3.1.2 Evaluation Ledger
- 3.1.3 Deterministic Aggregator

Invariant categories tested:
- Determinism: same input → same output
- Immutability: no mutation after creation
- Literalism: no qualitative labels, no scoring
- Structural purity: all metrics derived from raw data
"""

import inspect
import json
import os
import tempfile

import pytest
from pydantic import ValidationError

from phylax import (
    ExpectationIdentity,
    EvaluationLedger,
    LedgerEntry,
    AggregateMetrics,
    compute_definition_hash,
)
# Private helpers — not part of public API, used only in meta-tests
from phylax._internal.metrics.identity import (
    _canonical_serialize,
    _generate_deterministic_id,
)
from phylax import aggregate, aggregate_all


# ═══════════════════════════════════════════════════════════════════
# 3.1.1 — EXPECTATION IDENTITY FREEZING
# ═══════════════════════════════════════════════════════════════════

class TestIdentityDeterminism:
    """Same config → same hash. Always."""

    def test_same_config_same_hash(self):
        config = {"rule": "must_include", "substrings": ["hello"]}
        h1 = compute_definition_hash(config)
        h2 = compute_definition_hash(config)
        assert h1 == h2

    def test_key_order_irrelevant(self):
        c1 = {"rule": "must_include", "substrings": ["hello"]}
        c2 = {"substrings": ["hello"], "rule": "must_include"}
        assert compute_definition_hash(c1) == compute_definition_hash(c2)

    def test_whitespace_in_values_matters(self):
        c1 = {"rule": "must_include", "value": "hello"}
        c2 = {"rule": "must_include", "value": "hello "}
        assert compute_definition_hash(c1) != compute_definition_hash(c2)

    def test_semantic_change_changes_hash(self):
        c1 = {"rule": "must_include", "substrings": ["hello"]}
        c2 = {"rule": "must_include", "substrings": ["world"]}
        assert compute_definition_hash(c1) != compute_definition_hash(c2)

    def test_type_change_changes_hash(self):
        c1 = {"rule": "max_latency", "max_ms": 1000}
        c2 = {"rule": "max_latency", "max_ms": "1000"}
        assert compute_definition_hash(c1) != compute_definition_hash(c2)

    def test_hash_is_64_hex_chars(self):
        h = compute_definition_hash({"rule": "test"})
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_deterministic_id_same_config(self):
        config = {"rule": "must_include", "substrings": ["hello"]}
        id1 = _generate_deterministic_id(config)
        id2 = _generate_deterministic_id(config)
        assert id1 == id2
        assert id1.startswith("exp-")

    def test_100_runs_deterministic(self):
        config = {"rule": "must_include", "substrings": ["hello"], "case": False}
        hashes = set()
        for _ in range(100):
            hashes.add(compute_definition_hash(config))
        assert len(hashes) == 1


class TestIdentityImmutability:
    """Identity is frozen after creation."""

    def test_frozen_fields(self):
        identity = ExpectationIdentity.create({"rule": "test"})
        with pytest.raises(ValidationError):
            identity.expectation_id = "changed"

    def test_frozen_hash(self):
        identity = ExpectationIdentity.create({"rule": "test"})
        with pytest.raises(ValidationError):
            identity.definition_hash = "changed"

    def test_create_with_explicit_id(self):
        identity = ExpectationIdentity.create(
            {"rule": "test"},
            expectation_id="my-custom-id"
        )
        assert identity.expectation_id == "my-custom-id"

    def test_create_auto_id(self):
        identity = ExpectationIdentity.create({"rule": "test"})
        assert identity.expectation_id.startswith("exp-")


class TestIdentityChangeDetection:
    """Change detection is hash-only. No interpretation."""

    def test_unchanged_config(self):
        config = {"rule": "must_include", "substrings": ["hello"]}
        identity = ExpectationIdentity.create(config)
        assert identity.has_changed(config) is False

    def test_changed_config(self):
        config1 = {"rule": "must_include", "substrings": ["hello"]}
        config2 = {"rule": "must_include", "substrings": ["world"]}
        identity = ExpectationIdentity.create(config1)
        assert identity.has_changed(config2) is True

    def test_no_semantic_diff_in_source(self):
        """Identity module must not contain semantic diff logic."""
        from phylax._internal.metrics import identity
        source = inspect.getsource(identity)
        for forbidden in ["semantic_diff", "meaning_changed", "interpret_change",
                          "significant_change"]:
            assert forbidden not in source.lower()


class TestCanonicalSerialization:
    """Canonical form must be deterministic and minimal."""

    def test_no_whitespace(self):
        result = _canonical_serialize({"a": 1, "b": 2})
        assert " " not in result
        assert "\n" not in result
        assert "\t" not in result

    def test_sorted_keys(self):
        result = _canonical_serialize({"z": 1, "a": 2, "m": 3})
        parsed = json.loads(result)
        assert list(parsed.keys()) == ["a", "m", "z"]

    def test_nested_sorted(self):
        result = _canonical_serialize({"b": {"z": 1, "a": 2}})
        assert result == '{"b":{"a":2,"z":1}}'


# ═══════════════════════════════════════════════════════════════════
# 3.1.2 — EVALUATION LEDGER
# ═══════════════════════════════════════════════════════════════════

class TestLedgerAppendOnly:
    """Ledger is append-only. No update. No delete."""

    def test_record_and_retrieve(self):
        ledger = EvaluationLedger()
        entry = LedgerEntry(expectation_id="exp-1", verdict="pass")
        ledger.record(entry)
        assert ledger.total_entries == 1
        assert ledger.get_entries()[0].expectation_id == "exp-1"

    def test_multiple_entries(self):
        ledger = EvaluationLedger()
        for i in range(10):
            ledger.record(LedgerEntry(expectation_id=f"exp-{i}", verdict="pass"))
        assert ledger.total_entries == 10

    def test_filter_by_expectation_id(self):
        ledger = EvaluationLedger()
        ledger.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))
        ledger.record(LedgerEntry(expectation_id="exp-2", verdict="fail"))
        ledger.record(LedgerEntry(expectation_id="exp-1", verdict="fail"))

        entries = ledger.get_entries("exp-1")
        assert len(entries) == 2

    def test_windowed_query(self):
        ledger = EvaluationLedger()
        for i in range(10):
            ledger.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))
        entries = ledger.get_entries_windowed("exp-1", last_n=3)
        assert len(entries) == 3

    def test_no_delete_method(self):
        """Ledger must not have delete capability."""
        ledger = EvaluationLedger()
        assert not hasattr(ledger, "delete")
        assert not hasattr(ledger, "remove")
        assert not hasattr(ledger, "clear")

    def test_no_update_method(self):
        """Ledger must not have update capability."""
        ledger = EvaluationLedger()
        assert not hasattr(ledger, "update")
        assert not hasattr(ledger, "modify")
        assert not hasattr(ledger, "edit")


class TestLedgerEntryImmutability:
    """Entries are frozen after creation."""

    def test_frozen_verdict(self):
        entry = LedgerEntry(expectation_id="exp-1", verdict="pass")
        with pytest.raises(ValidationError):
            entry.verdict = "fail"

    def test_frozen_expectation_id(self):
        entry = LedgerEntry(expectation_id="exp-1", verdict="pass")
        with pytest.raises(ValidationError):
            entry.expectation_id = "changed"

    def test_verdict_binary_only(self):
        """Verdict must be pass or fail. Nothing else."""
        with pytest.raises(ValidationError):
            LedgerEntry(expectation_id="exp-1", verdict="warning")
        with pytest.raises(ValidationError):
            LedgerEntry(expectation_id="exp-1", verdict="skip")


class TestLedgerPersistence:
    """JSONL persistence is append-only."""

    def test_persist_and_reload(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name

        try:
            ledger1 = EvaluationLedger(path)
            ledger1.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))
            ledger1.record(LedgerEntry(expectation_id="exp-2", verdict="fail"))

            # Reload from disk
            ledger2 = EvaluationLedger(path)
            assert ledger2.total_entries == 2
            assert ledger2.get_entries()[0].expectation_id == "exp-1"
            assert ledger2.get_entries()[1].verdict == "fail"
        finally:
            os.unlink(path)

    def test_append_to_existing(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name

        try:
            ledger1 = EvaluationLedger(path)
            ledger1.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))

            ledger2 = EvaluationLedger(path)
            ledger2.record(LedgerEntry(expectation_id="exp-2", verdict="fail"))

            # Third load should see both
            ledger3 = EvaluationLedger(path)
            assert ledger3.total_entries == 2
        finally:
            os.unlink(path)


# ═══════════════════════════════════════════════════════════════════
# 3.1.3 — DETERMINISTIC AGGREGATOR
# ═══════════════════════════════════════════════════════════════════

class TestAggregatorPurity:
    """Aggregator is a pure function. No side effects."""

    def test_basic_aggregation(self):
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
        ]
        result = aggregate(entries, "exp-1")
        assert result.total_evaluations == 3
        assert result.total_passes == 2
        assert result.total_failures == 1
        assert result.failure_rate == pytest.approx(1/3)
        assert result.never_failed is False
        assert result.never_passed is False

    def test_never_failed(self):
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
        ]
        result = aggregate(entries, "exp-1")
        assert result.never_failed is True
        assert result.never_passed is False

    def test_never_passed(self):
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
        ]
        result = aggregate(entries, "exp-1")
        assert result.never_failed is False
        assert result.never_passed is True

    def test_empty_entries(self):
        result = aggregate([], "exp-1")
        assert result.total_evaluations == 0
        assert result.failure_rate == 0.0
        assert result.never_failed is False
        assert result.never_passed is False

    def test_filters_by_expectation_id(self):
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-2", verdict="fail"),
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
        ]
        result = aggregate(entries, "exp-1")
        assert result.total_evaluations == 2

    def test_aggregate_all(self):
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-2", verdict="fail"),
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
        ]
        results = aggregate_all(entries)
        assert len(results) == 2
        assert results[0].expectation_id == "exp-1"
        assert results[1].expectation_id == "exp-2"


class TestAggregatorDeterminism:
    """Same entries → same result. 100 times."""

    def test_100_runs_identical(self):
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
        ]
        results = set()
        for _ in range(100):
            r = aggregate(entries, "exp-1")
            results.add((r.total_evaluations, r.total_passes, r.total_failures,
                         r.failure_rate, r.never_failed, r.never_passed))
        assert len(results) == 1


class TestAggregateImmutability:
    """Aggregate results are frozen."""

    def test_frozen(self):
        entries = [LedgerEntry(expectation_id="exp-1", verdict="pass")]
        result = aggregate(entries, "exp-1")
        with pytest.raises(ValidationError):
            result.total_evaluations = 999


class TestNoQualitativeLabels:
    """No qualitative language anywhere in the module."""

    def test_no_labels_in_identity(self):
        from phylax._internal.metrics import identity
        source = inspect.getsource(identity)
        for forbidden in ["weak", "strong", "bad", "risky", "good",
                          "healthy", "unhealthy", "critical"]:
            assert forbidden not in source.lower(), (
                f"identity.py contains qualitative label: {forbidden}"
            )

    def test_no_labels_in_ledger(self):
        from phylax._internal.metrics import ledger
        source = inspect.getsource(ledger)
        for forbidden in ["weak", "strong", "bad", "risky", "good",
                          "healthy", "unhealthy", "score", "rank"]:
            assert forbidden not in source.lower(), (
                f"ledger.py contains qualitative label: {forbidden}"
            )

    def test_no_labels_in_aggregator(self):
        from phylax._internal.metrics import aggregator
        source = inspect.getsource(aggregator)
        for forbidden in ["signal_quality", "health_score", "risk_level",
                          "is_weak", "is_strong", "is_risky", "label =",
                          "compute_priority", "assign_rank"]:
            assert forbidden not in source.lower(), (
                f"aggregator.py contains qualitative label: {forbidden}"
            )

    def test_no_scoring_in_aggregator(self):
        from phylax._internal.metrics import aggregator
        source = inspect.getsource(aggregator)
        for forbidden in ["signal_quality", "health_score", "risk_level",
                          "confidence", "weight"]:
            assert forbidden not in source.lower()


class TestEngineUnchanged:
    """Engine core must remain untouched."""

    def test_engine_no_metrics_imports(self):
        from phylax._internal.expectations import rules, evaluator
        for mod in [rules, evaluator]:
            source = inspect.getsource(mod)
            assert "metrics" not in source, (
                f"{mod.__name__} imports metrics — engine contamination"
            )
