import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CI_YAML_SECTION = `
name: Phylax CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install phylax[all]

      # Run CI enforcement
      - run: phylax check
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}

      # Optional: run dataset contracts
      - run: phylax dataset run datasets/
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}
`;

const CODE_BLOCK_0 = `
from phylax import ModeHandler, EnforcementMode, VALID_MODES

# VALID_MODES = {"enforce", "quarantine", "observe"}

# enforce → CI fails on violation (default)
handler = ModeHandler(mode=EnforcementMode.ENFORCE)
result = handler.apply("fail")
# result.exit_code = 1

# quarantine → CI fails, violations logged for review
handler = ModeHandler(mode=EnforcementMode.QUARANTINE)
result = handler.apply("fail")
# result.exit_code = 1

# observe → CI passes, violations logged only
handler = ModeHandler(mode=EnforcementMode.OBSERVE)
result = handler.apply("fail")
# result.exit_code = 0
`;
const CODE_BLOCK_1 = `
from phylax import (
    generate_verdict_artifact,   # Overall CI verdict
    generate_failure_artifact,   # Detailed failure records
    generate_trace_diff,         # Changes between runs
    EXIT_PASS, EXIT_FAIL, EXIT_SYSTEM_ERROR, resolve_exit_code,
)

# Generate verdict artifact
verdict = generate_verdict_artifact(
    mode="enforce",
    verdict="FAIL",
    expectations_evaluated=10,
    failures=3,
    definition_snapshot_hash="abc123",
    engine_version="1.6.3",
)

# Deterministic exit code resolution
code = resolve_exit_code(verdict="FAIL", mode="enforce")  # → 1
code = resolve_exit_code(verdict="FAIL", mode="observe")  # → 0
`;
const CODE_BLOCK_2 = `
from phylax import (
    MinExpectationCountRule,    # Fail if too few expectations
    ZeroSignalRule,             # Fail if no expectations have been evaluated
    DefinitionChangeGuard,     # Detect expectation definition changes
    ExpectationRemovalGuard,   # Detect silent expectation removal
)

# Fail if fewer than 3 expectations defined
rule = MinExpectationCountRule(min_count=3)
result = rule.evaluate(current_count=2)
# result.passed = False

# Detect silent expectation removal
guard = ExpectationRemovalGuard()
result = guard.evaluate(
    previous_ids={"e1", "e2", "e3"},
    current_ids={"e1", "e2"},
)
# result.passed = False, result.removed = {"e3"}
`;

export default function CiIntegrationPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">CI Integration</h1>
      <p className="text-xl text-coffee-bean/80">
        Phylax is built for CI/CD pipelines. It exits with deterministic codes, produces machine-consumable artifacts, and integrates with GitHub Actions, GitLab CI, CircleCI, and any CI system that reads exit codes.
      </p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Exit Codes</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Code</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Meaning</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">CI Effect</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-sm">0</code></td><td className="py-3 pr-4">All checks passed</td><td className="py-3 text-lime-cream">✅ Pipeline continues</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-sm">1</code></td><td className="py-3 pr-4">Contract violation detected</td><td className="py-3 text-fail-red">❌ Pipeline blocked</td></tr>
            <tr><td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-sm">2</code></td><td className="py-3 pr-4">System error</td><td className="py-3 text-fail-red">❌ Pipeline blocked</td></tr>
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">GitHub Actions</h2>
      <CodeBlock language="yaml" title=".github/workflows/phylax.yml" code={CI_YAML_SECTION} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Enforcement Modes</h2>
      <p className="text-coffee-bean/80 mb-4">Control how violations affect your CI pipeline:</p>
      <CodeBlock language="python" title="enforcement_modes.py" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">CI Artifacts</h2>
      <p className="text-coffee-bean/80 mb-4">Phylax produces machine-consumable artifacts for downstream tools:</p>
      <CodeBlock language="python" title="ci_artifacts.py" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Meta-Enforcement Rules</h2>
      <p className="text-coffee-bean/80 mb-4">Prevent test suite dilution — guard against weakening your contracts:</p>
      <CodeBlock language="python" title="meta_enforcement.py" code={CODE_BLOCK_2} />

    </div>
  );
}
