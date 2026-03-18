import React from 'react';
import Link from 'next/link';
import { CodeBlock } from '@/components/code-block';
import { Footer } from '@/components/Footer';

export default function RagPipelineExample() {
    return (
        <>
            <div className="max-w-5xl mx-auto px-6 py-16">
                <Link href="/examples" className="text-sm font-medium text-coffee-bean/60 hover:text-lime-cream mb-8 inline-block">
                    &larr; Back to Examples
                </Link>

                <div className="mb-12">
                    <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-coffee-bean mb-4">
                        RAG Pipeline Validation
                    </h1>
                    <p className="text-lg text-coffee-bean/70">
                        Enforce that generated answers use retrieved context, don&apos;t hallucinate, and include proper citations — all with deterministic rules, no LLM judges.
                    </p>
                </div>

                <div className="grid lg:grid-cols-2 gap-12 items-start">

                    <div className="space-y-8">
                        <div>
                            <h3 className="text-xl font-bold text-coffee-bean mb-2">1. Define Context-Aware Rules</h3>
                            <p className="text-sm text-coffee-bean/70">
                                Phylax provides three RAG-specific rules that validate responses against the retrieved context.
                                <strong> ContextUsedRule</strong> checks that the response references terms from the context.
                                <strong> NoHallucinationRule</strong> blocks specific claims that contradict the source.
                                <strong> CitationRequiredRule</strong> ensures citations appear in the output.
                            </p>
                        </div>

                        <div>
                            <h3 className="text-xl font-bold text-coffee-bean mb-2">2. Write the Dataset Contract</h3>
                            <p className="text-sm text-coffee-bean/70">
                                Each test case includes the input prompt, the retrieved context in metadata,
                                and the expectations. The context field lets you validate grounding without
                                needing a live vector store.
                            </p>
                        </div>

                        <div>
                            <h3 className="text-xl font-bold text-coffee-bean mb-2">3. Run in CI</h3>
                            <p className="text-sm text-coffee-bean/70">
                                Execute <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">phylax dataset run</code> against
                                your RAG handler. Every case produces a PASS or FAIL. No probabilistic scoring — if the response
                                doesn&apos;t use the context or includes forbidden claims, the pipeline exits 1.
                            </p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <CodeBlock
                            title="rag_rules.py"
                            language="python"
                            code={`from phylax.rag import (
    ContextUsedRule,
    NoHallucinationRule,
    CitationRequiredRule,
    evaluate_rag,
)

# Response must use at least 3 terms from context
context_rule = ContextUsedRule(min_overlap_terms=3)

# Response must not claim GDPR is a US law
hallucination_rule = NoHallucinationRule(
    forbidden_claims=["US law", "American regulation"]
)

# Response must include at least 1 citation
citation_rule = CitationRequiredRule(min_citations=1)

# Evaluate all rules at once
results = evaluate_rag(
    response_text=response,
    context=retrieved_context,
    rules=[context_rule, hallucination_rule, citation_rule],
)

for r in results:
    print(f"{r.rule_name}: {'PASS' if r.passed else 'FAIL'}")`}
                        />

                        <CodeBlock
                            title="datasets/rag_pipeline.yaml"
                            language="yaml"
                            code={`dataset: rag_pipeline
cases:
  - input: "What is GDPR?"
    metadata:
      context: "GDPR is a European regulation enacted 
        in 2018 governing data privacy."
    expectations:
      must_include: ["European", "regulation"]
      must_not_include: ["US law", "American"]
      min_tokens: 15

  - input: "When was GDPR enacted?"
    metadata:
      context: "GDPR was enacted on May 25, 2018."
    expectations:
      must_include: ["2018"]
      must_not_include: ["2020", "2015"]`}
                        />

                        <CodeBlock
                            title="Terminal"
                            language="bash"
                            code={`$ phylax dataset run datasets/rag_pipeline.yaml

Running dataset 'rag_pipeline'...
[Case 1/2] "What is GDPR?"
  ✓ must_include: ['European', 'regulation']
  ✓ must_not_include: ['US law', 'American']
  ✓ min_tokens: 15 (actual: 28)
[Case 2/2] "When was GDPR enacted?"
  ✓ must_include: ['2018']
  ✓ must_not_include: ['2020', '2015']

✓ All expectations passed. Exit code 0.`}
                        />
                    </div>

                </div>
            </div>
            <Footer />
        </>
    );
}
