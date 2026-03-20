import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
from phylax import trace, expect, execution
from phylax import for_node, MustIncludeRule, ToolPresenceRule

@trace(provider="openai")
@expect(must_include=["intent"])
def classify(message): ...

@trace(provider="openai")
@expect(must_include=["query"])
def research(intent): ...

@trace(provider="openai")
@expect(must_include=["verified"])
def validate(data): ...

@trace(provider="openai")
@expect(must_include=["response"], max_latency_ms=3000)
def respond(validated_data): ...

# Run as an execution graph
with execution() as exec_id:
    intent = classify("I need help with my order")
    data = research(intent)
    verified = validate(data)
    response = respond(verified)

# DAG: [classify] → [research] → [validate] → [respond]
# If 'research' fails, 'validate' and 'respond' are marked tainted
`;
const CODE_BLOCK_1 = `
from phylax import for_node, for_provider, for_stage

# Only classifier must mention "intent"
classifier_rule = for_node("classify", MustIncludeRule("intent"))

# Only OpenAI nodes have latency limits
openai_latency = for_provider("openai", MaxLatencyRule(2000))

# Validation stage must include "approved"
validation_rule = for_stage("validation", MustIncludeRule("approved"))
`;
const CODE_BLOCK_2 = `
from phylax import ExecutionGraph

graph = ExecutionGraph.from_traces(traces)
verdict = graph.compute_verdict()

if verdict.status == "fail":
    print(f"First failure: {verdict.first_failing_node}")
    print(f"Tainted nodes: {verdict.tainted_count}")

    path = graph.investigation_path()
    for step in path:
        print(f"  → {step}")
`;
const CODE_BLOCK_3 = `
from phylax.agents import (
    ToolSequenceRule,
    ToolPresenceValidator,
    AgentStepValidator,
)

# Enforce tool ordering (relaxed — other tools may interleave)
sequence = ToolSequenceRule(
    required_sequence=["classify", "search", "respond"],
    strict=False,
)

# Enforce which tools must/must-not be called
presence = ToolPresenceValidator(
    must_call=["search"],
    must_not_call=["delete_user", "drop_table"],
)

# Validate agent step structure
steps = AgentStepValidator(
    min_steps=3,
    max_steps=10,
    required_step_types=["planner", "executor"],
)

# Evaluate
tool_calls = [{"tool_name": "classify"}, {"tool_name": "search"}, {"tool_name": "respond"}]
print(sequence.evaluate(tool_calls))  # passed=True
print(presence.evaluate(tool_calls))  # passed=True
`;

export default function AgentTestingPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Agent Workflows</h1>
      <p className="text-xl text-coffee-bean/80">Test multi-step AI agent pipelines with execution graphs, scoped expectations, and first-failure localization.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Why Agent Testing is Hard</h2>
      <p className="text-coffee-bean/80 mb-4">
        When a 5-step agent pipeline produces bad output, which step broke? Phylax&apos;s execution graphs automatically track dependencies and isolate the <em>first failing node</em> in topological order.
      </p>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Full Example</h2>
      <CodeBlock language="python" title="agent_pipeline.py" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Scoped Expectations</h2>
      <p className="text-coffee-bean/80 mb-4">Apply different rules to different nodes in the graph:</p>
      <CodeBlock language="python" title="scoped_rules.py" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Failure Localization</h2>
      <CodeBlock language="python" title="localization.py" code={CODE_BLOCK_2} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Tool Call Enforcement Rules</h2>
      <p className="text-coffee-bean/80 mb-4">
        Phylax provides dedicated rules for validating tool call behavior in agent workflows:
      </p>
      <CodeBlock language="python" title="tool_enforcement.py" code={CODE_BLOCK_3} />
    </div>
  );
}
