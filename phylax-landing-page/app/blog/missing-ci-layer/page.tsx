import React from 'react';
import Link from 'next/link';
import { Footer } from '@/components/Footer';

export default function MissingCiLayer() {
    return (
        <>
            <article className="max-w-3xl mx-auto px-6 py-24 prose prose-slate prose-a:text-lime-cream hover:prose-a:text-lime-cream/80 prose-headings:text-coffee-bean prose-p:text-coffee-bean/80 prose-li:text-coffee-bean/80 prose-code:text-coffee-bean prose-code:bg-beige prose-code:px-1.5 prose-code:rounded-md prose-strong:text-coffee-bean">

                <Link href="/blog" className="text-sm font-medium text-coffee-bean/60 hover:text-lime-cream mb-12 inline-block no-underline">
                    &larr; Back to Blog
                </Link>

                <div className="mb-12">
                    <div className="flex items-center gap-3 mb-6">
                        <span className="text-lime-cream bg-coffee-bean/10 px-2 py-0.5 rounded text-sm font-medium no-underline">Infrastructure</span>
                        <span className="text-coffee-bean/50 text-sm">March 17, 2026</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-coffee-bean mb-6 leading-tight">
                        The Missing CI Layer for AI Systems
                    </h1>
                    <p className="text-xl text-coffee-bean/60">
                        Every serious software team has CI. Almost no AI team does. Here&apos;s the workflow that changes that.
                    </p>
                </div>

                <h2>The State of AI Infrastructure in 2026</h2>
                <p>
                    If you look at the modern AI stack, there&apos;s a conspicuous gap. Teams have invested heavily in <strong>prompt engineering</strong> (crafting the right instructions), <strong>RAG pipelines</strong> (feeding the right context), and <strong>observability</strong> (logging what happened). But almost nobody has invested in the layer that prevents regressions before deployment.
                </p>
                <p>
                    In traditional software, this layer is called <strong>Continuous Integration</strong>. It&apos;s the automated checkpoint that stands between a developer&apos;s code change and production. If tests fail, the code doesn&apos;t ship.
                </p>
                <p>
                    AI systems don&apos;t have this. When a developer modifies a system prompt, updates a model version, or adjusts a RAG pipeline — there is no automated gate that verifies the AI&apos;s behavior hasn&apos;t regressed. The change goes into production and you find out something broke when latency spikes or customers complain.
                </p>

                <h2>Why Monitoring Isn&apos;t Enough</h2>
                <p>
                    The industry&apos;s first answer to this problem was monitoring. Tools like LangWatch, Helicone, and Humanloop record every LLM call and let you browse them in dashboards. Some even run secondary LLMs over the results to produce quality scores.
                </p>
                <p>
                    Monitoring is valuable — but it&apos;s inherently <strong>reactive</strong>. By the time your dashboard shows a spike in &quot;low quality&quot; responses, your chatbot has already been hallucinating to customers for hours. The damage is done. The support tickets are filed. The trust is eroded.
                </p>
                <p>
                    What you need is a <strong>proactive</strong> layer — one that catches behavioral regressions <em>before</em> they reach production.
                </p>

                <h2>The Phylax Workflow</h2>
                <p>
                    Phylax introduces four primitives that mirror traditional CI concepts:
                </p>

                <h3>1. Trace — The Test Fixture</h3>
                <p>
                    Every LLM call is automatically recorded into an immutable trace containing the full input, full output, latency, token count, and execution context. This is your test artifact — the equivalent of a test fixture in pytest or JUnit.
                </p>
                <pre className="bg-beige/30 rounded-xl p-4 text-sm overflow-x-auto border border-black/10">
                    {`from phylax import trace, expect, OpenAIAdapter

@trace(provider="openai")
@expect(must_include=["refund_policy"], max_latency_ms=2000)
def handle_refund(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.generate(prompt=message)
    return response`}
                </pre>

                <h3>2. Dataset Contract — The Test Suite</h3>
                <p>
                    A YAML file defines dozens or hundreds of test cases with explicit expectations. This is your test suite — it runs deterministically and produces binary pass/fail results.
                </p>
                <pre className="bg-beige/30 rounded-xl p-4 text-sm overflow-x-auto border border-black/10">
                    {`dataset: support_bot
cases:
  - input: "I want a refund"
    expectations:
      must_include: ["refund_policy"]
      max_latency_ms: 3000

  - input: "Delete my account"
    expectations:
      must_not_include: ["internal_admin_url"]
      must_include: ["confirmation"]`}
                </pre>

                <h3>3. Golden Baseline — The Snapshot Test</h3>
                <p>
                    Mark a known-good trace as &quot;blessed.&quot; Future runs are hash-compared against this baseline. If the output changes — even slightly — the test fails. This is your snapshot test, catching unexpected drift.
                </p>
                <pre className="bg-beige/30 rounded-xl p-4 text-sm overflow-x-auto border border-black/10">
                    {`phylax bless trace-abc123    # mark as golden reference
phylax check                 # exits 1 if output hash changed`}
                </pre>

                <h3>4. CI Integration — The Pipeline Gate</h3>
                <p>
                    Add two lines to your GitHub Actions, GitLab CI, or Jenkins pipeline. Every push triggers behavioral validation. If any contract is violated, the PR is blocked. Exit code 0 = all pass. Exit code 1 = regression detected.
                </p>
                <pre className="bg-beige/30 rounded-xl p-4 text-sm overflow-x-auto border border-black/10">
                    {`# .github/workflows/phylax.yml
- run: phylax check
- run: phylax dataset run datasets/*.yaml`}
                </pre>

                <h2>What This Looks Like in Practice</h2>
                <p>
                    Consider a team building a customer support bot. They have 50 dataset contract cases covering refunds, password resets, billing inquiries, and edge cases. Every morning, their CI pipeline runs these 50 cases against the live model.
                </p>
                <p>
                    One Tuesday, OpenAI pushes a minor model update. The team&apos;s CI pipeline runs at 6 AM:
                </p>
                <pre className="bg-beige/30 rounded-xl p-4 text-sm overflow-x-auto border border-black/10">
                    {`$ phylax dataset run datasets/support_bot.yaml

[Case 12/50] "Cancel my subscription" ✗ FAIL
   Violation: must_include("confirmation")
   Expected: substring "confirmation"
   Actual: "Your subscription is now inactive."

❌ 1 of 50 cases failed. Exit code 1.`}
                </pre>
                <p>
                    The team discovers the regression at 6:01 AM — before any customer encounters it. They update the prompt to ensure the word &quot;confirmation&quot; appears in cancellation responses, push the fix, CI turns green, and the new code ships.
                </p>
                <p>
                    <strong>Total customer impact: zero.</strong>
                </p>

                <h2>The Broader Vision</h2>
                <p>
                    Today, monitoring tools tell you what happened. Phylax prevents it from happening. These aren&apos;t competitors — they&apos;re complementary layers. Use Helicone to log production calls for analytics. Use Phylax to enforce behavioral contracts in CI.
                </p>
                <p>
                    The missing CI layer for AI is here. <Link href="/docs/quickstart">Start enforcing contracts today →</Link>
                </p>

            </article>
            <Footer />
        </>
    );
}
