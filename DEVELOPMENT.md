# Development Guide

Complete guide for local development, testing, and contributing to Phylax.

---

## Quick Setup (For Contributors)

```bash
# Clone
git clone https://github.com/xXMohitXx/Phylax.git
cd Phylax

# Virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install in dev mode
pip install -e ".[all,dev]"
```

## For Users

```bash
pip install phylax[all]
```

## Environment Variables

```powershell
$env:GOOGLE_API_KEY = "your-gemini-key"
$env:OPENAI_API_KEY = "your-openai-key"    # optional
$env:GROQ_API_KEY = "your-groq-key"        # optional
$env:MISTRAL_API_KEY = "your-mistral-key"  # optional
$env:HF_TOKEN = "your-hf-token"            # optional
$env:OLLAMA_HOST = "http://localhost:11434" # optional
```

---

## Running

### Start Server

```bash
phylax server
# UI: http://127.0.0.1:8000/ui
# API: http://127.0.0.1:8000/docs
```

### CLI Commands

```bash
phylax init           # Initialize
phylax list           # List traces
phylax list --failed  # Failed only
phylax show <id>      # Show trace
phylax replay <id>    # Replay
phylax bless <id>     # Mark golden
phylax check          # CI check
phylax dataset run    # Run dataset contract
phylax dataset diff   # Compare two runs
phylax --version      # Show version
```

---

## Testing

```bash
# Run all tests (1146 tests)
pytest tests/

# Run Axis 3 tests
pytest tests/test_metric_foundation.py tests/test_health_api.py tests/test_enforcement_modes.py tests/test_meta_enforcement.py tests/test_scale_validation.py -v

# Run public API surface test
pytest tests/test_public_api_surface.py -v

# Run Axis 2 invariant tests
pytest tests/test_axis2_invariants.py -v

# Run context tests
pytest tests/test_context.py -v
```

---

## Project Structure

```
Phylax/
├── phylax/                    # Main package (PyPI)
│   ├── __init__.py            # Public API exports
│   ├── agents.py              # Agent API
│   ├── rag.py                 # RAG API
│   ├── guardrails.py          # Domain packs API
│   ├── evidence.py            # Evidence API
│   ├── expectations.py        # Expectations API
│   ├── graph.py               # Graph API
│   ├── errors.py              # Error API
│   ├── _internal/             # Internal modules
│   │   ├── schema.py          # Trace schema
│   │   ├── decorator.py       # @trace, @expect
│   │   ├── capture.py         # Core capture
│   │   ├── context.py         # Execution context
│   │   ├── graph.py           # Graph models
│   │   ├── errors.py          # Error codes (PHYLAX_Exxx)
│   │   ├── evidence.py        # Evidence logic
│   │   ├── artifacts/         # Artifact contracts
│   │   ├── datasets/          # Dataset contracts
│   │   ├── expectations/      # 4 rules + evaluator + composition
│   │   ├── guardrails/        # Domain guardrail packs
│   │   ├── surfaces/          # Surface enforcement (Axis 2)
│   │   │   ├── agents.py
│   │   │   └── rag.py
│   │   ├── metrics/           # Metrics, ledger, health (Axis 3)
│   │   ├── modes/             # Enforcement modes (Axis 3)
│   │   ├── meta/              # Meta-enforcement rules (Axis 3)
│   │   └── adapters/          # All LLM provider adapters
│   ├── cli/                   # CLI commands
│   ├── server/                # FastAPI backend + health routes
│   ├── ui/                    # Web UI (HTML/JS)
│   └── assets/                # Logo, favicon
├── tests/                     # Unit tests (1146 tests)
│   └── phase_tests/
├── demos/                     # Usage demonstrations (24 demos)
├── examples/                  # Integration scripts (4 examples)
├── templates/                 # Scaffolding templates (5 templates)
│   └── support-bot/
├── ci-kits/                   # CI/CD platform templates
├── phylax_guardrails/         # Standalone guardrail package
├── marketing_agent/           # Groq-powered prompt generator
├── docs/                      # Documentation
├── config.yaml                # Default configuration
└── pyproject.toml             # Package config
```

---

## Creating a Demo Script

```python
from phylax import trace, expect, execution, GeminiAdapter


@trace(provider="gemini")
@expect(must_include=["hello"], max_latency_ms=5000)
def ask_gemini(prompt: str):
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=prompt,
        model="gemini-2.5-flash",
    )
    return response


# Single call
result = ask_gemini("Hello!")
print(result.text)

# Grouped calls
with execution() as exec_id:
    step1 = ask_gemini("Step 1")
    step2 = ask_gemini("Step 2")
```

---

## Building for PyPI

```bash
pip install build twine
python -m build
twine upload dist/* -u __token__ -p <PYPI_TOKEN>
```

---

## Version Checking

```python
import phylax
print(phylax.__version__)  # "1.6.3"
```

```bash
phylax --version
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Ensure all 1146 tests pass
6. Submit a pull request

---

## License

MIT License
