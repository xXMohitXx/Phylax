<p align="center">
  <img src="https://raw.githubusercontent.com/xXMohitXx/Phylax/main/assets/logo/phylax_logo.png" alt="Phylax Logo" width="180">
</p>

<h1 align="center">Phylax — CI for AI Behavior</h1>

<p align="center">
  <strong>Stop AI regressions before they reach production.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/phylax/"><img src="https://img.shields.io/pypi/v/phylax.svg" alt="PyPI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
</p>

---

## ⚡ 30-Second Example

```bash
pip install phylax
```

```python
from phylax import trace, expect

@trace(provider="openai")
@expect(must_include=["refund"], must_not_include=["lawsuit"])
def reply(prompt):
    return llm(prompt)  # your LLM call
```

```bash
phylax check
```

```
❌ FAIL — expected "refund" in response
   Trace ID: abc-123
   Violation: must_include rule failed
```

**That's it.** Your CI now blocks AI behavior regressions.

---

## 🎯 What Phylax Does

Phylax enforces **deterministic contracts** on LLM outputs. When your AI's behavior changes across model versions, prompts, or configurations — Phylax catches it.

```
Developer writes rules   →   Phylax tests every response   →   CI blocks regressions
```

**Phylax is NOT** monitoring, observability, or AI-based evaluation. It's a test framework for AI behavior.

---

## 🚀 Quick Start

### 1. Install

```bash
pip install phylax[openai]   # or phylax[google], phylax[groq], phylax[all]
```

### 2. Write Traced Code

```python
from phylax import trace, expect, execution, OpenAIAdapter

# Single call with expectations
@trace(provider="openai")
@expect(must_include=["refund"], max_latency_ms=3000)
def handle_refund(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.generate(prompt=message)
    return response

# Multi-step agent flow
@trace(provider="openai")
@expect(must_include=["intent"])
def classify(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.generate(prompt=f"Classify: {message}")
    return response

# Track agent workflows as execution graphs
with execution() as exec_id:
    intent = classify("I want a refund")
    response = handle_refund("Process refund for order #123")
```

### 3. Enforce in CI

```yaml
# .github/workflows/phylax.yml
name: Phylax CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install phylax[openai]
      - run: phylax check    # exits 1 on contract violation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## 📋 Expectation Rules

| Rule | What It Enforces | Example |
|------|------------------|---------|
| `must_include` | Response contains required text | `["refund", "policy"]` |
| `must_not_include` | Response excludes forbidden text | `["lawsuit", "attorney"]` |
| `max_latency_ms` | Response time limit | `3000` (3 seconds) |
| `min_tokens` | Minimum response length | `50` tokens |

### Combine with Logic

```python
from phylax import trace, expect, AndGroup, OrGroup, MustIncludeRule, MaxLatencyRule

@trace(provider="openai")
@expect(rules=AndGroup([
    MustIncludeRule("refund"),
    OrGroup([
        MaxLatencyRule(3000),
        MustIncludeRule("processing"),
    ]),
]))
def handle(message):
    ...
```

---

## 🔬 Surface Enforcement

Enforce contracts on **any** LLM output type — not just text.

```python
from phylax import (
    Surface, SurfaceEvaluator,
    FieldExistsRule,             # JSON field must exist
    TypeEnforcementRule,          # Strict type checking
    ToolPresenceRule,             # Tool must be called
    StepCountRule,                # Execution must have N steps
    ExactStabilityRule,           # Output must not change between runs
)
```

| Surface Type | Rules | Use Case |
|-------------|-------|----------|
| **Structured Output** | Field exists, type, value, enum, array bounds | JSON API responses |
| **Tool Calls** | Presence, count, argument, ordering | Agent tool usage |
| **Execution Traces** | Step count, forbidden transitions, required stages | Multi-step workflows |
| **Cross-Run Stability** | Exact match, allowed drift | Regression detection |

---

## 📊 Execution Graphs

Visualize and debug multi-step agent workflows:

```python
from phylax import trace, expect, execution

with execution() as exec_id:
    step1 = classify(message)      # → Node 1
    step2 = research(step1)        # → Node 2
    step3 = respond(step2)         # → Node 3

# Phylax builds a DAG:
#   [classify] → [research] → [respond]
#
# View it:
#   phylax server → http://127.0.0.1:8000/ui
```

---

## 🛡️ Enforcement Modes

```python
from phylax import ModeHandler, EnforcementMode

handler = ModeHandler(mode=EnforcementMode.ENFORCE)
# enforce    → CI fails on violation (default)
# quarantine → CI fails, but logs for review
# observe    → CI passes, violations logged only
```

---

## 🔧 Commands

| Command | What It Does |
|---------|----|
| `phylax init` | Initialize config |
| `phylax server` | Start API + UI |
| `phylax list` | List traces (`--failed` for failures only) |
| `phylax show <id>` | Inspect a trace |
| `phylax bless <id>` | Mark as golden baseline |
| `phylax check` | **CI enforcement** — exits 1 on violation |
| `phylax --version` | Show version |

---

## 🔌 Supported Providers

```bash
pip install phylax[all]   # Install all providers
```

| Provider | Import | Env Variable |
|----------|--------|--------------|
| OpenAI | `from phylax import OpenAIAdapter` | `OPENAI_API_KEY` |
| Gemini | `from phylax import GeminiAdapter` | `GOOGLE_API_KEY` |
| Groq | `from phylax import GroqAdapter` | `GROQ_API_KEY` |
| Mistral | `from phylax import MistralAdapter` | `MISTRAL_API_KEY` |
| HuggingFace | `from phylax import HuggingFaceAdapter` | `HF_TOKEN` |
| Ollama | `from phylax import OllamaAdapter` | `OLLAMA_HOST` |

---

## 📁 Examples & Templates

### Examples — Learn by doing

| Example | What You'll Learn |
|---------|-------------------|
| [`examples/quickstart/`](examples/quickstart/) | Basic tracing in 10 lines |
| [`examples/support_bot/`](examples/support_bot/) | Content safety enforcement |
| [`examples/summarization/`](examples/summarization/) | Latency + quality contracts |
| [`examples/agent_workflow/`](examples/agent_workflow/) | Multi-step agents with execution graphs |

### Templates — Start building

| Template | What It Includes |
|----------|------------------|
| [`templates/ai-chatbot/`](templates/ai-chatbot/) | Chatbot + contracts + CI config |
| [`templates/ai-agent/`](templates/ai-agent/) | Multi-step agent + execution tracking |
| [`templates/ai-rag/`](templates/ai-rag/) | RAG pipeline + grounding enforcement |

---

## 📖 Documentation

**Start here:**
- [Quickstart](docs/quickstart.md) — 10 minutes to CI enforcement
- [Mental Model](docs/mental-model.md) — What Phylax is and isn't
- [Providers](docs/providers.md) — LLM provider reference
- [Error Codes](docs/errors.md) — Error code reference

**Reference:**
- [API Contract](docs/reference/contract.md) — Stability guarantees
- [Execution Context](docs/reference/execution-context.md) — Trace grouping
- [Non-Goals](docs/reference/non-goals.md) — What Phylax will never do
- [Versioning](docs/reference/versioning.md) — Release policy

**Advanced:**
- [Surface Enforcement](docs/advanced/surface-enforcement.md)
- [Graph Model](docs/advanced/graph-model.md)
- [Failure Playbook](docs/advanced/failure-playbook.md)
- [Performance](docs/advanced/performance.md)
- [Invariants](docs/advanced/invariants.md)

---

## 🏛️ Architecture

```
phylax/
├── _internal/
│   ├── expectations/    # Deterministic rule engine
│   ├── surfaces/        # Surface enforcement (JSON, tools, traces)
│   ├── metrics/         # Expectation health & coverage
│   ├── modes/           # Enforcement mode control
│   ├── meta/            # Dilution guards
│   ├── artifacts/       # Machine-consumable CI outputs
│   ├── adapters/        # LLM provider adapters
│   └── graph.py         # Execution graphs
├── cli/                 # CLI commands
├── server/              # API + health routes
└── ui/                  # Web inspector
```

**910 tests** · **v1.6.0** · All 4 axes complete + Dataset Contracts + Behavioral Diff + Model Simulator + CI Kits + Guardrail Packs

---

## TL;DR

Phylax is **CI for AI behavior**. It records LLM outputs, evaluates them against declared contracts, and fails builds when behavior regresses. No scoring. No judgment. No AI-based evaluation. Just deterministic enforcement.

---

## License

MIT License

# Made with love❤️