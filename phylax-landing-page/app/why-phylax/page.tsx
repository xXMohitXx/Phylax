import React from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Footer } from '@/components/Footer';

export default function WhyPhylaxPage() {
  return (
    <>
      <div className="max-w-4xl mx-auto px-6 py-24 prose prose-slate prose-a:text-lime-cream hover:prose-a:text-lime-cream/80 prose-headings:text-coffee-bean prose-p:text-coffee-bean/80 prose-li:text-coffee-bean/80 prose-strong:text-coffee-bean prose-code:text-coffee-bean prose-code:bg-beige prose-code:px-1.5 prose-code:rounded-md prose-em:text-coffee-bean/70">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-coffee-bean mb-8">
          Why Phylax?
        </h1>
        
        <p className="text-xl text-coffee-bean/60 leading-relaxed mb-12">
          Software engineering has established rigorous standards for shipping code: type checking, unit tests, integration tests, and CI/CD pipelines. But when it comes to AI, the industry reverted to &quot;prompting and praying.&quot; Phylax exists to bring deterministic engineering back to AI development.
        </p>

        <h2>The Status Quo is Broken</h2>
        <p>
          Right now, if you are building a non-trivial AI application, your testing strategy likely looks like one of these:
        </p>
        <ul>
          <li><strong>Vibes-based testing:</strong> The developer manually types 5 prompts into a playground, sees it works, and ships it.</li>
          <li><strong>LLM-as-a-judge:</strong> Sending responses to GPT-4 to ask &quot;did this response follow the rules?&quot; This is slow, expensive, and adds non-determinism to your testing suite (who tests the tester?).</li>
          <li><strong>Production Monitoring:</strong> Waiting for users to encounter hallucinations or broken JSON, and then trying to patch the prompt in a panic.</li>
        </ul>

        <h2>A New Paradigm: CI Enforcement for AI Behavior</h2>
        <p>
          Phylax operates on a simple premise: <strong>If an AI behavior is a business requirement, it must be an enforced contract.</strong>
        </p>
        <p>
          If your medical support bot must <em>never</em> give dosages, that is not a &quot;prompting suggestion&quot;&mdash;it is a strict boolean constraint. Phylax allows you to express these constraints programmatically and enforce them in your CI pipeline.
        </p>

        <h3>How it Differs from Observability</h3>
        <p>
          Tools like LangSmith, Braintrust, or Datadog LLM Observability are designed to show you what happened <em>after</em> it happened in production. They are phenomenal for tracing and token counting latency.
        </p>
        <p>
          <strong>Phylax is not an observability tool.</strong> It is an active contract enforcement mechanism that blocks PRs and model deployments if behavioral tests fail. It is the unit testing framework for the AI age.
        </p>

        <h2>Core Design Principles</h2>
        <ol>
          <li>
            <strong>Determinism over &quot;AI Vibes&quot;:</strong> Phylax relies on pythonic AST extraction, regex, JSON schema validation, latency thresholds, and explicit token bounds. We never use an LLM to evaluate an LLM.
          </li>
          <li>
            <strong>Zero Infrastructure:</strong> Phylax stores ground-truth traces as local JSON files (with SQLite indexing). You don&apos;t need to spin up a Docker container or pay for a SaaS just to run your test suite.
          </li>
          <li>
            <strong>Evidence Purity:</strong> When a multi-agent system fails, Phylax&apos;s execution graph isolates the exact parent/child nested node that hallucinated, providing the <em>first failing node</em> rather than just the final corrupted output.
          </li>
        </ol>

        <h2>The Phylax Lifecycle</h2>
        <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 not-prose my-8">
          <div className="grid grid-cols-5 gap-2 text-center text-sm font-mono">
            <div className="bg-porcelain rounded-lg p-4 border border-black/5">
              <div className="text-lg mb-1">📝</div>
              <div className="font-bold text-coffee-bean">Trace</div>
              <div className="text-coffee-bean/60 text-xs mt-1">Record LLM calls</div>
            </div>
            <div className="bg-porcelain rounded-lg p-4 border border-black/5">
              <div className="text-lg mb-1">✅</div>
              <div className="font-bold text-coffee-bean">Expect</div>
              <div className="text-coffee-bean/60 text-xs mt-1">Define PASS/FAIL</div>
            </div>
            <div className="bg-porcelain rounded-lg p-4 border border-black/5">
              <div className="text-lg mb-1">⭐</div>
              <div className="font-bold text-coffee-bean">Bless</div>
              <div className="text-coffee-bean/60 text-xs mt-1">Lock baselines</div>
            </div>
            <div className="bg-porcelain rounded-lg p-4 border border-black/5">
              <div className="text-lg mb-1">🔍</div>
              <div className="font-bold text-coffee-bean">Check</div>
              <div className="text-coffee-bean/60 text-xs mt-1">Compare outputs</div>
            </div>
            <div className="bg-porcelain rounded-lg p-4 border border-black/5">
              <div className="text-lg mb-1">🚫</div>
              <div className="font-bold text-coffee-bean">Block</div>
              <div className="text-coffee-bean/60 text-xs mt-1">Fail CI on drift</div>
            </div>
          </div>
        </div>

        <div className="mt-16 p-8 bg-beige/40 border border-coffee-bean/10 rounded-2xl text-center not-prose">
          <h3 className="text-2xl font-bold text-coffee-bean mb-4 mt-0">Ready to enforce your AI contracts?</h3>
          <p className="mb-6 text-coffee-bean/60">Stop waiting for production to find out your prompt drifted.</p>
          <Link href="/docs/quickstart">
            <button className="px-6 py-3 bg-lime-cream hover:bg-lime-cream/90 text-coffee-bean rounded-lg font-bold transition-colors flex items-center gap-2 mx-auto">
              Get Started in 5 Minutes <ArrowRight className="w-4 h-4" />
            </button>
          </Link>
        </div>

      </div>
      <Footer />
    </>
  );
}
