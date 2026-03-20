import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
from phylax import trace, expect, execution

@trace(provider="openai")
@expect(must_include=["intent"])
def classify(message): ...

@trace(provider="openai")
@expect(must_include=["data"])
def research(intent): ...

@trace(provider="openai")
@expect(must_include=["answer"])
def respond(data): ...

with execution() as exec_id:
    step1 = classify(message)      # → Node 1
    step2 = research(step1)        # → Node 2
    step3 = respond(step2)         # → Node 3

# Phylax builds a DAG:
#   [classify] → [research] → [respond]
`;
const CODE_BLOCK_1 = `
class GraphVerdict:
    status: "pass" | "fail"
    first_failing_node: str | None  # First failing node in topological order
    failed_count: int               # Total failed nodes
    tainted_count: int              # Nodes downstream of failures
`;
const CODE_BLOCK_2 = `
from phylax import ExecutionGraph

# Build from stored traces
graph = ExecutionGraph.from_traces(traces)

# Get the verdict
verdict = graph.compute_verdict()
print(verdict.first_failing_node)

# Get investigation path (failure localization)
path = graph.investigation_path()

# Create immutable snapshot
snapshot = graph.to_snapshot()

# Diff two executions
from phylax import GraphDiff
diff = GraphDiff.compute(graph_a, graph_b)
`;
const CODE_BLOCK_3 = `
from phylax import NodeRole, GraphStage

# Available node roles
NodeRole.INPUT       # User input
NodeRole.LLM         # LLM call
NodeRole.VALIDATION  # Validation step
NodeRole.TOOL        # Tool/function call
NodeRole.OUTPUT      # Final output

# Graph stages
GraphStage.INGESTION    # Input processing
GraphStage.PROCESSING   # Core logic
GraphStage.VALIDATION   # Quality checks
GraphStage.OUTPUT       # Response generation
`;
const CODE_BLOCK_4 = `
# Start the server
phylax server

# Open http://127.0.0.1:8000/ui
# Navigate to an execution to see its graph
`;
const CODE_BLOCK_5 = `
GET /v1/executions                      # List executions
GET /v1/executions/{id}/graph           # Get DAG
GET /v1/executions/{id}/analysis        # Performance analysis
GET /v1/executions/{a}/diff/{b}         # Compare two executions
GET /v1/executions/{id}/investigate     # Failure localization
GET /v1/executions/{id}/snapshot        # Immutable copy
GET /v1/executions/{id}/verify          # Verify integrity
`;

export default function ExecutionGraphsPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Execution Graphs</h1>
      <p className="text-xl text-coffee-bean/80">
        Execution Graphs model multi-step agent workflows as Directed Acyclic Graphs (DAGs). When a failure cascades through a complex pipeline, Phylax pinpoints the <em>first failing node</em> rather than just the final corrupted output.
      </p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">How It Works</h2>
      <p className="text-coffee-bean/80 mb-4">
        When you wrap calls in an <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">execution()</code> context, Phylax automatically builds a DAG from the call hierarchy:
      </p>
      <CodeBlock language="python" title="execution_graph.py" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Graph Capabilities</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Capability</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Description</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">DAG Visualization</td><td className="py-3">Nodes and edges with hierarchical stages</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Semantic Nodes</td><td className="py-3">Role labels: INPUT, LLM, VALIDATION, TOOL, OUTPUT</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Time Visualization</td><td className="py-3">Latency heatmaps and bottleneck badges</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Failure Focus</td><td className="py-3">First-failure highlighting with evidence purity</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Graph Diffs</td><td className="py-3">Compare two execution runs side-by-side</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Investigation Paths</td><td className="py-3">Automated failure localization steps</td></tr>
            <tr><td className="py-3 pr-4 font-medium">Enterprise</td><td className="py-3">Integrity hashing, snapshots, exports</td></tr>
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Graph Verdict</h2>
      <CodeBlock language="python" title="Graph Verdict Model" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Building &amp; Analyzing Graphs</h2>
      <CodeBlock language="python" title="graph_analysis.py" code={CODE_BLOCK_2} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Node Roles &amp; Stages</h2>
      <CodeBlock language="python" title="Node Configuration" code={CODE_BLOCK_3} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Viewing Graphs</h2>
      <p className="text-coffee-bean/80 mb-4">Use the built-in Web UI or the API:</p>
      <CodeBlock language="bash" title="Terminal" code={CODE_BLOCK_4} />
      <CodeBlock language="bash" title="API Endpoints" code={CODE_BLOCK_5} />
    </div>
  );
}
