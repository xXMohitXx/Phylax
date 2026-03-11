# Phylax Demos

Replicable examples demonstrating all Phylax features (v1.6.3).

## Setup

```bash
pip install phylax[all]

# Set API key (choose your provider)
# Windows PowerShell:
$env:GOOGLE_API_KEY = "your-key"

# Linux/Mac:
export GOOGLE_API_KEY="your-key"
```

## Run Demos

```bash
python demos/01_basic_trace.py
python demos/21_dataset_contracts.py
python demos/22_behavioral_diff.py
```

## Demo Index

### Core Features (01–12)

| # | File | Feature | Description |
|---|------|---------|-------------|
| 01 | `01_basic_trace.py` | `@trace`, `@expect` | Basic tracing with expectations |
| 02 | `02_expectations.py` | `@expect` rules | All 4 expectation rules |
| 03 | `03_execution_context.py` | `execution()` | Grouping traces together |
| 04 | `04_graph_nodes.py` | Graph API | Building and traversing graphs |
| 05 | `05_golden_workflow.py` | `bless`, `check` | CI workflow demo |
| 06 | `06_raw_evidence.py` | Evidence API | Raw evidence comparison |
| 07 | `07_error_contracts.py` | Error codes | PHYLAX_E1xx/E2xx errors |
| 08 | `08_composition.py` | Composition | Nested traces and composition |
| 09 | `09_conditionals.py` | Conditionals | Conditional enforcement |
| 10 | `10_scoping.py` | Scoping | Scoped trace contexts |
| 11 | `11_templates.py` | Templates | Template-based expectations |
| 12 | `12_documentation.py` | Documentation | Self-documenting traces |

### Provider & Infrastructure (13–16)

| # | File | Feature | Description |
|---|------|---------|-------------|
| 13 | `13_gemini_live.py` | Gemini | Live Gemini API integration |
| 14 | `14_metrics_health.py` | Metrics | Health reports and coverage |
| 15 | `15_enforcement_modes.py` | Modes | enforce/quarantine/observe |
| 16 | `16_meta_enforcement.py` | Meta-rules | Meta-level enforcement |

### Artifacts & Exit Codes (17–20)

| # | File | Feature | Description |
|---|------|---------|-------------|
| 17 | `17_verdict_artifacts.py` | Verdicts | Machine-readable verdict artifacts |
| 18 | `18_failure_tracking.py` | Failures | Failure tracking artifacts |
| 19 | `19_trace_diffs.py` | Trace Diffs | Trace diff artifacts |
| 20 | `20_exit_codes.py` | Exit Codes | CI exit codes (0/1/2) |

### v1.6.0 Features (21–24)

| # | File | Feature | Description |
|---|------|---------|-------------|
| 21 | `21_dataset_contracts.py` | Dataset Contracts | Batch-test LLM behavior with YAML contracts |
| 22 | `22_behavioral_diff.py` | Behavioral Diff | Compare runs, detect regressions |
| 23 | `23_model_simulator.py` | Model Simulator | Safe model upgrade testing |
| 24 | `24_guardrail_packs.py` | Guardrail Packs | Pre-built safety/quality/compliance rules |

## Requirements

- Python 3.10+
- `pip install phylax[all]`
- API key for your provider

## Expected Behavior

All demos enforce expectations. If a function doesn't have `@expect`, it will fail with:
```
[PHYLAX_E101] Function 'X' has no expectations.
```

This is by design — Phylax requires expectations.
