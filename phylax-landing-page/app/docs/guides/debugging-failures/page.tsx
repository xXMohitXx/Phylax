import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
$ phylax check
❌ FAIL — trace-abc123
   Violation: must_include("refund_policy")
   Expected: substring "refund_policy" in response
   Actual: "We apologize for the inconvenience..."
   Latency: 1204ms
   Model: gpt-4
`;
const CODE_BLOCK_1 = `
# View full trace details
phylax show <trace_id>

# Or use the Web UI
phylax server
# → http://127.0.0.1:8000/ui
`;
const CODE_BLOCK_2 = `
from phylax import ExecutionGraph

graph = ExecutionGraph.from_traces(traces)
verdict = graph.compute_verdict()

# First-failing-node detection (Evidence Purity)
print(f"First failure: {verdict.first_failing_node}")
print(f"Failed count: {verdict.failed_count}")
print(f"Tainted (downstream): {verdict.tainted_count}")

# Automated investigation path
path = graph.investigation_path()
for step in path:
    print(f"  Investigate: {step}")
`;
const CODE_BLOCK_3 = `
# Diff two executions
GET /v1/executions/{golden_id}/diff/{failing_id}

# Replay the failing trace against the current model
phylax replay <trace_id>
`;

export default function DebuggingFailuresPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Debugging Failures</h1>
      <p className="text-xl text-coffee-bean/80">When Phylax catches a regression, here&apos;s how to diagnose, localize, and fix the problem.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Step 1: Read the Violation</h2>
      <CodeBlock language="bash" title="Terminal Output" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Step 2: Inspect the Trace</h2>
      <CodeBlock language="bash" title="Terminal" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Step 3: Investigate the Graph</h2>
      <p className="text-coffee-bean/80 mb-4">For multi-step agents, use investigation paths to find the root:</p>
      <CodeBlock language="python" title="investigate.py" code={CODE_BLOCK_2} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Step 4: Compare with Golden</h2>
      <CodeBlock language="bash" title="API Endpoints" code={CODE_BLOCK_3} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Common Failure Patterns</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Pattern</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Likely Cause</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Fix</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4">must_include fails</td><td className="py-3 pr-4">Prompt drift or model update</td><td className="py-3">Reinforce prompt, update golden</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4">Latency spike</td><td className="py-3 pr-4">Model overloaded or upgraded</td><td className="py-3">Increase threshold or switch provider</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4">Tool not called</td><td className="py-3 pr-4">Model hallucinated tool name</td><td className="py-3">Constrain tool names in prompt</td></tr>
            <tr><td className="py-3 pr-4">Golden hash mismatch</td><td className="py-3 pr-4">Non-deterministic output changed</td><td className="py-3">Re-bless with new output</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
