# Phylax Quickstart

> **Goal: From zero to CI failure in 10 minutes.**

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
import os
import phylax
from phylax._internal.decorator import trace
from phylax._internal.context import execution
from phylax._internal.adapters.gemini import GeminiAdapter

@trace(provider="gemini")
def greet(name):
    """Traced Gemini call."""
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
from phylax._internal.context import execution

with execution() as exec_id:
    print(f"Execution ID: {exec_id}")
    step1 = greet("Alice")
    step2 = greet("Bob")
    # Both traces share the same execution_id
```

---

## 5. Bless a Golden (1 min)

Find your trace ID in the UI and mark it as the baseline:

```bash
phylax bless <trace_id> --yes
```

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
✅ Execution context grouping  
✅ Golden baseline comparison  
✅ CI regression gate  
✅ Web UI for debugging  

---

## Next Steps

- [Mental Model](mental-model.md) — What Phylax is
- [Graph Model](graph-model.md) — Multi-step agents
- [Failure Playbook](failure-playbook.md) — Debug failures
