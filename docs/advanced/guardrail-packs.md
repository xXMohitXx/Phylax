# Guardrail Packs

Phylax provides out-of-the-box protection suites grouped into specific "Packs".

## 1. Safety Pack

`safety_pack()` blocks toxic language, prompt injection phrases, hate speech, and explicit material.

## 2. Quality Pack

`quality_pack()` mandates professional tone, readability metrics, and specific structural boundaries (like bullet-list formats where applicable).

## 3. Compliance Pack

`compliance_pack()` halts the LLM from acting as a certified professional, blocking medical, legal, or financial advice.

## Implementations

These rule bounds can be directly integrated into `DatasetCase` execution:

```python
from phylax.guardrails import safety_pack
from phylax import DatasetCase

_safety = safety_pack().to_expectations()

case = DatasetCase(
    input="Tell me a joke",
    name="joke_test",
    expectations=_safety
)
```
