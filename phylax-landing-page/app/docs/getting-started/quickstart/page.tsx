import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CI_YAML = `
name: Phylax Check
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
          GOOGLE_API_KEY: \${{ secrets.GOOGLE_API_KEY }}
`;

const TRACE_CODE = `
from phylax import trace, expect, GeminiAdapter
import os

os.environ["GOOGLE_API_KEY"] = "your-api-key"

@trace(provider="gemini")
@expect(must_include=["hello", "hi"], max_latency_ms=5000)
def greet(name):
    """Traced Gemini call with expectations."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=f"Say hello to {name} in a friendly way.",
        model="gemini-2.5-flash",
    )
    return response

if __name__ == "__main__":
    result = greet("World")
    print(f"Response: {result.text}")
`;

export default function QuickstartPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Quickstart</h1>
            <p className="text-xl text-coffee-bean/80">
                From zero to CI enforcement in 10 minutes.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">1. Start the Server</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax includes a built-in UI to view traces, expectations, and graph executions. Run this in a background terminal.
            </p>
            <CodeBlock language="bash" title="Terminal" code={`phylax server\n# Open http://127.0.0.1:8000/ui`} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">2. Create Your First Trace</h2>
            <p className="text-coffee-bean/80 mb-4">
                The <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">@trace</code> decorator wraps any function that calls an LLM. Phylax automatically intercepts it.
            </p>
            <CodeBlock language="python" title="myapp.py" code={TRACE_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">3. Bless a Golden Baseline</h2>
            <p className="text-coffee-bean/80 mb-4">
                Run your script. If it passes the rules, optionally bless it as a golden baseline for cross-run stability.
            </p>
            <CodeBlock language="bash" title="Terminal" code={`# Option A: Bless via CLI\nphylax bless <trace_id> --yes\n\n# Option B: Bless via Web UI\n# Go to http://127.0.0.1:8000/ui and click "⭐ Bless as Golden"`} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">4. Run the CI Check</h2>
            <p className="text-coffee-bean/80 mb-4">
                Run the exact command below in your CI/CD pipeline.
            </p>
            <CodeBlock language="bash" title="Terminal" code={`phylax check\n\n# Exit 0 → All goldens pass ✅\n# Exit 1 → Regression detected ❌`} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">5. Add to GitHub Actions</h2>
            <CodeBlock language="yaml" title=".github/workflows/phylax.yml" code={CI_YAML} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-8">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">🎉 You now have:</h3>
                <ul className="space-y-2 text-coffee-bean/80">
                    <li>✓ LLM call tracing</li>
                    <li>✓ Expectation validation</li>
                    <li>✓ Golden baseline comparison</li>
                    <li>✓ CI regression gating</li>
                </ul>
            </div>
        </div>
    );
}
