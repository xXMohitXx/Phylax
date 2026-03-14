import React from 'react';
import Link from 'next/link';
import { CodeBlock } from '@/components/code-block';
import { Footer } from '@/components/Footer';

export default function SupportBotExample() {
  return (
    <>
      <div className="max-w-5xl mx-auto px-6 py-16">
        <Link href="/examples" className="text-sm font-medium text-coffee-bean/60 hover:text-lime-cream mb-8 inline-block">
          &larr; Back to Examples
        </Link>

        <div className="mb-12">
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-coffee-bean mb-4">
            Support Bot Testing
          </h1>
          <p className="text-lg text-coffee-bean/70">
            How to isolate and test a customer support agent that utilizes internal tools and policies.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          
          <div className="space-y-8">
            <div>
              <h3 className="text-xl font-bold text-coffee-bean mb-2">1. Define the Dataset Contract</h3>
              <p className="text-sm text-coffee-bean/70">
                We define a YAML contract containing the explicit behaviors we expect. In this case, 
                if a user asks for a refund, the bot MUST include specific policy terminology and 
                respond within 3 seconds.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-bold text-coffee-bean mb-2">2. Instrument the Code</h3>
              <p className="text-sm text-coffee-bean/70">
                We wrap our existing Python agent handler in the <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">@trace</code> decorator so Phylax 
                can intercept the I/O for CI comparison.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-bold text-coffee-bean mb-2">3. Run CI Enforcement</h3>
              <p className="text-sm text-coffee-bean/70">
                We trigger the dataset execution in our GitHub Action. Phylax maps the YAML cases to 
                the Python trace hooks.
              </p>
            </div>
          </div>

          <div className="space-y-6">
            <CodeBlock 
              title="datasets/support_bot.yaml"
              language="yaml"
              code={`dataset: support_bot
cases:
  - input: "I want a refund for my last purchase"
    expectations:
      must_include: ["refund_policy", "30_days"]
      max_latency_ms: 3000
  - input: "How do I reset my password?"
    expectations:
      must_not_include: ["credit_card", "SQL"]`}
            />

            <CodeBlock 
              title="agent.py"
              language="python"
              code={`from phylax import trace, expect, OpenAIAdapter

@trace(provider="openai")
@expect(must_include=["refund_policy"])
def handle_support_query(prompt: str):
    adapter = OpenAIAdapter()
    response, _ = adapter.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response`}
            />

            <CodeBlock 
              title="Terminal (CI environment)"
              language="bash"
              code={`$ phylax dataset run datasets/support_bot.yaml

Running dataset 'support_bot'...
[Case 1/2] "I want a refund..."
  ✓ must_include: ['refund_policy', '30_days']
  ✓ max_latency_ms: 3000 (Actual: 1204ms)
[Case 2/2] "How do I reset..."
  ✓ must_not_include: ['credit_card', 'SQL']

✓ All expectations passed. Exit code 0.`}
            />
          </div>

        </div>
      </div>
      <Footer />
    </>
  );
}
