# AI Support Bot — Phylax Example

An AI customer support bot with enforced safety contracts.

## Rules

| Rule | Purpose |
|------|---------|
| `must_include=["refund"]` | Bot must mention refund policy |
| `must_not_include=["lawsuit"]` | Bot must never mention legal action |
| `max_latency_ms=3000` | Response must complete within 3 seconds |

## Run

```bash
pip install phylax[openai]
export OPENAI_API_KEY="your-key"
python app.py
```

## What This Demonstrates

- Content enforcement (`must_include` / `must_not_include`)
- Latency enforcement (`max_latency_ms`)
- How Phylax catches regressions when model behavior changes
