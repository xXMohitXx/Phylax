"""
Phase 3.2 — Health Exposure API Tests

Tests for:
- 3.2.1 Health Report Schema
- 3.2.2 Coverage Metrics
- 3.2.3 Windowed Metrics

Invariant categories tested:
- No qualitative labels in any response
- Arithmetic-only coverage
- Explicit window only (no auto-window)
- No statistical smoothing
"""

import inspect

import pytest
from pydantic import ValidationError

from phylax import (
    ExpectationIdentity,
    EvaluationLedger,
    LedgerEntry,
    AggregateMetrics,
    aggregate,
)
from phylax import (
    HealthReport,
    CoverageReport,
    get_windowed_health,
)


# ═══════════════════════════════════════════════════════════════════
# 3.2.1 — HEALTH REPORT SCHEMA
# ═══════════════════════════════════════════════════════════════════

class TestHealthReportSchema:
    """Health reports contain only facts."""

    def test_from_aggregate(self):
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
        ]
        metrics = aggregate(entries, "exp-1")
        report = HealthReport.from_aggregate(metrics, "abc123hash")
        
        assert report.expectation_id == "exp-1"
        assert report.definition_hash == "abc123hash"
        assert report.total_evaluations == 2
        assert report.total_failures == 1
        assert report.failure_rate == 0.5
        assert report.never_failed is False
        assert report.never_passed is False

    def test_frozen(self):
        entries = [LedgerEntry(expectation_id="exp-1", verdict="pass")]
        metrics = aggregate(entries, "exp-1")
        report = HealthReport.from_aggregate(metrics, "hash")
        with pytest.raises(ValidationError):
            report.total_evaluations = 999

    def test_no_qualitative_strings_in_model(self):
        """HealthReport fields must not contain qualitative labels."""
        field_names = list(HealthReport.model_fields.keys())
        for forbidden in ["status", "quality", "risk", "health_level",
                          "recommendation", "suggestion"]:
            assert forbidden not in field_names

    def test_no_qualitative_labels_in_source(self):
        from phylax._internal.metrics import health
        source = inspect.getsource(health)
        for forbidden in ["is_weak", "is_strong", "compute_risk",
                          "health_status", "quality_label", "severity_label"]:
            assert forbidden not in source, (
                f"health.py contains qualitative logic: {forbidden}"
            )


# ═══════════════════════════════════════════════════════════════════
# 3.2.2 — COVERAGE METRICS
# ═══════════════════════════════════════════════════════════════════

class TestCoverageReport:
    """Coverage is purely arithmetic."""

    def test_full_coverage(self):
        report = CoverageReport.compute(3, {"exp-1", "exp-2", "exp-3"})
        assert report.coverage_ratio == 1.0
        assert report.expectations_declared == 3
        assert report.expectations_evaluated == 3

    def test_partial_coverage(self):
        report = CoverageReport.compute(4, {"exp-1", "exp-2"})
        assert report.coverage_ratio == 0.5

    def test_zero_declared(self):
        report = CoverageReport.compute(0, set())
        assert report.coverage_ratio == 0.0

    def test_no_adequacy_judgment(self):
        """Coverage ratio must not trigger any adequacy judgment."""
        report = CoverageReport.compute(10, {"exp-1"})
        # 10% coverage — no "insufficient" label
        assert report.coverage_ratio == 0.1
        dump = report.model_dump()
        assert "sufficient" not in str(dump).lower()
        assert "adequate" not in str(dump).lower()

    def test_frozen(self):
        report = CoverageReport.compute(3, {"exp-1", "exp-2"})
        with pytest.raises(ValidationError):
            report.coverage_ratio = 1.0


# ═══════════════════════════════════════════════════════════════════
# 3.2.3 — WINDOWED METRICS
# ═══════════════════════════════════════════════════════════════════

class TestWindowedMetrics:
    """Windowed queries require explicit N."""

    def test_windowed_returns_last_n(self):
        ledger = EvaluationLedger()
        for i in range(10):
            v = "pass" if i < 7 else "fail"
            ledger.record(LedgerEntry(expectation_id="exp-1", verdict=v))
        
        entries = ledger.get_entries_windowed("exp-1", last_n=3)
        assert len(entries) == 3
        # Last 3 should be the ones with index 7, 8, 9 (all fail)
        assert all(e.verdict == "fail" for e in entries)

    def test_window_larger_than_entries(self):
        ledger = EvaluationLedger()
        ledger.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))
        entries = ledger.get_entries_windowed("exp-1", last_n=100)
        assert len(entries) == 1

    def test_no_auto_window_in_source(self):
        """No automatic window selection."""
        from phylax._internal.metrics import health
        source = inspect.getsource(health)
        for forbidden in ["auto_window", "rolling_window", "default_window",
                          "smart_window"]:
            assert forbidden not in source.lower()

    def test_no_statistical_smoothing(self):
        """No statistical smoothing or averaging."""
        from phylax._internal.metrics import health
        source = inspect.getsource(health)
        for forbidden in ["moving_average", "exponential_smooth",
                          "weighted_average", "trend_line"]:
            assert forbidden not in source.lower()


class TestHealthAPINoLabels:
    """API routes must not contain qualitative language."""

    def test_no_labels_in_route_source(self):
        from phylax.server.routes import health as health_routes
        source = inspect.getsource(health_routes)
        for forbidden in ["\"weak\"", "\"strong\"", "\"bad\"", "\"risky\"",
                          "\"good\"", "\"critical\""]:
            assert forbidden not in source
