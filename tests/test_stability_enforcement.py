"""
Cross-Run Stability Enforcement Tests (Axis 2 Phase 2.4)

Tests:
- ExactStabilityRule (field and hash comparison)
- AllowedDriftRule (whitelisted drift regions)
- StabilitySurfaceAdapter
- Determinism
- Forbidden behaviors
"""

import pytest

from phylax._internal.surfaces.surface import Surface, SurfaceEvaluator
from phylax._internal.surfaces.stability import (
    ExactStabilityRule,
    AllowedDriftRule,
    StabilitySurfaceAdapter,
    _deterministic_hash,
)


def _make_stability_surface(baseline, current):
    return Surface(
        type="cross_run_snapshot",
        raw_payload={"baseline": baseline, "current": current},
    )


BASELINE = {
    "version_id": "v1",
    "structured_output": {"status": "ok", "count": 42},
    "tool_trace": [{"name": "search", "args": {"q": "test"}}],
    "timestamp": "2026-01-01T00:00:00",
    "metadata": {"execution_id": "exec-1", "model": "gpt-4"},
}

IDENTICAL_CURRENT = {
    "version_id": "v1",
    "structured_output": {"status": "ok", "count": 42},
    "tool_trace": [{"name": "search", "args": {"q": "test"}}],
    "timestamp": "2026-01-01T00:00:00",
    "metadata": {"execution_id": "exec-1", "model": "gpt-4"},
}

DRIFTED_CURRENT = {
    "version_id": "v2",
    "structured_output": {"status": "ok", "count": 42},
    "tool_trace": [{"name": "search", "args": {"q": "test"}}],
    "timestamp": "2026-02-01T00:00:00",
    "metadata": {"execution_id": "exec-2", "model": "gpt-4"},
}

CHANGED_CURRENT = {
    "version_id": "v1",
    "structured_output": {"status": "error", "count": 42},
    "tool_trace": [{"name": "search", "args": {"q": "test"}}],
    "timestamp": "2026-01-01T00:00:00",
    "metadata": {"execution_id": "exec-1", "model": "gpt-4"},
}


# =============================================================================
# EXACT STABILITY — HASH
# =============================================================================

class TestExactStabilityHashRule:

    def test_identical_pass(self):
        s = _make_stability_surface(BASELINE, IDENTICAL_CURRENT)
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is True

    def test_changed_fail(self):
        s = _make_stability_surface(BASELINE, CHANGED_CURRENT)
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is False

    def test_drifted_fail(self):
        s = _make_stability_surface(BASELINE, DRIFTED_CURRENT)
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is False


# =============================================================================
# EXACT STABILITY — FIELD
# =============================================================================

class TestExactStabilityFieldRule:

    def test_field_unchanged_pass(self):
        s = _make_stability_surface(BASELINE, DRIFTED_CURRENT)
        r = ExactStabilityRule(path="structured_output.status").evaluate(s)
        assert r.passed is True

    def test_field_changed_fail(self):
        s = _make_stability_surface(BASELINE, CHANGED_CURRENT)
        r = ExactStabilityRule(path="structured_output.status").evaluate(s)
        assert r.passed is False

    def test_field_unchanged_nested(self):
        s = _make_stability_surface(BASELINE, DRIFTED_CURRENT)
        r = ExactStabilityRule(path="metadata.model").evaluate(s)
        assert r.passed is True

    def test_field_changed_metadata(self):
        s = _make_stability_surface(BASELINE, DRIFTED_CURRENT)
        r = ExactStabilityRule(path="metadata.execution_id").evaluate(s)
        assert r.passed is False

    def test_field_missing_both_passes(self):
        s = _make_stability_surface({"a": 1}, {"a": 1})
        r = ExactStabilityRule(path="nonexistent").evaluate(s)
        assert r.passed is True

    def test_field_existence_changed(self):
        s = _make_stability_surface({"a": 1, "b": 2}, {"a": 1})
        r = ExactStabilityRule(path="b").evaluate(s)
        assert r.passed is False

    def test_missing_baseline_key(self):
        s = Surface(type="cross_run_snapshot", raw_payload={"baseline": None, "current": {}})
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is False

    def test_not_dict_payload(self):
        s = Surface(type="cross_run_snapshot", raw_payload="not a dict")
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is False


# =============================================================================
# ALLOWED DRIFT
# =============================================================================

class TestAllowedDriftRule:

    def test_no_drift_pass(self):
        s = _make_stability_surface(BASELINE, IDENTICAL_CURRENT)
        r = AllowedDriftRule(allowed_fields=[]).evaluate(s)
        assert r.passed is True

    def test_whitelisted_drift_pass(self):
        """When only whitelisted fields change, it should pass."""
        s = _make_stability_surface(BASELINE, DRIFTED_CURRENT)
        r = AllowedDriftRule(
            allowed_fields=["version_id", "timestamp", "metadata.execution_id"]
        ).evaluate(s)
        assert r.passed is True

    def test_non_whitelisted_drift_fail(self):
        """When non-whitelisted fields change, it should fail."""
        s = _make_stability_surface(BASELINE, CHANGED_CURRENT)
        r = AllowedDriftRule(
            allowed_fields=["timestamp", "metadata.execution_id"]
        ).evaluate(s)
        assert r.passed is False

    def test_partial_whitelist_fail(self):
        """Only some drift fields whitelisted — should still fail."""
        s = _make_stability_surface(BASELINE, DRIFTED_CURRENT)
        r = AllowedDriftRule(
            allowed_fields=["timestamp"]  # Missing version_id and execution_id
        ).evaluate(s)
        assert r.passed is False

    def test_empty_whitelist_identical_pass(self):
        s = _make_stability_surface(BASELINE, IDENTICAL_CURRENT)
        r = AllowedDriftRule(allowed_fields=[]).evaluate(s)
        assert r.passed is True

    def test_missing_payload_fields(self):
        s = Surface(type="cross_run_snapshot", raw_payload={"baseline": None, "current": None})
        r = AllowedDriftRule(allowed_fields=[]).evaluate(s)
        assert r.passed is False


# =============================================================================
# STABILITY SURFACE ADAPTER
# =============================================================================

class TestStabilitySurfaceAdapter:

    def test_adapt_with_kwargs(self):
        adapter = StabilitySurfaceAdapter()
        s = adapter.adapt(baseline=BASELINE, current=IDENTICAL_CURRENT)
        assert s.type == "cross_run_snapshot"
        assert s.raw_payload["baseline"] == BASELINE
        assert s.raw_payload["current"] == IDENTICAL_CURRENT

    def test_adapt_with_dict(self):
        adapter = StabilitySurfaceAdapter()
        payload = {"baseline": BASELINE, "current": IDENTICAL_CURRENT}
        s = adapter.adapt(payload)
        assert s.raw_payload == payload

    def test_adapt_with_metadata(self):
        adapter = StabilitySurfaceAdapter()
        s = adapter.adapt(
            baseline=BASELINE,
            current=IDENTICAL_CURRENT,
            metadata={"comparison": "v1_vs_v2"},
        )
        assert s.metadata["comparison"] == "v1_vs_v2"


# =============================================================================
# DETERMINISM
# =============================================================================

class TestStabilityDeterminism:

    def test_hash_is_deterministic(self):
        data = {"b": 2, "a": 1, "c": [3, 2, 1]}
        h1 = _deterministic_hash(data)
        h2 = _deterministic_hash(data)
        assert h1 == h2

    def test_hash_order_independent(self):
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}
        assert _deterministic_hash(d1) == _deterministic_hash(d2)

    def test_evaluator_deterministic(self):
        ev = SurfaceEvaluator()
        ev.add_rule(ExactStabilityRule(path="structured_output.status"))
        ev.add_rule(AllowedDriftRule(["timestamp"]))
        s = _make_stability_surface(BASELINE, IDENTICAL_CURRENT)
        v1 = ev.evaluate(s)
        v2 = ev.evaluate(s)
        assert v1.status == v2.status


# =============================================================================
# EVALUATOR INTEGRATION
# =============================================================================

class TestStabilityEvaluatorIntegration:

    def test_multi_rule_pass(self):
        ev = SurfaceEvaluator()
        ev.add_rule(ExactStabilityRule(path="structured_output.status"))
        ev.add_rule(ExactStabilityRule(path="structured_output.count"))
        ev.add_rule(AllowedDriftRule(
            ["version_id", "timestamp", "metadata.execution_id"]
        ))
        s = _make_stability_surface(BASELINE, DRIFTED_CURRENT)
        v = ev.evaluate(s)
        assert v.status == "pass"

    def test_multi_rule_fail(self):
        ev = SurfaceEvaluator()
        ev.add_rule(ExactStabilityRule())  # Full hash comparison — will fail
        ev.add_rule(ExactStabilityRule(path="structured_output.status"))  # Will pass
        s = _make_stability_surface(BASELINE, DRIFTED_CURRENT)
        v = ev.evaluate(s)
        assert v.status == "fail"
        assert len(v.violations) == 1


# =============================================================================
# FORBIDDEN BEHAVIORS
# =============================================================================

class TestForbiddenStabilityBehaviors:

    def test_no_pattern_detection(self):
        import inspect
        from phylax._internal.surfaces import stability
        source = inspect.getsource(stability)
        for forbidden in ["regression_slope", "moving_average", "drift_analysis"]:
            assert forbidden not in source.lower()

    def test_no_auto_update(self):
        import inspect
        from phylax._internal.surfaces import stability
        source = inspect.getsource(stability)
        for forbidden in ["auto_update", "auto_baseline", "self_update"]:
            assert forbidden not in source.lower()

    def test_no_scoring(self):
        import inspect
        from phylax._internal.surfaces import stability
        source = inspect.getsource(stability)
        for forbidden in ["drift_score", "stability_score", "confidence"]:
            assert forbidden not in source.lower()
