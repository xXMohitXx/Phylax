# When NOT to Use Phylax

Phylax is a verdict engine. It is NOT for:

---

## Excluded Use Cases

### ❌ Exploratory Prompting
Phylax requires expectations. If you don't know what output to expect, Phylax cannot help.

### ❌ Subjective Evaluation
"Is this response good?" is not a Phylax question.
"Does this response contain X?" is.

### ❌ Live Monitoring
Phylax runs in CI. It is not a monitoring system. It has no dashboards. It does not alert.

### ❌ Adaptive Systems
If your acceptable outputs change over time, Phylax cannot track a moving target.

### ❌ Debugging Aid
Phylax says PASS or FAIL. It does not explain why. It does not suggest fixes.

---

## If You Need These

| Need | Tool |
|------|------|
| Monitoring | Langfuse, Helicone |
| Evaluation | RAGAS, DeepEval |
| Debugging | LangSmith |
| Adaptive testing | Human judgment |

---

Phylax's strength is knowing what it refuses to be.
