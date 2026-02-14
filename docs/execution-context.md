# Execution Context

> **How to group and track multi-step LLM workflows.**

---

## Overview

The `execution()` context manager groups related LLM traces into a single execution graph. All traces created inside the context share the same `execution_id` and are automatically linked by parent-child relationships.

---

## Basic Usage

```python
from phylax import trace, expect, execution, GeminiAdapter

@trace(provider="gemini")
@expect(must_include=["hello"], max_latency_ms=5000)
def greet(name: str):
    adapter = GeminiAdapter()
    response, _ = adapter.generate(
        prompt=f"Say hello to {name}",
        model="gemini-2.5-flash",
    )
    return response

# Group related calls
with execution() as exec_id:
    print(f"Execution ID: {exec_id}")
    step1 = greet("Alice")   # parent_node_id = None (root)
    step2 = greet("Bob")     # parent_node_id = step1.node_id
```

---

## What It Does

| Feature | Description |
|---------|-------------|
| **execution_id** | UUID assigned to all traces in the context |
| **parent tracking** | Automatic `parent_node_id` via node stack |
| **graph creation** | Traces form a DAG for visualization |
| **context isolation** | Nested contexts get independent IDs |

---

## Context Variables

The execution context uses Python's `contextvars` module — thread-safe and async-safe:

```python
from phylax._internal.context import (
    execution,           # Context manager
    get_execution_id,    # Get current execution ID
    get_parent_node_id,  # Get current parent node
    push_node,           # Push node to stack (internal)
    pop_node,            # Pop node from stack (internal)
    in_execution_context, # Check if inside context
)
```

---

## Nested Contexts

Nested `execution()` calls create independent contexts:

```python
with execution() as outer_id:
    greet("Alice")  # belongs to outer_id

    with execution() as inner_id:
        greet("Bob")  # belongs to inner_id

    greet("Charlie")  # back to outer_id
```

---

## Outside a Context

When no execution context exists:
- `get_execution_id()` generates a new UUID per call
- `get_parent_node_id()` returns `None`
- `push_node()` / `pop_node()` are no-ops

Traces are still created — they just aren't grouped.

---

## Behavior Notes

- **No validation on exit**: As of v1.2.6, `execution()` does **not** raise an error if no traced calls are made inside it. This allows unit tests to use the context for testing plumbing without requiring real LLM calls.

- **Graph evaluation**: Empty graph validation happens at graph evaluation time (`ExecutionGraph.compute_verdict()`), not at context exit.

- **Thread safety**: Uses `contextvars.ContextVar`, which is safe for both threaded and async code.

---

## Viewing Execution Graphs

After creating traces inside an execution, view the graph:

**Web UI:**
```
http://127.0.0.1:8000/ui
```

**API:**
```bash
curl http://127.0.0.1:8000/v1/executions/{exec_id}/graph
```

**CLI:**
```bash
phylax list      # Find execution IDs
phylax show <id> # Show trace details
```

---

## Related Docs

- [Graph Model](graph-model.md) — How to read execution graphs
- [Failure Playbook](failure-playbook.md) — Debugging graph failures
- [Contract](contract.md) — Execution context stability guarantees
- [Quickstart](quickstart.md) — Getting started with Phylax
