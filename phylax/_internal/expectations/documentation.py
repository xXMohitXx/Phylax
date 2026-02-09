"""
Expectation Documentation & Self-Description

Axis 1 · Phase 5: Expectation Documentation

Makes contracts self-documenting through:
- Human-readable rule descriptions
- Contract listing and export
- IDE-friendly documentation

Non-negotiable rules:
- Documentation is generated, not inferred
- No runtime interpretation
- No semantic analysis of rule intent
"""

from typing import Optional, Any
from phylax._internal.expectations.rules import (
    Rule,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
)
from phylax._internal.expectations.groups import AndGroup, OrGroup, NotGroup
from phylax._internal.expectations.conditionals import (
    ConditionalExpectation,
    InputContains,
    ModelEquals,
    ProviderEquals,
    MetadataEquals,
    FlagSet,
)
from phylax._internal.expectations.scoping import ScopedExpectation
from phylax._internal.expectations.templates import ExpectationTemplate


def describe_rule(rule: Rule, indent: int = 0) -> str:
    """
    Generate human-readable description of a rule.
    
    Returns a string describing what the rule checks.
    """
    prefix = "  " * indent
    
    if isinstance(rule, MustIncludeRule):
        keywords = ", ".join(f'"{kw}"' for kw in rule.substrings)
        return f"{prefix}✓ Must include: {keywords}"
    
    if isinstance(rule, MustNotIncludeRule):
        keywords = ", ".join(f'"{kw}"' for kw in rule.substrings)
        return f"{prefix}✗ Must NOT include: {keywords}"
    
    if isinstance(rule, MaxLatencyRule):
        return f"{prefix}⏱ Latency must be < {rule.max_ms}ms"
    
    if isinstance(rule, MinTokensRule):
        return f"{prefix}📝 Response must have ≥ {rule.min_tokens} tokens"
    
    if isinstance(rule, AndGroup):
        lines = [f"{prefix}AND (all must pass):"]
        for child in rule.rules:
            lines.append(describe_rule(child, indent + 1))
        return "\n".join(lines)
    
    if isinstance(rule, OrGroup):
        lines = [f"{prefix}OR (at least one must pass):"]
        for child in rule.rules:
            lines.append(describe_rule(child, indent + 1))
        return "\n".join(lines)
    
    if isinstance(rule, NotGroup):
        lines = [f"{prefix}NOT (must fail):"]
        lines.append(describe_rule(rule.rule, indent + 1))
        return "\n".join(lines)
    
    if isinstance(rule, ConditionalExpectation):
        condition_desc = describe_condition(rule.condition)
        lines = [f"{prefix}IF {condition_desc} THEN:"]
        lines.append(describe_rule(rule.rule, indent + 1))
        return "\n".join(lines)
    
    if isinstance(rule, ScopedExpectation):
        scope_desc = str(rule.scope)
        lines = [f"{prefix}SCOPED TO {scope_desc}:"]
        lines.append(describe_rule(rule.rule, indent + 1))
        return "\n".join(lines)
    
    # Fallback for unknown rules
    return f"{prefix}Rule: {rule.name}"


def describe_condition(condition) -> str:
    """Generate human-readable description of a condition."""
    if isinstance(condition, InputContains):
        return f'input contains "{condition.substring}"'
    
    if isinstance(condition, ModelEquals):
        return f'model = "{condition.model}"'
    
    if isinstance(condition, ProviderEquals):
        return f'provider = "{condition.provider}"'
    
    if isinstance(condition, MetadataEquals):
        return f'metadata["{condition.key}"] = "{condition.value}"'
    
    if isinstance(condition, FlagSet):
        return f'flag "{condition.flag_name}" is set'
    
    return f"condition: {condition.name}"


def describe_template(template: ExpectationTemplate) -> str:
    """Generate human-readable documentation for a template."""
    lines = [
        f"Template: {template.name} (v{template.version})",
        f"Description: {template.description}",
        "Rules:",
    ]
    
    for rule in template.rules:
        lines.append(describe_rule(rule, indent=1))
    
    return "\n".join(lines)


def list_contracts(rules: list[Rule]) -> str:
    """
    Generate a contract listing for a set of rules.
    
    Returns a formatted string showing all expectations.
    """
    if not rules:
        return "No expectations defined."
    
    lines = [f"Contract ({len(rules)} expectations):"]
    lines.append("-" * 40)
    
    for i, rule in enumerate(rules, 1):
        lines.append(f"{i}. {describe_rule(rule).strip()}")
    
    return "\n".join(lines)


def export_contract_markdown(
    rules: list[Rule],
    title: str = "Phylax Contract",
    description: str = "",
) -> str:
    """
    Export contract as Markdown documentation.
    
    Suitable for including in README or docs.
    """
    lines = [f"# {title}"]
    
    if description:
        lines.append("")
        lines.append(description)
    
    lines.append("")
    lines.append("## Expectations")
    lines.append("")
    
    if not rules:
        lines.append("*No expectations defined.*")
    else:
        for i, rule in enumerate(rules, 1):
            desc = describe_rule(rule).strip()
            lines.append(f"**{i}.** {desc}")
            lines.append("")
    
    return "\n".join(lines)


class ContractDocumenter:
    """
    Generates documentation for Evaluator contracts.
    
    Usage:
        documenter = ContractDocumenter(evaluator)
        print(documenter.describe())
        print(documenter.to_markdown())
    """
    
    def __init__(self, evaluator):
        self.evaluator = evaluator
    
    def describe(self) -> str:
        """Generate human-readable contract description."""
        return list_contracts(self.evaluator.rules)
    
    def to_markdown(
        self,
        title: str = "Phylax Contract",
        description: str = "",
    ) -> str:
        """Export contract as Markdown."""
        return export_contract_markdown(
            self.evaluator.rules,
            title=title,
            description=description,
        )
    
    def to_json(self) -> dict:
        """Export contract as JSON-serializable dict."""
        return {
            "expectation_count": len(self.evaluator.rules),
            "expectations": [
                {
                    "name": rule.name,
                    "severity": rule.severity,
                    "description": describe_rule(rule).strip(),
                }
                for rule in self.evaluator.rules
            ],
        }
