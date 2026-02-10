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

Open: http://127.0.0.1:8000/ui

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

Check UI at http://127.0.0.1:8000/ui — you should see your trace!

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

## Done! You now have:

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

## Next Steps

- [Providers](providers.md) — All supported providers
- [Error Codes](errors.md) — PHYLAX_Exxx error reference
- [Correct Usage](correct-usage.md) — Valid configurations
- [Mental Model](mental-model.md) — What Phylax is
- [Failure Playbook](failure-playbook.md) — Debug failures
