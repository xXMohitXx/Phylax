import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
phylax/_internal/expectations/
├── __init__.py          # Public exports
├── evaluator.py         # Core rule evaluator
├── rules.py             # 4 base rules
├── composition.py       # Phase 1: AND/OR/NOT groups
├── conditionals.py      # Phase 2: Conditional activation
├── scoping.py           # Phase 3: Structural scoping
├── templates.py         # Phase 4: Reusable templates
└── documentation.py     # Phase 5: Auto-generated docs
`;
const CODE_BLOCK_1 = `
from phylax import MustIncludeRule, MustNotIncludeRule, MaxLatencyRule, MinTokensRule

MustIncludeRule("refund")      # Output must contain "refund"
MustNotIncludeRule("lawsuit")  # Output must NOT contain "lawsuit"
MaxLatencyRule(3000)           # Must respond within 3000ms
MinTokensRule(50)              # Must generate at least 50 tokens
`;
const CODE_BLOCK_2 = `
from phylax import AndGroup, OrGroup, NotGroup

# All must pass
AndGroup([MustIncludeRule("refund"), MaxLatencyRule(3000)])

# At least one must pass
OrGroup([MustIncludeRule("refund"), MustIncludeRule("return")])

# Inner rule must NOT pass (double negation)
NotGroup([MustNotIncludeRule("error")])
`;
const CODE_BLOCK_3 = `
from phylax import when, InputContains, ModelEquals

# Only enforce when input mentions billing
when(InputContains("billing"), then=MustIncludeRule("invoice"))

# Only enforce on GPT-4
when(ModelEquals("gpt-4"), then=MaxLatencyRule(2000))
`;
const CODE_BLOCK_4 = `
from phylax import for_node, for_provider, for_stage, for_tool

for_node("classifier", MustIncludeRule("intent"))
for_provider("openai", MaxLatencyRule(2000))
for_stage("validation", MustIncludeRule("approved"))
for_tool("fetch_db", MustIncludeRule("query"))
`;
const CODE_BLOCK_5 = `
from phylax import register_template, get_template_rules
from phylax import export_contract_markdown, ContractDocumenter

# Register reusable template
register_template("safety", rules=[
    MustNotIncludeRule("hate_speech"),
    MustNotIncludeRule("violence"),
])

# Auto-generate contract documentation
markdown = export_contract_markdown()
`;

export default function Axis1Page() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Axis 1 — Expectations Engine</h1>
      <p className="text-xl text-coffee-bean/80">The deterministic rule engine that produces binary PASS/FAIL verdicts. Built in 5 phases: base rules, composition, conditionals, scoping, and templates.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Architecture Overview</h2>
      <CodeBlock language="bash" title="Directory Structure" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 1: Base Rules</h2>
      <p className="text-coffee-bean/80 mb-4">Four atomic rules — each produces a deterministic binary verdict:</p>
      <CodeBlock language="python" title="Base Rules" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 2: Composition (Algebra)</h2>
      <CodeBlock language="python" title="Composition" code={CODE_BLOCK_2} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 3: Conditionals</h2>
      <CodeBlock language="python" title="Conditionals" code={CODE_BLOCK_3} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 4: Scoping</h2>
      <CodeBlock language="python" title="Scoping" code={CODE_BLOCK_4} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 5: Templates &amp; Documentation</h2>
      <CodeBlock language="python" title="Templates" code={CODE_BLOCK_5} />
    </div>
  );
}
