# Model Simulator

The Model Simulator protects your production environment by evaluating an LLM model switch (e.g. GPT-3.5 to GPT-4o) using past execution traces.

## Simulating Upgrades

With `simulate_upgrade()`, you run your `baseline` model alongside the new `candidate` model locally.

### Example

```python
from phylax import simulate_upgrade, format_simulation_report

# ... dataset defined ...

sim = simulate_upgrade(
    dataset=ds,
    baseline_func=v1_agent,
    candidate_func=v2_agent,
    baseline_name="GPT-3.5",
    candidate_name="GPT-4o",
)

if sim.safe_to_upgrade:
    print("Zero regressions found. Safe to upgrade!")
```

The simulator runs your old and new constraints instantly, highlighting exact behavioral breaks before a bad model change hits your live end-users.
