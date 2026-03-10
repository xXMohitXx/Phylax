# AI Agent Workflow — Phylax Example

A multi-step AI agent with execution graph tracking.

## What This Shows

- **Execution contexts** — group multiple LLM calls into one traced flow
- **Execution graphs** — visualize agent decision paths as DAGs
- **Per-step enforcement** — each step has its own contracts

## Steps

```
[classify] → [research] → [respond]
```

1. **Classify** the user intent
2. **Research** relevant information
3. **Respond** with a grounded answer

## Run

```bash
pip install phylax[openai]
export OPENAI_API_KEY="your-key"
python app.py
```

## What This Demonstrates

- `execution()` context manager for grouping traces
- Multi-step agent flow with per-step expectations
- How to debug agent failures using execution graphs
