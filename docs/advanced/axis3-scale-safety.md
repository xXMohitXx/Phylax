# Axis 3: Scale Safety & Misuse Resistance

Axis 3 protects signal at scale. It prevents dilution, drift, and silent erosion of expectation coverage.

---

## Metrics Foundation (Phase 3.1)

### Expectation Identity

Every expectation gets a stable, content-based identity hash.

```python
from phylax import ExpectationIdentity, compute_definition_hash

# Compute a stable hash for any expectation definition
definition = {"rule": "must_include", "substrings": ["refund"]}
hash_val = compute_definition_hash(definition)
# Same input always produces the same hash
```

### Evaluation Ledger

Append-only record of every evaluation result. No update, no delete, no mutation.

```python
from phylax import LedgerEntry, EvaluationLedger

ledger = EvaluationLedger()
ledger.record(LedgerEntry(expectation_id="e1", verdict="pass"))
ledger.record(LedgerEntry(expectation_id="e1", verdict="fail"))
ledger.record(LedgerEntry(expectation_id="e1", verdict="pass"))

# Ledger is append-only
# No .update(), .delete(), .clear(), .pop() methods exist
```

### Aggregation

Deterministic metrics computed from ledger entries.

```python
from phylax import aggregate, aggregate_all

metrics = aggregate(ledger.entries, "e1")
# metrics.total_evaluations = 3
# metrics.failure_rate = 0.333...
# metrics.pass_count = 2
# metrics.fail_count = 1

# Aggregate all expectations at once
all_metrics = aggregate_all(ledger.entries)
```

### Health Reports

```python
from phylax import HealthReport, CoverageReport, get_windowed_health

report = HealthReport.from_aggregate(metrics, hash_val)
# Deterministic: same inputs always produce identical reports
```

---

## Enforcement Modes (Phase 3.3)

Three modes, explicitly set. No auto-switching.

| Mode | On FAIL | Exit Code | CI Behavior |
|------|---------|-----------|-------------|
| `enforce` | Block | 1 | Pipeline fails |
| `quarantine` | Log | 0 | Pipeline continues, failure logged |
| `observe` | Log | 0 | Pipeline continues, metrics only |

```python
from phylax import ModeHandler, VALID_MODES

# VALID_MODES = {"enforce", "quarantine", "observe"}
handler = ModeHandler("enforce")
result = handler.apply("fail")
# result.exit_code = 1

# Invalid modes are rejected
try:
    ModeHandler("auto")  # ValueError
except ValueError:
    pass
```

---

## Meta-Enforcement Rules (Phase 3.4)

Guards against silent erosion of expectation coverage.

### MinExpectationCountRule

Fail if too few expectations are defined.

```python
from phylax import MinExpectationCountRule

rule = MinExpectationCountRule(min_count=3)
result = rule.evaluate(current_count=2)
# result.passed = False
```

### ZeroSignalRule

Fail if no expectations produce signal (all pass trivially).

```python
from phylax import ZeroSignalRule

rule = ZeroSignalRule()
result = rule.evaluate(total_evaluations=0)
# result.passed = False
```

### DefinitionChangeGuard

Detect when expectation definitions change between runs.

```python
from phylax import DefinitionChangeGuard

guard = DefinitionChangeGuard()
result = guard.evaluate(
    previous_hash="abc123",
    current_hash="def456",
)
# result.passed = False (definitions changed)
```

### ExpectationRemovalGuard

Detect when expectations are silently removed.

```python
from phylax import ExpectationRemovalGuard

guard = ExpectationRemovalGuard()
result = guard.evaluate(
    previous_ids={"e1", "e2", "e3"},
    current_ids={"e1", "e2"},
)
# result.passed = False
# result.removed = {"e3"}
```

---

## Key Properties

- All metrics are **derived facts**, not interpretations
- Ledger is **append-only** -- no mutation methods exist
- Health reports are **deterministic** -- 1000 runs produce 1 hash
- No **advisory language** in any logic path
- No **adaptive behavior** -- no auto-adjust, learn, evolve
- No **heuristics** -- all values explicitly declared by user
