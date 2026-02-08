"""
Test Expectation Documentation (Axis 1 Phase 5)

Verifies self-documenting contract features:
- Human-readable rule descriptions
- Contract listing
- Markdown export
- Evaluator integration
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
    InputContains,
    ConditionalExpectation,
    for_provider,
    ScopedExpectation,
    ExpectationTemplate,
    describe_rule,
    describe_condition,
    describe_template,
    list_contracts,
    export_contract_markdown,
    ContractDocumenter,
)


class TestDescribeRule:
    """Test describe_rule() for various rule types."""
    
    def test_must_include(self):
        """Describe MustIncludeRule."""
        rule = MustIncludeRule(["hello", "world"])
        desc = describe_rule(rule)
        
        assert "Must include" in desc
        assert '"hello"' in desc
        assert '"world"' in desc
    
    def test_must_not_include(self):
        """Describe MustNotIncludeRule."""
        rule = MustNotIncludeRule(["error", "fail"])
        desc = describe_rule(rule)
        
        assert "Must NOT include" in desc
        assert '"error"' in desc
    
    def test_max_latency(self):
        """Describe MaxLatencyRule."""
        rule = MaxLatencyRule(2000)
        desc = describe_rule(rule)
        
        assert "Latency" in desc
        assert "2000" in desc
    
    def test_min_tokens(self):
        """Describe MinTokensRule."""
        rule = MinTokensRule(10)
        desc = describe_rule(rule)
        
        assert "tokens" in desc
        assert "10" in desc
    
    def test_and_group(self):
        """Describe AndGroup."""
        group = AndGroup([
            MustIncludeRule(["hello"]),
            MaxLatencyRule(1000),
        ])
        desc = describe_rule(group)
        
        assert "AND" in desc
        assert "all must pass" in desc
        assert "hello" in desc
        assert "1000" in desc
    
    def test_or_group(self):
        """Describe OrGroup."""
        group = OrGroup([
            MustIncludeRule(["a"]),
            MustIncludeRule(["b"]),
        ])
        desc = describe_rule(group)
        
        assert "OR" in desc
        assert "at least one" in desc
    
    def test_not_group(self):
        """Describe NotGroup."""
        group = NotGroup(MustIncludeRule(["error"]))
        desc = describe_rule(group)
        
        assert "NOT" in desc
        assert "must fail" in desc
    
    def test_conditional(self):
        """Describe ConditionalExpectation."""
        conditional = ConditionalExpectation(
            condition=InputContains("refund"),
            rule=MustIncludeRule(["policy"]),
        )
        desc = describe_rule(conditional)
        
        assert "IF" in desc
        assert "THEN" in desc
        assert "refund" in desc
        assert "policy" in desc
    
    def test_scoped(self):
        """Describe ScopedExpectation."""
        scoped = ScopedExpectation(
            scope=for_provider("openai"),
            rule=MaxLatencyRule(2000),
        )
        desc = describe_rule(scoped)
        
        assert "SCOPED" in desc
        assert "openai" in desc.lower()


class TestDescribeCondition:
    """Test describe_condition() for conditions."""
    
    def test_input_contains(self):
        cond = InputContains("refund")
        desc = describe_condition(cond)
        
        assert "input contains" in desc
        assert "refund" in desc


class TestListContracts:
    """Test list_contracts() function."""
    
    def test_empty_contracts(self):
        """Empty rules list."""
        result = list_contracts([])
        assert "No expectations defined" in result
    
    def test_multiple_rules(self):
        """List multiple rules."""
        rules = [
            MustIncludeRule(["hello"]),
            MaxLatencyRule(1000),
        ]
        result = list_contracts(rules)
        
        assert "2 expectations" in result
        assert "hello" in result
        assert "1000" in result


class TestExportMarkdown:
    """Test export_contract_markdown() function."""
    
    def test_markdown_format(self):
        """Export as Markdown."""
        rules = [MustIncludeRule(["test"])]
        md = export_contract_markdown(rules, title="My Contract", description="Test desc")
        
        assert "# My Contract" in md
        assert "Test desc" in md
        assert "## Expectations" in md
        assert "test" in md
    
    def test_empty_markdown(self):
        """Empty contract Markdown."""
        md = export_contract_markdown([])
        assert "No expectations defined" in md


class TestDescribeTemplate:
    """Test describe_template() function."""
    
    def test_template_description(self):
        """Describe a template."""
        template = ExpectationTemplate(
            name="test-template",
            description="A test template",
            rules=[MustIncludeRule(["required"])],
            version="1.0.0",
        )
        desc = describe_template(template)
        
        assert "test-template" in desc
        assert "1.0.0" in desc
        assert "A test template" in desc
        assert "required" in desc


class TestContractDocumenter:
    """Test ContractDocumenter class."""
    
    def test_describe(self):
        """Documenter.describe() works."""
        evaluator = Evaluator()
        evaluator.must_include(["hello"])
        evaluator.add_rule(MaxLatencyRule(1000))
        
        documenter = ContractDocumenter(evaluator)
        desc = documenter.describe()
        
        assert "hello" in desc
        assert "1000" in desc
    
    def test_to_markdown(self):
        """Documenter.to_markdown() works."""
        evaluator = Evaluator()
        evaluator.must_include(["test"])
        
        documenter = ContractDocumenter(evaluator)
        md = documenter.to_markdown(title="Test Contract")
        
        assert "# Test Contract" in md
    
    def test_to_json(self):
        """Documenter.to_json() works."""
        evaluator = Evaluator()
        evaluator.must_include(["hello"])
        
        documenter = ContractDocumenter(evaluator)
        data = documenter.to_json()
        
        assert data["expectation_count"] == 1
        assert len(data["expectations"]) == 1
        assert "hello" in data["expectations"][0]["description"]


class TestEvaluatorDocumentation:
    """Test Evaluator.describe() and .to_markdown()."""
    
    def test_evaluator_describe(self):
        """Evaluator.describe() returns human-readable output."""
        evaluator = Evaluator()
        evaluator.must_include(["hello"])
        evaluator.add_rule(MaxLatencyRule(2000))
        
        desc = evaluator.describe()
        
        assert "hello" in desc
        assert "2000" in desc
        assert "expectations" in desc.lower()
    
    def test_evaluator_to_markdown(self):
        """Evaluator.to_markdown() returns Markdown."""
        evaluator = Evaluator()
        evaluator.must_not_include(["error"])
        
        md = evaluator.to_markdown(title="API Contract")
        
        assert "# API Contract" in md
        assert "error" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
