import React from 'react';
import { CodeBlock } from '@/components/code-block';

// Secret interpolation in YAML: ${{ secrets.X }} - use a JS const to avoid JSX brace conflict
const GITHUB_ACTIONS_YAML = `
name: LLM Evaluation Gates

on:
  pull_request:
    branches: [ "main" ]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          pip install phylax

      - name: Run Phylax Suite
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}
          PHYLAX_MODE: "enforce"
        run: |
          python run_evals.py --dataset tests/support_ds.yaml

      # If phylax detects a regression, 
      # the step fails and blocks the PR merging.
`;

export default function GitHubActionsPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">GitHub Actions</h1>
            <p className="text-xl text-coffee-bean/80">
                Blocking Pull Requests when semantic regressions are detected.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The Pipeline</h2>
            <p className="text-coffee-bean/80 mb-4">
                Because Phylax enforces deterministic exit codes (<code>0</code> for pass or safe modes, <code>1</code> for failure in enforce mode), integrating it into GitHub Actions is as simple as running your standard python script.
            </p>

            <CodeBlock language="yaml" title=".github/workflows/phylax-eval.yml" code={GITHUB_ACTIONS_YAML} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Artifact Storage</h3>
                <p className="text-coffee-bean/80">
                    We recommend using the <code>actions/upload-artifact</code> step to capture the <code>verdict.json</code> and <code>ledger.jsonl</code> files after the run so they can be parsed by external dashboards.
                </p>
            </div>

        </div>
    );
}
