import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function OpenAIPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">OpenAI Integration</h1>
      <p className="text-xl text-coffee-bean/80">Connect Phylax to OpenAI&apos;s GPT models for traced, contract-enforced completions.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Installation</h2>
      <CodeBlock language="bash" title="Terminal" code={`pip install phylax[openai]`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Environment</h2>
      <CodeBlock language="bash" title="Environment Variable" code={`export OPENAI_API_KEY="sk-..."`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Basic Usage</h2>
      <CodeBlock language="python" title="openai_usage.py" code={`from phylax import OpenAIAdapter

adapter = OpenAIAdapter()  # Uses OPENAI_API_KEY env var

# Chat completion (standard)
response, trace = adapter.chat_completion(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=256,
)

# Simple prompt
response, trace = adapter.generate(
    prompt="Say hello!",
    model="gpt-4"
)`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">With Expectations</h2>
      <CodeBlock language="python" title="openai_traced.py" code={`from phylax import trace, expect, OpenAIAdapter

@trace(provider="openai")
@expect(must_include=["refund"], max_latency_ms=3000)
def handle_refund(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": message}]
    )
    return response`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Supported Models</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Model</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Notes</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4">gpt-4o</td><td className="py-3">Latest, recommended</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4">gpt-4-turbo</td><td className="py-3">128k context</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4">gpt-4</td><td className="py-3">Stable baseline</td></tr>
            <tr><td className="py-3 pr-4">gpt-3.5-turbo</td><td className="py-3">Fast, cost-effective</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
