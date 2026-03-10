# Phylax Quickstart

The fastest way to see Phylax in action.

## Setup

```bash
pip install phylax[openai]   # or phylax[google] for Gemini
export OPENAI_API_KEY="your-key"
```

## Run

```bash
python app.py
```

## What Happens

1. Phylax traces the LLM call automatically via `@trace`
2. `@expect` enforces that the response must include "hello" and complete within 5 seconds
3. If either rule fails → the trace is marked FAIL
4. Run `phylax check` in CI to block regressions

## CI Integration

```yaml
# .github/workflows/phylax.yml
- run: pip install phylax[openai]
- run: phylax check
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```
