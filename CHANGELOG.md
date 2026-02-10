# Changelog

All notable changes to Phylax.

## [1.2.0] - 2026-02-10

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
