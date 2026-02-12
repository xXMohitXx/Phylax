"""Phylax internal expectations module."""

from phylax._internal.expectations.evaluator import evaluate, Evaluator
from phylax._internal.schema import Verdict
from phylax._internal.expectations.rules import (
    Rule,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    RuleResult,
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
    register_template,
    get_template,
    get_template_rules,
)
from phylax._internal.expectations.documentation import (
    describe_rule,
    describe_condition,
    describe_template,
    list_contracts,
    export_contract_markdown,
    ContractDocumenter,
)

__all__ = [
    "evaluate",
    "Evaluator",
    "Rule",
    "MustIncludeRule",
    "MustNotIncludeRule",
    "MaxLatencyRule",
    "MinTokensRule",
    "RuleResult",
    # Axis 1 Phase 1: Expectation Composition
    "ExpectationGroup",
    "AndGroup",
    "OrGroup",
    "NotGroup",
    # Axis 1 Phase 2: Conditional Expectations
    "Condition",
    "ConditionalExpectation",
    "InputContains",
    "ModelEquals",
    "ProviderEquals",
    "MetadataEquals",
    "FlagSet",
    "when",
    # Axis 1 Phase 3: Expectation Scoping
    "ExpectationScope",
    "ScopedExpectation",
    "for_node",
    "for_provider",
    "for_stage",
    "for_tool",
    "scoped",
    # Axis 1 Phase 4: Expectation Templates
    "ExpectationTemplate",
    "TemplateRegistry",
    "get_registry",
    "register_template",
    "get_template",
    "get_template_rules",
    # Axis 1 Phase 5: Expectation Documentation
    "describe_rule",
    "describe_condition",
    "describe_template",
    "list_contracts",
    "export_contract_markdown",
    "ContractDocumenter",
]
