"""
Expectation Groups (Logical Algebra)

Axis 1 · Phase 1: Expectation Composition

Enables logical relationships between expectations:
- AndGroup: All rules must pass (FAIL if any fails)
- OrGroup: At least one rule must pass (FAIL only if all fail)
- NotGroup: Rule must FAIL for group to PASS

Non-negotiable rules:
- Verdict space stays PASS/FAIL only
- No weighting, scoring, or partial passes
- Group failure collapses to a single FAIL
- Failure attribution is structural, not semantic
"""

from typing import Literal, Optional
from phylax._internal.expectations.rules import Rule, RuleResult, SeverityLevel


class ExpectationGroup(Rule):
    """
    Base class for grouped expectations.
    
    Groups allow logical composition of rules while
    maintaining binary PASS/FAIL semantics.
    """
    
    operator: Literal["AND", "OR", "NOT"] = "AND"
    name: str = "group"
    severity: SeverityLevel = "medium"
    
    def __init__(self, rules: list[Rule], name: Optional[str] = None):
        """
        Args:
            rules: List of rules in this group
            name: Optional name for failure attribution
        """
        self.rules = rules
        if name:
            self.name = name
    
    def evaluate(self, response_text: str, latency_ms: int) -> RuleResult:
        """Override in subclasses."""
        raise NotImplementedError


class AndGroup(ExpectationGroup):
    """
    All rules must pass for group to PASS.
    
    Semantics:
    - PASS: All rules pass
    - FAIL: Any rule fails
    
    Severity: Maximum of all failed rules.
    """
    
    operator: Literal["AND", "OR", "NOT"] = "AND"
    name: str = "and_group"
    
    def evaluate(self, response_text: str, latency_ms: int) -> RuleResult:
        if not self.rules:
            return RuleResult(
                passed=True,
                rule_name=self.name,
                severity="low",
            )
        
        results = [rule.evaluate(response_text, latency_ms) for rule in self.rules]
        failures = [r for r in results if not r.passed]
        
        if not failures:
            return RuleResult(
                passed=True,
                rule_name=self.name,
                severity="low",
            )
        
        # Collapse to single FAIL with max severity
        severity_order = {"low": 0, "medium": 1, "high": 2}
        max_severity: SeverityLevel = "low"
        violation_parts = []
        
        for result in failures:
            if severity_order[result.severity] > severity_order[max_severity]:
                max_severity = result.severity
            violation_parts.append(f"{result.rule_name}: {result.violation_message}")
        
        return RuleResult(
            passed=False,
            rule_name=self.name,
            severity=max_severity,
            violation_message=f"AND group failed: [{', '.join(violation_parts)}]",
        )


class OrGroup(ExpectationGroup):
    """
    At least one rule must pass for group to PASS.
    
    Semantics:
    - PASS: Any rule passes
    - FAIL: All rules fail
    
    Severity: Maximum of all failed rules (only reported on total failure).
    """
    
    operator: Literal["AND", "OR", "NOT"] = "OR"
    name: str = "or_group"
    
    def evaluate(self, response_text: str, latency_ms: int) -> RuleResult:
        if not self.rules:
            return RuleResult(
                passed=True,
                rule_name=self.name,
                severity="low",
            )
        
        results = [rule.evaluate(response_text, latency_ms) for rule in self.rules]
        passes = [r for r in results if r.passed]
        
        if passes:
            return RuleResult(
                passed=True,
                rule_name=self.name,
                severity="low",
            )
        
        # All failed - collapse to single FAIL
        severity_order = {"low": 0, "medium": 1, "high": 2}
        max_severity: SeverityLevel = "low"
        violation_parts = []
        
        for result in results:
            if severity_order[result.severity] > severity_order[max_severity]:
                max_severity = result.severity
            violation_parts.append(f"{result.rule_name}: {result.violation_message}")
        
        return RuleResult(
            passed=False,
            rule_name=self.name,
            severity=max_severity,
            violation_message=f"OR group failed (all alternatives failed): [{', '.join(violation_parts)}]",
        )


class NotGroup(ExpectationGroup):
    """
    Single rule must FAIL for group to PASS.
    
    Semantics:
    - PASS: The wrapped rule fails
    - FAIL: The wrapped rule passes
    
    Use case: "Response must NOT satisfy condition X"
    This is different from must_not_include (substring check).
    NotGroup negates any rule.
    """
    
    operator: Literal["AND", "OR", "NOT"] = "NOT"
    name: str = "not_group"
    severity: SeverityLevel = "medium"
    
    def __init__(self, rule: Rule, name: Optional[str] = None):
        """
        Args:
            rule: Single rule to negate
            name: Optional name for failure attribution
        """
        self.rules = [rule]
        self.rule = rule
        if name:
            self.name = name
    
    def evaluate(self, response_text: str, latency_ms: int) -> RuleResult:
        result = self.rule.evaluate(response_text, latency_ms)
        
        if result.passed:
            # Rule passed, so NOT fails
            return RuleResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                violation_message=f"NOT group failed: {self.rule.name} unexpectedly passed",
            )
        else:
            # Rule failed, so NOT passes
            return RuleResult(
                passed=True,
                rule_name=self.name,
                severity="low",
            )
