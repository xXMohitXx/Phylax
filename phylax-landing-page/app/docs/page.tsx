import React from 'react';
import { CodeBlock } from '@/components/code-block';

const EXAMPLE_CODE = `
from phylax import trace, expect

@trace(provider="openai")
@expect(must_include=["refund"], must_not_include=["lawsuit"])
def reply(prompt):
    return llm(prompt)
`;

export default function DocsOverviewPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Phylax Documentation</h1>
      <p className="text-xl text-coffee-bean/80">
        Stop AI regressions before they reach production. Phylax is <strong>CI for AI behavior</strong>.
      </p>

      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">What is Phylax?</h2>
      <p className="text-coffee-bean/80 mb-4">
        Phylax records LLM outputs, evaluates them against declared contracts, and fails builds when behavior regresses.
        There is no probabilistic scoring, no AI judges, and no fuzzy "evals" — just deterministic PASS/FAIL enforcement.
      </p>

      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-4 mb-8">
        <h3 className="text-lg font-semibold text-coffee-bean mb-2">Key Value Proposition</h3>
        <ul className="space-y-2 text-coffee-bean/80 list-disc ml-4">
          <li><strong>Zero LLM Judges:</strong> Evaluation is entirely deterministic code.</li>
          <li><strong>CI-Native:</strong> Block pull requests if an LLM refactor breaks behavior.</li>
          <li><strong>Multi-Provider:</strong> Support for OpenAI, Gemini, Groq, Mistral, HuggingFace, and local Ollama models.</li>
          <li><strong>Multi-Agent Validation:</strong> Test exact step counts and required tool chains out-of-the-box.</li>
          <li><strong>Model Upgrade Simulator:</strong> Automatically A/B test a dataset across two models to identify breaking changes.</li>
        </ul>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">The 10-Second Example</h2>
      <CodeBlock language="python" title="example.py" code={EXAMPLE_CODE} />

      <p className="text-coffee-bean/80 mt-4 mb-4">
        Run your test suite, then run <code>phylax check</code> in CI. If any change to your prompt, model, or RAG context breaks the expectation, the CI job fails immediately.
      </p>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Where to go from here?</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <a href="/docs/getting-started/installation" className="block p-4 rounded-lg border border-black/10 hover:border-coffee-bean/30 transition-colors bg-white/50">
          <h3 className="font-semibold text-coffee-bean">Installation</h3>
          <p className="text-sm text-coffee-bean/70 mt-1">Get Phylax set up in your local environment.</p>
        </a>
        <a href="/docs/getting-started/quickstart" className="block p-4 rounded-lg border border-black/10 hover:border-coffee-bean/30 transition-colors bg-white/50">
          <h3 className="font-semibold text-coffee-bean">Quickstart</h3>
          <p className="text-sm text-coffee-bean/70 mt-1">From zero to your first passing CI check in 10 minutes.</p>
        </a>
        <a href="/docs/concepts/traces-expectations" className="block p-4 rounded-lg border border-black/10 hover:border-coffee-bean/30 transition-colors bg-white/50">
          <h3 className="font-semibold text-coffee-bean">Core Concepts</h3>
          <p className="text-sm text-coffee-bean/70 mt-1">Learn about Traces, Expectations, and the Graph Model.</p>
        </a>
        <a href="/docs/why-phylax" className="block p-4 rounded-lg border border-black/10 hover:border-coffee-bean/30 transition-colors bg-white/50">
          <h3 className="font-semibold text-coffee-bean">Why Phylax?</h3>
          <p className="text-sm text-coffee-bean/70 mt-1">The philosophy and design principles behind the library.</p>
        </a>
      </div>
    </div>
  );
}