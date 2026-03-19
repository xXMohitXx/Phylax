# Support Bot Example

This example demonstrates how to deploy robust support bots with content safety and guardrails.

## Features Showcased

- **Guardrail Packs**: Utilizing pre-built rule sets (`safety_pack()`) from `phylax.guardrails` to prevent hallucination, PII leakage, and hate speech.
- **Dataset Contracts**: Ensuring responses align with core business constraints using bulk `run_dataset` evaluations.
- **Trace Context**: Grouping sub-calls using `execution()`.

## Usage

Run the following from the root of this directory:

```bash
# Ensure phylax is installed
pip install phylax

# Run the support bot
python app.py
```
