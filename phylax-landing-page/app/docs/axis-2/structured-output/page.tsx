import React from 'react';
import { CodeBlock } from '@/components/code-block';

const STRUCTURED_CODE = `from phylax import (
    SurfaceEvaluator,
    FieldExistsRule,
    TypeEnforcementRule,
    EnumEnforcementRule,
    StructuredSurfaceAdapter,
)

# 1. Define expectations
evaluator = SurfaceEvaluator()
evaluator.add_rule(FieldExistsRule("user.id"))
evaluator.add_rule(TypeEnforcementRule("user.id", "number"))
evaluator.add_rule(EnumEnforcementRule("user.role", ["admin", "editor"]))

# 2. Adapt the payload
adapter = StructuredSurfaceAdapter()
surface = adapter.adapt({"user": {"id": 123, "role": "admin"}})

# 3. Evaluate deterministically
verdict = evaluator.evaluate(surface)
print(verdict.passed)   # True`;

const NESTED_CODE = `# Deep nested paths use dot notation
evaluator.add_rule(FieldExistsRule("response.data.items"))
evaluator.add_rule(TypeEnforcementRule("response.status_code", "number"))
evaluator.add_rule(EnumEnforcementRule(
    "response.status",
    ["ok", "error", "pending"],
))`;

export default function StructuredOutputPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Structured Output</h1>
            <p className="text-xl text-coffee-bean/80">
                Strict, type-safe enforcement for JSON payloads. Zero coercion allowed.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Surface Evaluation</h2>
            <p className="text-coffee-bean/80 mb-4">
                The structured output surface validates any JSON-serializable Python dict. Rules fire deterministically against exact field paths.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong><code>FieldExistsRule(path)</code></strong> — Fails if the dot-notation path doesn&apos;t exist in the payload.</li>
                    <li><strong><code>TypeEnforcementRule(path, type)</code></strong> — Fails if the value at <code>path</code> is not the expected JSON type (<code>&quot;number&quot;</code>, <code>&quot;string&quot;</code>, <code>&quot;boolean&quot;</code>, <code>&quot;array&quot;</code>, <code>&quot;object&quot;</code>). No coercion.</li>
                    <li><strong><code>EnumEnforcementRule(path, values)</code></strong> — Fails if the value at <code>path</code> is not in the allowed set.</li>
                </ul>
            </div>

            <CodeBlock language="python" title="structured_output.py" code={STRUCTURED_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Nested Field Paths</h2>
            <CodeBlock language="python" title="nested_paths.py" code={NESTED_CODE} />
        </div>
    );
}
