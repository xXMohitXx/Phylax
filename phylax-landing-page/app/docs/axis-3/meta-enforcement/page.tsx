import React from 'react';
import { CodeBlock } from '@/components/code-block';

const META_CODE = `from phylax import (
    MinExpectationCountRule,
    ZeroSignalRule,
    DefinitionChangeGuard,
    ExpectationRemovalGuard,
    compute_definition_hash,
)

# Guard 1: Detect silent test deletion
guard = ExpectationRemovalGuard()
res = guard.evaluate(
    previous_ids={"exp-1", "exp-2", "exp-3"},
    current_ids={"exp-1", "exp-2"},   # exp-3 was silently removed
)
print(res.passed)   # False

# Guard 2: Detect threshold relaxation (hash of config changed)
h_before = compute_definition_hash({"rule": "must_include", "substrings": ["refund"]})
h_after  = compute_definition_hash({"rule": "must_include", "substrings": ["help"]})

change_guard = DefinitionChangeGuard()
res2 = change_guard.evaluate(h_before, h_after)
print(res2.passed)  # False — hash mismatch

# Guard 3: Fail if a test has literally NEVER failed (zero signal)
zero = ZeroSignalRule()
res3 = zero.evaluate(never_failed=True)
print(res3.passed)  # False — trivially passing test, no signal

# Guard 4: Minimum expectation count
count_rule = MinExpectationCountRule(5)
res4 = count_rule.evaluate(3)   # Only 3 declared
print(res4.passed)  # False`;

export default function MetaEnforcementPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Meta-Enforcement</h1>
            <p className="text-xl text-coffee-bean/80">
                Rules that govern the rules. Prevent developers from silently deleting test coverage to bypass CI gates.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Safeguarding the Trust Contract</h2>
            <p className="text-coffee-bean/80 mb-4">
                An enforcement gate is worthless if a developer can simply comment out the <code>@expect</code> decorator when it starts failing their PR. Meta-enforcement treats your evaluation suite itself as a surface that must pass checks.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong><code>MinExpectationCountRule(N)</code></strong> — <code>rule.evaluate(count)</code>: Fails if fewer than N expectations exist.</li>
                    <li><strong><code>ZeroSignalRule()</code></strong> — <code>rule.evaluate(never_failed=True/False)</code>: Fails when an expectation has never failed — it&apos;s trivially passing and produces no signal.</li>
                    <li><strong><code>DefinitionChangeGuard()</code></strong> — <code>guard.evaluate(hash_before, hash_after)</code>: Fails if an expectation&apos;s definition hash changed between runs (prevents stealth threshold relaxation).</li>
                    <li><strong><code>ExpectationRemovalGuard()</code></strong> — <code>guard.evaluate(previous_ids=set(), current_ids=set())</code>: Fails if any expectation disappeared from the suite.</li>
                </ul>
            </div>

            <CodeBlock language="python" title="meta_suite.py" code={META_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Purely Mathematical</h2>
            <p className="text-coffee-bean/80 mb-4">
                Meta-enforcement applies only strict logical criteria. <code>ZeroSignalRule</code> does not assess &quot;complexity&quot; or &quot;usefulness&quot; — it only checks: <code>if never_failed == True: fail()</code>. No judgment, no semantics.
            </p>
        </div>
    );
}
