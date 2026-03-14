import React from 'react';
import Link from 'next/link';
import { Footer } from '@/components/Footer';

export default function WhyAiRegresses() {
  return (
    <>
      <article className="max-w-3xl mx-auto px-6 py-24 prose prose-slate prose-a:text-lime-cream hover:prose-a:text-lime-cream/80 prose-headings:text-coffee-bean prose-p:text-coffee-bean/80 prose-li:text-coffee-bean/80 prose-code:text-coffee-bean prose-code:bg-beige prose-code:px-1.5 prose-code:rounded-md prose-strong:text-coffee-bean">
        
        <Link href="/blog" className="text-sm font-medium text-coffee-bean/60 hover:text-lime-cream mb-12 inline-block no-underline">
          &larr; Back to Blog
        </Link>

        <div className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-lime-cream bg-coffee-bean/10 px-2 py-0.5 rounded text-sm font-medium no-underline">Engineering</span>
            <span className="text-coffee-bean/50 text-sm">March 14, 2026</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-coffee-bean mb-6 leading-tight">
            Why AI Systems Regress
          </h1>
          <p className="text-xl text-coffee-bean/60">
            The fundamental problem with prompt engineering is that you are building software on top of a shifting, non-deterministic foundation.
          </p>
        </div>

        <p>
          If you change a SQL query, you know exactly what rows will return. If you change a regex, you know what it matches. But when you tweak an LLM prompt, or when OpenAI silently updates their model weights, the blast radius is fundamentally unknowable without testing.
        </p>

        <h2>The Three Horsemen of AI Regressions</h2>
        
        <h3>1. Silent Model Updates</h3>
        <p>
          Upstream providers continuously refine their proprietary models (e.g., GPT-4 variants). Even if you pin a specific version, they are eventually deprecated. A model that perfectly followed your structured JSON output instructions yesterday might suddenly start wrapping its responses in markdown backticks today, breaking your parsing logic.
        </p>

        <h3>2. Prompt Drift</h3>
        <p>
          As systems scale, developers add &quot;just one more requirement&quot; to the prompt: <em>&quot;Also, if the user asks about billing, politely decline.&quot;</em> This context window bloat changes the attention mechanisms of the LLM. Your new billing requirement might work, but it might inexplicably cause the model to stop formatting prices correctly.
        </p>

        <h3>3. Non-deterministic Degradation</h3>
        <p>
          By nature, autoregressive models sample from probability distributions. Over millions of invocations, rare paths are taken. An agent workflow that calls the <code>fetch_database</code> tool 99.9% of the time might suddenly hallucinate a <code>query_database</code> tool that doesn&apos;t exist.
        </p>

        <h2>The Fallacy of Production Monitoring</h2>
        <p>
          The industry&apos;s first reaction to this problem was <strong>Observability</strong>. Tools that log every prompt and response, and perhaps run a weaker LLM over the logs to &quot;score&quot; them (LLM-as-a-judge).
        </p>
        <p>
          But observability is inherently reactive. You are finding out your system broke <em>after</em> it has already hallucinated to your enterprise customers for six hours.
        </p>

        <h2>How Phylax Solves This</h2>
        <p>
          Software engineering already solved this problem decades ago: Continuous Integration (CI).
        </p>
        <p>
          Phylax moves AI testing from the production monitoring layer to the CI testing layer. By running deterministic <strong>Dataset Contracts</strong> against live models during your GitHub Actions pipeline, Phylax ensures that your core behavioral constraints hold true <em>before</em> code merges.
        </p>
        <ul>
          <li>It doesn&apos;t use AI to judge AI (which is too flaky for CI).</li>
          <li>It runs fast enough to block PRs.</li>
          <li>It enforces explicit, boolean constraints (e.g., <code>must_include</code>, latency bounds, JSON schema matches).</li>
        </ul>

        <p>
          Stop testing with vibes. Start enforcing contracts. <Link href="/docs/quickstart">Check out the Quickstart</Link>.
        </p>

      </article>
      <Footer />
    </>
  );
}
