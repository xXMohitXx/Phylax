import React from 'react';
import { CodeBlock } from '@/components/code-block';

const YAML_CODE = `dataset: support_bot
cases:
  - input: "I want a refund"
    name: "refund_request_01"
    expectations:
      must_include: ["refund", "process"]
      min_tokens: 15

  - input: "My package is late, I am going to sue you!"
    name: "angry_customer_01"
    expectations:
      must_not_include: ["lawsuit", "legal"]
      max_latency_ms: 3000`;

const PYTHON_CODE = `from phylax import load_dataset, run_dataset, format_report

# 1. Load the declarative contracts
dataset = load_dataset("support_bot.yaml")

# 2. Define your LLM wrapper
def generate_response(prompt: str) -> str:
    return my_llm_client.chat(prompt)

# 3. Execute the suite
result = run_dataset(dataset, generate_response)

# 4. Human-readable CLI report
print(format_report(result))

if not result.all_passed:
    exit(1)`;

export default function DatasetContractsPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Dataset Contracts</h1>
            <p className="text-xl text-coffee-bean/80">
                Declarative YAML test cases for bulk evaluating LLM outputs against strict expectations.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The YAML Schema</h2>
            <p className="text-coffee-bean/80 mb-4">
                Rather than writing a hundred Python unit tests, construct one YAML dataset where each case declares an <code>input</code> and its specific <code>expectations</code>.
            </p>

            <CodeBlock language="yaml" title="support_bot.yaml" code={YAML_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Executing Datasets</h2>
            <p className="text-coffee-bean/80 mb-4">
                Load the YAML with <code>load_dataset()</code> and execute it against your model function with <code>run_dataset()</code>. Phylax handles parallelization, error catching, and strict evaluation.
            </p>

            <CodeBlock language="python" title="evaluate.py" code={PYTHON_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Result Artifacts</h3>
                <p className="text-coffee-bean/80">
                    The <code>DatasetResult</code> object contains exact counts of <code>passed_cases</code> and <code>failed_cases</code>, along with individual <code>CaseResult</code> objects holding the exact violation strings. Ideal for CI automation.
                </p>
            </div>
        </div>
    );
}
