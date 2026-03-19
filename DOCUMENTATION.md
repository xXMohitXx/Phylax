# Phylax Documentation

Complete technical reference for Phylax v1.6.3 -- CI-native regression enforcement for LLM outputs.

---

## Overview

Phylax enforces contracts so LLM behavior changes are caught before production:

1. **Recording** every LLM call
2. **Evaluating** explicit expectations (PASS/FAIL)
3. **Comparing** against golden baselines
4. **Failing CI** when declared contracts regress

### Status: v1.6.3 STABLE

Stable means execution semantics and verdict behavior are frozen.
Axis 1 (Expectations), Axis 2 (Surfaces), Axis 3 (Scale Safety), and Axis 4 (Ecosystem Discipline) are complete.
1146 tests passing.

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
| [docs/providers.md](docs/providers.md) | LLM provider reference |
| [docs/errors.md](docs/errors.md) | Error code reference |
| [docs/correct-usage.md](docs/correct-usage.md) | Intended usage patterns |
| [docs/when-not-to-use.md](docs/when-not-to-use.md) | Anti-patterns |
| [docs/advanced/graph-model.md](docs/advanced/graph-model.md) | How to read graphs |
| [docs/advanced/failure-playbook.md](docs/advanced/failure-playbook.md) | Debug procedures |
| [docs/advanced/invariants.md](docs/advanced/invariants.md) | Semantic invariants |
| [docs/advanced/failure-modes.md](docs/advanced/failure-modes.md) | Error behavior |
| [docs/advanced/performance.md](docs/advanced/performance.md) | Scale limits |
| [docs/advanced/surface-enforcement.md](docs/advanced/surface-enforcement.md) | Surface enforcement guide |
| [docs/reference/contract.md](docs/reference/contract.md) | API stability guarantees |
| [docs/reference/execution-context.md](docs/reference/execution-context.md) | Execution context usage |
| [docs/reference/non-goals.md](docs/reference/non-goals.md) | 5 permanent constraints |
| [docs/reference/versioning.md](docs/reference/versioning.md) | Release policy |

---

## SDK Reference

### Installation

```python
from phylax import trace, expect, execution
from phylax import GeminiAdapter, OpenAIAdapter, GroqAdapter
from phylax import MistralAdapter, HuggingFaceAdapter, OllamaAdapter

# Axis 3: Metrics, Modes, Meta-Enforcement
from phylax import (
    ExpectationIdentity, compute_definition_hash,
    EvaluationLedger, LedgerEntry, aggregate, aggregate_all,
    HealthReport, CoverageReport, get_windowed_health,
    ModeHandler, EnforcementMode, VALID_MODES,
    MinExpectationCountRule, ZeroSignalRule,
    DefinitionChangeGuard, ExpectationRemovalGuard,
)
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

## Agent & RAG Enforcement

Deterministic validation for multi-step agents and RAG loops.

### Agent Enforcement

```python
from phylax.agents import ToolSequenceRule, AgentStepValidator

# Validates agent execution steps
validator = AgentStepValidator(min_steps=1, max_steps=5, required_types={"tool_call"})
```

### RAG Enforcement

```python
from phylax.rag import evaluate_rag, ContextUsedRule, NoHallucinationRule, CitationRequiredRule

# Validates grounded generation
rag_rules = [
    ContextUsedRule(threshold=0.8),
    NoHallucinationRule(forbidden_claims=["competitor X"]),
    CitationRequiredRule(require_brackets=True)
]
```

---

## Dataset Contracts & Behavioral Diff

Shift-left evaluation of LLM behaviors over large YAML-defined datasets before production deployment.

### Run a Dataset Contract

```bash
phylax dataset run contracts.yaml --module app --function handle --json
```

### Compare Model Behaviors

```bash
phylax dataset diff runA.json runB.json --json
```

### Python API

```python
from phylax._internal.datasets.executor import run_dataset
from phylax._internal.datasets.diff import diff_runs
from phylax._internal.datasets.simulator import simulate_upgrade
```

---

## Guardrail Packs

Productized groupings of expectation rules mapped to real-world domain requirements. (Also available via the `phylax_guardrails` standalone package).

### Using Domain Packs

```python
from phylax.guardrails import pii_pack, security_pack, finance_pack, healthcare_pack

@expect(*pii_pack())
@expect(*security_pack())
def generate_safe_response(prompt: str) -> str:
    # ...
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
from phylax import ExecutionGraph

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
| `phylax dataset run` | Run YAML dataset contract (Axis 4) |
| `phylax dataset diff` | Compare two dataset outputs |
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

### Health & Metrics (Axis 3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/health/{expectation_id}` | Expectation health report |
| GET | `/v1/coverage` | Coverage report |

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

### Pre-configured CI Kits

Phylax provides pre-configured CI/CD templates for easy integration:

- `ci-kits/github-actions/phylax.yml`
- `ci-kits/gitlab-ci/phylax.yml`
- `ci-kits/jenkins/Jenkinsfile`

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

## Axis 3: Scale Safety & Misuse Resistance

### Metrics Foundation

```python
from phylax import (
    ExpectationIdentity, compute_definition_hash,
    LedgerEntry, EvaluationLedger,
    AggregateMetrics, aggregate, aggregate_all,
    HealthReport, CoverageReport, get_windowed_health,
)

# Compute a stable hash for any expectation definition
hash_val = compute_definition_hash({"rule": "must_include", "substrings": ["refund"]})

# Evaluation ledger (append-only, no mutation)
ledger = EvaluationLedger()
ledger.record(LedgerEntry(expectation_id="e1", verdict="pass"))
ledger.record(LedgerEntry(expectation_id="e1", verdict="fail"))

# Aggregate metrics (deterministic)
metrics = aggregate(ledger.entries, "e1")
# metrics.total_evaluations = 2, metrics.failure_rate = 0.5

# Health report
report = HealthReport.from_aggregate(metrics, hash_val)
```

### Enforcement Modes

```python
from phylax import ModeHandler, VALID_MODES

# VALID_MODES = {"enforce", "quarantine", "observe"}
handler = ModeHandler("enforce")
result = handler.apply("fail")
# result.exit_code = 1 (enforce blocks CI on failure)

handler = ModeHandler("observe")
result = handler.apply("fail")
# result.exit_code = 0 (observe logs but does not block)
```

### Meta-Enforcement Rules

```python
from phylax import (
    MinExpectationCountRule,
    ZeroSignalRule,
    DefinitionChangeGuard,
    ExpectationRemovalGuard,
)

# Fail if fewer than 3 expectations defined
rule = MinExpectationCountRule(min_count=3)
result = rule.evaluate(current_count=2)
# result.passed = False

# Detect silent expectation removal
guard = ExpectationRemovalGuard()
result = guard.evaluate(
    previous_ids={"e1", "e2", "e3"},
    current_ids={"e1", "e2"},
)
# result.passed = False, result.removed = {"e3"}
```

---

## Axis 4: Ecosystem Without Platformization

### Verdict Artifacts

```python
from phylax import generate_verdict_artifact

artifact = generate_verdict_artifact(
    mode="enforce",
    verdict="FAIL",
    expectations_evaluated=10,
    failures=3,
    definition_snapshot_hash="abc123",
    engine_version="1.6.3",
)
# Frozen, deterministic, machine-consumable JSON
# No commentary fields. No explanation. No severity.
print(artifact.model_dump_json())
```

### Failure Artifacts

```python
from phylax import generate_failure_artifact

artifact = generate_failure_artifact(
    run_id="ci-run-001",
    failures=[
        {"expectation_id": "e1", "violated_rule": "must_include",
         "raw_value": "Hello", "expected_value": "refund"},
    ],
)
# Mechanical failure records only.
# No 'explanation', 'severity', or 'suggestion' fields.
```

### Trace Diff Artifacts

```python
from phylax import generate_trace_diff

diff = generate_trace_diff(
    run_id_before="run-001",
    run_id_after="run-002",
    expectations_before={"e1", "e2"},
    expectations_after={"e2", "e3"},
    hash_before="hash_a",
    hash_after="hash_b",
)
# diff.added_expectations = ["e3"]
# diff.removed_expectations = ["e1"]
# diff.hashes_match = False
# Literal diffs only. No impact assessment.
```

### Deterministic Exit Codes

```python
from phylax import EXIT_PASS, EXIT_FAIL, EXIT_SYSTEM_ERROR, resolve_exit_code

# Frozen: 0=PASS, 1=FAIL(enforce), 2=system error
code = resolve_exit_code(verdict="FAIL", mode="enforce")  # 1
code = resolve_exit_code(verdict="FAIL", mode="observe")  # 0
```

### Governance Documents

- **`CONSTITUTION.md`** -- 12 promises Phylax will never break (explain failures, rank expectations, suggest improvements, add AI inference, embed dashboards, send alerts, etc.)
- **`ANTI_FEATURES.md`** -- Documented non-features (no dashboards, no alerting, no daemons, no plugins)

---

## Links

- [README](README.md)
- [Development Guide](DEVELOPMENT.md)
- [Changelog](CHANGELOG.md)
- [Constitution](CONSTITUTION.md)
- [Anti-Features](ANTI_FEATURES.md)
- [GitHub](https://github.com/xXMohitXx/Phylax)
