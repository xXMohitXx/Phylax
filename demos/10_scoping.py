"""
Demo 10: Axis 1 - Expectation Scoping

Shows how to scope expectations to specific nodes, providers, stages, or tools.
Scoped expectations only apply when context matches.
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

from phylax.expectations import (
    Evaluator,
    MustIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    for_node,
    for_provider,
    for_stage,
    for_tool,
)

print("=" * 60)
print("DEMO 10: Expectation Scoping & Targeting")
print("=" * 60)

# --- Example 1: Node-Scoped Expectation ---
print("\n--- Example 1: Node-Scoped Expectation ---")
print("Expectation only applies to specific node.")

evaluator = Evaluator()
evaluator.set_context({"node_id": "summarizer-node"})
evaluator.scoped_for(
    for_node("summarizer-node"),
    MinTokensRule(20)  # Summaries must be at least 20 tokens
)

verdict = evaluator.evaluate(
    "This is a comprehensive summary of the document covering all key points and conclusions.",
    latency_ms=100
)
print(f"  Node: summarizer-node")
print(f"  Result: {verdict.status.upper()}")

# Different node - expectation not applied
evaluator2 = Evaluator()
evaluator2.set_context({"node_id": "other-node"})
evaluator2.scoped_for(
    for_node("summarizer-node"),
    MinTokensRule(20)
)

verdict = evaluator2.evaluate("short", latency_ms=100)
print(f"  Node: other-node (different)")
print(f"  Result: {verdict.status.upper()} (scoped expectation inactive)")

# --- Example 2: Provider-Scoped Latency ---
print("\n--- Example 2: Provider-Scoped Latency ---")
print("Different latency thresholds for different providers.")

evaluator3 = Evaluator()
evaluator3.set_context({"provider": "openai"})

# OpenAI should be fast
evaluator3.scoped_for(for_provider("openai"), MaxLatencyRule(2000))
# Anthropic can be slower
evaluator3.scoped_for(for_provider("anthropic"), MaxLatencyRule(5000))

verdict = evaluator3.evaluate("response", latency_ms=3000)
print(f"  Provider: openai, Latency: 3000ms")
print(f"  Result: {verdict.status.upper()} (exceeds 2000ms for OpenAI)")

evaluator4 = Evaluator()
evaluator4.set_context({"provider": "anthropic"})
evaluator4.scoped_for(for_provider("openai"), MaxLatencyRule(2000))
evaluator4.scoped_for(for_provider("anthropic"), MaxLatencyRule(5000))

verdict = evaluator4.evaluate("response", latency_ms=3000)
print(f"  Provider: anthropic, Latency: 3000ms")
print(f"  Result: {verdict.status.upper()} (under 5000ms for Anthropic)")

# --- Example 3: Stage-Scoped Expectation ---
print("\n--- Example 3: Stage-Scoped Expectation ---")
print("Different rules for different pipeline stages.")

evaluator5 = Evaluator()
evaluator5.set_context({"stage": "final"})

# Final stage must have certain content
evaluator5.scoped_for(
    for_stage("final"),
    MustIncludeRule(["conclusion", "summary"])
)

verdict = evaluator5.evaluate(
    "In conclusion, here is the summary of our findings.",
    latency_ms=100
)
print(f"  Stage: final")
print(f"  Result: {verdict.status.upper()}")

# --- Example 4: Tool-Scoped Expectation ---
print("\n--- Example 4: Tool-Scoped Expectation ---")
print("Rules specific to tool calls.")

evaluator6 = Evaluator()
evaluator6.set_context({"tool": "search"})

# Search tool responses must include citation
evaluator6.scoped_for(
    for_tool("search"),
    MustIncludeRule(["source", "reference"])
)

verdict = evaluator6.evaluate(
    "According to our source, the reference indicates...",
    latency_ms=100
)
print(f"  Tool: search")
print(f"  Result: {verdict.status.upper()}")

# --- Example 5: Global vs Scoped ---
print("\n--- Example 5: Global vs Scoped ---")
print("Global expectations always apply; scoped only when matching.")

evaluator7 = Evaluator()
evaluator7.set_context({"node_id": "any-node"})

# Global: always applies
evaluator7.must_not_include(["error", "exception"])

# Scoped: only for specific node
evaluator7.scoped_for(
    for_node("critical-node"),
    MaxLatencyRule(500)
)

verdict = evaluator7.evaluate("operation successful", latency_ms=1000)
print(f"  Node: any-node")
print(f"  Result: {verdict.status.upper()}")
print(f"  (Global rule passes, scoped rule not applied)")

print("\n" + "=" * 60)
print("Key Point: Scopes are EXPLICIT and STATIC.")
print("No pattern matching, no wildcards, no dynamic resolution.")
print("=" * 60)
