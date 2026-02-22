# Phylax — Comprehensive Codebase Architecture

## 🎯 Executive Summary

**Phylax** is a CI-native, deterministic regression enforcement system for LLM outputs. It records LLM behavior, evaluates explicit expectations, compares against golden baselines, and fails builds when declared contracts regress. Phylax does not explain, score, or optimize outputs — it enforces consistency.

### Core Capabilities
- **Trace Capture**: Automatically records every LLM call (input, output, latency, tokens) into an immutable trace schema
- **Deterministic Expectations**: Four built-in rules (`must_include`, `must_not_include`, `max_latency_ms`, `min_tokens`) produce binary PASS/FAIL verdicts — never AI-based
- **Expectation Algebra**: Logical composition (AND/OR/NOT), conditional activation (IF/THEN), structural scoping (per-node, per-provider), reusable templates, and self-documenting contracts
- **Surface Enforcement (Axis 2)**: Generic enforcement over structured outputs (JSON), tool calls, execution traces, and cross-run snapshots via the Surface Abstraction Layer — 17 deterministic rules across 5 surface types
- **Execution Context**: Groups multi-step LLM workflows under a shared `execution_id` with automatic parent-child tracking via Python `contextvars`
- **Execution Graphs (DAG)**: Builds directed acyclic graphs from grouped traces with semantic node roles, hierarchical stages, performance analysis, diffing, and investigation paths
- **Golden Baselines**: Bless a trace as the known-good reference; `phylax check` replays golden traces and exits 1 if output hash diverges
- **Multi-Provider Adapters**: Unified adapter interface for OpenAI, Gemini, Groq, Mistral, HuggingFace, and Ollama — all with automatic tracing
- **CI Enforcement**: `phylax check` is the primary interface — exits 0 on success, exits 1 on contract violation
- **Raw Evidence**: Exposes hash, latency, path, and timestamp evidence as facts — interpretation is external
- **Enterprise Hardening**: SHA256 integrity hashing, immutable snapshots, JSON export for auditing, and integrity verification
- **Web UI**: Failure-first inspector with dark theme, graph visualization, bless/unbless controls, and forensics mode
- **REST API**: Auxiliary control surface for trace CRUD, graph queries, performance analysis, replay, and OpenAI-compatible chat endpoint

### Non-Goals (What Phylax is NOT)
- ❌ **Not monitoring or observability** — no metrics, no dashboards, no analytics
- ❌ **Not production runtime tooling** — CI enforcement only
- ❌ **Not AI-based judgment or scoring** — rules are deterministic, never LLM-based
- ❌ **Not exploratory prompt evaluation** — tests outputs against declared contracts
- ❌ **Not adaptive or heuristic-driven** — exact match, explicit expectations

---

## 🏗️ Technology Stack & Architectural Decisions

### Core Infrastructure
| Layer | Technology | Purpose | Rationale |
|-------|-----------|---------|-----------|
| **Language** | Python 3.10+ | All code | Type hints, `contextvars`, async/await, rich ecosystem |
| **Data Validation** | Pydantic ≥ 2.5.0 | Trace schema, API models, graph models | Immutable frozen models, JSON serialization, validation |
| **Configuration** | PyYAML ≥ 6.0 | Config files | Standard YAML parsing |
| **REST API** | FastAPI ≥ 0.109.0 | Server endpoints | Auto-generated docs, CORS, async support |
| **ASGI Server** | Uvicorn ≥ 0.27.0 | HTTP server | Production-grade, reload support |
| **Primary Storage** | JSON Files | Trace ground truth | Zero infrastructure, portable, human-readable |
| **Index Layer** | SQLite | Fast queries | Optional optimization over JSON files |
| **Frontend** | Vanilla HTML/CSS/JS | Web UI | Zero dependencies, static files, dark theme |
| **CLI** | argparse | Command-line interface | Standard library, no extra deps |
| **Package Manager** | setuptools + PyPI | Distribution | `pip install phylax` with optional extras |

### LLM Provider Integrations (Optional Dependencies)
| Provider | Package | Adapter Class | Env Variable |
|----------|---------|---------------|--------------|
| OpenAI | `openai ≥ 1.0.0` | `OpenAIAdapter` | `OPENAI_API_KEY` |
| Google Gemini | `google-genai ≥ 0.5.0` | `GeminiAdapter` | `GOOGLE_API_KEY` |
| Groq | `groq ≥ 0.4.0` | `GroqAdapter` | `GROQ_API_KEY` |
| Mistral | `mistralai ≥ 0.1.0` | `MistralAdapter` | `MISTRAL_API_KEY` |
| HuggingFace | `huggingface_hub ≥ 0.20.0` | `HuggingFaceAdapter` | `HF_TOKEN` |
| Ollama | `ollama ≥ 0.1.0` | `OllamaAdapter` | `OLLAMA_HOST` |

### Key Architecture Decisions Explained

**1. Deterministic-Only Verdicts**
- Verdict space is permanently frozen to `PASS` and `FAIL` — no scores, no partial passes, no weighting
- All four rules produce binary outcomes via exact string matching, threshold comparison, or word counting
- This ensures CI reproducibility: the same input always produces the same verdict

**2. Immutable Trace Schema**
- Traces are write-once, never recalculated; verdicts are computed at creation time
- Pydantic `frozen = True` enforces immutability at the model level
- Blessed traces get an output hash stored in metadata for future comparison

**3. Zero-Infrastructure Storage**
- JSON files organized by date (`~/.Phylax/traces/YYYY-MM-DD/<trace_id>.json`) are the ground truth
- SQLite index is an optional acceleration layer, not a requirement
- No database server, no connection strings, no infrastructure to maintain

**4. Adapter Pattern for Multi-Provider Support**
- All adapters share a unified interface: `chat_completion()` and `generate()` returning `(response, Trace)`
- Lazy-loading of provider SDKs (`@property client`) avoids import errors for uninstalled providers
- Capture layer normalizes all provider responses into the standard trace schema

**5. CI as Primary Interface**
- `phylax check` is the canonical command — everything else is auxiliary
- Exit code 0/1 integrates with any CI system (GitHub Actions, GitLab CI, Jenkins)
- The UI and API exist to support operations, not as extensibility platforms

**6. Evidence, Not Analysis**
- Phylax reports raw facts (hash changed, latency delta, path diverged) with no interpretation
- Every evidence artifact carries `_disclaimer: "Phylax reports evidence. Interpretation is external."`
- Investigation paths use "observations" not "reasoning" — no causal language

---

## 📊 High-Level System Architecture

### System Overview Diagram
```
┌──────────────────────────────────────────────────────────────────────────┐
│                        USER APPLICATION CODE                             │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ @trace(provider="gemini")                                         │  │
│  │ @expect(must_include=["hello"], max_latency_ms=5000)              │  │
│  │ def greet(name):                                                  │  │
│  │     adapter = GeminiAdapter()                                     │  │
│  │     return adapter.generate(prompt=f"Say hello to {name}")        │  │
│  │                                                                    │  │
│  │ with execution() as exec_id:                                      │  │
│  │     step1 = greet("Alice")                                        │  │
│  │     step2 = greet("Bob")                                          │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                    Decorators intercept calls                             │
│                              │                                           │
│                              ▼                                           │
├──────────────────────────────────────────────────────────────────────────┤
│                     PHYLAX SDK LAYER (phylax/)                           │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────┐  ┌─────────────┐  │
│  │ @trace     │  │ @expect      │  │ execution()   │  │ Adapters    │  │
│  │ Decorator  │  │ Decorator    │  │ Context Mgr   │  │ (6 LLM      │  │
│  │            │  │              │  │               │  │  providers) │  │
│  │ Intercepts │  │ Stores       │  │ Groups traces │  │             │  │
│  │ LLM calls  │  │ expectations │  │ under shared  │  │ Normalize   │  │
│  │ Measures   │  │ per function │  │ execution_id  │  │ requests &  │  │
│  │ latency    │  │              │  │ Tracks parent/│  │ responses   │  │
│  │ Creates    │  │ 4 rules:     │  │ child nodes   │  │ to standard │  │
│  │ trace      │  │ must_include │  │               │  │ trace       │  │
│  │            │  │ must_not_inc │  │ Uses Python   │  │ schema      │  │
│  │            │  │ max_latency  │  │ contextvars   │  │             │  │
│  │            │  │ min_tokens   │  │ (thread-safe) │  │             │  │
│  └─────┬──────┘  └──────┬───────┘  └───────┬───────┘  └──────┬──────┘  │
│        │                │                   │                 │         │
│        └────────────────┴─────────┬─────────┘                 │         │
│                                   │                           │         │
│                                   ▼                           │         │
│  ┌──────────────────────────────────────────────────────────┐ │         │
│  │                    CAPTURE LAYER                          │ │         │
│  │  • Accepts input payloads from decorators or adapters     │◄┘         │
│  │  • Normalizes into standard Trace schema                  │           │
│  │  • Evaluates expectations → produces Verdict              │           │
│  │  • Stores trace to filesystem (auto_store=True)           │           │
│  └─────────────────────────┬────────────────────────────────┘           │
│                             │                                            │
│                             ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │                   EXPECTATION ENGINE                      │           │
│  │  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌───────────┐ │           │
│  │  │ 4 Rules  │ │ Groups   │ │Conditionals│ │ Scoping   │ │           │
│  │  │ (base)   │ │ AND/OR/  │ │ IF/THEN    │ │ per-node  │ │           │
│  │  │          │ │ NOT      │ │ InputCont. │ │ per-prov  │ │           │
│  │  │          │ │          │ │ ModelEq    │ │ per-stage │ │           │
│  │  │          │ │          │ │ ProviderEq │ │ per-tool  │ │           │
│  │  └──────────┘ └──────────┘ └────────────┘ └───────────┘ │           │
│  │  ┌──────────────────────────────────────────────────────┐│           │
│  │  │ Templates & Registry │ Documentation & Self-Describe ││           │
│  │  └──────────────────────────────────────────────────────┘│           │
│  │                                                           │           │
│  │  → Output: Verdict { status: "pass"|"fail",              │           │
│  │                       severity: "low"|"medium"|"high",    │           │
│  │                       violations: [...] }                 │           │
│  └──────────────────────────────────────────────────────────┘           │
├──────────────────────────────────────────────────────────────────────────┤
│                      STORAGE LAYER                                       │
│  ┌──────────────────────────────────┐  ┌───────────────────────────┐    │
│  │ FileStorage (ground truth)       │  │ SQLiteIndex (optional)    │    │
│  │                                  │  │                           │    │
│  │ ~/.Phylax/                       │  │ ~/.Phylax/index.sqlite    │    │
│  │   traces/                        │  │                           │    │
│  │     2026-02-22/                  │  │ Indexed columns:          │    │
│  │       <trace_id>.json            │  │ • trace_id (PK)           │    │
│  │   graphs/                        │  │ • timestamp               │    │
│  │     <execution_id>.json          │  │ • provider                │    │
│  │   config.yaml                    │  │ • model                   │    │
│  │                                  │  │ • latency_ms              │    │
│  │ Operations:                      │  │ • replay_of               │    │
│  │ • save, get, list, delete        │  │                           │    │
│  │ • bless/unbless (golden)         │  │ Operations:               │    │
│  │ • lineage traversal              │  │ • index, search, count    │    │
│  │ • graph build from traces        │  │ • lineage chain           │    │
│  └──────────────────────────────────┘  └───────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────────┤
│                   EXECUTION GRAPH ENGINE                                 │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ExecutionGraph (DAG)                                             │   │
│  │                                                                   │   │
│  │ • from_traces(traces) → build graph with nodes, edges, stages    │   │
│  │ • compute_verdict() → graph-level PASS/FAIL                      │   │
│  │ • topological_order() → Kahn's algorithm                         │   │
│  │ • critical_path() → longest latency chain (dynamic programming)  │   │
│  │ • find_bottlenecks(top_n) → slowest nodes by % of total          │   │
│  │ • diff_with(other) → added/removed/changed nodes                 │   │
│  │ • investigation_path() → deterministic failure localization       │   │
│  │ • to_snapshot() → immutable copy with SHA256 hash                 │   │
│  │ • verify_integrity() → tamper detection                           │   │
│  │ • export_json() → audit artifact                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────┤
│                    AUXILIARY SURFACES                                     │
│  ┌─────────────────────┐ ┌────────────────────┐ ┌────────────────────┐  │
│  │ CLI (Primary)       │ │ REST API (Port 8000)│ │ Web UI (/ui)      │  │
│  │                     │ │                     │ │                    │  │
│  │ phylax check   ← CI│ │ /v1/traces          │ │ Failure-first      │  │
│  │ phylax bless       │ │ /v1/executions      │ │ inspector          │  │
│  │ phylax list        │ │ /v1/replay          │ │                    │  │
│  │ phylax show        │ │ /v1/chat/completions│ │ Failed-only mode   │  │
│  │ phylax replay      │ │ /v1/goldens         │ │ Graph visualization│  │
│  │ phylax server      │ │ /health             │ │ Bless/unbless      │  │
│  │ phylax init        │ │                     │ │ Forensics mode     │  │
│  │ phylax graph-check │ │ Analysis, Diff,     │ │                    │  │
│  │                     │ │ Snapshot, Verify    │ │ Dark theme         │  │
│  └─────────────────────┘ └────────────────────┘ └────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### Data Flow at a Glance
```
TRACE CREATION (per LLM call)
  User code → @trace/@expect decorators → Adapter.generate()
                                               ↓
                          CaptureLayer.capture(provider, model, messages)
                                               ↓
                          Execute LLM call → Measure latency
                                               ↓
                          Build TraceRequest + TraceResponse + TraceRuntime
                                               ↓
                          Evaluate expectations → Verdict (PASS/FAIL)
                                               ↓
                          Assemble Trace (with execution_id, node_id, parent)
                                               ↓
                          FileStorage.save_trace() → ~/.Phylax/traces/YYYY-MM-DD/<id>.json

CI ENFORCEMENT (phylax check)
  Load all blessed traces from storage
                    ↓
  For each golden trace:
    ├─ Replay with same parameters → new trace
    ├─ Hash new output → compare with golden hash
    ├─ MATCH → ✅ PASS
    └─ MISMATCH → ❌ FAIL → exit 1
                    ↓
  All passed → exit 0 (CI green)
  Any failed → exit 1 (CI red)

GRAPH ANALYSIS (multi-step workflows)
  execution() context manager → shared execution_id
    ├─ Trace A (root, no parent)
    ├─ Trace B (parent = A)
    └─ Trace C (parent = B)
                    ↓
  ExecutionGraph.from_traces([A, B, C])
    ├─ Build nodes with semantic roles (INPUT, LLM, VALIDATION, OUTPUT)
    ├─ Build edges from parent_node_id relationships
    ├─ Auto-generate hierarchical stages
    ├─ compute_verdict() → graph-level PASS/FAIL
    ├─ critical_path() → performance hotspots
    └─ investigation_path() → failure localization steps
```

---

## 🔄 Detailed Layer Specifications

### Layer 1: Trace Schema — Single Source of Truth
**File**: `phylax/_internal/schema.py`

**Purpose**: Define the immutable, portable trace format that all components operate on.

#### 1.1 Verdict Model
```python
class Verdict(BaseModel):
    """
    Immutable verdict for an LLM call.
    
    DESIGN RULE: Once a verdict is written to a trace, it MUST NEVER
    be recalculated or modified. Maintains trace as audit artifact.
    
    Attributes:
        status: "pass" or "fail" — only two values, ever
        severity: "low" | "medium" | "high" | None — None when passing
        violations: List of human-readable violation messages
    """
    status: Literal["pass", "fail"]
    severity: Optional[SeverityLevel] = None
    violations: list[str] = []
    
    Config: frozen = True  # Enforce immutability
```

#### 1.2 TraceParameters
```python
class TraceParameters(BaseModel):
    """
    LLM request parameters.
    
    Attributes:
        temperature: Sampling temperature (default 0.7)
        max_tokens: Maximum tokens to generate (default 256)
        top_p: Nucleus sampling parameter
        frequency_penalty: Frequency penalty
        presence_penalty: Presence penalty
        stop: Stop sequences
    """
```

#### 1.3 TraceMessage
```python
class TraceMessage(BaseModel):
    """
    A single message in the conversation.
    
    Attributes:
        role: Message role (user, assistant, system)
        content: Message text content
        name: Optional name for the sender
    """
```

#### 1.4 TraceRequest
```python
class TraceRequest(BaseModel):
    """
    The request portion of a trace.
    
    Attributes:
        provider: LLM provider (openai, gemini, groq, mistral, huggingface, ollama)
        model: Model name (gpt-4, gemini-2.5-flash, etc.)
        messages: List of conversation messages
        parameters: LLM parameters (temperature, max_tokens, etc.)
    """
```

#### 1.5 TraceResponse
```python
class TraceResponse(BaseModel):
    """
    The response portion of a trace.
    
    Attributes:
        text: Generated text response
        tokens: Optional list of individual tokens
        latency_ms: Response time in milliseconds
        usage: Optional token usage dict (prompt_tokens, completion_tokens, total_tokens)
    """
```

#### 1.6 TraceRuntime
```python
class TraceRuntime(BaseModel):
    """
    Runtime environment information.
    
    Attributes:
        library: Underlying library used (openai, llama_cpp, transformers, gemini)
        version: Library version string
    """
```

#### 1.7 Trace (Complete Record)
```python
class Trace(BaseModel):
    """
    Complete trace record — the canonical schema for all LLM call traces.
    
    Attributes:
        trace_id: UUID, immutable, auto-generated
        timestamp: ISO-8601 creation time
        execution_id: Groups traces from one program run
        node_id: Unique ID for this trace as a node in execution graph
        parent_node_id: Parent node that triggered this call (for DAG construction)
        request: TraceRequest — input data
        response: TraceResponse — output data
        runtime: TraceRuntime — environment info
        replay_of: Original trace_id if this is a replay
        metadata: Additional user-defined metadata
        verdict: Pass/fail verdict with violations (immutable once set)
        blessed: If true, this trace is a golden reference
    """
```

---

### Layer 2: Decorators — `@trace` and `@expect`
**File**: `phylax/_internal/decorator.py`

**Purpose**: Provide a clean, explicit decorator interface for tracing LLM calls and attaching expectations.

#### 2.1 `@expect` Decorator
```python
def expect(
    must_include: Optional[list[str]] = None,
    must_not_include: Optional[list[str]] = None,
    max_latency_ms: Optional[int] = None,
    min_tokens: Optional[int] = None,
) -> Callable:
    """
    Decorator to define expectations for LLM calls.
    
    Stores expectations in a module-level dict keyed by function reference.
    Must be used WITH @trace — @trace enforces that @expect is present.
    
    Usage:
        @trace(provider="gemini")
        @expect(must_include=["refund"], max_latency_ms=1500)
        def reply(prompt): ...
    """
```

#### 2.2 `@trace` Decorator
```python
def trace(
    provider: str = "openai",
    model: Optional[str] = None,
    capture_layer: Optional[CaptureLayer] = None,
) -> Callable:
    """
    Decorator to trace LLM calls.
    
    Workflow:
    1. Check that @expect is present (raises PHYLAX_E101 if missing)
    2. Get execution context (execution_id, parent_node_id)
    3. Extract messages and parameters from function args/kwargs
    4. Execute the wrapped function and measure latency
    5. Create trace with verdict via _create_trace()
    6. Push/pop node for child tracking
    7. Return original function result
    """
```

#### 2.3 `_extract_messages(args, kwargs)` → `list[dict]`
Extracts conversation messages from function arguments — checks `kwargs["messages"]` first, then first positional arg.

#### 2.4 `_extract_parameters(kwargs)` → `dict`
Extracts LLM parameters (`temperature`, `max_tokens`, `top_p`, etc.) from kwargs.

#### 2.5 `_extract_model(kwargs, result)` → `str`
Extracts model name from kwargs or result object, falls back to `"unknown"`.

#### 2.6 `_create_trace(...)` → `str`
Assembles a complete `Trace` from captured data, evaluates expectations to produce a `Verdict`, stores the trace via `CaptureLayer`, and returns the `node_id`.

---

### Layer 3: Capture Layer
**File**: `phylax/_internal/capture.py`

**Purpose**: Intercept LLM calls, normalize them into the standard trace schema, and store them.

#### 3.1 `CaptureLayer` Class
```python
class CaptureLayer:
    """
    Core capture layer for tracing LLM calls.
    
    Methods:
        __init__(storage_path, auto_store)
            Initialize with optional storage path and auto-store flag.
            
        capture(provider, model, messages, parameters, call_fn, **kwargs) → (response, Trace)
            Execute an LLM call, measure latency, build trace, and optionally store.
            
        context(provider, model) → CaptureContext
            Context manager for manual trace recording.
            
        _extract_response_text(response_data) → str
            Extract text from various response formats:
            - dict with "text" key
            - raw string
            - OpenAI response objects (choices[0].message.content)
            - Fallback: str(response_data)
            
        _extract_usage(response_data) → Optional[dict]
            Extract token usage (prompt_tokens, completion_tokens, total_tokens)
            from response objects.
            
        _detect_library(provider) → str
            Map provider name to library name (openai→openai, local→llama_cpp).
            
        _get_library_version(provider) → str
            Dynamically import provider library and return __version__.
            
        _store_trace(trace) → None
            Save trace via FileStorage to configured storage path.
            
        flush() → list[Trace]
            Flush and store all pending traces (when auto_store=False).
    """
```

#### 3.2 `CaptureContext` Class
```python
class CaptureContext:
    """
    Context for manual trace recording.
    
    Usage:
        with capture_layer.context("openai", "gpt-4") as ctx:
            response = openai.chat.completions.create(...)
            ctx.record(messages, response)
    
    Methods:
        record(messages, response, parameters) → Trace
            Record a manually captured call with measured latency.
    """
```

#### 3.3 `get_capture_layer()` → `CaptureLayer`
Returns the global singleton `CaptureLayer` instance (lazy-initialized).

---

### Layer 4: Execution Context
**File**: `phylax/_internal/context.py`

**Purpose**: Group traces into execution graphs and track causal parent-child relationships.

**Design Principles**: No magic, no AST tricks, no thread hacking. Uses Python's `contextvars` (thread-safe, async-safe).

#### 4.1 Context Variables
```python
_execution_id: ContextVar[str]     # Shared execution ID for all traces in context
_current_node_id: ContextVar[str]  # Current node for parent tracking
_node_stack: ContextVar[list]      # Stack of node IDs for nesting
_node_count: ContextVar[int]       # Counter for nodes in this execution
```

#### 4.2 Key Functions
```python
@contextmanager
def execution() -> Generator[str, None, None]:
    """
    Create an execution context that groups traces.
    
    All traces created inside this context share the same execution_id.
    Parent-child relationships are tracked automatically via node stack.
    
    Sets up: execution_id, node_stack, node_count.
    Cleans up: Resets all context variables on exit.
    """

def get_execution_id() -> str:
    """Get current execution_id, or generate new UUID if outside any context."""

def get_parent_node_id() -> Optional[str]:
    """Get the current parent node ID from the stack. None if first call or outside context."""

def push_node(node_id: str) -> None:
    """Push a node onto the stack (called when entering a traced function)."""

def pop_node() -> None:
    """Pop a node from the stack (called when exiting a traced function)."""

def in_execution_context() -> bool:
    """Check if we're inside an execution context."""
```

---

### Layer 5: Expectation Engine
**Files**: `phylax/_internal/expectations/` (7 files)

**Purpose**: Deterministic rule engine for LLM response validation with logical composition, conditional activation, structural scoping, templates, and self-documentation.

#### 5.1 Base Rules (`rules.py`)

Four deterministic rules, each with a fixed severity:

```python
class Rule(ABC):
    """Base class for expectation rules."""
    name: str
    severity: SeverityLevel  # "low" | "medium" | "high"
    
    @abstractmethod
    def evaluate(self, response_text: str, latency_ms: int) -> RuleResult:
        """Evaluate the rule against a response. Returns RuleResult."""

class MustIncludeRule(Rule):
    """
    Response must include specified substring(s). Severity: LOW.
    
    evaluate(): Case-insensitive substring check. Returns list of missing substrings.
    """

class MustNotIncludeRule(Rule):
    """
    Response must NOT include specified substring(s). Severity: HIGH.
    
    evaluate(): Case-insensitive substring check. Returns list of found forbidden substrings.
    """

class MaxLatencyRule(Rule):
    """
    Response latency must not exceed threshold. Severity: MEDIUM.
    
    evaluate(): Compares latency_ms against max_ms threshold.
    """

class MinTokensRule(Rule):
    """
    Response must have at least N tokens (approximated by word count). Severity: LOW.
    
    evaluate(): Counts words in response text and compares to minimum.
    """
```

#### 5.2 Expectation Groups — Logical Algebra (`groups.py`)

**Axis 1 · Phase 1**: Logical relationships between expectations.

```python
class AndGroup(ExpectationGroup):
    """
    All rules must pass for group to PASS.
    
    evaluate(): Runs all child rules. If any fails, returns FAIL with max severity
    of all failed rules. Violation message lists all failures.
    """

class OrGroup(ExpectationGroup):
    """
    At least one rule must pass for group to PASS.
    
    evaluate(): Runs all child rules. If any passes, returns PASS.
    If ALL fail, returns FAIL with max severity.
    """

class NotGroup(ExpectationGroup):
    """
    Single rule must FAIL for group to PASS.
    
    evaluate(): Evaluates wrapped rule. If rule passes → group FAILS.
    If rule fails → group PASSES. Negates any rule.
    """
```

**Non-negotiable**: Group failure collapses to a single FAIL. No weighting, scoring, or partial passes.

#### 5.3 Conditional Expectations — IF/THEN Logic (`conditionals.py`)

**Axis 1 · Phase 2**: Contracts that activate based on explicit, inspectable conditions.

```python
class InputContains(Condition):
    """Condition: input contains exact substring."""
    evaluate(context) → bool: # Checks context["input"] for substring

class ModelEquals(Condition):
    """Condition: model name equals exact value."""
    evaluate(context) → bool: # Checks context["model"]

class ProviderEquals(Condition):
    """Condition: provider equals exact value."""
    evaluate(context) → bool: # Checks context["provider"]

class MetadataEquals(Condition):
    """Condition: metadata key equals exact value."""
    evaluate(context) → bool: # Checks context["metadata"][key]

class FlagSet(Condition):
    """Condition: explicit flag is set to True."""
    evaluate(context) → bool: # Checks context["flags"][flag_name]

class ConditionalExpectation(Rule):
    """
    Expectation that only activates when condition is met.
    
    evaluate(): If condition is FALSE → returns PASS (skipped, no effect on verdict).
                If condition is TRUE → evaluates wrapped rule normally.
    
    with_context(context): Set context dict for condition evaluation.
    """
```

**Non-negotiable**: Conditions are declared, not inferred. No runtime reasoning. Inactive expectations do not affect verdicts.

#### 5.4 Expectation Scoping — Structural Targeting (`scoping.py`)

**Axis 1 · Phase 3**: Apply expectations to specific graph nodes, providers, stages, or tools.

```python
class ExpectationScope:
    """
    Defines where an expectation applies.
    
    Attributes:
        node_id: Target specific node
        provider: Target specific provider
        stage: Target execution stage ("input", "processing", "output", "final")
        tool: Target specific tool
    
    is_global() → bool: True if no scope restrictions
    matches(context) → bool: All specified fields must match (AND semantics)
    """

class ScopedExpectation(Rule):
    """
    Expectation that only applies within a specific scope.
    
    evaluate(): If scope doesn't match → PASS (skipped).
                If scope matches → evaluates wrapped rule.
    """

# Convenience builders
def for_node(node_id) → ExpectationScope
def for_provider(provider) → ExpectationScope
def for_stage(stage) → ExpectationScope
def for_tool(tool) → ExpectationScope
```

#### 5.5 Expectation Templates — Reuse & DRY (`templates.py`)

**Axis 1 · Phase 4**: Named, reusable expectation sets to prevent contract drift.

```python
class ExpectationTemplate:
    """
    A named, reusable set of expectations.
    
    Attributes:
        name: Unique identifier (e.g., "safe-response", "latency-fast")
        description: Human-readable contract description
        rules: List of Rule objects
        version: Semantic version string
    
    get_rules() → list[Rule]: Return a copy of the template's rules.
    """

class TemplateRegistry:
    """
    Central registry for expectation templates.
    
    register(template) → self: Register (raises ValueError on duplicate)
    register_or_update(template) → self: Register, replacing if exists
    get(name) → ExpectationTemplate: Lookup by name (raises KeyError if missing)
    get_rules(name) → list[Rule]: Get rules directly
    exists(name) → bool
    list_templates() → list[str]: All registered template names
    clear(): Clear all templates (testing only)
    """

# Built-in templates:
# "safe-response" — blocks apologies, errors, harmful content
# "latency-fast" — < 1s latency
# "latency-standard" — < 3s latency
# "latency-slow" — < 10s latency
```

**Non-negotiable**: Templates are static. No parameter auto-tuning. No adaptive templates.

#### 5.6 Expectation Documentation — Self-Describing Contracts (`documentation.py`)

**Axis 1 · Phase 5**: Makes contracts human-readable and exportable.

```python
def describe_rule(rule, indent=0) → str:
    """
    Generate human-readable description of any rule type.
    Handles: MustIncludeRule, MustNotIncludeRule, MaxLatencyRule, MinTokensRule,
             AndGroup, OrGroup, NotGroup, ConditionalExpectation, ScopedExpectation.
    """

def describe_condition(condition) → str:
    """Describe an InputContains, ModelEquals, ProviderEquals, MetadataEquals, or FlagSet."""

def describe_template(template) → str:
    """Generate formatted documentation for a template with all its rules."""

def list_contracts(rules) → str:
    """Generate numbered contract listing for a set of rules."""

def export_contract_markdown(rules, title, description) → str:
    """Export contract as Markdown documentation suitable for README or docs."""

class ContractDocumenter:
    """
    Generates documentation for an Evaluator instance.
    
    describe() → str: Human-readable contract description
    to_markdown(title, description) → str: Markdown export
    """
```

#### 5.7 Evaluator — Rule Orchestrator (`evaluator.py`)

```python
class Evaluator:
    """
    Evaluates rules against LLM responses with fluent API.
    
    Core methods:
        add_rule(rule) → self                  # Add any Rule
        must_include(substrings) → self        # Convenience: MustIncludeRule
        must_not_include(substrings) → self    # Convenience: MustNotIncludeRule
        max_latency_ms(max_ms) → self          # Convenience: MaxLatencyRule
        min_tokens(min_tokens) → self          # Convenience: MinTokensRule
        
    Composition methods (Axis 1):
        and_group(rules, name) → self          # AND group
        or_group(rules, name) → self           # OR group
        not_rule(rule, name) → self            # NOT group
        when_if(condition, rule, name) → self  # Conditional
        set_context(context) → self            # Context for conditionals/scoping
        scoped_for(scope, rule, name) → self   # Scoped expectation
        use_template(name) → self              # Apply template rules
        
    Documentation methods (Axis 1 Phase 5):
        describe() → str                       # Human-readable listing
        to_markdown(title, description) → str  # Markdown export
        
    Evaluation:
        evaluate(response_text, latency_ms) → Verdict
            All rules evaluated (no short-circuit).
            Severity = maximum of all violations.
            Passes context to conditional and scoped expectations.
    """

def evaluate(response_text, latency_ms, must_include, must_not_include, max_latency_ms, min_tokens) → Verdict:
    """Convenience function — creates Evaluator, adds rules, evaluates, returns Verdict."""
```

---

### Layer 6: Raw Evidence Module
**File**: `phylax/_internal/evidence.py`

**Purpose**: Expose raw facts for machine consumption. Observations, not explanations. Data, not insights.

```python
@dataclass
class HashEvidence:
    """Evidence: output hash changed."""
    original_hash: str
    new_hash: str
    match: bool
    to_dict() → dict  # Includes _disclaimer

@dataclass
class LatencyEvidence:
    """Evidence: latency measurement."""
    original_ms: int
    new_ms: int
    delta_ms: int
    to_dict() → dict  # Includes _disclaimer

@dataclass
class PathEvidence:
    """Evidence: execution path divergence."""
    original_path: list[str]
    new_path: list[str]
    diverged: bool
    divergence_point: Optional[str]  # "index_N" or "length_mismatch"
    to_dict() → dict  # Includes _disclaimer

@dataclass
class TimestampEvidence:
    """Evidence: timestamp delta."""
    original_timestamp: str
    new_timestamp: str
    to_dict() → dict  # Includes _disclaimer

def compute_hash(text) → str:
    """SHA256 hash, truncated to 16 chars."""

def compare_outputs(original_text, new_text) → HashEvidence:
    """Compare two outputs and return hash evidence."""

def compare_latency(original_ms, new_ms) → LatencyEvidence:
    """Compare latencies and return evidence."""

def compare_paths(original_path, new_path) → PathEvidence:
    """Compare execution paths and return evidence."""
```

---

### Layer 7: Error System
**File**: `phylax/_internal/errors.py`

**Purpose**: Canonical error codes for machine-readable failures. No explanations. No diagnostics. No suggestions.

| Error Code | Class | Meaning |
|------------|-------|---------|
| `PHYLAX_E000` | `PhylaxError` | Base class |
| `PHYLAX_E101` | `MissingExpectationsError` | Function has no `@expect` decorator |
| `PHYLAX_E102` | `EmptyExecutionGraphError` | Execution graph contains no nodes |
| `PHYLAX_E103` | `NoVerdictPathError` | Execution has no verdict-producing nodes |
| `PHYLAX_E201` | `NonDeterministicGoldenError` | Attempted to bless a non-deterministic trace |
| `PHYLAX_E202` | `ReplayWithoutGoldenError` | Replay requested but no golden reference exists |
| `PHYLAX_E203` | `GoldenHashMismatchError` | Output hash differs from golden reference |
| `PHYLAX_E301` | `MeaninglessConfigurationError` | Configuration cannot produce verdicts |

---

### Layer 8: Execution Graph Engine
**File**: `phylax/_internal/graph.py` (~834 lines)

**Purpose**: Model execution as a read-only Directed Acyclic Graph with semantic roles, hierarchical stages, performance analysis, diffing, investigation, and enterprise hardening.

#### 8.1 Semantic Node Roles (Phase 19)
```python
class NodeRole(str, Enum):
    """
    Semantic role of a node in the execution graph.
    
    INPUT       = "input"        # User input, API request
    TRANSFORM   = "transform"    # Data transformation, parsing
    LLM         = "llm"          # LLM call (default)
    TOOL        = "tool"         # Tool/function call
    VALIDATION  = "validation"   # Expectation check
    OUTPUT      = "output"       # Final output
    """
```

#### 8.2 Graph Models
```python
class GraphNode(BaseModel):      # Immutable node: node_id, trace_id, role, human_label,
                                  # description, model, provider, latency_ms, verdict_status, blessed

class GraphEdge(BaseModel):      # Immutable edge: from_node, to_node, edge_type ("calls"|"data_flow")

class GraphStage(BaseModel):     # Phase 20: Hierarchical grouping of nodes by role
                                 # stage_id, name, node_ids, total_latency_ms, has_failure, collapsed

class GraphVerdict(BaseModel):   # Phase 16: Graph-level verdict
                                 # status, first_failing_node, failed_count, tainted_count, message

class NodeDiff(BaseModel):       # Phase 23: Difference in a single node between two graphs
                                 # node_label, change_type ("added"|"removed"|"changed"),
                                 # latency_delta_ms, verdict_changed

class GraphDiff(BaseModel):      # Phase 23: Complete diff between two graphs
                                 # execution_a, execution_b, added_nodes, removed_nodes,
                                 # changed_nodes, total_changes, latency_delta_ms, verdict_changed
```

#### 8.3 `ExecutionGraph` Class — Full API
```python
class ExecutionGraph(BaseModel):
    """
    Complete execution graph (immutable after construction).
    
    Construction:
        from_traces(traces) → ExecutionGraph
            Build graph from traces with same execution_id.
            Auto-infers semantic roles via _infer_semantics().
            Auto-generates hierarchical stages via _generate_stages().
    
    Traversal:
        get_children(node_id) → list[str]     # Direct children
        get_parent(node_id) → Optional[str]    # Parent node
        get_node(node_id) → Optional[GraphNode]
        topological_order() → list[str]        # Kahn's algorithm
        get_failed_nodes() → list[GraphNode]
        get_tainted_nodes(failed_node_id) → list[str]  # Blast radius (BFS)
    
    Verdict (Phase 16):
        compute_verdict() → GraphVerdict
            Graph fails if any node fails.
            First failure = first failing node in topological order.
            Tainted = all downstream nodes of failures.
    
    Performance Analysis (Phase 18):
        critical_path() → dict
            Longest latency chain via dynamic programming.
            Returns: path, total_latency_ms, bottleneck_node, bottleneck_latency_ms
            
        find_bottlenecks(top_n=3) → list[dict]
            Slowest nodes sorted by latency.
            Returns: node_id, label, latency_ms, percent_of_total
    
    Graph Diff (Phase 23):
        diff_with(other) → GraphDiff
            Compare by semantic label (not UUID).
            50ms latency threshold for "changed" classification.
    
    Investigation (Phase 24):
        investigation_path() → list[dict]
            Deterministic failure localization (not AI):
            1. Examine first failing node
            2. Review input (parent node)
            3. Review validation rules
            4. Review blast radius (downstream nodes)
    
    Enterprise (Phase 25):
        compute_hash() → str           # SHA256 of canonical JSON
        to_snapshot() → ExecutionGraph  # New graph with integrity_hash + snapshot_at
        export_json(pretty=True) → str  # JSON artifact for auditing
        verify_integrity() → bool       # Compare stored hash vs computed hash
    """
```

#### 8.4 Helper Functions
```python
def _get_label(trace) → str:
    """Generate short label from first message content (truncated to 30 chars)."""

def _infer_semantics(trace, index, total) → (NodeRole, human_label, description):
    """
    Phase 19: Infer semantic role based on:
    - Message content keywords (check/validate → VALIDATION, parse/extract → TRANSFORM)
    - Position (first → INPUT, last → OUTPUT)
    - Verdict presence (has verdict → VALIDATION)
    - Default: LLM
    """

def _generate_stages(nodes) → list[GraphStage]:
    """
    Phase 20: Group consecutive nodes with same role into stages.
    Stage names: Input Processing, Data Transformation, LLM Processing,
                 Tool Execution, Validation, Output Generation.
    """
```

---

### Layer 9: LLM Provider Adapters
**Files**: `phylax/_internal/adapters/` (7 files)

**Purpose**: Unified interface for all supported LLM providers with automatic tracing.

All adapters share the same pattern:

```python
class <Provider>Adapter:
    """
    Adapter for <Provider> API.
    
    __init__(api_key=None, capture_layer=None):
        api_key defaults to env variable. capture_layer defaults to global singleton.
        
    @property client:
        Lazy-load the provider's SDK client.
        Raises ImportError with install instructions if package missing.
        
    chat_completion(model, messages, temperature, max_tokens, **kwargs) → (response, Trace):
        Create a chat completion with automatic tracing.
        Builds a closure (make_call) that executes the actual API call.
        Delegates to CaptureLayer.capture() for tracing.
        
    generate(prompt, model, temperature, max_tokens, **kwargs) → (response, Trace):
        Convenience wrapper — converts prompt to messages format
        and calls chat_completion().
    """
```

| Adapter | SDK Used | Default Model | Extra Methods |
|---------|----------|---------------|---------------|
| `OpenAIAdapter` | `openai.OpenAI` | gpt-4 | `completion()` for legacy completions API |
| `GeminiAdapter` | `google.genai.Client` | gemini-2.5-flash | Converts messages to Gemini `Content` format |
| `GroqAdapter` | `groq.Groq` | llama3-70b-8192 | — |
| `MistralAdapter` | `mistralai.Mistral` | mistral-large-latest | — |
| `HuggingFaceAdapter` | `huggingface_hub.InferenceClient` | meta-llama/Llama-3.1-8B-Instruct | — |
| `OllamaAdapter` | `ollama.Client` | llama3 | `list_models()` for local model discovery |

---

### Layer 10: File Storage Backend
**File**: `server/storage/files.py` (~393 lines)

**Purpose**: Zero-infrastructure trace persistence using JSON files as ground truth.

```
~/.Phylax/
├── traces/
│   ├── 2026-02-22/
│   │   ├── <trace_id_1>.json
│   │   └── <trace_id_2>.json
│   └── 2026-02-21/
│       └── ...
├── graphs/
│   └── <execution_id>.json
└── config.yaml
```

```python
class FileStorage:
    """
    Filesystem-based trace storage.
    
    CRUD Operations:
        save_trace(trace) → str              # Save to date-organized directory
        get_trace(trace_id) → Optional[Trace] # Search through date directories
        list_traces(limit, offset, model, provider, date) → list[Trace]
        count_traces(model, provider, date) → int
        delete_trace(trace_id) → bool
        update_trace(trace) → bool
    
    Lineage:
        get_lineage(trace_id) → list[Trace]
            Traverses up to root via replay_of, then finds all descendants.
    
    Golden Management:
        bless_trace(trace_id) → Optional[Trace]
            Sets blessed=True, computes output_hash, stores blessed_at timestamp.
            
        unbless_trace(trace_id) → bool
        list_blessed_traces() → list[Trace]
        get_golden_for_model(model, provider) → Optional[Trace]
    
    Graph Operations (Phase 14):
        get_traces_by_execution(execution_id) → list[Trace]
        get_execution_graph(execution_id) → Optional[ExecutionGraph]
        save_graph(graph) → str
        load_graph(execution_id) → Optional[ExecutionGraph]
        list_executions() → list[str]
    """
```

---

### Layer 11: SQLite Index (Optional)
**File**: `server/storage/sqlite.py` (~207 lines)

**Purpose**: Optional indexing layer for faster queries over JSON files.

```python
class SQLiteIndex:
    """
    SQLite-based index for fast trace queries.
    
    Schema:
        traces (
            trace_id TEXT PRIMARY KEY,
            timestamp TEXT,
            provider TEXT,
            model TEXT,
            latency_ms INTEGER,
            replay_of TEXT,
            file_path TEXT
        )
        
    Indexes: timestamp DESC, model, provider, replay_of
    
    Methods:
        index_trace(trace, file_path): Add trace to index
        search(limit, offset, model, provider, date) → list[dict]
        count(model, provider, date) → int
        get_lineage_ids(trace_id) → list[str]
    """
```

---

### Layer 12: FastAPI Server
**File**: `server/main.py`

**Purpose**: Expose traces via HTTP, support replay and comparison, serve UI.

```python
app = FastAPI(title="Phylax", version="1.0.0")

# CORS: localhost:3000, localhost:8000
# Routers: traces, replay, chat (all under /v1 prefix)
# Static files: /ui → ui/, /assets → assets/

GET  /          → API info
GET  /health    → {"status": "healthy"}
```

#### 12.1 Traces Routes (`server/routes/traces.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/traces` | GET | List traces with filtering (limit, offset, model, provider, date) |
| `/v1/traces/{id}` | GET | Get single trace |
| `/v1/traces` | POST | Create new trace |
| `/v1/traces/{id}` | DELETE | Delete trace |
| `/v1/traces/{id}/lineage` | GET | Lineage chain (original → replays) |
| `/v1/executions` | GET | List all execution IDs (Phase 14) |
| `/v1/executions/{id}` | GET | Get all traces for an execution |
| `/v1/executions/{id}/graph` | GET | Get execution DAG (Phase 14) |
| `/v1/executions/{id}/analysis` | GET | Performance analysis: critical path + bottlenecks (Phase 18) |
| `/v1/executions/{a}/diff/{b}` | GET | Compare two execution graphs (Phase 23) |
| `/v1/executions/{id}/investigate` | GET | Failure localization steps (Phase 24) |
| `/v1/executions/{id}/snapshot` | GET | Immutable snapshot with SHA256 (Phase 25) |
| `/v1/executions/{id}/export` | GET | Export graph as JSON artifact (Phase 25) |
| `/v1/executions/{id}/verify` | GET | Verify graph integrity (Phase 25) |

#### 12.2 Replay Routes (`server/routes/replay.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/replay/{id}` | POST | Replay a trace with optional model/parameter overrides |
| `/v1/replay/{id}/preview` | GET | Preview what a replay would execute |
| `/v1/executions/{id}/replay` | POST | Subgraph replay from specific node (Phase 17) |

#### 12.3 Chat Routes (`server/routes/chat.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/chat/completions` | POST | OpenAI-compatible chat endpoint with automatic tracing |

---

### Layer 13: CLI — Command Line Interface
**File**: `cli/main.py` (~516 lines)

**Purpose**: Primary user interface for CI enforcement and trace management.

| Command | Function | Description |
|---------|----------|-------------|
| `phylax init` | `cmd_init(args)` | Initialize `~/.phylax/config.yaml` with default settings. `--force` to overwrite. |
| `phylax server` | `cmd_server(args)` | Start FastAPI server via uvicorn. `--host`, `--port`, `--reload` flags. |
| `phylax list` | `cmd_list(args)` | List traces with status icons (✅/❌/⏳). `--failed` for failed only, `--model`/`--provider` filters, `--limit`. |
| `phylax show <id>` | `cmd_show(args)` | Display trace details: verdict, messages, response. `--json` for raw output. |
| `phylax replay <id>` | `cmd_replay(args)` | Re-execute a trace. `--model` to override, `--dry-run` to simulate. |
| `phylax bless <id>` | `cmd_bless(args)` | Mark trace as golden reference. Computes output hash. `--force` to override existing golden. `--yes` to skip confirmation. |
| `phylax check` | `cmd_check(args)` | **CI command**: Replay all golden traces, compare output hashes. Exit 0 = all pass, exit 1 = any fail. `--json` for report. |
| `phylax graph-check` | `cmd_graph_check(args)` | **Phase 16**: Evaluate execution graphs. Fail CI if any graph fails. Reports first failing node. |

---

### Layer 14: Web UI — Failure-First Inspector
**Files**: `ui/index.html` (~1282 lines), `ui/app.js` (~826 lines)

**Purpose**: Auxiliary visual interface for inspecting traces, managing golden baselines, and failure forensics.

**Design Principle**: When something breaks, Phylax explains why faster than a human can.

#### UI Features
- **Failed-Only Default Mode** (Phase 11): Opens showing only failed traces
- **Failure Summary**: Failed/Passed/Total counts in header
- **Trace Sidebar**: Searchable list with verdict badges
- **Trace Detail Panel**: Full request/response with syntax highlighting
- **Verdict Display**: Status, severity, violations list with color-coded badges
- **Golden Management**: Bless/unbless buttons, golden badges on blessed traces
- **Graph Visualization**: DAG rendering with node roles and latency
- **Forensics Mode** (Phase 22): Deep investigation interface
- **Dark Theme**: Professional dark UI with custom scrollbars
- **Responsive**: Flexbox layout that works at various screen sizes

#### Key JS Functions
```javascript
loadTraces()          // Fetch traces from API, update stats, render list
selectTrace(id)       // Load and display trace detail
updateStats()         // Update header counters
renderTraceList()     // Render filtered trace list in sidebar
setFilter(filter)     // Switch between "all", "failed", "passed"
blessTrace(id)        // POST to /v1/traces/{id}/bless
```

---

## 📁 Complete File Structure & Purposes

```
Phylax/
│
├── phylax/                          # Main package (PyPI-distributed)
│   ├── __init__.py                  # Public API: exports trace, expect, execution,
│   │                                  Trace, Verdict, ExecutionGraph, all 6 adapters,
│   │                                  all Axis 2 surface rules and adapters
│   │                                  __version__ = "1.3.3"
│   │
│   ├── _internal/                   # Internal implementation (not for direct import)
│   │   ├── __init__.py              # Module docstring only
│   │   ├── schema.py               # Trace schema: Trace, TraceRequest, TraceResponse,
│   │   │                             TraceRuntime, TraceMessage, TraceParameters, Verdict
│   │   ├── decorator.py            # @trace and @expect decorators
│   │   │                             _extract_messages(), _extract_parameters(),
│   │   │                             _extract_model(), _create_trace()
│   │   ├── capture.py              # CaptureLayer, CaptureContext,
│   │   │                             get_capture_layer() singleton
│   │   ├── context.py              # execution() context manager,
│   │   │                             get_execution_id(), get_parent_node_id(),
│   │   │                             push_node(), pop_node(), in_execution_context()
│   │   ├── graph.py                # ExecutionGraph, GraphNode, GraphEdge, GraphStage,
│   │   │                             GraphVerdict, GraphDiff, NodeDiff, NodeRole
│   │   │                             ~834 lines: from_traces(), compute_verdict(),
│   │   │                             critical_path(), find_bottlenecks(), diff_with(),
│   │   │                             investigation_path(), compute_hash(), to_snapshot(),
│   │   │                             verify_integrity(), export_json()
│   │   ├── errors.py               # PhylaxError base + 7 specific error codes
│   │   │                             PHYLAX_E101 through PHYLAX_E301
│   │   ├── evidence.py             # HashEvidence, LatencyEvidence, PathEvidence,
│   │   │                             TimestampEvidence, compare_outputs(),
│   │   │                             compare_latency(), compare_paths()
│   │   │
│   │   ├── expectations/            # Deterministic rule engine (5 Axis 1 phases)
│   │   │   ├── __init__.py          # Re-exports all rules, groups, conditionals,
│   │   │   │                          scoping, templates, documentation
│   │   │   ├── rules.py             # 4 base rules: MustIncludeRule, MustNotIncludeRule,
│   │   │   │                          MaxLatencyRule, MinTokensRule, RuleResult
│   │   │   ├── evaluator.py         # Evaluator class (fluent API), evaluate() function
│   │   │   ├── groups.py            # Phase 1: AndGroup, OrGroup, NotGroup
│   │   │   ├── conditionals.py      # Phase 2: InputContains, ModelEquals, ProviderEquals,
│   │   │   │                          MetadataEquals, FlagSet, ConditionalExpectation
│   │   │   ├── scoping.py           # Phase 3: ExpectationScope, ScopedExpectation,
│   │   │   │                          for_node(), for_provider(), for_stage(), for_tool()
│   │   │   ├── templates.py         # Phase 4: ExpectationTemplate, TemplateRegistry,
│   │   │   │                          4 built-in templates (safe-response, latency-*)
│   │   │   └── documentation.py     # Phase 5: describe_rule(), describe_condition(),
│   │   │                              describe_template(), list_contracts(),
│   │   │                              export_contract_markdown(), ContractDocumenter
│   │   │
│   │   └── adapters/                # LLM provider adapters (lazy-loaded)
│   │       ├── __init__.py           # Re-exports all 6 adapters
│   │       ├── openai.py            # OpenAIAdapter: chat_completion(), completion()
│   │       ├── gemini.py            # GeminiAdapter: chat_completion(), generate()
│   │       ├── groq.py              # GroqAdapter: chat_completion(), generate()
│   │       ├── mistral.py           # MistralAdapter: chat_completion(), generate()
│   │       ├── huggingface.py       # HuggingFaceAdapter: chat_completion(), generate()
│   │       ├── ollama.py            # OllamaAdapter: chat_completion(), generate(),
│   │       │                          list_models()
│   │       └── llama.py             # LlamaAdapter (local llama.cpp support)
│   │
│   │   ├── surfaces/                # Axis 2: Surface Abstraction Layer
│   │   │   ├── __init__.py          # Re-exports all surface models, rules, adapters
│   │   │   ├── surface.py           # Surface, SurfaceRule, SurfaceAdapter, SurfaceEvaluator,
│   │   │   │                          SurfaceVerdict, SurfaceRegistry (Phase 2.0)
│   │   │   ├── text.py              # TextSurfaceAdapter (Phase 2.0)
│   │   │   ├── structured.py        # FieldExistsRule, FieldNotExistsRule, TypeEnforcementRule,
│   │   │   │                          ExactValueRule, EnumEnforcementRule, ArrayBoundsRule,
│   │   │   │                          StructuredSurfaceAdapter (Phase 2.1)
│   │   │   ├── tools.py             # ToolPresenceRule, ToolCountRule, ToolArgumentRule,
│   │   │   │                          ToolOrderingRule, ToolSurfaceAdapter (Phase 2.2)
│   │   │   ├── execution_trace.py   # StepCountRule, ForbiddenTransitionRule,
│   │   │   │                          RequiredStageRule, ExecutionTraceSurfaceAdapter (Phase 2.3)
│   │   │   └── stability.py         # ExactStabilityRule, AllowedDriftRule,
│   │   │                              StabilitySurfaceAdapter (Phase 2.4)
│   │
│   ├── cli/                         # CLI entry point (phylax command)
│   │   ├── __init__.py
│   │   └── main.py                  # Alias/wrapper for top-level cli/main.py
│   │
│   ├── server/                      # Server entry point
│   │   └── (wrappers for top-level server/)
│   │
│   ├── ui/                          # Packaged UI files
│   │   └── (HTML/JS/CSS)
│   │
│   └── assets/                      # Logo, favicon
│       └── (PNG files)
│
├── sdk/                             # Development SDK (mirrors phylax/_internal/)
│   ├── __init__.py                  # Development imports
│   ├── schema.py                    # → same as phylax/_internal/schema.py
│   ├── capture.py                   # → same as phylax/_internal/capture.py
│   ├── context.py                   # → same as phylax/_internal/context.py
│   ├── decorator.py                 # → same as phylax/_internal/decorator.py
│   ├── graph.py                     # → same as phylax/_internal/graph.py
│   ├── adapters/                    # Subset of adapters for development
│   │   ├── openai.py
│   │   ├── gemini.py
│   │   └── llama.py
│   └── expectations/                # Development expectations
│       ├── __init__.py
│       ├── rules.py
│       └── evaluator.py
│
├── server/                          # FastAPI server (standalone)
│   ├── __init__.py
│   ├── main.py                      # FastAPI app: CORS, routers, static files,
│   │                                  /health, root endpoint
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── traces.py                # Trace CRUD, executions, graphs, analysis,
│   │   │                              diff, investigate, snapshot, export, verify
│   │   ├── replay.py                # Replay with overrides, preview, subgraph replay
│   │   └── chat.py                  # OpenAI-compatible /v1/chat/completions
│   └── storage/
│       ├── __init__.py
│       ├── files.py                 # FileStorage: JSON file persistence
│       │                              ~393 lines: CRUD, golden management, graphs
│       └── sqlite.py                # SQLiteIndex: optional fast query index
│                                      ~207 lines: schema, search, lineage
│
├── cli/                             # CLI (standalone)
│   ├── __init__.py
│   └── main.py                      # argparse commands: init, server, list, show,
│                                      replay, bless, check, graph-check
│                                      ~516 lines
│
├── ui/                              # Web UI (static files)
│   ├── index.html                   # Full UI layout + CSS (~1282 lines)
│   │                                  Dark theme, flexbox layout, responsive
│   └── app.js                       # UI logic (~826 lines)
│                                      Trace loading, filtering, selection,
│                                      golden management, graph visualization
│
├── tests/                           # Test suite (208 tests)
│   ├── __init__.py
│   ├── test_axis1_comprehensive.py  # Axis 1 phases 1-5 tests
│   ├── test_axis2_invariants.py     # 15 invariant guard tests
│   ├── test_conditional_expectations.py
│   ├── test_context.py              # Execution context tests
│   ├── test_contract.py             # API contract tests
│   ├── test_expectation_documentation.py
│   ├── test_expectation_groups.py   # AND/OR/NOT tests
│   ├── test_expectation_scoping.py  # Scoping tests
│   ├── test_expectation_templates.py
│   ├── test_expectations.py         # Base rule tests
│   └── test_schema.py              # Trace schema tests
│
├── examples/                        # Integration & feature test scripts
│   ├── test_execution_context.py
│   ├── test_expectations.py
│   ├── test_gemini_call.py
│   ├── test_graph_ascii.py
│   ├── test_graph_features.py
│   ├── test_graph_unit.py
│   ├── test_openai_call.py
│   ├── test_phases_19_25.py
│   └── ci/
│       ├── github_actions.yml       # CI workflow example
│       └── pytest_example.py
│
├── demos/                           # Runnable demonstration scripts
│   ├── 01_basic_trace.py            # Basic tracing
│   ├── 02_expectations.py           # All @expect rules
│   ├── 03_execution_context.py      # Trace grouping
│   ├── 04_graph_nodes.py            # Graph API
│   ├── 05_golden_workflow.py        # CI workflow
│   ├── 06_raw_evidence.py           # Evidence API
│   ├── 07_error_contracts.py        # Error codes
│   ├── 08_composition.py            # Expectation groups
│   ├── 09_conditionals.py           # Conditional expectations
│   ├── 10_scoping.py                # Expectation scoping
│   ├── 11_templates.py              # Templates & registry
│   ├── 12_documentation.py          # Self-documenting contracts
│   ├── 13_gemini_live.py            # Live Gemini integration
│   └── README.md
│
├── docs/                            # Documentation
│   ├── quickstart.md                # 10 min to CI enforcement
│   ├── mental-model.md              # What Phylax is/isn't
│   ├── contract.md                  # API stability guarantees
│   ├── correct-usage.md             # Intended usage patterns
│   ├── errors.md                    # Error code reference
│   ├── execution-context.md         # Execution context usage
│   ├── failure-modes.md             # Error behavior
│   ├── failure-playbook.md          # Failure localization procedures
│   ├── graph-model.md               # How to read graphs
│   ├── invariants.md                # Semantic invariants
│   ├── non-goals.md                 # 5 permanent constraints
│   ├── performance.md               # Scale limits
│   ├── providers.md                 # LLM provider reference
│   ├── versioning.md                # Release policy
│   └── when-not-to-use.md           # Anti-patterns
│
├── assets/                          # Static assets
│   ├── logo/                        # Phylax logo PNG
│   └── dashboard/                   # Dashboard screenshots
│
├── config.yaml                      # Default configuration
├── pyproject.toml                   # Package metadata & dependencies
├── requirements.txt                 # Dev dependencies
├── README.md                        # Project README
├── DOCUMENTATION.md                 # Complete technical reference
├── DEVELOPMENT.md                   # Contributor guide
├── CHANGELOG.md                     # Version history
└── LICENSE                          # MIT License
```

---

## 🔑 Design Patterns & Approaches

### 1. **Immutable Data Models (Pydantic Frozen)**
- All trace-related models (`Trace`, `Verdict`, `GraphNode`, `GraphEdge`, etc.) use `Config: frozen = True`
- Prevents accidental mutation after creation
- Traces are audit artifacts — once written, never modified (except bless/unbless)

### 2. **Decorator Pattern for Tracing**
- `@trace` intercepts function calls transparently
- `@expect` stores expectations per function in a module-level dict
- Explicit enforcement: `@trace` raises `PHYLAX_E101` if `@expect` is missing

### 3. **Adapter Pattern for Multi-Provider**
- All 6 LLM adapters share a uniform interface (`chat_completion()`, `generate()`)
- Lazy-loading via `@property client` avoids import errors for uninstalled SDKs
- Provider-specific logic is encapsulated in each adapter's `make_call()` closure

### 4. **Singleton Pattern for Global State**
- `get_capture_layer()` returns a global `CaptureLayer` instance
- `get_registry()` returns a global `TemplateRegistry`
- Prevents multiple instances from conflicting

### 5. **Strategy Pattern for Rules**
- All rules implement the `Rule` abstract base class with `evaluate(response_text, latency_ms) → RuleResult`
- Groups, conditionals, and scoped expectations are themselves `Rule` subclasses
- The `Evaluator` iterates all rules uniformly

### 6. **Composite Pattern for Expectation Groups**
- `AndGroup`, `OrGroup`, and `NotGroup` contain child rules and are themselves rules
- Enables arbitrary nesting: `AND(OR(rule1, rule2), NOT(rule3))`
- Binary PASS/FAIL collapses up through the tree

### 7. **Context Variables for Execution Tracking**
- Python `contextvars` provide thread-safe, async-safe execution context
- Node stack tracks parent-child relationships without global mutable state
- Optional usage — code works unchanged without `execution()` context

### 8. **Zero-Infrastructure Storage**
- JSON files as ground truth — no database server required
- Date-organized directory structure for natural temporal browsing
- SQLite index as optional optimization, not a requirement

### 9. **Evidence Over Analysis**
- All evidence classes expose raw data with `_disclaimer` field
- No causal language ("root cause", "reason") in user-facing output
- Investigation paths are structural graph traversal, not AI reasoning

### 10. **CI-First Design**
- `phylax check` is the primary interface — everything else supports it
- Exit codes 0/1 integrate with any CI system
- UI and API are explicitly labeled "auxiliary control surfaces"

---

## 🚀 Execution Flow (Complete User Journey)

### Phase A: Setup
```
Developer installs Phylax:
  pip install phylax[all]

Developer initializes:
  phylax init → creates ~/.phylax/config.yaml

Developer starts server (optional):
  phylax server → FastAPI on port 8000 + UI at /ui
```

### Phase B: Write Traced Code
```
Developer writes application code:

  from phylax import trace, expect, execution, GeminiAdapter

  @trace(provider="gemini")
  @expect(must_include=["hello"], max_latency_ms=5000)
  def greet(name):
      adapter = GeminiAdapter()
      response, _ = adapter.generate(
          prompt=f"Say hello to {name}",
          model="gemini-2.5-flash",
      )
      return response

  with execution() as exec_id:
      step1 = greet("Alice")
      step2 = greet("Bob")

What happens internally:
  1. @trace checks @expect exists (PHYLAX_E101 if missing)
  2. execution() creates shared execution_id via contextvars
  3. GeminiAdapter.generate() → CaptureLayer.capture()
  4. CaptureLayer measures latency, builds Trace
  5. Evaluator applies expectations → Verdict (PASS/FAIL)
  6. FileStorage.save_trace() → ~/.Phylax/traces/2026-02-22/<uuid>.json
  7. Node stack tracks parent-child for DAG construction
```

### Phase C: Establish Golden Baseline
```
Developer reviews traces:
  phylax list                    # See all traces
  phylax show <trace_id>         # Inspect details

Developer blesses a good trace:
  phylax bless <trace_id>
    → Computes SHA256 output hash
    → Stores hash in trace metadata
    → Sets blessed=True
    → This is now the golden reference
```

### Phase D: CI Enforcement
```
CI pipeline runs:
  phylax check
    ├── Load all blessed traces
    ├── For each golden:
    │   ├── Replay with same parameters
    │   ├── Compute hash of new output
    │   ├── Compare with golden hash
    │   ├── MATCH → ✅ PASS
    │   └── MISMATCH → ❌ FAIL
    ├── Exit 0: All pass → CI green
    └── Exit 1: Any fail → CI red, build blocked
```

### Phase E: Debug Failures (Optional)
```
Developer investigates via UI or CLI:
  phylax server → http://localhost:8000/ui
    ├── Failed-only mode shows broken traces
    ├── Select trace → see full request/response
    ├── View violations and severity
    ├── Check execution graph
    │   └── investigation_path() → structured steps:
    │       1. Examine first failing node
    │       2. Review input (parent node)
    │       3. Check validation rules
    │       4. Assess blast radius
    └── Compare graphs via diff endpoint
```

---

## 📊 Summary Table

| Layer | Purpose | Key Files | Lines | Key Classes/Functions |
|-------|---------|-----------|-------|----------------------|
| **1. Schema** | Trace data model | `_internal/schema.py` | ~130 | `Trace`, `Verdict`, `TraceRequest`, `TraceResponse` |
| **2. Decorators** | Tracing & expectations | `_internal/decorator.py` | ~240 | `@trace`, `@expect`, `_create_trace()` |
| **3. Capture** | LLM call interception | `_internal/capture.py` | ~280 | `CaptureLayer`, `CaptureContext` |
| **4. Context** | Execution grouping | `_internal/context.py` | ~110 | `execution()`, `push_node()`, `pop_node()` |
| **5. Expectations** | Rule engine (5 phases) | `_internal/expectations/` | ~1450+ | `Evaluator`, 4 rules, groups, conditionals, scoping, templates, docs |
| **6. Evidence** | Raw facts | `_internal/evidence.py` | ~160 | `HashEvidence`, `LatencyEvidence`, `PathEvidence` |
| **7. Errors** | Error codes | `_internal/errors.py` | ~95 | `PHYLAX_E101`–`PHYLAX_E301` |
| **8. Graph** | Execution DAGs | `_internal/graph.py` | ~834 | `ExecutionGraph`, `GraphNode`, `NodeRole`, `GraphDiff` |
| **9. Adapters** | LLM providers | `_internal/adapters/` | ~700+ | 6 adapters: OpenAI, Gemini, Groq, Mistral, HF, Ollama |
| **10. Storage** | File persistence | `server/storage/files.py` | ~393 | `FileStorage` (JSON ground truth) |
| **11. SQLite** | Fast queries | `server/storage/sqlite.py` | ~207 | `SQLiteIndex` (optional optimization) |
| **12. Server** | REST API | `server/` | ~850+ | FastAPI, 30+ endpoints across 3 route modules |
| **13. CLI** | CI interface | `cli/main.py` | ~516 | 8 commands: init, server, list, show, replay, bless, check, graph-check |
| **14. UI** | Web inspector | `ui/` | ~2100+ | Failure-first dark-theme inspector |
| **15. Tests** | Verification | `tests/` | 208 tests | Schema, expectations, context, invariants |

---

## 🎓 Key Architectural Highlights

✅ **Deterministic, Not AI**: Verdicts are PASS/FAIL — never scored, never probabilistic, never LLM-based  
✅ **Immutable Traces**: Write-once audit artifacts with Pydantic frozen models  
✅ **CI-First Design**: `phylax check` exit codes drive CI pipelines  
✅ **Zero Infrastructure**: JSON files as ground truth, no database required  
✅ **Multi-Provider**: 6 LLM adapters with unified interface and lazy-loading  
✅ **Rich Expectation Algebra**: 4 rules × logical composition × conditionals × scoping × templates × self-documentation  
✅ **Execution Graphs**: DAGs with semantic roles, performance analysis, diffing, investigation, and enterprise hardening  
✅ **Evidence, Not Analysis**: Raw facts with disclaimers — interpretation is external  
✅ **Machine-Readable Errors**: PHYLAX_Exxx codes, no prose  
✅ **Modular & Testable**: Each layer independently developed and tested (208 tests)  
✅ **Doctrine Frozen**: Semantic invariants enforced by guard tests that fail the build

---

## 🔐 Security & Configuration

### Environment Variables
```bash
GOOGLE_API_KEY="..."          # Gemini
OPENAI_API_KEY="..."          # OpenAI
GROQ_API_KEY="..."            # Groq
MISTRAL_API_KEY="..."         # Mistral
HF_TOKEN="..."                # HuggingFace
OLLAMA_HOST="http://..."      # Ollama (default: localhost:11434)
PHYLAX_HOME="~/.phylax"       # Config directory (optional)
```

### CORS Policy
```python
allow_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
```

### Storage Layout
```
~/.Phylax/
├── config.yaml           # User configuration
├── traces/               # Trace JSON files (by date)
│   └── YYYY-MM-DD/
│       └── <trace_id>.json
├── graphs/               # Saved execution graphs
│   └── <execution_id>.json
└── index.sqlite          # Optional SQLite index
```

---

## 📈 Version History Highlights

| Version | Date | Key Changes |
|---------|------|-------------|
| **1.3.3** | 2026-02-22 | Axis 2 Phase 2.4: Cross-Run Stability Enforcement |
| **1.3.2** | 2026-02-22 | Axis 2 Phase 2.3: Execution Trace Enforcement |
| **1.3.1** | 2026-02-22 | Axis 2 Phase 2.2: Tool & Function Call Invariants |
| **1.3.0** | 2026-02-22 | Axis 2 Phase 2.1: Structured Output Enforcement |
| **1.3.0a0** | 2026-02-22 | Axis 2 Phase 2.0: Surface Abstraction Layer |
| **1.2.6** | 2026-02-14 | Context manager fix for exception propagation |
| **1.2.5** | 2026-02-12 | Evidence purity (first_failing_node rename), google-genai update |
| **1.2.4** | 2026-02-10 | Axis 2 readiness audit, 15 invariant guard tests, doctrine freeze |
| **1.1.6** | 2026-02-07 | CLI `--version` flag |
| **1.1.5** | 2026-02-07 | Trace ID search in UI |
| **1.1.4** | 2026-02-07 | Golden Reference UI (bless/unbless from interface) |
| **1.1.3** | 2026-02-07 | Fixed expectations module exports |
| **1.1.2** | 2026-02-07 | Adapters exported from main package |

---

**Last Updated**: February 22, 2026  
**Architecture Version**: 1.3.3 (Axis 2 Complete — Surface Abstraction Layer with 17 enforcement rules across 5 surface types)
