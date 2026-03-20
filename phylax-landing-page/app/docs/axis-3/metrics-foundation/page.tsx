import React from 'react';
import { CodeBlock } from '@/components/code-block';

const IDENTITY_CODE = `from phylax import ExpectationIdentity, compute_definition_hash

config = {"rule": "must_include", "substrings": ["urgent", "action required"]}

# Creates a frozen identity with auto-generated exp-XXXX ID and SHA-256 hash
identity = ExpectationIdentity.create(config)
print(identity.expectation_id)   # "exp-..." (deterministic from config)
print(identity.definition_hash)  # 64-char SHA-256 hex string

# Optional: supply your own ID
identity2 = ExpectationIdentity.create(config, expectation_id="my-custom-id")
print(identity2.expectation_id)  # "my-custom-id"

# Check if config has changed (hash comparison only, no semantics)
changed_config = {"rule": "must_include", "substrings": ["help"]}
print(identity.has_changed(changed_config))  # True`;

const LEDGER_CODE = `from phylax import EvaluationLedger, LedgerEntry, aggregate
import tempfile, os

with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
    ledger_path = f.name

ledger = EvaluationLedger(ledger_path)

# Append-only — no delete or update methods exist
ledger.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))
ledger.record(LedgerEntry(expectation_id="exp-1", verdict="fail"))

# Deterministic aggregation
results = aggregate(ledger.get_entries(), "exp-1")
print(results.total_evaluations)  # 2
print(results.total_failures)     # 1
print(results.failure_rate)       # 0.5`;

export default function MetricsFoundationPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Metrics Foundation</h1>
            <p className="text-xl text-coffee-bean/80">
                Immutable cryptographic identity and append-only ledger storage for every test verdict.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Expectation Identity</h2>
            <p className="text-coffee-bean/80 mb-4">
                Every expectation config is canonically serialized and SHA-256 hashed. If you change a rule&apos;s threshold — even by a single character — the <code>definition_hash</code> changes, preventing metrics being aggregated across semantically different tests.
            </p>

            <CodeBlock language="python" title="identity_hashing.py" code={IDENTITY_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Evaluation Ledger</h2>
            <p className="text-coffee-bean/80 mb-4">
                Results are written to an append-only <code>.jsonl</code> file via <code>EvaluationLedger</code>. It exposes no <code>delete</code> or <code>update</code> methods — it is a pure audit trail.
            </p>

            <CodeBlock language="python" title="ledger_usage.py" code={LEDGER_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">No Qualitative Labels</h3>
                <p className="text-coffee-bean/80">
                    The metrics foundation operates strictly on numbers. It produces <code>total_evaluations</code>, <code>total_failures</code>, and <code>failure_rate</code>. No &quot;health scores&quot;, no &quot;severity ratings&quot;, no qualitative judgment.
                </p>
            </div>
        </div>
    );
}
