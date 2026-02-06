# Phylax Error Codes

Machine-readable error codes for CI integration.

---

## E1xx: Expectation Errors

| Code | Invariant Violated | User Action |
|------|-------------------|-------------|
| PHYLAX_E101 | Function has no expectations | Add `@expect` decorator |
| PHYLAX_E102 | Execution graph is empty | Add traced calls inside `execution()` |
| PHYLAX_E103 | Execution has no verdict path | Ensure traced functions have expectations |

---

## E2xx: Golden Trace Errors

| Code | Invariant Violated | User Action |
|------|-------------------|-------------|
| PHYLAX_E201 | Cannot bless trace without verdict or with failed verdict | Fix trace expectations before blessing |
| PHYLAX_E202 | No golden traces exist for check | Bless a trace with `phylax bless <id>` |
| PHYLAX_E203 | Output hash differs from golden | Investigate regression |

---

## E3xx: Configuration Errors

| Code | Invariant Violated | User Action |
|------|-------------------|-------------|
| PHYLAX_E301 | Configuration cannot produce verdicts | Fix configuration |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Failure or regression detected |

---

Phylax reports errors. Interpretation is external.
