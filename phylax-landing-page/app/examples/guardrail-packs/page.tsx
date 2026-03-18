import React from 'react';
import Link from 'next/link';
import { CodeBlock } from '@/components/code-block';
import { Footer } from '@/components/Footer';

export default function GuardrailPacksExample() {
    return (
        <>
            <div className="max-w-5xl mx-auto px-6 py-16">
                <Link href="/examples" className="text-sm font-medium text-coffee-bean/60 hover:text-lime-cream mb-8 inline-block">
                    &larr; Back to Examples
                </Link>

                <div className="mb-12">
                    <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-coffee-bean mb-4">
                        Guardrail Packs
                    </h1>
                    <p className="text-lg text-coffee-bean/70">
                        Apply pre-built, domain-specific guardrail packs to enforce content policies — PII detection, security, financial compliance, and healthcare regulations.
                    </p>
                </div>

                <div className="grid lg:grid-cols-2 gap-12 items-start">

                    <div className="space-y-8">
                        <div>
                            <h3 className="text-xl font-bold text-coffee-bean mb-2">Available Packs</h3>
                            <div className="space-y-4 text-sm text-coffee-bean/70">
                                <div>
                                    <p className="font-semibold text-coffee-bean">Safety Pack</p>
                                    <p>Blocks hate speech, PII leaks, jailbreak compliance, and harmful content.</p>
                                </div>
                                <div>
                                    <p className="font-semibold text-coffee-bean">Quality Pack</p>
                                    <p>Enforces minimum response length, latency limits, and blocks placeholder text.</p>
                                </div>
                                <div>
                                    <p className="font-semibold text-coffee-bean">PII Pack</p>
                                    <p>Detects and blocks SSN, credit card numbers, phone numbers, email addresses, and dates of birth.</p>
                                </div>
                                <div>
                                    <p className="font-semibold text-coffee-bean">Security Pack</p>
                                    <p>Blocks jailbreaks, system prompt disclosure, credential leaks, and code injection patterns.</p>
                                </div>
                                <div>
                                    <p className="font-semibold text-coffee-bean">Finance Pack</p>
                                    <p>Blocks unauthorized investment advice, tax advice, insurance recommendations, and profit guarantees.</p>
                                </div>
                                <div>
                                    <p className="font-semibold text-coffee-bean">Healthcare Pack</p>
                                    <p>Blocks medical diagnosis, medication advice, treatment plans, and patient health information disclosure.</p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 className="text-xl font-bold text-coffee-bean mb-2">Community Packs</h3>
                            <p className="text-sm text-coffee-bean/70">
                                Create and register your own guardrail packs using <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">register_pack()</code>.
                                Share them with the community via pull requests.
                            </p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <CodeBlock
                            title="guardrails.py"
                            language="python"
                            code={`from phylax import (
    safety_pack, quality_pack, apply_pack,
    trace, expect,
)
from phylax_guardrails import (
    pii_pack, security_pack,
    finance_pack, healthcare_pack,
)

# Built-in packs
safety = safety_pack()     # 5 rules
quality = quality_pack()   # 3 rules

# Domain-specific packs
pii = pii_pack()           # 6 rules
security = security_pack() # 4 rules
finance = finance_pack()   # 4 rules
health = healthcare_pack() # 4 rules

# Combine packs into expectations
rules = safety.to_expectations()
rules = apply_pack(quality, rules)
rules = apply_pack(pii, rules)

# Apply to your handler
@trace(provider="openai")
@expect(**rules)
def handle_customer_query(message: str):
    ...  # your LLM call`}
                        />

                        <CodeBlock
                            title="custom_pack.py"
                            language="python"
                            code={`from phylax._internal.guardrails.packs import (
    GuardrailPack, GuardrailRule,
)
from phylax_guardrails import register_pack

# Create a custom pack
def legal_pack():
    return GuardrailPack(
        name="legal",
        description="Legal industry guardrails",
        rules=[
            GuardrailRule(
                name="no_legal_advice",
                type="must_not_include",
                value=["this is legal advice",
                       "you should sue"],
                severity="high",
            ),
        ],
    )

# Register it globally
register_pack("legal", legal_pack)`}
                        />

                        <CodeBlock
                            title="Terminal"
                            language="bash"
                            code={`$ python -c "from phylax._internal.guardrails.packs import list_packs; print(list_packs())"

['safety', 'quality', 'compliance', 'pii', 'security', 'finance', 'healthcare']`}
                        />
                    </div>

                </div>
            </div>
            <Footer />
        </>
    );
}
