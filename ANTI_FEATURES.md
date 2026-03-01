# Anti-Features — What Phylax Explicitly Does NOT Include

These are documented **non-features** — things intentionally absent.

---

## 4.2.1 — No Embedded Dashboards

Phylax does not include:
- Web UI for analytics *(the existing UI is a trace inspector, not a dashboard)*
- Visualization layers
- Metrics dashboards
- Trend charts

**If you want dashboards**: Parse `verdict.json` and `failures.json` artifacts with your own tools.

## 4.2.2 — No Built-In Alerting

Phylax does not:
- Send Slack messages
- Send emails
- Trigger webhooks automatically
- Push notifications

**If you want alerting**: Wrap `phylax check` in your CI pipeline and use your existing alerting system on exit code.

## 4.2.3 — No Background Services

Phylax does not:
- Run as a daemon
- Schedule background jobs
- Maintain persistent connections
- Run a background scheduler

Phylax **runs and exits**. This prevents platform creep.

## 4.2.4 — No Plugin System

Phylax does not implement:
- Extension marketplace
- Plugin loading
- Runtime rule injection from external packages
- Custom rule registration at runtime

All expectations are declared explicitly in the repository.

---

## Why?

These non-features are not limitations — they are **architectural decisions**.

Phylax is a small, deterministic verdict authority.
Adding any of these features would transform it into a platform.

**Platforms attract gravity. Phylax must remain weightless.**
