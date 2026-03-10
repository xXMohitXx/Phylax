# AI RAG Pipeline Template

A ready-to-use Phylax starter template for RAG (Retrieval-Augmented Generation) pipelines.

## What's Included

| File | Purpose |
|------|---------|
| `app.py` | RAG pipeline with retrieval + generation |
| `contracts.yaml` | Grounding enforcement contracts |

## Features

- **Grounding enforcement** — response must reference retrieved context
- **Anti-hallucination** — blocks "I don't know" hedging
- **Latency + quality** — minimum token count, max latency

## Quick Start

```bash
cp -r templates/ai-rag my-rag
cd my-rag
pip install phylax[openai]
export OPENAI_API_KEY="your-key"
python app.py
```
