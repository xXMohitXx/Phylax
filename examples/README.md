# Phylax Examples

Ready-to-run examples showing how to use Phylax for AI behavior enforcement.

## 🚀 Start Here

| Example | What You'll Learn |
|---------|-------------------|
| [**quickstart/**](quickstart/) | Basic tracing + expectations in 10 lines |
| [**support_bot/**](support_bot/) | Content enforcement (`must_include` / `must_not_include`) |
| [**summarization/**](summarization/) | Latency + quality enforcement (`max_latency_ms`, `min_tokens`) |
| [**agent_workflow/**](agent_workflow/) | Multi-step agents with execution graphs |

## Setup

```bash
pip install phylax[openai]    # or phylax[google] for Gemini
export OPENAI_API_KEY="your-key"
```

## Run Any Example

```bash
cd examples/quickstart
python app.py
```

## CI Enforcement

After running examples, enforce contracts in CI:

```bash
phylax check   # exits 1 if any contract is violated
```

---

## Integration Tests

The `integration_tests/` directory contains internal test scripts.
These are not developer-facing examples.
