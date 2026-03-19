# RAG Enforcement

Retrieval-Augmented Generation relies strictly on the underlying documents provided to the model. Phylax provides strict validation bounds for these context windows via the `phylax.rag` integration.

## Key Rules

### 1. ContextUsedRule

Ensures that the LLM's answer was significantly dependent on the provided reference context, rather than its pre-trained weights.

### 2. NoHallucinationRule

Cross-references the generated answer with the provided retriever chunks to guarantee zero net-new factual statements are introduced.

### 3. CitationRequiredRule

Forces the model to append inline citations (e.g. `[1]`, `[Source A]`) mapping to the actual document index.

## Example Evaluation

```python
from phylax.rag import evaluate_rag

result = evaluate_rag(
    question="What is the stock price of ACME?",
    context="ACME is currently trading at $150.",
    answer="ACME is at $150. [1]",
    rules=["context_used", "no_hallucination", "citation_required"]
)

if not result.passed:
    print(f"RAG Hallucination Blocked: {result.violations}")
```
