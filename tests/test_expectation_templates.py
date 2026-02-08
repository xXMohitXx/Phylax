"""
Test Expectation Templates (Axis 1 Phase 4)

Verifies template system:
- Template registration and retrieval
- Built-in templates
- Evaluator integration
"""

import pytest
from phylax._internal.expectations import (
    Evaluator,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    ExpectationTemplate,
    TemplateRegistry,
    get_registry,
    register_template,
    get_template,
    get_template_rules,
)


class TestExpectationTemplate:
    """Test ExpectationTemplate model."""
    
    def test_template_creation(self):
        """Create a template with rules."""
        template = ExpectationTemplate(
            name="test-template",
            description="A test template",
            rules=[MustIncludeRule(["hello"])],
            version="1.0.0",
        )
        
        assert template.name == "test-template"
        assert len(template.get_rules()) == 1
    
    def test_template_repr(self):
        """Template has useful repr."""
        template = ExpectationTemplate(
            name="my-template",
            description="Test",
            rules=[MustIncludeRule(["a"]), MaxLatencyRule(1000)],
        )
        
        assert "my-template" in repr(template)
        assert "2 rules" in repr(template)


class TestTemplateRegistry:
    """Test TemplateRegistry."""
    
    def test_register_and_get(self):
        """Register and retrieve template."""
        registry = TemplateRegistry()
        template = ExpectationTemplate(
            name="custom",
            description="Custom template",
            rules=[MustIncludeRule(["required"])],
        )
        
        registry.register(template)
        retrieved = registry.get("custom")
        
        assert retrieved.name == "custom"
        assert len(retrieved.get_rules()) == 1
    
    def test_register_duplicate_fails(self):
        """Cannot register same name twice."""
        registry = TemplateRegistry()
        template1 = ExpectationTemplate(name="same", description="First", rules=[])
        template2 = ExpectationTemplate(name="same", description="Second", rules=[])
        
        registry.register(template1)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(template2)
    
    def test_register_or_update(self):
        """register_or_update replaces existing."""
        registry = TemplateRegistry()
        template1 = ExpectationTemplate(name="same", description="First", rules=[])
        template2 = ExpectationTemplate(
            name="same", description="Second", rules=[MaxLatencyRule(1000)]
        )
        
        registry.register(template1)
        registry.register_or_update(template2)
        
        assert registry.get("same").description == "Second"
    
    def test_get_nonexistent_fails(self):
        """Get nonexistent template raises KeyError."""
        registry = TemplateRegistry()
        
        with pytest.raises(KeyError, match="not found"):
            registry.get("nonexistent")
    
    def test_exists(self):
        """Check if template exists."""
        registry = TemplateRegistry()
        registry.register(ExpectationTemplate(name="exists", description="", rules=[]))
        
        assert registry.exists("exists") is True
        assert registry.exists("does-not-exist") is False
    
    def test_list_templates(self):
        """List all template names."""
        registry = TemplateRegistry()
        registry.register(ExpectationTemplate(name="a", description="", rules=[]))
        registry.register(ExpectationTemplate(name="b", description="", rules=[]))
        
        names = registry.list_templates()
        assert "a" in names
        assert "b" in names


class TestGlobalRegistry:
    """Test global registry functions."""
    
    def test_get_registry(self):
        """get_registry returns singleton."""
        registry = get_registry()
        assert isinstance(registry, TemplateRegistry)
    
    def test_builtin_templates_registered(self):
        """Built-in templates are auto-registered."""
        registry = get_registry()
        
        # Check built-in templates exist
        assert registry.exists("safe-response")
        assert registry.exists("latency-fast")
        assert registry.exists("latency-standard")
        assert registry.exists("latency-slow")
        assert registry.exists("minimum-response")
        assert registry.exists("detailed-response")
    
    def test_get_template(self):
        """get_template retrieves from global registry."""
        template = get_template("safe-response")
        assert template.name == "safe-response"
    
    def test_get_template_rules(self):
        """get_template_rules returns rules list."""
        rules = get_template_rules("latency-standard")
        assert len(rules) > 0


class TestBuiltinTemplates:
    """Test built-in template behavior."""
    
    def test_safe_response_blocks_apology(self):
        """safe-response blocks apologies."""
        rules = get_template_rules("safe-response")
        
        evaluator = Evaluator()
        for rule in rules:
            evaluator.add_rule(rule)
        
        verdict = evaluator.evaluate("Sorry, I cannot help with that", latency_ms=100)
        assert verdict.status == "fail"
    
    def test_safe_response_allows_normal(self):
        """safe-response allows normal responses."""
        rules = get_template_rules("safe-response")
        
        evaluator = Evaluator()
        for rule in rules:
            evaluator.add_rule(rule)
        
        verdict = evaluator.evaluate("Here is the information you requested", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_latency_standard(self):
        """latency-standard checks 3s threshold."""
        rules = get_template_rules("latency-standard")
        
        evaluator = Evaluator()
        for rule in rules:
            evaluator.add_rule(rule)
        
        verdict = evaluator.evaluate("response", latency_ms=2000)
        assert verdict.status == "pass"
        
        verdict = evaluator.evaluate("response", latency_ms=4000)
        assert verdict.status == "fail"


class TestEvaluatorWithTemplates:
    """Test Evaluator.use_template() integration."""
    
    def test_use_template(self):
        """Evaluator.use_template() applies rules."""
        evaluator = Evaluator()
        evaluator.use_template("latency-fast")
        
        verdict = evaluator.evaluate("response", latency_ms=500)
        assert verdict.status == "pass"
        
        verdict = evaluator.evaluate("response", latency_ms=2000)
        assert verdict.status == "fail"
    
    def test_multiple_templates(self):
        """Can use multiple templates."""
        evaluator = Evaluator()
        evaluator.use_template("safe-response")
        evaluator.use_template("minimum-response")
        
        # Both templates apply (minimum-response needs 10+ tokens)
        verdict = evaluator.evaluate(
            "This is a normal response that contains enough words to pass the minimum token check",
            latency_ms=100
        )
        assert verdict.status == "pass"
        
        # Too short
        verdict = evaluator.evaluate("Hi", latency_ms=100)
        assert verdict.status == "fail"
    
    def test_template_with_custom_rules(self):
        """Mix templates with custom rules."""
        evaluator = Evaluator()
        evaluator.use_template("latency-standard")
        evaluator.must_include(["required"])
        
        verdict = evaluator.evaluate("required text", latency_ms=2000)
        assert verdict.status == "pass"
        
        verdict = evaluator.evaluate("missing text", latency_ms=2000)
        assert verdict.status == "fail"


class TestTemplateSemantics:
    """Verify static, explicit template semantics."""
    
    def test_templates_are_static(self):
        """Templates don't change based on context."""
        template = get_template("latency-standard")
        rules1 = template.get_rules()
        rules2 = template.get_rules()
        
        # Same rules each time
        assert len(rules1) == len(rules2)
    
    def test_no_adaptive_behavior(self):
        """Templates have no adaptive/learning behavior."""
        evaluator = Evaluator()
        evaluator.use_template("latency-fast")
        
        # Same threshold every time
        verdict1 = evaluator.evaluate("response", latency_ms=1500)
        verdict2 = evaluator.evaluate("response", latency_ms=1500)
        
        assert verdict1.status == verdict2.status == "fail"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
