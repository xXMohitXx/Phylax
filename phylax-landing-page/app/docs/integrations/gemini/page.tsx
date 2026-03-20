import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
from phylax import GeminiAdapter

adapter = GeminiAdapter()  # Uses GOOGLE_API_KEY env var

response, trace = adapter.generate(
    prompt="Hello!",
    model="gemini-2.5-flash"
)
`;
const CODE_BLOCK_1 = `
from phylax import trace, expect, GeminiAdapter

@trace(provider="gemini")
@expect(must_include=["hello"], max_latency_ms=5000)
def greet(name):
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=f"Say hello to {name}",
        model="gemini-2.5-flash",
    )
    return response
`;

export default function GeminiPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Google Gemini Integration</h1>
      <p className="text-xl text-coffee-bean/80">Connect Phylax to Google&apos;s Gemini models using the <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">google-genai</code> SDK.</p>
      <hr className="my-6 border-black/10" />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Installation</h2>
      <CodeBlock language="bash" title="Terminal" code={`pip install phylax[google]`} />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Environment</h2>
      <CodeBlock language="bash" title="Environment Variable" code={`export GOOGLE_API_KEY="AIza..."`} />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Usage</h2>
      <CodeBlock language="python" title="gemini_usage.py" code={CODE_BLOCK_0} />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">With Expectations</h2>
      <CodeBlock language="python" title="gemini_traced.py" code={CODE_BLOCK_1} />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Supported Models</h2>
      <div className="overflow-x-auto"><table className="w-full text-sm border-collapse">
        <thead><tr className="border-b border-black/10"><th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Model</th><th className="text-left py-3 font-semibold text-coffee-bean">Notes</th></tr></thead>
        <tbody className="text-coffee-bean/80">
          <tr className="border-b border-black/5"><td className="py-3 pr-4">gemini-2.5-flash</td><td className="py-3">Fast, recommended for most use cases</td></tr>
          <tr><td className="py-3 pr-4">gemini-2.5-pro</td><td className="py-3">Highest quality, longer responses</td></tr>
        </tbody>
      </table></div>
      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-4 mt-4">
        <p className="text-coffee-bean/80 text-sm"><strong>Note:</strong> Requires <code className="px-1 py-0.5 rounded bg-porcelain text-xs">google-genai</code> SDK v0.5.0+</p>
      </div>
    </div>
  );
}
