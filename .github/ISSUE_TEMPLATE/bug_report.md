---
name: Bug Report
about: Report a bug in Phylax
title: "[BUG] "
labels: bug
assignees: ''
---

## Describe the Bug

A clear description of what the bug is.

## To Reproduce

Steps to reproduce the behavior:

1. Install Phylax: `pip install phylax[openai]`
2. Create file with this code: `...`
3. Run: `phylax check`
4. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened. Include the full error output if applicable.

## Environment

- **OS**: [e.g., Ubuntu 22.04, Windows 11, macOS 14]
- **Python version**: [e.g., 3.10.12]
- **Phylax version**: [e.g., 1.6.3]
- **Provider**: [e.g., OpenAI, Gemini, Groq]

## Code Example

```python
# Minimal reproducible example
from phylax import trace, expect

@trace(provider="openai")
@expect(must_include=["hello"])
def my_function():
    ...
```

## Additional Context

Any other context about the problem (logs, screenshots, related issues).
