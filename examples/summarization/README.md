# Summarization Pipeline Example

This example showcases a standard RAG-like text summarization flow.

## Features Showcased

- **Latency Restrictions**: Enforcing strict maximum latency rules (`max_latency_ms`).
- **Quality Guardrails**: Applying standard quality checks from `phylax.guardrails`.
- **Format Requirements**: Ensuring the model outputs within token restrictions (`max_tokens`).

## Usage

Run the following from the root of this directory:

```bash
# Ensure phylax is installed
pip install phylax

# Run the summarizer
python app.py
```
