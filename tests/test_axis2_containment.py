"""
Axis 2 — Semantic Containment Test Framework

PURPOSE: Prove the engine did NOT become intelligent.

This is not QA. This is semantic containment testing.

Every phase must pass 4 invariant categories:
  1. Determinism Tests
  2. Literalism Tests
  3. Mutation Resistance Tests
  4. Semantic Drift Tests

If any test fails, the phase is invalid.

Structure:
  - Phase 2.0 containment
  - Phase 2.1 containment
  - Phase 2.2 containment
  - Phase 2.3 containment
  - Phase 2.4 containment
  - Cross-Phase Meta Tests
"""

import copy
import hashlib
import inspect
import json

import pytest

from phylax import (
    Surface,
    SurfaceRule,
    SurfaceRuleResult,
    SurfaceVerdict,
    SurfaceAdapter,
    SurfaceEvaluator,
    SurfaceRegistry,
    TextSurfaceAdapter,
    FieldExistsRule,
    FieldNotExistsRule,
    TypeEnforcementRule,
    ExactValueRule,
    EnumEnforcementRule,
    ArrayBoundsRule,
    StructuredSurfaceAdapter,
    ToolPresenceRule,
    ToolCountRule,
    ToolArgumentRule,
    ToolOrderingRule,
    ToolSurfaceAdapter,
    StepCountRule,
    ForbiddenTransitionRule,
    RequiredStageRule,
    ExecutionTraceSurfaceAdapter,
    ExactStabilityRule,
    AllowedDriftRule,
    StabilitySurfaceAdapter,
)
# Private helper — not part of public API, imported directly for testing only
from phylax._internal.surfaces.stability import _deterministic_hash


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2.0 — SURFACE ABSTRACTION LAYER CONTAINMENT
# ═════════════════════════════════════════════════════════════════════════════

class TestPhase20_Determinism:
    """Same surface input twice → identical verdict. Always."""

    def test_same_text_surface_identical_verdict(self):
        s1 = Surface(type="text_output", raw_payload="Hello world")
        s2 = Surface(type="text_output", raw_payload="Hello world")

        class _PassIfHello(SurfaceRule):
            name = "check_hello"
            def evaluate(self, surface):
                passed = "Hello" in surface.raw_payload
                return SurfaceRuleResult(passed=passed, rule_name=self.name)

        ev = SurfaceEvaluator()
        ev.add_rule(_PassIfHello())
        v1 = ev.evaluate(s1)
        v2 = ev.evaluate(s2)
        assert v1.status == v2.status
        assert v1.violations == v2.violations

    def test_surface_ordering_irrelevant_deterministic(self):
        """Different surface ordering produces deterministic result."""
        payloads = [
            {"a": 1, "b": 2},
            {"b": 2, "a": 1},  # Reordered keys
        ]
        results = []
        for p in payloads:
            s = Surface(type="structured_output", raw_payload=p)
            rule = FieldExistsRule("a")
            results.append(rule.evaluate(s).passed)
        assert len(set(results)) == 1  # All identical

    def test_serialization_roundtrip_determinism(self):
        """Serialize → deserialize → enforce → identical result."""
        payload = {"name": "Alice", "scores": [10, 20, 30]}
        s_orig = Surface(type="structured_output", raw_payload=payload)

        # Serialize to JSON and back
        serialized = json.dumps(s_orig.raw_payload, sort_keys=True)
        deserialized = json.loads(serialized)

        s_round = Surface(type="structured_output", raw_payload=deserialized)
        rule = FieldExistsRule("name")
        r1 = rule.evaluate(s_orig)
        r2 = rule.evaluate(s_round)
        assert r1.passed == r2.passed


class TestPhase20_RawPayloadIntegrity:
    """Raw input must be preserved bit-for-bit. No canonicalization."""

    def test_whitespace_preserved(self):
        raw = "  Hello \t World \n  "
        s = Surface(type="text_output", raw_payload=raw)
        assert s.raw_payload == raw  # Exact match

    def test_no_key_reordering(self):
        raw = {"z": 1, "a": 2, "m": 3}
        s = Surface(type="structured_output", raw_payload=raw)
        assert list(s.raw_payload.keys()) == ["z", "a", "m"]

    def test_unicode_preserved(self):
        raw = "日本語テスト 🎯"
        s = Surface(type="text_output", raw_payload=raw)
        assert s.raw_payload == raw

    def test_nested_dict_preserved(self):
        raw = {"a": {"b": {"c": [1, {"d": True}]}}}
        s = Surface(type="structured_output", raw_payload=raw)
        assert s.raw_payload is raw  # Same object reference

    def test_empty_payload_preserved(self):
        for raw in ["", {}, [], None]:
            s = Surface(type="text_output", raw_payload=raw)
            assert s.raw_payload == raw

    def test_input_change_before_enforcement_detected(self):
        """If input changes, enforcement result must reflect the change."""
        payload = {"status": "ok"}
        s1 = Surface(type="structured_output", raw_payload=payload)
        r1 = ExactValueRule("status", "ok").evaluate(s1)
        assert r1.passed is True

        changed = {"status": "error"}
        s2 = Surface(type="structured_output", raw_payload=changed)
        r2 = ExactValueRule("status", "ok").evaluate(s2)
        assert r2.passed is False  # Different input → different result


class TestPhase20_EngineIsolation:
    """Engine core must not change. Only adapter layer changes."""

    def test_engine_rules_signature_unchanged(self):
        from phylax._internal.expectations.rules import Rule
        sig = inspect.signature(Rule.evaluate)
        params = list(sig.parameters.keys())
        assert params == ["self", "response_text", "latency_ms"]

    def test_engine_evaluator_signature_unchanged(self):
        from phylax._internal.expectations.evaluator import Evaluator
        sig = inspect.signature(Evaluator.evaluate)
        params = list(sig.parameters.keys())
        assert params == ["self", "response_text", "latency_ms"]

    def test_verdict_model_unchanged(self):
        import typing
        from phylax._internal.schema import Verdict
        args = typing.get_args(Verdict.model_fields["status"].annotation)
        assert set(args) == {"pass", "fail"}

    def test_engine_source_no_surface_imports(self):
        """Core engine files must not import surface modules."""
        from phylax._internal.expectations import rules, evaluator
        for mod in [rules, evaluator]:
            source = inspect.getsource(mod)
            assert "surfaces" not in source, (
                f"{mod.__name__} imports surfaces — engine isolation violated"
            )


class TestPhase20_SurfaceTypeBlindness:
    """Engine decision path must be identical regardless of surface type."""

    def test_evaluator_same_logic_for_all_types(self):
        """SurfaceEvaluator uses the same logic for all surface types."""
        class _CountFields(SurfaceRule):
            name = "field_check"
            def evaluate(self, surface):
                return SurfaceRuleResult(passed=True, rule_name=self.name)

        for surface_type in ["text_output", "structured_output", "tool_calls",
                             "execution_trace", "cross_run_snapshot"]:
            ev = SurfaceEvaluator()
            ev.add_rule(_CountFields())
            s = Surface(type=surface_type, raw_payload="anything")
            v = ev.evaluate(s)
            assert v.status == "pass"

    def test_evaluator_no_type_branching(self):
        """SurfaceEvaluator source must NOT branch on surface.type."""
        source = inspect.getsource(SurfaceEvaluator.evaluate)
        assert "surface.type" not in source
        assert "surface_type" not in source


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2.1 — STRUCTURED OUTPUT CONTAINMENT
# ═════════════════════════════════════════════════════════════════════════════

class TestPhase21_StrictEquality:
    """No implicit coercion. Ever."""

    def test_string_1_vs_int_1_fail(self):
        s = Surface(type="structured_output", raw_payload={"val": "1"})
        r = ExactValueRule("val", 1).evaluate(s)
        assert r.passed is False

    def test_int_1_vs_string_1_fail(self):
        s = Surface(type="structured_output", raw_payload={"val": 1})
        r = ExactValueRule("val", "1").evaluate(s)
        assert r.passed is False

    def test_approved_vs_APPROVED_fail(self):
        s = Surface(type="structured_output", raw_payload={"s": "Approved"})
        r = ExactValueRule("s", "approved").evaluate(s)
        assert r.passed is False

    def test_float_1_0_vs_int_1(self):
        """1.0 vs 1 — Python considers equal, but types differ.
        ExactValueRule checks value equality. 1.0 == 1 in Python.
        This is NOT coercion; it's Python's native == semantics."""
        s = Surface(type="structured_output", raw_payload={"val": 1.0})
        # Note: Python 1.0 == 1 is True. This is explicit language behavior,
        # not engine coercion. TypeEnforcementRule is the strict type gate.
        r = TypeEnforcementRule("val", "number").evaluate(s)
        assert r.passed is True  # Both are numbers

    def test_bool_true_not_int_1(self):
        s = Surface(type="structured_output", raw_payload={"val": True})
        r = TypeEnforcementRule("val", "number").evaluate(s)
        assert r.passed is False  # bool is NOT number

    def test_int_1_not_bool(self):
        s = Surface(type="structured_output", raw_payload={"val": 1})
        r = TypeEnforcementRule("val", "boolean").evaluate(s)
        assert r.passed is False

    def test_string_true_not_bool(self):
        s = Surface(type="structured_output", raw_payload={"val": "true"})
        r = TypeEnforcementRule("val", "boolean").evaluate(s)
        assert r.passed is False


class TestPhase21_FieldPresence:
    """Missing, extra, nested, and no default injection."""

    def test_missing_required_field_fail(self):
        s = Surface(type="structured_output", raw_payload={"name": "Alice"})
        r = FieldExistsRule("age").evaluate(s)
        assert r.passed is False

    def test_extra_undeclared_field_pass(self):
        """Extra fields not explicitly forbidden → PASS."""
        s = Surface(type="structured_output", raw_payload={"name": "Alice", "extra": 1})
        r = FieldExistsRule("name").evaluate(s)
        assert r.passed is True  # Extra field allowed unless explicitly forbidden

    def test_extra_field_explicitly_forbidden(self):
        s = Surface(type="structured_output", raw_payload={"name": "Alice", "extra": 1})
        r = FieldNotExistsRule("extra").evaluate(s)
        assert r.passed is False

    def test_nested_path_mismatch_fail(self):
        s = Surface(type="structured_output", raw_payload={"data": {"user": {}}})
        r = FieldExistsRule("data.user.name").evaluate(s)
        assert r.passed is False

    def test_no_automatic_default_insertion(self):
        """Engine must never insert default values."""
        payload = {"name": "Alice"}
        s = Surface(type="structured_output", raw_payload=payload)
        FieldExistsRule("age").evaluate(s)
        assert "age" not in payload  # Payload must not be modified


class TestPhase21_EnumEdgeCases:
    """No fuzzy matching, no trimming, no case folding."""

    def test_valid_enum_pass(self):
        s = Surface(type="structured_output", raw_payload={"color": "red"})
        r = EnumEnforcementRule("color", ["red", "green", "blue"]).evaluate(s)
        assert r.passed is True

    def test_near_match_fail(self):
        s = Surface(type="structured_output", raw_payload={"color": "redd"})
        r = EnumEnforcementRule("color", ["red", "green", "blue"]).evaluate(s)
        assert r.passed is False

    def test_case_mismatch_fail(self):
        s = Surface(type="structured_output", raw_payload={"color": "Red"})
        r = EnumEnforcementRule("color", ["red", "green", "blue"]).evaluate(s)
        assert r.passed is False

    def test_value_with_whitespace_fail(self):
        s = Surface(type="structured_output", raw_payload={"color": " red "})
        r = EnumEnforcementRule("color", ["red", "green", "blue"]).evaluate(s)
        assert r.passed is False

    def test_type_mismatch_in_enum(self):
        s = Surface(type="structured_output", raw_payload={"val": 1})
        r = EnumEnforcementRule("val", ["1", "2", "3"]).evaluate(s)
        assert r.passed is False  # int 1 is NOT in string list


class TestPhase21_SchemaAbsence:
    """Without declared schema/rules, no enforcement triggered."""

    def test_no_rules_no_enforcement(self):
        ev = SurfaceEvaluator()
        s = Surface(type="structured_output", raw_payload={"any": "thing"})
        v = ev.evaluate(s)
        assert v.status == "pass"  # No rules → pass

    def test_no_auto_schema_detection(self):
        """Engine must NOT auto-detect schema from data."""
        from phylax._internal.surfaces import structured
        source = inspect.getsource(structured)
        for forbidden in ["infer_schema", "auto_schema", "generate_schema",
                          "detect_schema", "guess_schema"]:
            assert forbidden not in source.lower()


class TestPhase21_JSONParsingEdges:
    """Malformed, partial, and edge-case JSON handling."""

    def test_malformed_json_string_fails_deterministically(self):
        """Non-dict payload → field checks must fail deterministically."""
        s = Surface(type="structured_output", raw_payload="not json")
        r = FieldExistsRule("key").evaluate(s)
        assert r.passed is False

    def test_partially_valid_structure_fails(self):
        s = Surface(type="structured_output", raw_payload={"valid": True})
        r = FieldExistsRule("missing_key").evaluate(s)
        assert r.passed is False

    def test_none_payload(self):
        s = Surface(type="structured_output", raw_payload=None)
        r = FieldExistsRule("key").evaluate(s)
        assert r.passed is False

    def test_list_payload_not_dict(self):
        s = Surface(type="structured_output", raw_payload=[1, 2, 3])
        r = FieldExistsRule("key").evaluate(s)
        assert r.passed is False


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2.2 — TOOL & FUNCTION CALL CONTAINMENT
# ═════════════════════════════════════════════════════════════════════════════

TOOL_TRACE_WITH_NOISE = [
    {"name": "search", "args": {"q": "test", "limit": 10}},
    {"name": "search", "args": {"q": "test", "limit": 10}},  # Retry (duplicate)
    {"name": "noop", "args": {}},  # No-op call
    {"name": "read", "args": {"url": "http://example.com"}},
    {"name": "search", "args": {"q": "final", "limit": 5}},  # Rapid sequence
]


class TestPhase22_RawTraceIntegrity:
    """No deduplication, no retry collapsing, no cleaning."""

    def test_no_deduplication(self):
        """Duplicate calls must be preserved."""
        s = Surface(type="tool_calls", raw_payload=TOOL_TRACE_WITH_NOISE)
        r = ToolCountRule("search", "==", 3).evaluate(s)
        assert r.passed is True  # All 3 search calls counted

    def test_no_retry_collapsing(self):
        """Back-to-back identical calls are NOT collapsed."""
        s = Surface(type="tool_calls", raw_payload=TOOL_TRACE_WITH_NOISE)
        r = ToolCountRule("search", "==", 2).evaluate(s)
        assert r.passed is False  # There are 3, not 2

    def test_noop_calls_counted(self):
        s = Surface(type="tool_calls", raw_payload=TOOL_TRACE_WITH_NOISE)
        r = ToolPresenceRule("noop", must_exist=True).evaluate(s)
        assert r.passed is True

    def test_adapter_preserves_all_events(self):
        adapter = ToolSurfaceAdapter()
        s = adapter.adapt(TOOL_TRACE_WITH_NOISE)
        assert len(s.raw_payload) == 5  # All events preserved


class TestPhase22_CallCountStrict:
    """Exactly N calls. Zero tolerance."""

    def test_exactly_n_pass(self):
        events = [{"name": "search", "args": {}}] * 3
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolCountRule("search", "==", 3).evaluate(s)
        assert r.passed is True

    def test_n_plus_1_fail(self):
        events = [{"name": "search", "args": {}}] * 4
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolCountRule("search", "==", 3).evaluate(s)
        assert r.passed is False

    def test_n_minus_1_fail(self):
        events = [{"name": "search", "args": {}}] * 2
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolCountRule("search", "==", 3).evaluate(s)
        assert r.passed is False


class TestPhase22_OrderingWithNoise:
    """Order evaluation is index-based only. Noise between is irrelevant."""

    def test_a_before_c_pass(self):
        events = [
            {"name": "A", "args": {}},
            {"name": "B", "args": {}},
            {"name": "C", "args": {}},
        ]
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolOrderingRule("A", "C", "before").evaluate(s)
        assert r.passed is True

    def test_c_before_a_fail(self):
        events = [
            {"name": "C", "args": {}},
            {"name": "B", "args": {}},
            {"name": "A", "args": {}},
        ]
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolOrderingRule("A", "C", "before").evaluate(s)
        assert r.passed is False

    def test_noise_between_still_passes(self):
        """A → X → C: A before C still passes."""
        events = [
            {"name": "A", "args": {}},
            {"name": "X", "args": {}},  # Noise
            {"name": "Y", "args": {}},  # Noise
            {"name": "C", "args": {}},
        ]
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolOrderingRule("A", "C", "before").evaluate(s)
        assert r.passed is True


class TestPhase22_ArgumentLiteralism:
    """Strict argument comparison. No coercion."""

    def test_string_10_vs_int_10_fail(self):
        events = [{"name": "search", "args": {"limit": 10}}]
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolArgumentRule("search", "limit", "10").evaluate(s)
        assert r.passed is False  # "10" != 10

    def test_string_true_vs_bool_true_fail(self):
        events = [{"name": "write", "args": {"safe_mode": True}}]
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolArgumentRule("write", "safe_mode", "true").evaluate(s)
        assert r.passed is False  # "true" != True

    def test_missing_arg_fail(self):
        events = [{"name": "search", "args": {"q": "test"}}]
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolArgumentRule("search", "limit", 10).evaluate(s)
        assert r.passed is False


class TestPhase22_ForbiddenInterpretation:
    """Engine must not evaluate quality or necessity."""

    def test_no_quality_assessment_in_source(self):
        from phylax._internal.surfaces import tools
        source = inspect.getsource(tools)
        for forbidden in ["assess_quality", "is_useful", "should_call",
                          "evaluate_necessity", "quality_score"]:
            assert forbidden not in source.lower(), (
                f"tools.py contains interpretation logic: {forbidden}"
            )


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2.3 — MULTI-STEP EXECUTION TRACE CONTAINMENT
# ═════════════════════════════════════════════════════════════════════════════

class TestPhase23_StepCountBoundary:
    """Exact boundaries. No context-based exceptions."""

    def test_exactly_max_steps_pass(self):
        steps = [{"stage": f"s{i}", "type": "t", "metadata": {}} for i in range(5)]
        s = Surface(type="execution_trace", raw_payload=steps)
        r = StepCountRule("<=", 5).evaluate(s)
        assert r.passed is True

    def test_max_steps_plus_1_fail(self):
        steps = [{"stage": f"s{i}", "type": "t", "metadata": {}} for i in range(6)]
        s = Surface(type="execution_trace", raw_payload=steps)
        r = StepCountRule("<=", 5).evaluate(s)
        assert r.passed is False

    def test_under_min_steps_fail(self):
        steps = [{"stage": "s0", "type": "t", "metadata": {}}]
        s = Surface(type="execution_trace", raw_payload=steps)
        r = StepCountRule(">=", 3).evaluate(s)
        assert r.passed is False


class TestPhase23_ForbiddenTransitions:
    """Only adjacent transitions evaluated."""

    def test_a_b_c_forbidden_a_c_pass(self):
        """A → B → C with forbidden A → C → PASS (not adjacent)."""
        steps = [
            {"stage": "A", "type": "t", "metadata": {}},
            {"stage": "B", "type": "t", "metadata": {}},
            {"stage": "C", "type": "t", "metadata": {}},
        ]
        s = Surface(type="execution_trace", raw_payload=steps)
        r = ForbiddenTransitionRule("A", "C").evaluate(s)
        assert r.passed is True

    def test_a_c_direct_forbidden_fail(self):
        """A → C directly → FAIL."""
        steps = [
            {"stage": "A", "type": "t", "metadata": {}},
            {"stage": "C", "type": "t", "metadata": {}},
        ]
        s = Surface(type="execution_trace", raw_payload=steps)
        r = ForbiddenTransitionRule("A", "C").evaluate(s)
        assert r.passed is False


class TestPhase23_RequiredStages:
    """Stage presence enforcement."""

    def test_missing_required_stage_fail(self):
        steps = [{"stage": "init", "type": "t", "metadata": {}}]
        s = Surface(type="execution_trace", raw_payload=steps)
        r = RequiredStageRule("cleanup").evaluate(s)
        assert r.passed is False

    def test_stage_present_twice_pass(self):
        """Stage appearing twice → PASS (no redundancy reasoning)."""
        steps = [
            {"stage": "init", "type": "t", "metadata": {}},
            {"stage": "process", "type": "t", "metadata": {}},
            {"stage": "init", "type": "t", "metadata": {}},  # Repeated
        ]
        s = Surface(type="execution_trace", raw_payload=steps)
        r = RequiredStageRule("init").evaluate(s)
        assert r.passed is True  # Stage exists, that's all that matters


class TestPhase23_LoopBehavior:
    """Engine must NOT infer looping inefficiency."""

    def test_loop_without_explicit_rule_passes(self):
        """A → B → A → B → A: no explicit loop rule → PASS."""
        steps = [
            {"stage": "A", "type": "t", "metadata": {}},
            {"stage": "B", "type": "t", "metadata": {}},
            {"stage": "A", "type": "t", "metadata": {}},
            {"stage": "B", "type": "t", "metadata": {}},
            {"stage": "A", "type": "t", "metadata": {}},
        ]
        s = Surface(type="execution_trace", raw_payload=steps)

        # Only explicit rules should fire. No loop detection.
        ev = SurfaceEvaluator()
        ev.add_rule(RequiredStageRule("A"))
        ev.add_rule(RequiredStageRule("B"))
        v = ev.evaluate(s)
        assert v.status == "pass"

    def test_no_loop_detection_in_source(self):
        from phylax._internal.surfaces import execution_trace
        source = inspect.getsource(execution_trace)
        for forbidden in ["loop_detect", "cycle_detect", "infinite_loop",
                          "repeated_pattern"]:
            assert forbidden not in source.lower()


class TestPhase23_ConditionalRuleRejection:
    """No conditional branching based on step output."""

    def test_no_conditional_logic_in_rules(self):
        """Execution trace rules must not accept conditions based on step output."""
        from phylax._internal.surfaces import execution_trace
        source = inspect.getsource(execution_trace)
        for forbidden in ["if_output", "when_result", "conditional_stage",
                          "dynamic_rule"]:
            assert forbidden not in source.lower()


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2.4 — CROSS-RUN STABILITY CONTAINMENT
# ═════════════════════════════════════════════════════════════════════════════

BASELINE_SNAP = {
    "version_id": "v1",
    "structured_output": {"status": "ok", "count": 42},
    "tool_trace": [{"name": "search", "args": {"q": "test"}}],
    "timestamp": "2026-01-01T00:00:00",
    "metadata": {"execution_id": "exec-1", "model": "gpt-4"},
}


class TestPhase24_ExactSnapshotComparison:
    """Binary pass/fail on snapshot comparison."""

    def test_identical_snapshot_pass(self):
        current = copy.deepcopy(BASELINE_SNAP)
        s = Surface(type="cross_run_snapshot",
                    raw_payload={"baseline": BASELINE_SNAP, "current": current})
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is True

    def test_one_character_change_fail(self):
        current = copy.deepcopy(BASELINE_SNAP)
        current["structured_output"]["status"] = "ok!"  # One char added
        s = Surface(type="cross_run_snapshot",
                    raw_payload={"baseline": BASELINE_SNAP, "current": current})
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is False

    def test_reordered_json_keys_deterministic(self):
        """JSON key reorder → hash uses sorted keys → deterministic."""
        b1 = {"a": 1, "b": 2, "c": 3}
        b2 = {"c": 3, "a": 1, "b": 2}
        assert _deterministic_hash(b1) == _deterministic_hash(b2)


class TestPhase24_AllowedDriftRegions:
    """Whitelist must be explicit. Only whitelisted fields may change."""

    def test_timestamp_whitelisted_pass(self):
        current = copy.deepcopy(BASELINE_SNAP)
        current["timestamp"] = "2026-12-31T23:59:59"
        s = Surface(type="cross_run_snapshot",
                    raw_payload={"baseline": BASELINE_SNAP, "current": current})
        r = AllowedDriftRule(allowed_fields=["timestamp"]).evaluate(s)
        assert r.passed is True

    def test_non_whitelisted_field_change_fail(self):
        current = copy.deepcopy(BASELINE_SNAP)
        current["timestamp"] = "2026-12-31T23:59:59"
        current["version_id"] = "v999"  # NOT whitelisted
        s = Surface(type="cross_run_snapshot",
                    raw_payload={"baseline": BASELINE_SNAP, "current": current})
        r = AllowedDriftRule(allowed_fields=["timestamp"]).evaluate(s)
        assert r.passed is False


class TestPhase24_BaselineMutationDetection:
    """Engine must detect baseline tampering."""

    def test_modified_baseline_detected(self):
        original_baseline = copy.deepcopy(BASELINE_SNAP)
        current = copy.deepcopy(BASELINE_SNAP)

        # Silently modify baseline
        tampered_baseline = copy.deepcopy(original_baseline)
        tampered_baseline["structured_output"]["count"] = 999

        s = Surface(type="cross_run_snapshot",
                    raw_payload={"baseline": tampered_baseline, "current": current})
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is False  # Mismatch detected

    def test_no_auto_baseline_updating_in_source(self):
        from phylax._internal.surfaces import stability
        source = inspect.getsource(stability)
        for forbidden in ["auto_update", "auto_baseline", "self_update",
                          "update_baseline"]:
            assert forbidden not in source.lower()


class TestPhase24_FuzzyToleranceRejection:
    """No fuzzy tolerance allowed."""

    def test_no_fuzzy_matching_in_source(self):
        from phylax._internal.surfaces import stability
        source = inspect.getsource(stability)
        for forbidden in ["fuzzy", "approximate", "similar",
                          "close_enough", "within_range"]:
            assert forbidden not in source.lower()

    def test_no_percentage_tolerance(self):
        """No percentage-based tolerance mechanisms."""
        from phylax._internal.surfaces import stability
        source = inspect.getsource(stability)
        for forbidden in ["percent_diff", "tolerance_pct", "margin_of_error"]:
            assert forbidden not in source.lower()


# ═════════════════════════════════════════════════════════════════════════════
# CROSS-PHASE META TESTS
# ═════════════════════════════════════════════════════════════════════════════

class TestMetaCrossPhase_DeterminismSweep:
    """Run same enforcement 100 times. Hash verdict. Any mismatch → FAIL."""

    def test_structured_100_runs(self):
        payload = {"name": "Alice", "status": "ok", "count": 42}
        verdicts = set()
        for _ in range(100):
            ev = SurfaceEvaluator()
            ev.add_rule(FieldExistsRule("name"))
            ev.add_rule(ExactValueRule("status", "ok"))
            ev.add_rule(TypeEnforcementRule("count", "number"))
            s = Surface(type="structured_output", raw_payload=payload)
            v = ev.evaluate(s)
            verdicts.add((v.status, tuple(v.violations)))
        assert len(verdicts) == 1  # All identical

    def test_tool_100_runs(self):
        events = [
            {"name": "search", "args": {"q": "test", "limit": 10}},
            {"name": "write", "args": {"data": "result"}},
        ]
        verdicts = set()
        for _ in range(100):
            ev = SurfaceEvaluator()
            ev.add_rule(ToolPresenceRule("search"))
            ev.add_rule(ToolCountRule("search", "==", 1))
            ev.add_rule(ToolOrderingRule("search", "write", "before"))
            s = Surface(type="tool_calls", raw_payload=events)
            v = ev.evaluate(s)
            verdicts.add((v.status, tuple(v.violations)))
        assert len(verdicts) == 1

    def test_trace_100_runs(self):
        steps = [
            {"stage": "init", "type": "t", "metadata": {}},
            {"stage": "process", "type": "t", "metadata": {}},
            {"stage": "output", "type": "t", "metadata": {}},
        ]
        verdicts = set()
        for _ in range(100):
            ev = SurfaceEvaluator()
            ev.add_rule(StepCountRule("==", 3))
            ev.add_rule(RequiredStageRule("init"))
            ev.add_rule(ForbiddenTransitionRule("init", "output"))
            s = Surface(type="execution_trace", raw_payload=steps)
            v = ev.evaluate(s)
            verdicts.add((v.status, tuple(v.violations)))
        assert len(verdicts) == 1

    def test_stability_100_runs(self):
        baseline = {"a": 1, "b": 2}
        current = {"a": 1, "b": 2}
        verdicts = set()
        for _ in range(100):
            ev = SurfaceEvaluator()
            ev.add_rule(ExactStabilityRule())
            s = Surface(type="cross_run_snapshot",
                        raw_payload={"baseline": baseline, "current": current})
            v = ev.evaluate(s)
            verdicts.add((v.status, tuple(v.violations)))
        assert len(verdicts) == 1


class TestMetaCrossPhase_RandomNoiseInjection:
    """Irrelevant metadata must not influence verdict."""

    def test_metadata_does_not_affect_structured_verdict(self):
        payload = {"status": "ok"}
        rule = ExactValueRule("status", "ok")

        s1 = Surface(type="structured_output", raw_payload=payload, metadata={})
        s2 = Surface(type="structured_output", raw_payload=payload,
                     metadata={"noise": "random", "timestamp": "now", "x": 42})
        assert rule.evaluate(s1).passed == rule.evaluate(s2).passed

    def test_metadata_does_not_affect_tool_verdict(self):
        events = [{"name": "search", "args": {"q": "test"}}]
        rule = ToolPresenceRule("search")

        s1 = Surface(type="tool_calls", raw_payload=events, metadata={})
        s2 = Surface(type="tool_calls", raw_payload=events,
                     metadata={"irrelevant": True})
        assert rule.evaluate(s1).passed == rule.evaluate(s2).passed

    def test_metadata_does_not_affect_trace_verdict(self):
        steps = [{"stage": "init", "type": "t", "metadata": {}}]
        rule = RequiredStageRule("init")

        s1 = Surface(type="execution_trace", raw_payload=steps, metadata={})
        s2 = Surface(type="execution_trace", raw_payload=steps,
                     metadata={"noise": [1, 2, 3]})
        assert rule.evaluate(s1).passed == rule.evaluate(s2).passed


class TestMetaCrossPhase_SurfaceIsolation:
    """No cross-surface leakage between enforcement types."""

    def test_structured_rules_dont_leak_to_tools(self):
        """Structured rules operate only on structured surfaces."""
        tool_surface = Surface(type="tool_calls",
                               raw_payload=[{"name": "search", "args": {}}])
        # FieldExistsRule should fail on non-dict payload
        r = FieldExistsRule("name").evaluate(tool_surface)
        assert r.passed is False  # List is not a dict → fails cleanly

    def test_tool_rules_dont_leak_to_structured(self):
        """Tool rules operate only on tool surfaces."""
        struct_surface = Surface(type="structured_output",
                                 raw_payload={"name": "search"})
        # ToolPresenceRule expects list payload
        r = ToolPresenceRule("search").evaluate(struct_surface)
        assert r.passed is False  # Dict is not a list → fails cleanly

    def test_trace_rules_dont_leak_to_stability(self):
        """Trace rules operate only on trace surfaces."""
        stability_surface = Surface(type="cross_run_snapshot",
                                    raw_payload={"baseline": {}, "current": {}})
        r = StepCountRule("==", 0).evaluate(stability_surface)
        assert r.passed is False  # Dict is not a list

    def test_stability_rules_dont_leak_to_traces(self):
        trace_surface = Surface(type="execution_trace",
                                raw_payload=[{"stage": "init"}])
        r = ExactStabilityRule().evaluate(trace_surface)
        # List has no "baseline"/"current" keys
        assert r.passed is False


class TestMetaCrossPhase_ShouldUnderstand:
    """Adversarial cases: engine must NOT interpret intent."""

    def test_retry_not_collapsed(self):
        """Tool called twice due to retry. Contract: exactly once. Must FAIL."""
        events = [
            {"name": "deploy", "args": {"env": "prod"}},
            {"name": "deploy", "args": {"env": "prod"}},  # Retry
        ]
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolCountRule("deploy", "==", 1).evaluate(s)
        assert r.passed is False  # 2 calls, not 1. No retry inference.

    def test_stage_repeated_not_pruned(self):
        """Stage repeated. Engine must not prune 'redundant' stages."""
        steps = [
            {"stage": "validate", "type": "t", "metadata": {}},
            {"stage": "validate", "type": "t", "metadata": {}},
            {"stage": "validate", "type": "t", "metadata": {}},
        ]
        s = Surface(type="execution_trace", raw_payload=steps)
        r = StepCountRule("==", 3).evaluate(s)
        assert r.passed is True  # All 3 steps counted

    def test_value_looks_wrong_but_matches_contract(self):
        """Output says status='error' but contract expects 'error' → PASS."""
        s = Surface(type="structured_output", raw_payload={"status": "error"})
        r = ExactValueRule("status", "error").evaluate(s)
        assert r.passed is True  # Engine doesn't judge, it enforces

    def test_baseline_drift_looks_harmless_still_fails(self):
        """Tiny change that 'looks harmless' must still FAIL."""
        baseline = {"output": "Hello, World!"}
        current = {"output": "Hello, World! "}  # Trailing space
        s = Surface(type="cross_run_snapshot",
                    raw_payload={"baseline": baseline, "current": current})
        r = ExactStabilityRule().evaluate(s)
        assert r.passed is False  # Exact = exact. No "harmless" exceptions.

    def test_tools_out_of_expected_context_still_counted(self):
        """Tools called in unexpected context are still counted literally."""
        events = [
            {"name": "search", "args": {"q": "wrong query"}},  # "Wrong" but still a call
            {"name": "search", "args": {"q": "right query"}},
        ]
        s = Surface(type="tool_calls", raw_payload=events)
        r = ToolCountRule("search", "==", 2).evaluate(s)
        assert r.passed is True  # No quality judgment


# ═════════════════════════════════════════════════════════════════════════════
# AXIS 2 READINESS CHECK — GLOBAL INVARIANTS
# ═════════════════════════════════════════════════════════════════════════════

class TestAxis2ReadinessCheck:
    """
    Axis 2 is complete only if:
    - Every test suite passes
    - No rule type requires interpretation
    - No dynamic branching exists
    - No soft logic detected
    - Engine core remains unchanged from Axis 1
    """

    def test_no_rule_requires_interpretation(self):
        """All surface rule modules must not contain interpretation logic."""
        from phylax._internal.surfaces import structured, tools, execution_trace, stability
        for mod in [structured, tools, execution_trace, stability]:
            source = inspect.getsource(mod)
            for forbidden in ["interpret", "understand", "reason_about",
                              "likely", "probably", "suggest"]:
                assert forbidden not in source.lower(), (
                    f"{mod.__name__} contains interpretation word: {forbidden}"
                )

    def test_no_dynamic_branching_in_rules(self):
        """No dynamic dispatch based on data content."""
        from phylax._internal.surfaces import structured, tools, execution_trace, stability
        for mod in [structured, tools, execution_trace, stability]:
            source = inspect.getsource(mod)
            for forbidden in ["dynamic_dispatch", "auto_detect_type",
                              "smart_match", "best_effort"]:
                assert forbidden not in source.lower()

    def test_engine_core_file_hashes_stable(self):
        """Core engine files must exist and not import surface logic."""
        from phylax._internal.expectations import rules, evaluator
        from phylax._internal import schema
        for mod in [rules, evaluator, schema]:
            source = inspect.getsource(mod)
            assert "from phylax._internal.surfaces" not in source
            assert "import surfaces" not in source

    def test_surface_verdict_still_binary(self):
        """SurfaceVerdict must only allow 'pass' or 'fail'."""
        import typing
        args = typing.get_args(SurfaceVerdict.model_fields["status"].annotation)
        assert set(args) == {"pass", "fail"}
