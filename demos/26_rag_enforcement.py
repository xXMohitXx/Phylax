"""
Demo 26: RAG Enforcement
========================
Demonstrate deterministic validation for retrieval-augmented generation.

Features demonstrated:
    - ContextUsedRule (term overlap detection)
    - NoHallucinationRule (forbidden claim detection)
    - CitationRequiredRule (citation pattern matching)
    - evaluate_rag() (combined pipeline evaluation)
"""
from phylax.rag import (
    ContextUsedRule,
    NoHallucinationRule,
    CitationRequiredRule,
    evaluate_rag,
)

def main():
    print("=" * 60)
    print("Demo 26: RAG Enforcement")
    print("=" * 60)

    context = (
        "Project Phylax is an open-source framework developed in 2026. "
        "It provides deterministic regression enforcement for LLMs."
    )
    
    # 1. Individual Rules
    print("\n--- 1. Individual RAG Rules ---")
    
    # Context Used
    overlap_rule = ContextUsedRule(min_overlap_terms=3)
    good_response = "Phylax provides deterministic regression enforcement for LLMs [1]."
    bad_response = "The weather in Seattle is cloudy today."
    
    res1 = overlap_rule.evaluate(good_response, context)
    print(f"Context used (good response): {'✅ PASS' if res1.passed else '❌ FAIL'}")
    res2 = overlap_rule.evaluate(bad_response, context)
    print(f"Context used (bad response): {'✅ PASS' if res2.passed else '❌ FAIL'}")
    
    # Hallucination Guard
    hallucination_rule = NoHallucinationRule(forbidden_claims=["proprietary", "paid software"])
    res3 = hallucination_rule.evaluate("Phylax is a proprietary software framework.", context)
    print(f"Hallucination check (proprietary claim): {'✅ PASS' if res3.passed else '❌ FAIL'}")
    if not res3.passed:
         print(f"  Violation: {res3.violations[0]}")

    # Citation Required
    citation_rule = CitationRequiredRule(min_citations=1)
    res4 = citation_rule.evaluate(good_response, context)
    print(f"Citation format check: {'✅ PASS' if res4.passed else '❌ FAIL'}")

    # 2. Combined Pipeline Evaluation
    print("\n--- 2. evaluate_rag() Combined Execution ---")
    
    # evaluate_rag runs all standard RAG rules simultaneously
    # It ensures overlap, no common hallucinations, and checks citations.
    responses = evaluate_rag(good_response, context)
    
    print("Aggregated RAG Rule Results for 'good_response':")
    for rule_res in responses:
        print(f"  - {rule_res.__class__.__name__}: {'✅ PASS' if rule_res.passed else '❌ FAIL'}")

if __name__ == "__main__":
    main()
