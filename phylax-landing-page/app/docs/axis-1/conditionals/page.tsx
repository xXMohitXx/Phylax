import React from 'react';
import { CodeBlock } from '@/components/code-block';

const COND_CODE = `from phylax.expectations import (
    when,
    InputContains,
    ModelEquals,
    ProviderEquals,
    FlagSet,
    MustIncludeRule,
    MaxLatencyRule,
)

# IF the input contains "refund" THEN response must contain "policy"
rule_1 = when(
    InputContains("refund"),
    MustIncludeRule(["policy"]),
)

# IF the model is "gpt-4" THEN enforce a strict latency ceiling
rule_2 = when(
    ModelEquals("gpt-4"),
    MaxLatencyRule(2000),
)

# IF the provider is "anthropic" THEN allow up to 5 seconds
rule_3 = when(
    ProviderEquals("anthropic"),
    MaxLatencyRule(5000),
)`;

export default function ConditionalsPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Conditionals (IF/THEN)</h1>
            <p className="text-xl text-coffee-bean/80">
                Activate expectations only when specific contexts are met.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Conditional Evaluation</h2>
            <p className="text-coffee-bean/80 mb-4">
                Conditionals act as exact-match IF gates. If the condition is met, the THEN expectation is evaluated. If the condition is NOT met, the expectation is skipped entirely.
            </p>

            <CodeBlock language="python" title="conditional.py" code={COND_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Condition Evaluators</h2>
            <ul className="space-y-4 text-coffee-bean/80 mt-4 mb-8 list-disc ml-6">
                <li><strong><code>InputContains(str)</code></strong> — Triggers if the trace prompt payload contains the exact substring.</li>
                <li><strong><code>ModelEquals(str)</code></strong> — Triggers if the parsed LLM model matches exactly (e.g. <code>&quot;gpt-4o&quot;</code>).</li>
                <li><strong><code>ProviderEquals(str)</code></strong> — Triggers if the trace source provider matches (e.g. <code>&quot;openai&quot;</code>, <code>&quot;gemini&quot;</code>).</li>
                <li><strong><code>FlagSet(str)</code></strong> — Triggers based on custom boolean metadata flags attached to the trace context.</li>
            </ul>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">No Fuzzy Logic</h3>
                <p className="text-coffee-bean/80">
                    Conditions are <strong>exact matches only</strong>. There is no regex, no semantic similarity, and no fuzzy matching. This ensures complete determinism across hundreds of CI pipeline runs.
                </p>
            </div>
        </div>
    );
}
