# Contributing to Phylax

Thanks for your interest in contributing to Phylax! We welcome contributions from everyone — whether it's bug fixes, new features, documentation improvements, or community guardrail packs.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/xXMohitXx/Phylax.git
cd Phylax

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[all]"

# Run the test suite
python -m pytest tests/ -v
```

## What to Contribute

### Good First Issues 🟢

Look for issues tagged with `good first issue`. These are self-contained tasks that don't require deep knowledge of the codebase.

### Community Guardrail Packs 🛡️

Create reusable guardrail packs for specific industries or use cases:

- PII detection rules
- Healthcare compliance rules
- Financial services rules
- Content moderation rules

See `phylax/_internal/guardrails/packs.py` for the existing pack structure.

### Example Datasets 📊

Add realistic dataset contracts that other developers can learn from:

- Customer support bots
- Code generation assistants
- Content summarization
- RAG pipelines

Add your datasets to `examples/` with a README explaining the use case.

### Documentation 📖

- Fix typos or unclear explanations
- Add code examples to existing docs
- Translate documentation

## Code Style

- **Python 3.10+** — use type hints everywhere
- **Pydantic** — use frozen models for immutable data
- **Deterministic** — all rules must produce binary PASS/FAIL. No scores, no probabilities
- **No AI-based evaluation** — rules must be deterministic. Never use LLM-as-a-judge
- **Tests required** — every new feature must include tests

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Write** your code and tests
4. **Run** the full test suite: `python -m pytest tests/ -v`
5. **Commit** with a clear message: `feat: add PII guardrail pack`
6. **Push** and open a Pull Request

### Commit Message Format

```
type: short description

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation only
  test:     Adding/updating tests
  refactor: Code restructuring
```

## Architecture Principles

Before contributing, understand these non-negotiable design principles:

1. **Verdicts are PASS/FAIL only** — no partial passes, no scores, no weighting
2. **Rules are deterministic** — same input always produces same verdict
3. **Traces are immutable** — once written, never recalculated
4. **Evidence, not analysis** — Phylax reports facts, interpretation is external
5. **CI is the primary interface** — `phylax check` exit code 0/1 is the main output

See [CODEBASE_ARCHITECTURE.md](CODEBASE_ARCHITECTURE.md) for detailed architecture documentation.

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_dataset_contracts.py -v

# Run with coverage
python -m pytest tests/ --cov=phylax --cov-report=term-missing
```

All PRs must pass the full test suite. PRs that break existing tests will not be merged.

## Community

- [GitHub Issues](https://github.com/xXMohitXx/Phylax/issues) — Bug reports and feature requests
- [GitHub Discussions](https://github.com/xXMohitXx/Phylax/discussions) — Questions and ideas

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
