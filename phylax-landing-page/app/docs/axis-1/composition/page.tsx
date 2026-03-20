import React from 'react';
import { CodeBlock } from '@/components/code-block';

const COMPOSITION_CODE = `from phylax.expectations import (
    AndGroup,
    OrGroup,
    NotGroup,
    MustIncludeRule,
    MaxLatencyRule,
)

# 1. AND Group (default) — ALL inner rules must pass
strict_rules = AndGroup([
    MustIncludeRule(["hello"]),
    MaxLatencyRule(2000),
])

# 2. OR Group — at least ONE inner rule must pass
fallback_rules = OrGroup([
    MustIncludeRule(["refund"]),
    MustIncludeRule(["policy"]),
])

# 3. NOT Group — the inner rule must FAIL for the group to pass
safety_rule = NotGroup(MustIncludeRule(["error"]))`;

const NESTED_CODE = `complex_rule = AndGroup([
    # Must be fast
    MaxLatencyRule(2000),

    # AND must contain either 'confirmed' or 'completed'
    OrGroup([
        MustIncludeRule(["confirmed"]),
        MustIncludeRule(["completed"]),
    ]),

    # AND must NOT contain 'error'
    NotGroup(MustIncludeRule(["error"])),
])`;

const EXPECT_CODE = `from phylax import trace, expect

@expect(rules=complex_rule)
@trace(provider="openai")
def ai_handler(query):
    ...`;

export default function CompositionPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Composition</h1>
            <p className="text-xl text-coffee-bean/80">
                Combine multiple expectations using standard boolean logic: AND, OR, NOT.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Logical Groups</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax provides three logical grouping constructs that evaluate to a strictly binary PASS/FAIL verdict — no partial scoring.
            </p>

            <CodeBlock language="python" title="composition_example.py" code={COMPOSITION_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Nested Composition</h2>
            <p className="text-coffee-bean/80 mb-4">
                Arbitrarily nest logical groups to create robust AI behavioral contracts.
            </p>

            <CodeBlock language="python" title="nested.py" code={NESTED_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Usage with @expect</h3>
                <p className="text-coffee-bean/80 mb-3">
                    Pass composed groups directly into the <code className="px-1.5 py-0.5 rounded-md bg-white text-coffee-bean">rules=</code> parameter.
                </p>
                <CodeBlock language="python" title="" code={EXPECT_CODE} />
            </div>
        </div>
    );
}
