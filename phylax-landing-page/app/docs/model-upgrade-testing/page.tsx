import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function ModelUpgradeTestingPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Model Upgrade Testing</h1>
      <p className="text-xl text-coffee-bean/80">
        Safely test model upgrades before deploying. Phylax runs your Dataset Contracts against both the current and candidate model, compares results, and tells you whether the upgrade is safe.
      </p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">The Problem</h2>
      <p className="text-coffee-bean/80 mb-4">
        When OpenAI releases GPT-4.5 or you want to switch from Gemini to Groq, how do you know your app&apos;s behavioral contracts still hold? Without systematic testing, model upgrades become &quot;deploy and pray.&quot;
      </p>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">simulate_upgrade()</h2>
      <CodeBlock language="python" title="simulation.py" code={`from phylax import (
    Dataset, DatasetCase, load_dataset,
    simulate_upgrade, SimulationResult, format_simulation_report,
)

# Define or load your dataset
ds = load_dataset("datasets/support_bot.yaml")

# Define handler functions for each model
def gpt4_handler(prompt):
    return openai_call(model="gpt-4", prompt=prompt)

def gpt45_handler(prompt):
    return openai_call(model="gpt-4.5", prompt=prompt)

# Run simulation
sim = simulate_upgrade(
    dataset=ds,
    baseline_func=gpt4_handler,
    candidate_func=gpt45_handler,
    baseline_name="GPT-4",
    candidate_name="GPT-4.5",
)

# Check result
if sim.safe_to_upgrade:
    print("✅ Safe to deploy!")
else:
    print("❌ Model upgrade introduces regressions")

# Full report
print(format_simulation_report(sim))`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">CLI Usage</h2>
      <CodeBlock language="bash" title="Terminal" code={`$ phylax simulate --from gpt-4 --to gpt-4.5 datasets/support_bot.yaml

[Simulating 450 contract interactions...]

[gpt-4.5] PASS: Test 12 (Latency: 800ms)
[gpt-4.5] FAIL: Test 42
   Violation: ToolPresenceRule failed
   Expected: 'fetch_db'
   Actual Payload: {}
[gpt-4.5] FAIL: Test 187
   Violation: must_include("refund_policy")

Results: 448/450 passed, 2 failed
CI Blocked. Model upgrade rejected.`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">What It Tests</h2>
      <ul className="space-y-3 text-coffee-bean/80 list-disc pl-6 marker:text-lime-cream">
        <li><strong>Content compliance:</strong> Do responses still include required terms and avoid forbidden content?</li>
        <li><strong>Latency regression:</strong> Is the new model slower than acceptable thresholds?</li>
        <li><strong>Tool call stability:</strong> Does the new model still call the right tools with correct arguments?</li>
        <li><strong>Response length:</strong> Does the new model produce shorter or longer responses than expected?</li>
        <li><strong>Structural output:</strong> Does the new model still produce valid JSON with required fields?</li>
      </ul>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">CI Integration</h2>
      <CodeBlock language="yaml" title=".github/workflows/model-upgrade.yml" code={`name: Model Upgrade Test
on:
  workflow_dispatch:
    inputs:
      candidate_model:
        description: 'New model to test'
        required: true
jobs:
  simulate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install phylax[openai]
      - run: phylax simulate --from gpt-4 --to \${{ inputs.candidate_model }} datasets/
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}`} />
    </div>
  );
}
