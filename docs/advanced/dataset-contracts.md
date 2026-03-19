# Dataset Contracts

Dataset Contracts act as the bedrock for continuous AI regression testing. Rather than writing subjective unit tests, Dataset Contracts let you map expectations strictly to bulk inputs.

## The YAML Configuration

Contracts are best declared as standalone `.yaml` files, enabling non-engineers to define LLM behavior policies.

```yaml
name: support-bot-contracts
cases:
  - name: greeting_test
    input: "Hi!"
    expectations:
      min_tokens: 5
```

## Running Contracts

Run them locally or securely inside GitHub Actions:

```bash
phylax dataset run dataset.yaml -m package.module -f target_function
```

Violations will instantly trigger exit code `1`, breaking the build if the model degenerates or drifts from expectations.
