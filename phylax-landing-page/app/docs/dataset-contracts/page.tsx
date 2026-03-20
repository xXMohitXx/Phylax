import React from 'react';
import { CodeBlock } from '@/components/code-block';

const DATASET_CI_YAML = `
name: Dataset Contract CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install phylax[openai]
      - run: phylax dataset run datasets/support_bot.yaml
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}
`;

const CODE_BLOCK_0 = `
dataset: support_bot
cases:
  - input: "I want a refund for my last purchase"
    expectations:
      must_include: ["refund_policy", "30_days"]
      must_not_include: ["credit_card_number"]
      max_latency_ms: 3000
      min_tokens: 20

  - input: "How do I reset my password?"
    expectations:
      must_include: ["password", "reset"]
      must_not_include: ["credit_card", "SQL"]
      max_latency_ms: 2000

  - input: "What is your return policy?"
    expectations:
      must_include: ["return", "days"]
      min_tokens: 50
`;
const CODE_BLOCK_1 = `
from phylax import (
    Dataset, DatasetCase, DatasetResult, CaseResult,
    load_dataset, run_dataset, format_report, format_json_report,
)

# Create programmatically
ds = Dataset(dataset="my_bot", cases=[
    DatasetCase(
        input="help with refund",
        expectations={"must_include": ["refund"], "min_tokens": 10},
    ),
    DatasetCase(
        input="billing question",
        expectations={"must_not_include": ["internal_error"]},
    ),
])

# Or load from YAML
ds = load_dataset("datasets/support_bot.yaml")

# Run against your handler
result = run_dataset(ds, handler_function)

# Human-readable report
print(format_report(result))

# Machine-consumable JSON report
json_report = format_json_report(result)
`;
const CODE_BLOCK_2 = `
# Run a dataset contract
phylax dataset run datasets/support_bot.yaml

# Output:
# Running dataset 'support_bot'...
# [Case 1/3] "I want a refund..." ✓ PASS
# [Case 2/3] "How do I reset..." ✓ PASS
# [Case 3/3] "What is your..."   ✗ FAIL
#   Violation: min_tokens (actual: 12, minimum: 50)
# 
# ❌ 1 of 3 cases failed. Exit code 1.
`;
const CODE_BLOCK_3 = `
from phylax import (
    CaseDiff, DatasetDiff,
    diff_runs, format_diff_report, format_diff_json,
)

# Compare run A vs run B
diff = diff_runs(result_before, result_after)

# See what changed
print(format_diff_report(diff))
# Shows: new failures, new passes, changed outputs

# Machine-consumable diff
json_diff = format_diff_json(diff)
`;

export default function DatasetContractsPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Dataset Contracts</h1>
      <p className="text-xl text-coffee-bean/80">
        Dataset Contracts are YAML-defined behavioral test suites. They batch-test hundreds of prompts against live models and enforce deterministic expectations — ideal for CI regression gates and model upgrade validation.
      </p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">YAML Format</h2>
      <CodeBlock language="yaml" title="datasets/support_bot.yaml" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Python API</h2>
      <CodeBlock language="python" title="dataset_usage.py" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">CLI Usage</h2>
      <CodeBlock language="bash" title="Terminal" code={CODE_BLOCK_2} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Behavioral Diff Engine</h2>
      <p className="text-coffee-bean/80 mb-4">Compare two dataset runs to detect behavioral changes between versions:</p>
      <CodeBlock language="python" title="diff_engine.py" code={CODE_BLOCK_3} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">CI Integration</h2>
      <CodeBlock language="yaml" title=".github/workflows/dataset.yml" code={DATASET_CI_YAML} />
    </div>
  );
}
