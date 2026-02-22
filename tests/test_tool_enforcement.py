"""
Tool & Function Call Invariants Tests (Axis 2 Phase 2.2)

Tests:
- ToolPresenceRule (must/must-not appear)
- ToolCountRule (exact/min/max)
- ToolArgumentRule (path-based strict comparison)
- ToolOrderingRule (before/not_after)
- ToolSurfaceAdapter
- Raw trace preservation
"""

import pytest

from phylax import (
    Surface,
    SurfaceEvaluator,
    ToolPresenceRule,
    ToolCountRule,
    ToolArgumentRule,
    ToolOrderingRule,
    ToolSurfaceAdapter,
)


def _make_tool_surface(events):
    return Surface(type="tool_calls", raw_payload=events)


SAMPLE_EVENTS = [
    {"name": "search", "args": {"q": "test", "limit": 10}, "timestamp": "t1", "id": "1"},
    {"name": "read", "args": {"url": "http://example.com"}, "timestamp": "t2", "id": "2"},
    {"name": "search", "args": {"q": "more", "limit": 5}, "timestamp": "t3", "id": "3"},
    {"name": "write", "args": {"data": "result", "safe_mode": True}, "timestamp": "t4", "id": "4"},
]


# =============================================================================
# TOOL PRESENCE
# =============================================================================

class TestToolPresenceRule:

    def test_tool_must_exist_pass(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolPresenceRule("search", must_exist=True).evaluate(s)
        assert r.passed is True

    def test_tool_must_exist_fail(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolPresenceRule("delete", must_exist=True).evaluate(s)
        assert r.passed is False

    def test_tool_must_not_exist_pass(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolPresenceRule("delete", must_exist=False).evaluate(s)
        assert r.passed is True

    def test_tool_must_not_exist_fail(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolPresenceRule("search", must_exist=False).evaluate(s)
        assert r.passed is False

    def test_empty_events(self):
        s = _make_tool_surface([])
        r = ToolPresenceRule("search", must_exist=True).evaluate(s)
        assert r.passed is False

    def test_not_a_list(self):
        s = _make_tool_surface("not a list")
        r = ToolPresenceRule("search").evaluate(s)
        assert r.passed is False


# =============================================================================
# TOOL COUNT
# =============================================================================

class TestToolCountRule:

    def test_exact_count_pass(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolCountRule("search", "==", 2).evaluate(s)
        assert r.passed is True

    def test_exact_count_fail(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolCountRule("search", "==", 1).evaluate(s)
        assert r.passed is False

    def test_max_count_pass(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolCountRule("search", "<=", 3).evaluate(s)
        assert r.passed is True

    def test_max_count_fail(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolCountRule("search", "<=", 1).evaluate(s)
        assert r.passed is False

    def test_min_count_pass(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolCountRule("search", ">=", 1).evaluate(s)
        assert r.passed is True

    def test_min_count_fail(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolCountRule("search", ">=", 5).evaluate(s)
        assert r.passed is False

    def test_count_zero(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolCountRule("delete", "==", 0).evaluate(s)
        assert r.passed is True

    def test_invalid_operator(self):
        with pytest.raises(ValueError):
            ToolCountRule("search", ">", 1)


# =============================================================================
# TOOL ARGUMENT
# =============================================================================

class TestToolArgumentRule:

    def test_arg_match_pass(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolArgumentRule("search", "limit", 10).evaluate(s)
        assert r.passed is True

    def test_arg_match_fail(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolArgumentRule("search", "limit", 20).evaluate(s)
        assert r.passed is False

    def test_arg_second_occurrence(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolArgumentRule("search", "limit", 5, occurrence=1).evaluate(s)
        assert r.passed is True

    def test_arg_boolean_strict(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolArgumentRule("write", "safe_mode", True).evaluate(s)
        assert r.passed is True

    def test_arg_no_coercion(self):
        """String "10" != int 10."""
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolArgumentRule("search", "limit", "10").evaluate(s)
        assert r.passed is False

    def test_arg_missing_path(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolArgumentRule("search", "nonexistent", "val").evaluate(s)
        assert r.passed is False

    def test_tool_not_found(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolArgumentRule("delete", "arg", "val").evaluate(s)
        assert r.passed is False

    def test_occurrence_out_of_range(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolArgumentRule("search", "limit", 10, occurrence=5).evaluate(s)
        assert r.passed is False


# =============================================================================
# TOOL ORDERING
# =============================================================================

class TestToolOrderingRule:

    def test_before_pass(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolOrderingRule("search", "write", "before").evaluate(s)
        assert r.passed is True

    def test_before_fail(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolOrderingRule("write", "search", "before").evaluate(s)
        assert r.passed is False

    def test_before_a_missing(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolOrderingRule("delete", "search", "before").evaluate(s)
        assert r.passed is False

    def test_before_b_missing(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolOrderingRule("search", "delete", "before").evaluate(s)
        assert r.passed is False

    def test_not_after_pass(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolOrderingRule("search", "write", "not_after").evaluate(s)
        assert r.passed is True

    def test_not_after_fail(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolOrderingRule("write", "search", "not_after").evaluate(s)
        assert r.passed is False

    def test_not_after_a_missing_passes(self):
        """If A is missing, constraint is satisfied (nothing violates)."""
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolOrderingRule("delete", "search", "not_after").evaluate(s)
        assert r.passed is True

    def test_not_after_b_missing_passes(self):
        s = _make_tool_surface(SAMPLE_EVENTS)
        r = ToolOrderingRule("search", "delete", "not_after").evaluate(s)
        assert r.passed is True

    def test_invalid_mode(self):
        with pytest.raises(ValueError):
            ToolOrderingRule("a", "b", "after")


# =============================================================================
# TOOL SURFACE ADAPTER
# =============================================================================

class TestToolSurfaceAdapter:

    def test_adapt(self):
        adapter = ToolSurfaceAdapter()
        events = [{"name": "search", "args": {}}]
        s = adapter.adapt(events)
        assert s.type == "tool_calls"
        assert s.raw_payload == events

    def test_adapt_preserves_order(self):
        adapter = ToolSurfaceAdapter()
        events = [
            {"name": "a", "args": {}},
            {"name": "b", "args": {}},
            {"name": "a", "args": {}},
        ]
        s = adapter.adapt(events)
        assert [e["name"] for e in s.raw_payload] == ["a", "b", "a"]

    def test_adapt_no_dedup(self):
        """No deduplication — duplicates preserved."""
        adapter = ToolSurfaceAdapter()
        events = [
            {"name": "search", "args": {"q": "test"}},
            {"name": "search", "args": {"q": "test"}},
        ]
        s = adapter.adapt(events)
        assert len(s.raw_payload) == 2

    def test_adapt_with_metadata(self):
        adapter = ToolSurfaceAdapter()
        s = adapter.adapt([], metadata={"agent": "v1"})
        assert s.metadata["agent"] == "v1"


# =============================================================================
# EVALUATOR INTEGRATION
# =============================================================================

class TestToolEvaluatorIntegration:

    def test_multi_rule_pass(self):
        ev = SurfaceEvaluator()
        ev.add_rule(ToolPresenceRule("search"))
        ev.add_rule(ToolCountRule("search", ">=", 1))
        ev.add_rule(ToolOrderingRule("search", "write", "before"))
        s = _make_tool_surface(SAMPLE_EVENTS)
        v = ev.evaluate(s)
        assert v.status == "pass"

    def test_multi_rule_fail(self):
        ev = SurfaceEvaluator()
        ev.add_rule(ToolPresenceRule("search"))
        ev.add_rule(ToolPresenceRule("delete"))  # Will fail
        s = _make_tool_surface(SAMPLE_EVENTS)
        v = ev.evaluate(s)
        assert v.status == "fail"
        assert len(v.violations) == 1
