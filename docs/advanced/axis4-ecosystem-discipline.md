# Axis 4: Ecosystem Discipline

Axis 4 protects identity at ecosystem scale. It prevents Phylax from becoming a platform.

---

## Core Invariant

> Phylax produces artifacts. Other systems consume them. Phylax does not embed those systems.

---

## What Phylax Will Never Do

These are constitutional constraints from `CONSTITUTION.md`. Violating any requires a MAJOR version bump.

1. **Explain failures** -- reports facts, interpretation is external
2. **Rank expectations** -- all expectations are equal
3. **Suggest improvements** -- no advisory language
4. **Provide optimization advice** -- enforces, doesn't coach
5. **Add AI inference** -- all verdicts are deterministic
6. **Embed dashboards** -- no built-in visualization
7. **Send alerts** -- no Slack, email, webhook
8. **Auto-adjust thresholds** -- all values explicitly declared
9. **Modify user expectations** -- expectations are immutable contracts
10. **Add a plugin system** -- no extension marketplace
11. **Run as a daemon** -- runs and exits
12. **Make outbound network calls** -- no telemetry, no phone-home

---

## Anti-Features

Documented in `ANTI_FEATURES.md`. These are intentional absences.

### No Embedded Dashboards

If you want dashboards, parse `verdict.json` and `failures.json` with your own tools.

### No Built-In Alerting

If you want alerting, wrap `phylax check` in your CI pipeline and use your existing alerting system.

### No Background Services

Phylax runs and exits. No daemon mode. No scheduler.

### No Plugin System

All expectations declared explicitly in the repository. No runtime injection.

---

## Versioning Discipline

| Change Type | Version Bump |
|-------------|-------------|
| Artifact schema changes | MAJOR |
| Verdict semantics change | MAJOR |
| Determinism guarantees change | MAJOR |
| New surface support added | MINOR |
| New meta-rule types added | MINOR |
| Bug fixes only | PATCH |

---

## Breaking Contract Definition

These changes constitute a trust violation and require MAJOR version bump:

1. Changing artifact schema silently
2. Adding interpretation fields to outputs
3. Adding advisory metadata to artifacts
4. Auto-switching enforcement modes
5. Introducing heuristic evaluation
6. Adding network dependencies
7. Embedding third-party integrations

---

## Ecosystem Fit

External tools build AROUND Phylax, not INSIDE it.

### External Dashboard Example

```python
# dashboard_tool.py -- SEPARATE repository, not inside Phylax
import json

with open("verdict.json") as f:
    data = json.load(f)

html = f"<h1>Verdict: {data['verdict']}</h1>"
html += f"<p>{data['failures']}/{data['expectations_evaluated']} failed</p>"
# Phylax core remains untouched
```

### External Alerting Example

```bash
#!/bin/bash
# alert.sh -- wrapper script, NOT inside Phylax
phylax check
if [ $? -eq 1 ]; then
    curl -X POST https://hooks.slack.com/... -d '{"text": "Phylax: FAIL"}'
fi
# Phylax does not send Slack messages. You do.
```

---

## Final State

After Axis 4, Phylax:

- Produces stable, frozen artifacts
- Is CI-native (runs and exits)
- Is ecosystem-consumable (JSON output, exit codes)
- Does NOT embed ecosystem features
- Has constitutional boundaries
- Is small, deterministic, authoritative
