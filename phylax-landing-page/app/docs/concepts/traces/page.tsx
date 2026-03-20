import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
class Trace:
    trace_id: str           # UUID, immutable after creation
    execution_id: str       # Links to execution context
    node_id: str            # Graph node identifier
    parent_node_id: str     # Parent in DAG hierarchy
    timestamp: str          # ISO-8601 timestamp
    request: TraceRequest   # Input (prompt, model, params)
    response: TraceResponse # Output (text, tokens, latency)
    verdict: Verdict | None # PASS/FAIL result
    blessed: bool           # Golden reference flag
`;
const CODE_BLOCK_1 = `
from phylax import trace, expect

@trace(provider="openai")
@expect(must_include=["refund"], max_latency_ms=3000)
def handle_refund(message: str) -> str:
    # Everything inside is recorded:
    # - Input: message parameter
    # - Output: return value
    # - Latency: execution time
    # - Tokens: input + output token count
    return llm(message)
`;
const CODE_BLOCK_2 = `
class Verdict:
    status: "pass" | "fail"           # Only two values, ever
    severity: "low" | "medium" | "high" | None
    violations: list[str]             # List of violated rules
`;
const CODE_BLOCK_3 = `
# Bless a trace as golden
phylax bless <trace_id> --yes

# Force overwrite existing golden
phylax bless <trace_id> --force

# View all golden traces
phylax list --blessed
`;
const CODE_BLOCK_4 = `
# List all traces
phylax list

# List only failed traces
phylax list --failed

# Inspect a specific trace
phylax show <trace_id>

# Replay a trace (re-run against the model)
phylax replay <trace_id>
`;

export default function TracesPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Traces</h1>
      <p className="text-xl text-coffee-bean/80">
        Traces are immutable records of every LLM interaction. They are the atomic unit of Phylax — every expectation, verdict, and graph node is built on top of a trace.
      </p>
      
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">What is a Trace?</h2>
      <p className="text-coffee-bean/80 mb-4">
        A trace captures: the input prompt, the model&apos;s response, execution timing, token counts, the model and provider used, and the verdict (PASS or FAIL). Traces are <strong>never modified after creation</strong> — this immutability is a core invariant.
      </p>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Trace Schema</h2>
      <CodeBlock language="python" title="Trace Model" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Creating Traces</h2>
      <p className="text-coffee-bean/80 mb-4">
        The <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">@trace</code> decorator captures all LLM interactions automatically:
      </p>
      <CodeBlock language="python" title="Decorator Usage" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Verdict Model</h2>
      <p className="text-coffee-bean/80 mb-4">
        Every trace that has expectations produces a binary verdict — exactly two possible outcomes:
      </p>
      <CodeBlock language="python" title="Verdict Schema" code={CODE_BLOCK_2} />

      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-4">
        <p className="text-coffee-bean/90 font-semibold mb-2">Key Invariants:</p>
        <ul className="space-y-2 text-coffee-bean/80 text-sm">
          <li>• Traces are <strong>immutable</strong> — never modified after creation</li>
          <li>• Verdicts are <strong>deterministic</strong> — same input always produces same result</li>
          <li>• Trace IDs are <strong>UUIDs</strong> — globally unique, auto-generated</li>
          <li>• Storage is <strong>local JSON</strong> — no cloud, no external dependencies</li>
        </ul>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Golden Baselines</h2>
      <p className="text-coffee-bean/80 mb-4">
        A trace can be <strong>blessed</strong> as a golden reference. When blessed, its output hash is locked — future <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">phylax check</code> runs compare against this hash.
      </p>
      <CodeBlock language="bash" title="Golden Management" code={CODE_BLOCK_3} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Viewing Traces</h2>
      <CodeBlock language="bash" title="CLI Commands" code={CODE_BLOCK_4} />
    </div>
  );
}
