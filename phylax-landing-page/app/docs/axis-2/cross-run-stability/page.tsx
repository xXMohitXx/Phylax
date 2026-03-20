import React from 'react';
import { CodeBlock } from '@/components/code-block';

const STABILITY_CODE = `from phylax import (
    SurfaceEvaluator,
    ExactStabilityRule,
    AllowedDriftRule,
    StabilitySurfaceAdapter,
)

evaluator = SurfaceEvaluator()

# The tool choice and execution trace must remain byte-for-byte identical
evaluator.add_rule(ExactStabilityRule(path="tool_trace"))

# Timestamps, execution IDs, and version_id are allowed to change
evaluator.add_rule(AllowedDriftRule([
    "timestamp",
    "metadata.execution_id",
    "version_id",
]))

adapter = StabilitySurfaceAdapter()

# Loaded from Phylax ledgers in practice
surface = adapter.adapt(
    baseline={"version_id": "gpt-4o", "tool_trace": [...], "timestamp": "t1"},
    current={"version_id": "gpt-4.5", "tool_trace": [...], "timestamp": "t2"},
)

verdict = evaluator.evaluate(surface)
# Passes IFF only timestamp and version_id drifted`;

export default function CrossRunStabilityPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Cross-Run Stability</h1>
            <p className="text-xl text-coffee-bean/80">
                Protect against regressions during LLM model upgrades by asserting output immutability.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The Regression Gate</h2>
            <p className="text-coffee-bean/80 mb-4">
                Stability surfaces compare a &quot;golden baseline&quot; run against the &quot;current&quot; run.
                When you upgrade from <code>gpt-4o</code> to <code>gpt-4.5</code>, you need to guarantee that JSON structures, tool choices, and logic didn&apos;t mutate.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong><code>ExactStabilityRule(path=None)</code></strong> — Asserts that a specific field (or the entire hashed payload if <code>None</code>) is byte-for-byte identical to the baseline.</li>
                    <li><strong><code>AllowedDriftRule(allowed_fields)</code></strong> — Fails if any field <em>other than</em> the explicitly permitted ones changed (e.g., timestamps, UUIDs).</li>
                </ul>
            </div>

            <CodeBlock language="python" title="model_upgrade_stability.py" code={STABILITY_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">No Fuzzy Diffing</h2>
            <p className="text-coffee-bean/80">
                Phylax explicitly bans &quot;smart&quot; diffing. There are no moving averages, no automated baselines, and no confidence scoring on drift. It&apos;s either a matched hash or it&apos;s a regression.
            </p>
        </div>
    );
}
