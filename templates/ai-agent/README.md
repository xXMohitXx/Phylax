# AI Agent Template

A ready-to-use Phylax starter template for multi-step AI agents.

## What's Included

| File | Purpose |
|------|---------|
| `app.py` | Multi-step agent with execution graph tracking |
| `contracts.yaml` | Dataset contract for batch testing |

## Features

- **Execution graphs** — tracks multi-step agent flows as DAGs
- **Per-step contracts** — each agent step has its own expectations
- **CI enforcement** — `phylax check` validates all steps

## Quick Start

```bash
cp -r templates/ai-agent my-agent
cd my-agent
pip install phylax[openai]
export OPENAI_API_KEY="your-key"
python app.py
```
