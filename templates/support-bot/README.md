# Support Bot Testing Template

A production-ready template demonstrating how to use Phylax to enforce behavioral contracts on a customer support bot. This includes a comprehensive dataset contract with 25+ realistic test cases, CI configuration, and failure scenarios.

## Quick Start

```bash
pip install phylax[openai]

# Run the support bot with Phylax tracing
python app.py

# Run the dataset contract
phylax dataset run dataset.yaml

# Simulate a model upgrade
phylax dataset diff baseline.json current.json
```

## Files

| File | Purpose |
|------|---------|
| `app.py` | Support bot handler with Phylax tracing and safety guardrails |
| `dataset.yaml` | 25 behavioral test cases covering refunds, password resets, billing, safety |
| `phylax.yaml` | Phylax configuration |
| `ci.yml` | GitHub Actions CI workflow template |
| `README.md` | This file |

## What This Template Demonstrates

1. **Safety Guardrails**: The bot applies the `safety_pack()` guardrail automatically — blocking PII leaks, hate speech, and jailbreak attempts
2. **Dataset Contracts**: 25 test cases covering every major user flow with explicit must_include/must_not_include expectations
3. **CI Enforcement**: A GitHub Actions workflow that runs the dataset contract on every push
4. **Failure Scenarios**: Intentionally broken test cases that demonstrate how Phylax catches regressions
