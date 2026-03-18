import React from 'react';
import Link from 'next/link';
import { CodeBlock } from '@/components/code-block';
import { Footer } from '@/components/Footer';

export default function MultiAgentExample() {
    return (
        <>
            <div className="max-w-5xl mx-auto px-6 py-16">
                <Link href="/examples" className="text-sm font-medium text-coffee-bean/60 hover:text-lime-cream mb-8 inline-block">
                    &larr; Back to Examples
                </Link>

                <div className="mb-12">
                    <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-coffee-bean mb-4">
                        Multi-Agent Workflow Debugging
                    </h1>
                    <p className="text-lg text-coffee-bean/70">
                        Enforce tool call ordering, validate agent execution structure, and pinpoint the first failing node in multi-step agent pipelines.
                    </p>
                </div>

                <div className="grid lg:grid-cols-2 gap-12 items-start">

                    <div className="space-y-8">
                        <div>
                            <h3 className="text-xl font-bold text-coffee-bean mb-2">1. Enforce Tool Call Order</h3>
                            <p className="text-sm text-coffee-bean/70">
                                <strong>ToolSequenceRule</strong> validates that tools are called in the expected order.
                                In <em>relaxed</em> mode, other tools may appear between the required ones.
                                In <em>strict</em> mode, the sequence must be consecutive.
                            </p>
                        </div>

                        <div>
                            <h3 className="text-xl font-bold text-coffee-bean mb-2">2. Validate Tool Presence</h3>
                            <p className="text-sm text-coffee-bean/70">
                                <strong>ToolPresenceValidator</strong> ensures required tools were called and forbidden tools
                                were not. For example, a read-only agent must never call <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">delete_user</code>.
                            </p>
                        </div>

                        <div>
                            <h3 className="text-xl font-bold text-coffee-bean mb-2">3. Detect First Failing Node</h3>
                            <p className="text-sm text-coffee-bean/70">
                                <strong>AgentStepValidator</strong> checks step count, required step types, and reports the
                                exact node that failed first — so you know where to start debugging in a 10-step pipeline.
                            </p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <CodeBlock
                            title="agent_enforcement.py"
                            language="python"
                            code={`from phylax.agents import (
    ToolSequenceRule,
    ToolPresenceValidator,
    AgentStepValidator,
)

# Tools must be called in this order
sequence_rule = ToolSequenceRule(
    required_sequence=["classify", "search", "respond"],
    strict=False,  # other tools may interleave
)

# "delete_user" must never be called
presence_rule = ToolPresenceValidator(
    must_call=["search", "respond"],
    must_not_call=["delete_user", "drop_table"],
)

# Validate execution structure
step_rule = AgentStepValidator(
    min_steps=3,
    max_steps=10,
    required_step_types=["planner", "executor"],
)

# Evaluate against actual tool calls
tool_calls = [
    {"tool_name": "classify"},
    {"tool_name": "search"},
    {"tool_name": "respond"},
]

result = sequence_rule.evaluate(tool_calls)
print(f"Sequence: {'PASS' if result.passed else 'FAIL'}")

result = presence_rule.evaluate(tool_calls)
print(f"Presence: {'PASS' if result.passed else 'FAIL'}")`}
                        />

                        <CodeBlock
                            title="agent_pipeline.py"
                            language="python"
                            code={`from phylax import trace, expect, execution

@trace(provider="openai")
@expect(must_include=["intent"])
def classify(message): ...

@trace(provider="openai")
@expect(must_include=["results"])
def search(intent): ...

@trace(provider="openai")
@expect(must_include=["response"], max_latency_ms=3000)
def respond(data): ...

# Execution graph tracks dependencies
with execution() as exec_id:
    intent = classify("I need help")
    data = search(intent)
    response = respond(data)

# DAG: [classify] → [search] → [respond]
# If search fails → respond is tainted`}
                        />

                        <CodeBlock
                            title="Terminal"
                            language="bash"
                            code={`$ phylax check

Evaluating execution graph...
  [classify]  ✓ PASS (intent found)
  [search]    ✗ FAIL — must_include("results")
  [respond]   ⚠ TAINTED (upstream failure)

First failing node: search
Investigation path: classify → search

❌ 1 node failed. Exit code 1.`}
                        />
                    </div>

                </div>
            </div>
            <Footer />
        </>
    );
}
