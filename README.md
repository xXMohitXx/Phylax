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
  <a href="https://pepy.tech/projects/phylax"><img src="https://static.pepy.tech/personalized-badge/phylax?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=Downloads" alt="PyPI Downloads"></a>
</p>

<p align="center">
  <a href="https://phylax.dev/docs/quickstart">Quickstart</a> · <a href="https://phylax.dev/docs">Docs</a> · <a href="https://phylax.dev/examples">Examples</a> · <a href="https://phylax.dev/blog">Blog</a> · <a href="https://phylax.dev/pricing">Cloud</a>
</p>

---

## ⚡ 10-Second Example

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
phylax check   # exits 1 on contract violation
```

```
❌ FAIL — expected "refund" in response
   Trace ID: abc-123
   Violation: must_include rule failed
```

**That's it.** Your CI now blocks AI behavior regressions. No AI judges, no probabilistic scoring — just deterministic PASS/FAIL.

---

## 📦 Dataset Contracts

Define behavioral test suites in YAML. Batch-test hundreds of prompts against live models. Run in CI.

```yaml
# datasets/support_bot.yaml
dataset: support_bot
cases:
  - input: "I want a refund for my last purchase"
    expectations:
      must_include: ["refund_policy", "30_days"]
      must_not_include: ["credit_card_number"]
      max_latency_ms: 3000

  - input: "How do I reset my password?"
    expectations:
      must_include: ["password", "reset"]
      max_latency_ms: 2000

  - input: "Tell me a joke"
    expectations:
      must_not_include: ["internal_error", "SQL"]
      min_tokens: 10
```

```bash
phylax dataset run datasets/support_bot.yaml

# Running dataset 'support_bot'...
# [Case 1/3] "I want a refund..."    ✓ PASS
# [Case 2/3] "How do I reset..."     ✓ PASS
# [Case 3/3] "Tell me a joke"        ✗ FAIL — min_tokens (actual: 4, minimum: 10)
#
# ❌ 1 of 3 cases failed. Exit code 1.
```

Or use the Python API:

```python
from phylax import Dataset, load_dataset, run_dataset, format_report

ds = load_dataset("datasets/support_bot.yaml")
result = run_dataset(ds, handler_function)
print(format_report(result))
```

---

## 🔄 CI Enforcement

Phylax runs inside your existing CI pipeline. Exit code 0 = all pass. Exit code 1 = regression detected. PR blocked.

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
      - run: phylax check
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      - run: phylax dataset run datasets/*.yaml
```

Works with GitHub Actions, GitLab CI, Jenkins, CircleCI — anything that reads exit codes.

---

## 📊 Execution Graphs

Track multi-step agent workflows as directed acyclic graphs (DAGs). Phylax automatically captures parent-child relationships across LLM calls.

```python
from phylax import trace, expect, execution, OpenAIAdapter

@trace(provider="openai")
@expect(must_include=["intent"])
def classify(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.generate(prompt=f"Classify: {message}")
    return response

@trace(provider="openai")
@expect(must_include=["refund"])
def handle_refund(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.generate(prompt=message)
    return response

# Group into execution graph
with execution() as exec_id:
    intent = classify("I want a refund")
    response = handle_refund("Process refund for order #123")

# Phylax builds:
#   [classify] → [handle_refund]
#
# If classify fails → Phylax reports the first failing node.
# View the graph: phylax server → http://127.0.0.1:8000/ui
```

**Graph capabilities**: topological ordering, critical path analysis, bottleneck detection, graph diffing, investigation paths, SHA256 integrity verification.

---

## 🧪 Model Upgrade Simulation

Upgrading from GPT-4 to GPT-4.5? Run your entire dataset contract against both models and diff the results:

```bash
phylax simulate --from gpt-4 --to gpt-4.5 datasets/support_bot.yaml
```

```python
from phylax import simulate_upgrade, format_simulation_report

result = simulate_upgrade(
    dataset=ds,
    baseline_func=gpt4_handler,
    candidate_func=gpt45_handler,
)
print(format_simulation_report(result))
# safe_to_upgrade: False — 3 regressions detected
```

---

## 🛡️ Guardrail Packs

Pre-built contract templates for common safety, quality, and compliance scenarios:

```python
from phylax import safety_pack, quality_pack, compliance_pack

# Safety: blocks PII, hate speech, prompt injection
safety_rules = safety_pack()

# Quality: min response length, max latency, coherence
quality_rules = quality_pack()

# Compliance: regulatory output constraints
compliance_rules = compliance_pack()
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

## 🔧 Commands

| Command | What It Does |
|---------|---|
| `phylax check` | **CI enforcement** — exits 1 on violation |
| `phylax dataset run` | Execute dataset contracts |
| `phylax simulate` | Model upgrade simulation |
| `phylax init` | Initialize config |
| `phylax server` | Start API + UI |
| `phylax list` | List traces (`--failed` for failures only) |
| `phylax show <id>` | Inspect a trace |
| `phylax bless <id>` | Mark as golden baseline |
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

## ☁️ Phylax Cloud — Coming Soon

**Zero infrastructure CI enforcement for teams.**

Managed cloud platform with:

- **Trace Upload**: `phylax init --cloud` + `PHYLAX_API_KEY` — traces upload automatically
- **Dataset Replay Engine**: Upload 1,000 prompts, run baselines and regression detection at scale
- **Team Collaboration**: Shared projects, datasets, rules, and baselines across developers
- **Dashboard**: Failed cases, dataset history, diff visualizations, graph analysis

**[Join the Cloud Beta Waitlist →](https://phylax.dev)**

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

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Good first issues are tagged with `good first issue`. Community guardrail packs and example datasets are always welcome.

---

## 🏛️ Architecture

```
phylax/
├── _internal/
│   ├── expectations/    # Deterministic rule engine
│   ├── surfaces/        # Surface enforcement (JSON, tools, traces)
│   ├── datasets/        # Dataset contracts & behavioral diff
│   ├── guardrails/      # Guardrail packs (safety, quality, compliance)
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

**910 tests** · **v1.6.3** · All 4 axes complete + Dataset Contracts + Behavioral Diff + Model Simulator + CI Kits + Guardrail Packs

---

## TL;DR

Phylax is **CI for AI behavior**. It records LLM outputs, evaluates them against declared contracts, and fails builds when behavior regresses. No scoring. No judgment. No AI-based evaluation. Just deterministic enforcement.

---

## License

MIT License

# Made with love❤️
