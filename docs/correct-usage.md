# Correct Usage

Phylax is a verdict engine. It answers one question:
**"Did a declared contract regress?"**

---

## Valid Setup

```python
from phylax._internal.decorator import trace, expect
from phylax._internal.context import execution

@trace(provider="gemini")
@expect(must_include=["hello"], max_latency_ms=2000)
def greet():
    # LLM call
    ...

with execution() as exec_id:
    greet()  # Creates trace with verdict
```

**Requirements:**
- Every `@trace` must have `@expect`
- Every `execution()` must contain traced calls
- Golden traces must have passing verdicts

---

## Invalid Setups

| Setup | Error |
|-------|-------|
| `@trace` without `@expect` | PHYLAX_E101 |
| Empty `execution()` | PHYLAX_E102 |
| Bless trace without verdict | PHYLAX_E201 |
| `phylax check` without goldens | PHYLAX_E202 |

---

## Why Phylax Refuses

Phylax refuses meaningless configurations because:
- A trace without expectations cannot produce a verdict
- An empty execution cannot be evaluated
- A failing trace cannot be a golden reference
- A check without goldens cannot detect regressions

These are not warnings. They are hard failures.
