# Phylax Examples

Developer-first examples demonstrating real-world Phylax usage patterns.

## Quick Start

| Example | Use Case | Key Features |
|---------|----------|--------------|
| [`quickstart/`](quickstart/) | First 5 minutes | `@trace`, `@expect`, basic enforcement |
| [`support_bot/`](support_bot/) | Customer support | Safety guardrails, content policies |
| [`summarization/`](summarization/) | Text summarization | Quality + latency enforcement |
| [`agent_workflow/`](agent_workflow/) | Multi-step agents | Dataset contracts, model comparison |

## Running

```bash
pip install phylax
cd examples/quickstart
python app.py
```

Each example is self-contained with its own `app.py` and optional `contracts.yaml`.
