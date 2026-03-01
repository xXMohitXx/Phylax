# What Phylax Will Never Do

This document is a constitutional constraint.
Violating any of these requires a **MAJOR version bump** and explicit community acknowledgment.

---

## Phylax will never:

1. **Explain failures** → Phylax reports facts. Interpretation is external.
2. **Rank expectations** → All expectations are equal. No priority ordering.
3. **Suggest improvements** → No advisory language. No optimization advice.
4. **Provide optimization advice** → Phylax enforces. It does not coach.
5. **Add AI inference** → All verdicts are deterministic. No LLM-based judgment.
6. **Embed dashboards** → No built-in visualization. Parse artifacts externally.
7. **Send alerts** → No Slack, email, webhook, or push notification.
8. **Auto-adjust thresholds** → All values are explicitly declared by the user.
9. **Modify user expectations** → Expectations are immutable contracts.
10. **Add a plugin system** → No extension marketplace. No runtime injection.
11. **Run as a daemon** → Phylax runs and exits. No background services.
12. **Make outbound network calls** → No telemetry. No phone-home. No cloud.

---

## What Phylax IS:

- A small, deterministic verdict authority
- CI-native: runs in CI, exits with code
- Artifact-producing: outputs machine-consumable contracts
- Ecosystem-consumable: other systems parse its output

## What Phylax is NOT:

- ❌ A dashboard product
- ❌ An alerting system
- ❌ A SaaS platform
- ❌ An ecosystem host
- ❌ An analytics engine
- ❌ A recommendation system

---

## Breaking Contract Definition

The following changes constitute a **trust violation** and require a MAJOR version bump:

1. Changing artifact schema silently
2. Adding interpretation fields to outputs
3. Adding advisory metadata to artifacts
4. Auto-switching enforcement modes
5. Introducing heuristic evaluation
6. Adding network dependencies
7. Embedding third-party integrations

---

## Governance

This document is part of the repository.
Any PR that introduces a feature violating this constitution must:

1. Be explicitly acknowledged in the PR description
2. Require a MAJOR version bump
3. Update this document to reflect the change

**Last Updated**: March 1, 2026
**Constitution Version**: 1.0.0
