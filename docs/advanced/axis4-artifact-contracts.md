# Axis 4: Artifact Contracts

Phylax produces frozen, machine-consumable artifacts. External systems consume them. Phylax does not embed those systems.

---

## Verdict Artifact

The primary output of every Phylax run.

```python
from phylax import generate_verdict_artifact, compute_definition_hash

definition = {"rule": "must_include", "substrings": ["refund"]}
snapshot_hash = compute_definition_hash(definition)

artifact = generate_verdict_artifact(
    mode="enforce",
    verdict="FAIL",
    expectations_evaluated=10,
    failures=3,
    definition_snapshot_hash=snapshot_hash,
    engine_version="1.4.1",
)
```

### verdict.json Schema

```json
{
  "schema_version": "1.0.0",
  "run_id": "uuid",
  "timestamp": "ISO-8601 UTC",
  "mode": "enforce|quarantine|observe",
  "verdict": "PASS|FAIL",
  "expectations_evaluated": 10,
  "failures": 3,
  "definition_snapshot_hash": "sha256",
  "engine_version": "1.4.1"
}
```

### Constraints

- **No optional fields** without schema version bump
- **No semantic additions** -- every field is mechanical fact
- **Deterministic ordering** of keys
- **No human commentary** -- no explanation, suggestion, or narrative


---

## Failure Artifact

Produced when verdict is FAIL. Strictly mechanical.

```python
from phylax import generate_failure_artifact

artifact = generate_failure_artifact(
    run_id="ci-run-001",
    failures=[
        {"expectation_id": "e1", "violated_rule": "must_include",
         "raw_value": "Hello", "expected_value": "refund"},
        {"expectation_id": "e2", "violated_rule": "max_latency_ms",
         "raw_value": "2500", "expected_value": "1500"},
    ],
)
```

### failures.json Schema

```json
{
  "schema_version": "1.0.0",
  "run_id": "string",
  "failures": [
    {
      "expectation_id": "string",
      "violated_rule": "string",
      "raw_value": "string",
      "expected_value": "string"
    }
  ]
}
```

### What is NOT included

- No `explanation` field
- No `severity` or `priority` ranking
- No `suggestion` or `recommendation`
- No narrative text of any kind

---

## Trace Diff Artifact

For cross-run comparison. Literal diffs only.

```python
from phylax import generate_trace_diff

diff = generate_trace_diff(
    run_id_before="run-001",
    run_id_after="run-002",
    expectations_before={"e1", "e2"},
    expectations_after={"e2", "e3"},
    hash_before="hash_a",
    hash_after="hash_b",
    changed_fields=["expectations"],
)
# diff.added_expectations = ["e3"]
# diff.removed_expectations = ["e1"]
# diff.hashes_match = False
```

### trace_diff.json Schema

```json
{
  "schema_version": "1.0.0",
  "run_id_before": "string",
  "run_id_after": "string",
  "changed_fields": ["string"],
  "added_expectations": ["string"],
  "removed_expectations": ["string"],
  "hash_before": "string",
  "hash_after": "string",
  "hashes_match": false
}
```

### What is NOT included

- No "impact assessment"
- No risk scoring
- No severity classification

---

## Deterministic Exit Codes

Frozen at exactly 3 values. No expansion without MAJOR version bump.

| Code | Meaning | When |
|------|---------|------|
| `0` | PASS | All expectations pass, OR non-blocking mode |
| `1` | FAIL | Failure in `enforce` mode |
| `2` | SYSTEM ERROR | Malformed config, missing files, etc. |

```python
from phylax import EXIT_PASS, EXIT_FAIL, EXIT_SYSTEM_ERROR, resolve_exit_code

code = resolve_exit_code(verdict="FAIL", mode="enforce")   # 1
code = resolve_exit_code(verdict="FAIL", mode="observe")   # 0
code = resolve_exit_code(verdict="PASS", mode="enforce")   # 0
```

### CI Usage

```yaml
# GitHub Actions
- run: phylax check
  # Exit 0 = pipeline continues
  # Exit 1 = pipeline fails
  # Exit 2 = investigate
```

---

## External Consumption

Artifacts are designed for external tools to parse **without importing Phylax**:

```python
# External tool -- no phylax import needed
import json

with open("verdict.json") as f:
    verdict = json.load(f)

if verdict["verdict"] == "FAIL":
    print(f"Failed: {verdict['failures']}/{verdict['expectations_evaluated']}")
    # Send to Slack, dashboard, etc. -- OUTSIDE Phylax
```
