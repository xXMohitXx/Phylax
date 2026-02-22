"""
Tool & Function Call Invariants (Axis 2 Phase 2.2)

Enforce invariants over tool usage as a structural log — not behavior quality.

Surface: Ordered list of immutable events:
    [{ name, args, timestamp, id }, ...]

Enforcement types:
1. Call Presence — tool must/must-not appear
2. Call Count — exact/min/max count
3. Argument Enforcement — path-based strict comparison
4. Ordering Constraints — index-based evaluation

What is forbidden:
- "Unnecessary tool" judgments
- "Inefficient call" judgments
- Quality evaluation of results
- Retry collapsing
- Dynamic rule branching
"""

from typing import Any, Literal, Optional

from phylax._internal.surfaces.surface import (
    Surface,
    SurfaceAdapter,
    SurfaceRule,
    SurfaceRuleResult,
)
from phylax._internal.surfaces.structured import _resolve_path


# ─── Rules ───────────────────────────────────────────────────────────────────

class ToolPresenceRule(SurfaceRule):
    """
    Tool must or must not appear in the tool call sequence.

    Count-based existence check only.
    No quality judgment of the tool call.
    """

    name = "tool_presence"

    def __init__(self, tool_name: str, must_exist: bool = True):
        """
        Args:
            tool_name: Exact tool name to check for
            must_exist: If True, tool must appear at least once.
                        If False, tool must NOT appear.
        """
        self.tool_name = tool_name
        self.must_exist = must_exist

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        events = surface.raw_payload
        if not isinstance(events, list):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload is not a list of events",
            )

        found = any(
            isinstance(e, dict) and e.get("name") == self.tool_name
            for e in events
        )

        if self.must_exist and not found:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"tool '{self.tool_name}' must appear but was not found",
            )

        if not self.must_exist and found:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"tool '{self.tool_name}' must not appear but was found",
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class ToolCountRule(SurfaceRule):
    """
    Tool must appear exactly N times, at least N times, or at most N times.

    Count-based only. No quality evaluation.
    """

    name = "tool_count"

    def __init__(
        self,
        tool_name: str,
        operator: Literal["==", "<=", ">="],
        count: int,
    ):
        """
        Args:
            tool_name: Exact tool name to count
            operator: Comparison operator
            count: Expected count bound
        """
        if operator not in ("==", "<=", ">="):
            raise ValueError(f"Invalid operator: {operator}. Must be ==, <=, or >=")
        self.tool_name = tool_name
        self.operator = operator
        self.count = count

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        events = surface.raw_payload
        if not isinstance(events, list):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload is not a list of events",
            )

        actual = sum(
            1 for e in events
            if isinstance(e, dict) and e.get("name") == self.tool_name
        )

        passed = False
        if self.operator == "==":
            passed = actual == self.count
        elif self.operator == "<=":
            passed = actual <= self.count
        elif self.operator == ">=":
            passed = actual >= self.count

        if not passed:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"tool '{self.tool_name}' count {actual} "
                    f"violates constraint {self.operator} {self.count}"
                ),
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class ToolArgumentRule(SurfaceRule):
    """
    Tool argument at path must equal expected value.

    Path-based. Strict comparison. No coercion.
    Applies to the FIRST matching tool call or a specific occurrence.
    """

    name = "tool_argument"

    def __init__(
        self,
        tool_name: str,
        arg_path: str,
        expected_value: Any,
        occurrence: int = 0,
    ):
        """
        Args:
            tool_name: Exact tool name to inspect
            arg_path: Dot-notation path within args (e.g. "limit", "options.safe_mode")
            expected_value: Expected value (strict ==)
            occurrence: Which occurrence of the tool to check (0-indexed, default first)
        """
        self.tool_name = tool_name
        self.arg_path = arg_path
        self.expected_value = expected_value
        self.occurrence = occurrence

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        events = surface.raw_payload
        if not isinstance(events, list):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload is not a list of events",
            )

        # Find the Nth occurrence of the tool
        matches = [
            e for e in events
            if isinstance(e, dict) and e.get("name") == self.tool_name
        ]

        if self.occurrence >= len(matches):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"tool '{self.tool_name}' occurrence {self.occurrence} not found "
                    f"(only {len(matches)} calls)"
                ),
            )

        tool_call = matches[self.occurrence]
        args = tool_call.get("args", {})

        exists, value = _resolve_path(args, self.arg_path)
        if not exists:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"tool '{self.tool_name}' args path '{self.arg_path}' does not exist"
                ),
            )

        if type(value) != type(self.expected_value) or value != self.expected_value:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"tool '{self.tool_name}' args.{self.arg_path}: "
                    f"expected {self.expected_value!r}, got {value!r}"
                ),
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class ToolOrderingRule(SurfaceRule):
    """
    Ordering constraint between two tools.

    Index-based evaluation only. No contextual evaluation.

    Modes:
        "before" — tool A must occur before tool B
        "not_after" — tool C must NOT occur after tool D
    """

    name = "tool_ordering"

    def __init__(
        self,
        tool_a: str,
        tool_b: str,
        mode: Literal["before", "not_after"],
    ):
        """
        Args:
            tool_a: First tool name
            tool_b: Second tool name
            mode: "before" (A must occur before B) or
                  "not_after" (A must NOT occur after B)
        """
        if mode not in ("before", "not_after"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'before' or 'not_after'")
        self.tool_a = tool_a
        self.tool_b = tool_b
        self.mode = mode

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        events = surface.raw_payload
        if not isinstance(events, list):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload is not a list of events",
            )

        # Find first index of each tool
        idx_a = None
        idx_b = None
        for i, e in enumerate(events):
            if isinstance(e, dict):
                if e.get("name") == self.tool_a and idx_a is None:
                    idx_a = i
                if e.get("name") == self.tool_b and idx_b is None:
                    idx_b = i

        if self.mode == "before":
            # A must occur before B; both must exist
            if idx_a is None:
                return SurfaceRuleResult(
                    passed=False,
                    rule_name=self.name,
                    violation_message=(
                        f"tool '{self.tool_a}' not found "
                        f"(required before '{self.tool_b}')"
                    ),
                )
            if idx_b is None:
                return SurfaceRuleResult(
                    passed=False,
                    rule_name=self.name,
                    violation_message=(
                        f"tool '{self.tool_b}' not found "
                        f"(required after '{self.tool_a}')"
                    ),
                )
            if idx_a >= idx_b:
                return SurfaceRuleResult(
                    passed=False,
                    rule_name=self.name,
                    violation_message=(
                        f"tool '{self.tool_a}' (index {idx_a}) must occur "
                        f"before '{self.tool_b}' (index {idx_b})"
                    ),
                )

        elif self.mode == "not_after":
            # A must NOT occur after B
            # If either is missing, constraint is satisfied
            if idx_a is not None and idx_b is not None:
                if idx_a > idx_b:
                    return SurfaceRuleResult(
                        passed=False,
                        rule_name=self.name,
                        violation_message=(
                            f"tool '{self.tool_a}' (index {idx_a}) must not occur "
                            f"after '{self.tool_b}' (index {idx_b})"
                        ),
                    )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


# ─── Tool Surface Adapter ───────────────────────────────────────────────────

class ToolSurfaceAdapter(SurfaceAdapter):
    """
    Adapter for tool/function call event sequences.

    Converts a list of tool call events into a Surface with type="tool_calls".

    Each event should be: { name, args, timestamp, id }
    No deduplication. No retry collapsing. No filtering.
    Raw sequence is preserved.

    Usage:
        adapter = ToolSurfaceAdapter()
        surface = adapter.adapt([
            {"name": "search", "args": {"q": "test"}, "timestamp": "...", "id": "1"},
            {"name": "read", "args": {"url": "..."}, "timestamp": "...", "id": "2"},
        ])
    """

    surface_type = "tool_calls"

    def adapt(self, raw_data: Any, **kwargs) -> Surface:
        """
        Convert tool call event list into a Surface.

        Args:
            raw_data: List of tool call events (preserved as-is)
            **kwargs: Optional metadata

        Returns:
            Surface with type="tool_calls"
        """
        metadata = kwargs.get("metadata", {})
        return Surface(
            type="tool_calls",
            raw_payload=raw_data,
            metadata=metadata,
        )
