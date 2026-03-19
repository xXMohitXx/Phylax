# Multi-Agent Enforcement

Phylax v1.6.3 introduces native support for enforcing constraints across complex Multi-Agent ecosystems.
Instead of evaluating single prompts, you can now validate entirely dynamic, non-deterministic agent trajectories.

## Overview

Using `phylax.agents`, you can protect agent workflows against prompt-injection and hallucinated tool calls.

### 1. Tool Sequence Rule

The `ToolSequenceRule` strictly enforces that an agent invokes sub-tools in a controlled, predefined order.
This prevents unauthorized loops or skipping critical security-check tools.

```python
from phylax.agents import ToolSequenceRule

# Must retrieve context before generating an answer
rule = ToolSequenceRule(required_sequence=["retriever", "generator"])

trace = [{"tool_name": "retriever"}, {"tool_name": "generator"}]
result = rule.evaluate(trace)
print(result.passed) # True
```

### 2. Agent Step Validator

Enforce the total number of steps an agent can take, protecting against infinite loops causing high LLM costs.

```python
from phylax.agents import AgentStepValidator

rule = AgentStepValidator(min_steps=1, max_steps=5, required_step_types=["planner"])
```

### Integration with Dataset Contracts

Agent rules can seamlessly be embedded inside `DatasetCase(expectations=...)` for offline bulk-testing agent traces during CI/CD.
