"""
Test Expectation Groups (Axis 1 Phase 1)

Verifies logical algebra for expectations:
- AndGroup: All must pass
- OrGroup: At least one must pass  
- NotGroup: Rule must fail
"""

import pytest
from phylax._internal.expectations import (
    Evaluator,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    AndGroup,
    OrGroup,
    NotGroup,
)


class TestAndGroup:
    """AND group: all rules must pass."""
    
    def test_and_group_all_pass(self):
        """All rules pass → group passes."""
        rules = [
            MustIncludeRule(["hello"]),
            MustIncludeRule(["world"]),
        ]
        group = AndGroup(rules, name="greeting_check")
        result = group.evaluate("hello world", latency_ms=100)
        
        assert result.passed is True
        assert result.rule_name == "greeting_check"
    
    def test_and_group_one_fails(self):
        """One rule fails → group fails."""
        rules = [
            MustIncludeRule(["hello"]),
            MustIncludeRule(["goodbye"]),  # This will fail
        ]
        group = AndGroup(rules)
        result = group.evaluate("hello world", latency_ms=100)
        
        assert result.passed is False
        assert "AND group failed" in result.violation_message
    
    def test_and_group_empty(self):
        """Empty group passes."""
        group = AndGroup([])
        result = group.evaluate("any text", latency_ms=100)
        
        assert result.passed is True
    
    def test_and_group_severity_propagation(self):
        """Severity is max of all failures."""
        rules = [
            MustIncludeRule(["missing"]),  # low severity
            MustNotIncludeRule(["world"]),  # high severity, will fail
        ]
        group = AndGroup(rules)
        result = group.evaluate("hello world", latency_ms=100)
        
        assert result.passed is False
        assert result.severity == "high"


class TestOrGroup:
    """OR group: at least one rule must pass."""
    
    def test_or_group_one_passes(self):
        """One rule passes → group passes."""
        rules = [
            MustIncludeRule(["hello"]),  # passes
            MustIncludeRule(["goodbye"]),  # fails
        ]
        group = OrGroup(rules, name="any_greeting")
        result = group.evaluate("hello world", latency_ms=100)
        
        assert result.passed is True
    
    def test_or_group_all_fail(self):
        """All rules fail → group fails."""
        rules = [
            MustIncludeRule(["goodbye"]),
            MustIncludeRule(["farewell"]),
        ]
        group = OrGroup(rules)
        result = group.evaluate("hello world", latency_ms=100)
        
        assert result.passed is False
        assert "OR group failed" in result.violation_message
    
    def test_or_group_empty(self):
        """Empty group passes."""
        group = OrGroup([])
        result = group.evaluate("any text", latency_ms=100)
        
        assert result.passed is True
    
    def test_or_group_all_pass(self):
        """All rules pass → group passes."""
        rules = [
            MustIncludeRule(["hello"]),
            MustIncludeRule(["world"]),
        ]
        group = OrGroup(rules)
        result = group.evaluate("hello world", latency_ms=100)
        
        assert result.passed is True


class TestNotGroup:
    """NOT group: rule must fail for group to pass."""
    
    def test_not_group_rule_fails(self):
        """Wrapped rule fails → NOT passes."""
        rule = MustIncludeRule(["goodbye"])  # Will fail
        group = NotGroup(rule, name="not_goodbye")
        result = group.evaluate("hello world", latency_ms=100)
        
        assert result.passed is True
    
    def test_not_group_rule_passes(self):
        """Wrapped rule passes → NOT fails."""
        rule = MustIncludeRule(["hello"])  # Will pass
        group = NotGroup(rule)
        result = group.evaluate("hello world", latency_ms=100)
        
        assert result.passed is False
        assert "NOT group failed" in result.violation_message
        assert "unexpectedly passed" in result.violation_message


class TestEvaluatorWithGroups:
    """Test Evaluator builder methods for groups."""
    
    def test_evaluator_and_group(self):
        """Evaluator.and_group() works correctly."""
        evaluator = Evaluator()
        evaluator.and_group([
            MustIncludeRule(["hello"]),
            MaxLatencyRule(1000),
        ], name="basic_check")
        
        verdict = evaluator.evaluate("hello world", latency_ms=500)
        assert verdict.status == "pass"
    
    def test_evaluator_or_group(self):
        """Evaluator.or_group() works correctly."""
        evaluator = Evaluator()
        evaluator.or_group([
            MustIncludeRule(["goodbye"]),  # fails
            MustIncludeRule(["hello"]),    # passes
        ])
        
        verdict = evaluator.evaluate("hello world", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_evaluator_not_rule(self):
        """Evaluator.not_rule() works correctly."""
        evaluator = Evaluator()
        evaluator.not_rule(MustIncludeRule(["error"]))
        
        verdict = evaluator.evaluate("success response", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_nested_groups(self):
        """Groups can be nested."""
        # (A AND B) OR (C AND D)
        group1 = AndGroup([
            MustIncludeRule(["hello"]),
            MustIncludeRule(["world"]),
        ])
        group2 = AndGroup([
            MustIncludeRule(["goodbye"]),
            MustIncludeRule(["moon"]),
        ])
        
        outer = OrGroup([group1, group2])
        result = outer.evaluate("hello world", latency_ms=100)
        
        assert result.passed is True  # group1 passes
    
    def test_complex_composition(self):
        """Complex logical composition."""
        evaluator = Evaluator()
        
        # Must include "hello" AND (include "world" OR include "moon")
        evaluator.and_group([
            MustIncludeRule(["hello"]),
            OrGroup([
                MustIncludeRule(["world"]),
                MustIncludeRule(["moon"]),
            ]),
        ])
        
        verdict = evaluator.evaluate("hello moon", latency_ms=100)
        assert verdict.status == "pass"


class TestGroupVerdictSemantics:
    """Verify PASS/FAIL binary semantics are preserved."""
    
    def test_no_partial_pass(self):
        """Groups never return partial pass."""
        rules = [
            MustIncludeRule(["a"]),
            MustIncludeRule(["b"]),
            MustIncludeRule(["c"]),  # will fail
        ]
        group = AndGroup(rules)
        result = group.evaluate("a b", latency_ms=100)
        
        # Not "2 of 3 passed" - just FAIL
        assert result.passed is False
        assert "partially" not in result.violation_message.lower()
    
    def test_no_scoring(self):
        """No numeric scores in results."""
        rules = [
            MustIncludeRule(["a"]),
            MustIncludeRule(["b"]),
        ]
        group = AndGroup(rules)
        result = group.evaluate("a b c", latency_ms=100)
        
        # Result is boolean, not scored
        assert isinstance(result.passed, bool)
        assert not hasattr(result, 'score')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
