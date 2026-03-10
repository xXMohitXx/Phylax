# Surface Enforcement — Axis 2

Phylax v1.3.x introduces the **Surface Abstraction Layer** — a generic enforcement framework for validating LLM outputs beyond plain text.

## What is a Surface?

A Surface is a typed, immutable wrapper around a raw LLM output payload. Surfaces enable enforcement rules to operate on structured data, tool calls, execution traces, and cross-run snapshots without modifying the core engine.

```python
from phylax import Surface

s = Surface(type="structured_output", raw_payload={"status": "ok", "count": 42})
```

**Properties:**
- `type` — one of 5 built-in types (see below)
- `raw_payload` — preserved exactly as provided, never normalized
- `metadata` — optional, never influences enforcement
- `id` — auto-generated UUID, immutable

## Surface Types

| Type | Payload Shape | Purpose |
|------|---------------|---------|
| `text_output` | `str` | Plain text responses |
| `structured_output` | `dict` | JSON / structured data |
| `tool_calls` | `list[dict]` | Function/tool call sequences |
| `execution_trace` | `list[dict]` | Multi-step workflow traces |
| `cross_run_snapshot` | `dict` with `baseline` + `current` | Cross-run stability comparisons |

## Rules by Surface Type

### Structured Output (6 rules)

| Rule | What it checks |
|------|----------------|
| `FieldExistsRule(path)` | Field exists at dot-notation path |
| `FieldNotExistsRule(path)` | Field must NOT exist |
| `TypeEnforcementRule(path, type)` | Strict type check (`string`, `number`, `boolean`, `array`, `object`, `null`) |
| `ExactValueRule(path, expected)` | Exact value match (no coercion) |
| `EnumEnforcementRule(path, values)` | Value must be in explicit set |
| `ArrayBoundsRule(path, op, n)` | Array length constraint (`==`, `<=`, `>=`) |

```python
from phylax import FieldExistsRule, ExactValueRule, Surface, SurfaceEvaluator

ev = SurfaceEvaluator()
ev.add_rule(FieldExistsRule("response.status"))
ev.add_rule(ExactValueRule("response.status", "approved"))

s = Surface(type="structured_output", raw_payload={"response": {"status": "approved"}})
verdict = ev.evaluate(s)
# verdict.status == "pass"
```

### Tool Calls (4 rules)

| Rule | What it checks |
|------|----------------|
| `ToolPresenceRule(name, must_exist)` | Tool must/must-not appear |
| `ToolCountRule(name, op, n)` | Exact/min/max call count |
| `ToolArgumentRule(name, arg, value)` | Argument strict equality |
| `ToolOrderingRule(a, b, mode)` | Tool A must appear before/not-after B |

### Execution Trace (3 rules)

| Rule | What it checks |
|------|----------------|
| `StepCountRule(op, n)` | Total step count constraint |
| `ForbiddenTransitionRule(from, to)` | Adjacent transition must not occur |
| `RequiredStageRule(stage)` | Stage must appear at least once |

### Cross-Run Stability (2 rules)

| Rule | What it checks |
|------|----------------|
| `ExactStabilityRule(path?)` | Hash or field comparison between baseline and current |
| `AllowedDriftRule(allowed_fields)` | Only whitelisted fields may change |

## Core Invariants

1. **Binary verdicts** — `SurfaceVerdict.status` is always `"pass"` or `"fail"`, never anything else
2. **No coercion** — `"1"` ≠ `1`, `"true"` ≠ `True`, `"Approved"` ≠ `"approved"`
3. **No normalization** — raw payloads are never trimmed, reordered, or canonicalized
4. **No inference** — rules must be explicitly declared; no auto-detection of schema, type, or intent
5. **No engine modification** — the core engine (`rules.py`, `evaluator.py`, `schema.py`) is untouched
6. **Metadata blindness** — surface metadata never influences rule outcomes

## Architecture

```
SurfaceAdapter.adapt(raw_data)  →  Surface (immutable)
                                      ↓
                               SurfaceEvaluator
                                 .add_rule(SurfaceRule)
                                 .evaluate(surface)
                                      ↓
                               SurfaceVerdict: pass | fail
```

The Surface layer operates **in parallel** to the existing expectation engine. They share no logic paths.
