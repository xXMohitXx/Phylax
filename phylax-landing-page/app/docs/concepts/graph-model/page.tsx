import React from 'react';
import { CodeBlock } from '@/components/code-block';

const GRAPH_CODE = `from phylax.graph import ExecutionGraph, NodeRole, GraphVerdict

# Retrieve a graph (built automatically from execution context traces)
graph = ExecutionGraph.from_traces(...)

print(f"Total nodes: {graph.node_count}")

# Traverse the graph
for node in graph.nodes:
    if node.role == NodeRole.ROOT:
        print(f"Root trace: {node.trace_id}")

    # Was this specific node the source of a failure?
    if node.verdict_status == "fail":
        print(f"Violation at node: {node.trace_id}")`;

export default function GraphModelPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Graph Model</h1>
            <p className="text-xl text-coffee-bean/80">
                Every execution context forms a Directed Acyclic Graph (DAG) for failure localization and multi-agent assertions.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The Execution Graph</h2>
            <p className="text-coffee-bean/80 mb-4">
                An <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">ExecutionGraph</code> represents the exact causality chain of how an output was created. It contains an array of <code>GraphNode</code>s and <code>GraphEdge</code>s (parent-to-child links).
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <h3 className="text-sm font-semibold text-coffee-bean mb-3 uppercase tracking-wider">Node Roles</h3>
                <ul className="space-y-3 text-coffee-bean/80">
                    <li><strong>ROOT</strong> — The entrypoint trace of the execution context.</li>
                    <li><strong>CHILD</strong> — Intermediate nodes that both receive from a parent and spawn another trace.</li>
                    <li><strong>LEAF</strong> — Final execution nodes that return data without generating sub-traces.</li>
                </ul>
            </div>

            <CodeBlock language="python" title="graph_inspection.py" code={GRAPH_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Graph Verdicts</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax computes an overarching <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">GraphVerdict</code> using topological traversal.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-4 mb-8">
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong>PASS</strong> — All nodes satisfy their individual expectations.</li>
                    <li><strong>FAIL</strong> — One or more nodes explicitly failed an expectation.</li>
                    <li><strong>First Failing Node</strong> — The earliest node in topological sort order to fail. This automatically isolates the root cause — so if an agent formatting step fails, the downstream responder is correctly identified as a consequence, not a cause.</li>
                </ul>
            </div>
        </div>
    );
}
