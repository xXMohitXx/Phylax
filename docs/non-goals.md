# Non-Goals

Phylax will **never**:

1. **Explain failures** — Phylax reports what failed, not why. No causal reasoning, no narrative.
2. **Recommend fixes** — Phylax does not suggest corrections. It reports contract violations.
3. **Score outputs** — No quality scores, confidence levels, or partial verdicts. Binary PASS/FAIL only.
4. **Reason semantically** — No NLP, no embeddings, no similarity matching. Evidence is exact comparison only.
5. **Monitor production** — Phylax is CI-only. It does not run in production, collect metrics, or alert.

These are permanent constraints, not roadmap items.

---

## Why These Matter

Each non-goal prevents Phylax from drifting into a different category of tool:

| Non-Goal | Prevents Becoming |
|----------|-------------------|
| No explanations | Debugging assistant |
| No recommendations | AI code reviewer |
| No scoring | Quality assessment platform |
| No semantics | NLP evaluation framework |
| No production | Observability/monitoring tool |

Phylax answers exactly one question: **"Did a declared contract regress?"**
