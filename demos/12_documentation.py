"""
Demo 12: Axis 1 - Contract Documentation

Shows how to generate human-readable documentation from contracts.
Self-describing contracts for transparency and auditability.
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

from phylax.expectations import (
    Evaluator,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    AndGroup,
    OrGroup,
    NotGroup,
    InputContains,
    for_provider,
    describe_rule,
    list_contracts,
    export_contract_markdown,
    ContractDocumenter,
    get_template,
)

print("=" * 60)
print("DEMO 12: Contract Documentation & Self-Description")
print("=" * 60)

# --- Example 1: Describe Individual Rules ---
print("\n--- Example 1: Describe Individual Rules ---")
print("Generate human-readable descriptions for each rule type.")

rules = [
    MustIncludeRule(["hello", "world"]),
    MustNotIncludeRule(["error", "fail"]),
    MaxLatencyRule(2000),
    MinTokensRule(10),
]

for rule in rules:
    print(f"  {describe_rule(rule)}")

# --- Example 2: Describe Complex Groups ---
print("\n--- Example 2: Describe Complex Groups ---")
print("Nested groups produce hierarchical descriptions.")

complex_group = AndGroup([
    MaxLatencyRule(3000),
    OrGroup([
        MustIncludeRule(["confirmed"]),
        MustIncludeRule(["completed"]),
    ]),
    NotGroup(MustIncludeRule(["error"])),
])

print(describe_rule(complex_group))

# --- Example 3: Evaluator.describe() ---
print("\n--- Example 3: Evaluator.describe() ---")
print("Get a contract listing from an evaluator.")

evaluator = Evaluator()
evaluator.must_include(["required"])
evaluator.must_not_include(["forbidden"])
evaluator.use_template("latency-standard")

print(evaluator.describe())

# --- Example 4: Markdown Export ---
print("\n--- Example 4: Markdown Export ---")
print("Export contracts as Markdown documentation.")

evaluator2 = Evaluator()
evaluator2.must_include(["response"])
evaluator2.scoped_for(
    for_provider("openai"),
    MaxLatencyRule(2000)
)

markdown = evaluator2.to_markdown(
    title="API Contract",
    description="Requirements for API responses."
)
print(markdown)

# --- Example 5: ContractDocumenter Class ---
print("\n--- Example 5: ContractDocumenter Class ---")
print("Full-featured documenter with multiple output formats.")

evaluator3 = Evaluator()
evaluator3.use_template("safe-response")
evaluator3.use_template("minimum-response")

documenter = ContractDocumenter(evaluator3)

print("Human-readable:")
print(documenter.describe())

print("\nJSON format:")
import json
print(json.dumps(documenter.to_json(), indent=2))

# --- Example 6: Template Documentation ---
print("\n--- Example 6: Template Documentation ---")
print("Describe what a template includes.")

from phylax.expectations import describe_template

template = get_template("safe-response")
print(describe_template(template))

print("\n" + "=" * 60)
print("Key Point: Documentation is GENERATED from declarations.")
print("No inference, no interpretation. What you declare is what you see.")
print("=" * 60)
