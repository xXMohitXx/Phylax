"""
Demo 11: Axis 1 - Expectation Templates

Shows how to use reusable templates for consistent contracts.
Templates are static macros - no adaptive or context-dependent behavior.
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

from phylax.expectations import (
    Evaluator,
    MustIncludeRule,
    MaxLatencyRule,
    ExpectationTemplate,
    TemplateRegistry,
    get_registry,
    get_template,
    get_template_rules,
)

print("=" * 60)
print("DEMO 11: Expectation Templates & Reuse")
print("=" * 60)

# --- Example 1: Built-in Templates ---
print("\n--- Example 1: Built-in Templates ---")
print("Phylax comes with pre-defined templates.")

registry = get_registry()
print(f"  Available templates: {registry.list_templates()}")

# --- Example 2: Using latency-standard Template ---
print("\n--- Example 2: Using latency-standard Template ---")
print("Apply consistent latency requirements.")

evaluator = Evaluator()
evaluator.use_template("latency-standard")  # 3000ms threshold

verdict = evaluator.evaluate("response", latency_ms=2000)
print(f"  Template: latency-standard (3000ms)")
print(f"  Latency: 2000ms → {verdict.status.upper()}")

verdict = evaluator.evaluate("response", latency_ms=4000)
print(f"  Latency: 4000ms → {verdict.status.upper()}")

# --- Example 3: safe-response Template ---
print("\n--- Example 3: safe-response Template ---")
print("Blocks common refusal patterns.")

evaluator2 = Evaluator()
evaluator2.use_template("safe-response")

verdict = evaluator2.evaluate("Here's the information you requested.", latency_ms=100)
print(f"  Response: 'Here's the information...'")
print(f"  Result: {verdict.status.upper()}")

verdict = evaluator2.evaluate("Sorry, I cannot help with that.", latency_ms=100)
print(f"  Response: 'Sorry, I cannot help...'")
print(f"  Result: {verdict.status.upper()}")

# --- Example 4: Combining Templates ---
print("\n--- Example 4: Combining Templates ---")
print("Apply multiple templates to one evaluator.")

evaluator3 = Evaluator()
evaluator3.use_template("safe-response")
evaluator3.use_template("latency-fast")  # 1000ms
evaluator3.use_template("minimum-response")  # 10 tokens

verdict = evaluator3.evaluate(
    "Here is a helpful response with enough detail to be useful.",
    latency_ms=500
)
print(f"  Templates: safe-response + latency-fast + minimum-response")
print(f"  Result: {verdict.status.upper()}")

# --- Example 5: Template + Custom Rules ---
print("\n--- Example 5: Template + Custom Rules ---")
print("Combine templates with additional custom rules.")

evaluator4 = Evaluator()
evaluator4.use_template("latency-standard")
evaluator4.must_include(["confirmed"])  # Custom rule

verdict = evaluator4.evaluate("Your request is confirmed.", latency_ms=2000)
print(f"  Template: latency-standard")
print(f"  Custom rule: must include 'confirmed'")
print(f"  Result: {verdict.status.upper()}")

# --- Example 6: Creating Custom Templates ---
print("\n--- Example 6: Creating Custom Templates ---")
print("Define your own reusable templates.")

# Create custom template
custom_template = ExpectationTemplate(
    name="api-response",
    description="Standard API response requirements",
    rules=[
        MaxLatencyRule(1500),
        MustIncludeRule(["data", "status"]),
    ],
    version="1.0.0",
)

print(f"  Custom template: {custom_template.name}")
print(f"  Rules: {len(custom_template.get_rules())}")

# Register and use (would typically do this once at startup)
# registry.register(custom_template)

# Apply rules manually
evaluator5 = Evaluator()
for rule in custom_template.get_rules():
    evaluator5.add_rule(rule)

verdict = evaluator5.evaluate(
    '{"data": {...}, "status": "success"}',
    latency_ms=1000
)
print(f"  Result: {verdict.status.upper()}")

print("\n" + "=" * 60)
print("Key Point: Templates are STATIC MACROS.")
print("Same rules every time. No context adaptation.")
print("=" * 60)
