"""
Tests for Agent Workflow Enforcement Rules.

Tests cover:
    - ToolSequenceRule: relaxed and strict ordering
    - ToolPresenceValidator: must_call / must_not_call
    - AgentStepValidator: step count, required types, first failing node
"""
import pytest
from phylax.agents import (
    ToolSequenceRule,
    ToolPresenceValidator,
    AgentStepValidator,
)


class TestToolSequenceRule:
    """Tests for ToolSequenceRule — tool call ordering enforcement."""

    def test_relaxed_passes_correct_order(self):
        rule = ToolSequenceRule(required_sequence=["classify", "execute", "respond"])
        tool_calls = [
            {"tool_name": "classify"},
            {"tool_name": "log"},
            {"tool_name": "execute"},
            {"tool_name": "respond"},
        ]
        result = rule.evaluate(tool_calls)
        assert result.passed is True

    def test_relaxed_fails_wrong_order(self):
        rule = ToolSequenceRule(required_sequence=["classify", "execute", "respond"])
        tool_calls = [
            {"tool_name": "respond"},
            {"tool_name": "classify"},
            {"tool_name": "execute"},
        ]
        result = rule.evaluate(tool_calls)
        assert result.passed is False

    def test_relaxed_fails_missing_tool(self):
        rule = ToolSequenceRule(required_sequence=["classify", "execute", "respond"])
        tool_calls = [
            {"tool_name": "classify"},
            {"tool_name": "execute"},
        ]
        result = rule.evaluate(tool_calls)
        assert result.passed is False
        assert "respond" in result.violations[0]

    def test_strict_passes_consecutive(self):
        rule = ToolSequenceRule(required_sequence=["classify", "execute"], strict=True)
        tool_calls = [
            {"tool_name": "init"},
            {"tool_name": "classify"},
            {"tool_name": "execute"},
            {"tool_name": "cleanup"},
        ]
        result = rule.evaluate(tool_calls)
        assert result.passed is True

    def test_strict_fails_non_consecutive(self):
        rule = ToolSequenceRule(required_sequence=["classify", "execute"], strict=True)
        tool_calls = [
            {"tool_name": "classify"},
            {"tool_name": "log"},
            {"tool_name": "execute"},
        ]
        result = rule.evaluate(tool_calls)
        assert result.passed is False

    def test_empty_tool_calls_fails(self):
        rule = ToolSequenceRule(required_sequence=["classify"])
        result = rule.evaluate([])
        assert result.passed is False


class TestToolPresenceValidator:
    """Tests for ToolPresenceValidator — must/must-not call enforcement."""

    def test_passes_when_required_tools_present(self):
        rule = ToolPresenceValidator(must_call=["search", "respond"])
        tool_calls = [
            {"tool_name": "search"},
            {"tool_name": "respond"},
        ]
        result = rule.evaluate(tool_calls)
        assert result.passed is True

    def test_fails_when_required_tool_missing(self):
        rule = ToolPresenceValidator(must_call=["search", "respond"])
        tool_calls = [{"tool_name": "search"}]
        result = rule.evaluate(tool_calls)
        assert result.passed is False
        assert "respond" in result.violations[0]

    def test_fails_when_forbidden_tool_called(self):
        rule = ToolPresenceValidator(must_not_call=["delete_user"])
        tool_calls = [
            {"tool_name": "search"},
            {"tool_name": "delete_user"},
        ]
        result = rule.evaluate(tool_calls)
        assert result.passed is False
        assert "delete_user" in result.violations[0]

    def test_passes_when_forbidden_tool_not_called(self):
        rule = ToolPresenceValidator(must_not_call=["delete_user"])
        tool_calls = [{"tool_name": "search"}, {"tool_name": "respond"}]
        result = rule.evaluate(tool_calls)
        assert result.passed is True


class TestAgentStepValidator:
    """Tests for AgentStepValidator — step structure enforcement."""

    def test_passes_within_bounds(self):
        rule = AgentStepValidator(min_steps=2, max_steps=5)
        steps = [
            {"type": "planner", "status": "pass", "name": "plan"},
            {"type": "executor", "status": "pass", "name": "exec"},
            {"type": "responder", "status": "pass", "name": "respond"},
        ]
        result = rule.evaluate(steps)
        assert result.passed is True

    def test_fails_below_minimum(self):
        rule = AgentStepValidator(min_steps=3)
        steps = [{"type": "planner", "status": "pass", "name": "plan"}]
        result = rule.evaluate(steps)
        assert result.passed is False

    def test_fails_above_maximum(self):
        rule = AgentStepValidator(max_steps=2)
        steps = [
            {"type": "a", "status": "pass", "name": "a"},
            {"type": "b", "status": "pass", "name": "b"},
            {"type": "c", "status": "pass", "name": "c"},
        ]
        result = rule.evaluate(steps)
        assert result.passed is False

    def test_fails_missing_required_type(self):
        rule = AgentStepValidator(required_step_types=["planner", "executor"])
        steps = [{"type": "planner", "status": "pass", "name": "plan"}]
        result = rule.evaluate(steps)
        assert result.passed is False
        assert "executor" in result.violations[0]

    def test_detects_first_failing_node(self):
        rule = AgentStepValidator()
        steps = [
            {"type": "planner", "status": "pass", "name": "plan_step"},
            {"type": "executor", "status": "fail", "name": "exec_step"},
            {"type": "responder", "status": "pass", "name": "respond_step"},
        ]
        result = rule.evaluate(steps)
        assert result.passed is False
        assert "exec_step" in result.violations[0]
