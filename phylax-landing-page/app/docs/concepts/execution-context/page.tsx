import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CONTEXT_CODE = `from phylax import trace, expect, execution, OpenAIAdapter

@trace(provider="openai")
@expect(must_include=["intent"])
def classify(message: str):
    adapter = OpenAIAdapter()
    response, _ = adapter.generate(prompt=f"Classify: {message}")
    return response

@trace(provider="openai")
@expect(must_not_include=["internal_db_error"])
def process_data(classification: str):
    adapter = OpenAIAdapter()
    response, _ = adapter.generate(prompt=classification)
    return response

# Group both traces in a single execution context
with execution() as exec_id:
    print(f"Tracing session: {exec_id}")

    # Step 1 — produces a ROOT trace
    intent = classify("I want to login")

    # Step 2 — produces a CHILD trace under the same exec_id
    response = process_data(intent)`;

const NESTED_CODE = `@trace(provider="openai")
def agent(query: str):
    # This call is tracked as the ROOT node

    # Step 1: tool call — tracked as a CHILD node
    data = fetch_db()

    # Step 2: inner LLM call — tracked as a LEAF node
    response = format_response(query, data)
    return response`;

export default function ExecutionContextPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Execution Context</h1>
            <p className="text-xl text-coffee-bean/80">
                Group multiple LLM calls together to trace complex agent workflows as a single logical execution unit.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The Context Manager</h2>
            <p className="text-coffee-bean/80 mb-4">
                Real applications rarely ship a solitary LLM call. Classifiers, tool callers, and final responders all need to be linked.
                Use the <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">execution()</code> context manager to group traces into a single session.
            </p>

            <CodeBlock language="python" title="multi_step.py" code={CONTEXT_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Parent-Child Relationships</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax automatically associates nested traces when functions call each other, constructing an execution hierarchy implicitly.
            </p>

            <CodeBlock language="python" title="nested.py" highlightedLines={[9, 10]} code={NESTED_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Important Constraints</h3>
                <ul className="space-y-2 text-coffee-bean/80">
                    <li><strong>Empty Contexts:</strong> An <code>execution()</code> block that produces zero traces triggers a <code>PHYLAX_E102</code> fatal error.</li>
                    <li><strong>Async Support:</strong> Phylax contexts are context-var aware and track executions across <code>async/await</code> boundaries cleanly.</li>
                </ul>
            </div>
        </div>
    );
}
