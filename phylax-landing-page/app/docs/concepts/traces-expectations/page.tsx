import React from 'react';
import { CodeBlock } from '@/components/code-block';

const TRACE_CODE = `from phylax import trace, OpenAIAdapter

@trace(provider="openai")
def simple_llm_call(prompt: str):
    adapter = OpenAIAdapter()
    response, trace_obj = adapter.generate(prompt=prompt, model="gpt-4o")

    # Trace contains all diagnostic info
    print(trace_obj.latency_ms)
    print(trace_obj.id)
    return response`;

const EXPECT_CODE = `from phylax import trace, expect

@trace(provider="openai")
@expect(must_include=["refund", "30 days"], max_latency_ms=2000, min_tokens=50)
def handle_customer_inquiry(message: str):
    ...`;

export default function TracesExpectationsPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Traces & Expectations</h1>
            <p className="text-xl text-coffee-bean/80">
                The fundamental building blocks of Phylax: recording behavior and evaluating it deterministically.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Traces: The Observer</h2>
            <p className="text-coffee-bean/80 mb-4">
                The <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">@trace</code> decorator watches your LLM calls and records them immutably. It captures the request parameters, prompt, response latency, token usage, and fully formed outputs.
            </p>

            <CodeBlock language="python" title="trace_example.py" code={TRACE_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Expectations: The Judge</h2>
            <p className="text-coffee-bean/80 mb-4">
                The <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">@expect</code> decorator applies rigorous rules to the captured trace. Phylax evaluates these rules deterministically. There is no fuzziness.
            </p>

            <CodeBlock language="python" title="expect_example.py" code={EXPECT_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Basic Rules</h3>
                <ul className="space-y-2 text-coffee-bean/80">
                    <li><strong>must_include:</strong> <code>List[str]</code> — The output must contain all these exact substrings.</li>
                    <li><strong>must_not_include:</strong> <code>List[str]</code> — The output must NOT contain any of these substrings.</li>
                    <li><strong>max_latency_ms:</strong> <code>int</code> — Hard ceiling on API response time in milliseconds.</li>
                    <li><strong>min_tokens:</strong> <code>int</code> — Hard floor on response length in tokens.</li>
                </ul>
            </div>

            <h2 className="text-2xl font-semibold text-coffee-bean mt-6 mb-4">The Trust Contract</h2>
            <ul className="list-disc ml-6 mt-2 text-coffee-bean/80 space-y-2">
                <li><strong>Traces are immutable:</strong> Never modified after creation.</li>
                <li><strong>Verdicts are deterministic:</strong> The exact same input yields the exact same evaluation outcome.</li>
                <li><strong>No AI judgment:</strong> Evaluation rules execute standard algorithmic checks — only exact matches trigger results.</li>
            </ul>

            <a href="/docs/concepts/execution-context" className="inline-block mt-6 px-4 py-2 bg-coffee-bean text-lime-cream rounded-md font-medium w-max hover:bg-coffee-bean/90 transition-colors">
                Read: Execution Context →
            </a>
        </div>
    );
}
