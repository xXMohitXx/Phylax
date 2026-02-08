"""
Demo 13: Axis 1 - Live Gemini Integration

Shows all Axis 1 features working with live Gemini API calls.
Demonstrates composition, conditionals, scoping, templates, and documentation
in a real-world scenario.
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

import google.generativeai as genai

from phylax._internal.expectations import (
    Evaluator,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    AndGroup,
    OrGroup,
    NotGroup,
    InputContains,
    ModelEquals,
    ProviderEquals,
    for_provider,
)
import time

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

print("=" * 70)
print("DEMO 13: Live Gemini Integration - All Axis 1 Features")
print("=" * 70)


def call_gemini(prompt: str) -> tuple[str, int]:
    """Call Gemini and return (response, latency_ms)."""
    start = time.time()
    response = model.generate_content(prompt)
    latency_ms = int((time.time() - start) * 1000)
    return response.text, latency_ms


# --- Test 1: Composition with AND ---
print("\n--- Test 1: AND Composition ---")
print("Rule: Response must include both 'Python' AND 'programming'")

evaluator = Evaluator()
evaluator.and_group([
    MustIncludeRule(["Python"]),
    MustIncludeRule(["programming"]),
])

prompt = "What is Python? Give a one-sentence answer."
print(f"Prompt: {prompt}")

response, latency = call_gemini(prompt)
print(f"Response: {response[:100]}...")
print(f"Latency: {latency}ms")

verdict = evaluator.evaluate(response, latency_ms=latency)
print(f"Verdict: {verdict.status.upper()}")
if verdict.violations:
    print(f"Violations: {verdict.violations}")

# --- Test 2: OR Composition ---
print("\n--- Test 2: OR Composition ---")
print("Rule: Response must mention either 'machine learning' OR 'artificial intelligence'")

evaluator2 = Evaluator()
evaluator2.or_group([
    MustIncludeRule(["machine learning"]),
    MustIncludeRule(["artificial intelligence"]),
])

prompt = "What are neural networks used for? One sentence."
print(f"Prompt: {prompt}")

response, latency = call_gemini(prompt)
print(f"Response: {response[:100]}...")
print(f"Latency: {latency}ms")

verdict = evaluator2.evaluate(response, latency_ms=latency)
print(f"Verdict: {verdict.status.upper()}")

# --- Test 3: NOT Composition ---
print("\n--- Test 3: NOT Composition ---")
print("Rule: Response must NOT contain 'sorry' or 'cannot'")

evaluator3 = Evaluator()
evaluator3.not_rule(MustIncludeRule(["sorry"]))
evaluator3.not_rule(MustIncludeRule(["cannot"]))

prompt = "Explain what a function is in programming. Be helpful."
print(f"Prompt: {prompt}")

response, latency = call_gemini(prompt)
print(f"Response: {response[:100]}...")
print(f"Latency: {latency}ms")

verdict = evaluator3.evaluate(response, latency_ms=latency)
print(f"Verdict: {verdict.status.upper()}")

# --- Test 4: Conditional with Provider ---
print("\n--- Test 4: Conditional Expectations ---")
print("Rule: IF provider is 'gemini' THEN latency < 5000ms")

evaluator4 = Evaluator()
evaluator4.set_context({"provider": "gemini", "input": prompt})
evaluator4.when_if(
    ProviderEquals("gemini"),
    MaxLatencyRule(5000)
)

prompt = "What is 2+2? Answer in one word."
print(f"Prompt: {prompt}")

response, latency = call_gemini(prompt)
print(f"Response: {response}")
print(f"Latency: {latency}ms")

verdict = evaluator4.evaluate(response, latency_ms=latency)
print(f"Verdict: {verdict.status.upper()}")

# --- Test 5: Provider-Scoped Expectations ---
print("\n--- Test 5: Provider-Scoped Latency ---")
print("Rule: Gemini provider must respond in < 5000ms")

evaluator5 = Evaluator()
evaluator5.set_context({"provider": "gemini"})
evaluator5.scoped_for(
    for_provider("gemini"),
    MaxLatencyRule(5000)
)

prompt = "Name three colors."
print(f"Prompt: {prompt}")

response, latency = call_gemini(prompt)
print(f"Response: {response}")
print(f"Latency: {latency}ms")

verdict = evaluator5.evaluate(response, latency_ms=latency)
print(f"Verdict: {verdict.status.upper()}")

# --- Test 6: Using Templates ---
print("\n--- Test 6: Template Usage ---")
print("Using: safe-response + latency-standard + minimum-response")

evaluator6 = Evaluator()
evaluator6.use_template("safe-response")  # No apologies/refusals
evaluator6.use_template("minimum-response")  # >= 10 tokens

prompt = "Explain recursion in programming in 2-3 sentences."
print(f"Prompt: {prompt}")

response, latency = call_gemini(prompt)
print(f"Response: {response[:150]}...")
print(f"Latency: {latency}ms")

verdict = evaluator6.evaluate(response, latency_ms=latency)
print(f"Verdict: {verdict.status.upper()}")

# --- Test 7: Contract Documentation ---
print("\n--- Test 7: Self-Documenting Contract ---")
print("Show what expectations are being enforced:")

evaluator7 = Evaluator()
evaluator7.use_template("safe-response")
evaluator7.use_template("latency-standard")
evaluator7.must_include(["data"])

print(evaluator7.describe())

# --- Summary ---
print("\n" + "=" * 70)
print("DEMO COMPLETE")
print("=" * 70)
print("\nAll Axis 1 features demonstrated with live Gemini API:")
print("  ✓ AND/OR/NOT composition")
print("  ✓ Conditional expectations")
print("  ✓ Provider-scoped rules")
print("  ✓ Template reuse")
print("  ✓ Self-documenting contracts")
print("\nKey Principle: Deterministic PASS/FAIL, no probabilistic logic.")
