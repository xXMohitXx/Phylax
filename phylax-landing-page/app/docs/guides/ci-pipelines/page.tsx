import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function CiPipelinesPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">CI Pipelines</h1>
      <p className="text-xl text-coffee-bean/80">End-to-end guide for integrating Phylax into your CI/CD pipeline — from basic checks to advanced dataset simulation.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">GitHub Actions (Basic)</h2>
      <CodeBlock language="yaml" title=".github/workflows/phylax.yml" code={`name: Phylax CI
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
      - run: phylax check
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">GitHub Actions (Dataset Contracts)</h2>
      <CodeBlock language="yaml" title=".github/workflows/phylax-datasets.yml" code={`name: Phylax Dataset CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install phylax[openai]
      - run: phylax check
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}
      - run: phylax dataset run datasets/
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">GitLab CI</h2>
      <CodeBlock language="yaml" title=".gitlab-ci.yml" code={`phylax:
  image: python:3.10
  stage: test
  script:
    - pip install phylax[all]
    - phylax check
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">CircleCI</h2>
      <CodeBlock language="yaml" title=".circleci/config.yml" code={`version: 2.1
jobs:
  phylax-check:
    docker:
      - image: cimg/python:3.10
    steps:
      - checkout
      - run: pip install phylax[all]
      - run: phylax check`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Enforcement Mode Strategy</h2>
      <p className="text-coffee-bean/80 mb-4">Gradually roll out contracts without breaking your pipeline:</p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Phase</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Mode</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Behavior</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Week 1-2</td><td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-xs">observe</code></td><td className="py-3">Log violations, CI always passes</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Week 3-4</td><td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-xs">quarantine</code></td><td className="py-3">CI fails, violations flagged for review</td></tr>
            <tr><td className="py-3 pr-4 font-medium">Week 5+</td><td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-xs">enforce</code></td><td className="py-3">CI blocks on any contract violation</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
