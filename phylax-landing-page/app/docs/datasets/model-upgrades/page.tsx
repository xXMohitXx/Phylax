import React from 'react';
import { CodeBlock } from '@/components/code-block';

const SIM_CODE = `from phylax import (
    load_dataset,
    simulate_upgrade,
    format_simulation_report,
)

ds = load_dataset("datasets/support_bot.yaml")

def gpt4_handler(prompt: str) -> str:
    return openai_call(model="gpt-4", prompt=prompt)

def gpt45_handler(prompt: str) -> str:
    return openai_call(model="gpt-4.5", prompt=prompt)

# Run simulation: baseline vs candidate model
sim = simulate_upgrade(
    dataset=ds,
    baseline_func=gpt4_handler,
    candidate_func=gpt45_handler,
    baseline_name="GPT-4",
    candidate_name="GPT-4.5",
)

if sim.safe_to_upgrade:
    print("✅ Safe to deploy!")
else:
    print("❌ Model upgrade introduces regressions")

print(format_simulation_report(sim))`;

const CLI_CODE = `$ phylax simulate --from gpt-4 --to gpt-4.5 datasets/support_bot.yaml

[Simulating 450 contract interactions...]

[gpt-4.5] PASS: Test 12  (Latency: 800ms)
[gpt-4.5] FAIL: Test 42
   Violation: ToolPresenceRule failed
   Expected:  'fetch_db'
   Actual:    {}
[gpt-4.5] FAIL: Test 187
   Violation: must_include("refund_policy")

Results: 448/450 passed — 2 failed
CI Blocked. Model upgrade rejected.`;

export default function ModelUpgradesPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Model Upgrades</h1>
            <p className="text-xl text-coffee-bean/80">
                A/B test a model upgrade against your full dataset before deploying — no surprises in production.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">simulate_upgrade()</h2>
            <p className="text-coffee-bean/80 mb-4">
                <code>simulate_upgrade()</code> runs your entire Dataset Contracts suite through both the baseline and candidate model, then compares results. The <code>safe_to_upgrade</code> flag is <code>True</code> only if the candidate introduces zero regressions.
            </p>

            <CodeBlock language="python" title="simulation.py" code={SIM_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">CLI Output</h2>
            <CodeBlock language="bash" title="Terminal" code={CLI_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Safety Criteria</h3>
                <ul className="space-y-2 text-coffee-bean/80">
                    <li>✓ Zero new contract failures introduced by candidate model</li>
                    <li>✓ No latency regression beyond declared thresholds</li>
                    <li>✓ No tool calling pattern changes</li>
                    <li>✓ Structural JSON output remains conformant</li>
                </ul>
            </div>
        </div>
    );
}
