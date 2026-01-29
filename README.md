<p align="center">
  <img src="https://raw.githubusercontent.com/xXMohitXx/Phylax/main/assets/logo/phylax_logo.png" alt="Phylax Logo" width="200">
</p>

# Phylax

**Deterministic regression enforcement for LLM systems.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/phylax.svg)](https://pypi.org/project/phylax/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## The Problem

LLM outputs change unexpectedly. Same prompt, different model version → different behavior.
Without Phylax, you discover this **in production**.

## Installation

```bash
pip install phylax
```

For server/UI support:
```bash
pip install phylax[server]
```

For all LLM providers:
```bash
pip install phylax[all]
```

## Quick Start

```python
import phylax
from phylax._internal.decorator import trace
from phylax._internal.context import execution
from phylax._internal.adapters.gemini import GeminiAdapter

@trace(provider="gemini")
def ask_gemini(prompt: str):
    """Traced Gemini call."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=prompt,
        model="gemini-2.5-flash",
    )
    return response

# Single call
result = ask_gemini("Hello!")
print(result.text)

# Track multi-step agent flows
with execution() as exec_id:
    step1 = ask_gemini("What is 2+2?")
    step2 = ask_gemini("Is that correct?")
```

```bash
# Start the UI server
phylax server
# Open http://127.0.0.1:8000/ui

# Mark a known-good response as baseline
phylax bless <trace_id>

# In CI: fail if output regresses
phylax check  # exits 1 on failure
```

That's it. Your CI now blocks LLM regressions.

---

## What Phylax is NOT

- ❌ **Not monitoring** — no metrics, no dashboards
- ❌ **Not observability** — no traces-to-cloud, no analytics
- ❌ **Not AI judgment** — rules are deterministic, not LLM-based
- ❌ **Not cloud-dependent** — runs entirely local
- ❌ **Not prompt engineering** — tests outputs, not prompts

Phylax is a **test framework**. It tells you when LLM behavior changes.

---

## Using the Web UI

```bash
pip install phylax[server]
phylax server
# Open http://127.0.0.1:8000/ui
```

The UI shows:
- Trace list with pass/fail status
- Execution graphs for multi-step flows
- Forensics mode for debugging

---

## CI Integration

```yaml
# .github/workflows/phylax.yml
- run: phylax check
  env:
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

**Exit codes:**
- `0` — All golden traces pass
- `1` — Regression detected

---

## Commands

| Command | What it does |
|---------|--------------|
| `phylax init` | Initialize config |
| `phylax server` | Start API server + UI |
| `phylax list` | List traces |
| `phylax list --failed` | Show only failed traces |
| `phylax show <id>` | Show trace details |
| `phylax replay <id>` | Re-run a trace |
| `phylax bless <id>` | Mark as golden baseline |
| `phylax check` | CI regression check |

---

## Features

| Feature | Description |
|---------|-------------|
| **Trace Capture** | Record every LLM call automatically |
| **Execution Context** | Group traces by `execution()` context |
| **Golden Traces** | Baseline comparisons with hash verification |
| **CI Integration** | `phylax check` exits 1 on regression |
| **Web UI** | View traces at http://127.0.0.1:8000/ui |
| **Forensics Mode** | Debug failures with guided investigation |

---

## Stability Guarantee

Phylax v1.x is **API-frozen**:

- No breaking changes in v1.x
- `trace`, `execution` are stable
- Exit codes are stable
- Schema is stable

See [docs/contract.md](https://github.com/xXMohitXx/Phylax/blob/main/docs/contract.md) for full guarantees.

---

## Documentation

- [Quickstart](https://github.com/xXMohitXx/Phylax/blob/main/docs/quickstart.md)
- [Mental Model](https://github.com/xXMohitXx/Phylax/blob/main/docs/mental-model.md)
- [API Contract](https://github.com/xXMohitXx/Phylax/blob/main/docs/contract.md)

---

## License

MIT License
