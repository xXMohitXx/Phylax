# Agent Workflow Example

This example demonstrates how to evaluate and simulate multi-step agent workflows.

## Features Showcased

- **Multi-Agent Enforcement**: Validating tool call sequences using `phylax.agents`.
- **Dataset Contracts**: Running bulk automated testing using `run_dataset()`.
- **Model Upgrade Simulation**: Safely comparing a baseline (`v1`) versus candidate (`v2`) agent model before deployment using `simulate_upgrade()`.
- **Behavioral Diff**: Pinpointing exact regressions when comparing the two agents.

## Usage

Run the following from the root of this directory:

```bash
# Ensure phylax is installed
pip install phylax

# Run the simulation
python app.py
```
