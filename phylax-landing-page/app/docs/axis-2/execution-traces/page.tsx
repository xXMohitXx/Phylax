import React from 'react';
import { CodeBlock } from '@/components/code-block';

const TRACE_FLOW_CODE = `from phylax import (
    SurfaceEvaluator,
    StepCountRule,
    RequiredStageRule,
    ForbiddenTransitionRule,
    ExecutionTraceSurfaceAdapter,
)

evaluator = SurfaceEvaluator()

# Prevent infinite agent loops — must complete in 10 steps or fewer
evaluator.add_rule(StepCountRule("<=", 10))

# The PII scrubber stage must always run
evaluator.add_rule(RequiredStageRule("pii_scrub"))

# Cannot jump directly from init to output (compliance bypass)
evaluator.add_rule(ForbiddenTransitionRule("init", "output"))

adapter = ExecutionTraceSurfaceAdapter()
surface = adapter.adapt([
    {"stage": "init",     "type": "setup",    "metadata": {}},
    {"stage": "pii_scrub","type": "check",    "metadata": {}},
    {"stage": "output",   "type": "response", "metadata": {}},
])

verdict = evaluator.evaluate(surface)
print(verdict.passed)  # True — pii_scrub was present, no illegal jumps`;

export default function ExecutionTracesPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Execution Traces</h1>
            <p className="text-xl text-coffee-bean/80">
                Assert the valid causality chain and state transitions of multi-step agents.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">State Machine Boundaries</h2>
            <p className="text-coffee-bean/80 mb-4">
                In complex agents (LangGraph, AutoGen, etc.), errors occur when an agent jumps from Step A directly to Step D, skipping critical intermediate validations. Phylax lets you codify the legal execution trace paths.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong><code>StepCountRule(operator, value)</code></strong> — Assert the total number of operations (e.g. prevent infinite agent loops).</li>
                    <li><strong><code>RequiredStageRule(stage_name)</code></strong> — Ensure a mandatory stage (like <code>&quot;compliance_check&quot;</code>) was not bypassed.</li>
                    <li><strong><code>ForbiddenTransitionRule(stage_a, stage_b)</code></strong> — Prohibit specific consecutive stage jumps.</li>
                </ul>
            </div>

            <CodeBlock language="python" title="workflow_enforcement.py" code={TRACE_FLOW_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Deterministic Verification</h2>
            <p className="text-coffee-bean/80 mb-4">
                Execution flow is matched case-sensitively. <code>&quot;PII_Scrub&quot;</code> is fundamentally different from <code>&quot;pii_scrub&quot;</code> — no semantic similarity is applied.
            </p>
        </div>
    );
}
