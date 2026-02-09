"""
Demo 09: Axis 1 - Conditional Expectations

Shows how to create IF/THEN expectations that activate based on context.
Inactive conditions are skipped (no effect on verdict).
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()


from phylax.expectations import (
    Evaluator,
    MustIncludeRule,
    MaxLatencyRule,
    InputContains,
    ModelEquals,
    ProviderEquals,
    FlagSet,
    when,
)

print("=" * 60)
print("DEMO 09: Conditional Expectations (IF/THEN)")
print("=" * 60)

# --- Example 1: Input-Based Condition ---
print("\n--- Example 1: Input-Based Condition ---")
print("IF input contains 'refund' THEN output must contain 'policy'")

evaluator = Evaluator()
evaluator.set_context({"input": "I want a refund"})
evaluator.when_if(
    InputContains("refund"),
    MustIncludeRule(["policy"])
)

verdict = evaluator.evaluate("see our refund policy for details", latency_ms=100)
print(f"  Input: 'I want a refund'")
print(f"  Output: 'see our refund policy for details'")
print(f"  Result: {verdict.status.upper()}")

# --- Example 2: Inactive Condition ---
print("\n--- Example 2: Inactive Condition ---")
print("When condition not met, expectation is skipped.")

evaluator2 = Evaluator()
evaluator2.set_context({"input": "general question"})
evaluator2.when_if(
    InputContains("refund"),
    MustIncludeRule(["policy"])  # Would fail if active
)

verdict = evaluator2.evaluate("hello there", latency_ms=100)
print(f"  Input: 'general question' (no 'refund')")
print(f"  Output: 'hello there' (no 'policy')")
print(f"  Result: {verdict.status.upper()} (condition inactive, skipped)")

# --- Example 3: Model-Based Condition ---
print("\n--- Example 3: Model-Based Condition ---")
print("IF model = 'gpt-4' THEN must be detailed (50+ tokens)")

evaluator3 = Evaluator()
evaluator3.set_context({"model": "gpt-4"})
evaluator3.when_if(
    ModelEquals("gpt-4"),
    MustIncludeRule(["detailed", "explanation"])
)

verdict = evaluator3.evaluate(
    "Here is a detailed explanation of the concept you asked about.",
    latency_ms=100
)
print(f"  Model: gpt-4")
print(f"  Result: {verdict.status.upper()}")

# --- Example 4: Provider-Based Condition ---
print("\n--- Example 4: Provider-Based Condition ---")
print("IF provider = 'openai' THEN latency < 2000ms")

evaluator4 = Evaluator()
evaluator4.set_context({"provider": "openai"})
evaluator4.when_if(
    ProviderEquals("openai"),
    MaxLatencyRule(2000)
)

verdict = evaluator4.evaluate("response text", latency_ms=1500)
print(f"  Provider: openai, Latency: 1500ms")
print(f"  Result: {verdict.status.upper()}")

verdict = evaluator4.evaluate("response text", latency_ms=2500)
print(f"  Provider: openai, Latency: 2500ms")
print(f"  Result: {verdict.status.upper()}")
print(f"    Violations: {verdict.violations}")

# --- Example 5: Flag-Based Condition ---
print("\n--- Example 5: Flag-Based Condition ---")
print("IF 'strict_mode' flag set THEN apply extra rules")

evaluator5 = Evaluator()
evaluator5.set_context({
    "flags": {"strict_mode": True}
})
evaluator5.when_if(
    FlagSet("strict_mode"),
    MustIncludeRule(["verified", "confirmed"])
)

verdict = evaluator5.evaluate("Your request has been verified and confirmed.", latency_ms=100)
print(f"  Strict mode: ON")
print(f"  Result: {verdict.status.upper()}")

print("\n" + "=" * 60)
print("Key Point: Conditions are EXACT matches only.")
print("No regex, no fuzzy matching, no semantic similarity.")
print("=" * 60)
