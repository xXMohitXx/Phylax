import React from 'react';
import { CodeBlock } from '@/components/code-block';

const SCOPING_CODE = `from phylax.expectations import (
    scoped,
    for_node,
    for_provider,
    for_stage,
    for_tool,
    MinTokensRule,
    MaxLatencyRule,
)

# Only applies to the node named "summarizer-node"
scoped(for_node("summarizer-node"), MinTokensRule(20))

# Only applies to OpenAI provider calls
scoped(for_provider("openai"), MaxLatencyRule(2000))

# Only applies to Anthropic provider calls
scoped(for_provider("anthropic"), MaxLatencyRule(5000))

# Only applies to nodes executing the "search_db" tool
scoped(for_tool("search_db"), MaxLatencyRule(1000))`;

export default function ScopingPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Scoping</h1>
            <p className="text-xl text-coffee-bean/80">
                Target rules to specific nodes, providers, tools, or stages in your execution graph.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Scoping Evaluators</h2>
            <p className="text-coffee-bean/80 mb-4">
                When evaluating multiple traces in a multi-agent graph, global expectations apply to all nodes.
                <code className="mx-1 px-1.5 py-0.5 rounded bg-beige">scoped()</code> rules only fire for traces that match the target exactly.
            </p>

            <CodeBlock language="python" title="scoping.py" code={SCOPING_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Global vs. Scoped</h2>
            <p className="text-coffee-bean/80 mb-4">
                Rules passed directly to <code>@expect</code> or a Dataset run against <strong>every trace</strong> in that execution context.
            </p>
            <p className="text-coffee-bean/80 mb-4">
                Using <code>scoped()</code> prevents highly specific checks — like &quot;this JSON parser must return exactly 3 keys&quot; — from incorrectly failing upstream text generation nodes.
            </p>

            <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                    <thead><tr className="border-b border-black/10">
                        <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Scope Function</th>
                        <th className="text-left py-3 font-semibold text-coffee-bean">Targets</th>
                    </tr></thead>
                    <tbody className="text-coffee-bean/80">
                        <tr className="border-b border-black/5"><td className="py-3 pr-4"><code>for_node(name)</code></td><td className="py-3">A specific named node in the execution graph</td></tr>
                        <tr className="border-b border-black/5"><td className="py-3 pr-4"><code>for_provider(name)</code></td><td className="py-3">All traces from a given LLM provider</td></tr>
                        <tr className="border-b border-black/5"><td className="py-3 pr-4"><code>for_stage(name)</code></td><td className="py-3">All traces at a given pipeline stage</td></tr>
                        <tr><td className="py-3 pr-4"><code>for_tool(name)</code></td><td className="py-3">All traces that invoke a specific tool</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
}
