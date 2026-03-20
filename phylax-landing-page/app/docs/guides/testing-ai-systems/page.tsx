import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
from phylax import trace, expect

# Level 1: Basic content checks
@trace(provider="openai")
@expect(must_include=["refund"])
def basic_support(msg): ...

# Level 2: Add safety guardrails
@trace(provider="openai")
@expect(
    must_include=["refund"],
    must_not_include=["internal_error", "SQL", "password"]
)
def safe_support(msg): ...

# Level 3: Add performance bounds
@trace(provider="openai")
@expect(
    must_include=["refund"],
    must_not_include=["internal_error"],
    max_latency_ms=2000,
    min_tokens=50
)
def production_support(msg): ...
`;

export default function TestingAiSystemsPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Testing AI Systems</h1>
      <p className="text-xl text-coffee-bean/80">A comprehensive guide to writing effective behavioral contracts for LLM-powered applications.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">The Mental Model</h2>
      <p className="text-coffee-bean/80 mb-4">Phylax treats AI testing like software testing: you don&apos;t test whether the LLM &quot;thinks&quot; correctly — you test whether its <strong>observable outputs</strong> meet declared contracts.</p>
      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-4">
        <div className="font-mono text-sm text-coffee-bean/80 space-y-1">
          <p>❌ &quot;Is the LLM output good?&quot; ← Subjective, non-deterministic</p>
          <p>✅ &quot;Does the output contain &apos;refund_policy&apos;?&quot; ← Deterministic, binary</p>
          <p>✅ &quot;Did it respond in under 2 seconds?&quot; ← Deterministic, binary</p>
          <p>✅ &quot;Did it call the correct tool?&quot; ← Deterministic, binary</p>
        </div>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">What to Test</h2>
      <ul className="space-y-3 text-coffee-bean/80 list-disc pl-6 marker:text-lime-cream">
        <li><strong>Content compliance:</strong> Required terms, forbidden content, safety keywords</li>
        <li><strong>Performance bounds:</strong> Latency ceilings, minimum response lengths</li>
        <li><strong>Structural output:</strong> JSON schema, required fields, type enforcement</li>
        <li><strong>Tool usage:</strong> Correct tools called, correct arguments, correct ordering</li>
        <li><strong>Behavioral stability:</strong> Output doesn&apos;t change between deployments</li>
      </ul>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Strategy: Start Simple, Layer Up</h2>
      <CodeBlock language="python" title="progressive_testing.py" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">When to Use Phylax</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Scenario</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Use Phylax?</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4">Production LLM app in CI/CD</td><td className="py-3 text-lime-cream">✅ Yes</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4">Multi-step agent pipeline</td><td className="py-3 text-lime-cream">✅ Yes</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4">Model upgrade validation</td><td className="py-3 text-lime-cream">✅ Yes</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4">Casual prompt experimentation</td><td className="py-3 text-fail-red">❌ Overkill</td></tr>
            <tr><td className="py-3 pr-4">Real-time monitoring</td><td className="py-3 text-fail-red">❌ Wrong tool</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
