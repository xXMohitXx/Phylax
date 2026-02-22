"""
Structured Output Enforcement Tests (Axis 2 Phase 2.1)

Tests all 6 structural rule types:
1. FieldExistsRule / FieldNotExistsRule
2. TypeEnforcementRule (strict, no coercion)
3. ExactValueRule (strict equality)
4. EnumEnforcementRule (set membership)
5. ArrayBoundsRule (length constraints)

Also tests:
- StructuredSurfaceAdapter
- Determinism (same input → same result)
- Forbidden behaviors (no coercion, no soft matching)
"""

import pytest

from phylax._internal.surfaces.surface import Surface, SurfaceEvaluator
from phylax._internal.surfaces.structured import (
    FieldExistsRule,
    FieldNotExistsRule,
    TypeEnforcementRule,
    ExactValueRule,
    EnumEnforcementRule,
    ArrayBoundsRule,
    StructuredSurfaceAdapter,
)


def _make_surface(payload):
    return Surface(type="structured_output", raw_payload=payload)


# =============================================================================
# FIELD EXISTS / NOT EXISTS
# =============================================================================

class TestFieldExistsRule:

    def test_field_exists_pass(self):
        s = _make_surface({"name": "Alice"})
        r = FieldExistsRule("name").evaluate(s)
        assert r.passed is True

    def test_field_exists_nested(self):
        s = _make_surface({"data": {"user": {"name": "Alice"}}})
        r = FieldExistsRule("data.user.name").evaluate(s)
        assert r.passed is True

    def test_field_exists_fail(self):
        s = _make_surface({"name": "Alice"})
        r = FieldExistsRule("age").evaluate(s)
        assert r.passed is False

    def test_field_exists_nested_fail(self):
        s = _make_surface({"data": {}})
        r = FieldExistsRule("data.user.name").evaluate(s)
        assert r.passed is False

    def test_field_exists_array_index(self):
        s = _make_surface({"items": ["a", "b", "c"]})
        r = FieldExistsRule("items.1").evaluate(s)
        assert r.passed is True

    def test_field_exists_array_out_of_bounds(self):
        s = _make_surface({"items": ["a"]})
        r = FieldExistsRule("items.5").evaluate(s)
        assert r.passed is False


class TestFieldNotExistsRule:

    def test_field_not_exists_pass(self):
        s = _make_surface({"name": "Alice"})
        r = FieldNotExistsRule("age").evaluate(s)
        assert r.passed is True

    def test_field_not_exists_fail(self):
        s = _make_surface({"name": "Alice"})
        r = FieldNotExistsRule("name").evaluate(s)
        assert r.passed is False


# =============================================================================
# TYPE ENFORCEMENT
# =============================================================================

class TestTypeEnforcementRule:

    def test_string_type_pass(self):
        s = _make_surface({"name": "Alice"})
        r = TypeEnforcementRule("name", "string").evaluate(s)
        assert r.passed is True

    def test_number_type_int_pass(self):
        s = _make_surface({"count": 42})
        r = TypeEnforcementRule("count", "number").evaluate(s)
        assert r.passed is True

    def test_number_type_float_pass(self):
        s = _make_surface({"score": 3.14})
        r = TypeEnforcementRule("score", "number").evaluate(s)
        assert r.passed is True

    def test_boolean_type_pass(self):
        s = _make_surface({"active": True})
        r = TypeEnforcementRule("active", "boolean").evaluate(s)
        assert r.passed is True

    def test_array_type_pass(self):
        s = _make_surface({"items": [1, 2, 3]})
        r = TypeEnforcementRule("items", "array").evaluate(s)
        assert r.passed is True

    def test_object_type_pass(self):
        s = _make_surface({"data": {"key": "val"}})
        r = TypeEnforcementRule("data", "object").evaluate(s)
        assert r.passed is True

    def test_null_type_pass(self):
        s = _make_surface({"value": None})
        r = TypeEnforcementRule("value", "null").evaluate(s)
        assert r.passed is True

    def test_string_vs_number_no_coercion(self):
        """'1' (string) is NOT a number — strict, no coercion."""
        s = _make_surface({"count": "1"})
        r = TypeEnforcementRule("count", "number").evaluate(s)
        assert r.passed is False

    def test_number_vs_string_no_coercion(self):
        """1 (number) is NOT a string — strict, no coercion."""
        s = _make_surface({"name": 1})
        r = TypeEnforcementRule("name", "string").evaluate(s)
        assert r.passed is False

    def test_boolean_is_not_number(self):
        """True (boolean) is NOT a number — even though bool < int in Python."""
        s = _make_surface({"count": True})
        r = TypeEnforcementRule("count", "number").evaluate(s)
        assert r.passed is False

    def test_number_is_not_boolean(self):
        """1 (number) is NOT a boolean."""
        s = _make_surface({"flag": 1})
        r = TypeEnforcementRule("flag", "boolean").evaluate(s)
        assert r.passed is False

    def test_missing_path_fails(self):
        s = _make_surface({})
        r = TypeEnforcementRule("missing", "string").evaluate(s)
        assert r.passed is False

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            TypeEnforcementRule("path", "invalid_type")


# =============================================================================
# EXACT VALUE
# =============================================================================

class TestExactValueRule:

    def test_exact_string_pass(self):
        s = _make_surface({"status": "approved"})
        r = ExactValueRule("status", "approved").evaluate(s)
        assert r.passed is True

    def test_exact_number_pass(self):
        s = _make_surface({"count": 3})
        r = ExactValueRule("count", 3).evaluate(s)
        assert r.passed is True

    def test_exact_boolean_pass(self):
        s = _make_surface({"active": True})
        r = ExactValueRule("active", True).evaluate(s)
        assert r.passed is True

    def test_exact_value_fail(self):
        s = _make_surface({"status": "rejected"})
        r = ExactValueRule("status", "approved").evaluate(s)
        assert r.passed is False

    def test_no_case_folding(self):
        """'Approved' != 'approved' — strict, no case folding."""
        s = _make_surface({"status": "Approved"})
        r = ExactValueRule("status", "approved").evaluate(s)
        assert r.passed is False

    def test_no_type_coercion(self):
        """'3' (string) != 3 (number) — strict type matching."""
        s = _make_surface({"count": "3"})
        r = ExactValueRule("count", 3).evaluate(s)
        assert r.passed is False

    def test_no_trimming(self):
        """' hello ' != 'hello' — no trimming."""
        s = _make_surface({"text": " hello "})
        r = ExactValueRule("text", "hello").evaluate(s)
        assert r.passed is False

    def test_missing_path_fails(self):
        s = _make_surface({})
        r = ExactValueRule("missing", "value").evaluate(s)
        assert r.passed is False


# =============================================================================
# ENUM ENFORCEMENT
# =============================================================================

class TestEnumEnforcementRule:

    def test_enum_pass(self):
        s = _make_surface({"color": "red"})
        r = EnumEnforcementRule("color", ["red", "green", "blue"]).evaluate(s)
        assert r.passed is True

    def test_enum_fail(self):
        s = _make_surface({"color": "yellow"})
        r = EnumEnforcementRule("color", ["red", "green", "blue"]).evaluate(s)
        assert r.passed is False

    def test_enum_strict_type(self):
        """1 (int) is not in ["1"] (string list)."""
        s = _make_surface({"val": 1})
        r = EnumEnforcementRule("val", ["1", "2", "3"]).evaluate(s)
        assert r.passed is False

    def test_enum_missing_path(self):
        s = _make_surface({})
        r = EnumEnforcementRule("missing", ["a"]).evaluate(s)
        assert r.passed is False


# =============================================================================
# ARRAY BOUNDS
# =============================================================================

class TestArrayBoundsRule:

    def test_exact_length_pass(self):
        s = _make_surface({"items": [1, 2, 3]})
        r = ArrayBoundsRule("items", "==", 3).evaluate(s)
        assert r.passed is True

    def test_exact_length_fail(self):
        s = _make_surface({"items": [1, 2]})
        r = ArrayBoundsRule("items", "==", 3).evaluate(s)
        assert r.passed is False

    def test_max_length_pass(self):
        s = _make_surface({"items": [1, 2]})
        r = ArrayBoundsRule("items", "<=", 5).evaluate(s)
        assert r.passed is True

    def test_max_length_fail(self):
        s = _make_surface({"items": [1, 2, 3, 4, 5, 6]})
        r = ArrayBoundsRule("items", "<=", 5).evaluate(s)
        assert r.passed is False

    def test_min_length_pass(self):
        s = _make_surface({"items": [1, 2, 3]})
        r = ArrayBoundsRule("items", ">=", 2).evaluate(s)
        assert r.passed is True

    def test_min_length_fail(self):
        s = _make_surface({"items": [1]})
        r = ArrayBoundsRule("items", ">=", 2).evaluate(s)
        assert r.passed is False

    def test_not_array_fails(self):
        s = _make_surface({"items": "not an array"})
        r = ArrayBoundsRule("items", "==", 1).evaluate(s)
        assert r.passed is False

    def test_invalid_operator_raises(self):
        with pytest.raises(ValueError):
            ArrayBoundsRule("items", ">", 5)


# =============================================================================
# STRUCTURED SURFACE ADAPTER
# =============================================================================

class TestStructuredSurfaceAdapter:

    def test_adapt_dict(self):
        adapter = StructuredSurfaceAdapter()
        s = adapter.adapt({"key": "value"})
        assert s.type == "structured_output"
        assert s.raw_payload == {"key": "value"}

    def test_adapt_preserves_payload(self):
        payload = {"nested": {"deep": [1, 2, {"x": True}]}}
        adapter = StructuredSurfaceAdapter()
        s = adapter.adapt(payload)
        assert s.raw_payload == payload

    def test_adapt_with_metadata(self):
        adapter = StructuredSurfaceAdapter()
        s = adapter.adapt({}, metadata={"model": "gpt-4"})
        assert s.metadata["model"] == "gpt-4"


# =============================================================================
# DETERMINISM
# =============================================================================

class TestDeterminism:
    """Same input twice → identical result."""

    def test_deterministic_field_exists(self):
        s1 = _make_surface({"name": "Alice"})
        s2 = _make_surface({"name": "Alice"})
        rule = FieldExistsRule("name")
        r1 = rule.evaluate(s1)
        r2 = rule.evaluate(s2)
        assert r1.passed == r2.passed

    def test_deterministic_type(self):
        s1 = _make_surface({"count": 42})
        s2 = _make_surface({"count": 42})
        rule = TypeEnforcementRule("count", "number")
        r1 = rule.evaluate(s1)
        r2 = rule.evaluate(s2)
        assert r1.passed == r2.passed

    def test_evaluator_deterministic(self):
        ev = SurfaceEvaluator()
        ev.add_rule(FieldExistsRule("name"))
        ev.add_rule(ExactValueRule("status", "ok"))
        payload = {"name": "Alice", "status": "ok"}
        v1 = ev.evaluate(_make_surface(payload))
        v2 = ev.evaluate(_make_surface(payload))
        assert v1.status == v2.status
        assert v1.violations == v2.violations


# =============================================================================
# FORBIDDEN BEHAVIORS
# =============================================================================

class TestForbiddenBehaviors:
    """Ensure no forbidden behaviors exist."""

    def test_no_schema_auto_generation(self):
        """No auto-schema generation from data."""
        import inspect
        from phylax._internal.surfaces import structured
        source = inspect.getsource(structured)
        for forbidden in ["auto_schema", "infer_schema", "generate_schema"]:
            assert forbidden not in source.lower()

    def test_no_soft_matching(self):
        """No approximate or soft matching functions."""
        import inspect
        from phylax._internal.surfaces import structured
        source = inspect.getsource(structured)
        for forbidden in ["similarity", "levenshtein", "approximate"]:
            assert forbidden not in source.lower()

    def test_no_default_injection(self):
        """No default value injection."""
        import inspect
        from phylax._internal.surfaces import structured
        source = inspect.getsource(structured)
        assert "default_value" not in source.lower()
        assert "inject_default" not in source.lower()
