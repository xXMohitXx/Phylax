import React from 'react';
import Link from 'next/link';
import { CodeBlock } from '@/components/code-block';

export default function GettingStartedPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Getting Started</h1>
      <p className="text-xl text-coffee-bean/80">
        Learn the fundamentals of Phylax — what it does, how it works, and how to integrate it into your AI development workflow.
      </p>
      
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">What is Phylax?</h2>
      <p className="text-coffee-bean/80 mb-4">
        Phylax is a <strong>CI-native regression enforcement system for LLM outputs</strong>. It answers one question: <em>&quot;Did my LLM behavior violate a declared contract?&quot;</em>
      </p>
      <p className="text-coffee-bean/80 mb-4">
        Think of it like unit tests for AI behavior. You declare rules (must include &quot;refund&quot;, must respond under 2 seconds, must return valid JSON) and Phylax enforces them in your CI pipeline.
      </p>

      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-4">
        <p className="text-coffee-bean/90 mb-3 font-semibold">The Phylax Lifecycle:</p>
        <div className="font-mono text-sm text-coffee-bean/80 space-y-1">
          <p>1. <strong>TRACE</strong> → Record every LLM call (input, output, latency, tokens)</p>
          <p>2. <strong>EVALUATE</strong> → Apply expectations (binary PASS/FAIL)</p>
          <p>3. <strong>BLESS</strong> → Lock known-good outputs as golden baselines</p>
          <p>4. <strong>CHECK</strong> → Compare new outputs to goldens</p>
          <p>5. <strong>FAIL CI</strong> → Block regressions in your pipeline</p>
        </div>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Prerequisites</h2>
      <ul className="space-y-2 text-coffee-bean/80 list-disc pl-6 marker:text-lime-cream">
        <li>Python 3.10 or higher</li>
        <li>An API key for at least one LLM provider (OpenAI, Google, Groq, Mistral, HuggingFace, or Ollama)</li>
        <li>pip (included with Python)</li>
      </ul>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Installation</h2>
      <CodeBlock language="bash" title="Terminal" code={`# Install with all provider adapters
pip install phylax[all]

# Or install only what you need
pip install phylax[openai]       # OpenAI (GPT-4, GPT-4o)
pip install phylax[google]       # Google Gemini
pip install phylax[groq]         # Groq (Llama 3, Mixtral)
pip install phylax[mistral]      # Mistral AI
pip install phylax[huggingface]  # HuggingFace Inference API
pip install phylax[ollama]       # Ollama (local models)`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Environment Setup</h2>
      <p className="text-coffee-bean/80 mb-4">Configure your provider&apos;s API key as an environment variable:</p>
      <CodeBlock language="bash" title="Environment Variables" code={`# Choose your provider
export OPENAI_API_KEY="sk-..."      # OpenAI
export GOOGLE_API_KEY="AIza..."     # Google Gemini
export GROQ_API_KEY="gsk_..."       # Groq
export MISTRAL_API_KEY="..."        # Mistral
export HF_TOKEN="hf_..."            # HuggingFace
export OLLAMA_HOST="localhost:11434" # Ollama (default)

# Optional: custom Phylax home directory
export PHYLAX_HOME="~/.phylax"      # Default location`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Storage</h2>
      <p className="text-coffee-bean/80 mb-4">Phylax stores all data locally — no cloud, no external dependencies:</p>
      <CodeBlock language="bash" title="File Structure" code={`~/.phylax/
├── config.yaml          # Configuration
├── traces/
│   └── YYYY-MM-DD/
│       └── <trace_id>.json  # Immutable trace records
└── phylax.db            # SQLite index`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Core Concepts</h2>
      <div className="grid md:grid-cols-2 gap-4">
        <Link href="/docs/concepts/traces" className="block p-4 bg-porcelain rounded-lg border border-black/5 hover:border-coffee-bean/20 transition-colors no-underline">
          <h3 className="text-lg font-semibold text-coffee-bean mb-1">Traces</h3>
          <p className="text-sm text-coffee-bean/70">Immutable records of every LLM call</p>
        </Link>
        <Link href="/docs/concepts/expectations" className="block p-4 bg-porcelain rounded-lg border border-black/5 hover:border-coffee-bean/20 transition-colors no-underline">
          <h3 className="text-lg font-semibold text-coffee-bean mb-1">Expectations</h3>
          <p className="text-sm text-coffee-bean/70">Deterministic PASS/FAIL rules</p>
        </Link>
        <Link href="/docs/concepts/execution-graphs" className="block p-4 bg-porcelain rounded-lg border border-black/5 hover:border-coffee-bean/20 transition-colors no-underline">
          <h3 className="text-lg font-semibold text-coffee-bean mb-1">Execution Graphs</h3>
          <p className="text-sm text-coffee-bean/70">DAGs for multi-step agent workflows</p>
        </Link>
        <Link href="/docs/concepts/surfaces" className="block p-4 bg-porcelain rounded-lg border border-black/5 hover:border-coffee-bean/20 transition-colors no-underline">
          <h3 className="text-lg font-semibold text-coffee-bean mb-1">Surfaces</h3>
          <p className="text-sm text-coffee-bean/70">Enforce JSON, tool calls, execution traces</p>
        </Link>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">What Phylax is NOT</h2>
      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6">
        <ul className="space-y-3 text-coffee-bean/80">
          <li className="flex items-center gap-2"><span className="text-fail-red">❌</span> Not monitoring or observability — no metrics, no dashboards</li>
          <li className="flex items-center gap-2"><span className="text-fail-red">❌</span> Not production runtime tooling — strictly for CI</li>
          <li className="flex items-center gap-2"><span className="text-fail-red">❌</span> Not AI-based evaluation — exact match, explicit expectations only</li>
          <li className="flex items-center gap-2"><span className="text-fail-red">❌</span> Not adaptive or heuristic — rules are code, not inference</li>
        </ul>
      </div>

      <div className="mt-8 flex gap-4">
        <Link href="/docs/quickstart" className="text-sm font-medium text-lime-cream hover:text-lime-cream/80 flex items-center gap-1 no-underline">
          Next: Quickstart Guide →
        </Link>
      </div>
    </div>
  );
}
