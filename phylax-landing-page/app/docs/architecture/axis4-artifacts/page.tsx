import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function Axis4Page() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Axis 4 — Ecosystem Discipline</h1>
      <p className="text-xl text-coffee-bean/80">Machine-consumable CI artifacts, deterministic exit codes, governance documents, Dataset Contracts, Behavioral Diffs, Model Simulator, and Guardrail Packs.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 4.1: Artifact Contracts</h2>
      <CodeBlock language="python" title="artifacts.py" code={`from phylax import (
    generate_verdict_artifact,   # Overall CI verdict
    generate_failure_artifact,   # Detailed failure records
    generate_trace_diff,         # Changes between runs
    EXIT_PASS, EXIT_FAIL, EXIT_SYSTEM_ERROR, resolve_exit_code,
)

# Verdict artifact: frozen, deterministic JSON
verdict = generate_verdict_artifact(
    mode="enforce", verdict="FAIL",
    expectations_evaluated=10, failures=3,
    definition_snapshot_hash="abc123",
    engine_version="1.6.3",
)

# Exit code resolution
code = resolve_exit_code(verdict="FAIL", mode="enforce")  # → 1
code = resolve_exit_code(verdict="FAIL", mode="observe")  # → 0`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 4.2: Dataset Contracts</h2>
      <CodeBlock language="python" title="datasets.py" code={`from phylax import Dataset, DatasetCase, load_dataset, run_dataset, format_report

ds = load_dataset("datasets/support_bot.yaml")
result = run_dataset(ds, handler_function)
print(format_report(result))`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 4.3: Behavioral Diff Engine</h2>
      <CodeBlock language="python" title="diff_engine.py" code={`from phylax import diff_runs, format_diff_report

diff = diff_runs(result_a, result_b)
print(format_diff_report(diff))
# Shows: new failures, new passes, changed outputs`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 4.4: Model Simulator</h2>
      <CodeBlock language="python" title="simulator.py" code={`from phylax import simulate_upgrade, format_simulation_report

sim = simulate_upgrade(
    dataset=ds,
    baseline_func=gpt4_handler,
    candidate_func=gpt45_handler,
    baseline_name="GPT-4",
    candidate_name="GPT-4.5",
)
print(format_simulation_report(sim))`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 4.5: Guardrail Packs</h2>
      <CodeBlock language="python" title="guardrails.py" code={`from phylax import (
    GuardrailPack, get_pack, list_packs, apply_pack,
    safety_pack, quality_pack, compliance_pack,
)

# Pre-built packs
safety = safety_pack()      # Blocks hate, PII, harmful content
quality = quality_pack()     # Min length, latency ceiling
compliance = compliance_pack() # Regulatory constraints

# List all available packs
all_packs = list_packs()

# Apply to expectations
expectations = safety.to_expectations()`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Governance Documents</h2>
      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6">
        <ul className="space-y-3 text-coffee-bean/80">
          <li><strong>CONSTITUTION.md</strong> — 12 promises Phylax will never break (no explanation, no ranking, no AI inference, no dashboards, no alerts)</li>
          <li><strong>ANTI_FEATURES.md</strong> — Documented non-features (no dashboards, no alerting, no daemons, no plugins)</li>
        </ul>
      </div>
    </div>
  );
}
