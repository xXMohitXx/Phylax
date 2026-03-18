"""
Agent Workflow Enforcement Rules — Deterministic validation for multi-agent systems.

Rules:
    ToolSequenceRule — Tools must be called in a specified order.
    AgentStepValidator — Validates agent execution step structure.
"""
from typing import Optional
from pydantic import BaseModel, Field


class AgentRuleResult(BaseModel):
    """Result of evaluating an agent enforcement rule."""
    passed: bool
    rule_name: str
    violations: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}


class ToolSequenceRule:
    """Enforces that tools are called in a required sequence.

    Given a list of tool call events, validates that specific tools appear
    in the correct relative order. This is index-based, deterministic matching.

    Args:
        required_sequence: Ordered list of tool names that must appear in this order.
        strict: If True, the tools must appear consecutively. If False, other tools
                may appear between them.
    """
    name = "tool_sequence"
    severity = "high"

    def __init__(self, required_sequence: list[str], strict: bool = False):
        self.required_sequence = required_sequence
        self.strict = strict

    def evaluate(self, tool_calls: list[dict]) -> AgentRuleResult:
        """Check that tool calls follow the required sequence.

        Args:
            tool_calls: List of dicts with at least a 'tool_name' key.
        """
        tool_names = [tc.get("tool_name", tc.get("name", "")) for tc in tool_calls]

        if self.strict:
            return self._check_strict(tool_names)
        return self._check_relaxed(tool_names)

    def _check_relaxed(self, tool_names: list[str]) -> AgentRuleResult:
        """Check that required tools appear in order (other tools may interleave)."""
        seq_idx = 0
        for tool_name in tool_names:
            if seq_idx < len(self.required_sequence) and tool_name == self.required_sequence[seq_idx]:
                seq_idx += 1
        
        if seq_idx == len(self.required_sequence):
            return AgentRuleResult(passed=True, rule_name=self.name)
        
        missing = self.required_sequence[seq_idx:]
        return AgentRuleResult(
            passed=False,
            rule_name=self.name,
            violations=[
                f"tool_sequence: expected sequence {self.required_sequence}, "
                f"but tools after index {seq_idx} were not found in order. "
                f"Missing/out-of-order: {missing}. "
                f"Actual tool order: {tool_names}"
            ],
        )

    def _check_strict(self, tool_names: list[str]) -> AgentRuleResult:
        """Check that required tools appear consecutively in order."""
        seq_len = len(self.required_sequence)
        for i in range(len(tool_names) - seq_len + 1):
            if tool_names[i:i + seq_len] == self.required_sequence:
                return AgentRuleResult(passed=True, rule_name=self.name)
        
        return AgentRuleResult(
            passed=False,
            rule_name=self.name,
            violations=[
                f"tool_sequence (strict): expected consecutive sequence "
                f"{self.required_sequence} not found in {tool_names}"
            ],
        )


class ToolPresenceValidator:
    """Validates that required tools were called and forbidden tools were not.

    Args:
        must_call: Tools that must appear in the call list.
        must_not_call: Tools that must NOT appear in the call list.
    """
    name = "tool_presence"
    severity = "high"

    def __init__(
        self,
        must_call: Optional[list[str]] = None,
        must_not_call: Optional[list[str]] = None,
    ):
        self.must_call = must_call or []
        self.must_not_call = must_not_call or []

    def evaluate(self, tool_calls: list[dict]) -> AgentRuleResult:
        """Check tool presence/absence."""
        tool_names = set(tc.get("tool_name", tc.get("name", "")) for tc in tool_calls)
        violations = []

        for required in self.must_call:
            if required not in tool_names:
                violations.append(f"tool_presence: required tool '{required}' was not called")

        for forbidden in self.must_not_call:
            if forbidden in tool_names:
                violations.append(f"tool_presence: forbidden tool '{forbidden}' was called")

        return AgentRuleResult(
            passed=len(violations) == 0,
            rule_name=self.name,
            violations=violations,
        )


class AgentStepValidator:
    """Validates the structure of an agent execution.

    Checks:
        - Minimum/maximum step count
        - Required step types
        - First failing node detection

    Args:
        min_steps: Minimum number of steps expected.
        max_steps: Maximum number of steps expected.
        required_step_types: Step types that must appear (e.g., ["planner", "executor"]).
    """
    name = "agent_step_validator"
    severity = "medium"

    def __init__(
        self,
        min_steps: Optional[int] = None,
        max_steps: Optional[int] = None,
        required_step_types: Optional[list[str]] = None,
    ):
        self.min_steps = min_steps
        self.max_steps = max_steps
        self.required_step_types = required_step_types or []

    def evaluate(self, steps: list[dict]) -> AgentRuleResult:
        """Validate agent execution steps.

        Args:
            steps: List of step dicts with at least 'type' and 'status' keys.
        """
        violations = []
        step_count = len(steps)

        if self.min_steps is not None and step_count < self.min_steps:
            violations.append(
                f"agent_steps: {step_count} steps (minimum: {self.min_steps})"
            )

        if self.max_steps is not None and step_count > self.max_steps:
            violations.append(
                f"agent_steps: {step_count} steps (maximum: {self.max_steps})"
            )

        step_types = set(s.get("type", "") for s in steps)
        for required_type in self.required_step_types:
            if required_type not in step_types:
                violations.append(
                    f"agent_steps: required step type '{required_type}' not found"
                )

        # First failing node detection
        first_failure = None
        for i, step in enumerate(steps):
            if step.get("status") == "fail":
                first_failure = step.get("name", f"step_{i}")
                break

        if first_failure:
            violations.append(
                f"agent_steps: first failure at node '{first_failure}'"
            )

        return AgentRuleResult(
            passed=len(violations) == 0,
            rule_name=self.name,
            violations=violations,
        )
