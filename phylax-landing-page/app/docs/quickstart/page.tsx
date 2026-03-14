import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function QuickstartPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Quickstart</h1>
      <p className="text-xl text-coffee-bean/80">
        From zero to CI enforcement in 10 minutes. This guide walks you through installing Phylax, creating your first trace, writing expectations, blessing a golden baseline, and running CI checks.
      </p>
      
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">1. Install Phylax</h2>
      <CodeBlock language="bash" title="Terminal" code={`# Install with all providers
pip install phylax[all]

# Or install specific providers
pip install phylax[openai]    # OpenAI only
pip install phylax[google]    # Google Gemini only
pip install phylax[groq]      # Groq only`} />

      <p className="text-coffee-bean/80 mt-4">Set your API key:</p>
      <CodeBlock language="bash" title="Environment" code={`# Windows PowerShell
$env:OPENAI_API_KEY = "your-key"

# Linux/Mac
export OPENAI_API_KEY="your-key"`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">2. Create Your First Trace</h2>
      <p className="text-coffee-bean/80 mb-4">
        The <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">@trace</code> decorator wraps any function that calls an LLM. Phylax records the full input, output, latency, and token count for every call.
      </p>
      <CodeBlock language="python" title="myapp.py" highlightedLines={[3, 4]} code={`from phylax import trace, expect, OpenAIAdapter

@trace(provider="openai")
@expect(must_include=["hello", "hi"], max_latency_ms=5000)
def greet(name):
    """Traced OpenAI call with expectations."""
    adapter = OpenAIAdapter()
    response, _ = adapter.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Say hello to {name}"}]
    )
    return response

# Run it
if __name__ == "__main__":
    result = greet("World")
    print(f"Response: {result}")`} />

      <p className="text-coffee-bean/80 mt-4">Run it:</p>
      <CodeBlock language="bash" title="Terminal" code={`python myapp.py`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">3. Start the Server &amp; UI</h2>
      <p className="text-coffee-bean/80 mb-4">
        Phylax includes a built-in web UI for inspecting traces, viewing execution graphs, and managing golden baselines:
      </p>
      <CodeBlock language="bash" title="Terminal" code={`phylax server
# Open http://127.0.0.1:8000/ui`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">4. Use Execution Context</h2>
      <p className="text-coffee-bean/80 mb-4">
        Group related calls into an execution graph. Phylax automatically tracks parent-child relationships between nested traced calls:
      </p>
      <CodeBlock language="python" title="multi_step.py" code={`from phylax import trace, expect, execution, OpenAIAdapter

@trace(provider="openai")
@expect(must_include=["intent"])
def classify(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Classify: {message}"}]
    )
    return response

@trace(provider="openai")
@expect(must_include=["refund"])
def handle_refund(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": message}]
    )
    return response

# Both traces share the same execution_id
with execution() as exec_id:
    intent = classify("I want a refund")
    response = handle_refund("Process refund for order #123")`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">5. Bless a Golden Baseline</h2>
      <p className="text-coffee-bean/80 mb-4">
        When an output looks correct, bless it as a golden reference. Future runs hash-compare against this baseline:
      </p>
      <CodeBlock language="bash" title="Terminal" code={`# From CLI
phylax bless <trace_id> --yes

# Or from the Web UI — click ⭐ Bless as Golden`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">6. Run CI Check</h2>
      <CodeBlock language="bash" title="Terminal" code={`phylax check
# Exit 0 → All goldens pass ✅
# Exit 1 → Regression detected ❌`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">7. Add to GitHub Actions</h2>
      <CodeBlock language="yaml" title=".github/workflows/phylax.yml" code={`name: Phylax CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install phylax[all]
      - run: phylax check
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">8. Dataset Contracts (v1.6.0+)</h2>
      <p className="text-coffee-bean/80 mb-4">Batch-test LLM behavior with YAML-defined contracts:</p>
      <CodeBlock language="python" title="dataset_test.py" code={`from phylax import Dataset, DatasetCase, run_dataset, format_report

ds = Dataset(dataset="my_bot", cases=[
    DatasetCase(
        input="help with refund",
        expectations={"must_include": ["refund"], "min_tokens": 10},
    ),
])

result = run_dataset(ds, my_handler)
print(format_report(result))`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">9. Guardrail Packs (v1.6.0+)</h2>
      <CodeBlock language="python" title="guardrails.py" code={`from phylax import safety_pack, quality_pack

safety = safety_pack()   # Blocks hate speech, PII, harmful content
quality = quality_pack()  # Min response length, latency ceiling

# Use with dataset contracts
expectations = safety.to_expectations()`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">10. Model Upgrade Simulation (v1.6.0+)</h2>
      <CodeBlock language="python" title="simulation.py" code={`from phylax import simulate_upgrade, format_simulation_report

sim = simulate_upgrade(
    dataset=ds,
    baseline_func=gpt4_handler,
    candidate_func=gpt45_handler,
    baseline_name="GPT-4",
    candidate_name="GPT-4.5",
)

if sim.safe_to_upgrade:
    print("✅ Safe to deploy!")
print(format_simulation_report(sim))`} />

      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-8">
        <h3 className="text-lg font-semibold text-coffee-bean mb-2">✅ You now have:</h3>
        <ul className="space-y-2 text-coffee-bean/80">
          <li>✓ LLM call tracing</li>
          <li>✓ Expectation validation</li>
          <li>✓ Execution context grouping</li>
          <li>✓ Golden baseline comparison</li>
          <li>✓ CI regression gate</li>
          <li>✓ Web UI for failure visualization</li>
          <li>✓ Dataset contract batch testing</li>
          <li>✓ Model upgrade simulation</li>
        </ul>
      </div>
    </div>
  );
}
