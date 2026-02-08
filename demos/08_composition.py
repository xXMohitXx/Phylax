"""
Demo 08: Axis 1 - Expectation Composition

Shows how to combine expectations using AND/OR/NOT logic.
Logical composition evaluates to single PASS/FAIL - no partial verdicts.
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()


from phylax._internal.expectations import (
    Evaluator,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    AndGroup,
    OrGroup,
    NotGroup,
)

print("=" * 60)
print("DEMO 08: Expectation Composition (AND/OR/NOT)")
print("=" * 60)

# --- Example 1: AND Group ---
print("\n--- Example 1: AND Group ---")
print("Both rules must pass for the group to pass.")

evaluator = Evaluator()
evaluator.and_group([
    MustIncludeRule(["hello"]),
    MaxLatencyRule(2000),
])

# Test 1: Both pass
verdict = evaluator.evaluate("hello world", latency_ms=1000)
print(f"  Response 'hello world' @ 1000ms: {verdict.status.upper()}")

# Test 2: One fails
verdict = evaluator.evaluate("hello world", latency_ms=3000)
print(f"  Response 'hello world' @ 3000ms: {verdict.status.upper()}")
print(f"    Violations: {verdict.violations}")

# --- Example 2: OR Group ---
print("\n--- Example 2: OR Group ---")
print("At least one rule must pass for the group to pass.")

evaluator2 = Evaluator()
evaluator2.or_group([
    MustIncludeRule(["refund"]),
    MustIncludeRule(["policy"]),
])

# Test 1: First passes
verdict = evaluator2.evaluate("process your refund", latency_ms=100)
print(f"  Response 'process your refund': {verdict.status.upper()}")

# Test 2: Second passes
verdict = evaluator2.evaluate("see our policy", latency_ms=100)
print(f"  Response 'see our policy': {verdict.status.upper()}")

# Test 3: Both fail
verdict = evaluator2.evaluate("hello there", latency_ms=100)
print(f"  Response 'hello there': {verdict.status.upper()}")

# --- Example 3: NOT Group ---
print("\n--- Example 3: NOT Group ---")
print("The wrapped rule must FAIL for the NOT group to pass.")

evaluator3 = Evaluator()
evaluator3.not_rule(MustIncludeRule(["error"]))

# Test 1: Does not contain "error" → NOT passes
verdict = evaluator3.evaluate("operation successful", latency_ms=100)
print(f"  Response 'operation successful': {verdict.status.upper()}")

# Test 2: Contains "error" → NOT fails
verdict = evaluator3.evaluate("error occurred", latency_ms=100)
print(f"  Response 'error occurred': {verdict.status.upper()}")

# --- Example 4: Nested Composition ---
print("\n--- Example 4: Nested Composition ---")
print("Groups can be nested for complex logic.")

evaluator4 = Evaluator()
evaluator4.and_group([
    # Must be fast
    MaxLatencyRule(2000),
    # AND either mention "confirmed" or "completed"
    OrGroup([
        MustIncludeRule(["confirmed"]),
        MustIncludeRule(["completed"]),
    ]),
    # AND must NOT contain "error"
    NotGroup(MustIncludeRule(["error"])),
])

# Test: All conditions met
verdict = evaluator4.evaluate("your order is confirmed", latency_ms=500)
print(f"  'your order is confirmed' @ 500ms: {verdict.status.upper()}")

# Test: Has error
verdict = evaluator4.evaluate("confirmed but error occurred", latency_ms=500)
print(f"  'confirmed but error occurred' @ 500ms: {verdict.status.upper()}")

print("\n" + "=" * 60)
print("Key Point: All compositions collapse to binary PASS/FAIL")
print("No partial verdicts, no scoring, no weighting.")
print("=" * 60)
