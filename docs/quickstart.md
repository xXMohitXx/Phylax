# Phylax Quickstart

> **Goal: From zero to CI enforcement in 10 minutes.**

---

## 1. Install (2 min)

```bash
pip install phylax[all]
```

Set your API key:

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY = "your-key"

# Linux/Mac
export GOOGLE_API_KEY="your-key"
```

---

## 2. Start Server (1 min)

```bash
phylax server
```

Open: <http://127.0.0.1:8000/ui>

---

## 3. Create Your First Trace (3 min)

Create `myapp.py`:

```python
from phylax import trace, expect, GeminiAdapter

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

# Run it
if __name__ == "__main__":
    result = greet("World")
    print(f"Response: {result.text}")
```

Run:

```bash
python myapp.py
```

Check UI at <http://127.0.0.1:8000/ui> — you should see your trace!

---

## 4. Use Execution Context (2 min)

Group related calls together:

```python
from phylax import trace, expect, execution, GeminiAdapter

with execution() as exec_id:
    print(f"Execution ID: {exec_id}")
    step1 = greet("Alice")
    step2 = greet("Bob")
    # Both traces share the same execution_id
```

---

## 5. Bless a Golden (1 min)

**Option A: From the UI (recommended)**

1. Find your trace in the sidebar
2. Click **⭐ Bless as Golden** button
3. Trace shows gold border and "GOLDEN" badge

**Option B: From CLI**

```bash
phylax bless <trace_id> --yes
```

**Tip:** Use the 🔍 search box to find traces by ID!

---

## 6. Run CI Check (1 min)

```bash
phylax check
```

- **Exit 0**: All goldens pass ✅
- **Exit 1**: Regression detected ❌

---

## 7. Add to CI (2 min)

```yaml
# .github/workflows/phylax.yml
name: Phylax Check
on: [push]
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
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

---

## Done! You now have

✅ LLM call tracing  
✅ Expectation validation  
✅ Execution context grouping  
✅ Golden baseline comparison  
✅ CI regression gate  
✅ Web UI for failure visualization  

---

## Using Other Providers

```python
from phylax import (
    OpenAIAdapter,     # pip install phylax[openai]
    GeminiAdapter,     # pip install phylax[google]
    GroqAdapter,       # pip install phylax[groq]
    MistralAdapter,    # pip install phylax[mistral]
    HuggingFaceAdapter, # pip install phylax[huggingface]
    OllamaAdapter,     # pip install phylax[ollama]
)

# All adapters share the same interface
adapter = GroqAdapter()
response, trace = adapter.generate(prompt="Hello!", model="llama3-70b-8192")
```

---

## 8. Dataset Contracts (v1.6.0+)

Batch-test LLM behavior:

```python
from phylax import Dataset, DatasetCase, run_dataset, format_report

ds = Dataset(dataset="my_bot", cases=[
    DatasetCase(
        input="help with refund",
        expectations={"must_include": ["refund"], "min_tokens": 10},
    ),
])

result = run_dataset(ds, my_handler)
print(format_report(result))
```

Or from CLI:

```bash
phylax dataset run contracts.yaml
```

---

## 9. Guardrail Packs (v1.6.0+)

Apply pre-built safety rules:

```python
from phylax import safety_pack, quality_pack, get_pack

safety = safety_pack()  # Blocks hate speech, PII, harmful content
quality = quality_pack()  # Min response length, latency ceiling

# Use with dataset contracts
expectations = safety.to_expectations()
```

Available packs: `safety`, `quality`, `compliance`

---

## 10. Model Upgrade Simulator (v1.6.0+)

Test model upgrades safely:

```python
from phylax import simulate_upgrade, format_simulation_report

sim = simulate_upgrade(
    dataset=ds,
    baseline_func=gpt4_handler,
    candidate_func=gpt45_handler,
    baseline_name="GPT-4",
    candidate_name="GPT-4.5",
)

if sim.safe_to_upgrade:
    print("✅ Safe to deploy!")
print(format_simulation_report(sim))
```

---

## 11. Multi-Agent Enforcement (v1.6.3+)

Validate entire agent workflow sequences dynamically:

```python
from phylax.agents import ToolSequenceRule

sequence = ToolSequenceRule(["search_db", "format_response"])
trace = [{"tool_name": "search_db"}, {"tool_name": "format_response"}]

result = sequence.evaluate(trace)
print(result.passed)
```

---

## 12. RAG Enforcement (v1.6.3+)

Evaluate strict bounds for your Retrieval-Augmented Generation context window:

```python
from phylax.rag import evaluate_rag

result = evaluate_rag(
    question="...",
    context="...",
    answer="...",
    rules=["no_hallucination", "context_used"]
)
```

---

## 13. Advanced CLI Capabilities (v1.6.3+)

Use `phylax graph-check` natively in CI to validate execution context dependencies mapping accurately:

```bash
phylax graph-check .phylax/traces
```

---

## Next Steps

- [Providers](providers.md) — All supported providers
- [Error Codes](errors.md) — PHYLAX_Exxx error reference
- [Correct Usage](correct-usage.md) — Valid configurations
- [Mental Model](mental-model.md) — What Phylax is
- [Advanced Guides](advanced/) — Advanced integrations
- [Examples](../examples/) — Real-world usage patterns
- [Demos](../demos/) — All 26 feature demos
