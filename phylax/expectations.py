"""
Phylax Expectations - Public API

Clean imports for expectation evaluation, rules, and templates.
"""

from phylax._internal.expectations import (
    # Core evaluator
    Evaluator,
    
    # Rules
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    
    # Composition groups
    AndGroup,
    OrGroup,
    NotGroup,
    
    # Conditions
    InputContains,
    ModelEquals,
    ProviderEquals,
    FlagSet,
    when,
    
    # Scoping
    for_node,
    for_provider,
    for_stage,
    for_tool,
    
    # Templates
    ExpectationTemplate,
    TemplateRegistry,
    get_registry,
    get_template,
    get_template_rules,
    
    # Documentation
    describe_rule,
    describe_template,
    list_contracts,
    export_contract_markdown,
    ContractDocumenter,
)

__all__ = [
    "Evaluator",
    "MustIncludeRule",
    "MustNotIncludeRule",
    "MaxLatencyRule",
    "MinTokensRule",
    "AndGroup",
    "OrGroup",
    "NotGroup",
    "InputContains",
    "ModelEquals",
    "ProviderEquals",
    "FlagSet",
    "when",
    "for_node",
    "for_provider",
    "for_stage",
    "for_tool",
    "ExpectationTemplate",
    "TemplateRegistry",
    "get_registry",
    "get_template",
    "get_template_rules",
    "describe_rule",
    "describe_template",
    "list_contracts",
    "export_contract_markdown",
    "ContractDocumenter",
]
