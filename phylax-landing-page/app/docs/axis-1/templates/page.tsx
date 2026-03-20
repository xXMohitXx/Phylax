import React from 'react';
import { CodeBlock } from '@/components/code-block';

const BUILTIN_CODE = `from phylax.expectations import Evaluator

evaluator = Evaluator()

# Phylax ships with built-in templates
evaluator.use_template("latency-standard")  # MaxLatencyRule(3000)
evaluator.use_template("safe-response")     # Blocks "I cannot help" phrases`;

const CUSTOM_CODE = `from phylax.expectations import (
    ExpectationTemplate,
    MaxLatencyRule,
    MustIncludeRule,
    get_registry,
)

custom_template = ExpectationTemplate(
    name="api-response",
    description="Standard API response requirements",
    rules=[
        MaxLatencyRule(1500),
        MustIncludeRule(["data", "status"]),
    ],
    version="1.0.0",
)

# Register globally (typically in a startup or conftest.py)
registry = get_registry()
registry.register(custom_template)`;

const USE_CODE = `evaluator = Evaluator()
evaluator.use_template("api-response")  # pulls in both rules above`;

export default function TemplatesPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Templates</h1>
            <p className="text-xl text-coffee-bean/80">
                Reusable expectation contracts. Write your rules once, apply them everywhere.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Using Built-in Templates</h2>
            <p className="text-coffee-bean/80 mb-4">
                Templates are static macros that bundle multiple rules into a single named unit. Phylax ships with a small set of built-in templates to get you started.
            </p>

            <CodeBlock language="python" title="template_usage.py" code={BUILTIN_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Creating Custom Templates</h2>
            <p className="text-coffee-bean/80 mb-4">
                Most teams define their own templates corresponding to internal safety or brand guidelines. Register them once, reference them by name everywhere.
            </p>

            <CodeBlock language="python" title="custom_templates.py" code={CUSTOM_CODE} />

            <p className="text-coffee-bean/80 mt-6 mb-4">
                Now any evaluator anywhere in the codebase can use <code>&quot;api-response&quot;</code>:
            </p>

            <CodeBlock language="python" title="reuse.py" code={USE_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Static Macros Only</h3>
                <p className="text-coffee-bean/80">
                    Templates are completely static. When invoked, they simply unpack their defined rules into the calling Evaluator. There is no runtime context adaptation inside the template definition itself.
                </p>
            </div>
        </div>
    );
}
