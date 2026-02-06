# Phylax Demos

Replicable examples demonstrating all Phylax features.

## Setup

```bash
# Install Phylax
pip install phylax[all]

# Set API key
# Windows PowerShell:
$env:GOOGLE_API_KEY = "your-key"

# Linux/Mac:
export GOOGLE_API_KEY="your-key"
```

## Run Demos

```bash
# Run any demo
python demos/01_basic_trace.py
python demos/02_expectations.py
python demos/03_execution_context.py
python demos/04_graph_nodes.py
python demos/05_golden_workflow.py
```

## Demo Index

| File | Feature | Description |
|------|---------|-------------|
| 01_basic_trace.py | `@trace`, `@expect` | Basic tracing with expectations |
| 02_expectations.py | `@expect` rules | All 4 expectation rules |
| 03_execution_context.py | `execution()` | Grouping traces together |
| 04_graph_nodes.py | Graph API | Building and traversing graphs |
| 05_golden_workflow.py | `bless`, `check` | CI workflow demo |
| 06_raw_evidence.py | Evidence API | Raw evidence comparison |

## Requirements

- Python 3.10+
- `GOOGLE_API_KEY` environment variable
- `pip install phylax[all]`

## Expected Behavior

All demos enforce expectations. If a demo doesn't have `@expect`, it will fail with:
```
[PHYLAX_E101] Function 'X' has no expectations.
```

This is by design. Phylax requires expectations.
