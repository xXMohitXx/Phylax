"""
Surface Abstraction Layer Tests (Axis 2 Phase 2.0)

Tests:
- Surface model creation and immutability
- SurfaceRegistry operations
- SurfaceAdapter pipeline
- SurfaceEvaluator verdict production
- Raw payload preservation (no normalization)
- TextSurfaceAdapter
- Engine integrity (no engine code modified)
"""

import pytest
import uuid
from pydantic import ValidationError

from phylax import (
    Surface,
    SurfaceRuleResult,
    SurfaceVerdict,
    SurfaceRule,
    SurfaceAdapter,
    SurfaceEvaluator,
    SurfaceRegistry,
    get_registry,
    TextSurfaceAdapter,
)


# =============================================================================
# SURFACE MODEL
# =============================================================================

class TestSurfaceModel:
    """Surface model creation, immutability, and raw payload preservation."""

    def test_surface_creation_text(self):
        """Surface can be created with text payload."""
        s = Surface(type="text_output", raw_payload="Hello, world!")
        assert s.type == "text_output"
        assert s.raw_payload == "Hello, world!"
        assert isinstance(s.id, str)
        assert len(s.id) > 0

    def test_surface_creation_structured(self):
        """Surface can be created with dict payload."""
        payload = {"name": "Alice", "age": 30}
        s = Surface(type="structured_output", raw_payload=payload)
        assert s.type == "structured_output"
        assert s.raw_payload == payload

    def test_surface_creation_tool_calls(self):
        """Surface can be created with list payload."""
        payload = [{"name": "search", "args": {"q": "test"}}]
        s = Surface(type="tool_calls", raw_payload=payload)
        assert s.type == "tool_calls"
        assert s.raw_payload == payload

    def test_surface_is_frozen(self):
        """Surface is immutable after creation."""
        s = Surface(type="text_output", raw_payload="test")
        with pytest.raises(ValidationError):
            s.type = "structured_output"

    def test_surface_raw_payload_preserved_exactly(self):
        """Raw payload is preserved without any modification."""
        # String with whitespace, special chars
        raw = "  Hello \t World \n  "
        s = Surface(type="text_output", raw_payload=raw)
        assert s.raw_payload == raw  # Exact match, no trimming

    def test_surface_raw_payload_dict_preserved(self):
        """Dict payload is not normalized or reordered."""
        raw = {"z_key": 1, "a_key": 2, "m_key": 3}
        s = Surface(type="structured_output", raw_payload=raw)
        assert s.raw_payload == raw

    def test_surface_metadata_default_empty(self):
        """Metadata defaults to empty dict."""
        s = Surface(type="text_output", raw_payload="test")
        assert s.metadata == {}

    def test_surface_metadata_custom(self):
        """Custom metadata is preserved."""
        meta = {"provider": "openai", "model": "gpt-4"}
        s = Surface(type="text_output", raw_payload="test", metadata=meta)
        assert s.metadata == meta

    def test_surface_auto_id(self):
        """Each surface gets a unique auto-generated ID."""
        s1 = Surface(type="text_output", raw_payload="a")
        s2 = Surface(type="text_output", raw_payload="b")
        assert s1.id != s2.id


# =============================================================================
# SURFACE RULE RESULT
# =============================================================================

class TestSurfaceRuleResult:
    """SurfaceRuleResult creation and repr."""

    def test_passing_result(self):
        r = SurfaceRuleResult(passed=True, rule_name="test_rule")
        assert r.passed is True
        assert r.rule_name == "test_rule"
        assert r.violation_message == ""
        assert "PASS" in repr(r)

    def test_failing_result(self):
        r = SurfaceRuleResult(
            passed=False,
            rule_name="test_rule",
            violation_message="field missing"
        )
        assert r.passed is False
        assert "FAIL" in repr(r)
        assert r.violation_message == "field missing"


# =============================================================================
# SURFACE VERDICT
# =============================================================================

class TestSurfaceVerdict:
    """SurfaceVerdict is binary PASS/FAIL, frozen."""

    def test_verdict_pass(self):
        v = SurfaceVerdict(status="pass", surface_id="abc")
        assert v.status == "pass"
        assert v.violations == []

    def test_verdict_fail(self):
        v = SurfaceVerdict(
            status="fail",
            violations=["[rule] violation"],
            surface_id="abc",
        )
        assert v.status == "fail"
        assert len(v.violations) == 1

    def test_verdict_is_frozen(self):
        v = SurfaceVerdict(status="pass", surface_id="abc")
        with pytest.raises(ValidationError):
            v.status = "fail"

    def test_verdict_only_pass_fail(self):
        """Verdict status must be only 'pass' or 'fail'."""
        with pytest.raises(ValidationError):
            SurfaceVerdict(status="warn", surface_id="abc")


# =============================================================================
# SURFACE EVALUATOR
# =============================================================================

class _AlwaysPassRule(SurfaceRule):
    name = "always_pass"
    def evaluate(self, surface):
        return SurfaceRuleResult(passed=True, rule_name=self.name)

class _AlwaysFailRule(SurfaceRule):
    name = "always_fail"
    def evaluate(self, surface):
        return SurfaceRuleResult(
            passed=False,
            rule_name=self.name,
            violation_message="always fails"
        )


class TestSurfaceEvaluator:
    """SurfaceEvaluator produces binary verdicts from rules."""

    def test_no_rules_passes(self):
        """No rules → PASS."""
        ev = SurfaceEvaluator()
        s = Surface(type="text_output", raw_payload="test")
        v = ev.evaluate(s)
        assert v.status == "pass"
        assert v.violations == []

    def test_all_pass(self):
        ev = SurfaceEvaluator()
        ev.add_rule(_AlwaysPassRule())
        ev.add_rule(_AlwaysPassRule())
        s = Surface(type="text_output", raw_payload="test")
        v = ev.evaluate(s)
        assert v.status == "pass"

    def test_one_fail(self):
        ev = SurfaceEvaluator()
        ev.add_rule(_AlwaysPassRule())
        ev.add_rule(_AlwaysFailRule())
        s = Surface(type="text_output", raw_payload="test")
        v = ev.evaluate(s)
        assert v.status == "fail"
        assert len(v.violations) == 1

    def test_all_fail(self):
        ev = SurfaceEvaluator()
        ev.add_rule(_AlwaysFailRule())
        ev.add_rule(_AlwaysFailRule())
        s = Surface(type="text_output", raw_payload="test")
        v = ev.evaluate(s)
        assert v.status == "fail"
        assert len(v.violations) == 2

    def test_chaining(self):
        ev = SurfaceEvaluator()
        result = ev.add_rule(_AlwaysPassRule())
        assert result is ev  # Fluent API

    def test_no_short_circuit(self):
        """All rules must be evaluated even after a failure."""
        ev = SurfaceEvaluator()
        ev.add_rule(_AlwaysFailRule())
        ev.add_rule(_AlwaysFailRule())
        s = Surface(type="text_output", raw_payload="test")
        v = ev.evaluate(s)
        assert len(v.violations) == 2  # Both evaluated

    def test_verdict_contains_surface_id(self):
        ev = SurfaceEvaluator()
        s = Surface(type="text_output", raw_payload="test")
        v = ev.evaluate(s)
        assert v.surface_id == s.id


# =============================================================================
# SURFACE REGISTRY
# =============================================================================

class TestSurfaceRegistry:
    """SurfaceRegistry manages surface type metadata."""

    def test_builtin_types_registered(self):
        reg = SurfaceRegistry()
        assert reg.exists("text_output")
        assert reg.exists("structured_output")
        assert reg.exists("tool_calls")
        assert reg.exists("execution_trace")
        assert reg.exists("cross_run_snapshot")

    def test_list_types(self):
        reg = SurfaceRegistry()
        types = reg.list_types()
        assert len(types) == 5
        assert "text_output" in types

    def test_custom_registration(self):
        reg = SurfaceRegistry()
        reg.register("custom_type", description="Custom")
        assert reg.exists("custom_type")
        assert reg.get("custom_type")["description"] == "Custom"

    def test_duplicate_registration_raises(self):
        reg = SurfaceRegistry()
        with pytest.raises(ValueError):
            reg.register("text_output")

    def test_unknown_type_raises(self):
        reg = SurfaceRegistry()
        with pytest.raises(KeyError):
            reg.get("nonexistent")

    def test_clear(self):
        reg = SurfaceRegistry()
        reg.clear()
        assert reg.list_types() == []

    def test_global_registry_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2


# =============================================================================
# TEXT SURFACE ADAPTER
# =============================================================================

class TestTextSurfaceAdapter:
    """TextSurfaceAdapter wraps text into Surface."""

    def test_adapt_text(self):
        adapter = TextSurfaceAdapter()
        s = adapter.adapt("Hello, world!")
        assert s.type == "text_output"
        assert s.raw_payload == "Hello, world!"

    def test_adapt_preserves_whitespace(self):
        adapter = TextSurfaceAdapter()
        raw = "  spaces  and\ttabs\n"
        s = adapter.adapt(raw)
        assert s.raw_payload == raw

    def test_adapt_with_metadata(self):
        adapter = TextSurfaceAdapter()
        s = adapter.adapt("test", metadata={"model": "gpt-4"})
        assert s.metadata["model"] == "gpt-4"

    def test_adapt_empty_string(self):
        adapter = TextSurfaceAdapter()
        s = adapter.adapt("")
        assert s.raw_payload == ""
        assert s.type == "text_output"


# =============================================================================
# ENGINE INTEGRITY — PHASE 2.0 MUST NOT MODIFY ENGINE
# =============================================================================

class TestPhase20EngineIntegrity:
    """Verify that Phase 2.0 does not modify the core engine."""

    def test_verdict_still_binary(self):
        """Verdict.status must still be Literal['pass', 'fail']."""
        import typing
        from phylax._internal.schema import Verdict
        args = typing.get_args(Verdict.model_fields["status"].annotation)
        assert set(args) == {"pass", "fail"}

    def test_rule_signature_unchanged(self):
        """Rule.evaluate still takes (response_text, latency_ms)."""
        import inspect
        from phylax._internal.expectations.rules import Rule
        sig = inspect.signature(Rule.evaluate)
        params = list(sig.parameters.keys())
        assert params == ["self", "response_text", "latency_ms"]

    def test_evaluator_signature_unchanged(self):
        """Evaluator.evaluate still takes (response_text, latency_ms)."""
        import inspect
        from phylax._internal.expectations.evaluator import Evaluator
        sig = inspect.signature(Evaluator.evaluate)
        params = list(sig.parameters.keys())
        assert params == ["self", "response_text", "latency_ms"]
