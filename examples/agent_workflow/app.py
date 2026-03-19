"""
Agent Workflow Example — Multi-step agent with model upgrade simulation.

Demonstrates:
    - Dataset contracts for agent testing
    - Model upgrade simulator (simulate_upgrade)
    - Behavioral diff for regression detection
    - Compliance guardrails

Run:
    pip install phylax
    python app.py
"""
from phylax import (
    trace, expect, execution,
    Dataset, DatasetCase,
    simulate_upgrade, format_simulation_report,
    diff_runs, format_diff_report,
    run_dataset, format_report,
)
from phylax.guardrails import compliance_pack
from phylax.agents import AgentStepValidator, ToolSequenceRule


# Compliance guardrails for agent responses
_compliance = compliance_pack()
_compliance_rules = _compliance.to_expectations()


@trace(provider="mock")
@expect(**_compliance_rules)
def agent_v1(query: str) -> str:
    """Baseline agent (v1) — simple response."""
    return (
        f"Based on your query about '{query}', here is what I found: "
        f"The topic involves multiple considerations. I recommend "
        f"reviewing the official documentation for detailed guidance."
    )


@trace(provider="mock")
@expect(**_compliance_rules)
def agent_v2(query: str) -> str:
    """Candidate agent (v2) — improved responses with more detail."""
    return (
        f"Regarding '{query}': After analyzing the available information, "
        f"here are the key points to consider. The topic requires careful "
        f"evaluation of multiple factors. For the most accurate and "
        f"up-to-date information, please consult the relevant resources."
    )


def main():
    print("=== Agent Workflow: Multi-Agent Validation ===")
    
    # Showcase phylax.agents before running the simulator
    print("--- Enforcing Tool Sequence Constraints ---")
    sequence_rule = ToolSequenceRule(required_sequence=["retriever", "generator"], strict=False)
    simulated_tool_trace = [{"tool_name": "retriever"}, {"tool_name": "generator"}]
    res = sequence_rule.evaluate(simulated_tool_trace)
    print(f"Tool Sequence Check: {'✅ PASS' if res.passed else '❌ FAIL'}\n")

    print("=== Agent Workflow: Model Upgrade Simulation ===\n")

    # Define test cases for the agent
    ds = Dataset(dataset="agent_workflow", cases=[
        DatasetCase(
            input="What stocks should I buy?",
            name="financial_query",
            expectations={**_compliance_rules, "min_tokens": 15},
        ),
        DatasetCase(
            input="How do I improve my code?",
            name="tech_query",
            expectations={**_compliance_rules, "must_include": ["consider"]},
        ),
        DatasetCase(
            input="What is the meaning of life?",
            name="philosophical_query",
            expectations={**_compliance_rules, "min_tokens": 10},
        ),
    ])

    # Run baseline
    print("--- Running baseline (v1) ---")
    result_v1 = run_dataset(ds, agent_v1)
    print(format_report(result_v1))

    # Simulate upgrade
    print("--- Simulating upgrade: v1 → v2 ---")
    sim = simulate_upgrade(
        dataset=ds,
        baseline_func=agent_v1,
        candidate_func=agent_v2,
        baseline_name="agent-v1",
        candidate_name="agent-v2",
    )
    print(format_simulation_report(sim))

    if sim.safe_to_upgrade:
        print("🚀 Safe to deploy agent-v2!")
    else:
        print("⚠️  Upgrade blocked — regressions found.")


if __name__ == "__main__":
    main()
