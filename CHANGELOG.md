# Changelog

All notable changes to Phylax.

## [1.4.0] - 2026-02-28 — Stable Launch: Scale Safety & Misuse Resistance

### Added — Axis 3: Scale Safety & Misuse Resistance

#### Phase 3.1: Metric Foundation Layer
- **`phylax/_internal/metrics/identity.py`**: `ExpectationIdentity` with deterministic SHA256 hashing, canonical serialization, frozen immutability
- **`phylax/_internal/metrics/ledger.py`**: Append-only `EvaluationLedger` with `LedgerEntry` (JSONL persistence, windowed query support)
- **`phylax/_internal/metrics/aggregator.py`**: Pure function `aggregate` / `aggregate_all` — no caching, no qualitative labels
- **`tests/test_metric_foundation.py`**: 42 tests (determinism, immutability, literalism, purity)

#### Phase 3.2: Health Exposure API
- **`phylax/_internal/metrics/health.py`**: `HealthReport` (pure data), `CoverageReport` (arithmetic only), windowed health queries
- **`phylax/server/routes/health.py`**: API endpoints for expectation health and coverage
- **`tests/test_health_api.py`**: 14 tests (no qualitative labels, arithmetic coverage, explicit windowing)

#### Phase 3.3: Enforcement Modes
- **`phylax/_internal/modes/handler.py`**: `ModeHandler` with `enforce` / `quarantine` / `observe` modes
- **`phylax/_internal/modes/definitions.py`**: `EnforcementMode`, `VALID_MODES`
- Modes affect CI exit code only — verdict is **never** modified
- **`tests/test_enforcement_modes.py`**: 20 tests (verdict invariance, no auto-escalation)

#### Phase 3.4: Meta-Enforcement Rules
- **`phylax/_internal/meta/rules.py`**: 4 dilution guards
  - `MinExpectationCountRule` — minimum declared count
  - `ZeroSignalRule` — fail if never failed (user opt-in)
  - `DefinitionChangeGuard` — hash-based definition change detection
  - `ExpectationRemovalGuard` — track IDs across versions
- **`tests/test_meta_enforcement.py`**: 21 tests (no scoring, no advisory language)

#### Phase 3.5: Scale Validation
- **`tests/test_scale_validation.py`**: 11 stress tests
  - 10k+ entry parity tests
  - Concurrent write safety
  - Massive JSONL replay
  - Definition churn determinism
  - 1000-run nondeterminism sweep

### Added — Public API Surface
- **`phylax/__init__.py`**: 60+ exports — all features accessible via `from phylax import ...`
- No `_internal` imports needed for any user-facing functionality
- **`tests/test_public_api_surface.py`**: 37 tests validating every exported symbol

### Added — Quickstart Demos
- **`demos/14_metrics_health.py`**: Metrics, ledger, aggregation, health reports
- **`demos/15_enforcement_modes.py`**: Mode behavior comparison
- **`demos/16_meta_enforcement.py`**: 4 dilution guards

### Stats
- **622 tests passing** (108 Axis 3 + 37 public API surface)
- **12 production branches** merged
- Engine core unchanged — zero contamination
- No scoring, no ranking, no advisory language

## [1.3.0a0] - 2026-02-22

### Added — Axis 2 Phase 2.0: Surface Abstraction Layer
- **`phylax/_internal/surfaces/surface.py`**: Generic `Surface` model (id, type, raw_payload, metadata), `SurfaceRule` ABC, `SurfaceAdapter` ABC, `SurfaceEvaluator`, `SurfaceRegistry`
- **`phylax/_internal/surfaces/text.py`**: `TextSurfaceAdapter` — bridges text responses into Surface abstraction
- **`tests/test_surface_abstraction.py`**: 35 tests covering Surface model, registry, adapter, evaluator, and engine integrity
- **Surface Registry**: Pre-registers 5 built-in types: `text_output`, `structured_output`, `tool_calls`, `execution_trace`, `cross_run_snapshot`
- **Engine Integrity**: Core engine code (`rules.py`, `evaluator.py`, `schema.py`) remains completely unchanged

## [1.3.0] - 2026-02-22

### Added — Axis 2 Phase 2.1: Structured Output Enforcement
- **`phylax/_internal/surfaces/structured.py`**: 6 deterministic structural validation rules
  - `FieldExistsRule` / `FieldNotExistsRule` — dot-notation path existence
  - `TypeEnforcementRule` — strict type check (no coercion: `"1"` ≠ `1`)
  - `ExactValueRule` — strict equality (no case folding, no trimming)
  - `EnumEnforcementRule` — set membership
  - `ArrayBoundsRule` — length constraints (`==`, `<=`, `>=`)
- **`StructuredSurfaceAdapter`** — JSON/dict → Surface conversion
- **`tests/test_structured_enforcement.py`**: 50 tests including determinism and forbidden behavior checks

## [1.3.1] - 2026-02-22

### Added — Axis 2 Phase 2.2: Tool & Function Call Invariants
- **`phylax/_internal/surfaces/tools.py`**: 4 tool enforcement rules
  - `ToolPresenceRule` — tool must/must-not appear
  - `ToolCountRule` — exact/min/max occurrence count
  - `ToolArgumentRule` — path-based strict argument comparison
  - `ToolOrderingRule` — index-based ordering (before / not_after)
- **`ToolSurfaceAdapter`** — event list → Surface conversion (no dedup, no retry collapsing)
- **`tests/test_tool_enforcement.py`**: 35+ tests

## [1.3.2] - 2026-02-22

### Added — Axis 2 Phase 2.3: Multi-Step Execution Trace Enforcement
- **`phylax/_internal/surfaces/execution_trace.py`**: 3 structural trace rules
  - `StepCountRule` — min/max/exact step count
  - `ForbiddenTransitionRule` — explicit consecutive transition prohibition
  - `RequiredStageRule` — stage must appear
- **`ExecutionTraceSurfaceAdapter`** — step list → Surface conversion
- **`tests/test_execution_trace_enforcement.py`**: 30+ tests

## [1.3.3] - 2026-02-22

### Added — Axis 2 Phase 2.4: Cross-Run Stability Enforcement
- **`phylax/_internal/surfaces/stability.py`**: Deterministic cross-run comparison
  - `ExactStabilityRule` — field/hash must not change between runs
  - `AllowedDriftRule` — only whitelisted fields may change
  - `StabilitySurfaceAdapter` — baseline+current snapshot → Surface
- **`tests/test_stability_enforcement.py`**: 28+ tests including forbidden behavior checks
- **Axis 2 Complete**: All 5 phases shipped (v1.3.0a0 → v1.3.3)

## [1.2.6] - 2026-02-14

### Fixed
- **Context Manager**: `execution()` no longer raises `EmptyExecutionGraphError` when an exception is already propagating

## [1.2.5] - 2026-02-12

### Changed
- **Evidence Purity**: Renamed `root_cause_node` to `first_failing_node` in `GraphVerdict`
- **Dependencies**: Updated to `google-genai>=0.5.0`
- **Configuration**: Added missing adapters to `config.yaml`

## [1.2.4] - 2026-02-10

### Added
- **Axis 2 Readiness Audit**: Full pass across all 6 audit phases
- **`docs/non-goals.md`**: Formal non-goals document listing 5 permanent constraints
- **`tests/test_axis2_invariants.py`**: 15 invariant guard tests that fail the build if:
  - Verdict space expands beyond PASS/FAIL
  - Expectations become adaptive or inferred
  - Evidence introduces interpretive language
  - Non-goals documentation is missing
  - Error messages contain advice instead of codes

### Changed
- **Doctrine Freeze**: All descriptions now say "CI-native regression enforcement for LLM outputs"
  - Fixed `phylax/__init__.py`, `phylax/cli/main.py`, `phylax/server/main.py`
  - Fixed legacy `cli/main.py`, `server/main.py`
- **Evidence Purity**: Removed all causal language from codebase
  - `"root cause"` → `"first failing node"` in all user-facing strings
  - `"reasoning"` → `"observation"` in investigation steps
  - `"debugging"` → `"failure localization"` in all docs and descriptions
  - Fixed `phylax/_internal/graph.py`, `phylax/server/routes/traces.py`
  - Fixed `docs/graph-model.md`, `docs/failure-playbook.md`, `docs/mental-model.md`,
    `docs/quickstart.md`, `docs/invariants.md`, `DOCUMENTATION.md`
- **Verdict Cleanup**: Removed residual `TAINTED` from `__init__.py` docstring

### Audit Results
| Phase | Status |
|-------|--------|
| 0 — Doctrine Freeze | ✅ PASS |
| 1 — Verdict Integrity | ✅ PASS |
| 2 — Expectation Model | ✅ PASS |
| 3 — Evidence Purity | ✅ PASS |
| 4 — UI & API Subordination | ✅ PASS |
| 5 — Test & Failure Signal | ✅ PASS |

---

## [1.1.6] - 2026-02-07

### Added
- **CLI Version Flag**: `phylax --version` or `phylax -v` shows current version

---

## [1.1.5] - 2026-02-07

### Added
- **Trace ID Search**: Search box in sidebar to find traces by ID
  - Type partial or full trace ID to filter
  - Auto-selects on exact match

---

## [1.1.4] - 2026-02-07

### Added
- **Golden Reference UI**: Bless/unbless traces directly from the UI
  - ⭐ "Bless as Golden" button next to Replay
  - Golden badge on blessed traces in sidebar
  - Gold border styling for blessed traces
  
- **Bless API Endpoints**:
  - `POST /v1/traces/{id}/bless` - Mark trace as golden
  - `DELETE /v1/traces/{id}/bless` - Remove golden status
  - `GET /v1/goldens` - List all golden traces

---

## [1.1.3] - 2026-02-07

### Fixed
- **Critical**: Fixed `expectations/__init__.py` to export `evaluate` function
- `@trace` + `@expect` decorators now work correctly together

---

## [1.1.2] - 2026-02-07

### Added
- **Adapters exported from main package**: Now `from phylax import GeminiAdapter` works
- All 7 demos updated to use clean imports

---

## [1.1.1] - 2026-02-07

### Changed
- **GeminiAdapter**: Migrated from deprecated `google-generativeai` to new `google-genai` SDK
  - Uses centralized `Client` architecture
  - Supports gemini-2.5-flash, gemini-2.5-pro models

### Fixed
- Updated google dependency: `google-genai>=0.5.0`

---

## [1.1.0] - 2026-02-07

### Added
- **Multi-Provider Support**:
  - `GroqAdapter` - Groq LPU inference (llama3-70b, mixtral-8x7b)
  - `MistralAdapter` - Mistral AI (mistral-large, codestral)
  - `HuggingFaceAdapter` - HuggingFace Inference API
  - `OllamaAdapter` - Local models via Ollama

- **Error Contracts Demo**: `demos/07_error_contracts.py`

- **Optional Dependencies**:
  - `pip install phylax[groq]`
  - `pip install phylax[mistral]`
  - `pip install phylax[huggingface]`
  - `pip install phylax[ollama]`

---

## [1.0.5] - 2026-02-07

### Added
- **Phase 1: Misuse Elimination**
  - PHYLAX_E101: `@trace` without `@expect` → hard fail
  - PHYLAX_E102: Empty `execution()` → hard fail
  - PHYLAX_E201: Bless trace without verdict → hard fail
  - PHYLAX_E202: `phylax check` without goldens → hard fail

- **Phase 2: Error Contracts**
  - `docs/errors.md` - Error taxonomy table

- **Phase 3: Raw Evidence**
  - `phylax/_internal/evidence.py` - HashEvidence, LatencyEvidence, PathEvidence

- **Phase 4: Opinionated Docs**
  - `docs/correct-usage.md`
  - `docs/when-not-to-use.md`

- **Demos Directory**: 6 comprehensive examples

---

## [1.0.4] - 2026-01-29

### Fixed
- Fixed `ModuleNotFoundError: No module named 'server'` in capture.py
- Corrected import to `phylax.server.storage.files`

---

## [1.0.3] - 2026-01-29

### Fixed
- Fixed `phylax server` command module path

---

## [1.0.2] - 2026-01-28

### Changed
- Updated PyPI description with latest README

---

## [1.0.1] - 2026-01-28

### Fixed
- Included UI and assets in PyPI package
- Added `[tool.setuptools.package-data]` to pyproject.toml

---

## [1.0.0] - 2026-01-20

### Added
- Initial stable release
- Core decorators: `@trace`, `@expect`
- Execution context: `execution()`
- CLI commands: `init`, `server`, `list`, `show`, `bless`, `check`
- Web UI for trace visualization
- Adapters: OpenAIAdapter, GeminiAdapter
