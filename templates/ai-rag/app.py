"""
AI RAG Template — Retrieval-Augmented Generation with grounding enforcement.

Features:
    - Must-include enforcement for grounding
    - Quality guardrails
    - Dataset contract testing for RAG accuracy

Usage:
    pip install phylax
    python app.py
"""
from phylax import (
    trace, expect, execution,
    Dataset, DatasetCase, run_dataset, format_report,
)
from phylax.guardrails import quality_pack
from phylax.rag import ContextUsedRule, CitationRequiredRule

_quality = quality_pack().to_expectations()


@trace(provider="mock")
@expect(
    must_include=["source"],
    min_tokens=15,
)
def retrieve_and_respond(question: str) -> str:
    """RAG pipeline with grounding enforcement. Must cite source."""
    context = f"According to the documentation about {question}"
    return (
        f"{context}, here is the relevant information. "
        f"The source material indicates several key points "
        f"that address your question comprehensively."
    )


def main():
    print("=== AI RAG with Grounding Enforcement ===\n")

    with execution():
        response = retrieve_and_respond("Python best practices")
        print(f"Response: {response[:80]}...\n")

    ds = Dataset(dataset="rag_accuracy", cases=[
        DatasetCase(
            input="What is machine learning?",
            name="ml_question",
            expectations={"must_include": ["source", "information"], "min_tokens": 10},
        ),
        DatasetCase(
            input="How does Python handle memory?",
            name="python_memory",
            expectations={"must_include": ["source"], "min_tokens": 10},
        ),
    ])

    result = run_dataset(ds, retrieve_and_respond)
    print(format_report(result))


if __name__ == "__main__":
    main()
