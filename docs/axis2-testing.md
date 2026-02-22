# Axis 2 Testing — Semantic Containment

Axis 2 testing is not quality assurance. It is **semantic containment testing** — proving that the engine did NOT become intelligent.

## Philosophy

Every Axis 2 phase must pass four invariant test categories:

1. **Determinism Tests** — Same input twice → identical verdict. Always.
2. **Literalism Tests** — No coercion, no fuzzy matching, no case folding.
3. **Mutation Resistance Tests** — No deduplication, no retry collapsing, no auto-correction.
4. **Semantic Drift Tests** — No interpretation, no quality judgment, no reasoning about intent.

If any test in these categories fails, the phase is invalid.

## Test Structure

All semantic containment tests live in `tests/test_axis2_containment.py`. They are organized by phase:

| Phase | Section | Key Tests |
|-------|---------|-----------|
| 2.0 | Surface Abstraction | Determinism, raw payload integrity, engine isolation, surface-type blindness |
| 2.1 | Structured Output | Strict equality, field presence, enum edges, schema absence, JSON parsing edges |
| 2.2 | Tool Calls | Raw trace integrity, call count strict, ordering with noise, argument literalism |
| 2.3 | Execution Traces | Step count boundaries, forbidden transitions, loop behavior, conditional rule rejection |
| 2.4 | Cross-Run Stability | Exact snapshot comparison, allowed drift regions, baseline mutation, fuzzy tolerance rejection |
| Meta | Cross-Phase | 100-run determinism sweep, noise injection, surface isolation, adversarial "should understand" tests |

## Cross-Phase Meta Tests

### 100-Run Determinism Sweep
Every rule type is evaluated 100 times with identical input. All verdict hashes must match. If any mismatch exists → non-deterministic logic exists → **FAIL**.

### Random Noise Injection
Irrelevant metadata is injected into surfaces. Verdict must remain unchanged unless a rule explicitly references the metadata. If metadata influences outcome implicitly → **FAIL**.

### Surface Isolation
Structured rules tested on tool surfaces. Tool rules tested on structured surfaces. No cross-surface leakage is permitted.

### "Should Understand" Test
Adversarial cases where the engine *could* interpret intent but *must not*:
- Tool called twice due to retry → contract says once → must **FAIL**
- Stage repeated → engine must not prune "redundant" stages
- Output looks wrong but matches contract → must **PASS**
- Tiny baseline change that "looks harmless" → must **FAIL**

## The Discipline Question

Testing must not only check correctness. It must check **absence of intelligence creep**.

If tests do not explicitly try to break determinism and literalism, Axis 2 will slowly mutate under convenience pressure.

Axis 2 is complete only when:
- Every test suite passes
- No rule type requires interpretation
- No dynamic branching exists
- No soft logic detected
- Engine core remains unchanged from Axis 1
