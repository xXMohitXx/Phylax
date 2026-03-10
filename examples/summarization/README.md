# AI Summarizer — Phylax Example

An AI summarizer with latency and quality enforcement.

## Rules

| Rule | Purpose |
|------|---------|
| `max_latency_ms=2000` | Summary must complete within 2 seconds |
| `min_tokens=50` | Summary must be at least 50 tokens |
| `must_not_include=["I think", "maybe"]` | No hedging language |

## Run

```bash
pip install phylax[openai]
export OPENAI_API_KEY="your-key"
python app.py
```

## What This Demonstrates

- Latency constraints (`max_latency_ms`)
- Minimum output quality (`min_tokens`)
- Forbidden content patterns
