# Phylax Documentation

Complete technical reference for Phylax v1.2.6 — CI-native regression enforcement for LLM outputs.

---

## Overview

Phylax enforces contracts so LLM behavior changes are caught before production:
1. **Recording** every LLM call
2. **Evaluating** explicit expectations (PASS/FAIL)
3. **Comparing** against golden baselines
4. **Failing CI** when declared contracts regress

### Status: ✅ v1.2.6 STABLE

Stable means execution semantics and verdict behavior are frozen.
Minor versions focus on correctness and misuse prevention.

---

## What Phylax is NOT

- ❌ **Not monitoring or observability** — no metrics, no dashboards, no analytics
- ❌ **Not production runtime tooling** — CI enforcement only
- ❌ **Not AI-based judgment or scoring** — rules are deterministic, never LLM-based
- ❌ **Not exploratory prompt evaluation** — tests outputs against declared contracts
- ❌ **Not adaptive or heuristic-driven** — exact match, explicit expectations

**If you need subjective evaluation or live insights, Phylax is the wrong tool.**

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [docs/quickstart.md](docs/quickstart.md) | 10 min to CI enforcement |
| [docs/mental-model.md](docs/mental-model.md) | What Phylax is/isn't |
| [docs/graph-model.md](docs/graph-model.md) | How to read graphs |
| [docs/execution-context.md](docs/execution-context.md) | Execution context usage |
| [docs/failure-playbook.md](docs/failure-playbook.md) | Debug procedures |
| [docs/contract.md](docs/contract.md) | API stability guarantees |
| [docs/invariants.md](docs/invariants.md) | Semantic invariants |
| [docs/failure-modes.md](docs/failure-modes.md) | Error behavior |
| [docs/versioning.md](docs/versioning.md) | Release policy |
| [docs/performance.md](docs/performance.md) | Scale limits |
| [docs/providers.md](docs/providers.md) | LLM provider reference |
| [docs/errors.md](docs/errors.md) | Error code reference |

---

## SDK Reference

### Installation
```python
from phylax import trace, expect, execution
from phylax import GeminiAdapter, OpenAIAdapter, GroqAdapter
from phylax import MistralAdapter, HuggingFaceAdapter, OllamaAdapter
```

### @trace Decorator
```python
@trace(provider="gemini", model="gemini-2.5-flash")
def my_function(prompt):
    adapter = GeminiAdapter()
    return adapter.generate(prompt)
```

### @expect Decorator
```python
@trace(provider="gemini")
@expect(
    must_include=["refund"],
    must_not_include=["sorry"],
    max_latency_ms=1500,
    min_tokens=10
)
def customer_support(query):
    return llm.generate(query)
```

### Execution Context
```python
from phylax import execution

# Track multi-step workflows
with execution() as exec_id:
    step1 = call_llm("First step")
    step2 = call_llm("Second step")  # Automatically linked
```

The `execution()` context manager groups traces into a single execution graph.
It does not validate whether traced calls were made inside it — validation
happens at graph evaluation time.

### Adapters

**GeminiAdapter** (uses `google-genai` SDK)
```python
adapter = GeminiAdapter()  # uses GOOGLE_API_KEY env
response, trace = adapter.generate(
    prompt="Hello!",
    model="gemini-2.5-flash"
)
```

**OpenAIAdapter**
```python
adapter = OpenAIAdapter()  # uses OPENAI_API_KEY env
response, trace = adapter.chat_completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**GroqAdapter**
```python
adapter = GroqAdapter()  # uses GROQ_API_KEY env
response, trace = adapter.chat_completion(
    model="llama3-70b-8192",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**MistralAdapter**
```python
adapter = MistralAdapter()  # uses MISTRAL_API_KEY env
response, trace = adapter.generate(
    prompt="Hello!",
    model="mistral-large-latest"
)
```

**HuggingFaceAdapter**
```python
adapter = HuggingFaceAdapter()  # uses HF_TOKEN env
response, trace = adapter.generate(
    prompt="Hello!",
    model="meta-llama/Llama-3.1-8B-Instruct"
)
```

**OllamaAdapter**
```python
adapter = OllamaAdapter()  # uses OLLAMA_HOST env (default: localhost:11434)
response, trace = adapter.generate(
    prompt="Hello!",
    model="llama3"
)
```

---

## Expectation Engine

### Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `must_include` | LOW | Substring must appear |
| `must_not_include` | HIGH | Substring must NOT appear |
| `max_latency_ms` | MEDIUM | Response time ceiling |
| `min_tokens` | LOW | Minimum response length |

### Verdict Model
```python
class Verdict:
    status: "pass" | "fail"  # Only two values, ever
    severity: "low" | "medium" | "high" | None
    violations: list[str]
```

---

## Execution Graphs

### Graph Capabilities

| Capability | Description |
|------------|-------------|
| DAG Visualization | Nodes and edges with hierarchical stages |
| Semantic Nodes | Role labels (INPUT, LLM, VALIDATION...) |
| Time Visualization | Latency heatmap, bottleneck badges |
| Failure Focus | First-failure highlighting |
| Graph Diffs | Compare two executions |
| Investigation Paths | Failure localization steps |
| Enterprise | Integrity hashing, snapshots, exports |

### Graph Verdict
```python
class GraphVerdict:
    status: "pass" | "fail"
    first_failing_node: str | None  # First failing node in topological order
    failed_count: int
    tainted_count: int
```

### Building Graphs
```python
from phylax._internal.graph import ExecutionGraph

graph = ExecutionGraph.from_traces(traces)
verdict = graph.compute_verdict()
path = graph.investigation_path()
snapshot = graph.to_snapshot()
```

---

## Golden Traces

### Bless a Trace
```bash
phylax bless <trace_id>
phylax bless <trace_id> --yes    # Skip confirmation
phylax bless <trace_id> --force  # Override existing
```

### How It Works
1. Output is hashed and stored
2. One golden per model/provider
3. `phylax check` compares against golden
4. Hash mismatch → Contract violation → CI fails

---

## CLI Reference (Primary Interface)

Phylax's primary interface is CI verdict enforcement.

| Command | Description |
|---------|-------------|
| `phylax check` | **CI enforcement** (exits 1 on violation) |
| `phylax bless <id>` | Mark golden baseline |
| `phylax init` | Initialize config |
| `phylax server` | Start auxiliary server |
| `phylax list` | List traces |
| `phylax list --failed` | Show only failed traces |
| `phylax show <id>` | Show trace |
| `phylax replay <id>` | Re-run trace |
| `phylax --version` | Show version |

---

## API Reference (Auxiliary)

The API server exists to support Phylax operations (trace storage, golden management, CI verdicts).
It is not an extensibility platform.

Base: `http://127.0.0.1:8000`

### Traces
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/traces` | List |
| GET | `/v1/traces/{id}` | Get |
| POST | `/v1/traces` | Create |
| DELETE | `/v1/traces/{id}` | Delete |

### Executions & Graphs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/executions` | List executions |
| GET | `/v1/executions/{id}` | Get traces |
| GET | `/v1/executions/{id}/graph` | Get DAG |
| GET | `/v1/executions/{id}/analysis` | Performance |
| GET | `/v1/executions/{a}/diff/{b}` | Compare |
| GET | `/v1/executions/{id}/investigate` | Failure path |
| GET | `/v1/executions/{id}/snapshot` | Immutable copy |
| GET | `/v1/executions/{id}/export` | Export artifact |
| GET | `/v1/executions/{id}/verify` | Verify integrity |

### Golden References
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/traces/{id}/bless` | Mark as golden |
| DELETE | `/v1/traces/{id}/bless` | Remove golden status |
| GET | `/v1/goldens` | List all golden traces |

### Replay
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/replay/{id}` | Replay |
| GET | `/v1/replay/{id}/preview` | Preview |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/chat/completions` | OpenAI compat |
| GET | `/health` | Health check |

---

## Storage

```
~/.phylax/
├── config.yaml
├── traces/
│   └── YYYY-MM-DD/
│       └── <trace_id>.json
└── phylax.db  # SQLite index
```

---

## CI Integration (Primary Use Case)

### GitHub Actions
```yaml
- run: phylax check
  env:
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

**Exit codes:**
- `0` — All golden traces pass declared expectations
- `1` — Contract violation detected

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Gemini API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `GROQ_API_KEY` | Groq API key |
| `MISTRAL_API_KEY` | Mistral API key |
| `HF_TOKEN` | HuggingFace token |
| `OLLAMA_HOST` | Ollama host |
| `PHYLAX_HOME` | Config directory (optional) |

---

## Trace Schema

```python
class Trace:
    trace_id: str           # UUID, immutable
    execution_id: str       # Links to execution
    node_id: str            # Graph node ID
    parent_node_id: str     # Parent in DAG
    timestamp: str          # ISO-8601
    request: TraceRequest   # Input
    response: TraceResponse # Output
    verdict: Verdict | None # PASS/FAIL
    blessed: bool           # Golden?
```

---

## Links

- [README](README.md)
- [Development Guide](DEVELOPMENT.md)
- [Changelog](CHANGELOG.md)
- [GitHub](https://github.com/xXMohitXx/Phylax)
