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

For all LLM providers (OpenAI, Gemini, Groq, Mistral, HuggingFace, Ollama):
```bash
pip install phylax[all]
```

Individual providers:
```bash
pip install phylax[openai]       # OpenAI
pip install phylax[google]       # Gemini (google-genai SDK)
pip install phylax[groq]         # Groq LPU
pip install phylax[mistral]      # Mistral AI
pip install phylax[huggingface]  # HuggingFace Inference API
pip install phylax[ollama]       # Ollama (local models)
```

## Quick Start

```python
from phylax import trace, expect, execution, GeminiAdapter

@trace(provider="gemini")
@expect(must_include=["hello"], max_latency_ms=5000)
def greet(name: str):
    """Traced Gemini call with expectations."""
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=f"Say hello to {name}",
        model="gemini-2.5-flash",
    )
    return response

# Single call
result = greet("World")
print(result.text)

# Track multi-step agent flows
with execution() as exec_id:
    step1 = greet("Alice")
    step2 = greet("Bob")
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

## Supported Providers

| Provider | Adapter | Env Variable |
|----------|---------|--------------|
| OpenAI | `OpenAIAdapter` | `OPENAI_API_KEY` |
| Gemini | `GeminiAdapter` | `GOOGLE_API_KEY` |
| Groq | `GroqAdapter` | `GROQ_API_KEY` |
| Mistral | `MistralAdapter` | `MISTRAL_API_KEY` |
| HuggingFace | `HuggingFaceAdapter` | `HF_TOKEN` |
| Ollama | `OllamaAdapter` | `OLLAMA_HOST` |

```python
from phylax import OpenAIAdapter, GroqAdapter, MistralAdapter

# All adapters share the same interface
adapter = GroqAdapter()
response, trace = adapter.generate(prompt="Hello!", model="llama3-70b-8192")
```

---

## What Phylax is NOT

- ❌ **Not monitoring** — no metrics, no dashboards
- ❌ **Not observability** — no traces-to-cloud, no analytics
- ❌ **Not AI judgment** — rules are deterministic, not LLM-based
- ❌ **Not cloud-dependent** — runs entirely local
- ❌ **Not prompt engineering** — tests outputs, not prompts

Phylax is a **test framework**. It tells you when LLM behavior changes.

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
| **Expectations** | Validate with `@expect` rules |
| **Execution Context** | Group traces by `execution()` context |
| **Golden Traces** | Baseline comparisons with hash verification |
| **CI Integration** | `phylax check` exits 1 on regression |
| **Web UI** | View traces at http://127.0.0.1:8000/ui |
| **Multi-Provider** | OpenAI, Gemini, Groq, Mistral, HuggingFace, Ollama |

---

## Demos

See the `demos/` directory for runnable examples:

```bash
python demos/01_basic_trace.py      # Basic tracing
python demos/02_expectations.py     # All @expect rules
python demos/03_execution_context.py # Trace grouping
python demos/04_graph_nodes.py      # Graph API
python demos/05_golden_workflow.py  # CI workflow
python demos/06_raw_evidence.py     # Evidence API
python demos/07_error_contracts.py  # Error codes
```

---

## Documentation

- [Quickstart](https://github.com/xXMohitXx/Phylax/blob/main/docs/quickstart.md)
- [Providers](https://github.com/xXMohitXx/Phylax/blob/main/docs/providers.md)
- [Error Codes](https://github.com/xXMohitXx/Phylax/blob/main/docs/errors.md)
- [Correct Usage](https://github.com/xXMohitXx/Phylax/blob/main/docs/correct-usage.md)
- [API Contract](https://github.com/xXMohitXx/Phylax/blob/main/docs/contract.md)

---

## License

MIT License
