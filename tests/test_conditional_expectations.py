"""
Test Conditional Expectations (Axis 1 Phase 2)

Verifies IF/THEN conditional expectation logic:
- Condition not met → rule skipped (no effect on verdict)
- Condition met → rule evaluated normally
"""

import pytest
from phylax._internal.expectations import (
    Evaluator,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    ConditionalExpectation,
    InputContains,
    ModelEquals,
    ProviderEquals,
    MetadataEquals,
    FlagSet,
    when,
)


class TestInputContains:
    """Test InputContains condition."""
    
    def test_contains_match(self):
        """Condition matches when substring present."""
        condition = InputContains("refund")
        context = {"input": "I need a refund please"}
        assert condition.evaluate(context) is True
    
    def test_contains_no_match(self):
        """Condition doesn't match when substring absent."""
        condition = InputContains("refund")
        context = {"input": "Hello world"}
        assert condition.evaluate(context) is False
    
    def test_case_insensitive(self):
        """Case insensitive by default."""
        condition = InputContains("REFUND")
        context = {"input": "I need a refund please"}
        assert condition.evaluate(context) is True
    
    def test_case_sensitive(self):
        """Case sensitive when specified."""
        condition = InputContains("REFUND", case_sensitive=True)
        context = {"input": "I need a refund please"}
        assert condition.evaluate(context) is False


class TestModelEquals:
    """Test ModelEquals condition."""
    
    def test_model_match(self):
        condition = ModelEquals("gpt-4")
        assert condition.evaluate({"model": "gpt-4"}) is True
    
    def test_model_no_match(self):
        condition = ModelEquals("gpt-4")
        assert condition.evaluate({"model": "gpt-3.5-turbo"}) is False


class TestProviderEquals:
    """Test ProviderEquals condition."""
    
    def test_provider_match(self):
        condition = ProviderEquals("openai")
        assert condition.evaluate({"provider": "OpenAI"}) is True  # case insensitive
    
    def test_provider_no_match(self):
        condition = ProviderEquals("openai")
        assert condition.evaluate({"provider": "gemini"}) is False


class TestMetadataEquals:
    """Test MetadataEquals condition."""
    
    def test_metadata_match(self):
        condition = MetadataEquals("tool", "search")
        context = {"metadata": {"tool": "search", "user": "admin"}}
        assert condition.evaluate(context) is True
    
    def test_metadata_no_match(self):
        condition = MetadataEquals("tool", "search")
        context = {"metadata": {"tool": "calculator"}}
        assert condition.evaluate(context) is False
    
    def test_metadata_missing(self):
        condition = MetadataEquals("tool", "search")
        context = {"metadata": {}}
        assert condition.evaluate(context) is False


class TestFlagSet:
    """Test FlagSet condition."""
    
    def test_flag_true(self):
        condition = FlagSet("strict_mode")
        context = {"flags": {"strict_mode": True}}
        assert condition.evaluate(context) is True
    
    def test_flag_false(self):
        condition = FlagSet("strict_mode")
        context = {"flags": {"strict_mode": False}}
        assert condition.evaluate(context) is False
    
    def test_flag_missing(self):
        condition = FlagSet("strict_mode")
        context = {"flags": {}}
        assert condition.evaluate(context) is False


class TestConditionalExpectation:
    """Test ConditionalExpectation wrapper."""
    
    def test_condition_met_rule_passes(self):
        """Condition met, rule passes → PASS."""
        conditional = ConditionalExpectation(
            condition=InputContains("refund"),
            rule=MustIncludeRule(["policy"]),
        )
        conditional.with_context({"input": "I need a refund"})
        result = conditional.evaluate("See our policy here", latency_ms=100)
        
        assert result.passed is True
    
    def test_condition_met_rule_fails(self):
        """Condition met, rule fails → FAIL."""
        conditional = ConditionalExpectation(
            condition=InputContains("refund"),
            rule=MustIncludeRule(["policy"]),
        )
        conditional.with_context({"input": "I need a refund"})
        result = conditional.evaluate("Sorry, no info", latency_ms=100)
        
        assert result.passed is False
        assert "input_contains" in result.violation_message
    
    def test_condition_not_met(self):
        """Condition not met → rule skipped, returns PASS."""
        conditional = ConditionalExpectation(
            condition=InputContains("refund"),
            rule=MustIncludeRule(["policy"]),  # Would fail
        )
        conditional.with_context({"input": "Hello world"})  # No "refund"
        result = conditional.evaluate("Random response", latency_ms=100)
        
        assert result.passed is True  # Skipped, no effect


class TestWhenBuilder:
    """Test when().then() fluent builder."""
    
    def test_when_then_builder(self):
        """when(condition).then(rule) creates conditional."""
        conditional = when(InputContains("error")).then(
            MustNotIncludeRule(["crash"]),
            name="error_handling"
        )
        
        assert isinstance(conditional, ConditionalExpectation)
        assert conditional.name == "error_handling"


class TestEvaluatorWithConditionals:
    """Test Evaluator integration with conditionals."""
    
    def test_evaluator_when_if(self):
        """Evaluator.when_if() integrates correctly."""
        evaluator = Evaluator()
        evaluator.set_context({"input": "I want a refund"})
        evaluator.when_if(
            InputContains("refund"),
            MustIncludeRule(["policy"])
        )
        
        verdict = evaluator.evaluate("See our policy", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_evaluator_conditional_skip(self):
        """Conditional is skipped when condition not met."""
        evaluator = Evaluator()
        evaluator.set_context({"input": "Hello world"})  # No "refund"
        evaluator.when_if(
            InputContains("refund"),
            MustIncludeRule(["policy"])  # Would fail, but skipped
        )
        
        verdict = evaluator.evaluate("Random response", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_evaluator_with_model_condition(self):
        """Model-based conditional works."""
        evaluator = Evaluator()
        evaluator.set_context({"model": "gpt-4", "input": "test"})
        evaluator.when_if(
            ModelEquals("gpt-4"),
            MaxLatencyRule(2000)
        )
        
        verdict = evaluator.evaluate("Response", latency_ms=1500)
        assert verdict.status == "pass"
        
        verdict = evaluator.evaluate("Response", latency_ms=3000)
        assert verdict.status == "fail"
    
    def test_mixed_conditional_and_regular(self):
        """Mix of conditional and regular rules."""
        evaluator = Evaluator()
        evaluator.set_context({"input": "refund request"})
        
        # Regular rule - always applies
        evaluator.must_include(["response"])
        
        # Conditional rule - only for refund requests
        evaluator.when_if(
            InputContains("refund"),
            MustIncludeRule(["policy"])
        )
        
        # Both pass
        verdict = evaluator.evaluate("response with policy", latency_ms=100)
        assert verdict.status == "pass"
        
        # Regular fails
        verdict = evaluator.evaluate("policy only", latency_ms=100)
        assert verdict.status == "fail"


class TestConditionalSemantics:
    """Verify deterministic, non-inferential semantics."""
    
    def test_no_fuzzy_matching(self):
        """Conditions use exact matching, not similarity."""
        condition = InputContains("refund")
        
        # Similar but not match
        assert condition.evaluate({"input": "return item"}) is False
        assert condition.evaluate({"input": "money back"}) is False
        
        # Exact match required
        assert condition.evaluate({"input": "refund"}) is True
    
    def test_inactive_no_verdict_effect(self):
        """Inactive conditionals don't affect verdict."""
        evaluator = Evaluator()
        evaluator.set_context({"input": "no match here"})
        
        # Add conditional that would fail if activated
        evaluator.when_if(
            InputContains("trigger"),
            MustIncludeRule(["required_text"])
        )
        
        # Should pass because conditional is inactive
        verdict = evaluator.evaluate("anything", latency_ms=100)
        assert verdict.status == "pass"
        assert not verdict.violations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
