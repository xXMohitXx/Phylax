"""
Structured Output Enforcement (Axis 2 Phase 2.1)

Deterministic structural validation for JSON/dict outputs.

Enforcement types:
1. Field Existence — path must exist / must not exist
2. Type Enforcement — strict type check, no coercion
3. Exact Value Matching — strict equality only
4. Enum Enforcement — set membership
5. Array Bounds — length constraints

What is forbidden:
- Schema auto-generation
- Soft matching
- Implicit casting
- Default value injection
- Optional inference
- Case-insensitive comparison
"""

from typing import Any, Literal, Optional

from phylax._internal.surfaces.surface import (
    Surface,
    SurfaceAdapter,
    SurfaceRule,
    SurfaceRuleResult,
)


# ─── Utility: Path Resolution ───────────────────────────────────────────────

def _resolve_path(data: Any, path: str) -> tuple[bool, Any]:
    """
    Resolve a dot-notation path against a dict/list structure.

    Returns (exists: bool, value: Any).
    No wildcards, no inference — explicit path only.
    """
    parts = path.split(".")
    current = data

    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                return False, None
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
                if idx < 0 or idx >= len(current):
                    return False, None
                current = current[idx]
            except (ValueError, IndexError):
                return False, None
        else:
            return False, None

    return True, current


# ─── Rules ───────────────────────────────────────────────────────────────────

class FieldExistsRule(SurfaceRule):
    """
    Path must exist in the structured output.

    Uses dot-notation: "data.user.name"
    No wildcards unless explicitly declared.
    """

    name = "field_exists"

    def __init__(self, path: str):
        """
        Args:
            path: Dot-notation path that must exist (e.g. "data.name")
        """
        self.path = path

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        exists, _ = _resolve_path(surface.raw_payload, self.path)
        if not exists:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"path '{self.path}' does not exist",
            )
        return SurfaceRuleResult(passed=True, rule_name=self.name)


class FieldNotExistsRule(SurfaceRule):
    """
    Path must NOT exist in the structured output.
    """

    name = "field_not_exists"

    def __init__(self, path: str):
        """
        Args:
            path: Dot-notation path that must NOT exist
        """
        self.path = path

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        exists, _ = _resolve_path(surface.raw_payload, self.path)
        if exists:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"path '{self.path}' exists but must not",
            )
        return SurfaceRuleResult(passed=True, rule_name=self.name)


class TypeEnforcementRule(SurfaceRule):
    """
    Value at path must be of the specified type.

    Strict type checking — NO coercion.
    "1" (string) != 1 (number) → FAIL.

    Valid types: "string", "number", "boolean", "array", "object", "null"
    """

    name = "type_enforcement"

    _TYPE_MAP = {
        "string": str,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }

    def __init__(self, path: str, expected_type: str):
        """
        Args:
            path: Dot-notation path to check
            expected_type: Expected type name (string/number/boolean/array/object/null)
        """
        if expected_type not in self._TYPE_MAP:
            raise ValueError(
                f"Invalid type: {expected_type}. "
                f"Must be one of: {list(self._TYPE_MAP.keys())}"
            )
        self.path = path
        self.expected_type = expected_type

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        exists, value = _resolve_path(surface.raw_payload, self.path)
        if not exists:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"path '{self.path}' does not exist",
            )

        expected_py_type = self._TYPE_MAP[self.expected_type]

        # Special case: bool is a subclass of int in Python.
        # If we expect "number", booleans should FAIL (strict).
        # If we expect "boolean", numbers should FAIL (strict).
        if self.expected_type == "number" and isinstance(value, bool):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"path '{self.path}': expected type 'number', "
                    f"got 'boolean' ({value!r})"
                ),
            )
        if self.expected_type == "boolean" and not isinstance(value, bool):
            if isinstance(value, (int, float)):
                return SurfaceRuleResult(
                    passed=False,
                    rule_name=self.name,
                    violation_message=(
                        f"path '{self.path}': expected type 'boolean', "
                        f"got 'number' ({value!r})"
                    ),
                )

        if not isinstance(value, expected_py_type):
            actual_type = type(value).__name__
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"path '{self.path}': expected type '{self.expected_type}', "
                    f"got '{actual_type}' ({value!r})"
                ),
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class ExactValueRule(SurfaceRule):
    """
    Value at path must be exactly equal to expected value.

    Strict equality only (==).
    No case folding. No trimming. No tolerance.
    """

    name = "exact_value"

    def __init__(self, path: str, expected_value: Any):
        """
        Args:
            path: Dot-notation path to check
            expected_value: Exact value expected (strict ==)
        """
        self.path = path
        self.expected_value = expected_value

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        exists, value = _resolve_path(surface.raw_payload, self.path)
        if not exists:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"path '{self.path}' does not exist",
            )

        # Strict type + value equality
        if type(value) != type(self.expected_value) or value != self.expected_value:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"path '{self.path}': expected {self.expected_value!r}, "
                    f"got {value!r}"
                ),
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class EnumEnforcementRule(SurfaceRule):
    """
    Value at path must be a member of an explicit set.

    Set membership only — no fuzzy matching.
    """

    name = "enum_enforcement"

    def __init__(self, path: str, allowed_values: list[Any]):
        """
        Args:
            path: Dot-notation path to check
            allowed_values: Explicit list of allowed values
        """
        self.path = path
        self.allowed_values = allowed_values

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        exists, value = _resolve_path(surface.raw_payload, self.path)
        if not exists:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"path '{self.path}' does not exist",
            )

        if value not in self.allowed_values:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"path '{self.path}': value {value!r} not in "
                    f"allowed set {self.allowed_values!r}"
                ),
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class ArrayBoundsRule(SurfaceRule):
    """
    Array at path must satisfy length constraint.

    Operators: "==", "<=", ">="
    No content inference. No semantic uniqueness checks.
    """

    name = "array_bounds"

    def __init__(self, path: str, operator: Literal["==", "<=", ">="], bound: int):
        """
        Args:
            path: Dot-notation path to the array
            operator: Comparison operator ("==", "<=", ">=")
            bound: Length bound to enforce
        """
        if operator not in ("==", "<=", ">="):
            raise ValueError(f"Invalid operator: {operator}. Must be ==, <=, or >=")
        self.path = path
        self.operator = operator
        self.bound = bound

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        exists, value = _resolve_path(surface.raw_payload, self.path)
        if not exists:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"path '{self.path}' does not exist",
            )

        if not isinstance(value, list):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"path '{self.path}': expected array, got {type(value).__name__}"
                ),
            )

        length = len(value)
        passed = False
        if self.operator == "==":
            passed = length == self.bound
        elif self.operator == "<=":
            passed = length <= self.bound
        elif self.operator == ">=":
            passed = length >= self.bound

        if not passed:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"path '{self.path}': array length {length} "
                    f"violates constraint {self.operator} {self.bound}"
                ),
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


# ─── Structured Surface Adapter ─────────────────────────────────────────────

class StructuredSurfaceAdapter(SurfaceAdapter):
    """
    Adapter for structured (JSON/dict) outputs.

    Converts a dict/JSON payload into a Surface with type="structured_output".
    Raw payload is preserved without modification.

    Usage:
        adapter = StructuredSurfaceAdapter()
        surface = adapter.adapt({"status": "ok", "count": 3})
    """

    surface_type = "structured_output"

    def adapt(self, raw_data: Any, **kwargs) -> Surface:
        """
        Convert structured data into a Surface.

        Args:
            raw_data: Dict/JSON payload to wrap
            **kwargs: Optional metadata

        Returns:
            Surface with type="structured_output"
        """
        metadata = kwargs.get("metadata", {})
        return Surface(
            type="structured_output",
            raw_payload=raw_data,
            metadata=metadata,
        )
