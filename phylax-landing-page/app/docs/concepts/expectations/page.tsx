import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
from phylax import trace, expect

@trace(provider="openai")
@expect(
    must_include=["refund"],
    must_not_include=["sorry"],
    max_latency_ms=1500,
    min_tokens=10
)
def customer_support(query):
    return llm.generate(query)
`;
const CODE_BLOCK_1 = `
from phylax import (
    trace, expect,
    AndGroup, OrGroup, NotGroup,
    MustIncludeRule, MaxLatencyRule, MustNotIncludeRule, MinTokensRule
)

@trace(provider="openai")
@expect(rules=AndGroup([
    MustIncludeRule("refund"),
    OrGroup([
        MaxLatencyRule(3000),
        MustIncludeRule("processing"),
    ]),
    NotGroup([
        MustNotIncludeRule("internal_error"),
    ]),
]))
def handle(message):
    ...
`;
const CODE_BLOCK_2 = `
from phylax import (
    trace, expect, when,
    InputContains, ModelEquals, ProviderEquals, FlagSet,
    MustIncludeRule, MaxLatencyRule,
)

@trace(provider="openai")
@expect(rules=when(
    InputContains("billing"),
    then=MustIncludeRule("invoice"),
))
def support(message):
    ...

# Conditions: InputContains, ModelEquals, ProviderEquals,
#             MetadataEquals, FlagSet
`;
const CODE_BLOCK_3 = `
from phylax import (
    for_node, for_provider, for_stage, for_tool, scoped,
    MustIncludeRule, MaxLatencyRule,
)

# Apply only to a specific node in the DAG
scoped_rule = for_node("classifier", MustIncludeRule("intent"))

# Apply only when using a specific provider
provider_rule = for_provider("openai", MaxLatencyRule(2000))

# Apply at a specific stage
stage_rule = for_stage("validation", MustIncludeRule("approved"))
`;
const CODE_BLOCK_4 = `
from phylax import (
    register_template, get_template, get_template_rules,
    MustIncludeRule, MustNotIncludeRule, MaxLatencyRule,
)

# Register a reusable template
register_template(
    name="customer_support",
    rules=[
        MustIncludeRule("thank"),
        MustNotIncludeRule("sorry"),
        MaxLatencyRule(2000),
    ],
    description="Standard customer support expectations"
)

# Use it anywhere
rules = get_template_rules("customer_support")
`;
const CODE_BLOCK_5 = `
from phylax import (
    describe_rule, describe_template,
    list_contracts, export_contract_markdown, ContractDocumenter,
)

# Describe a single rule
desc = describe_rule(MustIncludeRule("refund"))

# Export all contracts as Markdown
markdown = export_contract_markdown()

# Use the ContractDocumenter for full reports
doc = ContractDocumenter()
report = doc.generate()
`;

export default function ExpectationsPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Expectations</h1>
      <p className="text-xl text-coffee-bean/80">
        Expectations are deterministic rules that produce binary PASS/FAIL verdicts on LLM outputs. They are the core enforcement mechanism — no AI scoring, no probabilities, no ambiguity.
      </p>
      
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Built-in Rules</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-black/10">
              <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Rule</th>
              <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">What It Enforces</th>
              <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Severity</th>
              <th className="text-left py-3 font-semibold text-coffee-bean">Example</th>
            </tr>
          </thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5">
              <td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-sm">must_include</code></td>
              <td className="py-3 pr-4">Response must contain all listed substrings</td>
              <td className="py-3 pr-4">LOW</td>
              <td className="py-3"><code className="text-xs">[&quot;refund&quot;, &quot;policy&quot;]</code></td>
            </tr>
            <tr className="border-b border-black/5">
              <td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-sm">must_not_include</code></td>
              <td className="py-3 pr-4">Response must NOT contain any listed substrings</td>
              <td className="py-3 pr-4">HIGH</td>
              <td className="py-3"><code className="text-xs">[&quot;lawsuit&quot;, &quot;attorney&quot;]</code></td>
            </tr>
            <tr className="border-b border-black/5">
              <td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-sm">max_latency_ms</code></td>
              <td className="py-3 pr-4">Response must complete within time limit</td>
              <td className="py-3 pr-4">MEDIUM</td>
              <td className="py-3"><code className="text-xs">3000</code> (3 seconds)</td>
            </tr>
            <tr>
              <td className="py-3 pr-4"><code className="px-1.5 py-0.5 rounded bg-beige text-sm">min_tokens</code></td>
              <td className="py-3 pr-4">Response must be at least N tokens long</td>
              <td className="py-3 pr-4">LOW</td>
              <td className="py-3"><code className="text-xs">50</code></td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Basic Usage</h2>
      <CodeBlock language="python" title="expectations.py" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Expectation Algebra (Composition)</h2>
      <p className="text-coffee-bean/80 mb-4">
        Combine rules with logical operators for complex validation logic:
      </p>
      <CodeBlock language="python" title="composition.py" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Conditional Expectations</h2>
      <p className="text-coffee-bean/80 mb-4">
        Apply expectations only when certain conditions are met:
      </p>
      <CodeBlock language="python" title="conditionals.py" code={CODE_BLOCK_2} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Scoped Expectations</h2>
      <p className="text-coffee-bean/80 mb-4">
        Scope expectations to specific nodes, providers, stages, or tools in an execution graph:
      </p>
      <CodeBlock language="python" title="scoping.py" code={CODE_BLOCK_3} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Expectation Templates</h2>
      <p className="text-coffee-bean/80 mb-4">
        Register reusable expectation templates for common patterns:
      </p>
      <CodeBlock language="python" title="templates.py" code={CODE_BLOCK_4} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Contract Documentation</h2>
      <p className="text-coffee-bean/80 mb-4">
        Auto-generate documentation for your expectation contracts:
      </p>
      <CodeBlock language="python" title="documentation.py" code={CODE_BLOCK_5} />
    </div>
  );
}
