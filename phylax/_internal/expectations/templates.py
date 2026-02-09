"""
Expectation Templates

Axis 1 · Phase 4: Expectation Reuse & Templates

Prevents contract drift and copy-paste entropy through:
- Named expectation templates
- Reuse across executions
- Centralized contract definitions

Non-negotiable rules:
- Templates are static
- Overrides must be explicit
- No parameter auto-tuning
- No adaptive templates
- No context-dependent defaults
"""

from typing import Optional, Any
from dataclasses import dataclass, field
from phylax._internal.expectations.rules import (
    Rule,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
)
from phylax._internal.expectations.groups import AndGroup, OrGroup


@dataclass
class ExpectationTemplate:
    """
    A named, reusable set of expectations.
    
    Templates are defined once and referenced by name.
    They provide consistent contract definitions across executions.
    
    Attributes:
        name: Unique identifier for the template
        description: Human-readable description of the contract
        rules: List of rules that make up this template
        version: Optional version string for tracking changes
    """
    
    name: str
    description: str
    rules: list[Rule] = field(default_factory=list)
    version: str = "1.0.0"
    
    def get_rules(self) -> list[Rule]:
        """Return the rules in this template."""
        return self.rules.copy()
    
    def __repr__(self) -> str:
        return f"Template({self.name} v{self.version}, {len(self.rules)} rules)"


class TemplateRegistry:
    """
    Central registry for expectation templates.
    
    Templates are registered globally and can be retrieved by name.
    This prevents contract drift by ensuring consistent definitions.
    
    Usage:
        registry = TemplateRegistry()
        registry.register(template)
        rules = registry.get("template-name")
    """
    
    def __init__(self):
        self._templates: dict[str, ExpectationTemplate] = {}
    
    def register(self, template: ExpectationTemplate) -> "TemplateRegistry":
        """
        Register a template.
        
        Args:
            template: The template to register
            
        Raises:
            ValueError: If template with same name already exists
        """
        if template.name in self._templates:
            raise ValueError(
                f"Template '{template.name}' already registered. "
                "Use override=True to replace."
            )
        self._templates[template.name] = template
        return self
    
    def register_or_update(self, template: ExpectationTemplate) -> "TemplateRegistry":
        """
        Register a template, replacing if it already exists.
        
        Use sparingly - prefer explicit versioning.
        """
        self._templates[template.name] = template
        return self
    
    def get(self, name: str) -> ExpectationTemplate:
        """
        Get a template by name.
        
        Args:
            name: The template name
            
        Returns:
            The registered template
            
        Raises:
            KeyError: If template not found
        """
        if name not in self._templates:
            raise KeyError(
                f"Template '{name}' not found. "
                f"Available: {list(self._templates.keys())}"
            )
        return self._templates[name]
    
    def get_rules(self, name: str) -> list[Rule]:
        """
        Get rules from a template by name.
        
        Convenience method for getting rules directly.
        """
        return self.get(name).get_rules()
    
    def exists(self, name: str) -> bool:
        """Check if a template exists."""
        return name in self._templates
    
    def list_templates(self) -> list[str]:
        """List all registered template names."""
        return list(self._templates.keys())
    
    def clear(self) -> None:
        """Clear all templates. Use for testing only."""
        self._templates.clear()


# Global registry instance
_global_registry = TemplateRegistry()


def get_registry() -> TemplateRegistry:
    """Get the global template registry."""
    return _global_registry


def register_template(template: ExpectationTemplate) -> None:
    """Register a template in the global registry."""
    _global_registry.register(template)


def get_template(name: str) -> ExpectationTemplate:
    """Get a template from the global registry."""
    return _global_registry.get(name)


def get_template_rules(name: str) -> list[Rule]:
    """Get rules from a template in the global registry."""
    return _global_registry.get_rules(name)


# --- Built-in Templates ---

# Safe response template - blocks harmful content
SAFE_RESPONSE_TEMPLATE = ExpectationTemplate(
    name="safe-response",
    description="Blocks responses containing apologies, errors, or harmful content",
    rules=[
        MustNotIncludeRule(["sorry", "apologize", "cannot", "I'm unable"]),
        MustNotIncludeRule(["error", "exception", "failed"]),
    ],
    version="1.0.0",
)

# Latency SLA templates
LATENCY_FAST_TEMPLATE = ExpectationTemplate(
    name="latency-fast",
    description="Strict latency for fast operations (< 1s)",
    rules=[MaxLatencyRule(1000)],
    version="1.0.0",
)

LATENCY_STANDARD_TEMPLATE = ExpectationTemplate(
    name="latency-standard",
    description="Standard latency for typical operations (< 3s)",
    rules=[MaxLatencyRule(3000)],
    version="1.0.0",
)

LATENCY_SLOW_TEMPLATE = ExpectationTemplate(
    name="latency-slow",
    description="Relaxed latency for complex operations (< 10s)",
    rules=[MaxLatencyRule(10000)],
    version="1.0.0",
)

# Quality templates
MINIMUM_RESPONSE_TEMPLATE = ExpectationTemplate(
    name="minimum-response",
    description="Ensures response is not too short",
    rules=[MinTokensRule(10)],
    version="1.0.0",
)

DETAILED_RESPONSE_TEMPLATE = ExpectationTemplate(
    name="detailed-response",
    description="Ensures response has substantial content",
    rules=[MinTokensRule(50)],
    version="1.0.0",
)


def register_builtin_templates() -> None:
    """Register all built-in templates in the global registry."""
    templates = [
        SAFE_RESPONSE_TEMPLATE,
        LATENCY_FAST_TEMPLATE,
        LATENCY_STANDARD_TEMPLATE,
        LATENCY_SLOW_TEMPLATE,
        MINIMUM_RESPONSE_TEMPLATE,
        DETAILED_RESPONSE_TEMPLATE,
    ]
    for template in templates:
        if not _global_registry.exists(template.name):
            _global_registry.register(template)


# Auto-register built-in templates on import
register_builtin_templates()
