"""
Conditional Expectations

Axis 1 · Phase 2: Conditional Expectations

Enables contracts that activate based on explicit, inspectable conditions:
- IF input contains X → output must contain Y
- IF model = gpt-4 → latency < 2s
- IF tool = search → response must include citation

Conditions are:
- Exact string matches
- Exact metadata matches
- Explicit flags

Non-negotiable rules:
- Conditions are declared, not inferred
- No runtime reasoning
- Inactive expectations do not affect verdicts
"""

from typing import Optional, Callable, Any, Literal
from phylax._internal.expectations.rules import Rule, RuleResult, SeverityLevel


class Condition:
    """
    Base class for conditions that gate expectation activation.
    
    Conditions are deterministic checks that return True/False.
    No fuzzy logic, no heuristics.
    """
    
    name: str = "condition"
    
    def evaluate(self, context: dict[str, Any]) -> bool:
        """
        Evaluate whether condition is met.
        
        Args:
            context: Dictionary with keys like 'input', 'model', 'provider', 'metadata'
            
        Returns:
            True if condition is satisfied, False otherwise
        """
        raise NotImplementedError


class InputContains(Condition):
    """
    Condition: input contains exact substring.
    
    Example: IF input contains "refund" → apply expectation
    """
    
    name = "input_contains"
    
    def __init__(self, substring: str, case_sensitive: bool = False):
        self.substring = substring
        self.case_sensitive = case_sensitive
    
    def evaluate(self, context: dict[str, Any]) -> bool:
        input_text = context.get("input", "")
        if not self.case_sensitive:
            input_text = input_text.lower()
            substring = self.substring.lower()
        else:
            substring = self.substring
        return substring in input_text


class ModelEquals(Condition):
    """
    Condition: model name equals exact value.
    
    Example: IF model = "gpt-4" → apply expectation
    """
    
    name = "model_equals"
    
    def __init__(self, model: str):
        self.model = model
    
    def evaluate(self, context: dict[str, Any]) -> bool:
        return context.get("model", "") == self.model


class ProviderEquals(Condition):
    """
    Condition: provider equals exact value.
    
    Example: IF provider = "openai" → apply expectation
    """
    
    name = "provider_equals"
    
    def __init__(self, provider: str):
        self.provider = provider.lower()
    
    def evaluate(self, context: dict[str, Any]) -> bool:
        return context.get("provider", "").lower() == self.provider


class MetadataEquals(Condition):
    """
    Condition: metadata key equals exact value.
    
    Example: IF metadata["tool"] = "search" → apply expectation
    """
    
    name = "metadata_equals"
    
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
    
    def evaluate(self, context: dict[str, Any]) -> bool:
        metadata = context.get("metadata", {})
        return metadata.get(self.key) == self.value


class FlagSet(Condition):
    """
    Condition: explicit flag is set to True.
    
    Example: IF flag "strict_mode" → apply expectation
    """
    
    name = "flag_set"
    
    def __init__(self, flag_name: str):
        self.flag_name = flag_name
    
    def evaluate(self, context: dict[str, Any]) -> bool:
        flags = context.get("flags", {})
        return flags.get(self.flag_name, False) is True


class ConditionalExpectation(Rule):
    """
    Expectation that only activates when condition is met.
    
    Semantics:
    - Condition FALSE → Rule is skipped (returns PASS, no effect on verdict)
    - Condition TRUE → Rule is evaluated normally
    
    This is IF/THEN logic, not filtering.
    Inactive expectations do not contribute to verdict.
    """
    
    name: str = "conditional"
    severity: SeverityLevel = "medium"
    
    def __init__(
        self,
        condition: Condition,
        rule: Rule,
        name: Optional[str] = None,
    ):
        """
        Args:
            condition: Condition that must be met for rule to activate
            rule: The rule to evaluate if condition is met
            name: Optional name for failure attribution
        """
        self.condition = condition
        self.rule = rule
        if name:
            self.name = name
        else:
            self.name = f"if_{condition.name}_then_{rule.name}"
        self.severity = rule.severity
        
        # Store context for evaluation
        self._context: dict[str, Any] = {}
    
    def with_context(self, context: dict[str, Any]) -> "ConditionalExpectation":
        """
        Set context for condition evaluation.
        
        Args:
            context: Dict with 'input', 'model', 'provider', 'metadata', 'flags'
        """
        self._context = context
        return self
    
    def evaluate(self, response_text: str, latency_ms: int) -> RuleResult:
        """
        Evaluate the conditional expectation.
        
        If condition is not met, returns PASS with no effect.
        If condition is met, evaluates and returns the wrapped rule's result.
        """
        # Check condition
        if not self.condition.evaluate(self._context):
            # Condition not met - skip (no effect on verdict)
            return RuleResult(
                passed=True,
                rule_name=self.name,
                severity="low",
                violation_message="",  # No message - inactive
            )
        
        # Condition met - evaluate wrapped rule
        result = self.rule.evaluate(response_text, latency_ms)
        
        # Re-wrap result with conditional name for attribution
        if not result.passed:
            return RuleResult(
                passed=False,
                rule_name=self.name,
                severity=result.severity,
                violation_message=f"[{self.condition.name}] {result.violation_message}",
            )
        
        return RuleResult(
            passed=True,
            rule_name=self.name,
            severity="low",
        )


class ConditionBuilder:
    """
    Fluent builder for creating conditional expectations.
    
    Usage:
        when(InputContains("refund")).then(MustIncludeRule(["policy"]))
    """
    
    def __init__(self, condition: Condition):
        self.condition = condition
    
    def then(self, rule: Rule, name: Optional[str] = None) -> ConditionalExpectation:
        """Create conditional expectation with the given rule."""
        return ConditionalExpectation(self.condition, rule, name=name)


def when(condition: Condition) -> ConditionBuilder:
    """
    Start building a conditional expectation.
    
    Usage:
        when(InputContains("refund")).then(MustIncludeRule(["policy"]))
    """
    return ConditionBuilder(condition)
