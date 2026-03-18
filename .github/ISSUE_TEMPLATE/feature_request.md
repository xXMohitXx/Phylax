---
name: Feature Request
about: Suggest a feature for Phylax
title: "[FEATURE] "
labels: enhancement
assignees: ''
---

## Problem Statement

Describe the problem you're trying to solve. What limitation or gap does this address?

## Proposed Solution

Describe the solution you'd like. How should it work?

### API Design (if applicable)

```python
# How would a developer use this feature?
from phylax import new_feature

@trace(provider="openai")
@expect(new_rule=...)
def my_function():
    ...
```

### CLI Design (if applicable)

```bash
phylax new-command --flag value
```

### YAML Design (if applicable)

```yaml
dataset: example
cases:
  - input: "..."
    expectations:
      new_rule: ...
```

## Alternatives Considered

What other approaches did you consider? Why is this approach better?

## Is This a Good First Issue?

- [ ] Yes — this is self-contained and doesn't require deep knowledge of the codebase
- [ ] No — this requires understanding of Phylax internals

## Additional Context

Any other context, mockups, or examples.

## Checklist (for contributors)

Before submitting a PR for this feature:

- [ ] Added tests
- [ ] Updated documentation
- [ ] Rules are deterministic (PASS/FAIL only)
- [ ] No AI-based evaluation (no LLM-as-a-judge)
- [ ] All existing tests still pass
