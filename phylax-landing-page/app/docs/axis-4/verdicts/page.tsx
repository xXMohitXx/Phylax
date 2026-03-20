import React from 'react';
import { CodeBlock } from '@/components/code-block';

const VERDICT_JSON = `{
  "schema_version": "1.0.0",
  "run_id": "r1",
  "mode": "enforce",
  "verdict": "FAIL",
  "expectations_evaluated": 15,
  "failures": 1,
  "definition_snapshot_hash": "e3b0c442...",
  "timestamp": "2026-01-01T00:00:00Z",
  "engine_version": "1.6.4"
}`;

const EXIT_CODE_EXAMPLE = `from phylax import resolve_exit_code

# In enforce mode, a FAIL verdict → exit 1
code = resolve_exit_code(verdict="FAIL", mode="enforce")
print(code)  # 1

# In observe mode, a FAIL verdict → exit 0 (logged but not blocking)
code = resolve_exit_code(verdict="FAIL", mode="observe")
print(code)  # 0`;

export default function VerdictsPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Verdicts & Artifacts</h1>
            <p className="text-xl text-coffee-bean/80">
                Deterministic, schema-locked outputs designed for cold, mechanical CI automation.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Frozen Schema Contracts</h2>
            <p className="text-coffee-bean/80 mb-4">
                When Phylax completes an evaluation run, it serializes results into strictly typed JSON artifacts (<code>VerdictArtifact</code>, <code>FailureArtifact</code>, and <code>TraceDiffArtifact</code>). These artifacts are structurally guaranteed — they will never change shape without a major <code>schema_version</code> bump.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong>Deterministic Serialization:</strong> Identical runs yield identical JSON string hashes (excluding timestamps/UUIDs). Keys are always sorted.</li>
                    <li><strong>No Commentary:</strong> You will never find fields like <code>explanation</code>, <code>advice</code>, or <code>severity_score</code>. Failures only state what rule broke and the expected vs. actual data.</li>
                    <li><strong>Strict Backward Compatibility:</strong> A v1.0.0 artifact generated years ago will parse flawlessly in the current engine.</li>
                </ul>
            </div>

            <CodeBlock language="json" title="verdict.json" code={VERDICT_JSON} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Deterministic Exit Codes</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax outputs exactly three OS-level exit codes:
            </p>

            <div className="overflow-x-auto mb-6">
                <table className="w-full text-sm border-collapse">
                    <thead><tr className="border-b border-black/10">
                        <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Code</th>
                        <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Constant</th>
                        <th className="text-left py-3 font-semibold text-coffee-bean">Meaning</th>
                    </tr></thead>
                    <tbody className="text-coffee-bean/80">
                        <tr className="border-b border-black/5"><td className="py-3 pr-4"><code>0</code></td><td className="py-3 pr-4"><code>EXIT_PASS</code></td><td className="py-3">Passed, or in observe/quarantine mode</td></tr>
                        <tr className="border-b border-black/5"><td className="py-3 pr-4"><code>1</code></td><td className="py-3 pr-4"><code>EXIT_FAIL</code></td><td className="py-3">Test explicitly failed in enforce mode</td></tr>
                        <tr><td className="py-3 pr-4"><code>2</code></td><td className="py-3 pr-4"><code>EXIT_SYSTEM_ERROR</code></td><td className="py-3">Fatal configuration or system error</td></tr>
                    </tbody>
                </table>
            </div>

            <CodeBlock language="python" title="exit_codes.py" code={EXIT_CODE_EXAMPLE} />
        </div>
    );
}
