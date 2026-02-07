<p align="center">
  <img src="https://raw.githubusercontent.com/xXMohitXx/Phylax/main/assets/logo/phylax_logo.png" alt="Phylax Logo" width="200">
</p>

# Phylax

**CI-native regression enforcement for LLM outputs.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/phylax.svg)](https://pypi.org/project/phylax/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## The Problem

LLM systems change across model versions, prompts, and environments.
Phylax enforces contracts so these changes are caught before production.

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
# Start the server
phylax server

# Mark a known-good response as baseline
phylax bless <trace_id>

# In CI: fail if output violates declared expectations
phylax check  # exits 1 on contract violation
```

**That's it. Your CI now blocks LLM contract violations.**

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

- ❌ **Not monitoring or observability** — no metrics, no dashboards, no analytics
- ❌ **Not production runtime tooling** — CI enforcement only
- ❌ **Not AI-based judgment or scoring** — rules are deterministic, never LLM-based
- ❌ **Not exploratory prompt evaluation** — tests outputs against declared contracts
- ❌ **Not adaptive or heuristic-driven** — exact match, explicit expectations

**If you need subjective evaluation or live insights, Phylax is the wrong tool.**

---

## CI Integration (Primary Interface)

Phylax's primary interface is CI verdict enforcement.

```yaml
# .github/workflows/phylax.yml
- run: phylax check
  env:
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

**Exit codes:**
- `0` — All golden traces pass declared expectations
- `1` — Contract violation detected

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
| `phylax check` | **CI regression enforcement** |
| `phylax --version` | Show version |

---

## Capabilities

| Capability | Description |
|------------|-------------|
| **Trace Capture** | Record every LLM call automatically |
| **Expectations** | Validate with `@expect` rules |
| **Execution Context** | Group traces by `execution()` context |
| **Golden Traces** | Baseline comparisons with hash verification |
| **CI Enforcement** | `phylax check` exits 1 on contract violation |
| **Multi-Provider** | OpenAI, Gemini, Groq, Mistral, HuggingFace, Ollama |

### Auxiliary Control Surfaces

The UI and API are auxiliary control surfaces.
Phylax's primary interface is CI verdict enforcement.

| Surface | Purpose |
|---------|---------|
| **Web UI** | Inspect traces at http://127.0.0.1:8000/ui |
| **Golden Reference UI** | Bless/unbless traces from interface |
| **Trace ID Search** | Find traces by ID |
| **REST API** | Programmatic trace access |

---

## Architecture

```
phylax/
├── _internal/           # Core enforcement logic
│   ├── adapters/        # LLM provider adapters
│   ├── expectations/    # Deterministic rule engine
│   └── graph.py         # Execution graphs
├── cli/                 # CLI commands
├── server/              # API server
└── ui/                  # Web interface
```

The API server exists to support Phylax operations (trace storage, golden management, CI verdicts).
It is not an extensibility platform.

---

## Demos

See the `demos/` directory for runnable examples:

```bash
python demos/01_basic_trace.py       # Basic tracing
python demos/02_expectations.py      # All @expect rules
python demos/03_execution_context.py # Trace grouping
python demos/04_graph_nodes.py       # Graph API
python demos/05_golden_workflow.py   # CI workflow
python demos/06_raw_evidence.py      # Evidence API
python demos/07_error_contracts.py   # Error codes
```

---

## Version

**v1.1.6 STABLE**

Stable means execution semantics and verdict behavior are frozen.
Minor versions focus on correctness and misuse prevention.

---

## Documentation

- [Quickstart](https://github.com/xXMohitXx/Phylax/blob/main/docs/quickstart.md)
- [Providers](https://github.com/xXMohitXx/Phylax/blob/main/docs/providers.md)
- [Error Codes](https://github.com/xXMohitXx/Phylax/blob/main/docs/errors.md)
- [Correct Usage](https://github.com/xXMohitXx/Phylax/blob/main/docs/correct-usage.md)
- [API Contract](https://github.com/xXMohitXx/Phylax/blob/main/docs/contract.md)

---

## TL;DR

Phylax is a CI-native, deterministic regression enforcement system for LLM outputs.
It records LLM behavior, evaluates explicit expectations, and fails builds when declared contracts regress.
Phylax does not explain, score, or optimize outputs — it enforces consistency.

---

## License

MIT License
