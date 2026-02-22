"""
Multi-Step Execution Trace Enforcement Tests (Axis 2 Phase 2.3)

Tests:
- StepCountRule (exact/min/max)
- ForbiddenTransitionRule (consecutive stage prohibition)
- RequiredStageRule (stage must appear)
- ExecutionTraceSurfaceAdapter
"""

import pytest

from phylax._internal.surfaces.surface import Surface, SurfaceEvaluator
from phylax._internal.surfaces.execution_trace import (
    StepCountRule,
    ForbiddenTransitionRule,
    RequiredStageRule,
    ExecutionTraceSurfaceAdapter,
)


def _make_trace_surface(steps):
    return Surface(type="execution_trace", raw_payload=steps)


SAMPLE_STEPS = [
    {"stage": "init", "type": "setup", "metadata": {}},
    {"stage": "validate", "type": "check", "metadata": {}},
    {"stage": "process", "type": "transform", "metadata": {}},
    {"stage": "output", "type": "response", "metadata": {}},
]


# =============================================================================
# STEP COUNT
# =============================================================================

class TestStepCountRule:

    def test_exact_pass(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = StepCountRule("==", 4).evaluate(s)
        assert r.passed is True

    def test_exact_fail(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = StepCountRule("==", 3).evaluate(s)
        assert r.passed is False

    def test_max_pass(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = StepCountRule("<=", 10).evaluate(s)
        assert r.passed is True

    def test_max_fail(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = StepCountRule("<=", 2).evaluate(s)
        assert r.passed is False

    def test_min_pass(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = StepCountRule(">=", 3).evaluate(s)
        assert r.passed is True

    def test_min_fail(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = StepCountRule(">=", 10).evaluate(s)
        assert r.passed is False

    def test_empty_list(self):
        s = _make_trace_surface([])
        r = StepCountRule("==", 0).evaluate(s)
        assert r.passed is True

    def test_invalid_operator(self):
        with pytest.raises(ValueError):
            StepCountRule(">", 5)

    def test_not_a_list(self):
        s = _make_trace_surface("not a list")
        r = StepCountRule("==", 0).evaluate(s)
        assert r.passed is False


# =============================================================================
# FORBIDDEN TRANSITION
# =============================================================================

class TestForbiddenTransitionRule:

    def test_no_forbidden_pass(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = ForbiddenTransitionRule("init", "output").evaluate(s)
        assert r.passed is True  # init → validate, not init → output

    def test_forbidden_fail(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = ForbiddenTransitionRule("init", "validate").evaluate(s)
        assert r.passed is False  # init → validate is consecutive

    def test_forbidden_last_pair(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = ForbiddenTransitionRule("process", "output").evaluate(s)
        assert r.passed is False

    def test_non_consecutive_allowed(self):
        """Forbidden is only for consecutive transitions."""
        s = _make_trace_surface(SAMPLE_STEPS)
        r = ForbiddenTransitionRule("validate", "output").evaluate(s)
        assert r.passed is True  # validate → process → output, not consecutive

    def test_empty_list_pass(self):
        s = _make_trace_surface([])
        r = ForbiddenTransitionRule("a", "b").evaluate(s)
        assert r.passed is True

    def test_single_step_pass(self):
        s = _make_trace_surface([{"stage": "init", "type": "setup", "metadata": {}}])
        r = ForbiddenTransitionRule("init", "output").evaluate(s)
        assert r.passed is True

    def test_not_a_list(self):
        s = _make_trace_surface("not a list")
        r = ForbiddenTransitionRule("a", "b").evaluate(s)
        assert r.passed is False


# =============================================================================
# REQUIRED STAGE
# =============================================================================

class TestRequiredStageRule:

    def test_stage_present_pass(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = RequiredStageRule("init").evaluate(s)
        assert r.passed is True

    def test_stage_present_middle(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = RequiredStageRule("process").evaluate(s)
        assert r.passed is True

    def test_stage_missing_fail(self):
        s = _make_trace_surface(SAMPLE_STEPS)
        r = RequiredStageRule("cleanup").evaluate(s)
        assert r.passed is False

    def test_empty_list_fail(self):
        s = _make_trace_surface([])
        r = RequiredStageRule("init").evaluate(s)
        assert r.passed is False

    def test_not_a_list(self):
        s = _make_trace_surface("not a list")
        r = RequiredStageRule("init").evaluate(s)
        assert r.passed is False

    def test_exact_stage_match(self):
        """Stage must match exactly, no partial or case-insensitive."""
        s = _make_trace_surface(SAMPLE_STEPS)
        r = RequiredStageRule("Init").evaluate(s)
        assert r.passed is False  # "Init" != "init"


# =============================================================================
# EXECUTION TRACE ADAPTER
# =============================================================================

class TestExecutionTraceSurfaceAdapter:

    def test_adapt(self):
        adapter = ExecutionTraceSurfaceAdapter()
        s = adapter.adapt(SAMPLE_STEPS)
        assert s.type == "execution_trace"
        assert s.raw_payload == SAMPLE_STEPS

    def test_adapt_preserves_order(self):
        adapter = ExecutionTraceSurfaceAdapter()
        s = adapter.adapt(SAMPLE_STEPS)
        stages = [step["stage"] for step in s.raw_payload]
        assert stages == ["init", "validate", "process", "output"]

    def test_adapt_with_metadata(self):
        adapter = ExecutionTraceSurfaceAdapter()
        s = adapter.adapt([], metadata={"workflow": "pipeline_v2"})
        assert s.metadata["workflow"] == "pipeline_v2"


# =============================================================================
# EVALUATOR INTEGRATION
# =============================================================================

class TestExecutionTraceEvaluatorIntegration:

    def test_multi_rule_pass(self):
        ev = SurfaceEvaluator()
        ev.add_rule(StepCountRule("<=", 10))
        ev.add_rule(RequiredStageRule("init"))
        ev.add_rule(RequiredStageRule("output"))
        ev.add_rule(ForbiddenTransitionRule("init", "output"))
        s = _make_trace_surface(SAMPLE_STEPS)
        v = ev.evaluate(s)
        assert v.status == "pass"

    def test_multi_rule_fail(self):
        ev = SurfaceEvaluator()
        ev.add_rule(StepCountRule("<=", 10))
        ev.add_rule(RequiredStageRule("cleanup"))  # Will fail
        ev.add_rule(ForbiddenTransitionRule("init", "validate"))  # Will fail
        s = _make_trace_surface(SAMPLE_STEPS)
        v = ev.evaluate(s)
        assert v.status == "fail"
        assert len(v.violations) == 2
