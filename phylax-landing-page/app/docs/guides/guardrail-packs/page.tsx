import React from 'react';
import { CodeBlock } from '@/components/code-block';

const PACK_CODE = `from phylax import safety_pack, quality_pack, apply_pack

# Load built-in packs
s_pack = safety_pack()
q_pack = quality_pack()

# Your custom business logic expectations
my_expectations = {
    "must_include": ["thank you for your order"],
    "must_not_include": ["competitor_brand_name"],
}

# Safely merge the guardrails into your existing config
merged_rules = apply_pack(s_pack, my_expectations)
merged_rules = apply_pack(q_pack, merged_rules)

# merged_rules now contains business logic + safety blacklist + quality constraints
# Ready for a dataset YAML or @expect decorator`;

const COMPLIANCE_CODE = `from phylax import compliance_pack

c_pack = compliance_pack()

# Blocks: financial advice, unauthorized medical diagnoses,
# legal recommendations without "consult a professional" disclaimer
rules = c_pack.to_expectations()
print(rules["must_not_include"])
# ["invest in", "diagnostic", "you should sue", ...]`;

export default function GuardrailPacksPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Guardrail Packs</h1>
            <p className="text-xl text-coffee-bean/80">
                Pre-configured expectation bundles for Safety, Quality, and Compliance — zero configuration required.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Built-in Domain Packs</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax provides zero-configuration requirement dictionaries for standard operational hazards. Load them via the Pack Registry, convert to dataset expectations, and safely merge with your custom rules.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong>Safety Pack:</strong> Asserts against PII (SSNs), toxicity, self-harm, and violent terminology via <code>must_not_include</code> blacklists.</li>
                    <li><strong>Quality Pack:</strong> Enforces <code>min_tokens</code> (prevents empty responses), <code>max_latency_ms</code>, and bans placeholders like &quot;TODO&quot; or &quot;insert text here&quot;.</li>
                    <li><strong>Compliance Pack:</strong> Blocks financial/legal advice terms and unauthorized medical diagnostic statements.</li>
                </ul>
            </div>

            <CodeBlock language="python" title="pack_usage.py" code={PACK_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Compliance Pack</h2>
            <CodeBlock language="python" title="compliance.py" code={COMPLIANCE_CODE} />
        </div>
    );
}
