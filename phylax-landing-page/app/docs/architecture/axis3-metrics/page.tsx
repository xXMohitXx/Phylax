import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function Axis3Page() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Axis 3 — Scale Safety &amp; Misuse Resistance</h1>
      <p className="text-xl text-coffee-bean/80">Metrics, enforcement modes, and meta-rules that prevent test suite dilution and ensure Phylax scales safely.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 3.1: Metrics Foundation</h2>
      <CodeBlock language="python" title="metrics.py" code={`from phylax import (
    ExpectationIdentity, compute_definition_hash,
    LedgerEntry, EvaluationLedger,
    AggregateMetrics, aggregate, aggregate_all,
    HealthReport, CoverageReport, get_windowed_health,
)

# Stable hash for any expectation definition
hash_val = compute_definition_hash({"rule": "must_include", "substrings": ["refund"]})

# Append-only evaluation ledger
ledger = EvaluationLedger()
ledger.record(LedgerEntry(expectation_id="e1", verdict="pass"))
ledger.record(LedgerEntry(expectation_id="e1", verdict="fail"))

# Aggregate metrics
metrics = aggregate(ledger.entries, "e1")
# metrics.total_evaluations = 2, metrics.failure_rate = 0.5

# Health report
report = HealthReport.from_aggregate(metrics, hash_val)`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 3.3: Enforcement Modes</h2>
      <CodeBlock language="python" title="modes.py" code={`from phylax import ModeHandler, EnforcementMode, VALID_MODES

# Three modes: {"enforce", "quarantine", "observe"}
handler = ModeHandler(mode=EnforcementMode.ENFORCE)
result = handler.apply("fail")
# result.exit_code = 1 (blocks CI)

handler = ModeHandler(mode=EnforcementMode.OBSERVE)
result = handler.apply("fail")
# result.exit_code = 0 (logs only, CI passes)`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 3.4: Meta-Enforcement (Dilution Guards)</h2>
      <p className="text-coffee-bean/80 mb-4">Prevent teams from weakening their test suite:</p>
      <CodeBlock language="python" title="meta_rules.py" code={`from phylax import (
    MinExpectationCountRule,    # Minimum expectations required
    ZeroSignalRule,             # Detect zero-signal test suites
    DefinitionChangeGuard,     # Detect definition mutations
    ExpectationRemovalGuard,   # Detect silent removal
)

# Fail if fewer than 3 expectations
rule = MinExpectationCountRule(min_count=3)
result = rule.evaluate(current_count=2)  # result.passed = False

# Detect removed expectations
guard = ExpectationRemovalGuard()
result = guard.evaluate(
    previous_ids={"e1", "e2", "e3"},
    current_ids={"e1", "e2"},
)
# result.passed = False, result.removed = {"e3"}`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">API Endpoints</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Endpoint</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Description</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4"><code className="text-xs">GET /v1/health/{`{id}`}</code></td><td className="py-3">Expectation health report</td></tr>
            <tr><td className="py-3 pr-4"><code className="text-xs">GET /v1/coverage</code></td><td className="py-3">Coverage report across all expectations</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
