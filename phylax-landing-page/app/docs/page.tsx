import React from 'react';

export default function DocsIntroduction() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Introduction to Phylax</h1>
      <p className="text-xl text-coffee-bean/80">
        Phylax is a CI-native, deterministic regression enforcement system for LLM outputs. 
        It records LLM behavior, evaluates explicit expectations, compares against golden baselines, and fails builds when declared contracts regress.
      </p>

      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Core Capabilities</h2>
      <ul className="space-y-4 text-coffee-bean/80 list-disc pl-6 marker:text-lime-cream">
        <li><strong>Trace Capture:</strong> Automatically records every LLM call (input, output, latency, tokens) into an immutable trace schema.</li>
        <li><strong>Deterministic Expectations:</strong> Four built-in rules (<code className="px-1.5 py-0.5 rounded-md bg-code-bg text-lime-cream text-sm">must_include</code>, <code className="px-1.5 py-0.5 rounded-md bg-code-bg text-lime-cream text-sm">must_not_include</code>, <code className="px-1.5 py-0.5 rounded-md bg-code-bg text-lime-cream text-sm">max_latency_ms</code>, <code className="px-1.5 py-0.5 rounded-md bg-code-bg text-lime-cream text-sm">min_tokens</code>) produce binary PASS/FAIL verdicts.</li>
        <li><strong>Expectation Algebra:</strong> Logical composition (AND/OR/NOT), conditional activation, and structural scoping.</li>
        <li><strong>Execution Graphs (DAG):</strong> Builds directed acyclic graphs from grouped traces with semantic node roles.</li>
        <li><strong>CI Enforcement:</strong> Exits 0 on success, exits 1 on contract violation.</li>
      </ul>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Non-Goals</h2>
      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6">
        <p className="text-coffee-bean/90 mb-4">What Phylax will <strong>never</strong> do:</p>
        <ul className="space-y-3 text-coffee-bean/80">
          <li className="flex items-center gap-2"><span className="text-fail-red">❌</span> Not monitoring or observability — no metrics, no dashboards.</li>
          <li className="flex items-center gap-2"><span className="text-fail-red">❌</span> Not production runtime tooling — strictly for CI.</li>
          <li className="flex items-center gap-2"><span className="text-fail-red">❌</span> Not AI-based evaluation — exact match, explicit expectations only.</li>
        </ul>
      </div>
    </div>
  );
}