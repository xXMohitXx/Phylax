import React from 'react';
import Link from 'next/link';
import { Footer } from '@/components/Footer';

export default function TestingAiSystems() {
    return (
        <>
            <article className="max-w-3xl mx-auto px-6 py-24 prose prose-slate prose-a:text-lime-cream hover:prose-a:text-lime-cream/80 prose-headings:text-coffee-bean prose-p:text-coffee-bean/80 prose-li:text-coffee-bean/80 prose-code:text-coffee-bean prose-code:bg-beige prose-code:px-1.5 prose-code:rounded-md prose-strong:text-coffee-bean">

                <Link href="/blog" className="text-sm font-medium text-coffee-bean/60 hover:text-lime-cream mb-12 inline-block no-underline">
                    &larr; Back to Blog
                </Link>

                <div className="mb-12">
                    <div className="flex items-center gap-3 mb-6">
                        <span className="text-lime-cream bg-coffee-bean/10 px-2 py-0.5 rounded text-sm font-medium no-underline">Engineering</span>
                        <span className="text-coffee-bean/50 text-sm">March 16, 2026</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-coffee-bean mb-6 leading-tight">
                        How to Test AI Systems Like Software
                    </h1>
                    <p className="text-xl text-coffee-bean/60">
                        Software engineering solved this problem decades ago. Here&apos;s how to apply the same rigor to LLM-powered applications.
                    </p>
                </div>

                <h2>The Testing Gap</h2>
                <p>
                    When a software engineer ships a payment system, they don&apos;t deploy it and &quot;hope it works.&quot; They write unit tests that assert exact behavior: <em>given this input, produce this output</em>. They run integration tests that validate end-to-end flows. They enforce these tests in CI — if any test fails, the pull request doesn&apos;t merge.
                </p>
                <p>
                    AI systems have none of this. The current standard for testing an LLM-powered feature is: run it a few times, eyeball the output, deploy it, and pray. When the model provider pushes an update or someone modifies the system prompt, you find out something broke because a customer files a ticket.
                </p>
                <p>
                    This isn&apos;t a tooling gap — it&apos;s a <strong>discipline gap</strong>. The tools exist. We just haven&apos;t applied the same engineering principles to AI outputs that we apply to database queries and API responses.
                </p>

                <h2>What &quot;Testing AI&quot; Actually Means</h2>
                <p>
                    Testing AI doesn&apos;t mean getting another AI to judge the output (that&apos;s just adding more non-determinism). Testing AI means declaring <strong>behavioral contracts</strong> — explicit, machine-verifiable rules that an LLM response must satisfy — and enforcing them automatically.
                </p>
                <p>
                    A behavioral contract is a statement like:
                </p>
                <ul>
                    <li>&quot;When a user asks about refunds, the response <strong>must contain</strong> the word &apos;refund_policy&apos;&quot;</li>
                    <li>&quot;The response <strong>must not contain</strong> any internal database column names&quot;</li>
                    <li>&quot;The response must arrive in <strong>under 3 seconds</strong>&quot;</li>
                    <li>&quot;The response must be <strong>at least 50 tokens</strong> long&quot;</li>
                </ul>
                <p>
                    These are deterministic. They produce binary PASS/FAIL. They run in milliseconds. And they can run in CI.
                </p>

                <h2>Dataset Contracts — The Equivalent of Test Suites</h2>
                <p>
                    In traditional software, you organize related tests into test suites. In AI testing, the equivalent is a <strong>Dataset Contract</strong> — a YAML file that defines a set of prompts and the behavioral expectations for each:
                </p>
                <pre className="bg-beige/30 rounded-xl p-4 text-sm overflow-x-auto border border-black/10">
                    {`dataset: support_bot
cases:
  - input: "I want a refund"
    expectations:
      must_include: ["refund_policy"]
      must_not_include: ["credit_card_number"]
      max_latency_ms: 3000

  - input: "How do I reset my password?"
    expectations:
      must_include: ["password", "reset"]
      max_latency_ms: 2000

  - input: "Tell me a joke about my boss"
    expectations:
      must_not_include: ["HR_violation", "inappropriate"]
      min_tokens: 10`}
                </pre>
                <p>
                    This is not a prompt evaluation framework. There are no scores, no rubrics, no &quot;rate this on a scale of 1-5.&quot; Each test case either passes or fails. If any case fails, your CI pipeline exits with code 1 and the PR is blocked.
                </p>

                <h2>The Testing Lifecycle</h2>
                <p>
                    Here&apos;s what a mature AI testing workflow looks like:
                </p>
                <ol>
                    <li>
                        <strong>Trace</strong> — Wrap your LLM calls with <code>@trace</code>. Phylax records every input, output, latency, and token count into an immutable trace.
                    </li>
                    <li>
                        <strong>Expect</strong> — Declare behavioral contracts with <code>@expect</code>. These are the rules your outputs must follow.
                    </li>
                    <li>
                        <strong>Dataset</strong> — Organize your test prompts into YAML dataset contracts. Run them against your handler function.
                    </li>
                    <li>
                        <strong>Enforce</strong> — Add <code>phylax check</code> and <code>phylax dataset run</code> to your CI pipeline. Every push is tested. Every regression is caught.
                    </li>
                </ol>

                <h2>Why Not LLM-as-a-Judge?</h2>
                <p>
                    The most common objection is: &quot;Why not use GPT-4 to evaluate GPT-4&apos;s output?&quot;
                </p>
                <p>
                    Three reasons:
                </p>
                <ol>
                    <li><strong>Non-determinism</strong> — The judge model itself is non-deterministic. Run the same evaluation twice and you might get different scores. This makes CI unreliable.</li>
                    <li><strong>Latency</strong> — Each judge call adds 1-5 seconds of API latency. With 500 test cases, that&apos;s 40+ minutes of CI time.</li>
                    <li><strong>Cost</strong> — You&apos;re paying for two LLM calls per test: one to generate, one to judge. At scale, this compounds fast.</li>
                </ol>
                <p>
                    Deterministic rules run <strong>in memory</strong>, complete <strong>in milliseconds</strong>, and produce the <strong>same result every time</strong>. That&apos;s what makes them suitable for CI.
                </p>

                <h2>Start Today</h2>
                <p>
                    The entire Phylax framework is open source and installs in one command:
                </p>
                <pre className="bg-beige/30 rounded-xl p-4 text-sm overflow-x-auto border border-black/10">
                    {`pip install phylax[openai]`}
                </pre>
                <p>
                    Start with a single dataset contract for your most critical user flow. Add more cases as you discover edge cases. Enforce in CI. Stop testing AI with vibes.
                </p>
                <p>
                    <Link href="/docs/quickstart">Read the Quickstart →</Link>
                </p>

            </article>
            <Footer />
        </>
    );
}
