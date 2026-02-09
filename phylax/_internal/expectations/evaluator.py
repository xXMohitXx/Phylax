"""
Expectation Evaluator

Evaluates a set of rules against an LLM response and produces a Verdict.

Design rules:
- Verdicts are computed at trace creation time (never deferred)
- Verdicts are immutable once written
- All violations are reported (not short-circuited)
- Severity is the maximum of all violations
"""

from typing import Optional

from phylax._internal.schema import Verdict, SeverityLevel
from phylax._internal.expectations.rules import (
    Rule,
    RuleResult,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
)
from phylax._internal.expectations.groups import (
    ExpectationGroup,
    AndGroup,
    OrGroup,
    NotGroup,
)
from phylax._internal.expectations.conditionals import (
    Condition,
    ConditionalExpectation,
    InputContains,
    ModelEquals,
    ProviderEquals,
    MetadataEquals,
    FlagSet,
    when,
)
from phylax._internal.expectations.scoping import (
    ExpectationScope,
    ScopedExpectation,
    for_node,
    for_provider,
    for_stage,
    for_tool,
    scoped,
)
from phylax._internal.expectations.templates import (
    ExpectationTemplate,
    TemplateRegistry,
    get_registry,
    get_template,
    get_template_rules,
)


class Evaluator:
    """
    Evaluates rules against LLM responses.
    
    Usage:
        evaluator = Evaluator()
        evaluator.add_rule(MustIncludeRule(["refund"]))
        evaluator.add_rule(MaxLatencyRule(1500))
        verdict = evaluator.evaluate(response_text, latency_ms)
    """
    
    def __init__(self):
        self.rules: list[Rule] = []
    
    def add_rule(self, rule: Rule) -> "Evaluator":
        """Add a rule to the evaluator. Returns self for chaining."""
        self.rules.append(rule)
        return self
    
    def must_include(self, substrings: list[str], case_sensitive: bool = False) -> "Evaluator":
        """Add a must_include rule."""
        return self.add_rule(MustIncludeRule(substrings, case_sensitive))
    
    def must_not_include(self, substrings: list[str], case_sensitive: bool = False) -> "Evaluator":
        """Add a must_not_include rule."""
        return self.add_rule(MustNotIncludeRule(substrings, case_sensitive))
    
    def max_latency_ms(self, max_ms: int) -> "Evaluator":
        """Add a max_latency_ms rule."""
        return self.add_rule(MaxLatencyRule(max_ms))
    
    def min_tokens(self, min_tokens: int) -> "Evaluator":
        """Add a min_tokens rule."""
        return self.add_rule(MinTokensRule(min_tokens))
    
    # --- Axis 1 Phase 1: Expectation Composition (Logical Algebra) ---
    
    def and_group(self, rules: list[Rule], name: str = "and_group") -> "Evaluator":
        """
        Add an AND group: all rules must pass.
        
        Args:
            rules: List of rules that must all pass
            name: Optional name for failure attribution
        """
        return self.add_rule(AndGroup(rules, name=name))
    
    def or_group(self, rules: list[Rule], name: str = "or_group") -> "Evaluator":
        """
        Add an OR group: at least one rule must pass.
        
        Args:
            rules: List of rules where at least one must pass
            name: Optional name for failure attribution
        """
        return self.add_rule(OrGroup(rules, name=name))
    
    def not_rule(self, rule: Rule, name: str = "not_group") -> "Evaluator":
        """
        Add a NOT group: the rule must FAIL for group to PASS.
        
        Args:
            rule: Single rule to negate
            name: Optional name for failure attribution
        """
        return self.add_rule(NotGroup(rule, name=name))
    
    # --- Axis 1 Phase 2: Conditional Expectations ---
    
    def when_if(
        self,
        condition: Condition,
        rule: Rule,
        name: str | None = None,
    ) -> "Evaluator":
        """
        Add a conditional expectation: rule only activates when condition is met.
        
        Args:
            condition: Condition that must be met for rule to activate
            rule: The rule to evaluate if condition is met
            name: Optional name for failure attribution
            
        Example:
            evaluator.when_if(
                InputContains("refund"),
                MustIncludeRule(["policy"])
            )
        """
        conditional = ConditionalExpectation(condition, rule, name=name)
        return self.add_rule(conditional)
    
    def set_context(self, context: dict) -> "Evaluator":
        """
        Set context for conditional and scoped expectations.
        
        Args:
            context: Dict with 'input', 'model', 'provider', 'metadata', 'flags',
                     'node_id', 'stage', 'tool'
        """
        self._context = context
        return self
    
    # --- Axis 1 Phase 3: Expectation Scoping ---
    
    def scoped_for(
        self,
        scope: ExpectationScope,
        rule: Rule,
        name: str | None = None,
    ) -> "Evaluator":
        """
        Add a scoped expectation: rule only applies within the specified scope.
        
        Args:
            scope: Scope that must match for rule to apply
            rule: The rule to evaluate if scope matches
            name: Optional name for failure attribution
            
        Example:
            evaluator.scoped_for(
                for_provider("openai"),
                MaxLatencyRule(2000)
            )
        """
        scoped_rule = ScopedExpectation(scope, rule, name=name)
        return self.add_rule(scoped_rule)
    
    # --- Axis 1 Phase 4: Expectation Templates ---
    
    def use_template(self, name: str) -> "Evaluator":
        """
        Apply all rules from a named template.
        
        Templates are looked up from the global registry.
        
        Args:
            name: Name of the template to apply
            
        Example:
            evaluator.use_template("safe-response")
            evaluator.use_template("latency-standard")
        """
        rules = get_template_rules(name)
        for rule in rules:
            self.add_rule(rule)
        return self
    
    # --- Axis 1 Phase 5: Expectation Documentation ---
    
    def describe(self) -> str:
        """
        Generate human-readable description of all expectations.
        
        Returns:
            Formatted string listing all rules and their descriptions.
            
        Example:
            print(evaluator.describe())
        """
        # Import here to avoid circular dependency
        from phylax._internal.expectations.documentation import list_contracts
        return list_contracts(self.rules)
    
    def to_markdown(
        self,
        title: str = "Phylax Contract",
        description: str = "",
    ) -> str:
        """
        Export contract as Markdown documentation.
        
        Args:
            title: Document title
            description: Optional description text
            
        Returns:
            Markdown-formatted contract documentation.
        """
        from phylax._internal.expectations.documentation import export_contract_markdown
        return export_contract_markdown(self.rules, title=title, description=description)
    
    def evaluate(self, response_text: str, latency_ms: int) -> Verdict:
        """
        Evaluate all rules and produce a verdict.
        
        All rules are evaluated (no short-circuit).
        Severity is the maximum of all violations.
        """
        if not self.rules:
            return Verdict(status="pass")
        
        results: list[RuleResult] = []
        for rule in self.rules:
            # Pass context to conditional expectations (Axis 1 Phase 2)
            if isinstance(rule, ConditionalExpectation) and hasattr(self, '_context'):
                rule.with_context(self._context)
            # Pass context to scoped expectations (Axis 1 Phase 3)
            if isinstance(rule, ScopedExpectation) and hasattr(self, '_context'):
                rule.with_context(self._context)
            result = rule.evaluate(response_text, latency_ms)
            results.append(result)
        
        # Collect all violations
        violations = [r.violation_message for r in results if not r.passed]
        
        if not violations:
            return Verdict(status="pass")
        
        # Determine max severity
        severity_order = {"low": 0, "medium": 1, "high": 2}
        max_severity: SeverityLevel = "low"
        
        for result in results:
            if not result.passed:
                if severity_order[result.severity] > severity_order[max_severity]:
                    max_severity = result.severity
        
        return Verdict(
            status="fail",
            severity=max_severity,
            violations=violations,
        )


def evaluate(
    response_text: str,
    latency_ms: int,
    must_include: Optional[list[str]] = None,
    must_not_include: Optional[list[str]] = None,
    max_latency_ms: Optional[int] = None,
    min_tokens: Optional[int] = None,
) -> Verdict:
    """
    Convenience function to evaluate expectations.
    
    Args:
        response_text: The LLM response text
        latency_ms: Response latency in milliseconds
        must_include: Substrings that must appear
        must_not_include: Substrings that must NOT appear
        max_latency_ms: Maximum latency threshold
        min_tokens: Minimum token count
        
    Returns:
        Verdict with pass/fail status and any violations
    """
    evaluator = Evaluator()
    
    if must_include:
        evaluator.must_include(must_include)
    
    if must_not_include:
        evaluator.must_not_include(must_not_include)
    
    if max_latency_ms is not None:
        evaluator.max_latency_ms(max_latency_ms)
    
    if min_tokens is not None:
        evaluator.min_tokens(min_tokens)
    
    return evaluator.evaluate(response_text, latency_ms)
