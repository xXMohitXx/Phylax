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
$env:OPENAI_API_KEY = "your-openai-key"  # optional
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
```

---

## Testing

```bash
# Run all tests
pytest tests/

# Run Axis 2 invariant tests (must pass before Axis 2 work)
pytest tests/test_axis2_invariants.py -v

# Run specific tests
python examples/test_graph_unit.py
python examples/test_graph_features.py
python examples/test_phases_19_25.py
```

---

## Project Structure

```
Phylax/
├── phylax/                    # Main package (PyPI)
│   ├── __init__.py            # Public API
│   ├── _internal/             # Internal modules
│   │   ├── schema.py          # Trace schema
│   │   ├── decorator.py       # @trace, @expect
│   │   ├── capture.py         # Core capture
│   │   ├── context.py         # Execution context
│   │   ├── graph.py           # Graph models
│   │   ├── expectations/      # 4 rules + evaluator
│   │   └── adapters/          # OpenAI, Gemini
│   ├── cli/                   # CLI commands
│   ├── server/                # FastAPI backend
│   ├── ui/                    # Web UI (HTML/JS)
│   └── assets/                # Logo, favicon
├── tests/                     # Unit tests
├── examples/                  # Demo scripts
├── docs/                      # Documentation
└── pyproject.toml             # Package config
```

---

## Creating a Demo Script

```python
import phylax
from phylax._internal.decorator import trace
from phylax._internal.context import execution
from phylax._internal.adapters.gemini import GeminiAdapter


@trace(provider="gemini")
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
twine upload dist/*
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

---

## License

MIT License
