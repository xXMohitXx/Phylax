"""
Test Expectation Scoping (Axis 1 Phase 3)

Verifies scoped expectation targeting:
- Scope doesn't match → rule skipped
- Scope matches → rule evaluated
"""

import pytest
from phylax._internal.expectations import (
    Evaluator,
    MustIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    ExpectationScope,
    ScopedExpectation,
    for_node,
    for_provider,
    for_stage,
    for_tool,
    scoped,
)


class TestExpectationScope:
    """Test ExpectationScope model."""
    
    def test_empty_scope_is_global(self):
        """Empty scope matches everything."""
        scope = ExpectationScope()
        assert scope.is_global() is True
        assert scope.matches({}) is True
        assert scope.matches({"node_id": "x", "provider": "y"}) is True
    
    def test_node_scope(self):
        """Node ID scope matching."""
        scope = ExpectationScope(node_id="node-123")
        
        assert scope.is_global() is False
        assert scope.matches({"node_id": "node-123"}) is True
        assert scope.matches({"node_id": "node-456"}) is False
    
    def test_provider_scope(self):
        """Provider scope matching (case insensitive)."""
        scope = ExpectationScope(provider="openai")
        
        assert scope.matches({"provider": "openai"}) is True
        assert scope.matches({"provider": "OpenAI"}) is True
        assert scope.matches({"provider": "gemini"}) is False
    
    def test_stage_scope(self):
        """Stage scope matching."""
        scope = ExpectationScope(stage="output")
        
        assert scope.matches({"stage": "output"}) is True
        assert scope.matches({"stage": "input"}) is False
    
    def test_tool_scope(self):
        """Tool scope matching."""
        scope = ExpectationScope(tool="search")
        
        assert scope.matches({"tool": "search"}) is True
        assert scope.matches({"tool": "calculator"}) is False
    
    def test_combined_scope(self):
        """Multiple scope fields (AND semantics)."""
        scope = ExpectationScope(provider="openai", stage="output")
        
        # Both must match
        assert scope.matches({"provider": "openai", "stage": "output"}) is True
        assert scope.matches({"provider": "openai", "stage": "input"}) is False
        assert scope.matches({"provider": "gemini", "stage": "output"}) is False


class TestScopeBuilders:
    """Test convenience scope builders."""
    
    def test_for_node(self):
        scope = for_node("node-abc")
        assert scope.node_id == "node-abc"
        assert scope.is_global() is False
    
    def test_for_provider(self):
        scope = for_provider("gemini")
        assert scope.provider == "gemini"
    
    def test_for_stage(self):
        scope = for_stage("final")
        assert scope.stage == "final"
    
    def test_for_tool(self):
        scope = for_tool("web_search")
        assert scope.tool == "web_search"


class TestScopedExpectation:
    """Test ScopedExpectation wrapper."""
    
    def test_scope_matches_rule_passes(self):
        """Scope matches, rule passes → PASS."""
        scoped_rule = ScopedExpectation(
            scope=for_provider("openai"),
            rule=MustIncludeRule(["hello"]),
        )
        scoped_rule.with_context({"provider": "openai"})
        result = scoped_rule.evaluate("hello world", latency_ms=100)
        
        assert result.passed is True
    
    def test_scope_matches_rule_fails(self):
        """Scope matches, rule fails → FAIL."""
        scoped_rule = ScopedExpectation(
            scope=for_provider("openai"),
            rule=MustIncludeRule(["goodbye"]),
        )
        scoped_rule.with_context({"provider": "openai"})
        result = scoped_rule.evaluate("hello world", latency_ms=100)
        
        assert result.passed is False
        assert "Scope" in result.violation_message
    
    def test_scope_not_matches(self):
        """Scope doesn't match → rule skipped, returns PASS."""
        scoped_rule = ScopedExpectation(
            scope=for_provider("openai"),
            rule=MustIncludeRule(["goodbye"]),  # Would fail
        )
        scoped_rule.with_context({"provider": "gemini"})  # Different provider
        result = scoped_rule.evaluate("hello world", latency_ms=100)
        
        assert result.passed is True  # Skipped, no effect


class TestScopedBuilder:
    """Test scoped().expect() fluent builder."""
    
    def test_scoped_expect_builder(self):
        """scoped(scope).expect(rule) creates ScopedExpectation."""
        scoped_rule = scoped(for_provider("openai")).expect(
            MaxLatencyRule(2000),
            name="openai_latency"
        )
        
        assert isinstance(scoped_rule, ScopedExpectation)
        assert scoped_rule.name == "openai_latency"


class TestEvaluatorWithScoping:
    """Test Evaluator integration with scoping."""
    
    def test_evaluator_scoped_for(self):
        """Evaluator.scoped_for() integrates correctly."""
        evaluator = Evaluator()
        evaluator.set_context({"provider": "openai", "stage": "output"})
        evaluator.scoped_for(
            for_provider("openai"),
            MaxLatencyRule(2000)
        )
        
        verdict = evaluator.evaluate("response", latency_ms=1500)
        assert verdict.status == "pass"
        
        verdict = evaluator.evaluate("response", latency_ms=3000)
        assert verdict.status == "fail"
    
    def test_scoped_skip_different_provider(self):
        """Scoped rule skipped when provider doesn't match."""
        evaluator = Evaluator()
        evaluator.set_context({"provider": "gemini"})
        evaluator.scoped_for(
            for_provider("openai"),
            MaxLatencyRule(2000)  # Would fail, but skipped
        )
        
        verdict = evaluator.evaluate("response", latency_ms=5000)
        assert verdict.status == "pass"
    
    def test_global_and_scoped_together(self):
        """Mix of global and scoped rules."""
        evaluator = Evaluator()
        evaluator.set_context({"provider": "openai"})
        
        # Global rule - always applies
        evaluator.must_include(["response"])
        
        # Scoped rule - only for openai
        evaluator.scoped_for(
            for_provider("openai"),
            MaxLatencyRule(2000)
        )
        
        # Both pass
        verdict = evaluator.evaluate("response text", latency_ms=1500)
        assert verdict.status == "pass"
        
        # Global fails
        verdict = evaluator.evaluate("text only", latency_ms=1500)
        assert verdict.status == "fail"
    
    def test_scoped_for_node(self):
        """Node-scoped expectations work."""
        evaluator = Evaluator()
        evaluator.set_context({"node_id": "llm-call-1"})
        evaluator.scoped_for(
            for_node("llm-call-1"),
            MinTokensRule(5)
        )
        
        verdict = evaluator.evaluate("one two three four five six", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_multiple_scopes(self):
        """Multiple scoped rules for different providers."""
        evaluator = Evaluator()
        evaluator.set_context({"provider": "gemini"})
        
        # OpenAI rule (skipped)
        evaluator.scoped_for(
            for_provider("openai"),
            MaxLatencyRule(1000)
        )
        
        # Gemini rule (applied)
        evaluator.scoped_for(
            for_provider("gemini"),
            MaxLatencyRule(3000)
        )
        
        # Gemini limit is 3000ms
        verdict = evaluator.evaluate("response", latency_ms=2500)
        assert verdict.status == "pass"


class TestScopeSemantics:
    """Verify explicit, non-heuristic scope semantics."""
    
    def test_no_pattern_matching(self):
        """Scopes use exact matching, not patterns."""
        scope = for_node("node-1")
        
        # Only exact match works
        assert scope.matches({"node_id": "node-1"}) is True
        assert scope.matches({"node_id": "node-1-suffix"}) is False
        assert scope.matches({"node_id": "node"}) is False
    
    def test_out_of_scope_no_effect(self):
        """Out-of-scope rules don't affect verdict."""
        evaluator = Evaluator()
        evaluator.set_context({"provider": "ollama"})
        
        # Add scoped rule that would fail if applied
        evaluator.scoped_for(
            for_provider("openai"),
            MustIncludeRule(["required"])
        )
        
        verdict = evaluator.evaluate("no required text", latency_ms=100)
        assert verdict.status == "pass"
        assert not verdict.violations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
