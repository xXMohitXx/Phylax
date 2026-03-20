import React from 'react';
import { CodeBlock } from '@/components/code-block';

const RAG_CODE = `from phylax.rag import (
    ContextUsedRule,
    NoHallucinationRule,
    CitationRequiredRule,
    evaluate_rag,
)

context_chunks = "Refunds are processed within 30 days. Email support@company.com for help."
response = "Refunds take 30 days. Email support@company.com."

# Rule 1: Response must use at least 2 terms from the context
context_rule = ContextUsedRule(min_overlap_terms=2)

# Rule 2: No hallucinated facts — forbidden claims that aren't in context
hallucination_rule = NoHallucinationRule(forbidden_claims=["instant refund", "guaranteed"])

# Rule 3: Response must include bracketed citations
citation_rule = CitationRequiredRule(min_citations=1)

# evaluate_rag(response, context, rules=[...])
results = evaluate_rag(response, context_chunks, rules=[
    context_rule,
    hallucination_rule,
    citation_rule,
])

for r in results:
    print(r.rule_name, "->", "PASS" if r.passed else "FAIL")`;

const SIMPLE_CODE = `from phylax.rag import evaluate_rag

context = "GDPR is a European regulation about data privacy protection"
response = "According to GDPR, the European regulation ensures data privacy protection [1]."

# Default rules: ContextUsedRule + CitationRequiredRule
results = evaluate_rag(response, context)
print(all(r.passed for r in results))  # True`;

export default function RagEnforcementPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">RAG Enforcement</h1>
            <p className="text-xl text-coffee-bean/80">
                Deterministically enforce that RAG responses use their context, avoid hallucinations, and include citations.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">RAG-Specific Rules</h2>
            <p className="text-coffee-bean/80 mb-4">
                Import from <code>phylax.rag</code> — the dedicated RAG submodule. All three rules are fully deterministic; no embedding models or LLM judges are used.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong><code>ContextUsedRule(min_overlap_terms=N)</code></strong> — Checks that the response uses at least N terms from the context via exact, case-insensitive substring matching.</li>
                    <li><strong><code>NoHallucinationRule(forbidden_claims=[...])</code></strong> — Fails if any claim in the <code>forbidden_claims</code> list appears in the response.</li>
                    <li><strong><code>CitationRequiredRule(min_citations=1)</code></strong> — Checks that at least one citation marker (<code>[1]</code>, &quot;According to&quot;, &quot;Source:&quot;, etc.) appears in the response.</li>
                </ul>
            </div>

            <CodeBlock language="python" title="rag_enforcement.py" code={RAG_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Simple Usage</h2>
            <p className="text-coffee-bean/80 mb-4">
                Call <code>evaluate_rag(response, context)</code> with no custom rules to run the default <code>ContextUsedRule</code> + <code>CitationRequiredRule</code> combination.
            </p>
            <CodeBlock language="python" title="simple_rag.py" code={SIMPLE_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">No Embedding Models Required</h3>
                <p className="text-coffee-bean/80">
                    Unlike semantic similarity approaches, Phylax RAG enforcement runs completely offline. No API calls, no embeddings, no LLM judges — guaranteed to produce the same verdict every time CI runs.
                </p>
            </div>
        </div>
    );
}
