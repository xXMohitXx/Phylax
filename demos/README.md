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
| 07_error_contracts.py | Error codes | PHYLAX_E1xx/E2xx errors |

## Requirements

- Python 3.10+
- API key for your provider (see below)
- Install: `pip install phylax[all]`

## Provider Installation

```bash
# All providers
pip install phylax[all]

# Individual providers
pip install phylax[openai]     # OpenAI
pip install phylax[google]     # Gemini
pip install phylax[groq]       # Groq
pip install phylax[mistral]    # Mistral
pip install phylax[huggingface] # HuggingFace
pip install phylax[ollama]     # Ollama (local)
```

- Python 3.10+
- `GOOGLE_API_KEY` environment variable
- `pip install phylax[all]`

## Expected Behavior

All demos enforce expectations. If a demo doesn't have `@expect`, it will fail with:
```
[PHYLAX_E101] Function 'X' has no expectations.
```

This is by design. Phylax requires expectations.
