"""
Multi-Step Execution Trace Enforcement (Axis 2 Phase 2.3)

Enforce graph-level structural invariants across multi-step flows.

Surface: Ordered list of steps:
    [{ stage, type, metadata }, ...]

Stages must be explicitly labeled. No auto-inference.

Enforcement types:
1. Step Count Constraints — max/min/exact steps
2. Forbidden Transitions — explicit pair prohibition
3. Required Stage Presence — stages that must appear

What is forbidden:
- Loop detection/explanation
- Efficiency scoring
- Context-based legality
- Conditional transitions based on runtime values
"""

from typing import Any, Literal, Optional

from phylax._internal.surfaces.surface import (
    Surface,
    SurfaceAdapter,
    SurfaceRule,
    SurfaceRuleResult,
)


# ─── Rules ───────────────────────────────────────────────────────────────────

class StepCountRule(SurfaceRule):
    """
    Total step count must satisfy a constraint.

    No efficiency judgment. No "optimal step" evaluation.
    """

    name = "step_count"

    def __init__(self, operator: Literal["==", "<=", ">="], count: int):
        """
        Args:
            operator: Comparison operator
            count: Step count bound
        """
        if operator not in ("==", "<=", ">="):
            raise ValueError(f"Invalid operator: {operator}")
        self.operator = operator
        self.count = count

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        steps = surface.raw_payload
        if not isinstance(steps, list):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload is not a list of steps",
            )

        actual = len(steps)
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
                    f"step count {actual} violates constraint "
                    f"{self.operator} {self.count}"
                ),
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class ForbiddenTransitionRule(SurfaceRule):
    """
    Explicit stage transitions that must not occur.

    A transition is from_stage → to_stage in consecutive steps.
    No runtime value evaluation. No context-based exceptions.
    """

    name = "forbidden_transition"

    def __init__(self, from_stage: str, to_stage: str):
        """
        Args:
            from_stage: Source stage name
            to_stage: Target stage name that must NOT follow from_stage
        """
        self.from_stage = from_stage
        self.to_stage = to_stage

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        steps = surface.raw_payload
        if not isinstance(steps, list):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload is not a list of steps",
            )

        for i in range(len(steps) - 1):
            curr = steps[i]
            next_step = steps[i + 1]

            if not isinstance(curr, dict) or not isinstance(next_step, dict):
                continue

            curr_stage = curr.get("stage")
            next_stage = next_step.get("stage")

            if curr_stage == self.from_stage and next_stage == self.to_stage:
                return SurfaceRuleResult(
                    passed=False,
                    rule_name=self.name,
                    violation_message=(
                        f"forbidden transition '{self.from_stage}' → "
                        f"'{self.to_stage}' at step {i} → {i + 1}"
                    ),
                )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class RequiredStageRule(SurfaceRule):
    """
    A named stage must appear at least once in the execution trace.

    No implicit inference of stage from step type or metadata.
    Stage must be explicitly labeled in the step.
    """

    name = "required_stage"

    def __init__(self, stage: str):
        """
        Args:
            stage: Stage name that must appear in at least one step
        """
        self.stage = stage

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        steps = surface.raw_payload
        if not isinstance(steps, list):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload is not a list of steps",
            )

        found = any(
            isinstance(s, dict) and s.get("stage") == self.stage
            for s in steps
        )

        if not found:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=f"required stage '{self.stage}' not found",
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


# ─── Execution Trace Surface Adapter ────────────────────────────────────────

class ExecutionTraceSurfaceAdapter(SurfaceAdapter):
    """
    Adapter for multi-step execution traces.

    Converts a list of step events { stage, type, metadata } into
    a Surface with type="execution_trace".

    Raw step sequence is preserved. No filtering, reordering, or collapsing.

    Usage:
        adapter = ExecutionTraceSurfaceAdapter()
        surface = adapter.adapt([
            {"stage": "init", "type": "setup", "metadata": {}},
            {"stage": "process", "type": "transform", "metadata": {}},
            {"stage": "output", "type": "response", "metadata": {}},
        ])
    """

    surface_type = "execution_trace"

    def adapt(self, raw_data: Any, **kwargs) -> Surface:
        """
        Convert execution trace steps into a Surface.

        Args:
            raw_data: List of step events (preserved as-is)
            **kwargs: Optional metadata

        Returns:
            Surface with type="execution_trace"
        """
        metadata = kwargs.get("metadata", {})
        return Surface(
            type="execution_trace",
            raw_payload=raw_data,
            metadata=metadata,
        )
