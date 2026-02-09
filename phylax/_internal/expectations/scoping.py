"""
Expectation Scoping & Targeting

Axis 1 · Phase 3: Expectation Scoping

Enables expectations to apply to specific parts of a trace:
- Specific nodes
- Specific providers  
- Specific execution stages
- Specific tool calls

Non-negotiable rules:
- Scope resolution is explicit
- Unscoped expectations remain global
- No dynamic scoping
- No pattern-based scoping ("all nodes like X")
- No heuristic matching
"""

from typing import Optional, Any, Literal
from dataclasses import dataclass
from phylax._internal.expectations.rules import Rule, RuleResult, SeverityLevel


@dataclass
class ExpectationScope:
    """
    Defines where an expectation applies.
    
    All fields are optional. If unspecified, expectation is global.
    Multiple fields create AND semantics (all must match).
    
    Attributes:
        node_id: Specific node ID to apply to
        provider: Specific provider name (e.g., "openai", "gemini")
        stage: Execution stage ("input", "processing", "output", "final")
        tool: Specific tool name
    """
    
    node_id: Optional[str] = None
    provider: Optional[str] = None
    stage: Optional[Literal["input", "processing", "output", "final"]] = None
    tool: Optional[str] = None
    
    def is_global(self) -> bool:
        """Returns True if no scope restrictions are set."""
        return (
            self.node_id is None and
            self.provider is None and
            self.stage is None and
            self.tool is None
        )
    
    def matches(self, context: dict[str, Any]) -> bool:
        """
        Check if the scope matches the given execution context.
        
        Args:
            context: Dict with 'node_id', 'provider', 'stage', 'tool' keys
            
        Returns:
            True if all specified scope fields match context
        """
        if self.is_global():
            return True
        
        # All specified fields must match (AND semantics)
        if self.node_id is not None:
            if context.get("node_id") != self.node_id:
                return False
        
        if self.provider is not None:
            ctx_provider = context.get("provider", "").lower()
            if ctx_provider != self.provider.lower():
                return False
        
        if self.stage is not None:
            if context.get("stage") != self.stage:
                return False
        
        if self.tool is not None:
            if context.get("tool") != self.tool:
                return False
        
        return True
    
    def __repr__(self) -> str:
        parts = []
        if self.node_id:
            parts.append(f"node={self.node_id}")
        if self.provider:
            parts.append(f"provider={self.provider}")
        if self.stage:
            parts.append(f"stage={self.stage}")
        if self.tool:
            parts.append(f"tool={self.tool}")
        if not parts:
            return "Scope(global)"
        return f"Scope({', '.join(parts)})"


class ScopedExpectation(Rule):
    """
    Expectation that only applies within a specific scope.
    
    Semantics:
    - Scope doesn't match → Rule is skipped (returns PASS, no effect)
    - Scope matches → Rule is evaluated normally
    
    Similar to ConditionalExpectation but for structural targeting,
    not runtime conditions.
    """
    
    name: str = "scoped"
    severity: SeverityLevel = "medium"
    
    def __init__(
        self,
        scope: ExpectationScope,
        rule: Rule,
        name: Optional[str] = None,
    ):
        """
        Args:
            scope: Scope that must match for rule to apply
            rule: The rule to evaluate if scope matches
            name: Optional name for failure attribution
        """
        self.scope = scope
        self.rule = rule
        if name:
            self.name = name
        else:
            self.name = f"scoped_{rule.name}"
        self.severity = rule.severity
        
        # Store context for scope evaluation
        self._context: dict[str, Any] = {}
    
    def with_context(self, context: dict[str, Any]) -> "ScopedExpectation":
        """
        Set context for scope evaluation.
        
        Args:
            context: Dict with 'node_id', 'provider', 'stage', 'tool'
        """
        self._context = context
        return self
    
    def evaluate(self, response_text: str, latency_ms: int) -> RuleResult:
        """
        Evaluate the scoped expectation.
        
        If scope doesn't match, returns PASS with no effect.
        If scope matches, evaluates and returns the wrapped rule's result.
        """
        # Check if scope matches
        if not self.scope.matches(self._context):
            # Scope doesn't match - skip (no effect on verdict)
            return RuleResult(
                passed=True,
                rule_name=self.name,
                severity="low",
                violation_message="",  # No message - out of scope
            )
        
        # Scope matches - evaluate wrapped rule
        result = self.rule.evaluate(response_text, latency_ms)
        
        # Re-wrap result with scoped name for attribution
        if not result.passed:
            return RuleResult(
                passed=False,
                rule_name=self.name,
                severity=result.severity,
                violation_message=f"[{self.scope}] {result.violation_message}",
            )
        
        return RuleResult(
            passed=True,
            rule_name=self.name,
            severity="low",
        )


# Convenience builders for common scopes

def for_node(node_id: str) -> ExpectationScope:
    """Create scope for a specific node."""
    return ExpectationScope(node_id=node_id)


def for_provider(provider: str) -> ExpectationScope:
    """Create scope for a specific provider."""
    return ExpectationScope(provider=provider)


def for_stage(stage: Literal["input", "processing", "output", "final"]) -> ExpectationScope:
    """Create scope for a specific execution stage."""
    return ExpectationScope(stage=stage)


def for_tool(tool: str) -> ExpectationScope:
    """Create scope for a specific tool."""
    return ExpectationScope(tool=tool)


class ScopeBuilder:
    """
    Fluent builder for creating scoped expectations.
    
    Usage:
        scoped(for_provider("openai")).expect(MaxLatencyRule(2000))
    """
    
    def __init__(self, scope: ExpectationScope):
        self.scope = scope
    
    def expect(self, rule: Rule, name: Optional[str] = None) -> ScopedExpectation:
        """Create scoped expectation with the given rule."""
        return ScopedExpectation(self.scope, rule, name=name)


def scoped(scope: ExpectationScope) -> ScopeBuilder:
    """
    Start building a scoped expectation.
    
    Usage:
        scoped(for_provider("openai")).expect(MaxLatencyRule(2000))
    """
    return ScopeBuilder(scope)
