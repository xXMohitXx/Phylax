# Axis 3 & 4 Testing Guide

How to run and understand the Axis 3 (Scale Safety) and Axis 4 (Ecosystem Discipline) test suites.

---

## Test Files

| File | Tests | What it proves |
|------|-------|----------------|
| `tests/test_metric_foundation.py` | Axis 3 Phase 3.1 | Identity, ledger, aggregation, health |
| `tests/test_meta_enforcement.py` | Axis 3 Phase 3.4 | Meta-rules (min count, zero signal, guards) |
| `tests/test_axis3_integrity.py` | 78 | Fortress: no semantic creep, no non-determinism |
| `tests/test_artifact_contracts.py` | 27 | Artifact immutability, determinism, no commentary |
| `tests/test_axis4_integrity.py` | 19 | Anti-integration, governance, ecosystem fit |
| `tests/test_axis4_fortress.py` | 53 | Fortress: schema freeze, platform drift scan |

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -q

# Run only Axis 3 tests
python -m pytest tests/test_metric_foundation.py tests/test_meta_enforcement.py tests/test_axis3_integrity.py -v

# Run only Axis 4 tests
python -m pytest tests/test_artifact_contracts.py tests/test_axis4_integrity.py tests/test_axis4_fortress.py -v

# Run fortress tests only
python -m pytest tests/test_axis3_integrity.py tests/test_axis4_fortress.py -v
```

## What Fortress Tests Check

Fortress tests are NOT about "does it work?" They detect:

- **Semantic creep** -- advisory language sneaking into logic
- **Non-determinism** -- different outputs from identical inputs
- **Advisory drift** -- explanation/suggestion fields appearing
- **Enforcement mutation** -- modes auto-switching
- **Platform drift** -- dashboard/alerting/plugin code appearing
- **Dependency expansion** -- heavy libraries being imported
- **Network isolation** -- outbound HTTP/SMTP calls
- **Plugin injection** -- dynamic loading or runtime extension

## Test Philosophy

If a fortress test fails, it doesn't mean something crashed. It means something "helpful" was added that shouldn't be there.
