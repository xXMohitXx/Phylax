# Behavioral Diff

The Behavioral Diff engine compares two arbitrary trace sets logically, rather than purely via strings, identifying structural prompt adherence and failure modes between runs.

## `diff_runs()`

By using `diff_runs()`, you can track how two parallel model executions diverged on identical inputs. This is directly responsible for powering the `simulate_upgrade()` module, but can be invoked standalone:

```python
from phylax import diff_runs, format_diff_report

# Compare run results
diff = diff_runs(baseline_result, candidate_result)

summary = format_diff_report(diff)
print(summary)
```

### Regressions and Improvements

- A **Regression** is defined as an execution sequence that passed on the `baseline_result` but failed validations in the `candidate_result`.
- An **Improvement** is defined inversely.
